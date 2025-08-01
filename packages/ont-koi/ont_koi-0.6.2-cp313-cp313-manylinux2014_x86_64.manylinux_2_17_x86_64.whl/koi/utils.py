import time
import torch
from koi._runtime import ffi, lib
from collections import namedtuple

Buffer = namedtuple("Buffer", "data ptr")


def void_ptr(x):
    """
    Return a void * for given Tensor `x`.
    """
    return ffi.cast("void *", 0 if x is None else x.data_ptr())


def torch_dtype_to_koi_type(dtype):
    dtype_to_koi = {
        torch.float32: lib.KOI_F32,
        torch.float16: lib.KOI_F16,
        torch.float8_e4m3fn: lib.KOI_E4M3,
        torch.int8: lib.KOI_I8,
    }
    if dtype in dtype_to_koi:
        return dtype_to_koi[dtype]
    else:
        raise "Unsupported dtype"


def koi_tensor(t, dim_tags, scale_t_and_dim_tag=None):
    """
    Create a KoiTensor struct from the given torch tensor and dimension tags
    """
    kt = ffi.new("KoiTensor *")
    kt.type_id = torch_dtype_to_koi_type(t.dtype)

    ndims = len(dim_tags)
    if ndims != t.ndim or ndims > lib.KOI_TENSOR_MAX_DIMS:
        raise "Dimension mismatch"

    for i in range(ndims):
        kt.dims[i].tag = dim_tags[i] if type(dim_tags[i]) is int else ord(dim_tags[i])
        kt.dims[i].size = t.size(i)
        kt.dims[i].stride = t.stride(i)

    kt.ndims = ndims
    kt.data_ptr = void_ptr(t)

    if scale_t_and_dim_tag is None:
        kt.scale_data = void_ptr(None)
        kt.scale_tag = 0
        kt.scale_type_id = lib.KOI_NONE
    else:
        scale_t, scale_dim_tag = scale_t_and_dim_tag
        kt.scale_data = void_ptr(scale_t)
        kt.scale_tag = (
            scale_dim_tag if type(scale_dim_tag) is int else ord(scale_dim_tag)
        )
        kt.scale_type_id = torch_dtype_to_koi_type(scale_t.dtype)

    return kt


def empty(size, device, dtype=torch.float16):
    """
    Create an empty Tensor of size `size` on device `device`.
    """
    x = torch.empty(size, dtype=dtype, device=device)
    return Buffer(x, void_ptr(x))


def zeros(size, device, dtype=torch.float16):
    """
    Create an zeros Tensor of size `size` on device `device`.
    """
    x = torch.zeros(size, dtype=dtype, device=device)
    return Buffer(x, void_ptr(x))


def quantize_tensor(tensor, levels=256, dim=0, z=None):
    """
    Quantize a tensor to int8, returning the per-channel scales and the quantized tensor.

    If z is provided, the floating point range used for quantisation is clipped to
    z times the standard deviation from the mean for each channel.
    """
    fp_range = tensor.abs().amax(dim)

    if z is not None:
        fp_mean = tensor.mean(axis=0)
        fp_std = tensor.std(axis=0)
        fp_range_z = abs(fp_mean) + fp_std * z
        fp_range = torch.min(fp_range, fp_range_z)

    quant_scale = (levels / 2) / fp_range
    quant_max = (levels / 2) - 1
    tensor_quantized = (
        (tensor * quant_scale.unsqueeze(dim)).round().clip(-quant_max, quant_max)
    )
    return quant_scale.float(), tensor_quantized.char()


def show_diff_result(
    label, ref_out, out_bfr, mean_limit, max_limit, assert_limits=False
):
    diff = torch.abs(out_bfr.to(torch.float32) - ref_out.to(torch.float32))
    diff_mean = diff.mean().item()
    diff_max = diff.max().item()
    is_good = ("❌", "🟢")[diff_mean <= mean_limit and diff_max <= max_limit]
    print(f"{is_good} Compare {label}: diff mean {diff_mean}, max {diff_max}")
    if assert_limits:
        assert diff_mean <= mean_limit
        assert diff_max <= max_limit


def check_result(
    label, t1, t2, compare_relative, mean_limit, max_limit, assert_limits=False
):
    scale = (1 / max(t1.abs().amax(), t2.abs().amax())) if compare_relative else 1
    diff = torch.abs(t1.float() - t2.float()) * scale
    diff_mean = diff.mean().item()
    diff_max = diff.max().item()
    is_good = ("❌", "🟢")[diff_mean <= mean_limit and diff_max <= max_limit]
    rel_or_abs = ("absolute", "relative")[compare_relative]
    print(f"{is_good} {label}: {rel_or_abs} diff mean {diff_mean}, max {diff_max}")
    if assert_limits:
        assert diff_mean <= mean_limit
        assert diff_max <= max_limit


def time_kernel(iters, stream, fn, success_val):
    for i in range(iters + 1):
        if fn() != success_val:
            return None
        if i == 0:
            stream.synchronize()
            t0 = time.time()
    stream.synchronize()
    return time.time() - t0
