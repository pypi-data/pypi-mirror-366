"""文本识别模型."""

from __future__ import annotations

import re
from pathlib import Path

import cv2
import numpy as np

from xdeploy.base import Backend

CHARACTER = Path(__file__).resolve().parent / "ppocr_keys_v1.txt"


class TextRecognizer(Backend):
    """文本识别模型.

    Args:
        model_path (str): 模型路径.
        character_path (str, 可选): 字符集路径.默认为 None.
        device (str, 可选): 设备类型.默认为 "CPU".

    Functions:
        preprocess (image: Union[List, np.ndarray], std: tuple = (0.5,), mean: tuple = (0.5,)) -> np.ndarray: 预处理图像或图像列表.
        predict (image: Union[List, np.ndarray]) -> np.ndarray: 进行推理.
    """

    def __init__(
        self,
        model_path: str,
        character_path: str | None = None,
        use_space_char: bool = True,
        device="CPU",
    ):
        """初始化."""
        super().__init__(model_path=model_path, device=device)

        input_info = self.inputs_info[0]

        self.input_name = input_info.name
        self.input_shape = [-1, 3, 48, 320]
        self.input_type = input_info.dtype

        self.postprocess_op = CTCLabelDecode(character_path or CHARACTER, use_space_char=use_space_char)

    def predict(self, image: list | np.ndarray) -> list[tuple[str, float]]:
        """进行推理."""
        blob = self.preprocess(image)
        outputs = self.forward({self.input_name: blob})
        # 解析文字
        rec_result = self.postprocess_op(outputs)
        return rec_result

    def preprocess(self, image: list | np.ndarray, std: tuple = (0.5,), mean: tuple = (0.5,)) -> np.ndarray:
        """预处理图像或图像列表.

        参数:
            image (List | np.ndarray): 需要进行预处理的图像或图像列表.
            std (tuple, 可选): 标准差用于归一化.默认为 (0.5,).
            mean (tuple, 可选): 均值用于归一化.默认为 (0.5,).

        返回:
            np.ndarray: 预处理后的图像作为一个 NumPy 数组.
        """
        if isinstance(image, np.ndarray):
            image = [image]

        batch_size = len(image)
        h, w = self.input_shape[2], self.input_shape[3]
        ims = np.zeros((batch_size, h, w, 3), dtype=self.input_type)

        for i, im_ in enumerate(image):
            im, _ = self._preprocess_image(im_, (h, w), pad_color=(0, 0, 0))
            ims[i] = im

        ims = np.transpose(ims, (0, 3, 1, 2)).astype(self.input_type)
        return ims

    def _preprocess_image(
        self, img: np.ndarray, target_shape: tuple[int, int], pad_color: tuple[int, int, int]
    ) -> tuple[np.ndarray, float]:
        """预处理图像：调整大小，保持宽高比，归一化，并填充到目标形状.

        Args:
            img (np.ndarray): 输入图像.
            target_shape (Tuple[int, int, int]): 目标形状 [通道数，高度，宽度].
            pad_color (tuple[int, int, int]): 填充颜色.

        Returns:
            Tuple[np.ndarray, float]: 预处理后的图像和有效比例.
        """
        target_h, target_w = target_shape
        max_wh_ratio = min(target_w / target_h, img.shape[1] / img.shape[0])

        # 计算调整大小后的宽度
        resized_w = min(target_w, int(target_h * max_wh_ratio))
        resized_h = target_h

        # 调整图像大小
        resized_img = cv2.resize(img, (resized_w, resized_h), interpolation=cv2.INTER_LINEAR)
        resized_img = resized_img.astype(self.input_type)
        resized_img /= 255.0
        resized_img -= 0.5
        resized_img /= 0.5

        # 创建填充后的图像
        padded_img = np.zeros((target_h, target_w, 3), dtype=self.input_type)
        padded_img[:resized_h, :resized_w] = resized_img

        # 计算有效比例
        valid_ratio = min(1.0, resized_w / target_w)

        return padded_img, valid_ratio


class CTCLabelDecode:
    """文本识别结果反序列化."""

    def __init__(self, character_dict_path=None, use_space_char=False, ignored_tokens=None):
        """初始化.

        Args:
            character_dict_path (str): 字符字典路径.
            use_space_char (bool): 是否使用空格作为分隔符.
            ignored_tokens (list): 被忽略的字符索引.
        """
        self.reverse = False
        self.ignored_tokens = ignored_tokens or [0]

        character_str = []

        if character_dict_path is None:
            character_str = "0123456789abcdefghijklmnopqrstuvwxyz"
        else:
            with Path(character_dict_path).open("rb") as fin:
                character_str = [line.decode("utf-8").strip() for line in fin]
            if use_space_char:
                character_str.append(" ")
            if "arabic" in str(character_dict_path):
                self.reverse = True

        character_str = self.add_special_char(character_str)
        self.character = character_str

    def __call__(self, preds: np.ndarray, label=None) -> list[tuple[str, float]]:
        """预测结果反序列化."""
        preds_idx = preds.argmax(axis=2)
        preds_prob = preds.max(axis=2)
        text = self.decode(preds_idx, preds_prob, is_remove_duplicate=True)
        if label is None:
            return text
        label = self.decode(label)
        return text, label

    def get_ignored_tokens(self):
        """获取被忽略的字符索引."""
        return self.ignored_tokens

    def pred_reverse(self, pred):
        """预测结果反转."""
        pred_re = []
        c_current = ""
        for c in pred:
            if not bool(re.search("[a-zA-Z0-9 :*./%+-]", c)):
                if c_current != "":
                    pred_re.append(c_current)
                pred_re.append(c)
                c_current = ""
            else:
                c_current += c
        if c_current != "":
            pred_re.append(c_current)

        return "".join(pred_re[::-1])

    def decode(
        self,
        text_index: np.ndarray,
        text_prob: np.ndarray | None = None,
        is_remove_duplicate: bool = False,
    ) -> list[tuple[str, float]]:
        """将文本索引转换为文本."""
        result_list = []
        ignored_tokens = self.get_ignored_tokens()
        batch_size = len(text_index)
        for batch_idx in range(batch_size):
            selection = np.ones(len(text_index[batch_idx]), dtype=bool)
            if is_remove_duplicate:
                selection[1:] = text_index[batch_idx][1:] != text_index[batch_idx][:-1]
            for ignored_token in ignored_tokens:
                selection &= text_index[batch_idx] != ignored_token

            char_list = [self.character[text_id] for text_id in text_index[batch_idx][selection]]
            conf_list = text_prob[batch_idx][selection] if text_prob is not None else [1] * len(selection)
            if len(conf_list) == 0:
                conf_list = [0]

            text = "".join(char_list)

            if self.reverse:  # for arabic rec
                text = self.pred_reverse(text)

            result_list.append((text, np.mean(conf_list).tolist()))
        return result_list

    def add_special_char(self, dict_character):
        """添加空白字符."""
        dict_character = ["blank"] + dict_character
        return dict_character
