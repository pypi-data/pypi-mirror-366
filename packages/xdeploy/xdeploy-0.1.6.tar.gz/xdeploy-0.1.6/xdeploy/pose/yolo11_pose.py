"""YOLO11Pose 模型.

YOLO11Pose 模型输出格式如下：
prediction: (1, 56, *), where 56 = 4 + 1 + 3 * 17
    4 -> box_xywh
    1 -> box_score
    3*17 -> (x, y, kpt_score) * 17 keypoints

Example:
    >>> from xdeploy.pose import YOLO11Pose
    >>> detector = YOLO11Pose("yolov8n-pose.onnx")
    >>> results = detector.predict("input.jpg")
    >>> results.draw()
"""

from __future__ import annotations

from .yolov8_pose import YOLOv8Pose


class YOLO11Pose(YOLOv8Pose): ...
