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

# RMSNorm kernel is only ever needed with F16 
test_dims = (
    # N, T, C
    (128, 1024, 512),

    # N and T to test bound checks
    # (32, 512, 512),
    # (64, 512, 512),
    # (96, 512, 512),
    # (128, 512, 512),
    # (32, 1024, 512),
    # (64, 1024, 512),
    # (96, 1024, 512),
    # (128, 1024, 512),
)
iters = 500

@pytest.mark.parametrize("dims", test_dims)
def test(dims):
    if lib.koi_volta_tc_is_available(lib.KOI_F16) == lib.KOI_NOT_SUPPORTED:
        print("Volta or Turing GPU not available, skipping tests")
        return
    with torch.no_grad():

        N, T, C = dims
        eps = 1e-5
        torch.manual_seed(42)

        # PyTorch
        input_bfr = torch.randn((N*T, C), dtype=torch.float16, device=dev)
        residual_bfr = torch.randn((N*T, C), dtype=torch.float16, device=dev)
        weights = torch.randn((C,), dtype=torch.float16, device=dev)
        alpha_bfr = torch.ones((1,), device=dev, dtype=torch.float16) * 0.5
        torch_rmsnorm = torch.empty((N*T, C), device=dev, dtype=torch.float16)

        def torch_impl():
            torch_rmsnorm[:] = input_bfr + (residual_bfr * alpha_bfr)
            rstd = torch.rsqrt(torch_rmsnorm.square().mean(-1, keepdims=True).add_(eps))
            torch_rmsnorm.mul_(rstd).mul_(weights)

        torch_t = time_kernel(iters, stream, torch_impl, None)

        # Koi
        MemTile_residual = residual_bfr.view((N*T)//16, 16, C//16, 16).permute(0, 2, 1, 3).contiguous() # MCmc row-major
        MemTile_input = input_bfr.view((N*T)//16, 16, C//16, 16).permute(0, 2, 1, 3).contiguous()       # MCmc row-major
        koi_rmsnorm = torch.empty((N*T, C), device=dev, dtype=torch.float16).view(N, T//16, 16, C//16, 16).permute(0, 1, 3, 2, 4).contiguous()
        
        def koi_impl():
            lib.koi_volta_rmsnorm_residual(stream_ptr, void_ptr(MemTile_residual), void_ptr(MemTile_input), void_ptr(weights), void_ptr(koi_rmsnorm), alpha_bfr, N*T)
        koi_t = time_kernel(iters, stream, koi_impl, None)

        total_bytes_accessed = iters * N * T * C * 2 * 3
        GBps = total_bytes_accessed / (1024 * 1024 * 1024 * koi_t)

        koi_rmsnorm = koi_rmsnorm.permute(0, 1, 3, 2, 4).reshape(N*T, C).contiguous()

        label_rmsnorm = f"RMSNorm F16 | Torch {torch_t:.3f}s, Koi {koi_t:.3f}s, {GBps:.3f} GBps"
        show_diff_result(label_rmsnorm, torch_rmsnorm, koi_rmsnorm, 0.0002, 0.02, __name__ != "__main__")

if __name__ == "__main__":
    for test_dim in test_dims:
        test(test_dim)
