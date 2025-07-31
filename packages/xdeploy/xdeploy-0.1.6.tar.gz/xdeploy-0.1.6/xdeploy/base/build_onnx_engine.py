from __future__ import annotations

import numpy as np
import onnxruntime as ort

from .tensor import Tensor


class ORTBaseModel:
    """ONNX 模型.

    Args:
        model_path (str): 模型文件的路径。

    Attributes:
        inputs_info (List[Tensor]): 模型输入的信息。
        outputs_info (List[Tensor]): 模型输出的信息。
    """

    def __init__(self, model_path: str, *args, **kwargs) -> None:
        """初始化函数."""
        self.session = ort.InferenceSession(
            model_path,
            providers=(
                [
                    "CUDAExecutionProvider",
                    "CPUExecutionProvider",
                ]
                if ort.get_device() == "GPU"
                else ["CPUExecutionProvider"]
            ),
        )

        self.__init_bindings()
        self.__load_metadata()
        self.__warm_up()

    def __init_bindings(self) -> None:
        def is_dynamic(input_info) -> bool:
            return any(isinstance(dim, (str, type(None))) or dim < 0 for dim in input_info.shape)

        dynamic = False
        inp_info = []
        out_info = []

        for input_info in self.session.get_inputs():
            input_name = input_info.name
            input_dtype = np.half if input_info.type == "tensor(float16)" else np.single
            dynamic = dynamic or is_dynamic(input_info)

            if not dynamic:
                input_shape = input_info.shape
                input_buffer = np.zeros(input_shape, input_dtype)
            else:
                input_shape = None
                input_buffer = np.empty(0)

            inp_info.append(Tensor(input_name, input_dtype, input_shape, input_buffer, 0))

        for output_info in self.session.get_outputs():
            output_name = output_info.name
            output_dtype = np.half if output_info.type == "tensor(float16)" else np.single

            dynamic = dynamic or is_dynamic(output_info)

            output_shape = output_info.shape if not dynamic else None

            out_info.append(Tensor(output_name, output_dtype, output_shape, 0, 0))

        self.is_dynamic: bool = dynamic
        self.inputs_info: list[Tensor] = inp_info
        self.outputs_info: list[Tensor] = out_info

    def __load_metadata(self) -> None:
        """加载模型元数据."""
        self.input_names = [info.name for info in self.inputs_info]
        self.output_names = [info.name for info in self.outputs_info]
        self.metadata = self.session.get_modelmeta().custom_metadata_map

    def __warm_up(self, times: int = 10) -> None:
        if self.is_dynamic:
            return

        for _ in range(times):
            inputs = {}
            for i in self.inputs_info:
                inputs[i.name] = i.cpu
            self.forward(inputs)

    def forward(self, input_data: dict[str, np.ndarray]) -> list[np.ndarray]:
        """进行推理."""
        outputs = self.session.run(None, input_data)
        return outputs if len(outputs) > 1 else outputs[0]
