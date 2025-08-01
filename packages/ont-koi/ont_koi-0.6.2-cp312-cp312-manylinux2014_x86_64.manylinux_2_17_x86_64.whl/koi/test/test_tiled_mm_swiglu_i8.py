import time
import torch
import pytest
from koi._runtime import lib, ffi
from koi.utils import (
    void_ptr,
    show_diff_result,
    time_kernel,
    koi_tensor,
    quantize_tensor,
)

dtype = torch.float16
dev = "cuda"

test_dims = (
    (64 * 1024, 4096, 512),
    (64 * 1024, 4096, 1536),
)
iters = 500


@pytest.mark.parametrize("dims", test_dims)
def test_tiled_mm_swiglu(dims):
    if lib.koi_tc_is_available(lib.KOI_F16) == lib.KOI_NOT_SUPPORTED:
        print("Koi tensor core kernels not available, skipping test")
        return

    M, N, K = dims
    stream = torch.cuda.default_stream()
    stream_ptr = ffi.cast("void *", stream.cuda_stream)

    with torch.no_grad():
        torch.manual_seed(42)

        input = torch.rand((M, K), device=dev, dtype=dtype) * 0.5 - 0.25
        weights = torch.rand((N, K), device=dev, dtype=dtype) * 0.5 - 0.25
        out_ref = torch.zeros((M, N // 2), device=dev, dtype=dtype)
        out_koi_tiled = torch.zeros((M // 16, N // 16, 16, 8), device=dev, dtype=dtype)
        out_koi_tiled_fp8 = torch.zeros(
            (M // 16, N // 32, 16, 16), device=dev, dtype=torch.float8_e4m3fn
        )

        input_scale, input_i8 = quantize_tensor(input, 256, -1)
        input_scale.reciprocal_()
        input_i8_tiled = (
            input_i8.view((M // 16, 16, K // 16, 16)).transpose(1, 2).contiguous()
        )

        weights_scale, weights_i8 = quantize_tensor(weights, 256, -1)
        weights_scale.reciprocal_()
        weights_i8_interleaved = (
            weights_i8.view((N // 32, 16, 2, K)).transpose(1, 2).contiguous()
        )
        weights_i8_tiled = (
            weights_i8_interleaved.view((N // 16, 16, K // 16, 16))
            .transpose(1, 2)
            .contiguous()
        )

        input = (input_i8.float() * input_scale.unsqueeze(-1)).half()
        weights = (weights_i8.float() * weights_scale.unsqueeze(-1)).half()

        def torch_impl():
            mm = (input @ weights.T).view((M, N // 2, 2))
            out_ref[:] = torch.nn.functional.silu(mm[:, :, 1]) * mm[:, :, 0]

        t_ref = time_kernel(iters, stream, torch_impl, None)

        ctr_bfr = torch.zeros((iters + 1,), device=dev, dtype=torch.int32)
        ctr = 0

        def koi_impl():
            nonlocal ctr
            args = (
                stream_ptr,
                koi_tensor(input_i8_tiled, ["M", "K", "m", "k"], (input_scale, "K")),
                koi_tensor(
                    weights_i8_tiled, ["N", "K", "n", "k"], (weights_scale, "K")
                ),
                koi_tensor(out_koi_tiled, ["M", "N", "m", "n"]),
                void_ptr(ctr_bfr[ctr]),
                1,
            )
            ctr += 1
            return lib.koi_mm_swiglu(*args)

        time_kernel(iters // 2, stream, koi_impl, lib.KOI_SUCCESS)
        ctr = 0
        ctr_bfr[:] = 0
        t_koi = time_kernel(iters, stream, koi_impl, lib.KOI_SUCCESS)

        ops = iters * M * N * K * 2
        tflops = 1e-12 * ops / t_koi

        out_koi = out_koi_tiled.permute((0, 2, 1, 3)).contiguous().view((M, N // 2))

        label = f"{dims}, ref {t_ref:.3f}s, koi {t_koi:.3f}s, {tflops:.3f} TFlops"
        show_diff_result(label, out_ref, out_koi, 1e-2, 0.2, __name__ != "__main__")

        weights_shuffle_index = torch.tensor(
            [0, 1, 4, 5, 8, 9, 12, 13, 2, 3, 6, 7, 10, 11, 14, 15], device=dev
        )
        weights_fp8 = (
            torch.index_select(weights_i8_tiled, 2, weights_shuffle_index)
            .contiguous()
            .view((N // 16, K // 16, 16, 16))
        )

        def koi_impl_fp8():
            nonlocal ctr
            args = (
                stream_ptr,
                koi_tensor(input_i8_tiled, ["M", "K", "m", "k"], (input_scale, "K")),
                koi_tensor(weights_fp8, ["N", "K", "n", "k"], (weights_scale, "K")),
                koi_tensor(out_koi_tiled_fp8, ["M", "N", "m", "n"]),
                void_ptr(ctr_bfr[ctr]),
                1,
            )
            ctr += 1
            return lib.koi_mm_swiglu(*args)

        ctr = 0
        ctr_bfr[:] = 0
        t_koi = time_kernel(iters, stream, koi_impl_fp8, lib.KOI_SUCCESS)
        out_koi_fp8 = (
            out_koi_tiled_fp8.permute((0, 2, 1, 3)).contiguous().view((M, N // 2))
        )

        label = (
            f"{dims}, ref {t_ref:.3f}s, koi fp8 out {t_koi:.3f}s, {tflops:.3f} TFlops"
        )
        show_diff_result(label, out_ref, out_koi_fp8, 5e-2, 0.8, __name__ != "__main__")

        input[:] = 0
        weights[:] = 0
        ctr = 0
        ctr_bfr[:] = 0
        t_koi = time_kernel(iters, stream, koi_impl, lib.KOI_SUCCESS)
        tflops = 1e-12 * ops / t_koi
        print(f"All zero {t_koi:.3f}s, {tflops:.3f} TFlops")


if __name__ == "__main__":
    for test_dim in test_dims:
        test_tiled_mm_swiglu(test_dim)
