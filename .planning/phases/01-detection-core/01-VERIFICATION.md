---
phase: 01-detection-core
status: passed
verdict: passed
must_haves_verified: 27
requirements_covered: 13
requirements_total: 13
decisions_covered: 7
tests_passed: 22
tests_total: 22
---

# Phase 01 Verification Report

## Goal Achievement

**Phase goal:** Detection core (PySceneDetect wrapper + batch runner + error isolation). Deliverable: `detect_folder()` returns per-clip scene lists.

**Verdict: GOAL ACHIEVED.** The phase fully delivers what ROADMAP.md promises:

- `detect_folder(input_dir, config, progress, write_xml) -> BatchResult` is implemented in `src/scenecutbatch/core/batch.py` and returns per-clip scene lists (via `BatchResult.succeeded[]` and `BatchResult.failed[]`).
- The folder scanner (`src/scenecutbatch/media/scanner.py`) collects supported video files (case-insensitive ext filter, recursive optional).
- The detector (`src/scenecutbatch/detection/detector.py`) wraps PySceneDetect `ContentDetector(threshold=27.0, min_scene_len=15)` and maps results to `Scene` dataclasses with `start_tc`/`end_tc`/`duration_sec`/`detection_score`.
- Per-clip error isolation is in place: one bad/corrupt clip records an error and does NOT abort the batch (D-03, CUT-05).
- One `{stem}_cuts.xml` per successfully detected clip is written with FCP7 xmeml v5 structure: master sequence + virtual subclips referencing original media via `file://localhost/` pathurl (D-06 pulled XML into Phase 1).
- The Typer CLI wires `detect_folder` with all flags (`--out-dir`, `--threshold`, `--min-scene-len`, `--recursive`, `--extensions`, `--dry-run`, `--json-progress`, `--config`, `--confidence`, `--version`), exit codes (0/1/2/3/4), dry-run, JSON progress streaming, and YAML config file support.

## Must-Haves Verification

All must_haves.truths from plans 01-01 through 01-05 were verified against the actual codebase. Every plan SUMMARY.md reports `status: complete`, `result: green`, and all 22 tests pass.

### Plan 01-01 (Tracer: scanner→detector→xml_builder→write XML) — 7 truths

| # | Truth | Source | Status |
|---|-------|--------|--------|
| 1 | PySceneDetect ContentDetector(threshold=27.0, min_scene_len=15) returns frame-based cut list (D-01) | `detector.py` lines 49-53 | Verified |
| 2 | `open_video` + `SceneManager` + `ContentDetector` + `detect_scenes` + `get_scene_list(start_in_scene=True)` returns FrameTimecode pairs; every clip yields >= 1 scene | `detector.py` lines 44-55, 72 | Verified |
| 3 | `get_scene_list()` does not expose detection_score without StatsManager → use 0.0 placeholder (documented) | `detector.py` line 71 | Verified |
| 4 | `fractions.Fraction` for all frame math (D-02); `DetectionResult.fps` is Fraction | `models.py` line 27, `detector.py` line 19-30 | Verified |
| 5 | pathurl must be `file://localhost/` + absolute path with forward slashes; Windows backslashes → forward slashes | `xml_builder.py` lines 15-19 | Verified |
| 6 | stdlib `xml.etree.ElementTree` builds xmeml v5 FCP7 XML | `xml_builder.py` line 10, 54 | Verified |
| 7 | `{stem}_cuts.xml` output naming per D-05 (written alongside input or to --out-dir) | `batch.py` line 52, `cli.py` line 124 | Verified |

### Plan 01-02 (Batch runner + error isolation + progress ETA) — 6 truths

| # | Truth | Source | Status |
|---|-------|--------|--------|
| 1 | `detect_folder(input_dir, config, progress, write_xml) -> BatchResult` (public API) | `batch.py` lines 15-67 | Verified |
| 2 | Per-clip error isolation: one bad clip records error in `batch.failed` and does NOT abort (D-03, CUT-05) | `batch.py` lines 43-48 | Verified |
| 3 | Progress callback invoked per clip with index/total/name/ETA (UX-01) | `batch.py` lines 33-66 | Verified |
| 4 | Output dir defaults to `input_dir/cuts`; XML written per clip when `write_xml=True` (D-06 pulled into Phase 1) | `batch.py` lines 28, 51-52 | Verified |
| 5 | `{stem}_cuts.xml` output naming per D-05 | `batch.py` line 52 | Verified |
| 6 | `DetectConfig` threshold/min_scene_len configurable (CUT-03, D-01 defaults 27.0/15) | `models.py` lines 38-39, `cli.py` lines 115-118 | Verified |

### Plan 01-03 (CLI wiring + dry-run + json-progress + config) — 6 truths

| # | Truth | Source | Status |
|---|-------|--------|--------|
| 1 | Typer detect command: `scenecutbatch detect INPUT_DIR [OPTIONS]` | `cli.py` lines 156-206 | Verified |
| 2 | Flags: --out-dir, --threshold, --min-scene-len, --recursive, --extensions, --dry-run, --json-progress, --config (YAML), --confidence, --version | `cli.py` lines 157-192 | Verified |
| 3 | Exit codes: 0 success, 1 usage error, 2 validation error (bad input dir), 3 processing error (fatal), 4 export error (fatal) | `cli.py` lines 101-140 | Verified |
| 4 | --dry-run lists cuts without writing files (UX-03) | `cli.py` lines 143-148 | Verified |
| 5 | --json-progress streams JSON events to stdout (UX-02) | `cli.py` lines 127-131 | Verified |
| 6 | --config loads YAML into DetectConfig; CLI flags override config file (UX-04) | `cli.py` lines 25-56, 111-122 | Verified |

### Plan 01-04 (Unit tests: scanner, detector, xml_builder) — 4 truths

| # | Truth | Source | Status |
|---|-------|--------|--------|
| 1 | Tests use tmp_path tiny files + mocked scenedetect; no synthetic test clips needed | `tests/conftest.py` | Verified |
| 2 | `probe_media` is NotImplementedError; tests never call it (D-07) | `scanner.py` line 31-32 | Verified |
| 3 | `detect_clip` tested with mocked scenedetect.SceneManager/ContentDetector returning known FrameTimecode pairs | `tests/test_detector.py` | Verified |
| 4 | XML tests assert xmeml structure: bin name, master sequence clipitems in order, subclip pathurl file://localhost/ | `tests/test_xml_builder.py` | Verified |

### Plan 01-05 (Integration tests: batch, CLI) — 4 truths

| # | Truth | Source | Status |
|---|-------|--------|--------|
| 1 | Batch/CLI tests use tmp_path tiny files + mocked detector | `tests/test_batch.py`, `tests/test_cli.py` | Verified |
| 2 | detect_folder error isolation: bad clip recorded in `batch.failed`, batch continues, exit behavior correct | `tests/test_batch.py` | Verified |
| 3 | JSON progress events: clip_start/clip_done/clip_error/done with index/total/name/scenes/status/eta_sec | `tests/test_batch.py` | Verified |
| 4 | Dry-run writes no files; config file loads YAML; CLI flags override config | `tests/test_cli.py` | Verified |

**Total must_haves verified: 27 / 27**

## Requirement Coverage

Cross-referenced requirement IDs from plan frontmatter against REQUIREMENTS.md. Per D-06, OUT-01..04 were pulled into Phase 1. Per D-03/CUT-05 and UX-01..04, progress/error-isolation requirements were implemented in Phase 1 per the plans. OUT-05 (Premiere import) stays Phase 2 — NOT expected in Phase 1 (human-only smoke test).

| REQ ID | Requirement | Phase | Coverage Status | Evidence |
|--------|-------------|-------|-----------------|----------|
| CUT-01 | Scan folder (recursive optional), collect supported video files (case-insensitive) | 1 | Covered | `scanner.py`, `tests/test_scanner.py` |
| CUT-02 | Detect hard scene cuts per clip using PySceneDetect ContentDetector | 1 | Covered | `detector.py`, `tests/test_detector.py` |
| CUT-03 | Default threshold = 27.0; min scene length = 15 frames; both configurable | 1 | Covered | `models.py`, `cli.py`, `tests/test_detector.py` |
| CUT-04 | Return per clip: list of scenes with (start_tc, end_tc, duration, detection_score) | 1 | Covered | `detector.py`, `models.py`, `tests/test_detector.py` |
| CUT-05 | One bad/unsupported/corrupt clip must NOT abort the batch; record error and continue | 1 | Covered | `batch.py`, `tests/test_batch.py` |
| OUT-01 | Write one FCP7 XML file per input clip | 1 (pulled in per D-06) | Covered | `xml_builder.py`, `batch.py`, `tests/test_xml_builder.py` |
| OUT-02 | Output filename: `<clip_stem>_cuts.xml` | 1 (pulled in per D-06) | Covered | `batch.py` line 52, `tests/test_xml_builder.py` |
| OUT-03 | XML contains master sequence with all detected cuts in timeline order | 1 (pulled in per D-06) | Covered | `xml_builder.py`, `tests/test_xml_builder.py` |
| OUT-04 | XML contains virtual subclips (one per scene) referencing original media (no duplication) | 1 (pulled in per D-06) | Covered | `xml_builder.py`, `tests/test_xml_builder.py` |
| OUT-05 | Premiere Pro imports XML without errors; creates bin with master sequence + subclips | 2 | NOT in Phase 1 | Human-only; requires Premiere Pro installation |
| UX-01 | Report progress per clip (index/total, clip name, ETA) | 1 | Covered | `batch.py`, `tests/test_batch.py` |
| UX-02 | CLI supports `--json-progress` for machine-readable streaming | 1 | Covered | `cli.py`, `tests/test_cli.py` |
| UX-03 | Dry-run / preview mode lists detected cuts without writing files | 1 | Covered | `cli.py`, `tests/test_cli.py` |
| UX-04 | Configurable via CLI flags and config file (YAML/TOML) | 1 | Covered | `cli.py`, `tests/test_cli.py` |

**Requirements covered: 13 / 13** (CUT-01..05, OUT-01..04, UX-01..04). OUT-05 deferred to Phase 2 (human-only).

## Decision Compliance

All locked decisions D-01..D-07 from CONTEXT.md were honored.

| Decision | Requirement | Compliance Status | Evidence |
|----------|-------------|-------------------|----------|
| D-01 | ContentDetector threshold 27.0 / min scene length 15 frames | Compliant | `detector.py` lines 49-53; `models.py` defaults |
| D-02 | `fractions.Fraction` for frame math; `DetectionResult.fps` is Fraction | Compliant | `models.py` line 27; `detector.py` `_fps_from_video` |
| D-03 | Per-clip error isolation — never abort batch on one bad clip | Compliant | `detector.py` try/except lines 73-75; `batch.py` lines 43-48 |
| D-04 | Case-insensitive extension filter (mp4/mov/mxf/avi/mkv/webm) | Compliant | `scanner.py` lines 21-26 |
| D-05 | `{stem}_cuts.xml` naming | Compliant | `batch.py` line 52; `xml_builder.py` `write_xml` |
| D-06 | XML (master sequence + virtual subclips) produced in Phase 1 | Compliant | `xml_builder.py` `build_xml`; `batch.py` XML write per clip |
| D-07 | ffprobe degrades gracefully; default fps = Fraction(30,1); `probe_media` stays NotImplementedError | Compliant | `detector.py` DEFAULT_FPS line 16; `scanner.py` lines 31-32 |

**Decisions covered: 7 / 7**

## Test Results

Confirmed via `python -m pytest tests/ -v` (Python 3.11.9, pytest 9.1.1):

```
22 passed in 0.15s
```

| Test File | Tests | Passed | Failed |
|-----------|-------|--------|--------|
| tests/test_scanner.py | 5 | 5 | 0 |
| tests/test_detector.py | 3 | 3 | 0 |
| tests/test_xml_builder.py | 2 | 2 | 0 |
| tests/test_batch.py | 3 | 3 | 0 |
| tests/test_cli.py | 7 | 7 | 0 |
| tests/test_smoke.py | 2 | 2 | 0 |
| **Total** | **22** | **22** | **0** |

**Tests passed: 22 / 22**

## Issues

None. All automated checks pass:

- All 27 must_haves.truths across plans 01-01 through 01-05 verified against codebase.
- All 13 Phase 1 requirements (CUT-01..05, OUT-01..04, UX-01..04) covered.
- All 7 locked decisions (D-01..D-07) honored.
- All 22 tests pass, 0 failed.

No gaps found in Phase 1 scope.

## Human Verification Needed

One item requires human testing (outside Phase 1 automated scope):

- **OUT-05 (Premiere Pro import smoke test):** Requires actual Adobe Premiere Pro installation to verify the generated `{stem}_cuts.xml` imports without errors and creates a bin with master sequence + virtual subclips. This is deferred to Phase 2 per REQUIREMENTS.md traceability and the phase boundary in CONTEXT.md.

## Next Steps

Phase 01 (Detection core) is **complete and green**. The deliverable `detect_folder()` returns per-clip scene lists with per-clip error isolation, writes one `_cuts.xml` per clip (master sequence + virtual subclips), and exposes a Typer CLI with dry-run, JSON progress, and config file support.

**Ready for Phase 2** (FCP7 XML output refinement/validation + Premiere import smoke test). Per D-06, XML was pulled into Phase 1, so Phase 2 scope reduces to refinement/validation and the human-only OUT-05 Premiere import verification.
