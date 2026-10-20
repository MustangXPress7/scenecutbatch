# HANDOFF.md — for the next AI agent

## You are taking over: SceneCutBatch

A batch scene-cut detector for Premiere Pro. Full spec in `docs/`.

### Key context

- This is developed independently now, but its final home is as a tool **inside
  EsqueletoEdit** (the unified local AI editing platform). Do not build it as a
  permanent separate product; keep interfaces clean so it can be integrated
  later as `esqueletoedit.tools.scenecutbatch` or similar.
- Local-first, no cloud, Apache-2.0, Python 3.10+.

## First steps

1. Read `README.md`, then `docs/01-REQUIREMENTS.md` (points to `.planning/REQUIREMENTS.md`).
2. Read `docs/02-ARCHITECTURE.md`, `docs/04-DATA-MODELS.md`, `docs/08-ROADMAP.md`.
3. Read `docs/09-INTEGRATION-TO-ESQUELETOEDIT.md` for the integration target.
4. Check `.planning/STATE.md` (not started) and `.planning/ROADMAP.md`.
5. Run `/gsd-plan-phase 1` to generate the detailed plan for Phase 1 (Detection core).
6. Implement per plan, with tests, atomic commits.

## Key conventions (inherited from EsqueletoEdit)

- Python 3.10+, Typer CLI, pytest, Apache-2.0.
- GSD workflow: `.planning/` drives phases; config in `.planning/config.json`.
- Frame math via `fractions.Fraction`.
- Progress as JSON events (see `docs/04-DATA-MODELS.md`).
- Error isolation per clip (never abort batch on one bad file).

## Open questions to resolve during Phase 2

- Reuse otio-fcp-adapter (EsqueletoEdit) vs. build xmeml directly.
- GUI in v1 or v1.1 (recommend v1.1).

## Reference: sibling project

`H:\Proyectos Software\EsqueletoEdit` — reuse media scanner, FCP7 XML, progress,
Pinokio recipe, Nuitka build scripts. Do NOT import at runtime; copy patterns.

## Definition of done (v1)

See `.planning/REQUIREMENTS.md` success criteria + integration into EsqueletoEdit.
