# Phase 01: Detection core - Research

**Researched:** 2026-10-20
**Domain:** Python video scene-cut detection, FCP7 XML (xmeml) generation, Typer CLI
**Confidence:** HIGH

## Summary

Phase 01 (Detection core) must deliver `detect_folder()` returning per-clip scene lists plus one `_cuts.xml` per clip (pulled forward from Phase 2 per D-06). The PySceneDetect API is stable in 0.6.x: `scenedetect.open_video(path)` returns a `VideoStream`; `SceneManager().add_detector(ContentDetector(threshold=27.0, min_scene_len=15))`; `scene_manager.detect_scenes(video)`; `scene_manager.get_scene_list()` returns `List[Tuple[FrameTimecode, FrameTimecode]]` [VERIFIED: scenedetect docs 0.6.1 API (scene_manager, detectors, frame_timecode, package)]. PyPI confirms latest 0.6.x release is 0.6.7.1 (Sep 2025); 0.7+ is a breaking change overhauling timestamps, so pin `scenedetect>=0.6.3,<0.7` together with OpenCV [VERIFIED: PyPI scenedetect release history]. ffprobe is treated as optional/graceful per D-07: probe via subprocess JSON, warn once if absent, proceed without fps/duration metadata [ASSUMED]. XML uses stdlib `xml.etree.ElementTree` building FCP7 xmeml v5 with a `<bin>`, master `<sequence>` and virtual `<clip>` subclips referencing original media via `file://localhost/` pathurl [CITED: Apple FCP7 XML Interchange Format docs]. Typer CLI follows the existing scaffold; progress is JSONL events per docs/04-DATA-MODELS.md [VERIFIED: repo docs].

**Primary recommendation:** Implement `detect_clip()` with `scenedetect.open_video` + `SceneManager` + `ContentDetector`, map `FrameTimecode` pairs to `Scene` dataclasses using `fractions.Fraction` frame math, wrap each clip in try/except for error isolation (D-03), pull `build_xml()` forward into Phase 1, and wire `detect_folder()` to write XML per clip. Pin `scenedetect[opencv]>=0.6.3,<0.7` and OpenCV together.

## Architectural Responsibility Map

| Capability | Primary Tier | Secondary Tier | Rationale |
|---|---|---|---|
| Recursive folder scan + extension filter | `media/scanner.py` | — | Already scaffolded; CUT-01, D-04 |
| Per-clip hard-cut detection | `detection/detector.py` | — | PySceneDetect ContentDetector wrapper; CUT-02..04, D-01 |
| Per-clip error isolation | `core/batch.py` | `detection/detector.py` | try/except per clip, never abort batch; D-03, CUT-05 |
| Frame-accurate timecode/frame math | `core/models.py` (Scene fields) | — | `fractions.Fraction`; D-02 |
| ffprobe metadata probing | `media/scanner.py` (`probe_media`) | — | Degraded gracefully; D-07 |
| FCP7 XML build (master sequence + subclips) | `export/xml_builder.py` | — | Pulled forward per D-06; OUT-01..04 |
| Batch orchestration + progress callback | `core/batch.py` | — | progress events index/total/name/ETA; UX-01..03 |
| CLI wiring (Typer) | `cli.py` | — | flags + exit codes; docs/05-CLI-SPEC.md |
| Config file (YAML) load | `cli.py` / new config module | — | UX-04 |

## User Constraints (from CONTEXT.md)

### Locked Decisions
- **D-01:** PySceneDetect ContentDetector, threshold 27.0 default, min scene length 15 frames — **Reversibility:** costly — these defaults shape every detection result downstream; changing them re-scores all scenes and invalidates any XML/golden files already produced.
- **D-02:** `fractions.Fraction` for frame math (exact/NTSC-safe) — **Reversibility:** costly — timecode/frame representations are baked into the `Scene` model and XML output; switching to float math introduces rounding drift across 100+ clips.
- **D-03:** Per-clip error isolation — never abort the batch on one bad/corrupt clip; record the error and continue — **Reversibility:** reversible — this is a local behavioral choice in the batch runner.
- **D-04:** Supported extensions mp4, mov, mxf, avi, mkv, webm (case-insensitive) — **Reversibility:** reversible — a config tuple, easy to extend.
- **D-05:** Output naming `{stem}_cuts.xml` written alongside input or to `--out-dir` — **Reversibility:** reversible — filename convention, no migration impact.
- **D-06:** Phase 1 produces scene lists AND writes one `_cuts.xml` per clip (master sequence + virtual subclips referencing original media) — pulling the XML builder forward from Phase 2 — **Reversibility:** costly — Phase 2 was scoped assuming XML starts there; pulling it forward changes Phase 2's remaining work to refinement/validation only.
- **D-07:** ffmpeg/ffprobe degrades gracefully — run without ffprobe metadata (fps/duration unknown), proceed with detection, warn once — **Reversibility:** reversible — ffprobe can be added later without changing detection logic.

### Locked from PROJECT.md / REQUIREMENTS.md / docs (not re-asked)
- Local-first, no cloud/telemetry/network at runtime
- Python 3.10+, Typer CLI, Apache-2.0
- No media duplication — virtual subclips reference original media only
- Confidence scoring off by default (v1.1 / Phase 4)
- Final home is EsqueletoEdit; this repo must build/run alone; clean public Python API (`detect_folder`, `detect_clip`)
- Error codes: 0 success, 1 usage, 2 validation, 3 processing, 4 export

### the agent's Discretion
- Reuse otio-fcp-adapter (EsqueletoEdit) vs. build xmeml directly (docs/10-DECISIONS.md open question)
- ffprobe via subprocess vs `ffmpeg-python` package (docs/03-TECH-STACK.md lists both)
- Where to place config-file loading (new module vs cli.py)

### Deferred Ideas (OUT OF SCOPE)
- Confidence scoring (G/Y/R markers in XML) — Phase 4 / v1.1, off by default (locked in docs/07-CONFIDENCE.md and docs/10-DECISIONS.md)
- Premiere UXP auto-import plugin — v2 (docs/10-DECISIONS.md)
- Rust acceleration for detection — v2, benchmark first (docs/10-DECISIONS.md)
- EDL export in addition to FCP XML — v1.1 optional (REQUIREMENTS.md OUT-06)
- GUI (Gradio) — v1.1 optional (docs/03-TECH-STACK.md)

## Phase Requirements

| ID | Description | Research Support |
|----|-------------|------------------|
| CUT-01 | Scan folder recursively, collect supported video files | scanner.py scaffolded (rglob/iterdir + ext filter) [VERIFIED: repo scanner.py] |
| CUT-02 | Detect hard scene cuts per clip using PySceneDetect ContentDetector | ContentDetector(threshold=27.0, min_scene_len=15), SceneManager.detect_scenes [VERIFIED: scenedetect docs 0.6.1] |
| CUT-03 | Default threshold 27.0; min scene length 15 frames; both configurable | DetectConfig defaults match; ContentDetector params [VERIFIED: repo models.py + scenedetect docs] |
| CUT-04 | Return per clip: list of scenes with start_tc, end_tc, duration, detection_score | FrameTimecode.get_frames/get_seconds/get_timecode; scene_score not directly exposed — use cut index as proxy or StatsManager [VERIFIED: scenedetect docs] |
| CUT-05 | One bad clip must NOT abort the batch; record error and continue | try/except in detect_clip; batch appends to failed list [VERIFIED: repo detector.py/batch.py scaffold] |
| OUT-01 | Write one FCP7 XML file per input clip | xmeml v5 structure [CITED: Apple FCP7 XML docs] |
| OUT-02 | Output filename: `<clip_stem>_cuts.xml` | DetectConfig.output_naming = "{stem}_cuts.xml" [VERIFIED: repo models.py] |
| OUT-03 | XML contains master sequence with all cuts in timeline order | docs/06-OUTPUT-FORMAT.md conceptual structure [VERIFIED: repo docs] |
| OUT-04 | XML contains virtual subclips referencing original media | pathurl file://localhost/ form [CITED: Apple FCP7 XML docs] |
| UX-01 | Report progress per clip (index/total, name, ETA) | JSON progress events per docs/04-DATA-MODELS.md [VERIFIED: repo docs] |
| UX-02 | CLI supports `--json-progress` | cli.py scaffold has flag [VERIFIED: repo cli.py] |
| UX-03 | Dry-run / preview mode lists cuts without writing files | cli.py scaffold has --dry-run [VERIFIED: repo cli.py] |
| UX-04 | Configurable via CLI flags and config file | pyyaml dependency; docs/05-CLI-SPEC.md [VERIFIED: repo pyproject+cli] |

## Standard Stack

### Core
| Library | Version | Purpose | Why Standard |
|---|---|---|---|
| scenedetect[opencv] | >=0.6.3,<0.7 | Hard cut detection via ContentDetector | Locked D-01; Classical CV, no ML deps; verified 0.6.x API stable [VERIFIED: PyPI + scenedetect docs] |
| opencv-python | bundled with scenedetect[opencv] | Video decoding backend | OpenCV VideoStreamCv2 is the production backend [VERIFIED: scenedetect docs backends] |
| fractions (stdlib) | Python 3.10+ | Exact rational frame math (NTSC-safe) | Locked D-02 [VERIFIED: repo docs] |
| xml.etree.ElementTree (stdlib) | Python 3.10+ | FCP7 xmeml XML generation | stdlib, full control over xmeml structure [VERIFIED: repo docs/03] |

### Supporting
| Library | Version | Purpose | When to Use |
|---|---|---|---|
| typer | >=0.12 | CLI command + flags | Locked stack; cli.py scaffold [VERIFIED: repo pyproject+cli] |
| rich | >=13.0 | Pretty progress output to stdout | Already a dependency; UX-01 progress display |
| pyyaml | >=6.0 | YAML config file loading | UX-04 config file support; already a dependency |
| ffprobe (ffmpeg binary) | system PATH or bundled | Probe fps/duration/size/codec | Optional per D-07; degrade gracefully if missing |

### Alternatives Considered
| Instead of | Could Use | Tradeoff |
|---|---|---|
| scenedetect[opencv] | scenedetect-headless | headless lacks OpenCV GUI but same detection; opencv chosen for video decoding |
| subprocess ffprobe | ffmpeg-python | subprocess avoids extra dep; D-07 makes ffprobe optional anyway |
| xml.etree.ElementTree | lxml | lxml faster but adds dependency; stdlib sufficient for xmeml |
| build xmeml directly | otio-fcp-adapter | adapter reuse open question (docs/10); direct build gives full control for virtual subclips |

**Installation:** `pip install scenedetect[opencv]>=0.6.3,<0.7 typer>=0.12 rich>=13.0 pyyaml>=6.0` (ffmpeg binary separately for ffprobe)
**Version verification:** `pip index versions scenedetect` — confirm <0.7; `pip show scenedetect opencv-python typer`

## Package Legitimacy Audit

| Package | Registry | Age | Downloads | Source Repo | Verdict | Disposition |
|---|---|---|---|---|---|---|
| scenedetect | PyPI | 0.6.x since 2022; 0.6.7.1 Sep 2025 | high (video CV niche) | github.com/Breakthrough/PySceneDetect | Approved | Pin >=0.6.3,<0.7 |
| opencv-python | PyPI | mature | very high | github.com/opencv/opencv | Approved | Bundled with scenedetect[opencv] |
| typer | PyPI | mature | very high | github.com/fastapi/typer | Approved | >=0.12 |
| rich | PyPI | mature | very high | github.com/Textualize/rich | Approved | >=13.0 |
| pyyaml | PyPI | mature | very high | github.com/yaml/pyyaml | Approved | >=6.0 |
| ffmpeg (ffprobe) | system/conda | mature | N/A | ffmpeg.org | Approved | Optional, D-07 graceful degrade |

## Architecture Patterns

### Recommended Project Structure
```
src/scenecutbatch/
├── __init__.py          # exposes detect_folder, detect_clip, models, __version__
├── cli.py               # Typer detect command + config loading + exit codes
├── core/
│   ├── models.py        # Scene, DetectionResult, DetectConfig, BatchResult (Fraction fps)
│   └── batch.py         # detect_folder: scan + per-clip detect + error isolation + XML write + progress
├── detection/
│   └── detector.py      # detect_clip: open_video + SceneManager + ContentDetector -> DetectionResult
├── media/
│   └── scanner.py       # scan_folder (recursive, ext filter) + probe_media (ffprobe, graceful)
├── export/
│   └── xml_builder.py   # build_xml (xmeml) + write_xml (master sequence + virtual subclips)
└── config.py            # (optional) YAML config file loader
tests/
├── test_smoke.py        # replaced with real Phase 1 tests
├── test_detector.py
├── test_batch.py
├── test_scanner.py
├── test_xml_builder.py
└── fixtures/            # tiny synthetic clips for offline tests
```

## Don't Hand-Roll

| Problem | Don't Build | Use Instead | Why |
|---|---|---|---|
| Cut detection algorithm | Custom frame-diff / HSV change detection | PySceneDetect ContentDetector | Locked D-01; proven classical CV [VERIFIED: scenedetect docs] |
| Video decoding | cv2.VideoCapture manual loop | scenedetect.open_video + SceneManager | Handles threading, backends, frame skipping [VERIFIED: scenedetect docs] |
| Frame/time math | float seconds | fractions.Fraction + FrameTimecode | Locked D-02; NTSC-safe exact rational [VERIFIED: repo docs + scenedetect docs] |
| FCP7 XML | Hand-written XML strings | xml.etree.ElementTree -> xmeml | stdlib, valid xmeml v5 structure [CITED: Apple FCP7 XML docs] |
| CLI parsing | argparse manual | Typer | Locked stack; existing scaffold [VERIFIED: repo cli.py] |
| Progress reporting | ad-hoc print statements | JSONL events per docs/04 schema | Consistent with EsqueletoEdit [VERIFIED: repo docs] |
| Config file | custom INI parser | pyyaml YAML loading | Already a dependency; UX-04 [VERIFIED: repo pyproject] |

## Common Pitfalls

### Pitfall 1: PySceneDetect 0.7 breaking API change
`scenedetect>=0.7` overhauls timestamp handling (VFR support) and is NOT compatible with 0.6.x code. Pin `<0.7`. Verification: `pip show scenedetect` must report 0.6.x; tests must import `from scenedetect import open_video, SceneManager, ContentDetector, FrameTimecode` and run against 0.6.x semantics (`get_scene_list()` returns FrameTimecode pairs).

### Pitfall 2: detection_score not directly exposed
PySceneDetect `get_scene_list()` returns start/end FrameTimecode pairs but does NOT expose the per-scene detection_score/content_val without a StatsManager. Requirement CUT-04 asks for `detection_score`. Options: (a) set `detection_score` to the cut frame index or a normalized proxy, (b) use StatsManager to read per-frame content_val. Prescribe: initialize `detection_score = 0.0` placeholder and document that real scores require StatsManager (deferred to confidence phase). Do not fabricate scores.

### Pitfall 3: One bad clip aborting the batch
`detect_clip` must wrap everything (open_video + detect_scenes + scene mapping) in try/except and set `result.error` with empty scenes. `detect_folder` must append to `batch.failed` and continue. Verification: include a corrupt/unsupported file in test fixtures; assert batch completes with `len(failed) >= 1` and `len(succeeded) + len(failed) == total`.

### Pitfall 4: FFprobe absence crashing detection
D-07: probe_media must catch FileNotFoundError/subprocess failure, log warning once, and return defaults (fps=Fraction(30,1), duration=0). Detection must proceed without fps; timecodes use detected video fps from OpenCV backend instead.

### Pitfall 5: XML pathurl format
Premiere requires `file://localhost/` + absolute path with forward slashes. On Windows, convert `C:\Footage\clip.mov` to `file://localhost/C:/Footage/clip.mov`. Verification: golden-file XML must contain `pathurl` with `file://localhost/` and forward slashes.

### Pitfall 6: `start_in_scene` default
`SceneManager.get_scene_list()` has `start_in_scene=False` default. With ContentDetector and no cuts found, returns empty list (no scenes). For a clip with no cuts, consider emitting one scene spanning the whole clip via `start_in_scene=True` so XML still has a master sequence + subclip. Decision: use `start_in_scene=True` so every clip produces at least one scene.

## Code Examples

**Detector core pattern (verified against scenedetect 0.6.1 API):**
```python
from fractions import Fraction
from pathlib import Path
from scenedetect import open_video, SceneManager, ContentDetector, FrameTimecode

from ..core.models import DetectionResult, Scene, DetectConfig

def detect_clip(video_path: Path, config: DetectConfig = None) -> DetectionResult:
    config = config or DetectConfig()
    result = DetectionResult(clip_path=Path(video_path))
    try:
        video = open_video(str(video_path))
        # video.get_framerate() available on VideoStream; fall back to Fraction(30,1)
        fps = Fraction(str(video.get_framerate())) if hasattr(video, "get_framerate") else Fraction(30, 1)
        result.fps = fps
        scene_manager = SceneManager()
        scene_manager.add_detector(ContentDetector(
            threshold=config.threshold,
            min_scene_len=config.min_scene_len_frames,
        ))
        scene_manager.detect_scenes(video, show_progress=False)
        scene_list = scene_manager.get_scene_list(start_in_scene=True)
        for i, (start_tc, end_tc) in enumerate(scene_list):
            start_frame = start_tc.get_frames()
            end_frame = end_tc.get_frames()
            start_sec = start_tc.get_seconds()
            end_sec = end_tc.get_seconds()
            result.scenes.append(Scene(
                index=i,
                start_frame=start_frame,
                end_frame=end_frame,
                start_time=start_sec,
                end_time=end_sec,
                start_tc=start_tc.get_timecode(),
                end_tc=end_tc.get_timecode(),
                duration_sec=end_sec - start_sec,
                detection_score=0.0,  # placeholder; real score needs StatsManager
            ))
    except Exception as exc:
        result.error = str(exc)
    return result
```

**Error isolation in batch runner:**
```python
for i, f in enumerate(files, 1):
    res = detect_clip(f, config)
    if res.error:
        batch.failed.append(res)
        if progress:
            progress(f"clip_error {i}/{len(files)} {f.name} {res.error}")
    else:
        batch.succeeded.append(res)
    # XML write here (Phase 1 per D-06)
```

**FCP7 xmeml skeleton (ElementTree):**
```xml
<?xml version="1.0" encoding="UTF-8"?>
<xmeml version="5">
  <bin>
    <name>{stem}</name>
    <children>
      <sequence id="seq_{stem}">
        <name>{stem}_master</name>
        <rate><timebase>{fps_den}</timebase><ntsc>{ntsc}</ntsc></rate>
        <media><video><track>
          <clipitem id="clip_0"><name>{stem}_scene_0</name><start>0</start><end>{frames}</end>...</clipitem>
        </track></video></media>
      </sequence>
      <clip id="subclip_0"><name>{stem}_scene_0</name><duration>{frames}</duration>...</clip>
    </children>
  </bin>
</xmeml>
```

## Environment Availability

| Dependency | Required By | Available | Version | Fallback |
|---|---|---|---|---|
| scenedetect[opencv] | detection/detector.py | To be installed | >=0.6.3,<0.7 | None (locked D-01) |
| opencv-python | scenedetect backend | Bundled with scenedetect[opencv] | — | scenedetect-headless (no OpenCV) |
| typer | cli.py | To be installed | >=0.12 | None (locked stack) |
| rich | cli.py progress | To be installed | >=13.0 | plain typer.echo |
| pyyaml | config file | To be installed | >=6.0 | TOML via tomllib (3.11+) |
| ffprobe (ffmpeg) | media/scanner.py probe_media | System PATH optional | — | graceful degrade per D-07 |
| pytest | tests | dev extra | >=8.0 | — |
| xml.etree.ElementTree | export/xml_builder.py | stdlib | 3.10+ | lxml |

## Validation Architecture

### Test Framework
| Property | Value |
|---|---|
| Framework | pytest |
| Config file | pyproject.toml `[tool.pytest.ini_options]` |
| Quick run command | `pytest tests/ -x` |
| Full suite command | `pytest tests/` |

### Phase Requirements → Test Map
| Req ID | Behavior | Test Type | Automated Command | File Exists? |
|---|---|---|---|---|
| CUT-01 | scan_folder recursive + ext filter | unit | `pytest tests/test_scanner.py -x` | No (create) |
| CUT-02 | detect_clip runs ContentDetector, returns scenes | unit (synthetic clip) | `pytest tests/test_detector.py -x` | No (create) |
| CUT-03 | threshold/min_scene_len configurable defaults | unit | `pytest tests/test_models.py -x` | Partial (test_smoke) |
| CUT-04 | Scene has start_tc, end_tc, duration, detection_score | unit | `pytest tests/test_detector.py -x` | No (create) |
| CUT-05 | corrupt clip recorded in failed, batch continues | unit | `pytest tests/test_batch.py -x` | No (create) |
| OUT-01 | write_xml produces file | unit | `pytest tests/test_xml_builder.py -x` | No (create) |
| OUT-02 | filename `{stem}_cuts.xml` | unit | `pytest tests/test_xml_builder.py -x` | No (create) |
| OUT-03 | XML has master sequence + cuts in order | unit/golden | `pytest tests/test_xml_builder.py -x` | No (create) |
| OUT-04 | XML has virtual subclips + pathurl | unit/golden | `pytest tests/test_xml_builder.py -x` | No (create) |
| UX-01 | progress callback invoked per clip | unit | `pytest tests/test_batch.py -x` | No (create) |
| UX-02 | `--json-progress` flag accepted | CLI | `pytest tests/test_cli.py -x` | No (create) |
| UX-03 | `--dry-run` lists cuts, writes nothing | CLI | `pytest tests/test_cli.py -x` | No (create) |
| UX-04 | config file loads threshold/min_scene_len | unit | `pytest tests/test_config.py -x` | No (create) |

### Sampling Rate
- Per task commit: `pytest tests/ -x`
- Per wave merge: `pytest tests/`
- Phase gate: Full suite green before `/gsd-verify-work`

### Wave 0 Gaps
- [ ] No synthetic test clips exist (need tiny MP4/MOV fixtures or mock open_video)
- [ ] test_smoke.py will be replaced with real Phase 1 tests
- [ ] ffprobe not installed in environment — tests must mock probe_media

## Security Domain

### Applicable ASVS Categories
| ASVS Category | Applies | Standard Control |
|---|---|---|
| V5 Input Validation | yes | Validate input_dir exists and is a directory; validate extensions are safe (no path traversal via `..`); sanitize clip stem used in XML id/name attributes |
| V7 Error Handling | yes | Per-clip error isolation; never leak stack traces to stdout; log exceptions, record error strings |
| V14 Configuration | yes | Config file loaded only from explicit `--config` path; no arbitrary file read |

## Open Questions

1. Should `probe_media` use subprocess ffprobe directly or add `ffmpeg-python`? (D-07 makes it optional; subprocess is zero-extra-dep.) (RESOLVED: subprocess ffprobe directly, zero-extra-dep; `probe_media` stays NotImplementedError in Phase 1 and degrades gracefully per D-07.)
2. `detection_score` — PySceneDetect doesn't expose per-scene score without StatsManager. Use 0.0 placeholder now, or integrate StatsManager in Phase 1? (Prescribe: placeholder, defer real scoring to confidence phase.) (RESOLVED: `detection_score` = 0.0 placeholder in Phase 1; real scoring deferred to confidence phase via StatsManager.)
3. Reuse otio-fcp-adapter for xmeml or build directly with ElementTree? (Direct build prescribed for full virtual-subclip control; revisit in Phase 2.) (RESOLVED: build xmeml directly with stdlib ElementTree in Phase 1; revisit otio-fcp-adapter in Phase 2.)
4. `start_in_scene=True` means every clip yields ≥1 scene even with zero cuts — confirm this matches editor expectations. (RESOLVED: confirmed; `get_scene_list(start_in_scene=True)` used so every clip yields ≥1 scene.)
5. Output dir default: `INPUT_DIR/cuts` (current batch.py scaffold) vs alongside input? (Docs/05 says `INPUT_DIR/cuts`; keep scaffold default.) (RESOLVED: output dir defaults to `INPUT_DIR/cuts`, per docs/05 and the batch.py scaffold.)

## Sources

### Primary (HIGH confidence)
- scenedetect 0.6.1 API docs: https://www.scenedetect.com/docs/0.6.1/api.html (SceneManager, ContentDetector, FrameTimecode, detect/open_video) [VERIFIED]
- scenedetect detectors 0.6.1: https://www.scenedetect.com/docs/0.6.1/api/detectors.html [VERIFIED]
- scenedetect scene_manager 0.6.1: https://www.scenedetect.com/docs/0.6.1/api/scene_manager.html [VERIFIED]
- scenedetect frame_timecode 0.6.1: https://www.scenedetect.com/docs/0.6.1/api/frame_timecode.html [VERIFIED]
- PyPI scenedetect release history: https://pypi.org/project/scenedetect/ [VERIFIED — latest 0.6.x = 0.6.7.1; 0.7 is breaking]
- Apple Final Cut Pro 7 XML Interchange Format: https://developer.apple.com/library/archive/documentation/AppleApplications/Reference/FinalCutPro_XML/Elements/Elements.html [CITED]
- Repo docs: docs/02-ARCHITECTURE.md, docs/03-TECH-STACK.md, docs/04-DATA-MODELS.md, docs/05-CLI-SPEC.md, docs/06-OUTPUT-FORMAT.md, docs/10-DECISIONS.md [VERIFIED: read from disk]
- Repo CONTEXT.md/REQUIREMENTS.md/STATE.md [VERIFIED: read from disk]
- Repo source scaffold: src/scenecutbatch/*.py [VERIFIED: read from disk]

### Secondary (MEDIUM confidence)
- Typer docs: https://typer.tiangolo.com/ [CITED]
- ffprobe docs: https://ffmpeg.org/ffprobe.html [CITED]

### Tertiary (LOW confidence)
- Vultr PySceneDetect tutorial (2026) — general usage, version-agnostic [ASSUMED]
- markdown-it / third-party FCP7 XML guides [ASSUMED]

## Metadata

**Confidence breakdown:**
- PySceneDetect 0.6.x API: HIGH (verified against official docs)
- ffprobe graceful degrade: MEDIUM (D-07 decision; implementation pattern assumed)
- FCP7 xmeml structure: HIGH (Apple docs + repo docs)
- Typer CLI patterns: HIGH (repo scaffold + Typer docs)
- detection_score availability: MEDIUM (scenedetect docs confirm not directly exposed without StatsManager)

**Research date:** 2026-10-20
**Researcher:** gsd-phase-researcher
**Consumer:** gsd-planner (produces PLAN.md for Phase 01)