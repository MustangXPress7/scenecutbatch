"""Shared pytest fixtures for SceneCutBatch (Plan 01-04).

Fixtures:
- tmp_input_dir: empty temp dir (Path) used as scan_folder input (CUT-01, D-04).
- config: DetectConfig with v1 defaults (threshold 27.0, min scene length 15).
- mocked_scenedetect: monkeypatches scenedetect.open_video / SceneManager /
  ContentDetector / detect_scenes / get_scene_list so detector tests run without
  real video files or ffprobe. Returns {"content_detector_kwargs": ...} so tests
  can assert threshold/min_scene_len were forwarded to ContentDetector (CUT-03,
  D-01).
"""

from __future__ import annotations

from pathlib import Path

import pytest
from scenedetect import FrameTimecode

from scenecutbatch.core.models import DetectConfig


@pytest.fixture
def tmp_input_dir(tmp_path: Path) -> Path:
    """Empty temp directory used as scan_folder input."""
    return tmp_path


@pytest.fixture
def config() -> DetectConfig:
    """DetectConfig with v1 defaults (D-01)."""
    return DetectConfig()


@pytest.fixture
def mocked_scenedetect(monkeypatch: pytest.MonkeyPatch):
    """Monkeypatch scenedetect so detect_clip runs without real video/ffprobe.

    open_video returns a dummy object; SceneManager and ContentDetector are fakes
    that record constructor kwargs and return a fixed list of FrameTimecode pairs
    from get_scene_list().
    """
    import scenedetect

    captured: dict = {"content_detector_kwargs": None}

    # Two fixed scenes: frames [0, 30) and [30, 60) at 30 fps.
    scene_pairs = [
        (FrameTimecode(0, 30), FrameTimecode(30, 30)),
        (FrameTimecode(30, 30), FrameTimecode(60, 30)),
    ]

    class FakeSceneManager:
        def __init__(self) -> None:
            self.detectors = []

        def add_detector(self, detector) -> None:
            self.detectors.append(detector)
            captured["content_detector_kwargs"] = getattr(detector, "kwargs", None)

        def detect_scenes(self, video, show_progress: bool = False) -> None:
            return None

        def get_scene_list(self, start_in_scene: bool = False):
            return list(scene_pairs)

    class FakeContentDetector:
        def __init__(self, **kwargs) -> None:
            self.kwargs = kwargs

    _dummy_video = object()

    monkeypatch.setattr(scenedetect, "open_video", lambda path: _dummy_video)
    monkeypatch.setattr(scenedetect, "SceneManager", FakeSceneManager)
    monkeypatch.setattr(scenedetect, "ContentDetector", FakeContentDetector)

    return captured
