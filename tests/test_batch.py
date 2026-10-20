"""Integration tests for the batch runner (Plan 01-05-A).

Uses mocked ``detect_clip`` so no real video files or ffprobe are needed.
Covers CUT-05 (error isolation), UX-01 (progress + ETA), OUT-01/OUT-02 (XML per clip).
"""

from __future__ import annotations

from pathlib import Path
from unittest import mock

import pytest

from scenecutbatch.core.batch import detect_folder
from scenecutbatch.core.models import DetectConfig, DetectionResult, Scene


def _good_result(stem: str) -> DetectionResult:
    return DetectionResult(
        clip_path=Path(f"/tmp/{stem}.mp4"),
        scenes=[Scene(0, 0, 30, 0.0, 1.0, "00:00:00:00", "00:00:01:00", 1.0, 0.0)],
        processing_time_sec=0.5,
    )


def _bad_result(stem: str) -> DetectionResult:
    return DetectionResult(
        clip_path=Path(f"/tmp/{stem}.mp4"),
        error="unreadable file",
        processing_time_sec=0.1,
    )


def test_detect_folder_error_isolation(tmp_path: Path, monkeypatch: pytest.MonkeyPatch):
    """detect_folder returns total=2, succeeded=1, failed=1; no exception raised.

    {stem}_cuts.xml written only for the good clip.
    """
    (tmp_path / "good_clip.mp4").write_bytes(b"not a video")
    (tmp_path / "bad_file.mp4").write_bytes(b"this is not a video")

    calls = []

    def fake_detect_clip(video_path, config=None):
        name = Path(video_path).stem
        calls.append(name)
        if name == "good_clip":
            return _good_result("good_clip")
        return _bad_result("bad_file")

    monkeypatch.setattr("scenecutbatch.core.batch.detect_clip", fake_detect_clip)

    events = []

    def progress(event):
        events.append(event)

    batch = detect_folder(tmp_path, DetectConfig(), progress=progress, write_xml=True)

    assert batch.total == 2
    assert len(batch.succeeded) == 1
    assert len(batch.failed) == 1
    assert batch.succeeded[0].clip_path.name == "good_clip.mp4"
    assert batch.failed[0].clip_path.name == "bad_file.mp4"
    assert batch.failed[0].error is not None
    assert batch.started_at and batch.finished_at

    xml_files = list((tmp_path / "cuts").glob("*_cuts.xml"))
    assert len(xml_files) == 1
    assert xml_files[0].name == "good_clip_cuts.xml"


def test_detect_folder_progress_eta(tmp_path: Path, monkeypatch: pytest.MonkeyPatch):
    """Capture progress callback events; clip_done shaped per docs/04 schema, eta_sec>=0."""
    (tmp_path / "clip_one.mp4").write_bytes(b"x")
    (tmp_path / "clip_two.mp4").write_bytes(b"y")

    results = [_good_result("clip_one"), _good_result("clip_two")]

    def fake_detect_clip(video_path, config=None):
        return results.pop(0)

    monkeypatch.setattr("scenecutbatch.core.batch.detect_clip", fake_detect_clip)

    events = []

    def progress(event):
        events.append(event)

    detect_folder(tmp_path, DetectConfig(), progress=progress, write_xml=False)

    event_types = [e.get("event") for e in events]
    assert "clip_start" in event_types
    assert "clip_done" in event_types
    assert "done" in event_types

    done_events = [e for e in events if e.get("event") == "clip_done"]
    assert len(done_events) == 2
    for e in done_events:
        assert set(["event", "index", "total", "clip", "scenes", "status", "eta_sec"]).issubset(e.keys())
        assert e["event"] == "clip_done"
        assert e["total"] == 2
        assert e["index"] in (1, 2)
        assert isinstance(e["scenes"], int) and e["scenes"] >= 1
        assert e["status"] == "ok"
        assert e["eta_sec"] >= 0


def test_detect_folder_writes_xml_per_clip(tmp_path: Path, monkeypatch: pytest.MonkeyPatch):
    """Output dir contains {stem}_cuts.xml for each succeeded clip."""
    for stem in ("alpha", "beta", "gamma"):
        (tmp_path / f"{stem}.mp4").write_bytes(b"x")

    def fake_detect_clip(video_path, config=None):
        stem = Path(video_path).stem
        return _good_result(stem)

    monkeypatch.setattr("scenecutbatch.core.batch.detect_clip", fake_detect_clip)

    batch = detect_folder(tmp_path, DetectConfig(), progress=None, write_xml=True)

    assert len(batch.succeeded) == 3
    xml_files = sorted(p.name for p in (tmp_path / "cuts").glob("*_cuts.xml"))
    assert xml_files == ["alpha_cuts.xml", "beta_cuts.xml", "gamma_cuts.xml"]
