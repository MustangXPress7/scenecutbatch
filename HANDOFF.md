# HANDOFF.md — for the next AI agent

## You are taking over: SceneCutBatch

Batch scene-cut detection that emits FCP7 XML (xmeml) with virtual subclips, importable by professional video editors.

- Local-first, no cloud, Apache-2.0, Python 3.10+.

## First steps

1. Read `README.md` for the standalone user guide.
2. Read the surviving `docs/` set for technical reference.
3. Check `.planning/STATE.md` and `.planning/ROADMAP.md` for GSD working state.
4. Implement per plan, with tests, atomic commits.

## Key conventions

- Python 3.10+, Typer CLI, pytest, Apache-2.0.
- GSD workflow: `.planning/` drives phases; config in `.planning/config.json`.
- Frame math via `fractions.Fraction`.
- Progress as JSON events (see `docs/04-DATA-MODELS.md`).
- Error isolation per clip (never abort batch on one bad file).

## Open questions

- Build xmeml directly or reuse an FCP7 adapter.
- GUI in v1 or v1.1 (recommend v1.1).

## Project conventions

This repository follows its own conventions: Python 3.10+, Typer CLI, pytest,
Apache-2.0, local-first with no cloud or telemetry, FCP7 XML (xmeml v5) output
with virtual subclips referencing original media.

## Definition of done (v1)

See `.planning/REQUIREMENTS.md` success criteria.
