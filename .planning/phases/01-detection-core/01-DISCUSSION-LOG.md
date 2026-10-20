# Phase 01: Detection core - Discussion Log

> **Audit trail only.** Do not use as input to planning, research, or execution agents.
> Decisions are captured in CONTEXT.md — this log preserves the alternatives considered.

**Date:** 2026-10-20
**Phase:** 01-Detection core
**Areas discussed:** Phase 1 deliverable scope, ffmpeg/ffprobe handling

---

## Initial gray areas presented (redirected)

The agent presented four technical gray areas (media validation depth, progress callback contract, synthetic test clips, timecode source of truth). The user redirected, noting the tool is simpler — detect cuts, produce folders of cuts — and asked for a simplified discussion rather than the full technical surface.

## Phase 1 deliverable scope

| Option | Description | Selected |
|--------|-------------|----------|
| A — Scene lists only | `detect_folder()` returns per-clip scene lists via JSON progress/stdout. No XML files. XML stays in Phase 2. | |
| B — Scene lists + cuts XML | Phase 1 also writes one `_cuts.xml` per clip (master sequence + virtual subclips referencing original media), pulling the XML builder forward from Phase 2. | ✓ |

**User's choice:** B — scene lists + cuts XML. Usable folders of cuts immediately; Phase 2 becomes XML refinement/validation.
**Notes:** None.

## ffmpeg/ffprobe handling

| Option | Description | Selected |
|--------|-------------|----------|
| A — Required on PATH | Fail early with a clear message if ffprobe isn't on PATH. | |
| B — Degrade gracefully | Run without ffprobe metadata (fps/duration unknown), proceed with detection, warn once. | ✓ |

**User's choice:** B — degrade gracefully. Works out of the box with just PySceneDetect/OpenCV; ffprobe metadata added later when available.
**Notes:** None.

## the agent's Discretion

None — the user made explicit choices on both areas discussed.

## Deferred Ideas

None raised during discussion beyond the already-locked deferred items in CONTEXT.md (confidence scoring, Premiere UXP plugin, Rust acceleration, EDL export, GUI).
