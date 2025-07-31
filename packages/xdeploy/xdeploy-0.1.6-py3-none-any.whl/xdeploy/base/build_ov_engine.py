from __future__ import annotations

import numpy as np
import openvino as ov

from .tensor import Tensor


class OVBaseModel:
    """基于 OpenVino 模型的推理引擎.

    Args:
        model_path (str): 模型文件的路径。
        device (str, 可选): 推理使用的设备。默认为"CPU"，可选"CPU、GPU"。

    Attributes:
        inputs_info (List[Tensor]): 模型输入的信息。
        is_dynamic (bool): 模型是否有动态轴。
    """

    def __init__(self, model_path: str, device: str = "CPU", *args, **kwargs):
        """初始化函数."""
        self.core = ov.Core()
        self.core.set_property({"CACHE_DIR": "./cache"})
        self.compiled_model = self.core.compile_model(model_path, device)

        self.ir = self.compiled_model.create_infer_request()
        self.metadata = {}

        self.__init_bindings()
        self.__warm_up()

    def __init_bindings(self) -> None:
        dynamic = False
        inp_info = []
        for input_info in self.compiled_model.inputs:
            (input_name,) = input_info.names
            input_dtype = input_info.element_type.to_dtype()
            dynamic |= input_info.partial_shape.is_dynamic
            if not dynamic:
                input_shape = input_info.shape
                input_buffer = np.zeros(input_shape, input_dtype)
            else:
                input_shape = None
                input_buffer = np.empty(0)
            inp_info.append(Tensor(input_name, input_dtype, input_shape, input_buffer, 0))

        self.is_dynamic: bool = dynamic
        self.inputs_info: list[Tensor] = inp_info

    def __warm_up(self, times: int = 10) -> None:
        if self.is_dynamic:
            print("You engine has dynamic axes, please warm up by yourself !")
            return

        for _ in range(times):
            inputs = {}
            for i in self.inputs_info:
                inputs[i.name] = i.cpu
            self.forward(inputs)

    def forward(self, input_data: dict[str, np.ndarray]) -> list[np.ndarray]:
        """进行推理."""
        outputs = self.ir.infer(inputs=input_data)
        return outputs if len(outputs) > 1 else outputs[0]
