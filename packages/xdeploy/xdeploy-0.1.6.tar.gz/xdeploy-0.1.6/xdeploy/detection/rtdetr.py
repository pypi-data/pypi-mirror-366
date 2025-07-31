"""Baidu's RT-DETR 模型,是基于Vision Transformer的实时目标检测器.

RT-DETR提供实时性能和高准确性,在CUDA与TensorRT等加速后端上表现出色.它具有高效的混合编码器和IoU感知的查询选择,以增强检测准确性.

有关RT-DETR的更多信息,请访问:https://arxiv.org/pdf/2304.08069.pdf

Example:
    >>> from xdeploy.detection import RTDETR
    >>> detector = RTDETR("rt_detr.onnx", score_threshold=0.5)
    >>> results = detector.predict("input.jpg")[0]
    >>> results.draw()
"""

from __future__ import annotations

import numpy as np

from xdeploy.base import YOLO
from xdeploy.results import DetectionResult


class RTDETR(YOLO[DetectionResult]):
    """Baidu's RT-DETR 模型.

    这是基于Vision Transformer的实时目标检测器,具有高准确性和实时性能。它支持高效的混合编码、IoU感知的查询选择和可调整的推理速度.

    Attributes:
        score_threshold (float): 物体检测的得分阈值.默认为0.35.
    """

    def __init__(self, model_path: str, score_threshold: float = 0.35, device: str = "CPU"):
        """初始化对象.

        Args:
            model_path (str): 模型文件的路径.
            score_threshold (float, 可选): 物体检测的得分阈值.默认为0.35.
            device (str, 可选): 推理使用的设备.默认为"CPU",可选"CPU、GPU".
        """
        super().__init__(model_path=model_path, device=device)
        self.score_threshold = score_threshold

    def postprocess(self, batch_image: list[np.ndarray], batch_result: list[np.ndarray]) -> list[DetectionResult]:
        """对批量结果进行后处理.

        Args:
            batch_image (List[np.ndarray]): 原始图像,检测或结果可视化.
            batch_result (List[np.ndarray]): 需要进行后处理的批量结果.

        Returns:
            List[DetectionResult]: 后处理后的批量结果.
        """
        detections = []
        for i, batch in enumerate(batch_result):
            # 检测结果切片
            boxes, classes_scores = np.split(batch, [4], axis=1)
            class_ids = np.argmax(classes_scores, axis=1)
            scores = np.amax(classes_scores, axis=1)
            names = [self.names[int(class_id)] if self.names is not None else int(class_id) for class_id in class_ids]

            # 计算边界框的坐标 xywh -> xyxy
            boxes[:, :2] -= boxes[:, 2:] / 2
            boxes[:, 2:] += boxes[:, :2]

            # 修正边界框坐标
            pad_w, pad_h = self.batch_paddings[i, 0], self.batch_paddings[i, 1]
            boxes[:, 0::2] = np.clip(boxes[:, 0::2] * self.input_info.shape[3] - pad_w, 0, self.input_info.shape[3])
            boxes[:, 1::2] = np.clip(boxes[:, 1::2] * self.input_info.shape[3] - pad_h, 0, self.input_info.shape[2])
            boxes /= self.batch_scales[i]

            # 过滤掉得分低于阈值的边界框
            indices = scores > self.score_threshold
            detections.append(
                DetectionResult(batch_image[i], boxes[indices], scores[indices], class_ids[indices], names)
            )
        return detections
