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
    (64 * 1024, 512, 2048),
    (64 * 1024, 1536, 2048),
    # (16 * 4096, 2048, 4096),
    # (16 * 4096, 8192, 8192),
)
iters = 500

@pytest.mark.parametrize("dims", test_dims)
def test_tiled_mm(dims):
    if lib.koi_hopper_tc_is_available(lib.KOI_E4M3) == lib.KOI_NOT_SUPPORTED:
        print("GPU isn't Hopper, skipping test")
        return
    
    M, N, K = dims
    stream = torch.cuda.default_stream()
    stream_ptr = ffi.cast("void *", stream.cuda_stream)
    with torch.no_grad():
        torch.manual_seed(42)

        core_matrix_mn, core_matrix_k = 8, 16
        wgmma_m, wgmma_n, wgmma_k = 64, 256, 32
        smem_tile_m, smem_tile_n, smem_tile_k = 256, 256, 128

        input = torch.randn((M, K), device=dev, dtype=torch.float16).to(torch.float8_e4m3fn)
        weights = torch.randn((K, N), device=dev, dtype=torch.float16).to(torch.float8_e4m3fn)
        out_torch = torch.zeros((M, N), device=dev, dtype=torch.float8_e4m3fn)

        def torch_impl():
            out_torch[:] = input.half() @ weights.half()
            # out_torch[:], _ = torch._scaled_mm(input, weights.t().contiguous().t(), out_dtype=torch.float16, use_fast_accum=True)
        t_ref = time_kernel(iters, stream, torch_impl, None)
        # t_ref = 1

        # Koi
        input = input.view(M//smem_tile_m, smem_tile_m//wgmma_m, wgmma_m//core_matrix_mn, core_matrix_mn, 
                           K//smem_tile_k, smem_tile_k//wgmma_k, wgmma_k//core_matrix_k, core_matrix_k).permute(0, 4, 1, 5, 2, 6, 3, 7).contiguous()
        weights = weights.view(K, N // 16, 4, 2, 2).transpose(2, 3).contiguous().reshape(K, N)    # Interleave weights for FP8 store to GMEM
        weights = weights.view(K//smem_tile_k, smem_tile_k//wgmma_k, wgmma_k//core_matrix_k, core_matrix_k,
                               N//smem_tile_n, smem_tile_n//wgmma_n, wgmma_n//core_matrix_mn, core_matrix_mn).permute(4, 0, 5, 1, 6, 2, 7, 3).contiguous()
        out_koi_tiled_fp8 = torch.zeros((M, N), device=dev, dtype=torch.float8_e4m3fn).view(M//smem_tile_m, smem_tile_m//wgmma_m, wgmma_m//core_matrix_mn, core_matrix_mn,
                                                                                            N//smem_tile_k, smem_tile_k//wgmma_k, wgmma_k//core_matrix_k, core_matrix_k).permute(0, 4, 1, 5, 2, 6, 3, 7).contiguous()
        def koi_impl_fp8():
            return lib.koi_matmul_hopper(stream_ptr, void_ptr(input), void_ptr(weights), void_ptr(out_koi_tiled_fp8), M, N, K)
        
        t_koi = time_kernel(iters, stream, koi_impl_fp8, lib.KOI_SUCCESS)
        ops = iters * M * N * K * 2
        tflops = 1e-12 * ops / t_koi

        out_koi = out_koi_tiled_fp8.permute(0, 2, 4, 6, 1, 3, 5, 7).reshape(M, N)
        label = f"{dims}, ref {t_ref:.3f}s, koi {t_koi:.3f}s, {tflops:.3f} TFlops"
        show_diff_result(label, out_torch, out_koi, 0.04, 16, __name__ != "__main__")

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
        test_tiled_mm(test_dim)
