import torch
import pytest
from koi._runtime import lib, ffi
from koi.utils import void_ptr, show_diff_result
import time

dtype = torch.float16
dev = "cuda"
props = torch.cuda.get_device_properties(dev)

# in_size, out_size, kernel_size, stride
tests = [
    (16, 96, 19, 5),
    (16, 96, 19, 6),
    (16, 384, 19, 5),
    (16, 384, 19, 6),
    (16, 1024, 19, 5),
    (16, 1024, 19, 6),
]


@pytest.mark.skipif(props.major < 8, reason=f"{props.name} compute capability {props.major} < 8")
@pytest.mark.parametrize("window_params", tests)
def test_window_kernel(window_params):
    C_in, C_out, W, stride = window_params
    T_in = 1200
    N = 512

    stream = torch.cuda.default_stream()
    stream_ptr = ffi.cast("void *", stream.cuda_stream)

    with torch.no_grad():
        torch.manual_seed(42)
        padding = W // 2
        T_out = T_in // stride

        in_bfr = torch.rand((N, T_in, C_in), device=dev, dtype=dtype) * 2 - 1
        in_bfr_padded = torch.zeros(
            (N, T_in + 2 * padding, C_in), device=dev, dtype=dtype
        )
        in_bfr_padded[:, padding:-padding] = in_bfr

        ref_ntwc = in_bfr_padded.as_strided(
            (N, T_out, W * C_in), (in_bfr_padded.stride(0), stride * C_in, 1)
        )

        out_ntwc = torch.empty((N, T_out, W * C_in), device=dev, dtype=dtype)
        res = lib.host_window_ntwc_f16(
            stream_ptr,
            N,
            T_in,
            C_in,
            W,
            stride,
            out_ntwc.stride(0),
            out_ntwc.stride(1),
            void_ptr(in_bfr),
            void_ptr(out_ntwc),
        )
        assert res == 0
        stream.synchronize()
        assert torch.all(ref_ntwc == out_ntwc)


if __name__ == "__main__":
    for test in tests:
        print("Testing window kernel", test)
        test_window_kernel(test)
