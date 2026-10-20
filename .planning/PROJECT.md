# PROJECT.md — SceneCutBatch

## Project Reference

**Core Value**: Let an editor batch-detect scene cuts across hundreds of clips in
the background and import the results into Premiere as virtual subclips, instead
of running Premiere's slow one-clip-at-a-time Scene Edit Detection.

**Current Focus**: Pre-implementation. Documentation handoff complete; awaiting
`/gsd-plan-phase 1`.

## Problem

Adobe Premiere Pro's native "Scene Edit Detection" processes one clip at a time,
freezes the UI, and offers no batch mode. Editors with folders of 100+ clips
waste hours clicking through clips. A background tool that emits
Premiere-importable FCP7 XML with virtual subclips removes that bottleneck while
keeping the editor in full control of which subclips to use.

## Vision

A small, focused, local-first program (CLI first, optional GUI) that:

- Scans a folder of video files.
- Detects hard cuts per clip with PySceneDetect.
- Writes one FCP7 XML per clip (master sequence + virtual subclips, original
  media referenced, no duplication).
- Tags ambiguous detections with confidence markers for human review.
- Reports progress (per-clip, ETA) for long batches.
- Optionally auto-imports into Premiere via UXP/ExtendScript.

This program is developed independently now so it can be built and validated in
isolation, but its final destination is as a native tool **inside EsqueletoEdit**,
contributing to a useful, local, AI-assisted editing platform for real content
workflows.

## Constraints

- **Local-first**: no cloud, no telemetry, no network at runtime.
- **No media duplication**: subclips are virtual references only.
- **Non-destructive**: original media and Premiere project untouched until the
  editor imports.
- **Cross-platform**: Windows primary, macOS/Linux secondary (consistent with
  EsqueletoEdit).
- **Python 3.10+**, PySceneDetect with OpenCV backend.
- **License**: Apache-2.0.

## Out of Scope (v1)

- Script alignment / rough-cut generation (EsqueletoEdit's core job).
- Transcription, embeddings, matching.
- Soft-cut / dissolve detection (v2; ContentDetector hard cuts only in v1).
- Automatic selection of "best take" (editor decides).
- Premiere plugin auto-import (optional, v2; manual import is v1).
- Permanent separation from EsqueletoEdit (this is a future module of it).

## Success Criteria

1. Given a folder of N clips, the tool produces N valid FCP7 XML files that
   Premiere Pro imports without errors.
2. Each imported XML yields a bin with a master sequence (cuts in order) and
   virtual subclips pointing to original media.
3. Processing 100 clips completes without crashing; one bad clip does not abort
   the batch.
4. Progress is reportable per-clip with ETA.
5. Detection threshold and min scene length are configurable.
6. (Optional) Ambiguous detections are marked Green/Yellow/Red.

## Relationship to EsqueletoEdit

This project shares technology with EsqueletoEdit (Python, FCP7 XML, confidence
markers, progress reporting, Pinokio packaging) but has no runtime dependency on
it during independent development. See
`docs/09-INTEGRATION-TO-ESQUELETOEDIT.md` for the planned integration as a tool
inside EsqueletoEdit.
