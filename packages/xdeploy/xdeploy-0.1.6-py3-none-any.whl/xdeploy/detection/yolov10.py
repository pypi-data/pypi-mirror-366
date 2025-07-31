"""YOLOv10,这是由清华大学研究团队最新提出的,遵循 YOLO 系列设计原则,致力于打造实时端到端的高性能目标检测器.

Examples:
    >>> from xdeploy.detection import YOLOv10
    >>> detector = YOLOv10("yolov10n.onnx", score_threshold=0.5, device="CPU")
    >>> result = detector.predict("input.jpg")[0]
    >>> results.draw()
"""

from __future__ import annotations

import numpy as np

from xdeploy.base import YOLO
from xdeploy.results import DetectionResult


class YOLOv10(YOLO[DetectionResult]):
    """YOLOv10,这是由清华大学研究团队最新提出的,遵循 YOLO 系列设计原则,致力于打造实时端到端的高性能目标检测器."""

    def __init__(self, model_path: str, score_threshold: float = 0.35, device: str = "CPU"):
        """初始化对象.

        Args:
            model_path (str): 模型文件的路径.
            score_threshold (float, 可选): 物体检测的得分阈值.默认为0.35.
            device (str, 可选): 推理使用的设备.默认为"CPU"，可选"CPU、GPU".
        """
        super().__init__(model_path=model_path, device=device)
        self.score_threshold = score_threshold

    def postprocess(self, batch_image: list[np.ndarray], batch_result: list[np.ndarray]) -> list[DetectionResult]:
        """对批量结果进行后处理.

        Args:
            batch_image (List[np.ndarray]): 原始图像,检测或结果可视化.
            batch_result (List[np.ndarray]): 需要进行后处理的批量结果，[batch_size, 300, [x,y,x,y,score,class_id]].

        Returns:
            List[DetectionResult]: 后处理后的批量结果.
        """
        detections = []
        for i, batch in enumerate(batch_result):
            # 检测结果切片
            batch = batch[batch[:, 4] > self.score_threshold]
            boxes, scores, class_ids = np.split(batch, [4, 5], axis=1)
            scores = scores.reshape(-1)
            class_ids = class_ids.reshape(-1)
            names = [self.names[int(class_id)] if self.names is not None else int(class_id) for class_id in class_ids]

            # 修正边界框坐标
            boxes -= self.batch_paddings[i]
            boxes[:, 0::2] = np.clip(boxes[:, 0::2], 0, self.input_info.shape[3])
            boxes[:, 1::2] = np.clip(boxes[:, 1::2], 0, self.input_info.shape[2])
            boxes /= self.batch_scales[i]

            detections.append(DetectionResult(batch_image[i], boxes, scores, class_ids, names))

        return detections
