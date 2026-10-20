"""Core data models for SceneCutBatch."""

from dataclasses import dataclass, field
from fractions import Fraction
from pathlib import Path
from typing import List, Optional


@dataclass
class Scene:
    index: int
    start_frame: int
    end_frame: int
    start_time: float
    end_time: float
    start_tc: str
    end_tc: str
    duration_sec: float
    detection_score: float
    confidence: Optional[float] = None
    classification: Optional[str] = None


@dataclass
class DetectionResult:
    clip_path: Path
    fps: Fraction = Fraction(30, 1)
    width: int = 0
    height: int = 0
    duration_sec: float = 0.0
    scenes: List[Scene] = field(default_factory=list)
    error: Optional[str] = None
    processing_time_sec: float = 0.0


@dataclass
class DetectConfig:
    threshold: float = 27.0
    min_scene_len_frames: int = 15
    recursive: bool = False
    extensions: tuple = ("mp4", "mov", "mxf", "avi", "mkv", "webm")
    confidence_enabled: bool = False
    output_naming: str = "{stem}_cuts.xml"


@dataclass
class BatchResult:
    input_dir: Path
    output_dir: Path
    total: int = 0
    succeeded: List[DetectionResult] = field(default_factory=list)
    failed: List[DetectionResult] = field(default_factory=list)
    started_at: str = ""
    finished_at: str = ""
