---
phase: 03-ui-polish-presentation
plan: 01
subsystem: ui
tags: [tkinter, i18n, bilingual, gui, localization]

# Dependency graph
requires:
  - phase: 02-scene-cut-batch
    provides: release v0.1.0 baseline (GUI, CLI, detection core) that this phase polishes
provides:
  - src/scenecutbatch/i18n.py — en/es string catalog with detect_language/set_language/t
  - tests/test_i18n.py — catalog parity and normalization tests
  - Reworked src/scenecutbatch/gui.py — horizontal header, idempotent rebuild, EN/ES switch, JMW Studio credit
affects:
  - 04-confidence
  - 05-packaging
  - 06-integration

# Actuals (#2632) — pairs with the plan's `estimate` to calibrate future estimates.
# Same estimateTokens scale (chars/4 over the realized diff), never a harness token count.
actuals:
  tokens: 5496
  tasks: 3
  commits: 4

# Tech tracking
tech-stack:
  added: []  # stdlib only — locale, typing; no third-party dependencies added
  patterns:
    - "Idempotent _build_ui() with self._container — destroy children before re-pack"
    - "Horizontal header: logo left (side=tk.LEFT), title/subtitle/signature right"
    - "Language switch rebuild: set_language(code) + self._build_ui() preserves tk.StringVar state"
    - "Widget reference retention on every rebuild (logo_label.image, _logo_image, _icon_image)"
    - "t() string catalog with late-binding-safe lambdas (capture msg via default arg)"

key-files:
  created:
    - src/scenecutbatch/i18n.py
    - tests/test_i18n.py
  modified:
    - src/scenecutbatch/gui.py

key-decisions:
  - "None - followed plan as specified"

patterns-established:
  - "Module header convention: one-line docstring, from __future__ import annotations on line 3, stdlib-only imports, UPPER_SNAKE constant, Google-style one-line-summary docstrings"

requirements-completed:
  - PRES-01
  - PRES-05
  - PRES-06

# Coverage metadata (#1602)
coverage:
  - id: D1
    description: i18n string catalog with full en/es coverage for all GUI strings
    requirement: PRES-05
    verification:
      - kind: unit
        ref: tests/test_i18n.py#test_catalog_has_en_and_es_for_every_key
        status: pass
    human_judgment: false
  - id: D2
    description: Bilingual GUI rework — horizontal header, idempotent rebuild, EN/ES switch, JMW Studio credit
    requirement: PRES-01
    verification:
      - kind: automated_ui
        ref: python -c "from scenecutbatch.gui import SceneCutBatchGUI; ..." (minsize fit check)
        status: pass
      - kind: manual_procedural
        ref: Task 3 checkpoint — six visual UAT items (interface visibility, logo, auto-detect, switch, credit, functional smoke)
        status: pass
    human_judgment: true
    rationale: GUI visual acceptance requires human inspection per CONTEXT.md (GUI test automation deferred); all six UAT items confirmed "approved" by the developer.

# Metrics
duration: 45min
completed: 2026-10-23T21:30:00Z
status: complete
plan_head_before: bd73030fab2c3e4c68db0c4318255c93b11f05e5
plan_head_after: d429d74

---

# Phase 03 Plan 01: Bilingual GUI rework (i18n catalog + layout + EN/ES switch + credit) Summary

**Bilingual i18n catalog (en/es) with OS auto-detection, horizontal header logo relocation, in-app language switch, and JMW Studio credit — GUI structurally reworked to fit within minsize, all strings routed through t() lookups.**

## Performance

- **Duration:** 45 min
- **Started:** 2026-10-23T21:00:00Z
- **Completed:** 2026-10-23T21:30:00Z
- **Tasks:** 3 of 3 complete
- **Files modified:** 3 (1 created, 1 created, 1 modified)

## Accomplishments

- Created `src/scenecutbatch/i18n.py` — full en/es STRINGS catalog (32 keys) with `detect_language`, `set_language`, `current_language`, `t`, `normalize_language`; stdlib-only (`locale`, `typing`)
- Created `tests/test_i18n.py` — 9 tests covering normalization, fallback, interpolation, catalog parity, unknown-key passthrough
- Reworked `src/scenecutbatch/gui.py` — idempotent `_build_ui()` with `self._container`, horizontal header (logo + title + subtitle + signature + language switch), 880×740 / 820×700 sizing, language switch rebuilds UI immediately preserving input/output folder paths
- All hardcoded user-visible strings in `gui.py` replaced with `t()` lookups (grep gate passes: zero remaining)
- Progress event contract matches `batch.py` 1:1 (start, clip_start, clip_done, clip_error, done) with late-binding-safe lambdas
- Task 3 checkpoint (human-verify, gate="blocking-human") approved: all six visual UAT items confirmed — interface visibility at default size and minsize, logo relocation per D-31, OS auto-detection per D-35, in-app EN/ES switch rebuild per D-35, JMW Studio credit per D-36 ("Hecho por JMW Studio" / "Made by JMW Studio"), functional smoke test

## Task Commits

Each task was committed atomically:

1. **Task 1: End-to-end bilingual GUI shell — catalog, header, one translated path** - `490d9e4` (feat)
2. **Task 2: Route every remaining GUI string through the catalog (D-35, D-32)** - `d429d74` (feat)
3. **Task 3: Visual UAT — complete interface, switch, credit (PRES-01 / PRES-05 / PRES-06)** - checkpoint:human-verify (gate="blocking-human"), user response "approved", no code commit

**Plan metadata commit:** `03-01-SUMMARY.md` docs commit (this plan)

## Files Created/Modified

- `src/scenecutbatch/i18n.py` - New: bilingual string catalog module (en/es) with locale detection and t() lookup
- `tests/test_i18n.py` - New: unit tests for i18n module (9 tests, all passing)
- `src/scenecutbatch/gui.py` - Modified: layout rework + i18n integration + language switch + signature credit

## Decisions Made

None - followed plan as specified. All design decisions (D-31 through D-36) were locked in the plan and CONTEXT.md.

## Deviations from Plan

None - plan executed exactly as written.

## Issues Encountered

None.

## User Setup Required

None - no external service configuration required.

## Next Phase Readiness

All three tasks complete and committed. i18n catalog, GUI rework, and bilingual EN/ES switch are production-ready. Plan 03-01 fully done; ready for the next plan in Phase 03 or Phase 04.

## Self-Check: PASSED

All files created/modified exist and commits are recorded:
- `src/scenecutbatch/i18n.py` — FOUND
- `tests/test_i18n.py` — FOUND
- `src/scenecutbatch/gui.py` — FOUND
- Commit `490d9e4` — FOUND in HEAD history
- Commit `d429d74` — FOUND in HEAD history
