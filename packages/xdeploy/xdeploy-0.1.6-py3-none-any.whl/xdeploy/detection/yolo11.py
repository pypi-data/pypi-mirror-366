"""YOLO11,这是由 ultralytics 团队最新提出的,旨在快速、准确且易于使用，使其成为各种对象检测和跟踪、实例分割、图像分类和姿态估计任务的绝佳选择.

Examples:
    >>> from xdeploy.detection import YOLO11
    >>> detector = YOLO11("yolo11.onnx", score_threshold=0.5, device="CPU")
    >>> result = detector.predict("input.jpg")[0]
    >>> results.draw()
"""

from __future__ import annotations

from .yolov8 import YOLOv8


class YOLO11(YOLOv8):
    """YOLO11 检测模型.

    Attributes:
        model_path (str): 模型文件的路径.
        score_threshold (float, 可选): 物体检测的得分阈值.默认为0.35.
        nms_threshold (float, 可选): 非最大抑制阈值.默认为0.45.
        device (str, 可选): 推理使用的设备.默认为"CPU"，可选"CPU、GPU".
    """

    ...
