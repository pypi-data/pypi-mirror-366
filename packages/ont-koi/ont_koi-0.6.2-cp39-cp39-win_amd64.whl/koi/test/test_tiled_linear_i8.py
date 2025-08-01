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
is_main = __name__ == "__main__"

print(f"Running on: {torch.cuda.get_device_name(dev)}")

M_dim = 64 * 1024
test_dims = (
    (M_dim, 512, 512, False),
    (M_dim, 512, 512, True),
    (M_dim, 4096, 512, False),
    (M_dim, 4096, 512, True),
    (M_dim, 512, 1536, False),
    (M_dim, 512, 1536, True),
    (M_dim, 512, 2048, False),
    (M_dim, 512, 2048, True),
    (M_dim, 512, 6144, False),
    (M_dim, 512, 6144, True),
)
iters = 200


@pytest.mark.parametrize("dims", test_dims)
def test_tiled_linear(dims):
    if lib.koi_tc_is_available(lib.KOI_F16) == lib.KOI_NOT_SUPPORTED:
        print("Koi tensor core kernels not available, skipping test")
        return

    M, N, K, use_bias = dims
    stream = torch.cuda.default_stream()
    stream_ptr = ffi.cast("void *", stream.cuda_stream)

    with torch.no_grad():
        torch.manual_seed(42)

        a_bfr = torch.rand((M, K), device=dev, dtype=dtype) * 2 - 1
        b_bfr = torch.rand((N, K), device=dev, dtype=dtype) * 2 - 1
        if use_bias:
            bias_bfr = torch.rand((N,), device=dev, dtype=dtype) * 2 - 1
        a_scale, a_bfr_i8 = quantize_tensor(a_bfr, 256, -1)
        a_scale.reciprocal_()
        a_bfr_i8_tiled = (
            a_bfr_i8.view((M // 16, 16, K // 16, 16)).transpose(1, 2).contiguous()
        )

        b_scale, b_bfr_i8 = quantize_tensor(b_bfr, 256, -1)
        b_scale.reciprocal_()
        b_bfr_i8_tiled = (
            b_bfr_i8.view((N // 16, 16, K // 16, 16)).transpose(1, 2).contiguous()
        )

        out_ref = a_bfr_i8.float() @ b_bfr_i8.float().T
        out_ref = out_ref * (a_scale.unsqueeze(-1) @ b_scale.unsqueeze(0))
        if use_bias:
            out_ref[:] += bias_bfr
        out_ref = out_ref.to(dtype)

        out_koi = torch.zeros((M // 16, N // 8, 16, 8), device=dev, dtype=dtype)
        ctr_bfr = torch.zeros((iters + 1,), device=dev, dtype=torch.int32)
        ctr = 0

        def koi_impl():
            nonlocal ctr
            args = (
                stream_ptr,
                koi_tensor(a_bfr_i8_tiled, ["M", "K", "m", "k"], (a_scale, "K")),
                koi_tensor(b_bfr_i8_tiled, ["N", "K", "n", "k"], (b_scale, "K")),
                koi_tensor(bias_bfr, ["N"]) if use_bias else void_ptr(None),
                koi_tensor(out_koi, ["M", "N", "m", "n"]),
                void_ptr(ctr_bfr[ctr]),
            )
            ctr += 1
            return lib.koi_linear(*args)

        t_koi = time_kernel(iters // 2, stream, koi_impl, lib.KOI_SUCCESS)
        ctr = 0
        ctr_bfr[:] = 0
        t_koi = time_kernel(iters, stream, koi_impl, lib.KOI_SUCCESS)

        ops = iters * out_koi.numel() * K * 2
        tflops = 1e-12 * ops / t_koi

        out_koi2 = out_koi.permute((0, 2, 1, 3)).contiguous().view((M, N))

        # Time with all-zero inputs (lower power, runs at higher clock speeds)
        a_bfr_i8_tiled[:] = 0
        b_bfr_i8_tiled[:] = 0
        ctr = 0
        ctr_bfr[:] = 0
        t_koi_az = time_kernel(iters, stream, koi_impl, lib.KOI_SUCCESS)
        tflops_az = 1e-12 * ops / t_koi_az

        label = f"linear I8 {str(dims):30}, {t_koi:.3f}s, {tflops:.3f} TFlops"
        label += f" (all zero: {t_koi_az:.3f}s, {tflops_az:.3f} TFlops)"
        # TODO: if `not use_bias`, the tolerances should really be zero, but this would
        # TODO:  currently cause test failures on CC8.6/8.9 (DOR-1003)
        abs_limit = 0.2 if (K == 1536) else 0.125
        show_diff_result(label, out_ref, out_koi2, 5e-3, abs_limit, is_main)


if is_main:
    for test_dim in test_dims:
        test_tiled_linear(test_dim)
