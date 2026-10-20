# Phase 01: Detection core - Context

**Gathered:** 2026-10-20
**Status:** Ready for planning

<domain>
## Phase Boundary

Phase 1 delivers the detection core: a PySceneDetect ContentDetector wrapper that scans a folder of video clips, detects hard cuts per clip with per-clip error isolation (one bad clip never aborts the batch), and writes one `_cuts.xml` per clip with a master sequence + virtual subclips referencing the original media (no media duplication). Returns per-clip scene lists via `detect_folder()` with JSON progress reporting.

</domain>

<decisions>
## Implementation Decisions

### Detection approach
- **D-01:** PySceneDetect ContentDetector, threshold 27.0 default, min scene length 15 frames — **Reversibility:** costly — these defaults shape every detection result downstream; changing them re-scores all scenes and invalidates any XML/golden files already produced.
- **D-02:** `fractions.Fraction` for frame math (exact/NTSC-safe) — **Reversibility:** costly — timecode/frame representations are baked into the `Scene` model and XML output; switching to float math introduces rounding drift across 100+ clips.
- **D-03:** Per-clip error isolation — never abort the batch on one bad/corrupt clip; record the error and continue — **Reversibility:** reversible — this is a local behavioral choice in the batch runner.
- **D-04:** Supported extensions mp4, mov, mxf, avi, mkv, webm (case-insensitive) — **Reversibility:** reversible — a config tuple, easy to extend.
- **D-05:** Output naming `{stem}_cuts.xml` written alongside input or to `--out-dir` — **Reversibility:** reversible — filename convention, no migration impact.

### Phase 1 deliverable scope (discussed in this session)
- **D-06:** Phase 1 produces scene lists AND writes one `_cuts.xml` per clip (master sequence + virtual subclips referencing original media) — pulling the XML builder forward from Phase 2 — **Reversibility:** costly — Phase 2 was scoped assuming XML starts there; pulling it forward changes Phase 2's remaining work to refinement/validation only.
- **D-07:** ffmpeg/ffprobe degrades gracefully — run without ffprobe metadata (fps/duration unknown), proceed with detection, warn once — **Reversibility:** reversible — ffprobe can be added later without changing detection logic.

### Locked from PROJECT.md / REQUIREMENTS.md / docs (not re-asked)
- Local-first, no cloud/telemetry/network at runtime
- Python 3.10+, Typer CLI, Apache-2.0
- No media duplication — virtual subclips reference original media only
- Confidence scoring off by default (v1.1 / Phase 4)
- Final home is EsqueletoEdit; this repo must build/run alone; clean public Python API (`detect_folder`, `detect_clip`)
- Error codes: 0 success, 1 usage, 2 validation, 3 processing, 4 export

</decisions>

<canonical_refs>
## Canonical References

Downstream agents MUST read these before planning or implementing.

### Roadmap & requirements
- `.planning/ROADMAP.md` — Phase 1 goal and key deliverable ("detect_folder() returns per-clip scene lists")
- `.planning/REQUIREMENTS.md` — CUT-01..05 (detection), OUT-01..05 (output), UX-01..04 (progress & UX); success criteria
- `.planning/PROJECT.md` — project value, constraints, success criteria, relationship to EsqueletoEdit
- `.planning/STATE.md` — current project state (pre-implementation)

### Specs & decisions
- `docs/02-ARCHITECTURE.md` — components (media scanner, detector, batch runner, XML builder, confidence scorer, CLI) and data flow; design rules (no global mutable state, pure functions, I/O at edges)
- `docs/03-TECH-STACK.md` — Python 3.10+, PySceneDetect 0.6.x, OpenCV, ffprobe, fractions.Fraction, stdlib xml.etree.ElementTree or lxml, Typer, pytest
- `docs/04-DATA-MODELS.md` — Scene, DetectionResult, BatchResult, DetectConfig dataclasses; JSON progress schema
- `docs/05-CLI-SPEC.md` — `scenecutbatch detect INPUT_DIR` command, flags (--out-dir, --threshold, --min-scene-len, --recursive, --extensions, --dry-run, --json-progress, --config, --confidence, --version), exit codes
- `docs/06-OUTPUT-FORMAT.md` — FCP7 XML (xmeml) structure: bin, master sequence, virtual subclips, pathurl form, frame-accurate rational timebase, markers for confidence
- `docs/07-CONFIDENCE.md` — G/Y/R thresholds (GREEN ≥0.85, YELLOW 0.60-0.84, RED <0.60); off by default in v1
- `docs/10-DECISIONS.md` — locked decisions D1-D11; open questions for the implementing agent

### Integration
- `docs/09-INTEGRATION-TO-ESQUELETOEDIT.md` — final home inside EsqueletoEdit; integration rules (no hard dep, clean API, documented JSON progress schema)

</canonical_refs>

<code_context>
## Existing Code Insights

### Reusable Assets
- `src/scenecutbatch/core/models.py` — Scene, DetectionResult, DetectConfig, BatchResult dataclasses already scaffolded (matches docs/04-DATA-MODELS.md)
- `src/scenecutbatch/media/scanner.py` — `scan_folder(input_dir, config)` filters by extension (case-insensitive), supports recursive; `probe_media(path)` is `NotImplementedError` (ffprobe not yet wired)
- `src/scenecutbatch/detection/detector.py` — `detect_clip(video_path, config)` scaffolded; currently returns `error = "not implemented yet"`; needs PySceneDetect ContentDetector wiring
- `src/scenecutbatch/core/batch.py` — `detect_folder(input_dir, config, progress, write_xml)` scaffolded; iterates clips, calls detector, collects BatchResult; XML write is a Phase 2 TODO (now moved to Phase 1 per D-06)
- `src/scenecutbatch/export/xml_builder.py` — `build_xml(result)` raises `NotImplementedError`; `write_xml(result, output_path)` writes file; needs xmeml implementation (moved to Phase 1 per D-06)
- `src/scenecutbatch/cli.py` — Typer `detect` command scaffolded with all CLI flags from docs/05-CLI-SPEC.md; body is `typer.echo("not implemented yet")`
- `src/scenecutbatch/__init__.py` — exposes `detect_folder`, `detect_clip`, models, `__version__ = "0.1.0"`
- `tests/test_smoke.py` — tests `__version__`, `DetectConfig` defaults, `scan_folder` empty dir; Phase 1 will replace with real tests
- `pyproject.toml` — dependencies (scenedetect[opencv]>=0.6.3, typer>=0.12, rich>=13.0, pyyaml>=6.0), entry point `scenecutbatch = scenecutbatch.cli:main`, pytest config

### Established Patterns
- Dataclass-based config passed explicitly (no global mutable state) — per ARCHITECTURE design rules
- Detector as pure function of (video_path, params) → DetectionResult
- XML builder as pure function → str; all I/O at CLI/batch edges
- JSON progress events (start, clip_start, clip_done, clip_error, done) per docs/04-DATA-MODELS.md
- Error isolation per clip — catch exceptions, record error, continue

### Integration Points
- `detect_folder()` public API feeds EsqueletoEdit's media grouper and rough-cut flow (docs/09)
- XML output is Premiere-importable FCP7 (xmeml) for virtual subclip workflow

</code_context>

<specifics>
## Specific Ideas

No specific requirements beyond the locked decisions — open to standard approaches for implementing the detector, scanner ffprobe integration, and XML builder.

</specifics>

<deferred>
## Deferred Ideas

- Confidence scoring (G/Y/R markers in XML) — Phase 4 / v1.1, off by default (locked in docs/07-CONFIDENCE.md and docs/10-DECISIONS.md)
- Premiere UXP auto-import plugin — v2 (docs/10-DECISIONS.md)
- Rust acceleration for detection — v2, benchmark first (docs/10-DECISIONS.md)
- EDL export in addition to FCP XML — v1.1 optional (REQUIREMENTS.md OUT-06)
- GUI (Gradio) — v1.1 optional (docs/03-TECH-STACK.md)

</deferred>

---

*Phase: 01-Detection core*
*Context gathered: 2026-10-20*
