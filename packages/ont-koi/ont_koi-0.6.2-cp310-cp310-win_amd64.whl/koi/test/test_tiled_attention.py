import time
import torch
import pytest
from koi._runtime import lib, ffi
from koi.utils import void_ptr, show_diff_result, time_kernel, koi_tensor
from math import sqrt

dtype = torch.float16
dev = "cuda"
props = torch.cuda.get_device_properties(dev)

print(f"Running on: {torch.cuda.get_device_name(dev)}")

test_dims = (
    (64, 1024, 8, 64, (127, 128)),
    (64, 1024, 24, 64, (255, 256)),
)
iters = 200


@pytest.mark.skipif(props.major < 8, reason=f"{props.name} compute capability < 8.0")
@pytest.mark.parametrize("dims", test_dims)
def test_tiled_attention(dims):
    if lib.koi_tc_is_available(lib.KOI_F16) == lib.KOI_NOT_SUPPORTED:
        print("Koi tensor core kernels not available, skipping test")
        return

    N, T, H, D, window = dims
    win_upper, win_lower = window
    win_size = win_upper + win_lower + 1
    stream = torch.cuda.default_stream()
    stream_ptr = ffi.cast("void *", stream.cuda_stream)

    with torch.no_grad():
        torch.manual_seed(42)

        qkv = torch.rand((3, N, H, T, D), device=dev, dtype=dtype) * 0.25 - 0.125
        tri_mask = (
            torch.ones((T, T), device=dev, dtype=dtype)
            .triu_(-win_upper)
            .tril_(win_lower)
            .bool()
        )
        tile_size = 16
        tiled_T = T // tile_size
        tiled_mask = (
            torch.ones((tiled_T, tiled_T), device=dev, dtype=dtype)
            .triu_(-((win_size // 2) // 16))
            .tril_((win_size // 2) // 16)
            .bool()
        )
        tiled_mask = tiled_mask.repeat_interleave(tile_size, dim=0).repeat_interleave(
            tile_size, dim=1
        )

        out_tsplit_nomask = torch.zeros((N, T, H, D), device=dev, dtype=dtype)
        out_tsplit_tri = torch.zeros((N, T, H, D), device=dev, dtype=dtype)
        out_full_nomask = torch.zeros((N, T, H, D), device=dev, dtype=dtype)
        out_full_tiled = torch.zeros((N, T, H, D), device=dev, dtype=dtype)
        out_full_tri = torch.zeros((N, T, H, D), device=dev, dtype=dtype)
        out_koi = torch.zeros((N, T // 16, H, D // 8, 16, 8), device=dev, dtype=dtype)

        num_splits = 12

        def scaled_dot_product_attention(q, k, v, mask):
            return torch.nn.functional.scaled_dot_product_attention(
                q, k, v, mask
            ).transpose(1, 2)

        def get_tsplit_impl(use_mask, out):
            def torch_tsplit():
                for i in range(num_splits):
                    qb = i * T // num_splits
                    qe = (i * T + T) // num_splits
                    kvb = max(0, qb - win_lower)
                    kve = min(T, qe + win_upper)
                    q = qkv[0, :, :, qb:qe]
                    kv = qkv[1:, :, :, kvb:kve]
                    mask = tri_mask[qb:qe, kvb:kve] if use_mask else None
                    out[:, qb:qe] = scaled_dot_product_attention(q, kv[0], kv[1], mask)

            return torch_tsplit

        def torch_full_nomask():
            out_full_nomask[:] = scaled_dot_product_attention(
                qkv[0], qkv[1], qkv[2], None
            )

        def torch_full_tiled():
            out_full_tiled[:] = scaled_dot_product_attention(
                qkv[0], qkv[1], qkv[2], tiled_mask
            )

        def torch_full_tri():
            out_full_tri[:] = scaled_dot_product_attention(
                qkv[0], qkv[1], qkv[2], tri_mask
            )

        ref_results = []
        ref_impls = [
            ("full (triangle mask)", torch_full_tri, out_full_tri, False),
            ("full (tiled mask)", torch_full_tiled, out_full_tiled, True),
            ("full (no mask)", torch_full_nomask, out_full_nomask, False),
            (
                "tsplit (triangle mask)",
                get_tsplit_impl(True, out_tsplit_tri),
                out_tsplit_tri,
                False,
            ),
            (
                "tsplit (no mask)",
                get_tsplit_impl(False, out_tsplit_nomask),
                out_tsplit_nomask,
                False,
            ),
        ]
        for descr, impl, ref_out, assert_similar in ref_impls:
            ref_results.append(
                (descr, time_kernel(iters, stream, impl, None), ref_out, assert_similar)
            )

        qkv = (
            qkv.view((3, N, H, T // 16, 16, D // 8, 8))
            .permute((1, 3, 0, 2, 5, 4, 6))
            .contiguous()
        )

        # qkv -> N, T // 16, 3, H, D // 8, 16, 8
        # transpose8x8 V
        qkv[:, :, 2, :, :, 0:8, :] = (
            qkv[:, :, 2, :, :, 0:8, :].transpose(-2, -1).clone()
        )
        qkv[:, :, 2, :, :, 8:16, :] = (
            qkv[:, :, 2, :, :, 8:16, :].transpose(-2, -1).clone()
        )

        def koi_impl():
            args = (
                stream_ptr,
                win_upper,
                win_lower,
                koi_tensor(qkv, ["N", "T", lib.KOI_DIM_MAT_Q_K_V, "H", "D", "t", "d"]),
                koi_tensor(out_koi, ["N", "T", "H", "D", "t", "d"]),
            )
            return lib.koi_masked_attention(*args)

        ops = iters * 2 * N * T * H * win_size * D * 2

        t_koi = time_kernel(iters, stream, koi_impl, lib.KOI_SUCCESS)
        tflops = 1e-12 * ops / t_koi
        out_koi = out_koi.permute((0, 1, 4, 2, 3, 5)).contiguous().view((N, T, H, D))

        for descr, t_ref, out_ref, assert_similar in ref_results:
            label = f"ref ({descr}) {t_ref:.3f}s, koi {t_koi:.3f}s, {tflops:.3f} TFlops"
            show_diff_result(
                label,
                out_ref,
                out_koi,
                1e-6,
                2e-5,
                assert_similar and __name__ != "__main__",
            )


if __name__ == "__main__":
    for test_dim in test_dims:
        test_tiled_attention(test_dim)
