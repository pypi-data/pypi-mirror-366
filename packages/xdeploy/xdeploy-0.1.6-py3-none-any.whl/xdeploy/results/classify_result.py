"""图像分类结果."""

from __future__ import annotations

import cv2
import numpy as np


class ClassifyResult:
    """图像分类结果.

    Args:
        orig_img (np.ndarray): 原始RGB格式图像.
        class_ids (List[int]): 表示单张图片的分类结果，其个数根据在使用分类模型时传入的 `topk` 决定，例如可以返回 `top5` 的分类结果.
        scores (List[float]): 表示单张图片在相应分类结果上的置信度，其个数根据在使用分类模型时传入的 `topk` 决定，例如可以返回 `top5` 的分类置信度.

    """

    def __init__(
        self,
        orig_img: np.ndarray,
        class_ids: list[int] | None = None,
        scores: list[float] | None = None,
    ):
        """初始化图像分类结果."""
        self.orig_img = orig_img
        self.class_ids = class_ids or []
        self.scores = scores or []

    def __repr__(self) -> str:
        """返回图像分类结果的字符串表示."""
        return f"ClassifyResult(orig_img={self.orig_img}, class_ids={self.class_ids}, scores={self.scores})"

    def __str__(self) -> str:
        """返回图像分类结果的字符串表示."""
        return repr(self)

    def __len__(self) -> int:
        """返回图像分类结果的长度."""
        return len(self.class_ids)

    def __getitem__(self, index: int) -> tuple[int, float]:
        """返回图像分类结果的索引."""
        return self.class_ids[index], self.scores[index]

    def __iter__(self):
        """返回图像分类结果的迭代器."""
        for i in range(len(self)):
            yield self[i]

    def draw(self, save_path: str | None = None) -> np.ndarray:
        """绘制检测结果.

        Args:
            save_path (Optional[str], optional): 图像保存路径. Defaults to None.

        Returns:
            np.ndarray: 绘制了检测结果的图像.
        """
        img = self.orig_img.copy()

        if len(self) == 0:
            if save_path is not None:
                cv2.imwrite(save_path, cv2.cvtColor(img, cv2.COLOR_RGB2BGR))
            return self.orig_img

        text_color = (0, 128, 255)
        draw_thickness = int(min(img.shape[:2]) // 320)

        # 绘制分类结果
        cv2.putText(
            img,
            f"Top {len(self)} detections:",
            (10, 30),
            cv2.FONT_HERSHEY_SIMPLEX,
            1,
            text_color,
            draw_thickness,
        )
        for index, (cls_id, score) in enumerate(self):
            cv2.putText(
                img,
                f"{index}. {cls_id}: {score:.2f}",
                (20, 30 * (index + 2)),
                cv2.FONT_HERSHEY_SIMPLEX,
                1,
                text_color,
                draw_thickness,
            )

        if save_path is not None:
            cv2.imwrite(save_path, cv2.cvtColor(img, cv2.COLOR_RGB2BGR))

        return img
