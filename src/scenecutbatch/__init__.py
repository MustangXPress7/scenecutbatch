"""Scene Cut Batch — batch scene-cut detection for Premiere Pro."""

__version__ = "0.1.0"

from .core.batch import detect_folder
from .detection.detector import detect_clip
from .core.models import BatchResult, DetectionResult, DetectConfig, Scene

__all__ = [
    "detect_clip",
    "detect_folder",
    "BatchResult",
    "DetectionResult",
    "DetectConfig",
    "Scene",
    "__version__",
]
