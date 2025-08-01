import time
import torch
import pytest
from koi._runtime import lib, ffi
from koi.utils import void_ptr, check_result, time_kernel, koi_tensor

dtype = torch.float16
dev = "cuda"

test_dims = (
    (64, 1024, 512, 8, 64),
    (64, 1024, 1536, 24, 64),
)
iters = 500

is_main = __name__ == "__main__"


@pytest.mark.parametrize("dims", test_dims)
def test_tiled_qkv_rotary(dims):
    if lib.koi_tc_is_available(lib.KOI_F16) == lib.KOI_NOT_SUPPORTED:
        print("Koi tensor core kernels not available, skipping test")
        return

    N, T, C, H, D = dims
    dim = D // 2
    theta = 10000.0
    stream = torch.cuda.default_stream()
    stream_ptr = ffi.cast("void *", stream.cuda_stream)

    with torch.no_grad():
        torch.manual_seed(42)

        in_bfr = torch.rand((N, T, C), device=dev, dtype=dtype) * 2 - 1
        weight_bfr = torch.rand((C, 3, H, D), device=dev, dtype=dtype) * 2 - 1
        out_ref = torch.zeros((N, T, 3, H, D), device=dev, dtype=dtype)
        out_koi_tiled = torch.zeros(
            (N, T // 16, 3, H, D // 8, 16, 8), device=dev, dtype=dtype
        )
        ops = iters * out_koi_tiled.numel() * C * 2

        inv_freq = torch.pow(theta, (torch.arange(dim) / -dim))
        freq = torch.arange(T).reshape((T, 1, 1)) * inv_freq
        cos_buf = freq.cos().to(dev)
        sin_buf = freq.sin().to(dev)

        def torch_impl():
            out_ref[:] = (in_bfr.view((-1, C)) @ weight_bfr.view((C, -1))).view(
                (N, T, 3, H, D)
            )
            qk_even_odd = out_ref.view((N, T, 3, H, D // 2, 2)).permute(
                (5, 2, 0, 1, 3, 4)
            )[:, :2]
            qk_evens = qk_even_odd[0].clone()
            qk_even_odd[0] = cos_buf * qk_evens - sin_buf * qk_even_odd[1]
            qk_even_odd[1] = sin_buf * qk_evens + cos_buf * qk_even_odd[1]

        t_ref = time_kernel(iters, stream, torch_impl, None)

        sincos_bfr = torch.empty((T, dim, 2), device=dev, dtype=dtype)
        sincos_bfr[:, :, 0] = sin_buf[:, 0]
        sincos_bfr[:, :, 1] = cos_buf[:, 0]
        sincos_bfr = (
            sincos_bfr.view((T // 16, 16, D // 8, 8)).transpose(1, 2).contiguous()
        )

        in_bfr_tiled = (
            in_bfr.view((N, T // 16, 16, C // 8, 8)).transpose(2, 3).contiguous()
        )
        weight_bfr_tiled = (
            weight_bfr.view((C // 8, 8, 3, H, D // 16, 16))
            .permute((2, 3, 4, 0, 5, 1))
            .contiguous()
        )
        ctr_bfr = torch.zeros((iters + 1,), device=dev, dtype=torch.int32)
        ctr = 0

        def koi_impl():
            nonlocal ctr
            args = (
                stream_ptr,
                theta,
                koi_tensor(in_bfr_tiled, ["N", "T", "C", "t", "c"]),
                koi_tensor(
                    weight_bfr_tiled, [lib.KOI_DIM_MAT_Q_K_V, "H", "D", "C", "d", "c"]
                ),
                koi_tensor(sincos_bfr, ["T", "D", "t", "d"]),
                koi_tensor(
                    out_koi_tiled, ["N", "T", lib.KOI_DIM_MAT_Q_K_V, "H", "D", "t", "d"]
                ),
                void_ptr(ctr_bfr[ctr]),
            )
            ctr += 1
            return lib.koi_qkv_rotary(*args)

        t_koi = time_kernel(iters, stream, koi_impl, lib.KOI_SUCCESS)

        tflops = 1e-12 * ops / t_koi

        # qkv -> N, T // 16, 3, H, D // 8, 16, 8
        # transpose8x8 V
        out_koi_tiled[:, :, 2, :, :, 0:8, :] = (
            out_koi_tiled[:, :, 2, :, :, 0:8, :].transpose(-2, -1).clone()
        )
        out_koi_tiled[:, :, 2, :, :, 8:16, :] = (
            out_koi_tiled[:, :, 2, :, :, 8:16, :].transpose(-2, -1).clone()
        )

        out_koi = (
            out_koi_tiled.permute((0, 1, 5, 2, 3, 4, 6))
            .contiguous()
            .view((N, T, 3, H, D))
        )

        label = f"{dims}, ref {t_ref:.3f}s, koi {t_koi:.3f}s, {tflops:.3f} TFlops"
        check_result(label, out_ref, out_koi, True, 8e-4, 6e-3, not is_main)

        ctr_bfr = torch.zeros((iters + 1,), device=dev, dtype=torch.int32)
        ctr = 0
        in_bfr_tiled[:] = 0
        weight_bfr_tiled[:] = 0
        t_koi = time_kernel(iters, stream, koi_impl, lib.KOI_SUCCESS)
        tflops = 1e-12 * ops / t_koi
        print(f"All zeros: {t_koi:.3f}s, {tflops:.3f} TFlops")


if is_main:
    for test_dim in test_dims:
        test_tiled_qkv_rotary(test_dim)
