"""PPOCRv4模型的推理类."""

from __future__ import annotations

import cv2
import numpy as np

from xdeploy.results import OCRResult

from .predict_det import TextDetector
from .predict_rec import TextRecognizer
from .utility import get_rotate_crop_image, sorted_boxes


class PPOCRv4:
    """PPOCRv4模型的推理类.

    Args:
        det_model_path (str): 检测模型文件的路径.
        rec_model_path (str): 识别模型文件的路径.
        rec_character_path (str, 可选): 识别模型的字符集文件的路径.默认为None.
        cls_model_path (str, 可选): 分类模型文件的路径.默认为None.
        use_angle_cls (bool, 可选): 是否使用分类模型进行角度分类.默认为False.
        device (str, 可选): 推理使用的设备.默认为"CPU",可选"CPU、GPU".
    """

    def __init__(
        self,
        det_model_path: str,
        rec_model_path: str,
        rec_character_path: str | None = None,
        cls_model_path: str | None = None,
        use_angle_cls: bool = False,
        device: str = "CPU",
    ):
        """初始化.

        Args:
            det_model_path (str): 检测模型文件的路径.
            rec_model_path (str): 识别模型文件的路径.
            rec_character_path (str, 可选): 识别模型的字符集文件的路径.默认为None.
            cls_model_path (str, 可选): 分类模型文件的路径.默认为None.
            use_angle_cls (bool, 可选): 是否使用分类模型进行角度分类.默认为False.
            device (str, 可选): 推理使用的设备.默认为"CPU",可选"CPU、GPU".
        """
        self.det_net = TextDetector(det_model_path, device)
        self.rec_net = TextRecognizer(rec_model_path, rec_character_path, device=device)
        self.drop_score = 0.25

        self.crop_image_res_index = 0

    def predict(self, image: str | np.ndarray) -> OCRResult:
        """进行推理.

        Args:
            image (Union[str, np.ndarray]): 需要进行推理的输入图像,可以是文件路径或者numpy数组.

        Returns:
            OCRResult: 返回OCR结果.
        """
        filter_boxes = []
        filter_rec_txts = []

        image = image if isinstance(image, np.ndarray) else cv2.imread(image)
        ori_im = image.copy()
        ori_im = cv2.cvtColor(ori_im, cv2.COLOR_BGR2RGB)
        det_boxes = self.det_net.predict(image)

        if det_boxes is None:
            return OCRResult(ori_im, filter_boxes, filter_rec_txts)

        if len(det_boxes):
            det_boxes = sorted_boxes(det_boxes)
            img_crop_list = [get_rotate_crop_image(image, box) for box in det_boxes]
            rec_res = self.rec_net.predict(img_crop_list)

            for box, rec_result in zip(det_boxes, rec_res):
                if rec_result[1] >= self.drop_score:
                    filter_boxes.append(box)
                    filter_rec_txts.append(rec_result[0])

        return OCRResult(ori_im, filter_boxes, filter_rec_txts)
