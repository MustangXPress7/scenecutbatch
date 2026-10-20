"""Batch runner (Phase 1)."""

from __future__ import annotations

import time
from pathlib import Path
from typing import Callable, Optional

from ..core.models import BatchResult, DetectConfig, DetectionResult
from ..detection.detector import detect_clip
from ..media.scanner import scan_folder


def detect_folder(input_dir, config: Optional[DetectConfig] = None,
                  progress: Optional[Callable[[str], None]] = None,
                  write_xml: bool = True) -> BatchResult:
    """Process a folder of clips.

    TODO (Phase 1): implement scanning + per-clip detection + error isolation.
    TODO (Phase 2): write XML per clip.
    """
    config = config or DetectConfig()
    input_dir = Path(input_dir)
    out_dir = input_dir / "cuts"
    files = scan_folder(input_dir, config)
    batch = BatchResult(input_dir=input_dir, output_dir=out_dir, total=len(files))
    batch.started_at = _now()
    for i, f in enumerate(files, 1):
        if progress:
            progress(f"clip_start {i}/{len(files)} {f.name}")
        res = detect_clip(f, config)
        if res.error:
            batch.failed.append(res)
        else:
            batch.succeeded.append(res)
        # TODO Phase 2: xml_builder.write(res, out_dir)
    batch.finished_at = _now()
    return batch


def _now() -> str:
    return time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())
