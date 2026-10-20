"""Smoke tests for scaffold (Phase 1 will replace with real tests)."""

from scenecutbatch import __version__
from scenecutbatch.core.models import DetectConfig
from scenecutbatch.media.scanner import scan_folder


def test_version():
    assert __version__ == "0.1.0"


def test_detect_config_defaults():
    c = DetectConfig()
    assert c.threshold == 27.0
    assert c.min_scene_len_frames == 15


def test_scan_folder_empty(tmp_path):
    assert scan_folder(tmp_path, DetectConfig()) == []
