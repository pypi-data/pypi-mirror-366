import torch
import pytest
from koi._runtime import lib, ffi
from koi.utils import void_ptr, show_diff_result, quantize_tensor, time_kernel

torch.set_printoptions(linewidth=260, sci_mode=False)

is_not_main = __name__ != "__main__"
dtype = torch.float16
dev = "cuda"

props = torch.cuda.get_device_properties(dev)
print("Device properties", props)

sm_count = props.multi_processor_count


def tflops(T, N, C, iterations, time):
    return ((C * C * 8 * T * N * 2) / 1.0e12) * iterations / time


def run_kernel(kernel, T, Ns, Cs):
    with torch.no_grad():
        stream = torch.cuda.default_stream()
        stream_ptr = ffi.cast("void *", stream.cuda_stream)

        N_ref = 41

        for C in Cs:
            print(f"Running LSTM TNC {T}xNx{C}, dtype {dtype}")

            torch.cuda.empty_cache()
            torch.manual_seed(42)

            # run Torch on smaller batch size
            try:
                in_bfr_part = torch.rand((T, N_ref, C), device=dev, dtype=dtype) * 2 - 1
                ref_lstm = torch.nn.LSTM(C, C, device=dev, dtype=dtype)
                ref_out_part = ref_lstm.forward(in_bfr_part)[0]
                bias = ref_lstm.bias_ih_l0 + ref_lstm.bias_hh_l0
                weights = torch.concat(
                    (ref_lstm.weight_ih_l0.T, ref_lstm.weight_hh_l0.T), 0
                )
            except:
                break

            iterations = 100

            # run kernel with different batch sizes
            for N in Ns:
                in_bfr = in_bfr_part.repeat(1, (N // N_ref) + 1, 1)[:, 0:N, :]
                ref_out = ref_out_part.repeat(1, (N // N_ref) + 1, 1)[:, 0:N, :]

                kernel(
                    T,
                    N,
                    C,
                    iterations,
                    stream,
                    stream_ptr,
                    in_bfr,
                    ref_out,
                    ref_lstm,
                    bias,
                    weights,
                )


def lstm_step_kernel(
    T, N, C, iterations, stream, stream_ptr, in_bfr, ref_out, ref_lstm, bias, weights
):
    in_out_bfr = torch.zeros((T + 1, N, 2, C), device=dev, dtype=dtype)
    in_out_bfr[:T, :, 0] = in_bfr
    out_bfr = in_out_bfr[1:, :, 1]

    def lstm_step():
        state_buf = torch.zeros((N, C), device=dev, dtype=dtype)
        for t in range(T):
            gate_buf = torch.matmul(in_out_bfr[t].view((N, 2 * C)), weights)
            lib.host_lstm_step_f16(
                stream_ptr,
                N,
                C,
                void_ptr(bias),
                void_ptr(gate_buf),
                void_ptr(state_buf),
                void_ptr(out_bfr[t]),
            )

    label = f"N = {N:4d}: LSTM step kernel"

    try:
        time = time_kernel(iterations, stream, lstm_step, None)
    except:
        print(f"{label}: Unable to run with given N")
        return

    # run again, to produce right result
    in_out_bfr[:T, :, 0] = in_bfr
    lstm_step()

    show_diff_result(
        f"{label}: {tflops(N, T, C, iterations, time):7.3f} Tflops",
        ref_out,
        out_bfr,
        1e-4,
        2e-3,
        is_not_main,
    )


def lstm_small_kernel(
    T, N, C, iterations, stream, stream_ptr, in_bfr, ref_out, ref_lstm, bias, weights
):
    if (C != 96) and (C != 128):
        print("LSTM small kernel: Unable to run with given C")
        return

    weight_ih = ref_lstm.weight_ih_l0.T
    weight_hh = ref_lstm.weight_hh_l0.T.contiguous()
    scale_q, weight_hh_q = quantize_tensor(weight_hh)

    in_bfr_ntc = in_bfr.transpose(0, 1).contiguous()
    out_bfr_ntc = torch.empty_like(in_bfr_ntc)
    in_Wx = torch.matmul(in_bfr_ntc.view((-1, C)), weight_ih)
    in_Wx_rev = in_Wx.view((N, T, -1)).flip(1)

    if C == 96:
        tests = [
            (False, 1),
            (False, -1),
            (True, 1),
            (True, -1),
        ]  # [HMA2|DP4A] x [fwd|rev]
    else:
        tests = [
            (True, 1),
            (True, -1),
        ]  # Test only DP4A fwd/rev for 128-wide

    kernel_names = ["HMA2", "DP4A"]
    kernel_directions = {1: "fwd", -1: "rev"}
    kernel_limits = [[2e-4, 8e-4], [3e-3, 9e-3]]  # mean, max

    for quantised, direction in tests:

        def lstm_small():
            return lib.host_small_lstm(
                stream_ptr,
                N,
                T,
                C,
                direction,
                void_ptr(in_Wx if direction == 1 else in_Wx_rev),
                void_ptr(weight_hh_q if quantised else weight_hh),
                void_ptr(bias),
                void_ptr(scale_q) if quantised else ffi.cast("void *", 0),
                void_ptr(out_bfr_ntc),
            )

        label = f"N = {N:4d}: {kernel_names[quantised]} kernel {kernel_directions[direction]}"
        kernel_limit_mean = kernel_limits[0][quantised]
        kernel_limit_max = kernel_limits[1][quantised]

        try:
            time = time_kernel(iterations, stream, lstm_small, lib.KOI_SUCCESS)
        except:
            print(f"{label}: Unable to run with given N")
            return

        out_bfr = out_bfr_ntc.transpose(0, 1)
        if direction == -1:
            out_bfr = out_bfr.flip(0)

        show_diff_result(
            f"{label}: {tflops(N, T, C, iterations, time):7.3f} Tflops",
            ref_out,
            out_bfr,
            kernel_limit_mean,
            kernel_limit_max,
            is_not_main,
        )


def lstm_cutlass_kernel(
    T, N, C, iterations, stream, stream_ptr, in_bfr, ref_out, ref_lstm, bias, weights
):
    if props.major < 8:
        print(f"Cutlass LSTM kernel: sm too low: {props.major}.{props.minor}")
        return
    if ((C % 64) != 0) or (C <= 128):
        print(f"Cutlass LSTM kernel: Unable to run with given C {C}")
        return

    state_buf = torch.empty((N, C), device=dev, dtype=dtype)
    workspace_buf = torch.empty((4096,), device=dev, dtype=torch.int8)
    cutlass_bias = bias.view((4, C)).T.contiguous()

    for cutlass_dtype, koi_type in [
        (torch.float16, lib.KOI_F16),
        (torch.int8, lib.KOI_I8),
    ]:
        in_out_bfr = torch.zeros((T + 3, N, C), device=dev, dtype=cutlass_dtype)
        for direction, dir_str in [(-1, "rev"), (1, "fwd")]:
            cutlass_dtype_str = f"{cutlass_dtype}"
            label = f"N = {N:4d}: Cutlass LSTM {dir_str} {cutlass_dtype_str:13}"

            # reorder weights as <igigigigfofofofo>, and flip IH/HH order if reverse
            if cutlass_dtype == torch.int8:
                scale, cutlass_weights = quantize_tensor(weights)
                scale = scale.view((4, C)).T.contiguous().half()
                in_bfr_cutlass = (in_bfr.clip(-1.0, 1.0) * 127).round().to(torch.int8)
            else:
                scale = torch.ones((C, 4), device=dev, dtype=dtype)
                cutlass_weights = weights
                in_bfr_cutlass = in_bfr

            cutlass_weights = cutlass_weights.view((2, C, 2, 2, -1, 4))
            if direction == -1:
                cutlass_weights = cutlass_weights.flip(0)
            cutlass_weights = (
                cutlass_weights.permute(4, 2, 5, 3, 0, 1).contiguous().view((-1, 2 * C))
            )

            def lstm_initialise():
                state_buf[:] = 0
                if direction == -1:
                    in_out_bfr[1:-2] = in_bfr_cutlass.flip(0)
                else:
                    in_out_bfr[2:-1] = in_bfr_cutlass

            def lstm_cutlass():
                lib.host_cutlass_lstm(
                    stream_ptr,
                    koi_type,
                    0,
                    N,
                    C,
                    T,
                    direction,
                    in_out_bfr.stride(1),
                    void_ptr(in_out_bfr),
                    void_ptr(cutlass_weights),
                    void_ptr(cutlass_bias),
                    void_ptr(scale),
                    void_ptr(state_buf),
                    void_ptr(workspace_buf),
                    0,
                    0,
                )

            try:
                lstm_initialise()
                time = time_kernel(iterations, stream, lstm_cutlass, None)
            except:
                print(f"{label}: Unable to run with given N {N}")
                return
            lstm_initialise()
            lstm_cutlass()

            out_bfr = in_out_bfr[2:-1].flip(0) if direction == -1 else in_out_bfr[1:-2]
            if cutlass_dtype == torch.int8:
                out_bfr = out_bfr.to(torch.float16) * (1 / 127.0)

            show_diff_result(
                f"{label}: {tflops(N, T, C, iterations, time):7.3f} Tflops",
                ref_out,
                out_bfr,
                3e-3,
                1e-2,
                is_not_main,
            )


@pytest.mark.parametrize("T", (100,))
@pytest.mark.parametrize(
    "Ns,Cs", (((sm_count * 64,), (96, 128, 256, 384)), ((1024,), (512, 768, 1024)))
)
def test_lstm_step_kernel(T, Ns, Cs):
    run_kernel(lstm_step_kernel, T, Ns, Cs)


@pytest.mark.parametrize("T", (100,))
@pytest.mark.parametrize("Ns", ((sm_count * 64,),))
@pytest.mark.parametrize("Cs", ((96, 128),))
def test_lstm_small_kernel(T, Ns, Cs):
    run_kernel(lstm_small_kernel, T, Ns, Cs)


@pytest.mark.parametrize("T", (100,))
@pytest.mark.parametrize(
    "Ns,Cs", (((sm_count * 64,), (256, 384)), ((1024,), (512, 768, 1024)))
)
def test_lstm_cutlass_kernel(T, Ns, Cs):
    run_kernel(lstm_cutlass_kernel, T, Ns, Cs)


if __name__ == "__main__":
    test_lstm_step_kernel(100, (sm_count * 64,), (96, 128, 256, 384))
    test_lstm_step_kernel(100, (1024,), (512, 768, 1024))

    test_lstm_small_kernel(100, (sm_count * 64,), (96, 128))

    test_lstm_cutlass_kernel(100, ((sm_count // 6) * 256, sm_count * 64), (256, 384))
    test_lstm_cutlass_kernel(100, (1024,), (512, 768, 1024))

    # run with multiple batches Ns = [begin, end>, n = <int>
    # run_kernel(lstm_cutlass_kernel, 100, range(64, sm_count * 64, 64), (768,))
