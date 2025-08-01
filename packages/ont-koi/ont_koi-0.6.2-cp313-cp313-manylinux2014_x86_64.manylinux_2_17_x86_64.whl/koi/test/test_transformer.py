import torch
import pytest
from koi._runtime import lib, ffi
from koi.utils import (
    void_ptr,
    check_result,
    time_kernel,
    koi_tensor,
    quantize_tensor,
)

is_main = __name__ == "__main__"

dtype = torch.float16
dev = "cuda"
props = torch.cuda.get_device_properties(dev)

test_dims = (
    (128, 1024, 512),
    (128, 2048, 1536),
)
iters = 200


@pytest.mark.skipif(
    props.major < 8, reason=f"{props.name} compute capability {props.major} < 8"
)
@pytest.mark.parametrize("dims", test_dims)
def test_residual_rmsnorm(dims):
    N, T, C = dims
    stream = torch.cuda.default_stream()
    stream_ptr = ffi.cast("void *", stream.cuda_stream)

    with torch.no_grad():
        torch.manual_seed(42)

        in_bfr = torch.rand((N, T, C), device=dev, dtype=dtype) * 2 - 1
        residual_bfr = torch.rand((N, T, C), device=dev, dtype=dtype) * 2 - 1
        weight = torch.rand((C,), device=dev, dtype=dtype) * 2 - 1
        alpha = torch.ones((1,), device=dev, dtype=dtype) * 0.5
        out_ref = torch.zeros((N, T, C), device=dev, dtype=dtype)
        out_koi = torch.zeros((N, T, C), device=dev, dtype=dtype)
        eps = 1e-5

        def torch_impl():
            x = out_ref
            x[:] = in_bfr + (residual_bfr * alpha)
            rstd = torch.rsqrt(x.square().mean(-1, keepdims=True).add_(eps))
            x.mul_(rstd).mul_(weight)

        t_ref = time_kernel(iters, stream, torch_impl, None)

        args = (
            stream_ptr,
            C,
            N * T,
            void_ptr(in_bfr),
            void_ptr(residual_bfr),
            void_ptr(alpha),
            void_ptr(weight),
            void_ptr(out_koi),
        )

        def koi_linear_impl():
            return lib.host_fused_residual_rmsnorm_f16(*args)

        t_koi = time_kernel(iters, stream, koi_linear_impl, lib.KOI_SUCCESS)

        total_bytes_accessed = iters * N * T * C * 2 * 3
        GBps = total_bytes_accessed / (1024 * 1024 * 1024 * t_koi)

        label = f"Linear: {dims}, ref {t_ref:.3f}s, koi {t_koi:.3f}s, {GBps:.3f} GB/s"
        check_result(label, out_ref, out_koi, True, 2e-5, 2e-3, not is_main)

        # Skip tests below if tensor core kernels are not available
        if lib.koi_tc_is_available(lib.KOI_F16) == lib.KOI_NOT_SUPPORTED:
            return

        out_koi_tiled = torch.zeros(
            (N, T // 16, C // 8, 16, 8), device=dev, dtype=dtype
        )
        # Convert `in_bfr` and `residual_bfr` to tiled (16x8) format
        in_bfr = in_bfr.view((N, T // 16, 16, C // 8, 8)).transpose(2, 3).contiguous()
        residual_bfr = (
            residual_bfr.view((N, T // 16, 16, C // 8, 8)).transpose(2, 3).contiguous()
        )

        args = (
            stream_ptr,
            koi_tensor(in_bfr, ["N", "T", "C", "t", "c"]),
            koi_tensor(residual_bfr, ["N", "T", "C", "t", "c"]),
            0.5,
            koi_tensor(weight, ["C"]),
            koi_tensor(out_koi_tiled, ["N", "T", "C", "t", "c"]),
            void_ptr(None),
            void_ptr(None),
        )

        def koi_tiled_impl():
            return lib.koi_rmsnorm_residual(*args)

        t_koi = time_kernel(iters, stream, koi_tiled_impl, lib.KOI_SUCCESS)

        GBps = total_bytes_accessed / (1024 * 1024 * 1024 * t_koi)
        out_koi_tiled = out_koi_tiled.transpose(2, 3).contiguous().view((N, T, C))

        label = f"Tiled: {dims}, ref {t_ref:.3f}s, koi {t_koi:.3f}s, {GBps:.3f} GB/s"
        check_result(label, out_ref, out_koi_tiled, True, 5e-5, 2e-3, not is_main)
        check_result(
            "Linear/tiled", out_koi, out_koi_tiled, True, 4e-5, 2e-3, not is_main
        )

        # fp8 out

        out_koi_tiled2 = torch.zeros(
            (N, T // 16, C // 8, 16, 8), device=dev, dtype=dtype
        )

        out_koi_tiled_fp8 = torch.zeros(
            (N, T // 16, C // 16, 16, 16), device=dev, dtype=torch.float8_e4m3fn
        )

        args = (
            stream_ptr,
            koi_tensor(in_bfr, ["N", "T", "C", "t", "c"]),
            koi_tensor(residual_bfr, ["N", "T", "C", "t", "c"]),
            0.5,
            koi_tensor(weight, ["C"]),
            koi_tensor(out_koi_tiled2, ["N", "T", "C", "t", "c"]),
            koi_tensor(out_koi_tiled_fp8, ["N", "T", "C", "t", "c"]),
            void_ptr(None),
        )

        def koi_tiled_impl():
            return lib.koi_rmsnorm_residual(*args)

        t_koi = time_kernel(iters, stream, koi_tiled_impl, lib.KOI_SUCCESS)

        GBps = total_bytes_accessed / (1024 * 1024 * 1024 * t_koi)
        out_koi_tiled_fp8 = out_koi_tiled_fp8.transpose(2, 3).contiguous().view((N, T, C)).to(dtype)

        label = f"Tiled: {dims}, ref {t_ref:.3f}s, koi fp8 out {t_koi:.3f}s, {GBps:.3f} GB/s"
        check_result(label, out_ref, out_koi_tiled_fp8, True, 5e-3, 1e-1, not is_main)
        check_result(
            "Linear/tiled", out_koi, out_koi_tiled_fp8, True, 5e-3, 1e-1, not is_main
        )

        # Skip test below if I8 tensor core kernels are not available
        if lib.koi_tc_is_available(lib.KOI_I8) == lib.KOI_NOT_SUPPORTED:
            return

        out_koi_tiled2[:] = 0

        out_koi_i8_tiled = torch.zeros(
            (N, T // 16, C // 16, 16, 16), device=dev, dtype=torch.int8
        )
        out_koi_i8_scale = torch.zeros((N, T), device=dev, dtype=torch.float32)

        args = (
            stream_ptr,
            koi_tensor(in_bfr, ["N", "T", "C", "t", "c"]),
            koi_tensor(residual_bfr, ["N", "T", "C", "t", "c"]),
            0.5,
            koi_tensor(weight, ["C"]),
            koi_tensor(out_koi_tiled2, ["N", "T", "C", "t", "c"]),
            void_ptr(None),
            koi_tensor(
                out_koi_i8_tiled, ["N", "T", "C", "t", "c"], (out_koi_i8_scale, "C")
            ),
        )

        def koi_tiled_impl():
            return lib.koi_rmsnorm_residual(*args)

        t_koi = time_kernel(iters, stream, koi_tiled_impl, lib.KOI_SUCCESS)

        GBps = total_bytes_accessed / (1024 * 1024 * 1024 * t_koi)
        out_koi_tiled2 = out_koi_tiled2.transpose(2, 3).contiguous().view((N, T, C))
        out_koi_i8_tiled = out_koi_i8_tiled.transpose(2, 3).contiguous().view(
            (N, T, C)
        ).float() * out_koi_i8_scale.unsqueeze(-1)

        label = f"Tiled with I8 output: {dims}, ref {t_ref:.3f}s, koi {t_koi:.3f}s, {GBps:.3f} GB/s"
        check_result(label, out_ref, out_koi_i8_tiled, True, 2e-3, 2e-2, not is_main)
        check_result(
            "F16 output same:", out_koi_tiled, out_koi_tiled2, True, 0, 0, not is_main
        )


if is_main:
    for test_dim in test_dims:
        test_residual_rmsnorm(test_dim)
