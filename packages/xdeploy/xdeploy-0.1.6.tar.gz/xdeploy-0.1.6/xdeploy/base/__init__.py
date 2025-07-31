import importlib.util

if importlib.util.find_spec("tensorrt"):
    from .build_tensorrt_engine import TRTBaseModel as Backend
elif importlib.util.find_spec("onnxruntime"):
    from .build_onnx_engine import ORTBaseModel as Backend
elif importlib.util.find_spec("openvino"):
    from .build_ov_engine import OVBaseModel as Backend

from .tensor import Tensor
from .yolo import YOLO

__all__ = ["Backend", "Tensor", "YOLO"]
