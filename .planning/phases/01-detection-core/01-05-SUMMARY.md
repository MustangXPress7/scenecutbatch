---
phase: 01-detection-core
plan: 01-05
subsystem: tests
tags: [tests, batch, cli, integration, mock]
actuals:
  status: complete
  result: green
  tests_passed: 22
  tests_failed: 0
tech-stack:
  - Python 3.11
  - pytest 9.1.1
  - PySceneDetect 0.6.7.1 (mocked)
  - Typer
key-files:
  - tests/test_batch.py
  - tests/test_cli.py
  - src/scenecutbatch/cli.py
requirements-completed:
  - CUT-01: scan_folder collects clips (exercised via batch).
  - CUT-03: threshold/min_scene_len configurable; config file honored.
  - CUT-05: bad clip never aborts batch; recorded in failed.
  - UX-01: per-clip progress with ETA (clip_start/clip_done/eta_sec>=0).
  - UX-02: --json-progress emits valid JSONL events.
  - UX-03: --dry-run lists cuts, writes nothing.
  - UX-04: config file overrides threshold; CLI flags override config.
verification:
  - python -m pytest tests/test_batch.py -q — 3 passed
  - python -m pytest tests/test_cli.py -q — 7 passed
  - python -m pytest tests/ -q — 22 passed, 0 failed
---

# SUMMARY — Plan 01-05 (Detection core — batch + CLI integration tests), Phase 01 Detection Core

## Accomplishments

### Task 01-05-A — Batch integration tests (tests/test_batch.py)
Rewrote test_batch.py to mock `detect_clip` (no real video files, no ffprobe).

- `test_detect_folder_error_isolation`: one good clip + one bad/unreadable file → `BatchResult(total=2, succeeded=1, failed=1)`, no exception raised; `{stem}_cuts.xml` written only for the good clip. Confirms CUT-05 / D-03 error isolation.
- `test_detect_folder_progress_eta`: captures progress callback events; asserts `clip_start`/`clip_done`/`clip_error`/`done` received; each `clip_done` dict has `event,index,total,clip,scenes,status,eta_sec` with `eta_sec>=0`. Confirms UX-01.
- `test_detect_folder_writes_xml_per_clip`: output dir contains `{stem}_cuts.xml` for each succeeded clip. Confirms OUT-01/OUT-02.

### Task 01-05-B — CLI integration tests (tests/test_cli.py)
Rewrote test_cli.py using `_run_detect` with `detect_clip` mocked.

- `test_cli_detect_runs_and_exits_zero`: exit 0, "Batch done:", "1 succeeded".
- `test_cli_bad_input_dir_exit_2`: nonexistent input dir → exit code 2.
- `test_cli_version_prints_0_1_0`: `--version` prints "0.1.0".
- `test_cli_dry_run_writes_nothing`: `--dry-run` lists cuts to stdout, no `_cuts.xml` created.
- `test_cli_json_progress_emits_json`: `--json-progress` — every stdout line is valid JSON with `event` field; `start`/`clip_start`/`clip_done`/`done` present.
- `test_cli_config_file_overrides_threshold`: tmp yaml config with `threshold: 35.0`, detector called with `threshold == 35.0`.
- `test_cli_cli_threshold_overrides_config`: explicit CLI `--threshold 55.0` overrides config `42.0`.

### Production change
`src/scenecutbatch/cli.py`: `--threshold`/`--min-scene-len` now use `None` sentinel defaults and only override config values when explicitly provided, so config-file threshold is honored (UX-04) while explicit CLI flags still win.

## Verification
- `python -m pytest tests/test_batch.py -q` — 3 passed
- `python -m pytest tests/test_cli.py -q` — 7 passed
- `python -m pytest tests/ -q` — 22 passed, 0 failed

## Locked Decisions Honored
- D-01..D-07 unchanged. Tests mock scenedetect; no real video, no ffprobe.
- Error codes 0/1/2/3/4 per docs/05-CLI-SPEC.md.
- No deferred ideas.

## Deviations from Plan
- None.
