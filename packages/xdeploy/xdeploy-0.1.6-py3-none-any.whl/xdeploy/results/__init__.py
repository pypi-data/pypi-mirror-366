from .classify_result import ClassifyResult
from .detection_result import DetectionResult
from .instance_seg_result import InstanceSegResult
from .obb_result import OBBResult
from .ocr_result import OCRResult
from .pose_result import PoseResult
from .semantic_seg_result import SemanticSegResult

__all__ = [
    "ClassifyResult",
    "DetectionResult",
    "OBBResult",
    "OCRResult",
    "InstanceSegResult",
    "SemanticSegResult",
    "PoseResult",
]
