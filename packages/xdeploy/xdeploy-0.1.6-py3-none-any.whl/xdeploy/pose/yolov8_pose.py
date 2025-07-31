"""YOLOv8Pose 模型.

YOLOv8Pose 模型输出格式如下：
prediction: (1, 56, *), where 56 = 4 + 1 + 3 * 17
    4 -> box_xywh
    1 -> box_score
    3*17 -> (x, y, kpt_score) * 17 keypoints

Example:
    >>> from xdeploy.pose import YOLOv8Pose
    >>> detector = YOLOv8Pose("yolov8n-pose.onnx")
    >>> results = detector.predict("input.jpg")
    >>> results.draw()
"""

from __future__ import annotations

import cv2
import numpy as np

from xdeploy.base import YOLO
from xdeploy.results import PoseResult


class YOLOv8Pose(YOLO[PoseResult]):
    """YOLOv8Pose 模型.

    Args:
        model_path (str): 模型文件的路径.
        score_threshold (float, 可选): 物体检测的得分阈值.默认为0.35.
        nms_threshold (float, 可选): 非最大抑制阈值.默认为0.45.
        device (str, 可选): 推理使用的设备.默认为"CPU"，可选"CPU、GPU".
    """

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

    def postprocess(self, batch_image: list[np.ndarray], batch_result: list[np.ndarray]) -> list[PoseResult]:
        """对批量结果进行后处理.

        Args:
            batch_image ( Union[list[str], list[npt.NDArray[np.uint8]]]): 原始图像,检测或结果可视化.
            batch_result (list[npt.NDArray[np.float32]]): 需要进行后处理的批量结果.

        Returns:
            List[DetectionResult]: 后处理后的批量结果.
        """
        nc = len(self.names)
        outputs = np.transpose(batch_result, (0, 2, 1))  # [1, 84, 8400] -> [1, 8400, 84]
        detections = []
        for i, batch in enumerate(outputs):
            # 置信度过滤
            batch = batch[batch[:, 4 : 4 + nc].max(1) > self.score_threshold]
            if len(batch) == 0:
                detections.append(PoseResult(batch_image[i]))
                continue

            # 检测结果切片
            boxes, classes_scores, keypoints = np.split(batch, [4, 4 + nc], axis=1)
            class_ids = np.argmax(classes_scores, axis=1)
            scores = np.amax(classes_scores, axis=1)

            # NMS
            indices = cv2.dnn.NMSBoxesBatched(boxes, scores, class_ids, self.score_threshold, self.nms_threshold)  # type: ignore
            if len(indices) == 0:
                detections.append(PoseResult(batch_image[i]))
                continue

            # 确定关键点维度
            if keypoints.shape[-1] % 3 == 0:
                keypoints = keypoints.reshape((len(keypoints), -1, 3))
            elif keypoints.shape[-1] % 2 == 0:
                keypoints = keypoints.reshape((len(keypoints), -1, 2))

            boxes = boxes[indices]
            class_ids = class_ids[indices]
            scores = scores[indices]
            keypoints = keypoints[indices]
            names = [self.names[int(class_id)] if self.names is not None else int(class_id) for class_id in class_ids]

            # 计算边界框的坐标 xywh -> xyxy
            boxes[:, :2] -= boxes[:, 2:] / 2
            boxes[:, 2:] += boxes[:, :2]

            # 修正边界框坐标
            boxes -= self.batch_paddings[i]
            boxes[:, 0::2] = np.clip(boxes[:, 0::2], 0, self.input_info.shape[3])
            boxes[:, 1::2] = np.clip(boxes[:, 1::2], 0, self.input_info.shape[2])
            boxes /= self.batch_scales[i]

            # 修正 keypoints 坐标
            keypoints[:, :, :2] -= self.batch_paddings[i][:2]
            keypoints[:, :, 0] = np.clip(keypoints[:, :, 0], 0, self.input_info.shape[3])
            keypoints[:, :, 1] = np.clip(keypoints[:, :, 1], 0, self.input_info.shape[2])
            keypoints[:, :, :2] /= self.batch_scales[i]

            detections.append(PoseResult(batch_image[i], boxes, scores, class_ids, keypoints, names))

        return detections
