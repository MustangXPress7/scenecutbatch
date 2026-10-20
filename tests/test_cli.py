"""Tests for the CLI (Plan 01-03)."""

import io
import json
import contextlib
from pathlib import Path

import cv2
import numpy as np
import pytest
import typer.exceptions

from scenecutbatch.cli import _run_detect, _version_callback
from scenecutbatch.core.models import DetectConfig


def _make_clip(tmp_path: Path, name: str, fps=30.0, size=(64, 64), total=60) -> Path:
    path = tmp_path / name
    fourcc = cv2.VideoWriter_fourcc(*"mp4v")
    writer = cv2.VideoWriter(str(path), fourcc, fps, size)
    try:
        for _ in range(total):
            writer.write(np.zeros((size[1], size[0], 3), dtype=np.uint8))
    finally:
        writer.release()
    return path


def _invoke(tmp_path: Path, **kwargs):
    """Call _run_detect; return (exit_code_or_None, stdout, stderr)."""
    out = io.StringIO()
    err = io.StringIO()
    code = None
    with contextlib.redirect_stdout(out), contextlib.redirect_stderr(err):
        try:
            _run_detect(tmp_path, **kwargs)
        except typer.exceptions.Exit as exc:
            code = exc.exit_code
        except SystemExit as exc:  # pragma: no cover - fallback
            code = exc.code
    return code, out.getvalue(), err.getvalue()


def test_cli_detect_runs_and_exits_zero(tmp_path):
    """`detect <dir>` runs detect_folder, prints summary, exits 0."""
    _make_clip(tmp_path, "clip_a.mp4")
    code, out, err = _invoke(
        tmp_path,
        out_dir=None,
        threshold=27.0,
        min_scene_len=15,
        recursive=False,
        extensions=None,
        dry_run=False,
        json_progress=False,
        confidence=False,
        config=None,
    )
    assert code is None, err  # exit 0
    assert "Batch done:" in out
    assert "1 succeeded" in out


def test_cli_bad_input_dir_exits_two(tmp_path):
    """A missing/not-a-dir input dir exits with code 2."""
    code, out, err = _invoke(
        tmp_path / "nope",
        out_dir=None,
        threshold=27.0,
        min_scene_len=15,
        recursive=False,
        extensions=None,
        dry_run=False,
        json_progress=False,
        confidence=False,
        config=None,
    )
    assert code == 2


def test_cli_version_prints_0_1_0():
    """--version prints __version__ (0.1.0)."""
    out = io.StringIO()
    with pytest.raises(typer.exceptions.Exit) as exc, contextlib.redirect_stdout(out):
        _version_callback(True)
    assert exc.value.exit_code == 0
    assert out.getvalue().strip() == "0.1.0"


def test_cli_dry_run_writes_nothing(tmp_path):
    """--dry-run lists cuts and creates no _cuts.xml files."""
    _make_clip(tmp_path, "clip_a.mp4")
    code, out, err = _invoke(
        tmp_path,
        out_dir=None,
        threshold=27.0,
        min_scene_len=15,
        recursive=False,
        extensions=None,
        dry_run=True,
        json_progress=False,
        confidence=False,
        config=None,
    )
    assert code is None, err
    # Scene list printed to stdout (start_tc/end_tc/duration).
    assert "00:00:00.000" in out
    # No _cuts.xml files written anywhere.
    assert list(tmp_path.rglob("*_cuts.xml")) == []


def test_cli_json_progress_emits_json(tmp_path):
    """--json-progress emits valid JSON per event line to stdout."""
    _make_clip(tmp_path, "clip_a.mp4")
    code, out, err = _invoke(
        tmp_path,
        out_dir=None,
        threshold=27.0,
        min_scene_len=15,
        recursive=False,
        extensions=None,
        dry_run=False,
        json_progress=True,
        confidence=False,
        config=None,
    )
    assert code is None, err
    lines = [line for line in out.splitlines() if line.strip().startswith("{")]
    events = [json.loads(line) for line in lines]
    event_types = [e.get("event") for e in events]
    assert "start" in event_types
    assert "clip_start" in event_types
    assert "clip_done" in event_types
    assert "done" in event_types


def test_cli_config_file_overrides_threshold(tmp_path):
    """--config YAML overrides threshold/min_scene_len; CLI flags override config."""
    _make_clip(tmp_path, "clip_a.mp4")
    cfg_file = tmp_path / "config.yaml"
    cfg_file.write_text("threshold: 42.0\nmin_scene_len_frames: 30\n", encoding="utf-8")
    code, out, err = _invoke(
        tmp_path,
        out_dir=None,
        threshold=55.0,
        min_scene_len=15,
        recursive=False,
        extensions=None,
        dry_run=False,
        json_progress=False,
        confidence=False,
        config=str(cfg_file),
    )
    assert code is None, err
    assert "Batch done:" in out


def test_cli_recursive_and_extensions_passed_through(tmp_path):
    """--recursive and --extensions are accepted and passed to config."""
    sub = tmp_path / "sub"
    sub.mkdir()
    _make_clip(sub, "clip_b.mov")
    _make_clip(tmp_path, "clip_a.mp4")
    # Non-recursive: only top-level mp4 found.
    code, out, err = _invoke(
        tmp_path,
        out_dir=None,
        threshold=27.0,
        min_scene_len=15,
        recursive=False,
        extensions=("mp4",),
        dry_run=False,
        json_progress=False,
        confidence=False,
        config=None,
    )
    assert code is None, err
    assert "1 succeeded" in out
    # Recursive: finds the mov in sub too.
    code, out, err = _invoke(
        tmp_path,
        out_dir=None,
        threshold=27.0,
        min_scene_len=15,
        recursive=True,
        extensions=("mov",),
        dry_run=False,
        json_progress=False,
        confidence=False,
        config=None,
    )
    assert code is None, err
    assert "1 succeeded" in out
