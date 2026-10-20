---
phase: 01-detection-core
plan: 01-02
subsystem: detection-core
tags: [batch, error-isolation, progress, eta, xml]
actuals:
  status: complete
  result: green
  tests_passed: 2
  tests_failed: 0
tech-stack:
  - Python 3.10+
  - PySceneDetect 0.6.7.1 (pinned <0.7)
  - fractions.Fraction
  - xml.etree.ElementTree
  - pytest
key-files:
  - src/scenecutbatch/core/batch.py
  - tests/test_batch.py
key-decisions:
  - D-03: per-clip error isolation — detect_folder appends bad clips to failed and continues, never aborts the batch.
  - Progress events are JSON-serializable dicts matching docs/04-DATA-MODELS.md schema (start, clip_start, clip_done, clip_error, done).
  - ETA = running-average seconds-per-clip * remaining clips (eta_sec >= 0).
  - write_xml parameter shadows the imported builder function; imported as `_write_xml`.
requirements-completed:
  - CUT-01: files sourced via scan_folder (recursive + case-insensitive ext filter).
  - CUT-05: one bad/corrupt clip recorded in failed, batch continues, no exception.
  - UX-01: per-clip progress with index/total/name/scenes/status/eta_sec.
coverage: tests/test_batch.py (test_detect_folder_error_isolation, test_progress_eta_shape)
---

# SUMMARY — Plan 01-02 (Batch runner), Phase 01 Detection Core

## Accomplishments

Implemented `detect_folder(input_dir, config=None, progress=None, write_xml=True) -> BatchResult` in
`src/scenecutbatch/core/batch.py`, replacing the Phase 1/Phase 2 TODO scaffold.

- **Task 01-02-A (Batch runner + error isolation):**
  - `config = config or DetectConfig()`; `input_dir = Path(input_dir)`; `out_dir = input_dir / "cuts"`.
  - `files = scan_folder(input_dir, config)` (CUT-01 recursive + ext filter via scanner).
  - `batch = BatchResult(input_dir, output_dir=out_dir, total=len(files))`; `started_at = _now()`.
  - Loops `enumerate(files, 1)`; emits `clip_start` progress per clip; calls `detect_clip(f, config)`.
  - On `res.error`: appends to `batch.failed` and emits `clip_error` — never aborts (CUT-05, D-03).
  - On success: appends to `batch.succeeded`; if `write_xml`, writes `out_dir / f"{stem}_cuts.xml"` via
    `xml_builder.write_xml` (D-05/D-06, XML builder already in place from 01-01); emits `clip_done`.
  - `finished_at = _now()`; emits `done`; returns batch. Kept `_now()` helper.
- **Task 01-02-B (Progress ETA + per-clip timing):**
  - Tracks `res.processing_time_sec` per clip; running average seconds-per-clip; `ETA = avg * remaining clips`.
  - `clip_done` event is a JSON-serializable dict: `event, index, total, clip, scenes, status, eta_sec`
    (matches docs/04-DATA-MODELS.json schema); `eta_sec >= 0`.
  - Dry-run handling deferred to CLI plan 01-03.

## Verification

- `python -m pytest tests/test_batch.py::test_detect_folder_error_isolation -q` — passes.
  One good clip + one unreadable `.mp4` → `BatchResult(total=2, succeeded=1, failed=1)`, no exception,
  `good_clip_cuts.xml` written for the good clip only, progress receives clip_start/clip_done/clip_error/done.
- `python -m pytest tests/test_batch.py::test_progress_eta_shape -q` — passes.
  `clip_done` events are JSON-serializable dicts with the required fields; `eta_sec >= 0`, decreasing to 0.
- Full suite: `pytest tests/` → 14 passed, 0 failed.

## Task Commits

- `feat(batch): detect_folder with per-clip error isolation + ETA progress (Task 01-02-A/B)`

## Files Created/Modified

Modified:
- `src/scenecutbatch/core/batch.py` (Task 01-02-A/B)

Created:
- `tests/test_batch.py`
- `.planning/phases/01-detection-core/01-02-SUMMARY.md`

## Deviations from Plan

- Progress events are JSON dicts (not plain strings as the scaffold hinted), required by Task B's
  done-criteria and the docs/04-DATA-MODELS.json schema; applied consistently to start/clip_start/clip_done/clip_error/done.

## Locked Decisions Honored

- D-03 per-clip error isolation (critical for this plan); D-01/D-02/D-04/D-05/D-06/D-07 unchanged from 01-01.
- No deferred ideas (confidence scoring, UXP, Rust, EDL, GUI).
