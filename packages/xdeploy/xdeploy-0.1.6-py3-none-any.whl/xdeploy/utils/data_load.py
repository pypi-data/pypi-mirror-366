"""数据加载相关的工具函数."""

from __future__ import annotations

import cv2
import numpy as np
from PIL import Image


def load_image(image: str | np.ndarray) -> np.ndarray:
    """加载图像并转换为RGB格式.

    Args:
        image (Union[str, np.ndarray]): 图像的文件路径或numpy数组.

    Returns:
        np.ndarray: 转换后的RGB图像.
    """
    if isinstance(image, str):
        image = cv2.imread(image)
        if image is None:
            raise ValueError(f"Image at path {image} could not be loaded.")
    elif isinstance(image, np.ndarray):
        if image.ndim == 2:  # 灰度图
            image = cv2.cvtColor(image, cv2.COLOR_GRAY2BGR)
    else:
        raise ValueError(f"Invalid image type: {type(image)}")

    return cv2.cvtColor(image, cv2.COLOR_BGR2RGB)


def letterbox(
    image: np.ndarray,
    new_shape: tuple[int, int],
    pad_color: tuple[int, int, int] = (114, 114, 114),
) -> tuple[np.ndarray, float, tuple[int, int]]:
    """将图像调整大小并填充到目标形状.

    Args:
        image (np.ndarray): 输入图像.
        new_shape (Tuple[int]): 要将图像调整为的目标形状.
        pad_color (Tuple[int], optional): 用于填充的颜色.默认为 (114, 114, 114).

    Returns:
        pad (np.ndarray): 填充和调整大小的图像，
        scale (float): 使用的缩放因子
        padding (Tuple[int, int]): 填充宽度和高度.
    """
    height, width = image.shape[:2]
    new_h, new_w = new_shape
    scale = min(new_w / width, new_h / height)
    unpad_w, unpad_h = int(width * scale), int(height * scale)
    pad_w, pad_h = (new_w - unpad_w) // 2, (new_h - unpad_h) // 2
    image = cv2.resize(image, (unpad_w, unpad_h), interpolation=cv2.INTER_LINEAR)
    pad_im = cv2.copyMakeBorder(image, pad_h, pad_h, pad_w, pad_w, cv2.BORDER_CONSTANT, value=pad_color)
    pad_im = cv2.resize(pad_im, (new_w, new_h), interpolation=cv2.INTER_LINEAR)
    return pad_im, scale, (pad_w, pad_h)


def normalize(
    image: np.ndarray,
    mean: tuple[float, float, float] = (0.5, 0.5, 0.5),
    std: tuple[float, float, float] = (0.5, 0.5, 0.5),
    dtype: np.dtype = np.dtype(np.float32),
) -> np.ndarray:
    """标准化图像.

    Args:
        image (np.ndarray): 输入图像.
        mean (Tuple[float, float, float], optional): 均值用于归一化.默认为 (0.5, 0.5, 0.5).
        std (Tuple[float, float, float], optional): 标准差用于归一化.默认为 (0.5, 0.5, 0.5).
        dtype (np.dtype, optional): 数据类型.默认为 np.dtype(np.float32).

    Returns:
        np.ndarray: 标准化后的图像.
    """
    image = image.astype(dtype)
    image -= mean
    image /= std
    image /= 255.0

    return image


def resize_pad(
    image: np.ndarray,
    resize_shape: tuple[int, int],
    pad: bool = True,
    pad_color: tuple[int, int, int] = (114, 114, 114),
) -> tuple[np.ndarray, float]:
    """将图像调整大小并填充到目标形状.

    Args:
        image (np.ndarray): 输入图像.
        resize_shape (tuple[int]): 要将图像调整为的目标形状.
        pad (bool, optional): 是否填充.默认为 True.
        pad_color (tuple[int], optional): 用于填充的颜色.默认为 (114, 114, 114).

    Returns:
        pad_im (Image.Image): 填充和调整大小的图像，
        scale (float): 使用的缩放因子.
    """
    height, width = image.shape[:2]
    height_scale = height / resize_shape[0]
    width_scale = width / resize_shape[1]
    scale = 1.0 / max(width_scale, height_scale)
    image = cv2.resize(image, (round(width * scale), round(height * scale)), interpolation=cv2.INTER_LINEAR)
    if not pad:
        return image, scale
    pad_im = np.zeros((resize_shape[0], resize_shape[1], 3), dtype=np.uint8)
    pad_im[:, :] = pad_color
    pad_im[: image.shape[0], : image.shape[1]] = image
    return pad_im, scale


def resize_pad_with_pil(
    image: Image.Image,
    resize_shape: tuple[int, int],
    pad_color: tuple[int, int, int] = (114, 114, 114),
) -> tuple[Image.Image, float]:
    """将图像调整大小并填充到目标形状.

    Args:
        image (Image.Image): 输入图像.
        resize_shape (tuple[int]): 要将图像调整为的目标形状.
        pad_color (tuple[int], optional): 用于填充的颜色.默认为 (114, 114, 114).

    Returns:
        pad (Image.Image): 填充和调整大小的图像，
        scale (float): 使用的缩放因子.
    """
    width, height = image.size
    height_scale = height / resize_shape[0]
    width_scale = width / resize_shape[1]
    scale = 1.0 / max(width_scale, height_scale)
    image = image.resize((round(width * scale), round(height * scale)), resample=Image.BILINEAR)
    pad = Image.new("RGB", resize_shape)
    pad.paste(pad_color, [0, 0, *resize_shape])  # type: ignore
    pad.paste(image)
    return pad, scale
