"""Tests for detector (Task 01-01-B)."""

import cv2
import numpy as np
import pytest
from fractions import Fraction

from scenecutbatch.core.models import DetectConfig
from scenecutbatch.detection.detector import detect_clip


def _make_cut_clip(tmp_path, name="cut_clip.mp4", fps=30.0, size=(64, 64), cut_at=30, total=60):
    """Write a synthetic clip with a hard cut (black->white) at `cut_at`."""
    path = tmp_path / name
    fourcc = cv2.VideoWriter_fourcc(*"mp4v")
    writer = cv2.VideoWriter(str(path), fourcc, fps, size)
    try:
        for i in range(total):
            frame = np.zeros((size[1], size[0], 3), dtype=np.uint8) if i < cut_at else np.full(
                (size[1], size[0], 3), 255, dtype=np.uint8
            )
            writer.write(frame)
    finally:
        writer.release()
    return path


def test_detect_clip_returns_scenes(tmp_path):
    """detect_clip on a real clip returns DetectionResult with >= 1 Scene."""
    path = _make_cut_clip(tmp_path)
    result = detect_clip(path, DetectConfig())
    assert result.error is None, result.error
    assert len(result.scenes) >= 1
    scene = result.scenes[0]
    assert scene.start_tc and scene.end_tc
    assert scene.duration_sec >= 0
    assert scene.detection_score == 0.0  # placeholder
    assert result.fps == Fraction(30, 1)


def test_detect_clip_missing_file_returns_error(tmp_path):
    """On missing/corrupt file returns error set and empty scenes without raising."""
    missing = tmp_path / "does_not_exist.mp4"
    result = detect_clip(missing, DetectConfig())
    assert result.error is not None
    assert result.scenes == []
