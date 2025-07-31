"""基于PaddleSeg的分割模型."""

from __future__ import annotations

import cv2
import numpy as np

from xdeploy.base import Backend


class PaddleSeg(Backend):
    """分割模型,基于OCRNET."""

    def __init__(self, model_path: str, device: str = "CPU", std: tuple = (0.5,), mean: tuple = (0.5,)):
        """初始化对象.

        Args:
            model_path (str): 模型文件的路径.
            device (str, 可选): 推理使用的设备.默认为"CPU"，可选"CPU、GPU".
            std (Tuple, 可选): 标准差用于归一化.默认为 (0.5,).
            mean (Tuple, 可选): 均值用于归一化.默认为 (0.5,).
        """
        super().__init__(model_path=model_path, device=device)
        self.input_shape = (512, 512)  # 动态 batch

        input_info = self.inputs_info[0]
        self.input_type = input_info.dtype
        self.input_name = input_info.name

        self.std = std
        self.mean = mean

    def predict(self, image: list | np.ndarray) -> np.ndarray:
        """对给定的输入图像进行预测.

        参数:
            image (Union[List, np.ndarray]): 需要进行预测的输入图像.

        返回值:
            np.ndarray: 输入图像的预测输出.
        """
        batch_image = self.preprocess(image)
        input_buffer = {self.input_name: batch_image}

        return self.forward(input_buffer)

    def preprocess(self, image: list | np.ndarray) -> np.ndarray:
        """预处理图像或图像列表.

        参数:
            image (List | np.ndarray): 需要进行预处理的图像或图像列表.
            std (Tuple, 可选): 标准差用于归一化.默认为 (0.5,).
            mean (Tuple, 可选): 均值用于归一化.默认为 (0.5,).

        返回:
            np.ndarray: 预处理后的图像作为一个 NumPy 数组.
        """
        if isinstance(image, np.ndarray):
            image = [image]
        ims = np.array([cv2.resize(im, self.input_shape) for im in image])
        ims -= np.asarray(self.mean, dtype=self.input_type)
        ims /= np.asarray(self.std, dtype=self.input_type)
        ims /= 255
        ims = np.transpose(ims, (0, 3, 1, 2)).astype(self.input_type)

        return ims
