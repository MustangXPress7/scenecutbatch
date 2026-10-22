# ROADMAP.md — Scene Cut Batch

## Phases

| Phase | Goal | Key Deliverable | Status |
|-------|------|-----------------|--------|
| 1 | Detection core (PySceneDetect wrapper + batch runner + error isolation) | `detect_folder()` returns per-clip scene lists | Complete |
| 2 | Launch prep & multi-platform distribution | GitHub repo, README, LICENSE, installers, packaging, cross-platform tests | In Progress |
| 3 | CLI + progress reporting + config | `scenecutbatch` CLI with flags | Pending |
| 4 | Confidence scoring + markers (optional) | G/Y/R markers in XML | Pending |
| 5 | Packaging (Pinokio + binary) | One-click install + standalone binary | Pending |
| 6 | Integration API + docs for unified tool | Reusable Python API + schema docs | Pending |

---

### Phase 1 — Detection core (Complete)

- Wrap PySceneDetect ContentDetector.
- Media scanning (reuse EsqueletoEdit patterns): supported extensions, ffprobe metadata.
- Batch runner with per-clip error isolation and progress callback.
- Unit tests with small synthetic clips.

---

### Phase 2 — Launch prep & multi-platform (In Progress)

- Public GitHub repository "Scene Cut Batch" at https://github.com/MustangXPress7/scenecutbatch
- README.md with installation and usage instructions for Windows, Mac, and Linux
- .gitignore excluding build artifacts, virtual environments, and temporary files
- LICENSE Apache-2.0 added to repository
- .planning/ROADMAP.md updated with new phase structure (Phase 2 = this launch)
- Linux install script (install_linux.sh) + .deb / .rpm / AppImage packaging
- Project name "Scene Cut Batch" in all code, READMEs, and ROADMAP.md
- Logo (assets/logo.png or .svg)
- Cross-platform testing: Windows, macOS, Linux

*Note: Phases 2-6 from the original project structure have been redefined. Phase 2 (Fase 2 — Preparación y distribución multiplataforma) now covers launch prep and multi-platform distribution; phases 3-6 remain as listed above.*

---

### Phase 3 — CLI + progress reporting + config (Pending)

- Typer CLI consistent with EsqueletoEdit.
- `--json-progress`, `--out-dir`, `--threshold`, `--min-scene-len`, `--dry-run`.
- Config file support.

---

### Phase 4 — Confidence (Pending)

- Per-scene score + G/Y/R mapping.
- Embed markers in XML.

---

### Phase 5 — Packaging (Pending)

- Pinokio recipe, Nuitka/PyInstaller binary.

---

### Phase 6 — Integration (Pending)

- Clean Python API, schema docs, integration guide for unified tool.
