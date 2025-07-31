"""可视化工具模块.

该模块提供了一些可视化工具函数，用于在图像上绘制检测框、OCR结果等.

Example:
    >>> from xdeploy.utils.visualize import draw_detection, draw_ocr
    >>> from xdeploy.ocr import PPOCRv4
    >>> ocr = PPOCRv4(
    >>>     det_model_path="ocr/ppocr/DB/db_res18.onnx",
    >>>     rec_model_path="ocr/ppocr/CRNN/crnn.onnx",
    >>>     rec_character_path="ocr/ppocr/CRNN/ppocr_keys_v1.txt",
    >>>     device="CPU",
    >>> )
    >>> result = ocr.predict("test.jpg")
    >>> draw_ocr("test.jpg", result.rec_boxes, result.rec_txts, save_path="test_rec.jpg")
"""

from __future__ import annotations

import math
from pathlib import Path

import cv2
import numpy as np
from PIL import Image, ImageDraw, ImageFont


def load_font(
    font_path: str = "SmileySans-Oblique.ttf", font_size: int = 20
) -> ImageFont.FreeTypeFont | ImageFont.ImageFont:
    """加载字体文件,如果指定字体不存在则使用默认字体.

    Args:
        font_path (str): 字体文件路径
        font_size (int): 字体大小

    Returns:
        ImageFont.FreeTypeFont: 加载的字体对象
    """
    try:
        return ImageFont.truetype(font_path, font_size)
    except OSError:
        font_url = "https://github.com/atelier-anchor/smiley-sans/releases/download/v2.0.1/smiley-sans-v2.0.1.zip"
        print("=" * 32, "Warning", "=" * 32)
        print(f"{font_path} 未找到,已使用默认字体替代.如有乱码,请下载并安装字体:")
        print(f"  sudo wget -O /usr/share/fonts/truetype/{font_path} {font_url}")
        print("  sudo fc-cache -fv")
        print("=" * 73)
        return ImageFont.load_default()


DEFOULT_FONT = load_font()


class Colors:
    """Ultralytics default color palette https://ultralytics.com/.

    This class provides methods to work with the Ultralytics color palette, including converting hex color codes to
    RGB values.

    Attributes:
        palette (list of tuple): List of RGB color values.
        n (int): The number of colors in the palette.
        pose_palette (np.ndarray): A specific color palette array with dtype np.uint8.
    """

    def __init__(self):
        """Initialize colors as hex = matplotlib.colors.TABLEAU_COLORS.values()."""
        hexs = (
            "FF3838",
            "FF9D97",
            "FF701F",
            "FFB21D",
            "CFD231",
            "48F90A",
            "92CC17",
            "3DDB86",
            "1A9334",
            "00D4BB",
            "2C99A8",
            "00C2FF",
            "344593",
            "6473FF",
            "0018EC",
            "8438FF",
            "520085",
            "CB38FF",
            "FF95C8",
            "FF37C7",
        )
        self.palette = [self.hex2rgb(f"#{c}") for c in hexs]
        self.n = len(self.palette)
        self.pose_palette = np.array(
            [
                [255, 128, 0],
                [255, 153, 51],
                [255, 178, 102],
                [230, 230, 0],
                [255, 153, 255],
                [153, 204, 255],
                [255, 102, 255],
                [255, 51, 255],
                [102, 178, 255],
                [51, 153, 255],
                [255, 153, 153],
                [255, 102, 102],
                [255, 51, 51],
                [153, 255, 153],
                [102, 255, 102],
                [51, 255, 51],
                [0, 255, 0],
                [0, 0, 255],
                [255, 0, 0],
                [255, 255, 255],
            ],
            dtype=np.uint8,
        )

    def __getitem__(self, i) -> tuple[int, int, int]:
        return self.__call__(i)

    def __len__(self) -> int:
        return self.n

    def __call__(self, i, bgr=False) -> tuple[int, int, int]:
        """Converts hex color codes to RGB values."""
        c = self.palette[int(i) % self.n]
        return (c[2], c[1], c[0]) if bgr else c

    @staticmethod
    def hex2rgb(h):
        """Converts hex color codes to RGB values (i.e. default PIL order)."""
        return tuple(int(h[1 + i : 1 + i + 2], 16) for i in (0, 2, 4))


COLORS = Colors()  # create instance for 'from utils.plots import colors'


def draw_detection(
    im: Image.Image | np.ndarray | str,
    boxes: np.ndarray,
    names: list[str] | None = None,
    class_ids: list[int] | None = None,
    scores: list[float] | None = None,
    colors: list[tuple[int, int, int]] | None = None,
    save_path: str | None = None,
) -> np.ndarray:
    """在图像上绘制检测框并返回修改后的图像.

    Args:
        im (Image.Image | np.ndarray | str): 输入图像,可以是PIL Image对象、RGB格式Numpy数组或文件路径.
        boxes (np.ndarray): 检测到的物体的边界框坐标数组,格式为xyxy.
        names (List[str], 可选): 检测到的物体的名称列表.不填将不显示类别名称.
        class_ids (np.ndarray): 检测到的物体的类别ID数组.
        scores (np.ndarray, 可选): 检测到的物体的置信度分数数组.不填将不显示检测得分.
        colors (List[Tuple[int]], 可选): 用于绘制检测框的RGB颜色元组列表.默认选择自带的颜色列表.
        save_path (str, 可选): 保存修改后的图像的文件路径.默认为None.

    Returns:
        np.ndarray: 在上面绘制了检测框的修改后的图像.
    """
    # 加载图像
    if isinstance(im, str):
        im = Image.open(im)
    elif isinstance(im, np.ndarray):
        im = Image.fromarray(im.astype(np.uint8))

    # 绘制
    colors = colors or COLORS  # type: ignore

    draw = ImageDraw.Draw(im)
    draw_thickness = max(1, min(im.size) // 320)

    for i, box in enumerate(boxes):
        color = colors[class_ids[i] % len(colors)]  # type: ignore
        draw.rectangle(box.tolist(), outline=color, width=draw_thickness)

        text = names[i] if names else ""
        text = f"{text} {scores[i]:.2f}" if scores else text
        if text:
            tbox = draw.textbbox((box[0] + draw_thickness, box[1] - draw_thickness), text, font=DEFOULT_FONT)
            draw.rectangle(tbox, fill=color, width=draw_thickness)
            draw.text((box[0] + draw_thickness, box[1] - draw_thickness), text, fill=(255, 255, 255), font=DEFOULT_FONT)

    # 保存
    if save_path and not Path(save_path).parent.exists():
        Path(save_path).parent.mkdir(parents=True)

    if save_path:
        im.save(save_path)

    return np.array(im)


def draw_obb(
    im: Image.Image | np.ndarray | str,
    rboxes: np.ndarray,
    class_ids: np.ndarray,
    scores: np.ndarray | None = None,
    colors: list[tuple[int, int, int]] | None = None,
    save_path: str | None = None,
) -> np.ndarray:
    """在图像上绘制边界框，并可选择保存图像的函数.

    Args:
        im (Union[Image.Image, np.ndarray, str]): 输入图像, 可以是PIL Image对象、NumPy数组或文件路径.
        rboxes (np.ndarray): 检测到的旋转边界框数组.
        class_ids (np.ndarray): 检测到的物体的类别ID数组.
        scores (Optional[np.ndarray], 可选): 检测到的物体的置信度分数数组.默认为None.
        colors (Optional[List[Tuple[int, int, int]]], 可选): 用于绘制边界框的RGB颜色元组列表.默认为None.
        save_path (Optional[str], 可选): 保存带有边界框绘制的图像的文件路径.默认为None.

    Returns:
        np.ndarray: 绘制了边界框的图像.
    """
    if isinstance(im, str):
        im = cv2.imread(im)
    elif isinstance(im, Image.Image):
        im = cv2.cvtColor(np.array(im), cv2.COLOR_RGB2BGR)
    elif isinstance(im, np.ndarray):
        im = cv2.cvtColor(im, cv2.COLOR_RGB2BGR)

    mask = np.zeros_like(im)
    colors = colors or COLORS  # type: ignore

    draw_thickness = max(1, min(im.shape[:2]) // 320)

    for i, box in enumerate(rboxes):
        color = colors[class_ids[i] % len(colors)]  # type: ignore
        points = box.points().astype(int)  # 假设rbox有一个points()方法返回顶点坐标

        cv2.polylines(im, [points], isClosed=True, color=color, thickness=draw_thickness)
        cv2.fillPoly(mask, [points], color=color)

        text = f"{class_ids[i]} {scores[i]:.2f}" if scores is not None else None
        if text:
            tbox = cv2.getTextSize(text, cv2.FONT_HERSHEY_SIMPLEX, 0.5, 1)[0]
            cv2.rectangle(
                im, (points[0][0], points[0][1] - tbox[1] - 1), (points[0][0] + tbox[0], points[0][1] - 1), color, -1
            )
            cv2.putText(im, text, (points[0][0], points[0][1] - 1), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 255, 255), 1)

    im = cv2.addWeighted(im, 0.9, mask, 0.1, 0)

    # 保存
    if save_path and not Path(save_path).parent.exists():
        Path(save_path).parent.mkdir(parents=True)

    if save_path:
        cv2.imwrite(save_path, im)

    return im


def draw_ocr(
    im: Image.Image | np.ndarray | str,
    boxes: np.ndarray,
    txts: list[str],
    save_path: str | None = None,
) -> np.ndarray:
    """在图像上绘制OCR结果并返回修改后的图像.

    Args:
        im (Union[Image.Image, np.ndarray, str]): 输入图像,可以是PIL Image对象、NumPy数组或文件路径.
        boxes (np.ndarray): 检测到的文本的边界框坐标数组,格式为xyxy.
        txts (list[str]): 检测到的文本列表.
        save_path (str, 可选): 保存修改后的图像的文件路径.默认为None.

    Returns:
        np.ndarray: 在上面绘制了OCR结果的修改后的图像.
    """
    # 加载图像
    if isinstance(im, str):
        im = Image.open(im)
    elif isinstance(im, np.ndarray):
        im = Image.fromarray(im.astype(np.uint8))

    w, h = im.size
    img_left = im.copy()
    img_right = Image.new("RGB", (w, h), (255, 255, 255))

    draw_left = ImageDraw.Draw(img_left)
    draw_right = ImageDraw.Draw(img_right)
    FONT = load_font(font_size=max(int(min(h, w) * 0.05), 20))
    for box, txt in zip(boxes, txts, strict=False):
        draw_left.polygon(box, fill=COLORS[0])
        draw_right.polygon([coord for point in box for coord in point], outline=COLORS[0])
        box_height = math.sqrt((box[0][0] - box[3][0]) ** 2 + (box[0][1] - box[3][1]) ** 2)
        box_width = math.sqrt((box[0][0] - box[1][0]) ** 2 + (box[0][1] - box[1][1]) ** 2)
        if box_height > 2 * box_width:
            cur_y = box[0][1]
            for c in txt:
                char_size = FONT.getsize(c)  # type: ignore
                draw_right.text((box[0][0] + 3, cur_y), c, fill=(0, 0, 0), font=FONT)
                cur_y += char_size[1]
        else:
            draw_right.text(box[0], txt, fill=(0, 0, 0), font=FONT)
    img_left = Image.blend(im, img_left, 0.5)
    img_show = Image.new("RGB", (w * 2, h), (255, 255, 255))
    img_show.paste(img_left, (0, 0, w, h))
    img_show.paste(img_right, (w, 0, w * 2, h))

    # 保存
    if save_path and not Path(save_path).parent.exists():
        Path(save_path).parent.mkdir(parents=True)
    if save_path:
        img_show.save(save_path)
    return np.array(img_show)
