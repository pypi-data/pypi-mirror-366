"""YOLOv8 分类模型.

Example:
    >>> from xdeploy.classification  import YOLOv8CLS
    >>> model = YOLOv8CLS(model_path="yolov8n-cls.onnx", device="CPU")
    >>> results = model(["input.jpg"], topk=1)
    >>> print(results)
"""

from __future__ import annotations

from typing import overload

import numpy as np

from xdeploy.base import YOLO
from xdeploy.results import ClassifyResult
from xdeploy.utils.data_load import load_image


class YOLOv8CLS(YOLO[ClassifyResult]):
    """YOLOv8分类模型."""

    def __init__(self, model_path: str, device: str = "CPU"):
        """初始化对象.

        Args:
            model_path (str): 模型文件的路径.
            device (str, 可选): 推理使用的设备.默认为"CPU"，可选"CPU、GPU".
        """
        super().__init__(model_path=model_path, device=device)

    @overload
    def predict(self, images: str | np.ndarray, topk: int = 1) -> ClassifyResult: ...

    @overload
    def predict(self, images: list[str | np.ndarray], topk: int = 1) -> list[ClassifyResult]: ...

    def predict(
        self, images: list[str | np.ndarray] | str | np.ndarray, topk: int = 1
    ) -> ClassifyResult | list[ClassifyResult]:
        """对图像进行推理.

        Args:
            images (Union[List[Union[str, np.ndarray]], str, np.ndarray]): 一组图像的路径或numpy数组.
            topk (int, 可选): 保留的最大检测结果数.

        Returns:
            ClassifyResult | list[ClassifyResult]: 一组包含每个图像的检测结果的列表.
        """
        if isinstance(images, str | np.ndarray):
            images = [images]

        self._validate_batch_size(len(images))
        batch_images = [load_image(im) for im in images]

        self.preprocess(batch_images)
        batch_result = self.forward(self.input_buffer)
        batch_result = self.postprocess(batch_images, batch_result, topk)
        return batch_result[0] if len(batch_result) == 1 else batch_result

    def postprocess(
        self, batch_image: list[np.ndarray], batch_result: list[np.ndarray], k: int = 1
    ) -> list[ClassifyResult]:
        """对批量结果进行后处理.

        Args:
            batch_image (List[np.ndarray]): 原始图像,检测或结果可视化.
            batch_result (List[np.ndarray]): 需要进行后处理的批量结果.
            k (int, 可选): 保留的最大检测结果数.

        Returns:
            List[ClassifyResult]: 后处理后的批量结果.
        """
        detections = []
        for i, batch in enumerate(batch_result):
            class_ids = np.argsort(batch)[-k:][::-1]
            scores = batch[class_ids]

            detections.append(ClassifyResult(batch_image[i], class_ids.tolist(), scores.tolist()))

        return detections
