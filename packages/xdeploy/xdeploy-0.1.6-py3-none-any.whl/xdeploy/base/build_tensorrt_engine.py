from __future__ import annotations

import contextlib
from pathlib import Path

import numpy as np
import tensorrt as trt
from cuda.bindings import driver, nvrtc

from .tensor import Tensor


def _cuda_get_error_enum(error: driver.CUresult | nvrtc.nvrtcResult) -> str:
    if isinstance(error, driver.CUresult):
        err, name = driver.cuGetErrorName(error)
        return name if err == driver.CUresult.CUDA_SUCCESS else "<unknown>"
    elif isinstance(error, nvrtc.nvrtcResult):
        return nvrtc.nvrtcGetErrorString(error)[1]
    else:
        raise RuntimeError(f"Unknown error type: {error}")


def check_cuda_errors(
    result: tuple[driver.CUresult | nvrtc.nvrtcResult, ...],
) -> None | tuple[driver.CUresult | nvrtc.nvrtcResult, ...]:
    """检查CUDA错误."""
    if result[0].value:
        raise RuntimeError(f"CUDA error code={result[0].value}({_cuda_get_error_enum(result[0])})")
    if len(result) == 1:
        return None
    elif len(result) == 2:
        return result[1]
    else:
        return result[1:]


@contextlib.contextmanager
def tensorrt_context():
    """TensorRT资源管理上下文管理器."""
    logger = trt.Logger(trt.Logger.INFO)
    trt.init_libnvinfer_plugins(logger, namespace="")

    builder = trt.Builder(logger)
    config = builder.create_builder_config()

    try:
        yield builder, config, logger
    finally:
        # 自动清理资源
        del config
        del builder
        import gc

        gc.collect()


def build_engine_from_onnx(onnx_path: Path, precision: str = "fp16") -> Path:
    """从ONNX模型构建TensorRT引擎."""
    engine_path = onnx_path.with_suffix(".trt")

    if engine_path.exists():
        return engine_path

    if not onnx_path.exists():
        raise FileNotFoundError(f"文件{onnx_path}不存在")
    if onnx_path.suffix != ".onnx":
        raise ValueError(f"文件{onnx_path}不是有效的 ONNX 模型文件")

    with tensorrt_context() as (builder, config, logger):
        config.set_memory_pool_limit(trt.MemoryPoolType.WORKSPACE, 1 << 32)
        network = builder.create_network(0)
        parser = trt.OnnxParser(network, logger)

        try:
            # 读取并解析ONNX文件
            with onnx_path.open("rb") as f:
                if not parser.parse(f.read()):
                    raise RuntimeError(f"解析 ONNX 模型失败: {onnx_path}")

            # 设置精度（与原代码相同）
            for i in range(network.num_layers):
                if network.get_layer(i).name in [
                    "FirstStageBoxPredictor/ConvolutionalBoxHead_0/BoxEncodingPredictor/squeeze",
                    "FirstStageBoxPredictor/ConvolutionalBoxHead_0/BoxEncodingPredictor/scale_value:0",
                    "FirstStageBoxPredictor/ConvolutionalBoxHead_0/BoxEncodingPredictor/scale",
                    "nms/anchors:0",
                ]:
                    network.get_layer(i).precision = trt.DataType.FLOAT
                    network.get_layer(i - 1).precision = trt.DataType.FLOAT
                if network.get_layer(i).name == "FirstNMS/detection_boxes_conversion":
                    network.get_layer(i).precision = trt.DataType.FLOAT

            # 设置构建标志
            config.set_flag(trt.BuilderFlag.PREFER_PRECISION_CONSTRAINTS)
            config.set_flag(trt.BuilderFlag.DIRECT_IO)
            config.set_flag(trt.BuilderFlag.REJECT_EMPTY_ALGORITHMS)

            # 根据精度设置配置FP16
            if precision == "fp16":
                if not builder.platform_has_fast_fp16:
                    print("此平台/设备原生不支持FP16")
                else:
                    config.set_flag(trt.BuilderFlag.FP16)

            # 构建并序列化引擎并保存
            engine_bytes = builder.build_serialized_network(network, config)
            if engine_bytes is None:
                raise RuntimeError("构建 TensorRT 引擎失败")

            with engine_path.open("wb") as f:
                f.write(engine_bytes)

        finally:
            # 清理网络和解析器
            del parser
            del network

        return engine_path


class TRTBaseModel:
    """TensorRT 后端推理模型.

    Args:
        model_path (Union[str, Path]): 模型文件的路径。

    Attributes:
        inputs_info (List[Tensor]): 模型输入的信息。
        outputs_info (List[Tensor]): 模型输出的信息。
        is_dynamic (bool): 模型是否有动态轴。
        input_names (List[str]): 输入tensor名称列表。
        output_names (List[str]): 输出tensor名称列表。
    """

    def __init__(self, model_path: str | Path, *args, **kwargs) -> None:
        """初始化函数."""
        self.weight = Path(model_path) if isinstance(model_path, str) else model_path

        if self.weight.suffix == ".onnx":
            self.weight = build_engine_from_onnx(self.weight)

        if not self.weight.exists():
            raise FileNotFoundError(f"File {self.weight} not found.")
        if self.weight.suffix not in {".trt", ".engine"}:
            raise ValueError(f"File {self.weight} is not a valid TensorRT engine file.")

        self.metadata = {}

        self.__init_engine()
        self.__init_cuda()
        self.__init_tensors()
        self.__warm_up()

    def __init_cuda(self) -> None:
        check_cuda_errors(driver.cuInit(0))
        self.cu_stream = check_cuda_errors(driver.cuStreamCreate(0))

    def __init_engine(self) -> None:
        logger = trt.Logger(trt.Logger.INFO)
        trt.init_libnvinfer_plugins(logger, namespace="")
        model = trt.Runtime(logger).deserialize_cuda_engine(self.weight.read_bytes())
        context = model.create_execution_context()

        self.model = model
        self.context = context

    def __init_tensors(self) -> None:
        """初始化tensor信息，使用新的tensor-based API."""
        dynamic = False
        inp_info = []
        out_info = []
        input_names = []
        output_names = []

        # 使用新的tensor API获取所有tensor名称
        for i in range(self.model.num_io_tensors):
            name = self.model.get_tensor_name(i)
            dtype = trt.nptype(self.model.get_tensor_dtype(name))
            shape = tuple(self.model.get_tensor_shape(name))
            is_input = self.model.get_tensor_mode(name) == trt.TensorIOMode.INPUT

            if -1 in shape and is_input:
                dynamic |= True

            if not dynamic:
                cpu = np.empty(shape, dtype)
                err, gpu = driver.cuMemAlloc(cpu.nbytes)
                assert err == driver.CUresult.CUDA_SUCCESS

                (err,) = driver.cuMemcpyHtoDAsync(gpu, cpu.ctypes.data, cpu.nbytes, self.cu_stream)
                assert err == driver.CUresult.CUDA_SUCCESS
            else:
                cpu, gpu = np.empty(0), 0

            tensor = Tensor(name, dtype, shape, cpu, gpu)

            if is_input:
                inp_info.append(tensor)
                input_names.append(name)
            else:
                out_info.append(tensor)
                output_names.append(name)

        self.is_dynamic: bool = dynamic
        self.inputs_info: list[Tensor] = inp_info
        self.outputs_info: list[Tensor] = out_info
        self.input_names: list[str] = input_names
        self.output_names: list[str] = output_names

    def __warm_up(self, times: int = 10) -> None:
        if self.is_dynamic:
            print("You engine has dynamic axes, please warm up by yourself !")
            return
        for _ in range(times):
            inputs = {}
            for i in self.inputs_info:
                inputs[i.name] = i.cpu
            self.forward(inputs)

    def set_profiler(self, profiler: trt.IProfiler | None) -> None:
        """设置 profiler."""
        self.context.profiler = profiler if profiler is not None else trt.Profiler()

    def __copy_input_to_device(self, input_dict: dict[str, np.ndarray]):
        """将输入数据复制到GPU，使用新的tensor-based API."""
        for input_tensor in self.inputs_info:
            input_name = input_tensor.name
            if input_name not in input_dict:
                raise ValueError(f"Input data of {input_name} is not provided.")

            input_data = input_dict[input_name]

            if self.is_dynamic:
                self.context.set_input_shape(input_name, tuple(input_data.shape))
                input_tensor.gpu = check_cuda_errors(driver.cuMemAlloc(input_data.nbytes))

            check_cuda_errors(
                driver.cuMemcpyHtoDAsync(input_tensor.gpu, input_data.ctypes.data, input_data.nbytes, self.cu_stream)
            )

            self.context.set_tensor_address(input_name, input_tensor.gpu)

        # 处理输出tensor
        for output_tensor in self.outputs_info:
            output_name = output_tensor.name

            if self.is_dynamic:
                shape = tuple(self.context.get_tensor_shape(output_name))
                dtype = output_tensor.dtype
                cpu = np.empty(shape, dtype=dtype)
                gpu = check_cuda_errors(driver.cuMemAlloc(cpu.nbytes))

                check_cuda_errors(driver.cuMemcpyHtoDAsync(gpu, cpu.ctypes.data, cpu.nbytes, self.cu_stream))

                output_tensor.gpu = gpu
                output_tensor.cpu = cpu

            self.context.set_tensor_address(output_name, output_tensor.gpu)

    def __copy_output_to_host(self):
        """将输出数据从GPU复制到CPU."""
        for tensor in self.outputs_info:
            check_cuda_errors(
                driver.cuMemcpyDtoHAsync(tensor.cpu.ctypes.data, tensor.gpu, tensor.cpu.nbytes, self.cu_stream)
            )

    def forward(self, input_data: dict[str, np.ndarray]) -> tuple | np.ndarray:
        """执行推理.

        Args:
            input_data (Dict[str, np.ndarray]): 输入数据.

        Returns:
            Union[Tuple, np.ndarray]: 推理结果

        """
        assert len(input_data) == len(self.inputs_info), "Input data does not match with the engine."

        # 复制输入数据到设备
        self.__copy_input_to_device(input_data)

        success = self.context.execute_async_v3(self.cu_stream)
        if not success:
            raise RuntimeError("Failed to execute inference with execute_async_v3")

        check_cuda_errors(driver.cuStreamSynchronize(self.cu_stream))

        # 复制输出数据到主机
        self.__copy_output_to_host()

        outputs = [output.cpu for output in self.outputs_info]
        return tuple(outputs) if len(outputs) > 1 else outputs[0]

    def __del__(self):
        """清理资源."""
        if hasattr(self, "stream"):
            check_cuda_errors(driver.cuStreamDestroy(self.cu_stream))

        # 清理GPU内存
        if hasattr(self, "inputs_info"):
            for tensor in self.inputs_info:
                if tensor.gpu != 0:
                    check_cuda_errors(driver.cuMemFree(tensor.gpu))

        if hasattr(self, "outputs_info"):
            for tensor in self.outputs_info:
                if tensor.gpu != 0:
                    check_cuda_errors(driver.cuMemFree(tensor.gpu))
