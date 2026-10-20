# ROADMAP.md — SceneCutBatch

## Phases

| Phase | Goal | Key Deliverable |
|-------|------|-----------------|
| 1 | Detection core (PySceneDetect wrapper + batch runner + error isolation) | `detect_folder()` returns per-clip scene lists |
| 2 | FCP7 XML output (master sequence + virtual subclips) | Premiere-importable XML per clip |
| 3 | CLI + progress reporting + config | `scenecutbatch` CLI with flags |
| 4 | Confidence scoring + markers (optional) | G/Y/R markers in XML |
| 5 | Packaging (Pinokio + binary) | One-click install + standalone binary |
| 6 | Integration API + docs for unified tool | Reusable Python API + schema docs |

## Phase details

### Phase 1 — Detection core
- Wrap PySceneDetect ContentDetector.
- Media scanning (reuse EsqueletoEdit patterns): supported extensions, ffprobe metadata.
- Batch runner with per-clip error isolation and progress callback.
- Unit tests with small synthetic clips.

### Phase 2 — FCP7 XML output
- Build master sequence + virtual subclips referencing original media.
- Validate import in Premiere (manual smoke test).
- Golden-file tests.

### Phase 3 — CLI + progress
- Typer CLI consistent with EsqueletoEdit.
- `--json-progress`, `--out-dir`, `--threshold`, `--min-scene-len`, `--dry-run`.
- Config file support.

### Phase 4 — Confidence
- Per-scene score + G/Y/R mapping.
- Embed markers in XML.

### Phase 5 — Packaging
- Pinokio recipe, Nuitka/PyInstaller binary.

### Phase 6 — Integration
- Clean Python API, schema docs, integration guide for unified tool.
