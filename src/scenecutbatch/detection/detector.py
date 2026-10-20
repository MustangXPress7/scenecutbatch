"""Scene-cut detection wrapper around PySceneDetect."""

from __future__ import annotations

import logging
import time
from fractions import Fraction
from pathlib import Path
from typing import Callable, Optional

from ..core.models import DetectionResult, Scene, DetectConfig

logger = logging.getLogger(__name__)

# Default fps used when the video stream/ffprobe cannot be probed (D-07 graceful degrade).
DEFAULT_FPS = Fraction(30, 1)


def _fps_from_video(video) -> Fraction:
    """Best-effort frame rate from a scenedetect VideoStream; falls back to 30/1."""
    fps = getattr(video, "frame_rate", None)
    if fps is None:
        fps = getattr(video, "_frame_rate", None)
    if fps is None:
        return DEFAULT_FPS
    try:
        return Fraction(str(fps))
    except (ValueError, ZeroDivisionError):
        logger.warning("Could not parse frame rate %r; defaulting to 30/1", fps)
        return DEFAULT_FPS


def detect_clip(video_path: Path, config: Optional[DetectConfig] = None,
                progress: Optional[Callable[[str], None]] = None) -> DetectionResult:
    """Detect hard cuts in a single clip using PySceneDetect ContentDetector.

    Returns a DetectionResult; on failure sets .error and returns empty scenes
    (D-03 per-clip error isolation).
    """
    config = config or DetectConfig()
    result = DetectionResult(clip_path=Path(video_path))
    started = time.time()
    try:
        from scenedetect import open_video, SceneManager, ContentDetector

        video = open_video(str(video_path))
        result.fps = _fps_from_video(video)

        scene_manager = SceneManager()
        scene_manager.add_detector(ContentDetector(
            threshold=config.threshold,
            min_scene_len=config.min_scene_len_frames,
        ))
        scene_manager.detect_scenes(video, show_progress=False)
        scene_list = scene_manager.get_scene_list(start_in_scene=True)

        for i, (start_tc, end_tc) in enumerate(scene_list):
            start_frame = int(start_tc.get_frames())
            end_frame = int(end_tc.get_frames())
            start_sec = float(start_tc.get_seconds())
            end_sec = float(end_tc.get_seconds())
            result.scenes.append(Scene(
                index=i,
                start_frame=start_frame,
                end_frame=end_frame,
                start_time=start_sec,
                end_time=end_sec,
                start_tc=start_tc.get_timecode(),
                end_tc=end_tc.get_timecode(),
                duration_sec=end_sec - start_sec,
                detection_score=0.0,  # placeholder; real score needs StatsManager (deferred)
            ))
    except Exception as exc:  # noqa: BLE001
        logger.exception("Detection failed for %s", video_path)
        result.error = str(exc)
    result.processing_time_sec = time.time() - started
    return result
