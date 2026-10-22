---
phase: 02-scene-cut-batch
plan: 04-ext
subsystem: branding, packaging
tags: [logo, gui, release, zip, windows, packaging]

requires:
  - phase: 02-scene-cut-batch (plan 01)
    provides: Repo structure, README, LICENSE, ROADMAP.md
  - phase: 02-scene-cut-batch (plan 02)
    provides: install_linux.sh, packaging/debian/, packaging/rpm/, packaging/appimage/
  - phase: 02-scene-cut-batch (plan 03)
    provides: Project name "Scene Cut Batch", logo in assets/logo.png
  - phase: 02-scene-cut-batch (plan 04)
    provides: Cross-platform test results in STATE.md

provides:
  - Logo integrado en la GUI de Tkinter (src/scenecutbatch/gui.py)
  - Script de empaquetado de releases (scripts/make_release.py)
  - Release zip de Windows: releases/SceneCutBatch-0.1.0-Windows.zip
  - scenecutbatch.spec actualizado con assets/logo.png en datas

affects:
  - 02-scene-cut-batch (extensión de plan 04)
  - 03-cli-progress-config (futuros releases)

actuals:
  tokens: 6000
  tasks: 3
  commits: 0

tech-stack:
  added: []
  patterns: [_asset_path() helper para resolver assets en desarrollo y PyInstaller; tk.PhotoImage para logo en GUI]

key-files:
  created: [scripts/make_release.py, releases/SceneCutBatch-0.1.0-Windows.zip]
  modified: [src/scenecutbatch/gui.py, scenecutbatch.spec]

key-decisions:
  - "Logo mostrado en la GUI encima del título, escalado a máximo 200 px de ancho"
  - "Ruta de assets resuelta tanto en desarrollo como bajo PyInstaller (_asset_path)"
  - "Releases empaquetados como .zip por plataforma (Windows generado; macOS/Linux por documentar)"

patterns-established:
  - "Helper _asset_path() para localizar assets tanto en modo desarrollo como en ejecutable empaquetado"

requirements-completed: []

coverage:
  - id: D1
    description: "Logo de la aplicación visible en la interfaz gráfica (GUI)"
    verification:
      - kind: manual_procedural
        ref: "Ejecutar python src/scenecutbatch/gui.py y verificar que se muestra el logo"
        status: unknown
    human_judgment: true
    rationale: "Requiere entorno gráfico para verificar visualmente"
  - id: D2
    description: "Release zip de Windows con ejecutable y scripts"
    requirement: "REPO-10"
    verification:
      - kind: automated
        ref: "ls releases/SceneCutBatch-0.1.0-Windows.zip"
        status: pass
    human_judgment: false

metrics:
  duration: 20min
  completed: 2026-10-22
  status: complete

---

# Phase 02 Plan 04-ext: Logo en GUI + Releases ZIP

**Extensión de Plan 02-04: logo integrado en la GUI y releases empaquetados por plataforma.**

## Accomplishments

### Logo en la aplicación (GUI)
- `src/scenecutbatch/gui.py`: Se agregó función `_asset_path()` que resuelve la ruta de assets tanto en desarrollo como bajo PyInstaller (one-folder y one-file).
- La GUI ahora muestra `assets/logo.png` encima del título "Scene Cut Batch", escalado automáticamente a máximo 200 px de ancho.
- Si la imagen no se puede cargar (TclError), se omite silenciosamente sin romper la aplicación.

### Releases ZIP por plataforma
- `scripts/make_release.py`: Script que empaqueta releases en `.zip` por plataforma (windows, macos, linux, all).
- Incluye en cada zip: ejecutable, scripts de lanzamiento (run.bat/install.bat, run_mac.sh/SceneCutBatch.command/install.sh, run.sh/install_linux.sh), README.md, LICENSE, pyproject.toml, carpeta assets/ y código fuente src/.
- `scenecutbatch.spec`: Actualizado con `datas=[('assets/logo.png', 'assets')]` para incluir el logo en futuros builds de PyInstaller.

### Release generado
- `releases/SceneCutBatch-0.1.0-Windows.zip`: Contiene `scenecutbatch.exe` (70MB), `run.bat`, `install.bat`, `README.md`, `LICENSE`, `pyproject.toml`, `assets/logo.png` y código fuente `src/`.

## Task Commits

- **Logo en GUI**: modificación de `src/scenecutbatch/gui.py` (incluida en este commit)
- **Script de releases**: creación de `scripts/make_release.py` (incluida en este commit)
- **Release Windows**: generación de `releases/SceneCutBatch-0.1.0-Windows.zip` (incluida en este commit)
- **Spec PyInstaller**: modificación de `scenecutbatch.spec` (incluida en este commit)

## Files Created/Modified

- `src/scenecutbatch/gui.py` - Logo integrado en la GUI + helper _asset_path()
- `scripts/make_release.py` - Script de empaquetado de releases por plataforma
- `releases/SceneCutBatch-0.1.0-Windows.zip` - Release zip de Windows
- `scenecutbatch.spec` - Logo incluido en datos de PyInstaller

## Decisions Made

- Logo escalado a máximo 200 px para no ocupar demasiado espacio en la ventana
- Fallback silencioso si el logo no se puede cargar (evita que la app falle por un asset opcional)
- Releases como .zip para facilitar distribución sin instalación previa

## Deviations from Plan

Estas tareas son una extensión del Plan 02-04 (cross-platform testing), solicitadas como mejoras de la Fase 2.

**Total deviations:** 0 auto-fixed.
**Impact on plan:** La Fase 2 ahora incluye logo visible en la aplicación y releases empaquetados listos para distribuir.

## Issues Encountered

None.

## User Setup Required

- **macOS/Linux releases**: Ejecutar `python scripts/make_release.py --version 0.1.0 --platform macos` y `--platform linux` en sus respectivos hosts para generar los zips de esas plataformas.
- **Push a GitHub**: El release zip y el código deben subirse a https://github.com/MustangXPress7/scenecutbatch

## Next Phase Readiness

Mejoras de Fase 2 completadas. Listo para `/gsd-plan-phase 3` (CLI + progress reporting + config).

---
*Phase: 02-scene-cut-batch*
*Completed: 2026-10-22*
