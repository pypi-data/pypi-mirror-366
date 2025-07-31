"""目标检测识别结果模块.

该模块提供了目标检测识别结果类.

Example:
    >>> from xdeploy.results import DetectionResult
    >>> detection_result = DetectionResult(orig_img, boxes, scores, class_ids)
    >>> detection_result.draw()
"""

from __future__ import annotations

from pathlib import Path

import cv2
import numpy as np

from xdeploy.utils.visualize import draw_detection


class DetectionResult:
    """目标检测识别结果.

    Attributes:
        orig_img (np.ndarray): 原始RGB格式图像.
        boxes (np.ndarray): 检测边界框.
        scores (np.ndarray): 检测得分.
        class_ids (np.ndarray): 检测类别ID.
        names (List[str]): 检测类别名称.
    """

    def __init__(
        self,
        orig_img: np.ndarray,
        boxes: np.ndarray | None = None,
        scores: np.ndarray | None = None,
        class_ids: np.ndarray | None = None,
        names: list[str] | None = None,
    ) -> None:
        """初始化检测结果.

        Args:
            orig_img (np.ndarray): 原始图像.
            boxes (Optional[np.ndarray], 可选): 检测边界框.
            scores (Optional[np.ndarray], 可选): 检测得分.
            class_ids (Optional[np.ndarray], 可选): 检测类别ID.
            names (Optional[List[str]], 可选): 检测类别名称.
        """
        self.orig_img = orig_img
        self.boxes = boxes.astype(np.float32) if boxes is not None else np.array([])
        self.scores = scores.astype(np.float32) if scores is not None else np.array([])
        self.class_ids = class_ids.astype(np.int8) if class_ids is not None else np.array([])

        self.names = names

    def __repr__(self) -> str:
        return f"{self.__class__.__name__}(boxes={self.boxes}, scores={self.scores}, class_ids={self.class_ids})"

    def __len__(self) -> int:
        return len(self.boxes)

    def __getitem__(self, index: int) -> tuple[np.ndarray, np.ndarray, np.ndarray]:
        """返回指定索引的检测结果.

        Args:
            index (int): 指定索引.

        Returns:
            Tuple:
                boxes (np.ndarray): 检测边界框.
                scores (np.ndarray): 检测得分.
                class_ids (np.ndarray): 检测类别ID.
        """
        return self.boxes[index], self.scores[index], self.class_ids[index]

    def __iter__(self):
        for i in range(len(self)):
            yield self[i]

    def __bool__(self) -> bool:
        return len(self) > 0

    def to_dict(self) -> dict[str, np.ndarray | list]:
        """将检测结果转换为字典.

        Returns:
            Dict[str, Union[np.ndarray, List]]: 检测结果字典.
        """
        return {"boxes": self.boxes, "scores": self.scores, "class_ids": self.class_ids}

    def draw(
        self,
        names: list[str] | None = None,
        colors: list[tuple[int, int, int]] | None = None,
        with_names: bool = True,
        with_scores: bool = True,
        save_path: str | None = None,
    ) -> np.ndarray:
        """绘制检测结果.

        Args:
            names (List[str], 可选): 类别名称列表.
            colors (List[Tuple[int, int, int]], 可选): 绘制边界框的颜色列表.
            with_names (bool): 是否显示类别名称.
            with_scores (bool): 是否显示检测得分.
            save_path (str, 可选): 保存绘制结果的文件路径.默认为 None.

        Returns:
            np.ndarray: 绘制了检测结果的图像.
        """
        if len(self) == 0 and save_path is None:
            return self.orig_img

        if not with_names:
            names = None
        elif names is None:
            names = self.names or [f"{id}" for id in self.class_ids]

        scores = None if not with_scores else self.scores.tolist()
        return draw_detection(self.orig_img, self.boxes, names, self.class_ids.tolist(), scores, colors, save_path)

    def filter(self, score: float | None = None, class_id: list[int] | None = None) -> None:
        """过滤检测结果.

        Args:
            score (float, 可选): 检测得分阈值.默认为 None.
            class_id (List[int], 可选): 检测类别ID.默认为 None.
        """
        if len(self) == 0:
            return
        mask = np.ones(len(self.boxes), dtype=bool)
        if score is not None:
            mask &= self.scores >= score
        if class_id is not None:
            mask &= np.isin(self.class_ids, class_id)
        self.boxes = self.boxes[mask]
        self.scores = self.scores[mask]
        self.class_ids = self.class_ids[mask]

    def get_crops(self, padding: int = 0) -> list[np.ndarray]:
        """裁剪检测结果边界框的图像.

        Args:
            padding (int, 可选): 边界框的填充像素数.默认为 0.

        Returns:
            List[np.ndarray]: 边界框裁剪出的图像列表.
        """
        crops = []
        for box in self.boxes:
            box = box.astype(np.int32)
            x1, y1, x2, y2 = box
            crop = self.orig_img[
                max(0, y1 - padding) : min(self.orig_img.shape[0], y2 + padding),
                max(0, x1 - padding) : min(self.orig_img.shape[1], x2 + padding),
            ]
            crops.append(crop)
        return crops

    def save_crops(self, save_dir: str, padding: int = 0) -> None:
        """保存检测结果裁剪出的图像.

        Args:
            save_dir (str): 保存裁剪图像的目录.
            padding (int, 可选): 边界框的填充像素数.默认为 0.
        """
        for i, crop in enumerate(self.get_crops(padding)):
            cv2.imwrite(f"{save_dir}/{i}.jpg", crop[..., ::-1])  # RGB to BGR

    def save_txt(self, save_path: str, with_score: bool = True, with_label: bool = True) -> None:
        """保存检测结果到txt文件.

        Args:
            save_path (str): 保存检测结果的文件路径.
            with_score (bool, 可选): 是否保存得分.默认为 True.
            with_label (bool, 可选): 是否保存类别名称.默认为 True.
        """
        with Path(save_path).open("w") as f:
            for box, score, class_id in zip(self.boxes, self.scores, self.class_ids):
                line = f"{box[0]} {box[1]} {box[2]} {box[3]}"
                if with_score:
                    line += f" {score}"
                if with_label:
                    line += f" {class_id}"
                f.write(line + "\n")
