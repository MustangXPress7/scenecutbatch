# Phase 03: UI polish & public-facing presentation — Context

**Gathered:** 2026-10-23
**Status:** Ready for planning
**Requested by:** User after release v0.1.0 (2026-10-22) — "retoques estéticos"

<domain>
## Phase Boundary

Phase 3 is a presentation/polish phase: it reworks the Tkinter GUI layout (the
new logo cramps the window and clips the interface), neutralizes Premiere-Pro
exclusive terminology into editor-agnostic copy (FCP7 XML importable by
professional video editors), and removes internal-development references
(EsqueletoEdit, integration plans, phase status) from every repository text.
No detection/output behavior changes — the XML format and CLI semantics stay
as delivered in Phases 1-2.
</domain>

<decisions>
## Implementation Decisions

### D-31: GUI layout rework (PRES-01)
- The logo (700×700 PNG) is displayed at ~233 px (subsample 3) at the top of a
  700×520 window with minsize 650×450; title, subtitle, form rows, checkbox
  rows, run button, progress bar, log (12 lines) and status do not all fit —
  the interface reads as cramped/clipped.
- **Decision:** full layout redesign — smaller/relocated logo (header next to
  the title), window default size that fits the whole interface, consistent
  spacing, and verification that nothing is clipped at min size.
- **Reversibility:** reversible — GUI-only change, no data/output impact.

### D-32: Neutral NLE terminology (PRES-02)
- Current copy says "for Adobe Premiere Pro" / "genera XML para Premiere Pro".
- **Decision:** replace with accurate editor-agnostic phrasing — the tool
  emits FCP7 XML (xmeml) importable by professional video editors (Premiere
  Pro, DaVinci Resolve and other NLEs reading FCP7 XML). Keep "FCP7 XML" as
  the technical term.
- **Reversibility:** reversible — copy-only.

### D-33: Public copy review — remove internal references (PRES-03)
- Internal-development text exists in: README.md ("Parent ecosystem:
  EsqueletoEdit...", "Status: Active development (Phase 2...)"), README_USO.md,
  README_PORTABLE.md, gui.py subtitle, `__init__.py` docstring, cli.py help,
  pyproject description, packaging metadata (deb/rpm/desktop), docs/*.md
  (EsqueletoEdit consistency notes, integration doc 09), docs/10-DECISIONS.md.
- **Decision (user):** review and modify ALL texts, including technical docs
  under docs/ (not only user-facing surfaces).
- Internal planning artifacts under `.planning/` are GSD working state, not
  product documentation — keep them consistent but they are not part of the
  public-copy scope.
- **Reversibility:** costly-ish — touches many files, but copy-only.

### D-34: Cross-surface consistency (PRES-04)
- GUI, CLI (`--version`, help epilogs), READMEs, pyproject.toml and package
  metadata must tell the same story after the rewrite.
- **Reversibility:** reversible.

### Numbering (user-approved)
- New phase inserted as **Phase 3**; previous pending phases renumbered:
  Confidence 3→4, Packaging 4→5, Integration 5→6. REQUIREMENTS.md
  traceability updated accordingly.

### Locked from PROJECT.md / docs (not re-asked)
- Local-first, no cloud/telemetry/network at runtime
- Python 3.10+, Typer CLI, Apache-2.0
- No media duplication — virtual subclips reference original media only
- Error codes: 0 success, 1 usage, 2 validation, 3 processing, 4 export

### Deferred Ideas
- Advanced GUI (beyond simple one) — stays deferred
- Dark/light theme support
- GUI test automation (manual visual verification is acceptable)
</decisions>

<canonical_refs>
## Canonical References

Downstream agents MUST read these before planning or implementing.

### Roadmap & requirements
- `.planning/ROADMAP.md` — Phase 3 goal and deliverables
- `.planning/REQUIREMENTS.md` — PRES-01..04
- `.planning/STATE.md` — current state

### Code & assets to touch (expected)
- `src/scenecutbatch/gui.py` — layout rework + copy
- `src/scenecutbatch/__init__.py`, `src/scenecutbatch/cli.py` — help copy
- `src/scenecutbatch/export/xml_builder.py` — docstrings
- `README.md`, `README_USO.md`, `README_PORTABLE.md`
- `docs/01..10-*.md` — terminology + internal references
- `pyproject.toml`, `packaging/debian`, `packaging/rpm`, `packaging/appimage`
- `install.bat`, `install.sh`, `run*.sh/.bat/command` — any copy

### Internal references
- Phase 2 artifacts (`.planning/phases/02-scene-cut-batch/`) — VERIFICATION.md
  records the release state this phase polishes
</canonical_refs>

<code_context>
## Existing Code Insights

### GUI (src/scenecutbatch/gui.py, ~300 lines)
- `SceneCutBatchGUI(tk.Tk)` — 700×520, minsize 650×450.
- `_asset_path()` resolves assets in dev and PyInstaller (one-folder/one-file).
- `_set_window_icon()` applies `iconphoto` (works, verified).
- Logo block: `tk.PhotoImage` + `subsample(width//200)` (~233 px), packed
  above the title.
- `_build_ui()` single-column `ttk.Frame` with padding 12: title (Segoe UI 16
  bold), subtitle (10), form rows (input/output dirs), LabelFrame options
  (threshold, min-scene-len, recursive, dry-run, json-progress, confidence),
  run button, indeterminate Progressbar, "Salida:" label, ScrolledText (height
  12), status label.
- Fonts hardcode "Segoe UI" — Windows-only; falls back elsewhere.

### Established Patterns
- Pure detection core (`detect_folder()`), I/O at edges, JSON progress events
- Typer CLI with exit codes 0-4, `--json-progress`
- Release pipeline (CI) must stay green — spec `datas` includes assets
</code_context>

<specifics>
## Specific Ideas

- User (verbatim): "La aplicación, debido al nuevo logo, queda compactada y no
  muestra toda la interfaz completa."
- User (verbatim): "Hay un texto que menciona a Premiere Pro, pero la
  explicación correcta sería que es compatible con editores de vídeo
  profesionales. Incluso cualquier texto que hable sobre desarrollo interno
  revisarlo y modificarlo."
</specifics>

<deferred>
## Deferred Ideas

- Phase 4 (Confidence), Phase 5 (Packaging), Phase 6 (Integration) — renumbered
- EsqueletoEdit integration work (INT-01/02) — still future; this phase only
  removes *public copy* about it, not the plan itself
</deferred>
