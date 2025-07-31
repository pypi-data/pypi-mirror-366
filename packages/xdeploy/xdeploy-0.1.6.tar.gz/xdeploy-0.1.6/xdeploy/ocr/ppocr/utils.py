from __future__ import annotations

import cv2
import numpy as np
import pyclipper
from shapely.geometry import Polygon


class DetPreProcess:
    def __init__(self, limit_side_len: int = 736, limit_type: str = "min"):
        """初始化文本检测器的默认预处理操作.

        Args:
            limit_side_len (int): 预处理后图像的目标尺寸
            limit_type (str): 处理类型，'min' 或 'max'
        """
        self.mean = np.array([0.485, 0.456, 0.406])
        self.std = np.array([0.229, 0.224, 0.225])
        self.scale = 1 / 255.0

        self.limit_side_len = limit_side_len
        self.limit_type = limit_type

    def __call__(self, img: np.ndarray) -> np.ndarray | None:
        """调整图像大小并进行标准化，保持长宽比不变."""
        resized_img = self.resize(img)
        if resized_img is None:
            return None

        img = self.normalize(resized_img)
        img = self.permute(img)
        img = np.expand_dims(img, axis=0).astype(np.float32)
        return img

    def normalize(self, img: np.ndarray) -> np.ndarray:
        """使用均值和标准差对图像进行标准化."""
        return (img.astype("float32") * self.scale - self.mean) / self.std

    def permute(self, img: np.ndarray) -> np.ndarray:
        """转置图像通道."""
        return img.transpose((2, 0, 1))

    def resize(self, img: np.ndarray) -> np.ndarray | None:
        """将图像调整为 32 的倍数大小，这是网络所要求的."""
        h, w = img.shape[:2]

        if self.limit_type == "max":
            if max(h, w) > self.limit_side_len:
                ratio = float(self.limit_side_len) / h if h > w else float(self.limit_side_len) / w
            else:
                ratio = 1.0
        else:
            if min(h, w) < self.limit_side_len:
                ratio = float(self.limit_side_len) / h if h < w else float(self.limit_side_len) / w
            else:
                ratio = 1.0

        resize_h = int(h * ratio)
        resize_w = int(w * ratio)

        resize_h = int(round(resize_h / 32) * 32)
        resize_w = int(round(resize_w / 32) * 32)

        try:
            if int(resize_w) <= 0 or int(resize_h) <= 0:
                return None
            img = cv2.resize(img, (int(resize_w), int(resize_h)))
        except Exception as exc:
            raise ResizeImgError from exc

        return img


class ResizeImgError(Exception):
    pass


class DBPostProcess:
    """Differentiable Binarization (DB) 的后处理."""

    def __init__(
        self,
        thresh: float = 0.3,
        box_thresh: float = 0.7,
        max_candidates: int = 1000,
        unclip_ratio: float = 2.0,
        score_mode: str = "fast",
        use_dilation: bool = False,
    ):
        """初始化 DB 后处理.

        Args:
            thresh (float): 预测得分阈值
            box_thresh (float): 边界框得分阈值
            max_candidates (int): 最大候选框数
            unclip_ratio (float): unclip 的比例
            score_mode (str): 'fast' 或 'slow'，选择使用快速模型还是慢速模型
            use_dilation (bool): 是否使用膨胀
        """
        self.thresh = thresh
        self.box_thresh = box_thresh
        self.max_candidates = max_candidates
        self.unclip_ratio = unclip_ratio
        self.min_size = 3
        self.score_mode = score_mode

        self.dilation_kernel = None
        if use_dilation:
            self.dilation_kernel = np.array([[1, 1], [1, 1]])

    def __call__(self, pred: np.ndarray, ori_shape: tuple[int, int]) -> tuple[np.ndarray, list[float]]:
        """将 DB 预测结果转换为边界框.

        Args:
            pred (np.ndarray): DB 预测结果.
            ori_shape (tuple[int, int]): 原始图像形状.

        Returns:
            tuple[np.ndarray, list[float]]: (边界框, 得分)
        """
        src_h, src_w = ori_shape
        pred = pred[:, 0, :, :]
        segmentation = pred > self.thresh

        mask = segmentation[0]
        if self.dilation_kernel is not None:
            mask = cv2.dilate(np.array(segmentation[0]).astype(np.uint8), self.dilation_kernel)
        boxes, scores = self.boxes_from_bitmap(pred[0], mask, src_w, src_h)
        return boxes, scores

    def boxes_from_bitmap(
        self, pred: np.ndarray, bitmap: np.ndarray, dest_width: int, dest_height: int
    ) -> tuple[np.ndarray, list[float]]:
        """从位图中提取边界框.

        Args:
            pred (np.ndarray): 预测结果.
            bitmap (np.ndarray): 位图,形状为(1, H, W),值为 0 或 1.
            dest_width (int): 目标宽度.
            dest_height (int): 目标高度.

        Returns:
            tuple[np.ndarray, List[float]]: (边界框, 得分)
        """
        height, width = bitmap.shape

        outs = cv2.findContours((bitmap * 255).astype(np.uint8), cv2.RETR_LIST, cv2.CHAIN_APPROX_SIMPLE)
        if len(outs) == 3:
            _img, contours, _ = outs[0], outs[1], outs[2]
        elif len(outs) == 2:
            contours, _ = outs[0], outs[1]

        num_contours = min(len(contours), self.max_candidates)

        boxes, scores = [], []
        for index in range(num_contours):
            contour = contours[index]
            points, sside = self.get_mini_boxes(contour)
            if sside < self.min_size:
                continue

            if self.score_mode == "fast":
                score = self.box_score_fast(pred, points.reshape(-1, 2))
            else:
                score = self.box_score_slow(pred, contour)

            if self.box_thresh > score:
                continue

            box = self.unclip(points)
            box, sside = self.get_mini_boxes(box)
            if sside < self.min_size + 2:
                continue

            box[:, 0] = np.clip(np.round(box[:, 0] / width * dest_width), 0, dest_width)
            box[:, 1] = np.clip(np.round(box[:, 1] / height * dest_height), 0, dest_height)
            boxes.append(box.astype(np.int32))
            scores.append(score)
        return np.array(boxes, dtype=np.int32), scores

    def get_mini_boxes(self, contour: np.ndarray) -> tuple[np.ndarray, float]:
        """获取轮廓的最小外接矩形.

        Args:
            contour (np.ndarray): 轮廓点.

        Returns:
            tuple[np.ndarray, float]: 最小外接矩形和其边长.
        """
        bounding_box = cv2.minAreaRect(contour)
        points = sorted(list(cv2.boxPoints(bounding_box)), key=lambda x: x[0])

        index_1, index_2, index_3, index_4 = 0, 1, 2, 3
        if points[1][1] > points[0][1]:
            index_1 = 0
            index_4 = 1
        else:
            index_1 = 1
            index_4 = 0

        if points[3][1] > points[2][1]:
            index_2 = 2
            index_3 = 3
        else:
            index_2 = 3
            index_3 = 2

        box = np.array([points[index_1], points[index_2], points[index_3], points[index_4]])
        return box, min(bounding_box[1])

    @staticmethod
    def box_score_fast(bitmap: np.ndarray, _box: np.ndarray) -> float:
        """计算位图中一个框的平均得分（快速版本）.

        Args:
            bitmap (np.ndarray): 输入位图.
            _box (np.ndarray): 框.

        Returns:
            float: 平均得分.
        """
        h, w = bitmap.shape[:2]
        box = _box.copy()
        xmin = np.clip(np.floor(box[:, 0].min()).astype(np.int32), 0, w - 1)
        xmax = np.clip(np.ceil(box[:, 0].max()).astype(np.int32), 0, w - 1)
        ymin = np.clip(np.floor(box[:, 1].min()).astype(np.int32), 0, h - 1)
        ymax = np.clip(np.ceil(box[:, 1].max()).astype(np.int32), 0, h - 1)

        mask = np.zeros((ymax - ymin + 1, xmax - xmin + 1), dtype=np.uint8)
        box[:, 0] = box[:, 0] - xmin
        box[:, 1] = box[:, 1] - ymin
        cv2.fillPoly(mask, box.reshape(1, -1, 2).astype(np.int32), 1)
        return cv2.mean(bitmap[ymin : ymax + 1, xmin : xmax + 1], mask)[0]

    def box_score_slow(self, bitmap: np.ndarray, contour: np.ndarray) -> float:
        """使用多边形平均得分作为平均得分（慢速版本）."""
        h, w = bitmap.shape[:2]
        contour = contour.copy()
        contour = np.reshape(contour, (-1, 2))

        xmin = np.clip(np.min(contour[:, 0]), 0, w - 1)
        xmax = np.clip(np.max(contour[:, 0]), 0, w - 1)
        ymin = np.clip(np.min(contour[:, 1]), 0, h - 1)
        ymax = np.clip(np.max(contour[:, 1]), 0, h - 1)

        mask = np.zeros((ymax - ymin + 1, xmax - xmin + 1), dtype=np.uint8)

        contour[:, 0] = contour[:, 0] - xmin
        contour[:, 1] = contour[:, 1] - ymin

        cv2.fillPoly(mask, contour.reshape(1, -1, 2).astype(np.int32), 1)
        return cv2.mean(bitmap[ymin : ymax + 1, xmin : xmax + 1], mask)[0]

    def unclip(self, box: np.ndarray) -> np.ndarray:
        """根据 unclip 比率展开框.

        Args:
            box (np.ndarray): 输入框.

        Returns:
            np.ndarray: 展开后的框.
        """
        unclip_ratio = self.unclip_ratio
        poly = Polygon(box)
        distance = poly.area * unclip_ratio / poly.length
        offset = pyclipper.PyclipperOffset()
        offset.AddPath(box, pyclipper.JT_ROUND, pyclipper.ET_CLOSEDPOLYGON)
        expanded = np.array(offset.Execute(distance)).reshape((-1, 1, 2))
        return expanded
