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
    # N, T, H, D, window
    (256, 1024, 8, 64, (127, 128)),
    (128, 512, 8, 64, (127, 128)),

    # N multiple of 32, T multiple of 16, bound check test
    # (32, 16, 8, 64, (127, 128)),
    # (64, 32, 8, 64, (127, 128)),
    # (96, 64, 8, 64, (127, 128)),
    # (128, 512, 8, 64, (127, 128)),
    # (128, 1024, 8, 64, (127, 128)),
    # (32, 1024, 8, 64, (127, 128)),
    # (64, 1024, 8, 64, (127, 128)),
    # (96, 1024, 8, 64, (127, 128)),
    # (128, 1024, 8, 64, (127, 128)),
)
iters = 500

@pytest.mark.parametrize("dims", test_dims)
def test(dims):
    if lib.koi_volta_tc_is_available(lib.KOI_F16) == lib.KOI_NOT_SUPPORTED:
        print("Volta or Turing GPU not available, skipping tests")
        return
    with torch.no_grad():

        N, T, H, D, window = dims
        win_upper, win_lower = window
        win_size = win_upper + win_lower + 1
        torch.manual_seed(42)

        # PyTorch
        qkv = torch.randn((3, N, H, T, D), device=dev, dtype=torch.float16)
        tiled_mask = (torch.ones((T // 16, T // 16), device=dev, dtype=torch.float16).triu_(-8).tril_(8).bool())
        tiled_mask = tiled_mask.repeat_interleave(16, dim=0).repeat_interleave(16, dim=1)
        torch_attention_full_nomask = torch.empty((N, T, H, D), device=dev, dtype=torch.float32)

        def torch_impl_full_tiled():
            torch_attention_full_nomask[:] = torch.nn.functional.scaled_dot_product_attention(qkv[0], qkv[1], qkv[2], tiled_mask).transpose(1, 2)
        torch_t = time_kernel(iters, stream, torch_impl_full_tiled, None)

        # Koi
        koi_qkv = qkv.view(3, N, H, T // 16, 16, D // 16, 16).permute(1, 3, 0, 2, 5, 4, 6).contiguous() # NT3HDtd
        koi_attention = torch.empty((N, T // 16, H, D // 16, 16, 16), device=dev, dtype=torch.float16)

        def koi_impl():
            lib.koi_volta_attn(stream_ptr, void_ptr(koi_qkv), void_ptr(koi_attention), N, T)
        koi_t = time_kernel(iters, stream, koi_impl, None)

        ops = iters * 2 * N * T * H * win_size * D * 2
        tflops = 1e-12 * ops / koi_t

        koi_attention = koi_attention.permute(0, 1, 4, 2, 3, 5).reshape(N, T, H, D).contiguous()

        label_attn = f"Window FlashAttention Accum and Online Softmax F16 | Torch {torch_t:.3f}s, Koi {koi_t:.3f}s, {tflops:.3f} TFlops"
        show_diff_result(label_attn, torch_attention_full_nomask, koi_attention, 0.0002, 0.011, __name__ != "__main__")

if __name__ == "__main__":
    for test_dim in test_dims:
        test(test_dim)
