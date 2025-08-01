import time
import torch
import pytest
import sys
from koi._runtime import lib, ffi
from koi.utils import (
    void_ptr,
    show_diff_result,
    time_kernel,
    koi_tensor,
    quantize_tensor,
)

dev = torch.device("cuda" if torch.cuda.is_available() else sys.exit("No GPU present"))
torch.set_printoptions(linewidth=260)
torch.set_printoptions(sci_mode=False)
print(f"\033[1;32mUsing {torch.cuda.get_device_name(dev)} GPU\033[0m")

test_dims = (
    # M, N, K
    (64 * 1024, 4096, 512),
    (64 * 1024, 4096, 1536),
)
iters = 500

@pytest.mark.parametrize("dims", test_dims)
def test_tiled_swiglu(dims):
    if lib.koi_hopper_tc_is_available(lib.KOI_E4M3) == lib.KOI_NOT_SUPPORTED:
        print("GPU isn't Hopper, skipping test")
        return
    
    M, N, K = dims
    if K == 512:
        mean_diff_limit = 0.004
        max_diff_limit = 0.25
    else:
        mean_diff_limit = 0.012
        max_diff_limit = 1
    stream = torch.cuda.default_stream()
    stream_ptr = ffi.cast("void *", stream.cuda_stream)
    with torch.no_grad():
        torch.manual_seed(42)

        core_matrix_mn, core_matrix_k = 8, 16
        wgmma_m, wgmma_n, wgmma_k = 64, 256, 32
        smem_tile_m, smem_tile_n, smem_tile_k = 256, 256, 128

        input = torch.rand((M, K), device=dev, dtype=torch.float16) * 0.5 - 0.25 
        weights = torch.rand((K, N), device=dev, dtype=torch.float16) * 0.5 - 0.25
        mm = torch.zeros((M, N//2, 2), device=dev, dtype=torch.float16)
        out_torch = torch.zeros((M, N // 2), device=dev, dtype=torch.float8_e4m3fn)

        def torch_impl():
            mm[:] = (input.half() @ weights.half()).view((M, N // 2, 2))    # Changed from .float() to .half()
            out_torch[:] = torch.nn.functional.silu(mm[:, :, 1]) * mm[:, :, 0]
        t_ref = time_kernel(iters, stream, torch_impl, None)
        # t_ref = 1

        # Koi
        input = input.view(M//smem_tile_m, smem_tile_m//wgmma_m, wgmma_m//core_matrix_mn, core_matrix_mn, 
                           K//smem_tile_k, smem_tile_k//wgmma_k, wgmma_k//core_matrix_k, core_matrix_k).permute(0, 4, 1, 5, 2, 6, 3, 7).contiguous()
        weights = weights.view(K, N//32, 4, 4, 2).transpose(2, 3).contiguous().reshape(K, N)    # Interleave weights for FP8 store to GMEM
        weights = weights.view(K//smem_tile_k, smem_tile_k//wgmma_k, wgmma_k//core_matrix_k, core_matrix_k,
                               N//smem_tile_n, smem_tile_n//wgmma_n, wgmma_n//core_matrix_mn, core_matrix_mn).permute(4, 0, 5, 1, 6, 2, 7, 3).contiguous()
        # Layout(C) == Layout(A)
        input = input.to(torch.float8_e4m3fn)
        weights = weights.to(torch.float8_e4m3fn)
        out_koi_tiled_fp8 = torch.zeros((M, N//2), device=dev, dtype=torch.float8_e4m3fn).view(M//smem_tile_m, smem_tile_m//wgmma_m, wgmma_m//core_matrix_mn, core_matrix_mn,
                                                                                              (N//2)//smem_tile_k, smem_tile_k//wgmma_k, wgmma_k//core_matrix_k, core_matrix_k).permute(0, 4, 1, 5, 2, 6, 3, 7).contiguous()

        def koi_impl_fp8():
            return lib.koi_swiglu_hopper(stream_ptr, void_ptr(input), void_ptr(weights), void_ptr(out_koi_tiled_fp8), M, N, K)
        
        t_koi = time_kernel(iters, stream, koi_impl_fp8, lib.KOI_SUCCESS)
        ops = iters * M * N * K * 2
        tflops = 1e-12 * ops / t_koi

        out_koi = out_koi_tiled_fp8.permute(0, 2, 4, 6, 1, 3, 5, 7).reshape(M, N//2)
        label = f"{dims}, ref {t_ref:.3f}s, koi {t_koi:.3f}s, {tflops:.3f} TFlops"
        show_diff_result(label, out_torch, out_koi, mean_diff_limit, max_diff_limit, __name__ != "__main__")

        input = input.to(torch.float16)
        input[:] = 0
        input = input.to(torch.float8_e4m3fn)
        weights = weights.to(torch.float16)
        weights[:] = 0
        weights = weights.to(torch.float8_e4m3fn)
        t_koi = time_kernel(iters, stream, koi_impl_fp8, lib.KOI_SUCCESS)
        tflops = 1e-12 * ops / t_koi
        print(f"All zero {t_koi:.3f}s, {tflops:.3f} TFlops")

if __name__ == "__main__":
    for test_dim in test_dims:
        test_tiled_swiglu(test_dim)