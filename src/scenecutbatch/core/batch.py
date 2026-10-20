"""Batch runner (Phase 1)."""

from __future__ import annotations

import time
from pathlib import Path
from typing import Callable, Optional

from ..core.models import BatchResult, DetectConfig, DetectionResult
from ..detection.detector import detect_clip
from ..export.xml_builder import write_xml as _write_xml
from ..media.scanner import scan_folder


def detect_folder(input_dir, config: Optional[DetectConfig] = None,
                  progress: Optional[Callable[[dict], None]] = None,
                  write_xml: bool = True) -> BatchResult:
    """Process a folder of clips.

    Iterates clips returned by scan_folder, runs per-clip detection with
    error isolation (one bad clip never aborts the batch), writes one
    `{stem}_cuts.xml` per successful clip when write_xml is True, and reports
    JSON progress events (start, clip_start, clip_done, clip_error, done)
    including a running-average ETA (UX-01, matches docs/04-DATA-MODELS.json).
    """
    config = config or DetectConfig()
    input_dir = Path(input_dir)
    out_dir = input_dir / "cuts"
    files = scan_folder(input_dir, config)
    total = len(files)
    batch = BatchResult(input_dir=input_dir, output_dir=out_dir, total=total)
    batch.started_at = _now()
    if progress:
        progress({"event": "start", "total": total, "input_dir": str(input_dir)})

    elapsed_sum = 0.0
    completed = 0
    for i, f in enumerate(files, 1):
        if progress:
            progress({"event": "clip_start", "index": i, "total": total,
                      "clip": f.name, "status": "started"})
        res = detect_clip(f, config)
        if res.error:
            # D-03 / CUT-05: per-clip error isolation, never abort the batch.
            batch.failed.append(res)
            if progress:
                progress({"event": "clip_error", "index": i, "total": total,
                          "clip": f.name, "status": "error", "error": res.error})
        else:
            batch.succeeded.append(res)
            if write_xml:
                _write_xml(res, out_dir / f"{res.clip_path.stem}_cuts.xml", config)
            # Task 01-02-B: running-average ETA.
            completed += 1
            elapsed_sum += float(res.processing_time_sec)
            avg_sec_per_clip = elapsed_sum / completed
            remaining = total - i
            eta_sec = avg_sec_per_clip * remaining
            if progress:
                progress({"event": "clip_done", "index": i, "total": total,
                          "clip": f.name, "scenes": len(res.scenes),
                          "status": "ok", "eta_sec": eta_sec})
    batch.finished_at = _now()
    if progress:
        progress({"event": "done", "total": total,
                  "succeeded": len(batch.succeeded), "failed": len(batch.failed)})
    return batch


def _now() -> str:
    return time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())
