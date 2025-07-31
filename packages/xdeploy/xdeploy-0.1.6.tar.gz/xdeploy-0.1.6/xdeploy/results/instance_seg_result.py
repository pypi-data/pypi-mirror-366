"""分割结果模块.

该模块提供了一些分割结果类.

Example:
    >>> from xdeploy.results import InstanceSegResult
    >>> result = InstanceSegResult("test.jpg", bboxes, masks)
    >>> result.draw()
"""

from __future__ import annotations

from pathlib import Path

import cv2
import numpy as np

from xdeploy.utils.visualize import COLORS


class InstanceSegResult:
    """分割结果.

    Attributes:
        orig_img (np.ndarray): 原始RGB格式图像.
        bboxes (np.ndarray): 边界框, 类似于 (x1, y1, x2, y2, score, class_id, mask_pres).
        masks (np.ndarray): 掩膜.
        bg_mask (np.ndarray): 背景掩膜.
        segments (List): 分割掩膜轮廓的列表.
    """

    def __init__(self, image: np.ndarray, bboxes: np.ndarray, masks: np.ndarray):
        """初始化.

        Args:
            image (np.ndarray): 原始RGB格式图像.
            bboxes (np.ndarray): 边界框, 类似于 (x1, y1, x2, y2, score, class_id, mask_pres).
            masks (np.ndarray): 掩膜.
        """
        self.image = image
        self.bboxes = bboxes
        self.masks = masks
        self.bg_mask = self.get_bg_mask()
        self.segments = self.get_segments()

    def __len__(self) -> int:
        return len(self.bboxes)

    def __getitem__(self, index: int) -> tuple[np.ndarray, np.ndarray]:
        return self.bboxes[index], self.masks[index]

    def __iter__(self):
        for i in range(len(self)):
            yield self[i]

    def __repr__(self) -> str:
        return f"self.__class__.__name__(bboxes={self.bboxes}, masks={self.masks})"

    def get_bg_mask(self, dilate: bool = True) -> np.ndarray:
        """返回背景掩膜.

        Args:
            dilate (bool, 可选): 是否对掩膜进行膨胀。默认为True.

        Returns:
            np.ndarray: 背景掩膜.
        """
        img_h, img_w = self.image.shape[:2]
        bg_mask = np.ones((img_h, img_w), dtype=np.uint8)
        for mask in self.masks:
            if dilate:
                mask = cv2.dilate(mask, np.ones((7, 7), np.uint8), iterations=1)
            bg_mask = np.bitwise_and(bg_mask, np.bitwise_not(mask.astype(np.uint8)))
        return bg_mask

    def get_segments(self) -> list[np.ndarray]:
        """返回一个包含numpy数组的列表,其中每个数组表示掩模中一个片段的轮廓.

        Returns:
            List[np.ndarray]: 一个包含numpy数组的列表,其中每个数组表示掩模中一个片段的轮廓.
        """
        segments = []
        for x in self.masks.astype("uint8"):
            c = cv2.findContours(x, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_NONE)[0]  # CHAIN_APPROX_SIMPLE
            c = np.array(c[np.array([len(x) for x in c]).argmax()]).reshape(-1, 2) if c else np.zeros((0, 2))
            segments.append(c.astype("float32"))
        return segments

    def draw(self, img: np.ndarray | None = None, save_path: str | None = None) -> np.ndarray:
        """绘制结果.

        Args:
            img (np.ndarray, 可选): 图像.
            save_path (str, 可选): 保存路径.

        Returns:
            np.ndarray: 绘制结果的图像.
        """
        img = img if img is not None else self.image
        mask = img.copy()

        alpha = 0.5  # 设置 alpha 值为 0.5，即半透明效果
        draw_thickness = int(min(img.shape[:2]) // 320)

        for box, segment in zip(self.bboxes, self.segments):
            color = COLORS[int(box[5]) % len(COLORS)]

            cv2.polylines(img, np.int32([segment]), True, (255, 255, 255), draw_thickness)  # 白色边框
            cv2.fillPoly(mask, np.int32([segment]), color)  # 在空白图像上进行填充

            x1, y1, x2, y2 = map(int, box[:4])
            cv2.rectangle(img, (x1, y1), (x2, y2), color, draw_thickness)  # 边界框

        img = cv2.addWeighted(img, 1 - alpha, mask, alpha, 0)  # 将填充的区域与原始图像进行混合

        if save_path:
            cv2.imwrite(save_path, cv2.cvtColor(img, cv2.COLOR_RGB2BGR))

        return img

    def save_datasets(self, save_path: str, file_name: str) -> None:
        """保存数据集.

        Args:
            save_path (str): 数据集目录.
            file_name (str): 文件名.
        """
        datasets_dir = Path(save_path)

        (datasets_dir / "images").mkdir(parents=True, exist_ok=True)
        (datasets_dir / "labels").mkdir(parents=True, exist_ok=True)

        # 图像保存
        cv2.imwrite(str(datasets_dir / "images" / f"{file_name}.jpg"), self.image)

        # 标签保存
        img_h, img_w = self.image.shape[:2]
        with Path(datasets_dir / "labels" / f"{file_name}.txt").open("w") as f:
            for box, segment in zip(self.bboxes, self.segments):
                class_id = int(box[5])
                segment = cv2.approxPolyDP(segment, 2, closed=True)

                # 将segment reshape为(x, y)的形状
                points = segment.reshape(-1, 2)

                # 归一化处理
                points[:, 0] = points[:, 0] / img_w  # x坐标除以图像宽度
                points[:, 1] = points[:, 1] / img_h  # y坐标除以图像高度

                # 拉平
                points = points.flatten().tolist()

                f.write(f"{class_id} {' '.join(map(str, points))}\n")
