# Phase 02: Scene Cut Batch - Context

**Gathered:** 2026-10-20
**Status:** Ready for planning

<domain>
## Phase Boundary

Phase 2 delivers the launch-ready, multi-platform distribution of Scene Cut Batch: public GitHub repository, installation scripts for Windows/macOS/Linux, Linux native packaging (AppImage), project branding ("Scene Cut Batch" with mixer/grinder logo), and cross-platform verification.
</domain>

<decisions>
## Implementation Decisions

### D-21: Project name
- **D-21:** "Scene Cut Batch" (with space, not "SceneCutBatch") — **Reversibility:** costly — changes name in all metadata, READMEs, code and communication.

### D-22: Logo
- **D-22:** Logo = drawing of meat grinder/cutter machine with pieces coming out (image provided by user) — **Reversibility:** costly — it is the primary visual identity of the project.

### D-23: Linux packaging
- **D-23:** Native Linux packaging in **AppImage** format — **Reversibility:** costly — AppImage is portable and does not require system installation.

### D-24: Reference seeds
- **D-24a:** **TransNetV2** — https://github.com/soCzech/TransNetV2 — deep learning scene-cut detection architecture, reference for future.
- **D-24b:** **OmniShotCut** — https://github.com/UVA-Computer-Vision-Lab/OmniShotCut — shot-based cut detection, reference for future.
- **Reversibility:** reversible — these are external references, not direct dependencies.

### D-25: Repository
- **D-25:** Public GitHub at https://github.com/MustangXPress7/scenecutbatch — **Reversibility:** costly — it is the official home of the project.

### Locked from PROJECT.md / docs (not re-asked)
- Local-first, no cloud/telemetry/network at runtime
- Python 3.10+, Typer CLI, Apache-2.0
- No media duplication — virtual subclips reference original media only
- Final home inside EsqueletoEdit; this repo must build/run alone
- Error codes: 0 success, 1 usage, 2 validation, 3 processing, 4 export

### Deferred Ideas
- Advanced GUI (beyond simple one)
- Direct Premiere auto-import plugin
- Rust acceleration
- EDL export
</decisions>

<canonical_refs>
## Canonical References

Downstream agents MUST read these before planning or implementing.

### Roadmap & requirements
- `.planning/ROADMAP.md` — Phase 2 goal and key deliverable
- `.planning/REQUIREMENTS.md` — updated requirements for Phase 2
- `.planning/PROJECT.md` — project value and constraints
- `.planning/STATE.md` — current project state

### External references
- `https://github.com/MustangXPress7/scenecutbatch` — GitHub repository (target)
- `https://github.com/soCzech/TransNetV2` — TransNetV2, reference architecture for scene-cut detection (seed/inspiration)
- `https://github.com/UVA-Computer-Vision-Lab/OmniShotCut` — OmniShotCut, shot-based cut detection reference
- `docs/02-ARCHITECTURE.md` — system architecture
- `docs/03-TECH-STACK.md` — tech stack
- `docs/05-CLI-SPEC.md` — CLI specification

### Integration
- `docs/09-INTEGRATION-TO-ESQUELETOEDIT.md` — final home inside EsqueletoEdit
</canonical_refs>

<code_context>
## Existing Code Insights

### Reusable Assets
- `src/scenecutbatch/cli.py` — Typer CLI already implemented
- `src/scenecutbatch/core/batch.py` — detect_folder batch runner
- `src/scenecutbatch/detection/detector.py` — PySceneDetect wrapper
- `src/scenecutbatch/export/xml_builder.py` — FCP7 XML builder (updated for Premiere compatibility)
- `src/scenecutbatch/media/scanner.py` — folder scanner
- `src/scenecutbatch/gui.py` — Tkinter GUI
- `src/scenecutbatch/core/models.py` — data models
- `src/scenecutbatch/__init__.py` — package init
- `pyproject.toml` — project metadata
- `install.bat`, `run.bat` — Windows installer/launcher
- `install.sh`, `run_mac.sh` — Mac/Linux installer/launcher
- `SceneCutBatch.command` — Mac double-click launcher
- `scenecutbatch.spec` — PyInstaller spec file

### Established Patterns
- Dataclass-based config passed explicitly
- Detector as pure function (video_path, params) → DetectionResult
- XML builder as pure function → str
- All I/O at CLI/batch edges
- JSON progress events

### Integration Points
- `detect_folder()` public API feeds EsqueletoEdit's media grouper
- XML output is Premiere-importable FCP7 (xmeml)
</code_context>

<specifics>
## Specific Ideas

Logo is the hand-drawn mixer/grinder drawing provided by the user (machine cuts scene into pieces). Save as `assets/logo.png` or `assets/logo.svg`.
</specifics>

<deferred>
## Deferred Ideas

- Windows .exe installer (Inno Setup) — later
- macOS .app / .dmg — later
- Premiere auto-import plugin — v2
- Rust acceleration — v2
- EDL export — v2
</deferred>