"""Smoke tests for scaffold (Phase 1 scanner tests moved to test_scanner.py)."""

from scenecutbatch import __version__
from scenecutbatch.core.models import DetectConfig


def test_version():
    assert __version__ == "0.1.0"


def test_detect_config_defaults():
    c = DetectConfig()
    assert c.threshold == 27.0
    assert c.min_scene_len_frames == 15
