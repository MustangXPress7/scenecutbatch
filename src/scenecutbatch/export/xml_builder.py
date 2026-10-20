"""FCP7 XML builder for virtual subclips."""

from __future__ import annotations

from pathlib import Path
from typing import Optional

from ..core.models import DetectionResult, DetectConfig


def build_xml(result: DetectionResult, config: Optional[DetectConfig] = None) -> str:
    """Return FCP7 XML string for a detection result.

    TODO (Phase 2): implement xmeml with master sequence + virtual subclips.
    """
    raise NotImplementedError


def write_xml(result: DetectionResult, output_path: Path,
              config: Optional[DetectConfig] = None) -> Path:
    """Write XML to disk and return path."""
    output_path = Path(output_path)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    content = build_xml(result, config)
    output_path.write_text(content, encoding="utf-8")
    return output_path
