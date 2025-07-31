from __future__ import annotations

import cv2
import numpy as np

from xdeploy.base import YOLO
from xdeploy.results import InstanceSegResult


class YOLOV8_SEG(YOLO[InstanceSegResult]):
    """分割模型,基于YOLOV8."""

    def __init__(
        self, model_path: str, score_threshold: float = 0.45, nms_threshold: float = 0.65, device: str = "CPU"
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

    def postprocess(self, batch_image: list[np.ndarray], batch_result: list[np.ndarray]) -> list[InstanceSegResult]:
        """对批量结果进行后处理.

        Args:
            batch_image (List[np.ndarray]): 原始图像,检测或结果可视化.
            batch_result (List[np.ndarray]): 需要进行后处理的批量结果，[batch_size, 300, [x,y,x,y,score,class_id]].

        Returns:
            List[InstanceSegResult]: 后处理后的批量结果.
        """
        results = []
        bboxes_results, seg_results = batch_result
        bboxes_results = np.einsum("bcn->bnc", bboxes_results)

        for i, im in enumerate(batch_image):
            bboxes = self._process_bboxes(bboxes_results[i], self.batch_scales[i], im.shape[:2], self.batch_paddings[i])
            masks = self._process_masks(bboxes, seg_results[i], im)
            results.append(InstanceSegResult(batch_image[i], bboxes, masks))

        return results

    def _process_bboxes(
        self,
        batch_bboxes: np.ndarray,
        scale: float,
        image_shape: tuple[int, int],
        padding: tuple[int, int, int, int],
        nm: int = 32,
    ) -> np.ndarray:
        """处理单张图像的边界框结果.

        Args:
            batch_bboxes (np.ndarray): 批量边界框.
            scale (float): 缩放比例.
            image_shape (Tuple[int, int]): 图像形状 h,w.
            padding (Tuple[int, int, int, int]): 边界
            nm (int, optional): mask 数.默认为 32.

        Returns:
            BBoxes: 处理后的边界框.
        """
        batch_bboxes = batch_bboxes[np.amax(batch_bboxes[..., 4:-nm], axis=-1) > self.score_threshold]

        if len(batch_bboxes) == 0:
            return np.array([])

        bboxes, classes_scores, mask_pres = np.split(batch_bboxes, [4, -nm], axis=1)
        class_ids = np.argmax(classes_scores, axis=1)
        scores = np.amax(classes_scores, axis=1)

        # NMS
        indices = cv2.dnn.NMSBoxesBatched(bboxes, scores, class_ids, self.score_threshold, self.nms_threshold)  # type: ignore

        if len(indices) == 0:
            return np.array([])

        bboxes = bboxes[indices]
        scores = scores[indices]
        class_ids = class_ids[indices]
        mask_pres = mask_pres[indices]

        # xywh -> xyxy
        bboxes[:, :2] -= bboxes[:, 2:] / 2
        bboxes[:, 2:] += bboxes[:, :2]

        # 修正边界框坐标
        bboxes -= padding
        bboxes /= scale
        bboxes[:, 0::2] = np.clip(bboxes[:, 0::2], 0, image_shape[1])
        bboxes[:, 1::2] = np.clip(bboxes[:, 1::2], 0, image_shape[0])

        return np.concatenate(
            [bboxes, np.expand_dims(scores, axis=1), np.expand_dims(class_ids, axis=1), mask_pres], axis=1
        )

    def _process_masks(self, bboxes: np.ndarray, batch_segment: np.ndarray, image: np.ndarray) -> np.ndarray:
        """处理单张图像的掩膜结果.

        Args:
            bboxes (np.ndarray): 边界框, 类似于 (x1, y1, x2, y2, score, class_id, mask_pres).
            batch_segment (np.ndarray): 批量分割掩膜.
            image (np.ndarray): 原始图像.

        Returns:
            Masks: 处理后的掩膜.
        """
        if len(bboxes) == 0:
            return np.array([])

        segment_num, segment_height, segment_width = batch_segment.shape
        im0_height, im0_width = image.shape[:2]

        segments = np.matmul(bboxes[:, 6:], batch_segment.reshape((segment_num, -1)))
        segments = segments.reshape((-1, segment_height, segment_width))
        segments = np.ascontiguousarray(segments)

        # 计算 padding
        gain = min(segment_height / im0_height, segment_width / im0_width)
        pad_w, pad_h = (
            int((segment_width - im0_width * gain) // 2),
            int((segment_height - im0_height * gain) // 2),
        )  # wh padding

        top, left, bottom, right = pad_h, pad_w, segment_height - pad_h, segment_width - pad_w
        segments = segments[:, top:bottom, left:right]

        mask_maps = np.zeros((len(bboxes), im0_height, im0_width), dtype=np.float32)
        blur_size = int(im0_width / segment_width), int(im0_height / segment_height)

        for i, (bbox, segment) in enumerate(zip(bboxes, segments)):
            x1, y1, x2, y2 = map(int, bbox[:4])
            segment_resized = cv2.resize(segment, (im0_width, im0_height), interpolation=cv2.INTER_LINEAR)
            segment_crop = segment_resized[y1:y2, x1:x2]
            segment_crop = cv2.blur(segment_crop, blur_size)
            segment_crop = (segment_crop > 0.5).astype(np.uint8)

            mask_maps[i, y1:y2, x1:x2] = segment_crop

        return mask_maps

    @staticmethod
    def mask_nms(masks: np.ndarray, scores: np.ndarray, threshold: float = 0.25) -> np.ndarray:
        """使用mask的非极大值抑制(NMS)过滤掉重叠过多的mask,并返回保留的mask索引.

        Args:
            masks (np.ndarray): 形状为 (N, H, W) 的掩膜数组,N 表示掩膜的数量,H 和 W 分别表示掩膜的高度和宽度.
            scores (np.ndarray): 形状为 (N,) 的分数数组,表示每个掩膜的分数.
            threshold (float): 重叠阈值,用于确定是否保留掩膜.

        Returns:
            np.ndarray: 保留的掩膜索引数组.
        """
        sorted_indices = np.argsort(scores)[::-1]
        keep = []

        while len(sorted_indices) > 0:
            max_index = sorted_indices[0]
            keep.append(max_index)
            overlap = np.sum(masks[max_index] * masks[sorted_indices[1:]], axis=(1, 2)) / np.sum(masks[max_index])
            sorted_indices = sorted_indices[1:][overlap <= threshold]

        return np.array(keep)
