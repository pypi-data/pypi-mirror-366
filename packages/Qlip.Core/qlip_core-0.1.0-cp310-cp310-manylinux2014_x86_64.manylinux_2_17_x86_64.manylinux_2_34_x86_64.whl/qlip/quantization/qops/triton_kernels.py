import torch
import triton
import triton.language as tl

autotune_configs = [
    triton.Config(kwargs={"BLOCK_SIZE": 32}, num_warps=1),
    triton.Config(kwargs={"BLOCK_SIZE": 32}, num_warps=2),
    triton.Config(kwargs={"BLOCK_SIZE": 64}, num_warps=2),
    triton.Config(kwargs={"BLOCK_SIZE": 128}, num_warps=4),
    triton.Config(kwargs={"BLOCK_SIZE": 256}, num_warps=4),
    triton.Config(kwargs={"BLOCK_SIZE": 256}, num_warps=8),
    triton.Config(kwargs={"BLOCK_SIZE": 512}, num_warps=8),
    triton.Config(kwargs={"BLOCK_SIZE": 512}, num_warps=16),
    triton.Config(kwargs={"BLOCK_SIZE": 1024}, num_warps=16),
]


# @triton.autotune(configs=autotune_configs, key=[])
@triton.jit
def fake_quantize_int_scalar_kernel(
    input_ptr,
    scale_ptr,
    zero_point_ptr,
    output_ptr,
    numel,
    min,
    max,
    BLOCK_SIZE: tl.constexpr,
):
    idx = tl.program_id(0) * BLOCK_SIZE + tl.arange(0, BLOCK_SIZE)
    mask = idx < numel

    input = tl.load(input_ptr + idx, mask=mask, other=0.0)

    scale = tl.load(scale_ptr)
    zero_point = tl.load(zero_point_ptr)

    round_tensor = tl.extra.cuda.libdevice.rint(input / scale)
    round_tensor = round_tensor + zero_point
    clamped_tensor = tl.clamp(round_tensor, min, max)
    output = (clamped_tensor - zero_point) * scale

    tl.store(output_ptr + idx, output, mask=mask)


# @triton.autotune(configs=autotune_configs, key=[])
@triton.jit
def fake_quantize_int_vector_kernel(
    input_ptr,
    scale_ptr,
    zero_point_ptr,
    output_ptr,
    numel,
    stride,
    scale_size,
    min,
    max,
    BLOCK_SIZE: tl.constexpr,
):
    idx = tl.program_id(0) * BLOCK_SIZE + tl.arange(0, BLOCK_SIZE)
    mask = idx < numel

    axis_idx = (idx // stride) % scale_size
    scale = tl.load(scale_ptr + axis_idx, mask=mask, other=1.0)
    zero_point = tl.load(zero_point_ptr + axis_idx, mask=mask, other=0.0)

    input = tl.load(input_ptr + idx, mask=mask, other=0.0)

    round_tensor = tl.extra.cuda.libdevice.rint(input / scale)
    round_tensor = round_tensor + zero_point
    clamped_tensor = tl.clamp(round_tensor, min, max)
    output = (clamped_tensor - zero_point) * scale

    tl.store(output_ptr + idx, output, mask=mask)


@triton.jit
def fake_quantize_int_block_kernel(
    input_ptr,
    scale_ptr,
    zero_point_ptr,
    output_ptr,
    numel,
    stride,
    block_size,
    min,
    max,
    BLOCK_SIZE: tl.constexpr,
):
    idx = tl.program_id(0) * BLOCK_SIZE + tl.arange(0, BLOCK_SIZE)
    mask = idx < numel

    axis_idx = ((idx // stride) // block_size) * stride + (idx % stride)
    scale = tl.load(scale_ptr + axis_idx, mask=mask, other=1.0)
    zero_point = tl.load(zero_point_ptr + axis_idx, mask=mask, other=0.0)

    input = tl.load(input_ptr + idx, mask=mask, other=0.0)

    round_tensor = tl.extra.cuda.libdevice.rint(input / scale)
    round_tensor = round_tensor + zero_point
    clamped_tensor = tl.clamp(round_tensor, min, max)
    output = (clamped_tensor - zero_point) * scale

    tl.store(output_ptr + idx, output, mask=mask)


def fake_quantize_int_cuda(input, scale, zero_point, axis=0, min=-8, max=7):
    output = torch.empty_like(input)
    numel = input.numel()

    # grid = lambda meta: (triton.cdiv(numel, meta["BLOCK_SIZE"]),)
    BLOCK_SIZE = 512
    grid = (triton.cdiv(numel, BLOCK_SIZE),)

    if scale.numel() == 1:
        fake_quantize_int_scalar_kernel[grid](
            input,
            scale,
            zero_point,
            output,
            numel,
            min,
            max,
            BLOCK_SIZE=BLOCK_SIZE,
        )
    elif scale.numel() == input.size(axis):
        axis_dim = input.size(axis)

        stride = input.stride(axis)
        fake_quantize_int_vector_kernel[grid](
            input,
            scale,
            zero_point,
            output,
            numel,
            stride,
            axis_dim,
            min,
            max,
            BLOCK_SIZE=BLOCK_SIZE,
        )
    else:
        stride = input.stride(axis)
        block_size = input.size(axis) // scale.size(axis)
        fake_quantize_int_block_kernel[grid](
            input,
            scale,
            zero_point,
            output,
            numel,
            stride,
            block_size,
            min,
            max,
            BLOCK_SIZE=BLOCK_SIZE,
        )

    return output
