"""OCR 识别结果.

用于处理OCR识别结果

Example:
    >>> from xdeploy.results.ocr_result import OCRResult
    >>> ocr_result = OCRResult(orig_img, boxes, txts)
"""

from __future__ import annotations

import numpy as np

from xdeploy.utils.visualize import draw_ocr


class OCRResult:
    """OCR 识别结果.

    Args:
        orig_img (np.ndarray): 原始RGB格式图像.
        boxes (List): 检测边界框. 格式为xy点坐标.[[x,y],...].
        txts (List[str]): 检测文本.

    Attributes:
        orig_img (np.ndarray): 原始RGB格式图像.
        boxes (List): 检测边界框. 格式为xy点坐标.[[x,y],...].
        txts (List[str]): 检测文本.
    """

    def __init__(self, orig_img: np.ndarray, boxes: list | None = None, txts: list[str] | None = None) -> None:
        """初始化函数.

        Args:
            orig_img (np.ndarray): 原始RGB格式图像.
            boxes (Optional[List], 可选): 检测边界框.
            txts (Optional[List[str]], 可选): 检测文本.
        """
        self.orig_img = orig_img
        self.boxes: list = boxes or []
        self.txts: list[str] = txts or []

    def __repr__(self) -> str:
        return f"{self.__class__.__name__}(boxes={self.boxes}, txts={self.txts})"

    def __len__(self) -> int:
        return len(self.boxes)

    def __getitem__(self, index: int) -> tuple[np.ndarray, str]:
        return self.boxes[index], self.txts[index]

    def __iter__(self):
        for i in range(len(self)):
            yield self[i]

    def __bool__(self) -> bool:
        return len(self) > 0

    def to_dict(self) -> dict:
        """转换为字典.

        Returns:
            Dict: 检测结果字典.
        """
        return {"boxes": self.boxes, "txts": self.txts}

    def draw(self, save_path: str | None = None) -> np.ndarray:
        """绘制检测结果.

        Args:
            save_path (str, 可选): 保存绘制结果的文件路径.默认为 None.

        Returns:
            np.ndarray: 绘制了检测结果的图像.
        """
        if len(self) == 0 and save_path is None:
            return self.orig_img
        return draw_ocr(self.orig_img, self.boxes, self.txts, save_path)
