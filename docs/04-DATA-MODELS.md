# 04 — Data Models

## Core types (Python dataclasses)

```python
from dataclasses import dataclass, field
from pathlib import Path
from fractions import Fraction
from typing import Optional, List

@dataclass
class Scene:
    index: int
    start_frame: int
    end_frame: int
    start_time: float        # seconds
    end_time: float
    start_tc: str           # SMPTE-ish "HH:MM:SS:FF"
    end_tc: str
    duration_sec: float
    detection_score: float   # PySceneDetect score (higher = stronger cut)
    confidence: Optional[float] = None   # 0..1, filled by scorer
    classification: Optional[str] = None  # GREEN/YELLOW/RED

@dataclass
class DetectionResult:
    clip_path: Path
    fps: Fraction
    width: int
    height: int
    duration_sec: float
    scenes: List[Scene] = field(default_factory=list)
    error: Optional[str] = None   # if failed
    processing_time_sec: float = 0.0

@dataclass
class BatchResult:
    input_dir: Path
    output_dir: Path
    total: int
    succeeded: List[DetectionResult] = field(default_factory=list)
    failed: List[DetectionResult] = field(default_factory=list)
    started_at: str = ""
    finished_at: str = ""
```

## Config

```python
@dataclass
class DetectConfig:
    threshold: float = 27.0
    min_scene_len_frames: int = 15
    recursive: bool = False
    extensions: tuple = ("mp4","mov","mxf","avi","mkv","webm")
    confidence_enabled: bool = False
    output_naming: str = "{stem}_cuts.xml"
```

## JSON progress (stdout/file)

```json
{
  "event": "clip_done",
  "index": 3,
  "total": 100,
  "clip": "take_042.mov",
  "scenes": 7,
  "status": "ok",
  "eta_sec": 124.5
}
```

Events: `start`, `clip_start`, `clip_done`, `clip_error`, `done`.
The progress schema is versioned and its fields are stable across v1; consumers should not rely on undocumented fields.
