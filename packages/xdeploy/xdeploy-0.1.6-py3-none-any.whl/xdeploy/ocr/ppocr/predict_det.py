"""文本检测模块."""

from __future__ import annotations

import cv2
import numpy as np

from xdeploy.base import Backend

from .utils import DBPostProcess, DetPreProcess


class TextDetector(Backend):
    """文本检测模型.

    Args:
        model_path (str): 模型文件的路径。
        device (str, 可选): 推理使用的设备。默认为"CPU"，可选"CPU、GPU"。
    """

    def __init__(self, model_path: str, device: str = "CPU") -> None:
        """初始化对象."""
        super().__init__(model_path=model_path, device=device)

        self.input_info = self.inputs_info[0]
        self.input_info.shape = [1, 3, 960, 960] or self.input_info.shape  # type: ignore # noqa: SIM222

        self.batch_size = self.input_info.shape[0]
        self.batch_scales = np.ones(self.batch_size)

        _input_name = self.input_info.name
        _input_data = np.zeros(self.input_info.shape, dtype=self.input_info.dtype)
        self.input_buffer = {_input_name: _input_data}

        self.preprocess_op = DetPreProcess(limit_side_len=960, limit_type="max")
        self.postprocess_op = DBPostProcess(
            thresh=0.3,
            box_thresh=0.5,
            max_candidates=1000,
            unclip_ratio=1.6,
            use_dilation=True,
            score_mode="fast",
        )

    def predict(self, img: str | np.ndarray) -> np.ndarray | None:
        """对图像进行预测.

        Args:
            img (Union[str, np.ndarray]): 需要进行预测的图像的路径或numpy数组

        Returns:
            np.ndarray: 预测结果.
        """
        if img is None:
            raise ValueError("img is None")

        img = img if isinstance(img, np.ndarray) else cv2.imread(img)[..., ::-1]

        ori_img_shape = img.shape[0], img.shape[1]
        prepro_img = self.preprocess_op(img)

        if prepro_img is None:
            return None

        input_buffer = {self.input_info.name: prepro_img}
        # self.input_buffer[self.input_info.name][0] = prepro_img
        preds = self.forward(input_buffer)

        dt_boxes, dt_boxes_scores = self.postprocess_op(preds, ori_img_shape)
        dt_boxes = self.filter_tag_det_res(dt_boxes, ori_img_shape)

        return dt_boxes

    def filter_tag_det_res(self, dt_boxes: np.ndarray, image_shape: tuple[int, int]) -> np.ndarray:
        """过滤文本框.

        Args:
            dt_boxes (np.ndarray): 文本框.
            image_shape (Tuple[int, int]): 图像形状.

        Returns:
            np.ndarray: 过滤后的文本框.
        """
        img_height, img_width = image_shape
        dt_boxes_new = []
        for box in dt_boxes:
            box = self.order_points_clockwise(box)
            box = self.clip_det_res(box, img_height, img_width)

            rect_width = int(np.linalg.norm(box[0] - box[1]))
            rect_height = int(np.linalg.norm(box[0] - box[3]))
            if rect_width <= 3 or rect_height <= 3:
                continue

            dt_boxes_new.append(box)
        return np.array(dt_boxes_new)

    def clip_det_res(self, points: np.ndarray, img_height: int, img_width: int) -> np.ndarray:
        """将检测结果的边界框裁剪到图像边界内.

        Args:
            points (np.ndarray): 检测结果的边界框,形状为(4, 2).
            img_height (int): 图像高度.
            img_width (int): 图像宽度.

        Returns:
            np.ndarray: 裁剪后的边界框.
        """
        for pno in range(points.shape[0]):
            points[pno, 0] = int(min(max(points[pno, 0], 0), img_width - 1))
            points[pno, 1] = int(min(max(points[pno, 1], 0), img_height - 1))
        return points

    def order_points_clockwise(self, pts: np.ndarray) -> np.ndarray:
        """对文本框的四个点进行排序.

        Args:
            pts (np.ndarray): 文本框的四个点.

        Returns:
            np.ndarray: 排序后的文本框的四个点.
        """
        rect = np.zeros((4, 2), dtype="float32")
        s = pts.sum(axis=1)
        rect[0] = pts[np.argmin(s)]
        rect[2] = pts[np.argmax(s)]
        tmp = np.delete(pts, (np.argmin(s), np.argmax(s)), axis=0)
        diff = np.diff(np.array(tmp), axis=1)
        rect[1] = tmp[np.argmin(diff)]
        rect[3] = tmp[np.argmax(diff)]
        return rect
