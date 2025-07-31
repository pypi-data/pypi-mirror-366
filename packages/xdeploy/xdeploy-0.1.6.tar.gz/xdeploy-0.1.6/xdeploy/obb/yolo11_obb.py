"""YOLO11 OBB 检测模型.

Example:
    >>> from xdeploy.obb import YOLO11OBB
    >>> detector = YOLO11OBB(model_path="yolov8n_obb.onnx", score_threshold=0.35, nms_threshold=0.45, device="CPU")
    >>> results = detector.predict("test.jpg")
    >>> results = detector.predict([im1, im2, im3])
    >>> results.draw()
"""

from __future__ import annotations

from .yolov8_obb import YOLOv8OBB


class YOLO11OBB(YOLOv8OBB): ...
