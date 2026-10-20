"""Scene-cut detection wrapper around PySceneDetect."""

from __future__ import annotations

import logging
import time
from pathlib import Path
from typing import Callable, Optional

from ..core.models import DetectionResult, Scene, DetectConfig

logger = logging.getLogger(__name__)


def detect_clip(video_path: Path, config: Optional[DetectConfig] = None,
                progress: Optional[Callable[[str], None]] = None) -> DetectionResult:
    """Detect hard cuts in a single clip.

    TODO (Phase 1): implement using scenedetect ContentDetector.
    Returns a DetectionResult; on failure sets .error and returns empty scenes.
    """
    config = config or DetectConfig()
    result = DetectionResult(clip_path=Path(video_path))
    started = time.time()
    try:
        # TODO: probe media (fps, size, duration) via ffprobe
        # TODO: run PySceneDetect ContentDetector
        # TODO: map detected scenes -> Scene list with timecodes
        result.error = "not implemented yet"
    except Exception as exc:  # noqa: BLE001
        logger.exception("Detection failed for %s", video_path)
        result.error = str(exc)
    result.processing_time_sec = time.time() - started
    return result
