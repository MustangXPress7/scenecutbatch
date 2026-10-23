# 09 — Extensibility and reuse

## Vision

SceneCutBatch is a local, offline scene-cut detector for professional video
editors' workflows. It scans a folder of video clips, detects hard cuts per clip
with PySceneDetect, and writes one FCP7 XML per clip (master sequence plus
virtual subclips that reference the original media) that any FCP7-capable editor
can import. The tool builds and runs by itself, with no runtime dependency on
any other application.

## Reusable pieces

The following pieces are documented so they can be reused within this project or
consumed by another tool:

- Media scanner (extensions, ffprobe probing, validation).
- FCP7 XML writer (virtual subclips referencing original media).
- Progress reporting schema (JSON events, see docs/04).
- Packaging scripts (PyInstaller one-folder plus one-file).
- Confidence marker conventions (G/Y/R thresholds).
- CLI conventions (Typer, exit codes, `--json-progress`).

## Ways to use SceneCutBatch

As a standalone public tool, SceneCutBatch can be consumed in several roles:

1. **As a library**: the public API `detect_folder` / `detect_clip` exposed by
   `scenecutbatch/__init__.py` returns `DetectionResult` objects that another
   tool can feed into its own media handling or rough-cut flow.
2. **As a CLI step in a pipeline or another tool's menu**: a host application
   runs SceneCutBatch over a footage folder and produces FCP7 XMLs the editor
   can import into a bin with a master sequence and virtual subclips.
3. **As a standalone desktop app**: the optional GUI runs locally and emits the
   same XML output without depending on any editing application.

## Design rules that keep reuse cheap

- No hard dependency on any host application (this repo must build/run alone).
- Public Python API in `scenecutbatch/__init__.py` (`detect_folder`, `detect_clip`).
- Documented JSON progress schema.
- Documented output filename convention.
- Keep config as plain dataclasses + YAML/TOML (no framework lock-in).
- Version the output schema; bump on breaking changes.

## Self-contained tool

SceneCutBatch is self-contained: it builds and runs alone, and other tools can
consume its documented API and schema when they choose to. There is no separate
"unified tool" and no designated consuming application.
