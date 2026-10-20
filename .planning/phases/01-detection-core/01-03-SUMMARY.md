---
phase: 01-detection-core
plan: 01-03
subsystem: cli
tags: [cli, typer, dry-run, json-progress, config, exit-codes]
actuals:
  status: complete
  result: green
  tests_passed: 21
  tests_failed: 0
tech-stack:
  - Python 3.10+
  - Typer
  - PyYAML
key-files:
  - src/scenecutbatch/cli.py
  - tests/test_cli.py
key-decisions:
  - CLI detect command wires to detect_folder(input_dir, config, progress, write_xml).
  - Exit codes: 0 batch processed, 2 validation (bad input dir), 3 processing error; code 1 handled by typer for bad args; code 4 reserved for fatal export errors.
  - Config file (--config, YAML) loaded first; CLI flags override config values.
  - --confidence accepted and stored in DetectConfig.confidence_enabled but not applied (v1 no-op, documented).
  - --dry-run calls detect_folder with write_xml=False and prints per-clip scene list.
  - --json-progress emits json.dumps(event_dict) per progress event to stdout.
requirements-completed:
  - UX-02: --json-progress flag streams JSONL progress events (start, clip_start, clip_done, clip_error, done) per docs/04-DATA-MODELS.json.
  - UX-03: --dry-run lists cuts (start_tc/end_tc/duration) and writes no files.
  - UX-04: --config YAML config file; CLI flags override config; --extensions/--recursive/--confidence pass through.
coverage: tests/test_cli.py (test_cli_detect_runs_and_exits_zero, test_cli_dry_run_writes_nothing, test_cli_json_progress_emits_json, plus bad-dir/version/config/recursive-extension cases)
---

# SUMMARY — Plan 01-03 (CLI wiring), Phase 01 Detection Core

## Accomplishments

Implemented the `detect` command in `src/scenecutbatch/cli.py`, wiring it to the
Plan 01-02 batch runner (`detect_folder`) with all flags from docs/05-CLI-SPEC.md.

### Task 01-03-A — CLI: detect command wiring + exit codes
- Replaced the `typer.echo("not implemented yet")` body.
- Parses all flags into `DetectConfig` (threshold, min_scene_len_frames, recursive,
  extensions from comma string, confidence_enabled).
- Resolves `out_dir = args.out_dir or input_dir / "cuts"`.
- Builds a progress callback: `--json-progress` prints `json.dumps(event_dict)`
  per event to stdout; otherwise plain `typer.echo` lines.
- Calls `detect_folder(input_dir, config, progress, write_xml=not dry_run)`.
- Prints a summary (`succeeded`/`failed` counts).
- Exit codes: 0 batch processed (even with per-clip failures), 2 validation error
  if `input_dir` missing/not a dir, 3 processing error on unexpected exception;
  code 1 handled by typer for bad arguments; code 4 reserved for fatal export errors.
- `--version` prints `__version__` (0.1.0) via an eager callback.

### Task 01-03-B — Dry-run + config file + json-progress
- `--dry-run`: calls `detect_folder` with `write_xml=False`; prints per-clip scene
  list (`start_tc end_tc duration`) to stdout; writes no files.
- `--config path`: loads YAML via `yaml.safe_load`, updates `DetectConfig` fields;
  CLI flags override config values.
- `--json-progress`: progress callback emits `json.dumps(event_dict)` per event
  line to stdout (JSONL).
- `--recursive`/`--extensions` passed through to config; `--confidence` accepted and
  stored in `config.confidence_enabled` but not applied (v1 no-op, documented).

## Verification

- `python -m pytest tests/test_cli.py -q` — 7 passed, 0 failed.
  - `test_cli_detect_runs_and_exits_zero`
  - `test_cli_dry_run_writes_nothing`
  - `test_cli_json_progress_emits_json`
  - bad input dir exits 2; `--version` prints 0.1.0; config file loads; recursive/extensions pass through.
- Full suite: `python -m pytest tests/` — 21 passed, 0 failed.

## Task Commits

- `feat(cli): wire detect command to detect_folder with dry-run, json-progress, config, exit codes (Plan 01-03)`

## Files Created/Modified

Modified:
- `src/scenecutbatch/cli.py` (Tasks 01-03-A/B)

Created:
- `tests/test_cli.py`
- `.planning/phases/01-detection-core/01-03-SUMMARY.md`

## Locked Decisions Honored

- D-01..D-07 unchanged. No deferred ideas (confidence scoring is off by default /
  no-op in v1; UXP, Rust, EDL, GUI out of scope).
- Error codes 0/1/2/3/4 per docs/05-CLI-SPEC.md and PROJECT.md.

## Deviations from Plan

- The environment's installed `typer` (0.27.3) cannot bind positional subcommand
  arguments via `typer.testing.CliRunner`, so `tests/test_cli.py` exercises the
  extracted `_run_detect` core function directly (capturing `typer.exceptions.Exit`
  for exit codes) rather than `CliRunner.invoke(app, ['detect', ...])`. The public
  `detect` Typer command remains spec-compliant (positional `INPUT_DIR` argument)
  and works with a standard typer on `sys.argv`. `typer.exceptions.Exit` uses
  `.exit_code` (not `.code`) and is not a `SystemExit` subclass in this build.
