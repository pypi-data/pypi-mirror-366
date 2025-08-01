import torch
import pytest
from koi._runtime import lib, ffi
from koi.utils import void_ptr, show_diff_result, time_kernel

dtype = torch.float16
dev = "cuda"
props = torch.cuda.get_device_properties(dev)

test_dims = ((32, 32, 128), (128 * 1000, 4096, 512), (528 * 1024, 4096, 512))
iters = 200


@pytest.mark.skipif(props.major < 8, reason=f"{props.name} compute capability {props.major} < 8")
@pytest.mark.skipif(props.major == 8 and props.minor == 6, reason=f"{props.name} compute capability == 8.6")
@pytest.mark.parametrize("dims", test_dims)
def test_linear_swiglu(dims):
    M, N, K = dims
    stream = torch.cuda.default_stream()
    stream_ptr = ffi.cast("void *", stream.cuda_stream)

    with torch.no_grad():
        torch.manual_seed(42)

        input = torch.rand((M, K), device=dev, dtype=dtype) * 0.5 - 0.25
        weights = torch.rand((N, K), device=dev, dtype=dtype) * 0.5 - 0.25
        out_ref = torch.zeros((M, N // 2), device=dev, dtype=dtype)
        out_koi = torch.zeros((M, N // 2), device=dev, dtype=dtype)

        def torch_impl():
            mm = (input @ weights.T).view((M, N // 2, 2))
            out_ref[:] = torch.nn.functional.silu(mm[:, :, 1]) * mm[:, :, 0]

        t_ref = time_kernel(iters, stream, torch_impl, None)

        def koi_impl():
            args = (
                stream_ptr,
                M,
                N,
                K,
                void_ptr(input),
                void_ptr(weights),
                void_ptr(out_koi),
            )
            return lib.host_linear_swiglu_f16(*args)

        t_koi = time_kernel(iters, stream, koi_impl, lib.KOI_SUCCESS)

        ops = iters * M * N * K * 2
        tflops = 1e-12 * ops / t_koi

        label = f"{dims}, (runtime: ref {t_ref:.3f}s, koi {t_koi:.3f}s), {tflops:.3f} TFlops"
        show_diff_result(label, out_ref, out_koi, 2e-4, 2e-2, __name__ != "__main__")


if __name__ == "__main__":
    for test_dim in test_dims:
        test_linear_swiglu(test_dim)
