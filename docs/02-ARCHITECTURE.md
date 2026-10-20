# 02 — Architecture

## High-level

```
┌────────────┐     ┌──────────────┐     ┌──────────────┐     ┌────────────┐
│  CLI / GUI │ --> │ Media scanner │ --> │ Detector     │ --> │ XML builder│ --> .xml
└────────────┘     └──────────────┘     │ (PySceneDetect)│     └────────────┘
                                        └──────────────┘
                                              │
                                              ▼
                                       ┌──────────────┐
                                       │ Confidence   │ (optional)
                                       │ scorer       │
                                       └──────────────┘
```

## Components

### 1. Media scanner (`media/scanner.py`)
- Walk input folder (recursive optional).
- Filter by supported extensions (case-insensitive).
- Probe each file with ffprobe to get duration, fps, resolution, codec.
- Skip unreadable files with a warning (do not crash).
- Reuse EsqueletoEdit's `media/scanner.py` and `media/models.py` patterns.

### 2. Detector (`detection/detector.py`)
- Wrap `scenedetect` (PySceneDetect).
- Use `ContentDetector(threshold=..., min_scene_len=...)`.
- Open video via OpenCV backend.
- Return `DetectionResult(clip_path, scenes=[Scene(start, end, score)], error=None)`.
- Isolate per-clip failures: catch exceptions, record error, continue.

### 3. Batch runner (`core/batch.py`)
- Iterate clips, call detector, call xml_builder, write output.
- Invoke progress callback `(index, total, clip_name, status, eta)`.
- Collect results into `BatchResult` (successes, failures, timings).
- Support cancellation (optional flag).

### 4. XML builder (`export/xml_builder.py`)
- Build FCP7 XML (xmeml) with:
  - `<bin>` named after clip.
  - Master `<sequence>` with clips in order.
  - One `<clip>`/`<subclip>` per detected scene referencing original media
    (`<file>` with `<pathurl>`).
  - Optional `<marker>` elements for confidence.
- Use `pathurl` `file://localhost/...` form (Premiere-compatible).
- Frame-accurate via rational timebase (reuse EsqueletoEdit's Fraction approach).

### 5. Confidence scorer (`confidence/scorer.py`) — optional
- Score per scene from detection score + duration + min-length proximity.
- Map to G/Y/R.
- Inject markers into XML.

### 6. CLI (`cli.py`)
- Typer, consistent with EsqueletoEdit.
- Flags: `--input`, `--out-dir`, `--threshold`, `--min-scene-len`,
  `--recursive`, `--dry-run`, `--json-progress`, `--config`.
- Exit codes: 0 success, 1 usage, 2 validation, 3 processing error, 4 export error.

### 7. Optional GUI (`gui.py`)
- Gradio, consistent with EsqueletoEdit (v1.1, optional).

## Data flow

```
folder -> scanner -> [clip paths] -> batch runner
  -> detector per clip -> scenes
  -> xml_builder -> <clip>_cuts.xml
  -> progress callback -> stdout/json
```

## Reusable from EsqueletoEdit

- `media/scanner.py`, `media/models.py`, `media/validator.py`
- `export/fcp7xml_exporter.py` patterns (FCP7 XML via otio-fcp-adapter) — but
  note: this project needs *virtual subclips referencing original media*, which
  the EsqueletoEdit exporter (timeline clips with source ranges) already
  approximates. Evaluate reusing `otio_builder` + `fcp7xml_exporter` directly.
- `progress.py` SSE/JSON progress.
- Pinokio recipe + Nuitka build scripts.

## Design rules

- No global mutable state; pass config explicitly.
- Detector is a pure function of (video_path, params) -> DetectionResult.
- XML builder is a pure function of (clip_path, scenes, params) -> str.
- All I/O at the edges (CLI/batch).
- Tests are fast and offline (use tiny synthetic clips or mocked detector).
