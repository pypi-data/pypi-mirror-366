import torch
import pytest
from koi.lstm import LSTMStack

props = torch.cuda.get_device_properties("cuda")


@pytest.mark.skipif(props.major < 8, reason=f"{props.name} compute capability {props.major} < 8")
def test_one_layer_lstm_returns_tensor():
    layer_size = 96
    batch_size = 32
    chunk_size = 700
    directions = (0,)

    lstm = LSTMStack(directions, layer_size, batch_size, chunk_size).half().cuda()
    input_data = torch.rand(batch_size, chunk_size, layer_size).half().cuda()
    output = lstm(input_data)

    assert output.shape == input_data.shape


def test_five_layer_lstm_fp16_returns_tensor():
    layer_size = 96
    batch_size = 32
    chunk_size = 700
    directions = (1, 0, 1, 0, 1)

    lstm = LSTMStack(directions, layer_size, batch_size, chunk_size).half().cuda()
    input_data = torch.rand(batch_size, chunk_size, layer_size).half().cuda()
    output = lstm(input_data)

    assert output.shape == input_data.shape


def test_one_layer_lstm_fp32_data_raises():
    layer_size = 96
    batch_size = 32
    chunk_size = 700
    directions = (0,)

    lstm = LSTMStack(directions, layer_size, batch_size, chunk_size).half().cuda()
    input_data = torch.rand(batch_size, chunk_size, layer_size).cuda()

    with pytest.raises(TypeError):
        output = lstm(input_data)


def test_five_layer_128_lstm_fp16_raises_():
    layer_size = 128
    batch_size = 32
    chunk_size = 700
    directions = (1, 0, 1, 0, 1)

    with pytest.raises(ValueError):
        lstm = LSTMStack(directions, layer_size, batch_size, chunk_size)


@pytest.mark.skipif(props.major < 8, reason=f"{props.name} compute capability {props.major} < 8")
def test_five_layer_lstm_int8_returns_tensor():
    batch_size = 32
    chunk_size = 700
    directions = (1, 0, 1, 0, 1)

    for layer_size in [96, 128]:
        lstm = (
            LSTMStack(directions, layer_size, batch_size, chunk_size, quantized=True)
            .half()
            .cuda()
        )
        input_data = torch.rand(batch_size, chunk_size, layer_size).half().cuda()
        output = lstm(input_data)

        assert output.shape == input_data.shape


@pytest.mark.skipif(props.major < 8, reason=f"{props.name} compute capability {props.major} < 8")
def test_torch_compile():
    batch_size = 32
    chunk_size = 700
    layer_size = 96
    directions = (1, 0, 1, 0, 1)

    for layer_size in [96, 128]:
        lstm = torch.compile(
            LSTMStack(directions, layer_size, batch_size, chunk_size, quantized=True)
            .half()
            .cuda()
        )
        input_data = torch.rand(batch_size, chunk_size, layer_size).half().cuda()
        output = lstm(input_data)

        assert output.shape == input_data.shape
