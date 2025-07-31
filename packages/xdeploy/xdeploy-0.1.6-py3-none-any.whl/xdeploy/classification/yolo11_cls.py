"""YOLO11 分类模型.

Example:
    >>> from xdeploy.classification  import YOLO11CLS
    >>> model = YOLO11CLS(model_path="yolov8n-cls.onnx", device="CPU")
    >>> results = model(["input.jpg"], topk=1)
    >>> print(results)
"""

from __future__ import annotations

from .yolov8_cls import YOLOv8CLS


class YOLO11CLS(YOLOv8CLS): ...
