import torch
import pytest
from koi._runtime import lib, ffi
from koi.utils import void_ptr, show_diff_result, time_kernel

dtype = torch.float16
dev = "cuda"

test_dims = ((256, 1000, 8, 64, 10000.0), (128, 1000, 8, 64, 10000.0))
iters = 100


@pytest.mark.parametrize("dims", test_dims)
def test_rotary_embedding(dims):
    N, T, H, D, theta = dims
    dim = D // 2
    stream = torch.cuda.default_stream()
    stream_ptr = ffi.cast("void *", stream.cuda_stream)

    with torch.no_grad():
        torch.manual_seed(42)

        qkv = torch.rand((N, T, 3, H, dim, 2), device=dev, dtype=dtype) * 2 - 1
        out_ref = torch.zeros((3, N, H, T, dim, 2), device=dev, dtype=dtype)
        out_koi = torch.zeros((3, N, H, T, dim, 2), device=dev, dtype=dtype)

        inv_freq = torch.pow(theta, (torch.arange(dim) / -dim))
        freq = torch.arange(T).reshape((T, 1, 1, 1)) * inv_freq
        cos_buf = freq.cos().to(dev)
        sin_buf = freq.sin().to(dev)

        def torch_impl():
            qk_evens = qkv[:, :, :2, :, :, 0]
            qk_odds = qkv[:, :, :2, :, :, 1]
            # permute to [even|odd, N, T, q|k, H, dim]
            qk_output_even_odd = out_ref[:2].permute((5, 1, 3, 0, 2, 4))
            qk_output_even_odd[0] = cos_buf * qk_evens - sin_buf * qk_odds
            qk_output_even_odd[1] = sin_buf * qk_evens + cos_buf * qk_odds
            out_ref[2] = qkv[:, :, 2].transpose(1, 2)

        t_ref = time_kernel(iters, stream, torch_impl, None)

        def koi_impl():
            args = (
                stream_ptr,
                N,
                T,
                H,
                D,
                theta,
                void_ptr(qkv),
                void_ptr(out_koi),
            )
            return lib.host_rotary_embed_transpose_f16(*args)

        t_koi = time_kernel(iters, stream, koi_impl, lib.KOI_SUCCESS)

        label = f"{dims}, (runtime: ref {t_ref:.3f}s, koi {t_koi:.3f}s)"
        show_diff_result(label, out_ref, out_koi, 1e-5, 1e-3, __name__ != "__main__")


if __name__ == "__main__":
    for test_dim in test_dims:
        test_rotary_embedding(test_dim)
