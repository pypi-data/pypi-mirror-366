import torch
import pytest
import sys
from koi._runtime import lib, ffi
from koi.utils import void_ptr, time_kernel, show_diff_result

torch.set_printoptions(linewidth=260)
torch.set_printoptions(sci_mode=False)
torch.cuda.empty_cache()
opts_i8 = {"device": "cuda", "dtype": torch.int8}
opts_i32 = {"device": "cuda", "dtype": torch.int32}
opts_f16 = {"device": "cuda", "dtype": torch.float16}
opts_f32 = {"device": "cuda", "dtype": torch.float32}
dev = torch.device("cuda" if torch.cuda.is_available() else sys.exit("No GPU present"))
stream = torch.cuda.default_stream()
stream_ptr = ffi.cast("void *", stream.cuda_stream)
print(f"\033[1;32mUsing {torch.cuda.get_device_name(dev)} GPU\033[0m")

test_dims = (
    # M, N, K, use_bias, use_float_accum
    (5*32*1024, 512, 512, 0, 0),
    (5*32*1024, 512, 512, 0, 1),
    (5*32*1024, 512, 512, 1, 0),
    (5*32*1024, 512, 512, 1, 1),
    (5*32*1024, 512, 2048, 0, 0),
    (5*32*1024, 512, 2048, 0, 1),
    (5*32*1024, 512, 2048, 1, 0),
    (5*32*1024, 512, 2048, 1, 1),
    
    # M dims to test boundary checks
    # (512, 512, 512, 0, 0),
    # (1024, 512, 512, 0, 1),
    # (2048, 512, 512, 1, 0),
    # (512*9, 512, 512, 1, 1),
    # (512*7, 512, 2048, 0, 0),
    # (512*19, 512, 2048, 0, 1),
)
iters = 500

@pytest.mark.parametrize("dims", test_dims)
def test(dims):
    if lib.koi_volta_tc_is_available(lib.KOI_F16) == lib.KOI_NOT_SUPPORTED:
        print("Volta or Turing GPU not available, skipping tests")
        return
    with torch.no_grad():

        M, N, K, use_bias, use_float_accum = dims
        if use_float_accum:
            torch_dtype = torch.float32
            AccumTypeString = "F32"
            diff_mean = 0.007
            diff_max = 0.07
        else:
            torch_dtype = torch.float16
            AccumTypeString = "F16"
            diff_mean = 0.11
            diff_max = 2.7
        torch.manual_seed(42)

        # PyTorch
        a_bfr = torch.randn((M, K), device=dev, dtype=torch.float16)
        b_bfr = torch.randn((K, N), device=dev, dtype=torch.float16)
        torch_c_bfr = torch.empty((M, N), device=dev, dtype=torch_dtype)
        bias_bfr = torch.randn((N,), device=dev, dtype=torch.float16)

        def torch_impl():
            torch_c_bfr[:] = a_bfr @ b_bfr
            if use_bias:
                torch_c_bfr[:] += bias_bfr
        torch_t = time_kernel(iters, stream, torch_impl, None)

        # Koi
        MemTileA = a_bfr.view(M//16, 16, K//16, 16).permute(0, 2, 1, 3).contiguous() # MKmk
        MemTileB = b_bfr.view(K//16, 16, N//16, 16).permute(2, 0, 3, 1).contiguous() # NKnk
        koi_bias_bfr = bias_bfr
        koi_c_bfr = torch.empty((M//16, 16, N//16, 16), device=dev, dtype=torch.float16).permute(0, 2, 1, 3).contiguous()

        def koi_impl():
            lib.koi_volta_linear(stream_ptr, void_ptr(MemTileA), void_ptr(MemTileB), void_ptr(koi_c_bfr), void_ptr(koi_bias_bfr), use_float_accum, use_bias, M, K)
        koi_t = time_kernel(iters, stream, koi_impl, None)

        ops = iters * 2 * M * N * K
        tflops = 1e-12 * ops / koi_t

        koi_c_bfr = koi_c_bfr.permute(0, 2, 1, 3).reshape(M, N).contiguous()

        label_linear = f"Linear Accum: {AccumTypeString}, Use Bias: {use_bias}, K={K} | Torch {torch_t:.3f}s, Koi {koi_t:.3f}s, {tflops:.3f} TFlops"
        show_diff_result(label_linear, torch_c_bfr, koi_c_bfr, diff_mean, diff_max, __name__ != "__main__")

if __name__ == "__main__":
    for test_dim in test_dims:
        test(test_dim)
