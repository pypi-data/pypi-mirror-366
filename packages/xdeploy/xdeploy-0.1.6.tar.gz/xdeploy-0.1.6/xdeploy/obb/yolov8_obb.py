"""YOLOv8 OBB 检测模型.

Example:
    >>> from xdeploy.obb import YOLOv8OBB
    >>> detector = YOLOv8OBB(model_path="yolov8n_obb.onnx", score_threshold=0.35, nms_threshold=0.45, device="CPU")
    >>> results = detector.predict("test.jpg")
    >>> results = detector.predict([im1, im2, im3])
    >>> results.draw()
"""

from __future__ import annotations

import cv2
import numpy as np

from xdeploy.base import YOLO
from xdeploy.results import OBBResult


class YOLOv8OBB(YOLO[OBBResult]):
    """YOLOv8 OBB 检测模型."""

    def __init__(
        self, model_path: str, score_threshold: float = 0.35, nms_threshold: float = 0.45, device: str = "CPU"
    ):
        """初始化对象.

        Args:
            model_path (str): 模型文件的路径.
            score_threshold (float, 可选): 物体检测的得分阈值.默认为0.35.
            nms_threshold (float, 可选): 非最大抑制阈值.默认为0.45.
            device (str, 可选): 推理使用的设备.默认为"CPU"，可选"CPU、GPU".
        """
        super().__init__(model_path=model_path, device=device)

        self.score_threshold = score_threshold
        self.nms_threshold = nms_threshold

    def postprocess(self, batch_image: list[np.ndarray], batch_result: list[np.ndarray]) -> list[OBBResult]:
        """对批量结果进行后处理.

        Args:
            batch_image (List[np.ndarray]): 原始图像,检测或结果可视化.
            batch_result (List[np.ndarray]): 需要进行后处理的批量结果.

        Returns:
            list[DetectionResult]: 后处理后的批量结果.
        """
        outputs = np.transpose(batch_result, (0, 2, 1))  # [1, 84, 8400] -> [1, 8400, 84]
        detections = []
        for i, batch in enumerate(outputs):
            # 检测结果切片
            boxes, classes_scores, angles = np.split(batch, [4, -1], axis=1)
            class_ids = np.argmax(classes_scores, axis=1)
            scores = np.amax(classes_scores, axis=1)
            angles = map(int, (angles - np.pi) * 180 / np.pi)

            # 计算边界框的坐标 xywh -> xyxy
            boxes[:, :2] -= boxes[:, 2:] / 2
            boxes[:, 2:] += boxes[:, :2]

            # 修正边界框坐标
            boxes -= self.batch_paddings[i]
            boxes /= self.batch_scales[i]

            # 计算边界框的坐标 xyxy -> xywh
            boxes_xywh = np.zeros_like(boxes)
            boxes_xywh[:, :2] = (boxes[:, :2] + boxes[:, 2:]) / 2  # 中心点
            boxes_xywh[:, 2:] = boxes[:, 2:] - boxes[:, :2]  # wh

            rboxes = []
            for box, angle in zip(boxes_xywh, angles):
                center = box[:2]
                size = box[2:4]
                angle = angle % 180
                if size[0] < size[1]:
                    size = size[::-1]
                    angle += 90
                box = cv2.RotatedRect(center=center, size=size, angle=angle)
                rboxes.append(box)
            rboxes = np.array(rboxes)

            # NMS
            indices = cv2.dnn.NMSBoxesRotated(rboxes, scores, self.score_threshold, self.nms_threshold)  # type: ignore
            if len(indices) > 0:
                detections.append(OBBResult(batch_image[i], rboxes[indices], scores[indices], class_ids[indices]))  # type: ignore
            else:
                detections.append(OBBResult(batch_image[i]))
        return detections
