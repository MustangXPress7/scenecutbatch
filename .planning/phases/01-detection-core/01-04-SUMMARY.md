---
phase: 01-detection-core
plan: 01-04
subsystem: tests
tags: [tests, scanner, detector, xml_builder, conftest, mock]
actuals:
  status: complete
  result: green
  tests_passed: 21
  tests_failed: 0
tech-stack:
  - Python 3.10+
  - pytest
  - PySceneDetect 0.6.x
key-files:
  - tests/conftest.py
  - tests/test_scanner.py
  - tests/test_detector.py
  - tests/test_xml_builder.py
  - tests/test_smoke.py
key-decisions:
  - scenedetect (open_video/SceneManager/ContentDetector) is monkeypatched in tests; no real video files or ffprobe needed.
  - detect_clip bad-file test uses real scenedetect so open_video raises OSError, exercising per-clip error isolation (D-03).
  - FrameTimecode pairs returned by mocked get_scene_list map to Scene dataclasses; detection_score stays 0.0 placeholder.
requirements-completed:
  - CUT-01: scan_folder recursive + extension filter (case-insensitive).
  - CUT-02: detect_clip returns scenes via mocked ContentDetector.
  - CUT-04: Scene has start_tc/end_tc/duration_sec/detection_score.
  - OUT-01: write_xml produces file on disk.
  - OUT-02: {stem}_cuts.xml naming.
  - OUT-03: master sequence with clipitems in timeline order.
  - OUT-04: virtual subclips + pathurl file://localhost/ + abs forward-slash path.
coverage: tests/test_scanner.py (5), tests/test_detector.py (3), tests/test_xml_builder.py (2), tests/test_smoke.py (2)
---

# SUMMARY — Plan 01-04 (Detection core unit tests), Phase 01 Detection Core

## Accomplishments

Implemented unit tests for the scanner, detector, and XML builder, plus the shared
conftest.py fixtures. All tests mock scenedetect where needed — no real video files,
no ffprobe.

### Task 01-04-A — conftest + scanner unit tests
- Created tests/conftest.py with fixtures: tmp_input_dir, config (DetectConfig defaults),
  mocked_scenedetect (monkeypatches scenedetect.open_video/SceneManager/ContentDetector
  to return fixed FrameTimecode pairs).
- Rewrote tests/test_scanner.py: test_scan_folder_empty, test_scan_folder_single_file,
  test_scan_folder_case_insensitive, test_scan_folder_ignores_unsupported,
  test_scan_folder_recursive. Uses tmp_path + tiny empty files with supported/
  unsupported extensions.
- Trimmed tests/test_smoke.py (removed duplicated test_scan_folder_empty).

### Task 01-04-B — Detector unit tests (mocked scenedetect)
- Rewrote tests/test_detector.py:
  - test_detect_clip_returns_scenes: >= 1 Scene, start_tc/end_tc/duration_sec populated,
    detection_score == 0.0 placeholder.
  - test_detect_clip_bad_file_error_isolation: nonexistent path -> error set, empty
    scenes, no exception raised (real scenedetect raises OSError, caught by D-03).
  - test_detect_clip_config_defaults: threshold 27.0 and min_scene_len 15 forwarded to
    ContentDetector (assert via mock call args).

### Task 01-04-C — XML builder unit tests
- Rewrote tests/test_xml_builder.py:
  - test_build_xml_contains_master_and_subclips: 2 scenes; root xmeml version 5, bin
    name = clip stem, master sequence has 2 clipitems in order, subclips present,
    each pathurl starts with file://localhost/ and contains absolute forward-slash path.
  - test_write_xml_writes_file: write_xml creates {stem}_cuts.xml on disk, parses.

## Verification

- python -m pytest tests/test_scanner.py -q — 5 passed
- python -m pytest tests/test_detector.py -q — 3 passed
- python -m pytest tests/test_xml_builder.py -q — 2 passed
- Full suite: python -m pytest tests/ — 21 passed, 0 failed

## Task Commits

- feat(tests): conftest fixtures + scanner unit tests (Plan 01-04-A)
- feat(tests): detector unit tests with mocked scenedetect (Plan 01-04-B)
- feat(tests): xml_builder unit tests (Plan 01-04-C)
- docs: add 01-04-SUMMARY.md (Plan 01-04)

## Locked Decisions Honored

- D-01..D-07 unchanged. probe_media stays NotImplementedError (D-07); tests never call it.
- No deferred ideas.
- Error codes 0/1/2/3/4 per docs/05-CLI-SPEC.md and PROJECT.md.

## Deviations from Plan

- test_detect_clip_bad_file_error_isolation uses real (unmocked) scenedetect rather than
  mocked_scenedetect, because the mock makes open_video always succeed and therefore
  cannot produce a file-not-found error. Real scenedetect raises OSError on a missing
  file, which detect_clip's try/except (D-03) catches — exactly the error isolation
  the test is meant to confirm.
