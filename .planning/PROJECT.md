# PROJECT.md — SceneCutBatch

## Project Reference

**Core Value**: Let an editor batch-detect scene cuts across hundreds of clips in
the background and import the results into Premiere as virtual subclips, instead
of running Premiere's slow one-clip-at-a-time Scene Edit Detection.

**Current Focus**: Phase 03 (UI polish & public-facing presentation) complete —
bilingual GUI rework, editor-agnostic NLE terminology, public copy review, studio
signature across all public surfaces. Next: Phase 04 (Confidence scoring + markers).

## Problem

Adobe Premiere Pro's native "Scene Edit Detection" processes one clip at a time,
freezes the UI, and offers no batch mode. Editors with folders of 100+ clips
waste hours clicking through clips. A background tool that emits
FCP7 XML (xmeml) with virtual subclips, importable by professional video editors
(Premiere Pro, DaVinci Resolve and other NLEs that read FCP7 XML), removes that
bottleneck while keeping the editor in full control of which subclips to use.

## Vision

A small, focused, local-first program (CLI first, optional GUI) that:

- Scans a folder of video files.
- Detects hard cuts per clip with PySceneDetect.
- Writes one FCP7 XML per clip (master sequence + virtual subclips, original
  media referenced, no duplication).
- Tags ambiguous detections with confidence markers for human review.
- Reports progress (per-clip, ETA) for long batches.
- Optionally auto-imports into Premiere via UXP/ExtendScript.

This program is developed independently as a standalone, local-first tool that can
be built and validated in isolation. It is designed to be consumable by other
applications through its documented public API and JSON progress schema, without
any hard dependency on a host application.

## Constraints

- **Local-first**: no cloud, no telemetry, no network at runtime.
- **No media duplication**: subclips are virtual references only.
- **Non-destructive**: original media and Premiere project untouched until the
  editor imports.
- **Cross-platform**: Windows primary, macOS/Linux secondary.
- **Python 3.10+**, PySceneDetect with OpenCV backend.
- **License**: Apache-2.0.

## Out of Scope (v1)

- Script alignment / rough-cut generation.
- Transcription, embeddings, matching.
- Soft-cut / dissolve detection (v2; ContentDetector hard cuts only in v1).
- Automatic selection of "best take" (editor decides).
- Premiere plugin auto-import (optional, v2; manual import is v1).
- Permanent separation from EsqueletoEdit (this is a future module of it).

## Success Criteria

1. Given a folder of N clips, the tool produces N valid FCP7 XML files that
   professional video editors (Premiere Pro, DaVinci Resolve and other NLEs
   reading FCP7 XML) import without errors.
2. Each imported XML yields a bin with a master sequence (cuts in order) and
   virtual subclips pointing to original media.
3. Processing 100 clips completes without crashing; one bad clip does not abort
   the batch.
4. Progress is reportable per-clip with ETA.
5. Detection threshold and min scene length are configurable.
6. (Optional) Ambiguous detections are marked Green/Yellow/Red.

## Phase Learnings (from completed phases)

### Phase 03 — UI polish & public-facing presentation

**Decisions (D-31 through D-36):**
- D-31: GUI layout rework — logo relocated to horizontal header next to title, window sized 880×740 / minsize 820×700 so nothing clips at minsize
- D-32: Neutral NLE terminology — "FCP7 XML (xmeml) importable by professional video editors" replaces Premiere-exclusive claims
- D-33: Public copy review — internal-development references removed from all repository texts except `.planning/` (GSD working state)
- D-34: Cross-surface consistency — same canonical pitch across GUI, CLI, READMEs, pyproject.toml, and packaging metadata
- D-35: Bilingual GUI — en/es string catalog with OS auto-detection and in-app EN/ES switch; CLI stays Spanish-first
- D-36: Studio signature — "JMW Studio" credit on GUI, READMEs (per-language), CLI `--version` footer, and packaging metadata

**Key patterns established:**
- i18n string catalog (`src/scenecutbatch/i18n.py`) with `t()` lookups, stdlib-only
- Idempotent `_build_ui()` with container destroy-before-rebuild for language switching
- Widget reference retention (`logo_label.image`) across rebuilds to prevent GC
- Late-binding-safe lambdas in progress event logging (capture via default arg)

## Distribution Decisions

**D-37: Executable-only distribution (Windows).** The release artifact is the standalone `.exe`
produced by PyInstaller, not a `.zip` bundle. Pattern confirmed by sister project CosechaMedia
(v1.6.2 publishes `CosechaMedia-windows-x86_64.exe` as a raw 70 MB executable, no zip). The
`.exe` is self-contained (embeds Python interpreter, all dependencies, and the `assets/logo.png`
icon), so it runs by itself without any accompanying files. `run.bat` / `install.bat` are
convenience scripts only and are not required for execution. This avoids shipping redundant ZIPs
that duplicate what the `.exe` already contains. Each binary ships with a matching `.sha256`
checksum file for download verification.

**D-38: macOS installation via Homebrew tap.** macOS users install via the project's Homebrew
tap at `https://github.com/MustangXPress7/homebrew-tap` rather than downloading a standalone
`.app` bundle or `.zip`. No macOS binary is published as a release artifact. (CosechaMedia does
publish a `CosechaMedia-macos.app.zip` for reference, but this project opts for Homebrew-only
distribution on macOS.)

**D-39: Logo refresh.** `assets/logo.ico` regenerated from `assets/logo.png` (700×700 RGBA)
with embedded sizes 16, 32, 48, 64, 128, 256 px. The `.exe` embeds this icon for the Windows
taskbar/window titlebar.


## Relationship to Other Tools

This project shares technology patterns with other editing tools (Python, FCP7 XML,
confidence markers, progress reporting, Pinokio packaging) but has no runtime
dependency on any of them during independent development. It is a self-contained,
standalone application. See `docs/09-EXTENSIBILITY-AND-REUSE.md` for how other
tools can consume its documented API and schema.
