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
    # N, T, C, In_Amp, Res_Amp, Out_Amp
    (128, 1024, 512, 1),
    (128, 1024, 1536, 1),
    (128, 1024, 512, 0),
    (128, 1024, 1536, 0),
)
iters = 500

@pytest.mark.parametrize("dims", test_dims)
def test(dims):
    if lib.koi_hopper_tc_is_available(lib.KOI_E4M3) == lib.KOI_NOT_SUPPORTED:
        print("GPU isn't Hopper, skipping test")
        return
    with torch.no_grad():

        N, T, C, in_ampere_layout = dims
        eps = 1e-5
        torch.manual_seed(42)

        # PyTorch
        if in_ampere_layout:
            input_bfr = torch.randn((N*T, C), dtype=torch.float16, device=dev)
        else:
            input_bfr = torch.randint(-3, 4, (N*T, C), device=dev, dtype=torch.int32) / 16 # Torch doesn't have randn implemented for float8 yet
            input_bfr = input_bfr.to(torch.float8_e4m3fn)
        residual_bfr = torch.randn((N*T, C), dtype=torch.float16, device=dev)
        weights = torch.randn((C,), dtype=torch.float16, device=dev)
        alpha_bfr = torch.ones((1,), device=dev, dtype=torch.float16) * 0.5
        torch_rmsnorm = torch.empty((N*T, C), device=dev, dtype=torch.float32)

        def torch_impl():
            torch_rmsnorm[:] = input_bfr.half() + (residual_bfr * alpha_bfr)
            rstd = torch.rsqrt(torch_rmsnorm.square().mean(-1, keepdims=True).add_(eps))
            torch_rmsnorm.mul_(rstd).mul_(weights)

        torch_t = time_kernel(iters, stream, torch_impl, None)
        # torch_t = 1

        # Koi
        if in_ampere_layout:
            MemTile_input = input_bfr.view((N*T)//16, 16, C//8, 8).permute(0, 2, 1, 3).contiguous()       # MCmc row-major
            MemTile_residual = residual_bfr.view((N*T)//16, 16, C//8, 8).permute(0, 2, 1, 3).contiguous() # MCmc row-major
            koi_weights = weights.view(-1, 8).repeat(1, 8).flatten() # Smem conflicts reasons
            koi_out_fp16 = torch.zeros((N*T, C), device=dev, dtype=torch.float16).view((N*T)//256, 256//64, 64//8, 8, C//128, 128//32, 32//16, 16).permute(0, 4, 1, 5, 2, 6, 3, 7).contiguous()
            koi_out_fp8 = torch.zeros((N*T, C), device=dev, dtype=torch.float8_e4m3fn).view((N*T)//256, 256//64, 64//8, 8, C//128, 128//32, 32//16, 16).permute(0, 4, 1, 5, 2, 6, 3, 7).contiguous()
        else:
            MemTile_input = input_bfr.view((N*T)//256, 256//64, 64//8, 8, C//128, 128//32, 32//16, 16).permute(0, 4, 1, 5, 2, 6, 3, 7).contiguous()
            MemTile_residual = residual_bfr.view((N*T)//256, 256//64, 64//8, 8, C//128, 128//32, 32//16, 16).permute(0, 4, 1, 5, 2, 6, 3, 7).contiguous()
            koi_weights = weights.view(-1, 16).repeat(1, 4).flatten() # Smem conflicts reasons
            koi_out_fp16 = torch.zeros((N*T, C), device=dev, dtype=torch.float16).view((N*T)//16, 16, C//8, 8).permute(0, 2, 1, 3).contiguous()
            koi_out_int8 = torch.zeros((N*T, C), device=dev, dtype=torch.int8).view((N*T)//16, 16, C//16, 16).permute(0, 2, 1, 3).contiguous()
            koi_out_scale_factor = torch.zeros((N*T), device=dev, dtype=torch.float32)

        def koi_impl_amp_in():
            lib.koi_rmsnorm_hopper(stream_ptr, void_ptr(MemTile_input), void_ptr(MemTile_residual), void_ptr(koi_weights), void_ptr(koi_out_fp16), void_ptr(koi_out_fp8), void_ptr(None), N*T, C, alpha_bfr, in_ampere_layout)
        def koi_impl_hop_in():
            lib.koi_rmsnorm_hopper(stream_ptr, void_ptr(MemTile_input), void_ptr(MemTile_residual), void_ptr(koi_weights), void_ptr(koi_out_fp16), void_ptr(koi_out_int8), void_ptr(koi_out_scale_factor), N*T, C, alpha_bfr, in_ampere_layout)
        if in_ampere_layout:
            koi_t = time_kernel(iters, stream, koi_impl_amp_in, None)
        else:
            koi_t = time_kernel(iters, stream, koi_impl_hop_in, None)

        total_bytes_accessed = iters * N * T * C * 2 * 3
        GBps = total_bytes_accessed / (1024 * 1024 * 1024 * koi_t)

        if in_ampere_layout:
            koi_out_fp16 = koi_out_fp16.permute(0, 2, 4, 6, 1, 3, 5, 7).reshape(N*T, C).contiguous()
            koi_out_fp8 = koi_out_fp8.permute(0, 2, 4, 6, 1, 3, 5, 7).reshape(N*T, C).contiguous()
        else:
            koi_out_fp16 = koi_out_fp16.permute(0, 2, 1, 3).reshape(N*T, C).contiguous()
            koi_out_int8 = koi_out_int8.permute(0, 2, 1, 3).reshape(N*T, C).contiguous()
            koi_out_int8_scaled = koi_out_int8 * koi_out_scale_factor.unsqueeze(1)

        if in_ampere_layout:
            label_rmsnorm = f"RMSNorm InAmpere F16 M={N}*{T}, C={C} | Torch {torch_t:.3f}s, Koi {koi_t:.3f}s, {GBps:.3f} GBps"
            show_diff_result(label_rmsnorm, torch_rmsnorm, koi_out_fp16, 0.0002, 0.02, __name__ != "__main__")
            label_rmsnorm = f"RMSNorm InAmpere F8 M={N}*{T}, C={C} | Torch {torch_t:.3f}s, Koi {koi_t:.3f}s, {GBps:.3f} GBps"
            show_diff_result(label_rmsnorm, torch_rmsnorm, koi_out_fp8, 0.02, 1, __name__ != "__main__")
        else:
            label_rmsnorm = f"RMSNorm InHopper F16 M={N}*{T}, C={C} | Torch {torch_t:.3f}s, Koi {koi_t:.3f}s, {GBps:.3f} GBps"
            show_diff_result(label_rmsnorm, torch_rmsnorm, koi_out_fp16, 0.0002, 0.02, __name__ != "__main__")
            label_rmsnorm = f"RMSNorm InHopper F8 M={N}*{T}, C={C} | Torch {torch_t:.3f}s, Koi {koi_t:.3f}s, {GBps:.3f} GBps"
            show_diff_result(label_rmsnorm, torch_rmsnorm, koi_out_int8_scaled, 0.025, 12, __name__ != "__main__")

if __name__ == "__main__":
    for test_dim in test_dims:
        test(test_dim)
