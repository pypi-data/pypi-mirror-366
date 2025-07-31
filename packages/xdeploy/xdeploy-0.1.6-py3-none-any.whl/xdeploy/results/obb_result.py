"""旋转框检测结果.

旋转框检测结果包括原始图像、检测边界框、检测得分、检测类别ID.

Example:
    >>> from xdeploy.results import OBBResult
    >>> obb_result = OBBResult(orig_img, rboxes, scores, class_ids)
"""

from __future__ import annotations

import cv2
import numpy as np

from xdeploy.utils.visualize import draw_obb


class OBBResult:
    """旋转框检测结果.

    Args:
        orig_img (np.ndarray): 原始RGB格式图像.
        rboxes (np.ndarray[float]): 旋转边界框,格式为 (x, y, w, h, angle).
        scores (np.ndarray[float]): 分数.
        class_ids (np.ndarray[float]): 类别 ID.

    Attributes:
        rboxes (np.ndarray): 旋转边界框(四个顶点坐标),格式为 (x, y, w, h, angle).
        scores (np.ndarray): 分数.
        class_ids (np.ndarray): 类别 ID.
    """

    def __init__(
        self,
        orig_img: np.ndarray,
        rboxes: list[cv2.RotatedRect] | None = None,
        scores: np.ndarray | None = None,
        class_ids: np.ndarray | None = None,
    ) -> None:
        """初始化旋转框检测结果.

        Args:
            orig_img (np.ndarray): 原始RGB格式图像.
            rboxes (np.ndarray[float]): 旋转边界框,格式为 (x, y, w, h, angle).
            scores (np.ndarray[float]): 分数.
            class_ids (np.ndarray[float]): 类别 ID.
        """
        self.orig_img = orig_img
        self.rboxes = rboxes if rboxes is not None else []
        self.scores = scores if scores is not None else []
        self.class_ids = class_ids if class_ids is not None else []

    def __bool__(self) -> bool:
        return len(self) > 0

    def __len__(self) -> int:
        return len(self.rboxes)

    def __getitem__(self, index: int) -> tuple[cv2.RotatedRect, np.ndarray, np.ndarray]:
        return self.rboxes[index], self.scores[index], self.class_ids[index]

    def __iter__(self):
        for i in range(len(self)):
            yield self[i]

    def draw(self, with_scores: bool = True, save_path: str | None = None) -> np.ndarray:
        """在图像上绘制边界框，并可选择保存图像的函数.

        Args:
            with_scores (bool): 是否显示检测得分.
            save_path (Optional[str]): 保存带有边界框绘制的图像的文件路径.

        Returns:
            np.ndarray: 绘制了边界框的图像.
        """
        if len(self) == 0 and save_path is None:
            return self.orig_img
        scores = None if not with_scores else self.scores
        return draw_obb(self.orig_img, self.rboxes, self.class_ids, scores, save_path=save_path)  # type: ignore
