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
    # M, N, K, use_float_accum
    (1024*32, 4096, 512, 0),
    (1024*32, 4096, 512, 1),

    # M dims to test boundary checks
    # (512, 4096, 512, 0),
    # (1024, 4096, 512, 1),
    # (2048, 4096, 512, 0),
    # (512*9, 4096, 512, 1),
    # (512*97, 4096, 512, 0),
    # (512*89, 4096, 512, 1),
)
iters = 500

@pytest.mark.parametrize("dims", test_dims)
def test(dims):
    if lib.koi_volta_tc_is_available(lib.KOI_F16) == lib.KOI_NOT_SUPPORTED:
        print("Volta or Turing GPU not available, skipping tests")
        return
    with torch.no_grad():

        M, N, K, use_float_accum = dims
        if use_float_accum:
            torch_dtype = torch.float32
            AccumTypeString = "F32"
            diff_mean = 0.04
            diff_max = 10
        else:
            torch_dtype = torch.float16
            AccumTypeString = "F16"
            diff_mean = 0.4
            diff_max = 45
        torch.manual_seed(42)

        # PyTorch
        a_bfr = torch.randn((M, K), device=dev, dtype=torch.float16)
        b_bfr = torch.randn((K, N), device=dev, dtype=torch.float16)
        torch_c_bfr = torch.empty((M, N//2), device=dev, dtype=torch_dtype)

        def torch_impl():
            mm = (a_bfr @ b_bfr).view(M, 2, N//2)
            torch_c_bfr[:] = torch.nn.functional.silu(mm[:, 1]) * mm[:, 0]
        torch_t = time_kernel(iters, stream, torch_impl, None)

        # Koi
        MemTileA = a_bfr.view(M//16, 16, K//16, 16).permute(0, 2, 1, 3).contiguous()    # MKmk row-major
        b_bfr_interleaved = b_bfr.unflatten(1, (2, -1, 16)).transpose(1, 2).contiguous()
        MemTileB = b_bfr_interleaved.view(K//16, 16, N//16, 16).permute(2, 0, 3, 1).contiguous()    # NKnk col-major
        koi_c_bfr = torch.empty((M//16, 16, (N//(16*2)), 16), device=dev, dtype=torch.float16).permute(0, 2, 1, 3).contiguous()
        
        def koi_impl():
            lib.koi_volta_mm_swiglu(stream_ptr, void_ptr(MemTileA), void_ptr(MemTileB), void_ptr(koi_c_bfr), use_float_accum, M)
        koi_t = time_kernel(iters, stream, koi_impl, None)

        ops = iters * 2 * M * N * K
        tflops = 1e-12 * ops / koi_t

        koi_c_bfr = koi_c_bfr.permute(0, 2, 1, 3).reshape(M, N//2).contiguous()

        label_swiglu = f"Swiglu Accum: {AccumTypeString} | Torch {torch_t:.3f}s, Koi {koi_t:.3f}s, {tflops:.3f} TFlops"
        show_diff_result(label_swiglu, torch_c_bfr, koi_c_bfr, diff_mean, diff_max, __name__ != "__main__")

if __name__ == "__main__":
    for test_dim in test_dims:
        test(test_dim)
