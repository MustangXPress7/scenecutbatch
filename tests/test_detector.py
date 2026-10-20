"""Tests for detector (Plan 01-04-B) using mocked scenedetect."""

from fractions import Fraction
from pathlib import Path

from scenecutbatch.core.models import DetectConfig
from scenecutbatch.detection.detector import detect_clip


def test_detect_clip_returns_scenes(tmp_path, mocked_scenedetect, config):
    """detect_clip on a tmp clip returns DetectionResult with >= 1 Scene,
    start_tc/end_tc/duration_sec populated, detection_score == 0.0 placeholder."""
    clip = tmp_path / "clip.mp4"
    clip.write_bytes(b"dummy video bytes")
    result = detect_clip(clip, config)
    assert result.error is None, result.error
    assert len(result.scenes) >= 1
    scene = result.scenes[0]
    assert scene.start_tc
    assert scene.end_tc
    assert scene.duration_sec >= 0
    assert scene.detection_score == 0.0
    assert result.fps == Fraction(30, 1)


def test_detect_clip_bad_file_error_isolation(tmp_path, config):
    """detect_clip on nonexistent path returns error set, empty scenes, does not raise.

    Real scenedetect is used here (no mock) so open_video raises OSError on the
    missing file and detect_clip's per-clip error isolation (D-03) catches it.
    """
    missing = tmp_path / "does_not_exist.mp4"
    result = detect_clip(missing, config)
    assert result.error is not None
    assert result.scenes == []


def test_detect_clip_config_defaults(tmp_path, mocked_scenedetect, config):
    """threshold 27.0 and min_scene_len 15 are passed to ContentDetector (D-01)."""
    clip = tmp_path / "clip.mp4"
    clip.write_bytes(b"dummy video bytes")
    detect_clip(clip, config)
    kwargs = mocked_scenedetect["content_detector_kwargs"]
    assert kwargs == {"threshold": 27.0, "min_scene_len": 15}
