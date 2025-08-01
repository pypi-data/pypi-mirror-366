import time
import torch
import pytest
from koi._runtime import lib, ffi
from koi.utils import void_ptr, show_diff_result, time_kernel, koi_tensor

dtype = torch.float16
dev = "cuda"

test_dims = (
    (128 * 1024, 512, 512, False),
    (128 * 1024, 512, 512, True),
    (128 * 1024, 4096, 512, False),
    (128 * 1024, 4096, 512, True),
    (128 * 1024, 512, 1536, False),
    (128 * 1024, 512, 1536, True),
    (128 * 1024, 512, 2048, False),
    (128 * 1024, 512, 2048, True),
    (128 * 1024, 512, 6144, False),
    (128 * 1024, 512, 6144, True),
)
iters = 500


def apply_rounding(t, bits):
    t.view(torch.int16).add_(1 << (bits - 1))
    t.view(torch.int16).bitwise_and_(0x10000 - (1 << bits))


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
        out_ref = torch.zeros((M, N), device=dev, dtype=dtype)
        out_koi = torch.zeros((M // 16, N // 8, 16, 8), device=dev, dtype=dtype)

        # apply_rounding(a_bfr, 4)
        # apply_rounding(b_bfr, 4)

        def torch_impl():
            out_ref[:] = a_bfr @ b_bfr.T
            if use_bias:
                out_ref[:] += bias_bfr

        t_ref = time_kernel(iters, stream, torch_impl, None)
        # t_ref = 1

        a_bfr = a_bfr.view((M // 16, 16, K // 8, 8)).transpose(1, 2).contiguous()
        b_bfr = b_bfr.view((N // 16, 16, K // 8, 8)).transpose(1, 2).contiguous()

        ctr_bfr = torch.zeros((iters + 1,), device=dev, dtype=torch.int32)
        ctr = 0

        def koi_impl():
            nonlocal ctr
            args = (
                stream_ptr,
                koi_tensor(a_bfr, ["M", "K", "m", "k"]),
                koi_tensor(b_bfr, ["N", "K", "n", "k"]),
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

        label = f"linear F16 {dims}, ref {t_ref:.3f}s, koi {t_koi:.3f}s, {tflops:.3f} TFlops"
        show_diff_result(label, out_ref, out_koi2, 1e-2, 0.2, __name__ != "__main__")

        a_bfr[:] = 0
        b_bfr[:] = 0
        ctr = 0
        ctr_bfr[:] = 0
        t_koi = time_kernel(iters, stream, koi_impl, lib.KOI_SUCCESS)
        tflops = 1e-12 * ops / t_koi
        print(f"All zero {t_koi:.3f}s, {tflops:.3f} TFlops")


if __name__ == "__main__":
    for test_dim in test_dims:
        test_tiled_linear(test_dim)
