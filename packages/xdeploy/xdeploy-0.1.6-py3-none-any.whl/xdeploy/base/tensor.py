from __future__ import annotations

from dataclasses import dataclass

import numpy as np


@dataclass
class Tensor:
    """数据类.

    Attributes:
        name (str): 名称.
        dtype (np.dtype): 数据类型.
        shape (Tuple): 形状.
        cpu (np.ndarray): CPU数据.
    """

    name: str
    dtype: np.dtype
    shape: tuple
    cpu: np.ndarray
    gpu: int
