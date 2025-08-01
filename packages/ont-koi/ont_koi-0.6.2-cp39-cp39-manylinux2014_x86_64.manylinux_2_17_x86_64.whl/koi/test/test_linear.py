import time
import torch
import pytest
from koi._runtime import lib, ffi
from koi.utils import void_ptr, show_diff_result, quantize_tensor

dtype = torch.float16
dev = "cuda"

# (N, T, C_in, C_out)
tests = ((512, 1024, 384, 1024),)

act_dict = {
    lib.KOI_SWISH: ("Swish", torch.nn.SiLU()),
    lib.KOI_TANH: ("Tanh", torch.nn.Tanh()),
    lib.KOI_IDENTITY: ("Identity", lambda x: x),
}
koi_type_dict = {
    lib.KOI_F16: "f16",
    lib.KOI_I8: "i8",
}


@pytest.mark.parametrize("linear_params", tests)
@pytest.mark.parametrize("activation_params", act_dict.items())
@pytest.mark.parametrize("in_type", koi_type_dict.keys())
@pytest.mark.parametrize("out_type", koi_type_dict.keys())
def test_cutlass_linear(linear_params, activation_params, in_type, out_type):
    devprop = torch.cuda.get_device_properties(torch.cuda.current_device())
    if devprop.major < 8:
        return

    N, T, C_in, C_out = linear_params
    act_id, (act_str, act_fn) = activation_params
    stream = torch.cuda.default_stream()
    stream_ptr = ffi.cast("void *", stream.cuda_stream)

    with torch.no_grad():
        torch.manual_seed(42)
        ref_linear = torch.nn.Linear(C_in, C_out, bias=True, device=dev, dtype=dtype)

        in_bfr = torch.rand((N, T, C_in), device=dev, dtype=dtype) * 2 - 1
        out_ref = act_fn(ref_linear(in_bfr))

        weights = ref_linear.weight
        bias = ref_linear.bias
        scale = None

        if in_type == lib.KOI_I8:
            in_bfr = (in_bfr * 128).round().clip(-127, 127).to(torch.int8)
            q_scale, weights_q = quantize_tensor(weights.T)
            scale = q_scale.to(torch.float16)
            weights = weights_q.T.contiguous()

        out_dtype = torch.int8 if out_type == lib.KOI_I8 else torch.float16
        out_bfr = torch.empty((N, T, C_out), device=dev, dtype=out_dtype)
        args = (
            stream_ptr,
            in_type,
            act_id,
            out_type,
            in_bfr.size(0),
            in_bfr.size(1),
            C_in,
            C_out,
            in_bfr.stride(0),
            in_bfr.stride(1),
            out_bfr.stride(0),
            out_bfr.stride(1),
            void_ptr(in_bfr),
            void_ptr(weights),
            void_ptr(out_bfr),
            void_ptr(scale),
            void_ptr(bias),
        )
        res = lib.host_linear(*args)

        if out_type is lib.KOI_I8 and act_id != lib.KOI_TANH:
            assert res == lib.KOI_INVALID_VALUE
            return
        else:
            assert res == lib.KOI_SUCCESS

        label = f"{linear_params}, {act_str}, {koi_type_dict[in_type]}->{koi_type_dict[out_type]}"
        if out_type == lib.KOI_I8:
            out_bfr = out_bfr.to(torch.float32) * (1 / 127)
        show_diff_result(label, out_ref, out_bfr, 1e-2, 0.2, True)


@pytest.mark.parametrize("linear_params", tests)
@pytest.mark.parametrize("activation_params", act_dict.items())
def test_cublas_linear(linear_params, activation_params):
    N, T, C_in, C_out = linear_params
    act_id, (act_str, act_fn) = activation_params
    stream = torch.cuda.default_stream()
    stream_ptr = ffi.cast("void *", stream.cuda_stream)

    with torch.no_grad():
        torch.manual_seed(42)
        ref_linear = torch.nn.Linear(C_in, C_out, bias=True, device=dev, dtype=dtype)
        weights = ref_linear.weight.T.contiguous()
        bias = ref_linear.bias

        in_bfr = torch.rand((N, T, C_in), device=dev, dtype=dtype) * 2 - 1
        out_ref = act_fn(ref_linear(in_bfr))

        # Using CuBLAS gemm followed by host_bias_activation_f16_inplace
        blas_h = ffi.cast("void *", torch.cuda.current_blas_handle())
        out_bfr = torch.zeros((N, T, C_out), device=dev, dtype=dtype)

        res = lib.host_cublas_gemm_f16(
            blas_h,
            C_out,
            N * T,
            C_in,
            0,
            void_ptr(weights),
            void_ptr(in_bfr),
            void_ptr(out_bfr),
        )
        if res is lib.KOI_NOT_SUPPORTED:
            torch.matmul(
                in_bfr.view((-1, C_in)), weights, out=out_bfr.view((-1, C_out))
            )
            res = lib.KOI_SUCCESS
        assert res == lib.KOI_SUCCESS
        res = lib.host_bias_activation_f16_inplace(
            stream_ptr,
            N * T,
            C_out,
            C_out,
            void_ptr(out_bfr),
            void_ptr(ref_linear.bias),
            act_id,
        )
        assert res == lib.KOI_SUCCESS
        show_diff_result("cublasGemmEx", out_ref, out_bfr, 1e-2, 0.2, True)


def time_kernel(iters, stream, fn):
    for i in range(iters + 1):
        if fn() != lib.KOI_SUCCESS:
            return None
        if i == 0:
            stream.synchronize()
            t0 = time.time()
    stream.synchronize()
    return time.time() - t0


if __name__ == "__main__":
    with torch.no_grad():
        stream = torch.cuda.default_stream()
        stream_ptr = ffi.cast("void *", stream.cuda_stream)
        iters = 100

        for N, T, C_in, C_out in tests:
            tflop = (N * T * C_in * C_out * 2 * iters) / 1.0e12
            torch.manual_seed(42)
            ref_linear = torch.nn.Linear(
                C_in, C_out, bias=True, device=dev, dtype=dtype
            )
            weights_t = ref_linear.weight
            weights = weights_t.T.contiguous()
            bias = ref_linear.bias
            q_scale, weights_q = quantize_tensor(weights)
            q_scale = q_scale.to(torch.float16)
            weights_q_t = weights_q.T.contiguous()

            in_bfr_ntc = torch.rand((N, T, C_in), device=dev, dtype=dtype) * 2 - 1
            in_bfr_tnc = in_bfr_ntc.transpose(0, 1).contiguous()
            in_bfr_ntc_i8 = (
                (in_bfr_ntc.to(torch.float32) * 128)
                .round()
                .clip(-127, 127)
                .to(torch.int8)
            )
            in_bfr_tnc_i8 = in_bfr_ntc_i8.transpose(1, 0).contiguous()
            q_scale, weights_q = quantize_tensor(weights)
            q_scale = q_scale.to(torch.float16)
            weights_q_t = weights_q.T.contiguous()

            out_ref_ntc = torch.empty((N, T, C_out), device=dev, dtype=dtype)
            out_ref_tnc = out_ref_ntc.transpose(0, 1)

            for act_id, (act_str, act_fn) in act_dict.items():
                print(f"Running linear NTCC {N}, {T}, {C_in}, {C_out}, {act_str}")

                def torch_fn():
                    out_ref_ntc[:] = act_fn(ref_linear(in_bfr_ntc))
                    return 0

                t_ref = time_kernel(iters, stream, torch_fn)
                print(f"⬜ Torch matmul {t_ref:6f}s, {tflop / t_ref:.1f} Tflop/s")

                out_type_list = [(lib.KOI_F16, torch.float16)]
                if act_id == lib.KOI_TANH:
                    out_type_list.append((lib.KOI_I8, torch.int8))

                # Using Cutlass-based host_linear_ntc
                cutlass_tests = []
                devprop = torch.cuda.get_device_properties(torch.cuda.current_device())
                if devprop.major >= 8:
                    cutlass_tests = [
                        (lib.KOI_F16, (in_bfr_ntc, in_bfr_tnc), weights_t, None),
                        (
                            lib.KOI_I8,
                            (in_bfr_ntc_i8, in_bfr_tnc_i8),
                            weights_q_t,
                            q_scale,
                        ),
                    ]
                for in_koi_type, in_bfrs, wts_bfr, scale in cutlass_tests:
                    for out_koi_type, out_dtype in out_type_list:
                        for in_bfr, in_is_ntc in (
                            (in_bfrs[0], True),
                            (in_bfrs[1], False),
                        ):
                            for out_is_ntc in (True, False):
                                in_fmt = "ntc" if in_is_ntc else "tnc"
                                out_fmt = "ntc" if out_is_ntc else "tnc"
                                out_sizes = (
                                    (N, T, C_out) if out_is_ntc else (T, N, C_out)
                                )
                                out_bfr = torch.empty(
                                    out_sizes, device=dev, dtype=out_dtype
                                )
                                out_ref = out_ref_ntc if out_is_ntc else out_ref_tnc

                                for dim0, dim1 in ((0, 1), (1, 0)):
                                    label = f"host_linear {in_fmt}->{out_fmt}, {dim0}, {koi_type_dict[in_koi_type]}->{koi_type_dict[out_koi_type]}"
                                    stride_dims = (dim0, dim1)
                                    if out_is_ntc != in_is_ntc:
                                        stride_dims = (dim1, dim0)

                                    def kernel_fn():
                                        args = (
                                            stream_ptr,
                                            in_koi_type,
                                            act_id,
                                            out_koi_type,
                                            in_bfr.size(dim0),
                                            in_bfr.size(dim1),
                                            C_in,
                                            C_out,
                                            in_bfr.stride(dim0),
                                            in_bfr.stride(dim1),
                                            out_bfr.stride(stride_dims[0]),
                                            out_bfr.stride(stride_dims[1]),
                                            void_ptr(in_bfr),
                                            void_ptr(wts_bfr),
                                            void_ptr(out_bfr),
                                            void_ptr(scale),
                                            void_ptr(bias),
                                        )
                                        res = lib.host_linear(*args)
                                        if res != lib.KOI_SUCCESS:
                                            print("host_linear", res, args)
                                        return res

                                    t = time_kernel(iters, stream, kernel_fn)
                                    if t is None:
                                        print(f"❌ {label} failed")
                                        continue
                                    label = f"{label} {t:6f}s, {tflop / t:.1f} Tflop/s"
                                    if out_dtype == torch.int8:
                                        show_diff_result(
                                            label,
                                            out_ref.clamp(-1, 1),
                                            out_bfr.to(torch.float32) * (1 / 127),
                                            1e-2,
                                            0.2,
                                        )
                                    else:
                                        show_diff_result(
                                            label, out_ref, out_bfr, 1e-2, 0.2
                                        )

                # Using CuBLAS gemm followed by host_bias_activation_f16_inplace
                blas_h = ffi.cast("void *", torch.cuda.current_blas_handle())
                out_bfr_cu = torch.zeros((N, T, C_out), device=dev, dtype=dtype)

                def kernel_fn():
                    res = lib.host_cublas_gemm_f16(
                        blas_h,
                        C_out,
                        N * T,
                        C_in,
                        0,
                        void_ptr(weights),
                        void_ptr(in_bfr_ntc),
                        void_ptr(out_bfr_cu),
                    )
                    if res is lib.KOI_NOT_SUPPORTED:
                        torch.matmul(
                            in_bfr_ntc.view((-1, C_in)),
                            weights,
                            out=out_bfr_cu.view((-1, C_out)),
                        )
                        res = lib.KOI_SUCCESS
                    if res == lib.KOI_SUCCESS:
                        res = lib.host_bias_activation_f16_inplace(
                            stream_ptr,
                            N * T,
                            C_out,
                            C_out,
                            void_ptr(out_bfr_cu),
                            void_ptr(bias),
                            act_id,
                        )
                    return res

                t = time_kernel(iters, stream, kernel_fn)
                label = f"cublasGemmEx {t:6f}s, {tflop / t:.1f} Tflop/s"
                show_diff_result(label, out_ref_ntc, out_bfr_cu, 1e-2, 0.2)
