"""Integration tests for the CLI (Plan 01-05-B).

Uses Typer CliRunner-style invocation via ``_run_detect`` with a mocked
``detect_clip`` so no real video files or ffprobe are needed.
Covers exit codes (0/2), dry-run, json-progress, config-file threshold, version.
"""

from __future__ import annotations

import contextlib
import io
import json
from pathlib import Path
from unittest import mock

import pytest
import typer.exceptions

from scenecutbatch.cli import _run_detect, _version_callback
from scenecutbatch.core.models import BatchResult, DetectionResult, Scene


def _empty_clip(tmp_path: Path, name: str) -> Path:
    path = tmp_path / name
    path.write_bytes(b"")
    return path


def _good_result(stem: str) -> DetectionResult:
    return DetectionResult(
        clip_path=Path(f"/tmp/{stem}.mp4"),
        scenes=[Scene(0, 0, 30, 0.0, 1.0, "00:00:00:00", "00:00:01:00", 1.0, 0.0)],
        processing_time_sec=0.5,
    )


def _invoke(tmp_path: Path, monkeypatch: pytest.MonkeyPatch, **kwargs):
    """Call _run_detect with detect_clip mocked; return (exit_code, stdout, stderr)."""
    detected = []

    def fake_detect_clip(video_path, config=None):
        detected.append(config)
        return _good_result(Path(video_path).stem)

    monkeypatch.setattr("scenecutbatch.core.batch.detect_clip", fake_detect_clip)

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
    return code, out.getvalue(), err.getvalue(), detected


def test_cli_detect_runs_and_exits_zero(tmp_path, monkeypatch):
    """`detect <dir>` runs detect_folder, prints summary, exits 0."""
    _empty_clip(tmp_path, "clip_a.mp4")
    code, out, err, _detected = _invoke(
        tmp_path,
        monkeypatch,
        out_dir=None,
        threshold=None,
        min_scene_len=None,
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


def test_cli_bad_input_dir_exit_2(tmp_path, monkeypatch):
    """A nonexistent input dir exits with code 2 (validation, before detection)."""
    code, out, err, _detected = _invoke(
        tmp_path / "nope",
        monkeypatch,
        out_dir=None,
        threshold=None,
        min_scene_len=None,
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


def test_cli_dry_run_writes_nothing(tmp_path, monkeypatch):
    """--dry-run lists cuts and creates no _cuts.xml files."""
    _empty_clip(tmp_path, "clip_a.mp4")
    code, out, err, _detected = _invoke(
        tmp_path,
        monkeypatch,
        out_dir=None,
        threshold=None,
        min_scene_len=None,
        recursive=False,
        extensions=None,
        dry_run=True,
        json_progress=False,
        confidence=False,
        config=None,
    )
    assert code is None, err
    # stdout lists cuts (start_tc/end_tc/duration).
    assert "00:00:00:00" in out
    # No _cuts.xml files written anywhere.
    assert list(tmp_path.rglob("*_cuts.xml")) == []


def test_cli_json_progress_emits_json(tmp_path, monkeypatch):
    """--json-progress emits valid JSON per event line to stdout."""
    _empty_clip(tmp_path, "clip_a.mp4")
    code, out, err, _detected = _invoke(
        tmp_path,
        monkeypatch,
        out_dir=None,
        threshold=None,
        min_scene_len=None,
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


def test_cli_config_file_overrides_threshold(tmp_path, monkeypatch):
    """--config YAML threshold wins when CLI --threshold is not given (UX-04).

    Config sets threshold 35.0; detector must be called with threshold 35.
    """
    _empty_clip(tmp_path, "clip_a.mp4")
    cfg_file = tmp_path / "config.yaml"
    cfg_file.write_text("threshold: 35.0\n", encoding="utf-8")
    code, out, err, detected = _invoke(
        tmp_path,
        monkeypatch,
        out_dir=None,
        threshold=None,
        min_scene_len=None,
        recursive=False,
        extensions=None,
        dry_run=False,
        json_progress=False,
        confidence=False,
        config=str(cfg_file),
    )
    assert code is None, err
    assert detected, "detect_clip should have been called"
    assert detected[0].threshold == 35.0, detected[0]


def test_cli_cli_threshold_overrides_config(tmp_path, monkeypatch):
    """Explicit CLI --threshold overrides config-file threshold."""
    _empty_clip(tmp_path, "clip_a.mp4")
    cfg_file = tmp_path / "config.yaml"
    cfg_file.write_text("threshold: 42.0\n", encoding="utf-8")
    code, out, err, detected = _invoke(
        tmp_path,
        monkeypatch,
        out_dir=None,
        threshold=55.0,
        min_scene_len=None,
        recursive=False,
        extensions=None,
        dry_run=False,
        json_progress=False,
        confidence=False,
        config=str(cfg_file),
    )
    assert code is None, err
    assert detected[0].threshold == 55.0, detected[0]
