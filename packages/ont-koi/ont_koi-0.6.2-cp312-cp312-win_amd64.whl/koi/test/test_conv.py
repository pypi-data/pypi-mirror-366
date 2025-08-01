import time
import torch
import pytest
from koi._runtime import lib, ffi
from koi.utils import void_ptr, show_diff_result

# in_size, out_size, kernel_size, stride, activation
test_small_convs = [
    # conv1
    (1, 4, 5, 1, lib.KOI_SWISH),
    (1, 16, 5, 1, lib.KOI_SWISH),
    (13, 16, 5, 1, lib.KOI_SWISH),
    (1, 16, 5, 1, lib.KOI_TANH),
    # conv2
    (4, 16, 5, 1, lib.KOI_SWISH),
    (16, 16, 5, 1, lib.KOI_SWISH),
    (16, 16, 5, 1, lib.KOI_TANH),
]

test_large_convs = [
    # conv3
    (16, 96, 19, 5, lib.KOI_SWISH),
    (16, 96, 19, 6, lib.KOI_SWISH),
    (16, 384, 19, 5, lib.KOI_SWISH),
    (16, 384, 19, 6, lib.KOI_SWISH),
    (16, 768, 19, 5, lib.KOI_SWISH),
    (16, 768, 19, 6, lib.KOI_SWISH),
    (16, 96, 19, 6, lib.KOI_TANH),
    (16, 384, 19, 6, lib.KOI_TANH),
    (16, 1024, 19, 6, lib.KOI_TANH),
]

act_dict = {
    lib.KOI_SWISH: torch.nn.SiLU(),
    lib.KOI_TANH: torch.nn.Tanh(),
    lib.KOI_IDENTITY: torch.nn.Identity(),
}

dtype = torch.float16
dev = "cuda"
props = torch.cuda.get_device_properties(dev)


def ref_convolution(N, C_in, C_out, T_in, W, stride, koi_activation):
    torch.manual_seed(42)
    # torch.nn.Conv1d expects input in NCT order
    in_bfr = torch.rand((N, C_in, T_in), device=dev, dtype=dtype) * 2 - 1
    ref_conv = torch.nn.Conv1d(
        C_in,
        C_out,
        W,
        stride=stride,
        padding=W // 2,
        bias=True,
        device=dev,
        dtype=dtype,
    )
    ref_out = act_dict[koi_activation](ref_conv(in_bfr))

    # reorder input and output to NTC
    in_bfr_ntc = in_bfr.transpose(1, 2).contiguous()
    ref_out_ntc = ref_out.transpose(1, 2)
    # ref_conv.weight is [C_out, C_in, W], we want [W, C_in, C_out]
    weights = ref_conv.weight.permute(2, 1, 0).contiguous()
    bias = ref_conv.bias
    return in_bfr_ntc, ref_out_ntc, weights, bias


@pytest.mark.parametrize("conv_params", test_small_convs)
def test_small_convolutions(conv_params, assert_limits=True):
    C_in, C_out, W, stride, koi_activation = conv_params
    T_in = 1200
    N = 128
    padding = W // 2
    T_out = T_in // stride

    stream = torch.cuda.default_stream()
    stream_ptr = ffi.cast("void *", stream.cuda_stream)

    with torch.no_grad():
        in_bfr, ref_out, weights, bias = ref_convolution(
            N, C_in, C_out, T_in, W, stride, koi_activation
        )
        out_bfr = torch.empty((N, T_out, C_out), device=dev, dtype=dtype)
        res = lib.host_convolution_f16(
            stream_ptr,
            N,
            C_in,
            C_out,
            T_in,
            W,
            stride,
            padding,
            out_bfr.stride(0),
            void_ptr(in_bfr),
            void_ptr(out_bfr),
            void_ptr(weights),
            void_ptr(bias),
            koi_activation,
        )
        stream.synchronize()
        assert res == 0
        label = f"Small conv {C_in, C_out, W, stride, koi_activation}"
        show_diff_result(label, ref_out, out_bfr, 1e-4, 2e-3, assert_limits)


@pytest.mark.parametrize("conv_params", test_large_convs)
def test_large_convolutions(conv_params, assert_limits=True):
    C_in, C_out, W, stride, koi_activation = conv_params
    T_in = 1200
    N = 128
    padding = W // 2
    T_out = T_in // stride

    stream = torch.cuda.default_stream()
    stream_ptr = ffi.cast("void *", stream.cuda_stream)

    with torch.no_grad():
        in_bfr, ref_out, weights, bias = ref_convolution(
            N, C_in, C_out, T_in, W, stride, koi_activation
        )

        # Convolution using window kernel
        out_ntwc = torch.empty((N, T_out, W, C_in), device=dev, dtype=dtype)
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
        mm_out = torch.matmul(out_ntwc.view((N * T_out, -1)), weights.view((-1, C_out)))
        res = lib.host_bias_activation_f16_inplace(
            stream_ptr,
            mm_out.size(0),
            mm_out.size(1),
            mm_out.stride(0),
            void_ptr(mm_out),
            void_ptr(bias),
            koi_activation,
        )
        assert res == 0
        stream.synchronize()
        out_bfr = mm_out.view((N, T_out, C_out))
        show_diff_result(
            f"Window conv {C_in, C_out, W, stride, koi_activation}",
            ref_out,
            out_bfr,
            1e-4,
            2e-3,
        )

        devprop = torch.cuda.get_device_properties(torch.cuda.current_device())
        if devprop.major >= 8:
            in_bfr_padded = torch.zeros(
                (N, T_in + 2 * padding, C_in), device=dev, dtype=dtype
            )
            in_bfr_padded[:, padding:-padding] = in_bfr
            in_bfr_window = in_bfr_padded.as_strided(
                (N, T_out, W * C_in), (in_bfr_padded.stride(0), stride * C_in, 1)
            )
            out_koi_type, out_dtype = (lib.KOI_F16, torch.float16)
            if koi_activation is lib.KOI_TANH:
                out_koi_type, out_dtype = (lib.KOI_I8, torch.int8)
            out_bfr = torch.empty((T_out, N, C_out), device=dev, dtype=out_dtype)
            weights_t = weights.view((-1, C_out)).T.contiguous()
            res = lib.host_linear(
                stream_ptr,
                lib.KOI_F16,
                koi_activation,
                out_koi_type,
                in_bfr_window.size(1),
                in_bfr_window.size(0),
                in_bfr_window.size(2),
                out_bfr.size(2),
                in_bfr_window.stride(1),
                in_bfr_window.stride(0),
                out_bfr.stride(0),
                out_bfr.stride(1),
                void_ptr(in_bfr_window),
                void_ptr(weights_t),
                void_ptr(out_bfr),
                void_ptr(None),
                void_ptr(bias),
            )
            assert res == lib.KOI_SUCCESS
            stream.synchronize()
            if out_koi_type is lib.KOI_I8:
                out_bfr = out_bfr.to(torch.float32) * (1 / 127)
            out_bfr = out_bfr.transpose(1, 0)
            label = f"Cutlass conv {C_in, C_out, W, stride, koi_activation}"
            show_diff_result(label, ref_out, out_bfr, 2e-3, 7e-3, assert_limits)


if __name__ == "__main__":
    for test in test_small_convs:
        test_small_convolutions(test, False)
    for test in test_large_convs:
        test_large_convolutions(test, False)

    T_in = 600  # needs to be multiple of strides used, i.e. 5 and 6
    N = 6912

    stream = torch.cuda.default_stream()
    stream_ptr = ffi.cast("void *", stream.cuda_stream)
    iters = 100

    print(f"Benchmarking convolutions with N={N}, T_in={T_in}, iters={iters}")

    with torch.no_grad():
        for (C_in, C_out, W, stride, koi_activation) in test_small_convs:
            in_bfr, ref_out, weights, bias = ref_convolution(
                N, C_in, C_out, T_in, W, stride, koi_activation
            )
            padding = W // 2
            T_out = T_in // stride
            tflop = (iters * N * T_out * C_out * W * C_in * 2) / 1.0e12

            out_bfr = torch.empty((N, T_out, C_out), device=dev, dtype=dtype)
            for i in range(iters + 1):
                res = lib.host_convolution_f16(
                    stream_ptr,
                    N,
                    C_in,
                    C_out,
                    T_in,
                    W,
                    stride,
                    padding,
                    out_bfr.stride(0),
                    void_ptr(in_bfr),
                    void_ptr(out_bfr),
                    void_ptr(weights),
                    void_ptr(bias),
                    koi_activation,
                )
                assert res == 0
                if i == 0:
                    stream.synchronize()
                    t0 = time.time()
            stream.synchronize()
            t = time.time() - t0
            label = f"small conv: {C_in} {C_out} {W} {stride} {koi_activation} {t:6f}s, {tflop / t:.1f} Tflop/s"
            show_diff_result(label, ref_out, out_bfr, 1e-4, 2e-3)

        for (C_in, C_out, W, stride, koi_activation) in test_large_convs:
            in_bfr, ref_out, weights, bias = ref_convolution(
                N, C_in, C_out, T_in, W, stride, koi_activation
            )
            padding = W // 2
            T_out = T_in // stride
            tflop = (iters * N * T_out * C_out * W * C_in * 2) / 1.0e12

            out_ntwc = torch.empty((N, T_out, W, C_in), device=dev, dtype=dtype)
            for i in range(iters + 1):
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
                mm_out = torch.matmul(
                    out_ntwc.view((N * T_out, -1)), weights.view((-1, C_out))
                )
                res = lib.host_bias_activation_f16_inplace(
                    stream_ptr,
                    mm_out.size(0),
                    mm_out.size(1),
                    mm_out.stride(0),
                    void_ptr(mm_out),
                    void_ptr(bias),
                    koi_activation,
                )
                assert res == 0
                if i == 0:
                    stream.synchronize()
                    t0 = time.time()
            out_bfr = mm_out.view((N, T_out, C_out))
            stream.synchronize()
            t = time.time() - t0
            label = f"Window conv: {C_in} {C_out} {W} {stride} {koi_activation} {t:6f}s, {tflop / t:.1f} Tflop/s"
            show_diff_result(label, ref_out, out_bfr, 1e-4, 2e-3)

            devprop = torch.cuda.get_device_properties(torch.cuda.current_device())
            if devprop.major >= 8:
                in_bfr_padded = torch.zeros(
                    (N, T_in + 2 * padding, C_in), device=dev, dtype=dtype
                )
                in_bfr_padded[:, padding:-padding] = in_bfr
                in_bfr_window = in_bfr_padded.as_strided(
                    (N, T_out, W * C_in), (in_bfr_padded.stride(0), stride * C_in, 1)
                )
                out_bfr = torch.empty((T_out, N, C_out), device=dev, dtype=dtype)
                weights_t = weights.view((-1, C_out)).T.contiguous()
                for i in range(iters + 1):
                    res = lib.host_linear(
                        stream_ptr,
                        lib.KOI_F16,
                        koi_activation,
                        lib.KOI_F16,
                        in_bfr_window.size(0),
                        in_bfr_window.size(1),
                        in_bfr_window.size(2),
                        out_bfr.size(2),
                        in_bfr_window.stride(0),
                        in_bfr_window.stride(1),
                        out_bfr.stride(1),
                        out_bfr.stride(0),
                        void_ptr(in_bfr_window),
                        void_ptr(weights_t),
                        void_ptr(out_bfr),
                        void_ptr(None),
                        void_ptr(bias),
                    )
                    assert res == lib.KOI_SUCCESS
                    if i == 0:
                        stream.synchronize()
                        t0 = time.time()
                stream.synchronize()
                t = time.time() - t0
                label = f"Cutlass conv: {C_in} {C_out} {W} {stride} {koi_activation} {t:6f}s, {tflop / t:.1f} Tflop/s"
                show_diff_result(label, ref_out, out_bfr.transpose(0, 1), 2e-4, 6e-3)
