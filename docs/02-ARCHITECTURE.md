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
- Media scanner/layout follows this project's own module conventions.

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
- Use `pathurl` `file://localhost/...` form (FCP7 xmeml convention).
- Frame-accurate via rational timebase (`fractions.Fraction`, exact for NTSC 24000/1001 etc.).

### 5. Confidence scorer (`confidence/scorer.py`) — optional
- Score per scene from detection score + duration + min-length proximity.
- Map to G/Y/R.
- Inject markers into XML.

### 6. CLI (`cli.py`)
- Typer, chosen for its typed CLI shape and eager `--version` callback.
- Flags: `--input`, `--out-dir`, `--threshold`, `--min-scene-len`,
  `--recursive`, `--dry-run`, `--json-progress`, `--config`.
- Exit codes: 0 success, 1 usage, 2 validation, 3 processing error, 4 export error.

### 7. Optional GUI (`gui.py`)
- Gradio, optional desktop GUI (v1.1).

## Data flow

```
folder -> scanner -> [clip paths] -> batch runner
  -> detector per clip -> scenes
  -> xml_builder -> <clip>_cuts.xml
  -> progress callback -> stdout/json
```

## Design decisions and reuse within this project

- Virtual subclips reference original media (no duplication), built from the
  same scanner, detector and XML builder used by the CLI.
- JSON progress callback (`docs/04`) drives CLI and GUI progress reporting.
- Packaging is PyInstaller one-folder plus one-file, with assets bundled next
  to the executable.

## Design rules

- No global mutable state; pass config explicitly.
- Detector is a pure function of (video_path, params) -> DetectionResult.
- XML builder is a pure function of (clip_path, scenes, params) -> str.
- All I/O at the edges (CLI/batch).
- Tests are fast and offline (use tiny synthetic clips or mocked detector).
