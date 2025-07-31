"""关键点检测识别结果.

关键点检测识别结果包括原始图像、检测边界框、检测得分、检测类别ID.

Example:
    >>> from xdeploy.results import PoseResult
    >>> pose_result = PoseResult(orig_img, boxes, scores, class_ids)
"""

from __future__ import annotations

import cv2
import numpy as np

from xdeploy.utils.visualize import COLORS


class PoseResult:
    """关键点检测识别结果.

    Attributes:
        orig_img (np.ndarray): 原始RGB格式图像.
        boxes (np.ndarray): 检测边界框.
        scores (np.ndarray): 检测得分.
        class_ids (np.ndarray): 检测类别ID.
        keypoints (np.ndarray): 关键点坐标.
        names (List[str]): 检测类别名称.
    """

    def __init__(
        self,
        orig_img: np.ndarray,
        boxes: np.ndarray | None = None,
        scores: np.ndarray | None = None,
        class_ids: np.ndarray | None = None,
        keypoints: np.ndarray | None = None,
        names: list[str] | None = None,
    ) -> None:
        """初始化函数.

        Args:
            orig_img (np.ndarray): 原始RGB格式图像.
            boxes (Optional[np.ndarray], 可选): 检测边界框.
            scores (Optional[np.ndarray], 可选): 检测得分.
            class_ids (Optional[np.ndarray], 可选): 检测类别ID.
            keypoints (Optional[np.ndarray], 可选): 关键点坐标.
            names (Optional[List[str]], 可选): 检测类别名称.
        """
        self.orig_img = orig_img
        self.boxes = boxes.astype(np.float32) if boxes is not None else np.array([])
        self.scores = scores.astype(np.float32) if scores is not None else np.array([])
        self.class_ids = class_ids.astype(np.int8) if class_ids is not None else np.array([])
        self.keypoints = keypoints.astype(np.float32) if keypoints is not None else np.array([])
        self.names = names

    def __repr__(self) -> str:
        return f"{self.__class__.__name__}:\n\tboxes={self.boxes}\n\tscores={self.scores}\n\tclass_ids={self.class_ids}\n\tkeypoints={self.keypoints}"

    def __len__(self) -> int:
        return len(self.boxes)

    def __getitem__(self, index: int) -> tuple[np.ndarray, np.ndarray, np.ndarray, np.ndarray]:
        """返回指定索引的检测结果.

        Args:
            index (int): 指定索引.

        Returns:
            Tuple:
                boxes (np.ndarray): 检测边界框.
                scores (np.ndarray): 检测得分.
                class_ids (np.ndarray): 检测类别ID.
                keypoints (np.ndarray): 关键点坐标.
        """
        return self.boxes[index], self.scores[index], self.class_ids[index], self.keypoints[index]

    def __iter__(self):
        for i in range(len(self)):
            yield self[i]

    def __bool__(self) -> bool:
        return len(self) > 0

    def to_dict(self) -> dict[str, np.ndarray | list]:
        """将关键点检测识别结果转换为字典.

        Returns:
            Dict[str, Union[np.ndarray, List]]: 关键点检测识别结果字典.
        """
        return {"boxes": self.boxes, "scores": self.scores, "class_ids": self.class_ids, "keypoints": self.keypoints}

    def draw(self, save_path: str | None = None) -> np.ndarray:
        """绘制检测结果.

        Args:
            save_path (str, 可选): 保存绘制结果的文件路径.默认为 None.

        Returns:
            np.ndarray: 绘制了检测结果的图像.
        """
        if len(self) == 0 and save_path is None:
            return self.orig_img

        img = self.orig_img.copy()

        # 绘制关键点
        for bbox, _score, class_id, keypoints in self:
            x1, y1, x2, y2 = map(int, bbox)
            cv2.rectangle(img, (x1, y1), (x2, y2), COLORS[class_id % len(COLORS)], 2)
            for i, point in enumerate(keypoints):
                x, y = int(point[0]), int(point[1])
                color = COLORS[i % len(COLORS)]
                cv2.circle(img, (x, y), 3, color, -1)

        # 保存图像
        if save_path:
            cv2.imwrite(save_path, cv2.cvtColor(img, cv2.COLOR_RGB2BGR))

        return img

    def save_txt(self, save_path: str, with_score: bool = True, with_label: bool = True) -> None:
        """保存检测结果到txt文件.

        Args:
            save_path (str): 保存检测结果的文件路径.
            with_score (bool, 可选): 是否保存得分.默认为 True.
            with_label (bool, 可选): 是否保存类别名称.默认为 True.
        """
        # TODO
        ...
