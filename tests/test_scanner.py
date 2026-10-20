"""Tests for media scanner (Task 01-01-A)."""

from pathlib import Path

from scenecutbatch.core.models import DetectConfig
from scenecutbatch.media.scanner import scan_folder


def _make_video(tmp_path: Path, name: str) -> Path:
    p = tmp_path / name
    p.write_bytes(b"dummy video bytes")
    return p


def test_scan_folder_single_file(tmp_path):
    """scan_folder returns exactly one Path for a dir containing one supported video."""
    _make_video(tmp_path, "clip.mp4")
    _make_video(tmp_path, "readme.txt")
    files = scan_folder(tmp_path, DetectConfig())
    assert len(files) == 1
    assert files[0].name == "clip.mp4"
    assert files[0] == sorted(files)[0]


def test_scan_folder_empty(tmp_path):
    """scan_folder returns [] for an empty dir."""
    assert scan_folder(tmp_path, DetectConfig()) == []


def test_scan_folder_ignores_unsupported_extensions(tmp_path):
    """scan_folder ignores unsupported extensions."""
    _make_video(tmp_path, "clip.mp4")
    _make_video(tmp_path, "clip.jpg")
    _make_video(tmp_path, "clip.txt")
    files = scan_folder(tmp_path, DetectConfig())
    assert [f.name for f in files] == ["clip.mp4"]


def test_scan_folder_case_insensitive(tmp_path):
    """scan_folder matches extensions case-insensitively (.MP4 matches)."""
    _make_video(tmp_path, "clip.MP4")
    _make_video(tmp_path, "clip.Mov")
    files = scan_folder(tmp_path, DetectConfig())
    assert sorted(f.name for f in files) == ["clip.MP4", "clip.Mov"]


def test_scan_folder_recursive(tmp_path):
    """scan_folder walks subdirectories when recursive=True."""
    _make_video(tmp_path, "top.mp4")
    sub = tmp_path / "sub"
    sub.mkdir()
    _make_video(sub, "nested.mp4")
    files = scan_folder(tmp_path, DetectConfig(recursive=True))
    names = sorted(f.name for f in files)
    assert names == ["nested.mp4", "top.mp4"]
    # non-recursive should not find nested
    files_flat = scan_folder(tmp_path, DetectConfig(recursive=False))
    assert [f.name for f in files_flat] == ["top.mp4"]
