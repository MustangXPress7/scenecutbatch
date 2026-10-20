"""Media scanning (reuse EsqueletoEdit patterns)."""

from __future__ import annotations

from pathlib import Path
from typing import List

from ..core.models import DetectConfig


SUPPORTED_EXTENSIONS = {".mp4", ".mov", ".mxf", ".avi", ".mkv", ".webm"}


def scan_folder(input_dir: Path, config: DetectConfig) -> List[Path]:
    """Return list of video files in input_dir.

    TODO (Phase 1): implement recursive walk, extension filter (case-insensitive),
    ffprobe validation.
    """
    input_dir = Path(input_dir)
    exts = {e.lower().lstrip(".") for e in config.extensions}
    files: List[Path] = []
    iterator = input_dir.rglob("*") if config.recursive else input_dir.iterdir()
    for p in iterator:
        if p.is_file() and p.suffix.lower().lstrip(".") in exts:
            files.append(p)
    files.sort()
    return files


def probe_media(path: Path):
    """TODO: ffprobe JSON probe returning fps, duration, size, codec."""
    raise NotImplementedError
