# ROADMAP.md — Scene Cut Batch

## Phases

| Phase | Goal | Key Deliverable | Status |
|-------|------|-----------------|--------|
| 1 | Detection core (PySceneDetect wrapper + batch runner + error isolation) | `detect_folder()` returns per-clip scene lists | Complete |
| 2 | Launch prep & multi-platform distribution | GitHub repo, README, LICENSE, installers, packaging, cross-platform tests | Complete |
| 3 | UI polish & public-facing presentation | Restyled GUI (complete interface visible) + neutral NLE terminology + public copy review | Pending |
| 4 | Confidence scoring + markers (optional) | G/Y/R markers in XML | Pending |
| 5 | Packaging (Pinokio + binary) | One-click install + standalone binary | Pending |
| 6 | Integration API + docs for unified tool | Reusable Python API + schema docs | Pending |

---

### Phase 1: Detection core

- Wrap PySceneDetect ContentDetector.
- Media scanning (reuse EsqueletoEdit patterns): supported extensions, ffprobe metadata.
- Batch runner with per-clip error isolation and progress callback.
- Unit tests with small synthetic clips.

---

### Phase 2: Launch prep & multi-platform

- Public GitHub repository "Scene Cut Batch" at https://github.com/MustangXPress7/scenecutbatch
- README.md with installation and usage instructions for Windows, Mac, and Linux
- .gitignore excluding build artifacts, virtual environments, and temporary files
- LICENSE Apache-2.0 added to repository
- .planning/ROADMAP.md updated with new phase structure (Phase 2 = this launch)
- Linux install script (install_linux.sh) + .deb / .rpm / AppImage packaging
- Project name "Scene Cut Batch" in all code, READMEs, and ROADMAP.md
- Logo (assets/logo.png or .svg)
- Cross-platform testing: Windows, macOS, Linux
- Multi-platform release builds: GitHub Actions matrix (windows/macOS/linux) publishing zip + .deb + AppImage + .app bundle (delivered 2026-10-22)

*Note: Phases 2-5 from the original project structure have been redefined. Phase 2 (Fase 2 — Preparación y distribución multiplataforma) now covers launch prep and multi-platform distribution. (A former "Phase 3 — CLI + progress reporting + config" was removed: its scope, requirements UX-01..04, was delivered and verified inside Phase 1.) On 2026-10-23 Phase 3 was redefined as "UI polish & public-facing presentation" (user request); the previous pending phases were renumbered: Confidence 3→4, Packaging 4→5, Integration 5→6.*

---

### Phase 3: UI polish & public-facing presentation

**Requirements:** PRES-01, PRES-02, PRES-03, PRES-04, PRES-05, PRES-06

- **GUI layout rework**: the new logo (700×700 shown at ~233 px) crams the 700×520 window — controls, log and status get clipped. Redesign the layout (logo placement, header, spacing, window sizing) so the complete interface is visible and usable.
- **Neutral NLE terminology**: replace Premiere-Pro-exclusive claims ("for Adobe Premiere Pro", "imports directly into Premiere") with accurate, editor-agnostic phrasing: FCP7 XML (xmeml) importable by professional video editors (Premiere Pro, DaVinci Resolve and other NLEs that read FCP7 XML).
- **Public copy review**: remove/neutralize internal-development references everywhere (EsqueletoEdit, "parent ecosystem", integration plans, phase-status text) in code, READMEs, docs/, packaging metadata and GUI/CLI copy.
- **Consistency**: GUI, CLI (`--version`, help), READMEs, pyproject, .deb/.rpm/.desktop metadata all tell the same story.
- **Bilingual GUI** (added 2026-10-23): English/Spanish with OS language auto-detection and in-app EN/ES switch — PRES-05.
- **Studio signature** (added 2026-10-23): "Hecho por JMW Studio" in GUI, READMEs, CLI output and package metadata — PRES-06.

**Plans:** 5 plans

Plans:
**Wave 1**
- [ ] 03-01-PLAN.md — Bilingual GUI rework (i18n catalog + layout + EN/ES switch + credit)

**Wave 2** *(blocked on Wave 1 completion)*
- [ ] 03-02-PLAN.md — Python source/docstring sweep + CLI version footer + pyproject metadata
- [ ] 03-03-PLAN.md — READMEs + HANDOFF.md public copy sweep

**Wave 3** *(blocked on Wave 2 completion)*
- [ ] 03-04-PLAN.md — docs/ sweep (docs/09 reframed as extensibility) + repo-wide PRES-03 gate

**Wave 4** *(blocked on Wave 3 completion)*
- [ ] 03-05-PLAN.md — Packaging metadata (.deb/.rpm/.desktop) + phase-closing sweep + final review

---

### Phase 4: Confidence

- Per-scene score + G/Y/R mapping.
- Embed markers in XML.

---

### Phase 5: Packaging

- Pinokio recipe, Nuitka/PyInstaller binary.

---

### Phase 6: Integration

- Clean Python API, schema docs, integration guide for unified tool.
