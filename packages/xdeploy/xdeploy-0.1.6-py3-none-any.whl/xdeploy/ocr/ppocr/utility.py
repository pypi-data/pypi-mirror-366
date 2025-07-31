"""Utility functions for xdeploy."""

from __future__ import annotations

import cv2
import numpy as np


def get_rotate_crop_image(img: np.ndarray, points: np.ndarray) -> np.ndarray:
    """根据指定的点裁剪并旋转图像.

    Args:
        img: 输入图像以NumPy数组的形式.
        points: 用于裁剪和旋转的点.形状为(N, 2),其中N是点的数量.

    Returns:
        裁剪并旋转后的图像以NumPy数组的形式.
    """
    assert len(points) == 4, "Shape of points must be 4x2"
    img_crop_width = int(max(np.linalg.norm(points[0] - points[1]), np.linalg.norm(points[2] - points[3])))
    img_crop_height = int(max(np.linalg.norm(points[0] - points[3]), np.linalg.norm(points[1] - points[2])))
    pts_std = np.float32([[0, 0], [img_crop_width, 0], [img_crop_width, img_crop_height], [0, img_crop_height]])
    M = cv2.getPerspectiveTransform(points, pts_std)
    dst_img = cv2.warpPerspective(
        img,
        M,
        (img_crop_width, img_crop_height),
        borderMode=cv2.BORDER_REPLICATE,
        flags=cv2.INTER_CUBIC,
    )
    dst_img_height, dst_img_width = dst_img.shape[:2]
    if dst_img_height * 1.0 / dst_img_width >= 1.5:
        dst_img = np.rot90(dst_img)
    return dst_img


def sorted_boxes(dt_boxes: np.ndarray) -> np.ndarray:
    """对给定数组中的框进行排序.

    Args:
        dt_boxes: 形状为(N, 4, 2)的numpy数组,表示N个框.

    Returns:
        形状为(N, 4, 2)的排序后的numpy数组,表示排序后的框.
    """
    # 计算每个框的中心点坐标
    center_points = np.mean(dt_boxes, axis=1)  # 形状为(N, 2)

    # 获取每个框中心点的x和y坐标
    x_coords = center_points[:, 0]
    y_coords = center_points[:, 1]

    # 先按y坐标升序排序，再按x坐标升序排序
    indices = np.lexsort((x_coords, y_coords))

    # 根据排序后的索引重新排列框
    sorted_boxes = dt_boxes[indices]

    return sorted_boxes
