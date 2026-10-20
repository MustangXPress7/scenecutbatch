# 09 — Integration into EsqueletoEdit (final home)

## Vision

EsqueletoEdit IS the unified tool. SceneCutBatch is being built independently now
so it can be validated in isolation, but it will eventually become a native tool
inside EsqueletoEdit — batch cut detection for Premiere takes, available as part
of the same local AI editing platform for real content workflows.

## Reusable assets to share later

- Media scanner (extensions, ffprobe probing, validation).
- FCP7 XML writer (virtual subclips).
- Progress reporting schema (JSON events).
- Pinokio recipe + Nuitka build scripts.
- Confidence marker conventions (G/Y/R thresholds, hex colors).
- CLI conventions (Typer, exit codes, `--json-progress`).

## Integration points (planned)

1. **As a library inside EsqueletoEdit**: `esqueletoedit.tools.scenecutbatch` or
   similar, exposing `detect_folder(...)` / `detect_clip(...)`. The returned
   `DetectionResult` feeds into EsqueletoEdit's media grouper and rough-cut flow.
2. **As a menu/tool step**: A "Prep takes / Batch cut detection" entry in
   EsqueletoEdit's GUI runs SceneCutBatch over the footage folder and produces
   Premiere-importable XMLs the editor can import.
3. **Shared packaging**: Single Pinokio recipe installing EsqueletoEdit with the
   SceneCutBatch tool included; single binary.

## Rules to keep integration cheap

- No hard dependency on EsqueletoEdit (this repo must build/run alone).
- Public Python API in `scenecutbatch/__init__.py` (`detect_folder`, `detect_clip`).
- Documented JSON progress schema.
- Documented output filename convention.
- Keep config as plain dataclasses + YAML/TOML (no framework lock-in).
- Version the output schema; bump on breaking changes.

## Unified tool = EsqueletoEdit

There is no separate "unified tool" planned. EsqueletoEdit is the destination.
SceneCutBatch becomes one more capability inside it, alongside script parsing,
transcription, alignment, confidence scoring, and export.
