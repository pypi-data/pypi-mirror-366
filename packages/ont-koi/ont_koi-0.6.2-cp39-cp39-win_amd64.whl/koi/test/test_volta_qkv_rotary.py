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
    # N, T, C, H, D, use_float_accum
    (11*32, 1024, 512, 8, 64, 0),
    (11*32, 1024, 512, 8, 64, 1),

    # N multiple of 32, T multiple of 16, bound check test
    # (8*32, 16*64, 512, 8, 64, 1),
    # (1*32, 16*64, 512, 8, 64, 1),
    # (1*32, 16*64, 512, 8, 64, 0),
    # (1*32, 16*1, 512, 8, 64, 0),
    # (2*32, 16*2, 512, 8, 64, 1),
    # (3*32, 16*3, 512, 8, 64, 0),
    # (4*32, 16*5, 512, 8, 64, 1),
    # (5*32, 16*7, 512, 8, 64, 0),
    # (6*32, 16*53, 512, 8, 64, 1),
    # (7*32, 16*29, 512, 8, 64, 0),
    # (8*32, 16*64, 512, 8, 64, 1),
)
iters = 200

@pytest.mark.parametrize("dims", test_dims)
def test(dims):
    if lib.koi_volta_tc_is_available(lib.KOI_F16) == lib.KOI_NOT_SUPPORTED:
        print("Volta or Turing GPU not available, skipping tests")
        return
    with torch.no_grad():
        N, T, C, H, D, use_float_accum = dims
        theta = 10000.0
        if use_float_accum:
            torch_dtype = torch.float32
            AccumTypeString = "F32"
            diff_mean = 0.003
            diff_max = 0.07
        else:
            torch_dtype = torch.float16
            AccumTypeString = "F16"
            diff_mean = 0.03
            diff_max = 0.7
        torch.manual_seed(42)

        # PyTorch
        a_bfr = torch.randn((N*T, C), device=dev, dtype=torch.float16)
        b_bfr = torch.randn((C, 3*H*D), device=dev, dtype=torch.float16)
        torch_qkv = torch.empty((N*T, 3*H*D), device=dev, dtype=torch_dtype)

        inv_freq = torch.pow(theta, (torch.arange(D//2) / (-D//2)))
        freq = torch.arange(T).reshape((T, 1, 1)) * inv_freq
        cos_buf = freq.cos().to(dev)
        sin_buf = freq.sin().to(dev)

        def torch_impl():
            torch_qkv[:] = a_bfr @ b_bfr 
            torch_qk_even_odd = torch_qkv.view(N, T, 3, H, D//2, 2).permute(5, 2, 0, 1, 3, 4)[:, :2]
            torch_qk_evens = torch_qk_even_odd[0].clone()
            torch_qk_even_odd[0] = cos_buf * torch_qk_evens - sin_buf * torch_qk_even_odd[1]
            torch_qk_even_odd[1] = sin_buf * torch_qk_evens + cos_buf * torch_qk_even_odd[1]
        torch_t = time_kernel(iters, stream, torch_impl, None)

        # Koi
        sincos_bfr = torch.empty((T, D//2, 2), device=dev, dtype=torch.float16)
        sincos_bfr[:, :, 0] = sin_buf[:, 0]
        sincos_bfr[:, :, 1] = cos_buf[:, 0]
        sincos_bfr = sincos_bfr.view(T // 16, 2, 2, 4, D // 16, 2, 8).permute(0, 4, 5, 2, 1, 3, 6).contiguous() # Turn it to MemTile row-major format, as that is how it will be loaded.

        # MemTileA = a_bfr.view((N*T)//16, 16, C//16, 16).permute(0, 2, 1, 3).contiguous()    # MKmk row-major
        MemTileA = a_bfr.view(N, T//16, 16, C//16, 16).transpose(2, 3).contiguous()    # MKmk row-major
        MemTileB = b_bfr.view(C//16, 16, (3*H*D)//16, 16).permute(2, 0, 3, 1).contiguous()    # NKnk col-major
        koi_qkv = torch.empty((N, T // 16, 3, H, D // 16, 16, 16), dtype=torch.float16, device=dev)  # MNmn row-major

        def koi_impl():
            lib.koi_volta_qkv_rotary(stream_ptr, void_ptr(MemTileA), void_ptr(MemTileB), void_ptr(koi_qkv), void_ptr(sincos_bfr), use_float_accum, N, T)
        koi_t = time_kernel(iters, stream, koi_impl, None)

        tflops = 1e-12 * ((iters * koi_qkv.numel() * C * 2) / koi_t)

        koi_qkv = koi_qkv.permute(0, 1, 5, 2, 3, 4, 6).reshape(N*T, 3*H*D).contiguous()

        label_qkv_rotary = f"QKV+RoPE Accum: {AccumTypeString} | Torch {torch_t:.3f}s, Koi {koi_t:.3f}s, {tflops:.3f} TFlops"
        show_diff_result(label_qkv_rotary, torch_qkv, koi_qkv, diff_mean, diff_max, __name__ != "__main__")

if __name__ == "__main__":
    for test_dim in test_dims:
        test(test_dim)
