# SceneCutBatch (working name)

> Batch scene-cut detection for Adobe Premiere Pro — generates FCP7 XML files with
> virtual subclips so an editor can review and pick takes without re-encoding or
> duplicating media.

**Status:** Pre-implementation. Documented handoff for a separate AI agent to build.
**License:** Apache-2.0 (consistent with EsqueletoEdit)
**Parent ecosystem:** EsqueletoEdit (local AI editing platform). This module is
being developed as an *independent program* first so it can be built and validated
in isolation, with the clear intent of being integrated later as a native tool
*inside* EsqueletoEdit (batch cut detection for Premiere takes).

---

## What this is

A small, focused, local-first CLI (and optional GUI) that:

1. Takes a folder of video clips.
2. For each clip, runs **PySceneDetect** (ContentDetector, threshold 27.0 default)
   to find hard cuts.
3. Emits **one FCP7 XML file per clip** that Premiere Pro can import directly.
4. Each XML creates a bin containing:
   - a **master sequence** with all detected cuts in order, and
   - **virtual subclips** pointing at the original media (no duplication).
5. Optionally tags ambiguous/short scenes with confidence markers (Green/Yellow/Red)
   so the editor knows what to double-check.

The point is to replace Premiere's slow, one-clip-at-a-time "Scene Edit Detection"
with a background batch job over hundreds of clips.

## What this is NOT

- Not a rough-cut / script-alignment engine (that is EsqueletoEdit's core).
- Not a transcriber or matcher.
- Not a cloud service. Everything runs locally.
- Not a permanent separate product: it will become a tool inside EsqueletoEdit.


## Quick links

- [`docs/01-REQUIREMENTS.md`](docs/01-REQUIREMENTS.md) — REQ-IDs and acceptance criteria
- [`docs/02-ARCHITECTURE.md`](docs/02-ARCHITECTURE.md) — components and data flow
- [`docs/03-TECH-STACK.md`](docs/03-TECH-STACK.md) — dependencies and versions
- [`docs/04-DATA-MODELS.md`](docs/04-DATA-MODELS.md) — core data structures
- [`docs/05-CLI-SPEC.md`](docs/05-CLI-SPEC.md) — command-line interface
- [`docs/06-OUTPUT-FORMAT.md`](docs/06-OUTPUT-FORMAT.md) — FCP7 XML layout
- [`docs/07-CONFIDENCE.md`](docs/07-CONFIDENCE.md) — G/Y/R tagging
- [`docs/08-ROADMAP.md`](docs/08-ROADMAP.md) — phases to implement
- [`docs/09-INTEGRATION-TO-ESQUELETOEDIT.md`](docs/09-INTEGRATION-TO-ESQUELETOEDIT.md) — integration into EsqueletoEdit
- [`docs/10-DECISIONS.md`](docs/10-DECISIONS.md) — locked decisions

GSD planning artifacts live under [`.planning/`](.planning/) so an agent can run
`/gsd-plan-phase 1`, `/gsd-execute-phase 1`, etc.

## Getting started (for the implementing agent)

1. Read `docs/01-REQUIREMENTS.md` and `docs/08-ROADMAP.md`.
2. Run `/gsd-plan-phase 1` to produce the detailed plan for Phase 1.
3. Implement per the plan, with tests, atomic commits.
4. See `docs/09-INTEGRATION-TO-ESQUELETOEDIT.md` for how this will later be
   integrated as a tool inside EsqueletoEdit — keep interfaces clean and reusable.

## Origin

Promoted from EsqueletoEdit seed `SEED-261012-001-premiere-cut-detection.md`
(see `H:\Proyectos Software\EsqueletoEdit\.planning\seeds\`). It is developed
independently now for validation, but its final home is as a tool *inside*
EsqueletoEdit, contributing to a useful local AI editing platform for real
content workflows.
