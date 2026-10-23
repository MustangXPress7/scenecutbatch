# 10 — Decisions (locked)

| # | Decision | Rationale |
|---|----------|-----------|
| 1 | Built and usable as a standalone tool; no dependency on any other application | Validate the detector in isolation before any integration |
| 2 | Standalone product (no unified tool planned) | SceneCutBatch builds and runs alone; other tools consume its documented API when they choose to |
| 3 | PySceneDetect ContentDetector, threshold 27.0 default | Proven, classical CV, no ML deps |
| 4 | FCP7 XML (xmeml) output | Editor-agnostic import; virtual subclips reference original media |
| 5 | No media duplication | Editor trust + storage |
| 6 | Python 3.10+, Typer CLI | Typed CLI with eager --version callback; stdlib-friendly |
| 7 | Local-first, no cloud | Privacy, offline editing environments |
| 8 | Confidence off by default | Keep v1 simple; add in v1.1 |
| 9 | Apache-2.0 | Permissive, business-friendly open-source license |
| 10 | Error isolation per clip | Batch robustness |
| 11 | Frame math via `fractions.Fraction` | Exact (NTSC) |

## Open questions (for implementing agent to resolve)

- Reuse otio-fcp-adapter or build xmeml directly? (Phase 2 spike)
- GUI in v1 or v1.1? (recommend v1.1)
- Auto-import plugin: UXP vs ExtendScript? (v2)
- Rust acceleration worth it? (benchmark first; default no)
