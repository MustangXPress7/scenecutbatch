"""Tests for batch runner (Plan 01-02)."""

import json
from pathlib import Path

import cv2
import numpy as np
import pytest

from scenecutbatch.core.batch import detect_folder
from scenecutbatch.core.models import DetectConfig


def _make_clip(tmp_path: Path, name: str, fps=30.0, size=(64, 64), total=60) -> Path:
    """Write a synthetic all-black clip (no cuts -> 1 scene via start_in_scene=True)."""
    path = tmp_path / name
    fourcc = cv2.VideoWriter_fourcc(*"mp4v")
    writer = cv2.VideoWriter(str(path), fourcc, fps, size)
    try:
        for _ in range(total):
            frame = np.zeros((size[1], size[0], 3), dtype=np.uint8)
            writer.write(frame)
    finally:
        writer.release()
    return path


def test_detect_folder_error_isolation(tmp_path):
    """detect_folder on one good clip + one unreadable file: total=2, succeeded=1, failed=1."""
    good = _make_clip(tmp_path, "good_clip.mp4")
    bad = tmp_path / "bad_file.mp4"
    bad.write_bytes(b"this is not a video file")

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

    # {stem}_cuts.xml written for good clip only.
    xml_files = list((tmp_path / "cuts").glob("*_cuts.xml"))
    assert len(xml_files) == 1
    assert xml_files[0].name == "good_clip_cuts.xml"

    # Progress callback receives clip_start / clip_done / clip_error / done.
    event_types = [e.get("event") for e in events]
    assert "clip_start" in event_types
    assert "clip_done" in event_types
    assert "clip_error" in event_types
    assert "done" in event_types


def test_progress_eta_shape(tmp_path):
    """clip_done progress event is a JSON-serializable dict with eta_sec >= 0."""
    _make_clip(tmp_path, "clip_one.mp4", total=30)
    _make_clip(tmp_path, "clip_two.mp4", total=30)

    events = []

    def progress(event):
        events.append(event)

    batch = detect_folder(tmp_path, DetectConfig(), progress=progress, write_xml=False)

    done_events = [e for e in events if e.get("event") == "clip_done"]
    assert len(done_events) == 2
    for e in done_events:
        # JSON-serializable dict matching docs/04-DATA-MODELS.json schema.
        json.dumps(e)
        assert set(["event", "index", "total", "clip", "scenes", "status", "eta_sec"]).issubset(e.keys())
        assert e["event"] == "clip_done"
        assert e["total"] == 2
        assert e["index"] in (1, 2)
        assert isinstance(e["scenes"], int) and e["scenes"] >= 1
        assert e["status"] == "ok"
        assert e["eta_sec"] >= 0
    # ETA decreases as clips complete; last clip has 0 remaining.
    assert done_events[0]["eta_sec"] >= done_events[1]["eta_sec"]
    assert done_events[1]["eta_sec"] == 0
