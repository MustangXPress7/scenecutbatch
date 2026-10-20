---
phase: "01"
slug: "detection-core"
# status lifecycle: draft (seeded by plan-phase) → validated (set by validate-phase §6)
# audit-milestone §5.5 distinguishes NOT-VALIDATED (draft) from PARTIAL (validated + nyquist_compliant: false) (#2117)
status: draft
nyquist_compliant: false
wave_0_complete: false
created: "2026-10-20"
---

# Phase 01 — Validation Strategy

> Per-phase validation contract for feedback sampling during execution.

---

## Test Infrastructure

| Property | Value |
|----------|-------|
| **Framework** | pytest |
| **Config file** | pyproject.toml `[tool.pytest.ini_options]` |
| **Quick run command** | `pytest tests/ -x` |
| **Full suite command** | `pytest tests/` |
| **Estimated runtime** | ~30 seconds |

---

## Sampling Rate

- **After every task commit:** Run `pytest tests/ -x`
- **After every plan wave:** Run `pytest tests/`
- **Before `/gsd-verify-work`:** Full suite must be green
- **Max feedback latency:** 30 seconds

---

## Per-Task Verification Map

| Task ID | Plan | Wave | Requirement | Threat Ref | Secure Behavior | Test Type | Automated Command | File Exists | Status |
|---------|------|------|-------------|------------|-----------------|-----------|-------------------|-------------|--------|
| 01-01-01 | 01 | 1 | CUT-01 | — | scan_folder returns only supported extensions, case-insensitive | unit | `pytest tests/test_scanner.py -x` | ❌ W0 | ⬜ pending |
| 01-01-02 | 01 | 1 | CUT-02 | — | detect_clip runs ContentDetector, returns scenes | unit | `pytest tests/test_detector.py -x` | ❌ W0 | ⬜ pending |
| 01-01-03 | 01 | 1 | CUT-03 | — | threshold/min_scene_len defaults 27.0 / 15 | unit | `pytest tests/test_models.py -x` | ⚠️ partial | ⬜ pending |
| 01-01-04 | 01 | 1 | CUT-04 | — | Scene has start_tc, end_tc, duration, detection_score | unit | `pytest tests/test_detector.py -x` | ❌ W0 | ⬜ pending |
| 01-01-05 | 01 | 1 | CUT-05 | — | corrupt clip recorded in failed, batch continues | unit | `pytest tests/test_batch.py -x` | ❌ W0 | ⬜ pending |
| 01-01-06 | 01 | 1 | OUT-01 | — | write_xml produces file | unit | `pytest tests/test_xml_builder.py -x` | ❌ W0 | ⬜ pending |
| 01-01-07 | 01 | 1 | OUT-02 | — | filename `{stem}_cuts.xml` | unit | `pytest tests/test_xml_builder.py -x` | ❌ W0 | ⬜ pending |
| 01-01-08 | 01 | 1 | OUT-03 | — | XML has master sequence + cuts in order | unit/golden | `pytest tests/test_xml_builder.py -x` | ❌ W0 | ⬜ pending |
| 01-01-09 | 01 | 1 | OUT-04 | — | XML has virtual subclips + pathurl | unit/golden | `pytest tests/test_xml_builder.py -x` | ❌ W0 | ⬜ pending |
| 01-01-10 | 01 | 1 | UX-01 | — | progress callback invoked per clip | unit | `pytest tests/test_batch.py -x` | ❌ W0 | ⬜ pending |
| 01-01-11 | 01 | 1 | UX-02 | — | `--json-progress` flag accepted | CLI | `pytest tests/test_cli.py -x` | ❌ W0 | ⬜ pending |
| 01-01-12 | 01 | 1 | UX-03 | — | `--dry-run` lists cuts, writes nothing | CLI | `pytest tests/test_cli.py -x` | ❌ W0 | ⬜ pending |
| 01-01-13 | 01 | 1 | UX-04 | — | config file loads threshold/min_scene_len | unit | `pytest tests/test_config.py -x` | ❌ W0 | ⬜ pending |

*Status: ⬜ pending · ✅ green · ❌ red · ⚠️ flaky*

---

## Wave 0 Requirements

- [ ] `tests/test_scanner.py` — stubs for CUT-01
- [ ] `tests/test_detector.py` — stubs for CUT-02, CUT-04
- [ ] `tests/test_batch.py` — stubs for CUT-05, UX-01
- [ ] `tests/test_xml_builder.py` — stubs for OUT-01..04
- [ ] `tests/test_cli.py` — stubs for UX-02, UX-03
- [ ] `tests/test_config.py` — stubs for UX-04
- [ ] `tests/conftest.py` — shared fixtures (mock open_video, probe_media)
- [ ] `tests/fixtures/` — tiny synthetic clips or mocked detector
- [ ] Framework install: `pip install pytest>=8.0 pytest-cov>=5.0` — if not detected

---

## Manual-Only Verifications

| Behavior | Requirement | Why Manual | Test Instructions |
|----------|-------------|------------|-------------------|
| Premiere Pro imports XML without errors | OUT-05 | Requires Premiere Pro installation | Import golden-file XML into Premiere, verify bin + master sequence + subclips |

---

## Validation Sign-Off

- [ ] All tasks have `<automated>` verify or Wave 0 dependencies
- [ ] Sampling continuity: no 3 consecutive tasks without automated verify
- [ ] Wave 0 covers all MISSING references
- [ ] No watch-mode flags
- [ ] Feedback latency < 30s
- [ ] `nyquist_compliant: true` set in frontmatter

**Approval:** pending
