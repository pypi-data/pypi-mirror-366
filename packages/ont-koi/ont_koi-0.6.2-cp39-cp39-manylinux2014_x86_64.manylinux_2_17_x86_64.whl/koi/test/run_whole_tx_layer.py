import time
import torch
import pytest
from koi._runtime import lib, ffi
from koi.utils import void_ptr, show_diff_result, time_kernel, koi_tensor

dtype = torch.float16
dev = "cuda"

test_dims = ((256, 1024, 512, 8, 64, 4096),)
iters = 200


def run_whole_tx_layer(dims):
    if lib.koi_tc_is_available(lib.KOI_F16) == lib.KOI_NOT_SUPPORTED:
        print("Koi tensor core kernels not available, skipping")
        return

    N, T, C, H, D, E = dims
    dim = D // 2
    alpha = 0.5
    theta = 10000.0
    win_upper, win_lower = 127, 128
    stream = torch.cuda.default_stream()
    stream_ptr = ffi.cast("void *", stream.cuda_stream)

    with torch.no_grad():
        torch.manual_seed(42)

        inv_freq = torch.pow(theta, (torch.arange(dim) / -dim))
        freq = torch.arange(T).reshape((T, 1, 1)) * inv_freq
        cos_buf = freq.cos().to(dev)
        sin_buf = freq.sin().to(dev)
        sincos_bfr = torch.empty((T, dim, 2), device=dev, dtype=dtype)
        sincos_bfr[:, :, 0] = sin_buf[:, 0]
        sincos_bfr[:, :, 1] = cos_buf[:, 0]
        sincos_bfr = (
            sincos_bfr.view((T // 16, 16, D // 8, 8)).transpose(1, 2).contiguous()
        )

        ctr_bfr = torch.zeros((8,), device=dev, dtype=torch.int32)

        in_bfr = (
            torch.rand((N, T // 16, C // 8, 16, 8), device=dev, dtype=dtype) * 2 - 1
        )
        qkv_weight_bfr = (
            torch.rand((3, H, D // 16, C // 8, 16, 8), device=dev, dtype=dtype) * 2 - 1
        )
        proj_weight_bfr = (
            torch.rand((C // 16, C // 8, 16, 8), device=dev, dtype=dtype) * 2 - 1
        )
        proj_bias_bfr = torch.rand((C,), device=dev, dtype=dtype) * 2 - 1
        residual1_weight_bfr = torch.rand((C,), device=dev, dtype=dtype) * 2 - 1
        residual2_weight_bfr = torch.rand((C,), device=dev, dtype=dtype) * 2 - 1
        fc1_weight_bfr = (
            torch.rand((E // 16, C // 8, 16, 8), device=dev, dtype=dtype) * 2 - 1
        )
        fc2_weight_bfr = (
            torch.rand((C // 16, E // 16, 16, 8), device=dev, dtype=dtype) * 2 - 1
        )

        qkv_bfr = torch.empty(
            (N, T // 16, 3, H, D // 8, 16, 8), device=dev, dtype=dtype
        )
        attn_out_bfr = torch.empty(
            (N, T // 16, H, D // 8, 16, 8), device=dev, dtype=dtype
        )
        proj_out_bfr = torch.empty((N, T // 16, C // 8, 16, 8), device=dev, dtype=dtype)
        residual1_out_bfr = torch.empty(
            (N, T // 16, C // 8, 16, 8), device=dev, dtype=dtype
        )
        fc1_out_bfr = torch.empty(
            (N * T // 16, E // 16, 16, 8), device=dev, dtype=dtype
        )
        fc2_out_bfr = torch.empty((N, T // 16, C // 8, 16, 8), device=dev, dtype=dtype)
        residual2_out_bfr = torch.empty(
            (N, T // 16, C // 8, 16, 8), device=dev, dtype=dtype
        )

        def koi_impl():
            ctr_bfr[:] = 0
            args = (
                stream_ptr,
                theta,
                koi_tensor(in_bfr, ["N", "T", "C", "t", "c"]),
                koi_tensor(
                    qkv_weight_bfr, [lib.KOI_DIM_MAT_Q_K_V, "H", "D", "C", "d", "c"]
                ),
                koi_tensor(sincos_bfr, ["T", "D", "t", "d"]),
                koi_tensor(
                    qkv_bfr, ["N", "T", lib.KOI_DIM_MAT_Q_K_V, "H", "D", "t", "d"]
                ),
                void_ptr(ctr_bfr[0]),
            )
            res = lib.koi_qkv_rotary(*args)
            if res != lib.KOI_SUCCESS:
                return res

            args = (
                stream_ptr,
                win_upper,
                win_lower,
                koi_tensor(
                    qkv_bfr, ["N", "T", lib.KOI_DIM_MAT_Q_K_V, "H", "D", "t", "d"]
                ),
                koi_tensor(attn_out_bfr, ["N", "T", "H", "D", "t", "d"]),
            )
            res = lib.koi_masked_attention(*args)
            if res != lib.KOI_SUCCESS:
                return res

            args = (
                stream_ptr,
                koi_tensor(
                    attn_out_bfr.view((N * T // 16, H * D // 8, 16, 8)),
                    ["M", "K", "m", "k"],
                ),
                koi_tensor(proj_weight_bfr, ["N", "K", "n", "k"]),
                koi_tensor(proj_bias_bfr, ["N"]),
                koi_tensor(
                    proj_out_bfr.view((N * T // 16, C // 8, 16, 8)),
                    ["M", "N", "m", "n"],
                ),
                void_ptr(ctr_bfr[1]),
            )
            res = lib.koi_linear(*args)
            if res != lib.KOI_SUCCESS:
                return res

            args = (
                stream_ptr,
                koi_tensor(proj_out_bfr, ["N", "T", "C", "t", "c"]),
                koi_tensor(in_bfr, ["N", "T", "C", "t", "c"]),
                alpha,
                koi_tensor(residual1_weight_bfr, ["C"]),
                koi_tensor(residual1_out_bfr, ["N", "T", "C", "t", "c"]),
            )
            res = lib.koi_rmsnorm_residual(*args)
            if res != lib.KOI_SUCCESS:
                return res

            args = (
                stream_ptr,
                koi_tensor(
                    residual1_out_bfr.view((N * T // 16, C // 8, 16, 8)),
                    ["M", "K", "m", "k"],
                ),
                koi_tensor(fc1_weight_bfr, ["N", "K", "n", "k"]),
                koi_tensor(fc1_out_bfr, ["M", "N", "m", "n"]),
                void_ptr(ctr_bfr[2]),
            )
            res = lib.koi_mm_swiglu(*args)
            if res != lib.KOI_SUCCESS:
                return res

            args = (
                stream_ptr,
                koi_tensor(fc1_out_bfr, ["M", "K", "m", "k"]),
                koi_tensor(fc2_weight_bfr, ["N", "K", "n", "k"]),
                void_ptr(None),
                koi_tensor(
                    fc2_out_bfr.view((N * T // 16, C // 8, 16, 8)), ["M", "N", "m", "n"]
                ),
                void_ptr(ctr_bfr[3]),
            )
            res = lib.koi_linear(*args)
            if res != lib.KOI_SUCCESS:
                print("F")
                return res

            args = (
                stream_ptr,
                koi_tensor(fc2_out_bfr, ["N", "T", "C", "t", "c"]),
                koi_tensor(residual1_out_bfr, ["N", "T", "C", "t", "c"]),
                alpha,
                koi_tensor(residual2_weight_bfr, ["C"]),
                koi_tensor(residual2_out_bfr, ["N", "T", "C", "t", "c"]),
            )
            return lib.koi_rmsnorm_residual(*args)

        t_koi = time_kernel(50, stream, koi_impl, lib.KOI_SUCCESS)
        t_koi = time_kernel(iters, stream, koi_impl, lib.KOI_SUCCESS)

        ops = T * 3 * C * C
        ops += T * 256 * H * D * 2
        ops += T * C * C
        ops += T * E * C
        ops += T * C * E // 2
        ops *= iters * N * 2
        tflops = 1e-12 * ops / t_koi
        ms_per_iter = 1000 * t_koi / iters

        print(
            f"{dims}, total time {t_koi:.3f}s, time per iter {ms_per_iter:.3f}ms, {tflops:.3f} TFlops"
        )


if __name__ == "__main__":
    for test_dim in test_dims:
        run_whole_tx_layer(test_dim)
