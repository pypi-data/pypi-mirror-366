from __future__ import annotations

import ast
import json
from abc import ABC, abstractmethod
from collections.abc import Sequence
from typing import Generic, TypeVar, overload

import numpy as np

from xdeploy.base import Backend
from xdeploy.utils.data_load import letterbox, load_image

T = TypeVar("T")


class YOLO(ABC, Backend, Generic[T]):
    """YOLO模型基类."""

    def __init__(self, model_path: str, device: str = "CPU", *args, **kwds):
        """初始化对象.

        Args:
            model_path (str): 模型文件的路径
            device (str, 可选): 推理使用的设备.默认为"CPU",可选"CPU、GPU".
            args: 其他参数
            kwds: 其他参数
        """
        super().__init__(model_path, device, *args, **kwds)

        self.input_info = self.inputs_info[0]
        self.batch_size = self.input_info.shape[0]
        self.batch_scales = np.ones(self.batch_size)
        self.batch_paddings = np.zeros((self.batch_size, 4))

        _input_name = self.input_info.name
        _input_data = np.zeros(self.input_info.shape, dtype=self.input_info.dtype)
        self.input_buffer = {_input_name: _input_data}

        # 加载模型元数据
        self._parse_metadata()
        self.stride = self.metadata.get("stride", 32)
        self.task = self.metadata.get("task", "detection")
        self.batch = self.metadata.get("batch", self.batch_size or 1)
        self.imgsz = self.metadata.get("imgsz", self.input_info.shape[-1] or 640)
        self.names = self.metadata.get("names", None)
        self.kpt_shape = self.metadata.get("kpt_shape", None)

    def _parse_metadata(self) -> None:
        """安全地解析模型元数据.

        使用安全的方法解析字符串格式的元数据，避免使用eval()带来的安全风险。

        Raises:
            ValueError: 当元数据格式无法解析时.
        """
        for k, v in self.metadata.items():
            try:
                if k in {"stride", "batch"}:
                    self.metadata[k] = int(v)
                elif k in {"imgsz", "names", "kpt_shape"} and isinstance(v, str):
                    # 尝试使用ast.literal_eval安全解析
                    try:
                        self.metadata[k] = ast.literal_eval(v)
                    except (ValueError, SyntaxError):
                        # 如果ast.literal_eval失败，尝试JSON解析
                        try:
                            self.metadata[k] = json.loads(v)
                        except json.JSONDecodeError:
                            # 如果都失败，保持原始字符串值并记录警告
                            print(f"警告: 无法解析元数据 '{k}': {v}，保持原始值")
            except Exception as e:
                print(f"警告: 解析元数据 '{k}' 时出错: {e}，保持原始值")

    @overload
    def predict(self, images: str | np.ndarray) -> T: ...

    @overload
    def predict(self, images: Sequence[str | np.ndarray]) -> Sequence[T]: ...

    def predict(self, images: Sequence[str | np.ndarray] | str | np.ndarray) -> T | Sequence[T]:
        """对图像进行推理.

        该方法可以处理单张图像或多张图像的批量推理.

        Args:
            images: 输入图像.可以是以下形式之一：
                - 单张图像的文件路径(str)
                - 单张图像的 numpy 数组(np.ndarray)
                - 多张图像的文件路径列表(List[str])
                - 多张图像的 numpy 数组列表(List[np.ndarray])

        Returns:
            推理结果.根据输入的不同,返回类型会有所不同：
                - 对于单张图像输入,返回单个推理结果(类型 T)
                - 对于多张图像输入,返回推理结果列表(List[T])

            其中 T 是由子类定义的具体结果类型.

        Raises:
            ValueError: 如果输入的图像格式不正确或无法加载图像.

        Note:
            具体的返回值格式取决于子类中 `postprocess` 方法的实现.
        """
        if isinstance(images, (str, np.ndarray)):
            images = [images]
            input_is_sequence = False
        else:
            input_is_sequence = True

        self._validate_batch_size(len(images))
        batch_images = [load_image(im) for im in images]

        self.preprocess(batch_images)
        batch_result = self.forward(self.input_buffer)
        batch_result = self.postprocess(batch_images, batch_result)

        out = batch_result if input_is_sequence else batch_result[0] if len(batch_result) == 1 else batch_result

        return out

    def _validate_batch_size(self, batch_size: int) -> None:
        """验证批次大小是否有效.

        Args:
            batch_size (int): 要验证的批次大小.

        Raises:
            ValueError: 当批次大小超过模型支持的最大批次时.
        """
        if batch_size > self.batch:
            raise ValueError(
                f"批次大小过大: 期望最大 {self.batch}，实际收到 {batch_size}。"
                f"请减少输入图像数量或使用支持更大批次的模型。"
            )
        if batch_size <= 0:
            raise ValueError("批次大小必须大于0")

    def preprocess(self, batch_image: list[np.ndarray]) -> None:
        """对一批图像进行预处理.

        Args:
            batch_image (List[np.ndarray]): 需要进行预处理的图像列表.
        """
        for i, im in enumerate(batch_image):
            image, scale, (pad_w, pad_h) = self._preprocess_single_image(im)
            self.input_buffer[self.input_info.name][i] = image
            self.batch_scales[i] = scale
            self.batch_paddings[i] = [pad_w, pad_h, pad_w, pad_h]

    def _preprocess_single_image(self, image: np.ndarray) -> tuple[np.ndarray, float, tuple[int, int]]:
        """预处理单张图像.

        Args:
            image (np.ndarray): 需要进行预处理的输入图像.

        Returns:
            Tuple[np.ndarray, float, Tuple[int, int]]: 返回预处理后的图像、缩放比例和填充信息的元组.

        Note:
            预处理步骤包括:
            1. 调整图像大小并添加填充(letterbox)
            2. 归一化到[0,1]范围
            3. 转换维度顺序从HWC到CHW
        """
        resize_shape = (self.input_info.shape[2], self.input_info.shape[3])
        image, scale, padding = letterbox(image, resize_shape)
        image = image.astype(self.input_info.dtype) / 255.0
        image = image.transpose((2, 0, 1))
        return image, scale, padding

    @abstractmethod
    def postprocess(self, batch_image: Sequence[np.ndarray], batch_result: Sequence[np.ndarray]) -> Sequence[T]:
        """对一批图像进行后处理.

        Args:
            batch_image (List[np.ndarray]): 需要进行后处理的图像列表.
            batch_result (List[np.ndarray]): 需要进行后处理的结果列表.

        Returns:
            List[T]: 后处理后的结果列表.
        """
        pass
