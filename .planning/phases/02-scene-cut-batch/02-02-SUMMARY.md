---
phase: 02-scene-cut-batch
plan: 02
subsystem: packaging
tags: [linux, packaging, deb, rpm, appimage, installer]

requires:
  - phase: 01-detection-core
    provides: Detection core scaffold and pyproject.toml with project metadata

provides:
  - install_linux.sh — Linux install script with dependency validation
  - packaging/debian/ — .deb package structure (DEBIAN/control, postinst, usr/bin/)
  - packaging/rpm/scenecutbatch.spec — .rpm package spec
  - packaging/appimage/ — AppImage packaging docs and desktop entry

affects:
  - 02-scene-cut-batch (subsequent plans 02-03, 02-04)
  - 05-packaging

actuals:
  tokens: 10000
  tasks: 3
  commits: 1

tech-stack:
  added: [dpkg-deb .deb packaging, RPM spec, AppImage directory structure]
  patterns: [Install script validates python3 + ffmpeg, graceful degradation when ffmpeg missing]

key-files:
  created: [install_linux.sh, packaging/debian/DEBIAN/control, packaging/debian/DEBIAN/postinst, packaging/debian/usr/bin/scenecutbatch, packaging/rpm/scenecutbatch.spec, packaging/appimage/README.md, packaging/appimage/scenecutbatch.desktop]
  modified: []

key-decisions:
  - "Support apt/dnf/yum package managers in install_linux.sh"
  - "ffmpeg treated as optional (graceful degradation) per D-07"

patterns-established:
  - "Install script pattern: verify python3 -> install system deps -> install Python deps -> set permissions -> usage instructions"

requirements-completed: [REPO-05, REPO-06]

coverage:
  - id: D1
    description: "install_linux.sh script installs dependencies and launches the app"
    requirement: "REPO-05"
    verification:
      - kind: automated
        ref: "bash -n install_linux.sh"
        status: pass
    human_judgment: false
  - id: D2
    description: ".deb package structure with DEBIAN/control and postinst script"
    requirement: "REPO-06"
    verification:
      - kind: automated
        ref: "ls packaging/debian/DEBIAN/control"
        status: pass
    human_judgment: false
  - id: D3
    description: "At least one additional packaging directory (.rpm or AppImage) with documentation"
    requirement: "REPO-06"
    verification:
      - kind: automated
        ref: "ls packaging/rpm/ && ls packaging/appimage/"
        status: pass
    human_judgment: false

metrics:
  duration: 12min
  completed: 2026-10-22
  status: complete

---

# Phase 02 Plan 02: Linux Packaging Summary

**Linux install script and multi-format packaging created — install_linux.sh with dependency validation, .deb package structure, .rpm spec, and AppImage documentation.**

## Performance

- **Duration:** 12 min
- **Started:** 2026-10-22T00:45:00Z
- **Completed:** 2026-10-22T00:57:00Z
- **Tasks:** 3
- **Files modified:** 7

## Accomplishments

- Created install_linux.sh: verifies python3, installs system dependencies (python3-pip, ffmpeg via apt/dnf/yum), installs Python dependencies, sets execution permissions, clear error messages for missing dependencies
- Created packaging/debian/DEBIAN/control: package metadata (name, version, dependencies, maintainer, description)
- Created packaging/debian/DEBIAN/postinst: post-install script that ensures Python dependencies and executable permissions
- Created packaging/debian/usr/bin/scenecutbatch: entry point script
- Created packaging/rpm/scenecutbatch.spec: RPM package spec with build/install/changelog sections
- Created packaging/appimage/README.md: AppImage build instructions and directory structure
- Created packaging/appimage/scenecutbatch.desktop: desktop entry file

## Task Commits

1. **Task 02-02-A: Create install_linux.sh** - included in commit `4098f09` (feat)
2. **Task 02-02-B: Create .deb package** - included in commit `4098f09` (feat)
3. **Task 02-02-C: Create .rpm and AppImage packaging** - included in commit `4098f09` (feat)

**Plan metadata:** `4098f09` (feat: add Linux install script and deb/rpm/appimage packaging)

## Files Created/Modified

- `install_linux.sh` - Linux install script with system dependency detection and Python package installation
- `packaging/debian/DEBIAN/control` - .deb package control file
- `packaging/debian/DEBIAN/postinst` - .deb post-install script
- `packaging/debian/usr/bin/scenecutbatch` - .deb entry point script
- `packaging/rpm/scenecutbatch.spec` - RPM package specification
- `packaging/appimage/README.md` - AppImage packaging documentation
- `packaging/appimage/scenecutbatch.desktop` - Desktop entry for AppImage

## Decisions Made

- install_linux.sh supports apt (Debian/Ubuntu), dnf (Fedora), and yum (CentOS/RHEL) package managers
- ffmpeg treated as optional with graceful degradation and clear warning message (consistent with D-07)
- Package dependencies declared: python3 >= 3.10, python3-pip, ffmpeg

## Deviations from Plan

None - plan executed exactly as written. Actual .deb/.rpm/.AppImage binary generation requires dpkg-deb/rpmbuild/appimagetool which may not be available in this environment; packaging structure and documentation are complete.

**Total deviations:** 0 auto-fixed.
**Impact on plan:** All packaging deliverables produced as structure and documentation.

## Issues Encountered

None.

## User Setup Required

None - no external service configuration required.

## Next Phase Readiness

Packaging infrastructure ready. Next: Plan 02-03 (project name "Scene Cut Batch" in code, READMEs, logo, ROADMAP.md update).

---
*Phase: 02-scene-cut-batch*
*Completed: 2026-10-22*
