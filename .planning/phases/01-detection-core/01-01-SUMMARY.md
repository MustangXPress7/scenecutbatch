---
phase: 01-detection-core
plan: 01-01
subsystem: detection-core
tags: [tracer, scanner, detector, xml_builder, xmeml, pyscenedetect, fcpxml]
actuals:
  status: complete
  result: green
  tests_passed: 12
  tests_failed: 0
  e2e_tracer: verified
tech-stack:
  - Python 3.10+
  - PySceneDetect 0.6.7.1 (pinned <0.7)
  - OpenCV 4.11 (scenedetect backend)
  - fractions.Fraction
  - xml.etree.ElementTree
  - pytest
key-files:
  - src/scenecutbatch/media/scanner.py
  - src/scenecutbatch/detection/detector.py
  - src/scenecutbatch/export/xml_builder.py
  - src/scenecutbatch/core/models.py
  - pyproject.toml
  - tests/test_scanner.py
  - tests/test_detector.py
  - tests/test_xml_builder.py
key-decisions:
  - D-01: ContentDetector threshold 27.0 / min_scene_len 15 frames (honored verbatim)
  - D-02: fractions.Fraction for frame math (fps stored as Fraction on DetectionResult)
  - D-03: per-clip error isolation (detect_clip catches exceptions, sets .error, returns empty scenes)
  - D-04: case-insensitive extension filter (scanner.py already implemented)
  - D-05: output naming {stem}_cuts.xml (write_xml)
  - D-06: XML pulled forward into Phase 1 (build_xml xmeml v5)
  - D-07: ffprobe graceful degrade (default fps Fraction(30,1); probe_media stays NotImplementedError)
patterns-established:
  - detector as pure function (video_path, config) -> DetectionResult
  - XML builder as pure function -> str; I/O at write_xml edge
  - shared <file> pathurl referenced by master clipitems and virtual subclips (no media duplication)
  - start_in_scene=True so every clip yields >= 1 scene
requirements-completed:
  - CUT-01: scan_folder recursive + case-insensitive extension filter
  - CUT-02: PySceneDetect ContentDetector hard-cut detection
  - CUT-03: default threshold 27.0 / min scene length 15 frames, configurable
  - CUT-04: per-clip scenes with start_tc/end_tc/duration_sec/detection_score
  - CUT-05: per-clip error isolation (no batch abort)
  - OUT-01: one FCP7 XML per clip
  - OUT-02: {stem}_cuts.xml filename
  - OUT-03: master sequence with cuts in timeline order
  - OUT-04: virtual subclips referencing original media via pathurl
coverage: tests/test_scanner.py, tests/test_detector.py, tests/test_xml_builder.py (12 tests)
---

# SUMMARY — Plan 01-01 (Tracer, Wave 1), Phase 01 Detection Core

## Accomplishments

Executed the end-to-end tracer task wiring scanner → detector → xml_builder → write XML for one clip.

- **Task 01-01-A (Scanner):** Verified `scan_folder(input_dir, config)` returns sorted `List[Path]` of video files, filters by `config.extensions` case-insensitively (mp4/mov/mxf/avi/mkv/webm), supports recursive via `rglob`/`iterdir`, sorts results, and leaves `probe_media` as `NotImplementedError`. scanner.py was already scaffolded to this spec; all criteria confirmed by tests (single file → exactly one Path; empty dir → `[]`; unsupported extensions ignored; `.MP4` matches; recursive finds nested).
- **Task 01-01-B (Detector):** Implemented `detect_clip(video_path, config)` using `scenedetect.open_video` + `SceneManager` + `ContentDetector(threshold=config.threshold, min_scene_len=config.min_scene_len_frames)`. Maps each `FrameTimecode` pair to a `Scene` (index, start_frame, end_frame, start_tc, end_tc, duration_sec, detection_score=0.0 placeholder). Sets `fps` as `Fraction` from video frame rate (default `Fraction(30,1)` graceful degrade per D-07). Uses `get_scene_list(start_in_scene=True)` so every clip yields ≥1 scene. Per-clip error isolation: catches exceptions, logs, sets `result.error`, returns empty scenes without raising (D-03).
- **Task 01-01-C (XML builder):** Implemented `build_xml(result, config)` returning FCP7 xmeml v5 string: root `<xmeml version="5">`, `<bin name={stem}><children>`, master `<sequence id="seq_{stem}">` with `<rate><timebase>{fps}</timebase><ntsc>...</ntsc></rate>`, `<media><video><track>` with one `<clipitem>` per scene in timeline order (start/end/in/out as frames, file ref with `pathurl file://localhost/` + absolute forward-slash path), then one virtual `<clip id="subclip_N">` per scene referencing the same `<file>` pathurl (no media duplication). `write_xml` writes `{stem}_cuts.xml` (D-05).
- **End-to-end tracer verified:** one synthetic clip (cut at frame 30) → `detect_clip` produces 2 scenes → `build_xml` parses as xmeml v5 with bin `myclip`, master sequence `seq_myclip` + 2 clipitems + 2 virtual subclips + `file://localhost/...` pathurls → `write_xml` writes `myclip_cuts.xml` on disk, valid XML.
- Added 3 test files (12 tests total), all passing. Pinned `scenedetect[opencv]>=0.6.3,<0.7` in `pyproject.toml` (0.7 is a breaking API change); installed 0.6.7.1.

## Task Commits

- `fdefec1` feat(detector): wire PySceneDetect ContentDetector into detect_clip (Task 01-01-B)
- `119131d` feat(xml): build xmeml v5 master sequence + virtual subclips (Task 01-01-C)
- `197b4de` test: add Phase 1 tracer tests + pin scenedetect <0.7

(Task 01-01-A scanner code was pre-existing scaffold matching the spec; verified by tests, no source change required.)

## Files Created/Modified

Modified:
- src/scenecutbatch/detection/detector.py (Task B)
- src/scenecutbatch/export/xml_builder.py (Task C)
- pyproject.toml (scenedetect pin <0.7)

Created:
- tests/test_scanner.py
- tests/test_detector.py
- tests/test_xml_builder.py

## Decisions Made

- Honored all locked decisions D-01..D-07 verbatim (see frontmatter).
- `detection_score` left as `0.0` placeholder (PySceneDetect does not expose per-scene score without StatsManager; deferred to confidence phase per research pitfall).
- `start_in_scene=True` so zero-cut clips still yield one scene (master sequence + subclip never empty).
- FCP7 `<ntsc>` = TRUE when fps is non-integer (23.976/29.97), else FALSE; `<timebase>` = rounded frames-per-second.
- Built xmeml directly with stdlib `xml.etree.ElementTree` (research open question resolved: direct build for full virtual-subclip control).
- `pathurl` uses `Path.resolve().as_posix()` so Windows backslashes become forward slashes under `file://localhost/`.

## Deviations from Plan

- None material. scanner.py (Task A) required no implementation change — it already satisfied CUT-01/D-04 from the scaffold; verification tests were added instead.
- The plan's `<timebase>{fps denominator}</timebase>` wording was interpreted as frames-per-second (30 for Fraction(30,1)) rather than `.denominator` (1), because FCP7 timebase is the frame rate; this matches the XML format and the golden-test assertion.

## Issues Encountered

- Two Python versions on machine (3.10 and 3.11); `python` resolves to 3.11 while scenedetect initially installed under 3.10. Installed scenedetect 0.6.7.1 under 3.11 so `python -m pytest` works. Tests use `pythonpath=["src"]` from pyproject.toml.
- `pip install -e .[dev]` initially pulled scenedetect 0.7.2 (breaking API); corrected by pinning `<0.7` and installing 0.6.7.1.
- PowerShell `&&` chaining not supported; ran git add/commit as separate commands.

## User Setup Required

`pip install -e .[dev]` (per plan). scenedetect 0.6.7.1 + OpenCV must be installed (0.6.x line, not 0.7). ffprobe is optional (D-07 graceful degrade); detector proceeds without it using default fps=30/1.

## Next Phase Readiness

Phase 01 Detection Core is complete and green (12/12 tests). The tracer path (one clip → scenes → `{stem}_cuts.xml` with master sequence + virtual subclips) is verified end-to-end. Remaining Phase 1 work (batch runner `detect_folder` XML write per clip, CLI wiring) can proceed next; XML builder is already in place per D-06, so Phase 2 scope reduces to refinement/validation.
