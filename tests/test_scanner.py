"""Tests for media scanner (Plan 01-04-A)."""

from pathlib import Path

from scenecutbatch.core.models import DetectConfig
from scenecutbatch.media.scanner import scan_folder


def _make_file(tmp_input_dir: Path, name: str) -> Path:
    p = tmp_input_dir / name
    p.write_bytes(b"dummy video bytes")
    return p


def test_scan_folder_empty(tmp_input_dir: Path, config: DetectConfig):
    """scan_folder returns [] for an empty dir."""
    assert scan_folder(tmp_input_dir, config) == []


def test_scan_folder_single_file(tmp_input_dir: Path, config: DetectConfig):
    """scan_folder returns exactly one Path for a dir containing one supported video."""
    _make_file(tmp_input_dir, "clip.mp4")
    _make_file(tmp_input_dir, "readme.txt")
    files = scan_folder(tmp_input_dir, config)
    assert len(files) == 1
    assert files[0].name == "clip.mp4"


def test_scan_folder_case_insensitive(tmp_input_dir: Path, config: DetectConfig):
    """scan_folder matches extensions case-insensitively (.MP4/.Mov match)."""
    _make_file(tmp_input_dir, "clip.MP4")
    _make_file(tmp_input_dir, "clip.Mov")
    files = scan_folder(tmp_input_dir, config)
    assert sorted(f.name for f in files) == ["clip.MP4", "clip.Mov"]


def test_scan_folder_ignores_unsupported(tmp_input_dir: Path, config: DetectConfig):
    """scan_folder ignores unsupported extensions (.txt ignored)."""
    _make_file(tmp_input_dir, "clip.mp4")
    _make_file(tmp_input_dir, "clip.txt")
    files = scan_folder(tmp_input_dir, config)
    assert [f.name for f in files] == ["clip.mp4"]


def test_scan_folder_recursive(tmp_input_dir: Path, config: DetectConfig):
    """scan_folder walks subdirectories when recursive=True (CUT-01)."""
    _make_file(tmp_input_dir, "top.mp4")
    sub = tmp_input_dir / "sub"
    sub.mkdir()
    _make_file(sub, "nested.mp4")
    files = scan_folder(tmp_input_dir, DetectConfig(recursive=True))
    names = sorted(f.name for f in files)
    assert names == ["nested.mp4", "top.mp4"]
    # non-recursive should not find nested
    files_flat = scan_folder(tmp_input_dir, DetectConfig(recursive=False))
    assert [f.name for f in files_flat] == ["top.mp4"]
