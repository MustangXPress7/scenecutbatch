# 10 — Decisions (locked)

| # | Decision | Rationale |
|---|----------|-----------|
| 1 | Independent project now, native tool inside EsqueletoEdit later | Validate in isolation, then integrate into the unified platform |
| 2 | Final home is EsqueletoEdit (no separate "unified tool" planned) | EsqueletoEdit IS the unified local AI editing platform |
| 3 | PySceneDetect ContentDetector, threshold 27.0 default | Proven, classical CV, no ML deps |
| 4 | FCP7 XML (xmeml) output | Premiere-native import, virtual subclips |
| 5 | No media duplication | Editor trust + storage |
| 6 | Python 3.10+, Typer CLI | Consistency with EsqueletoEdit |
| 7 | Local-first, no cloud | Privacy, offline editing environments |
| 8 | Confidence off by default | Keep v1 simple; add in v1.1 |
| 9 | Apache-2.0 | Consistency with EsqueletoEdit |
| 10 | Error isolation per clip | Batch robustness |
| 11 | Frame math via `fractions.Fraction` | Exact (NTSC) |

## Open questions (for implementing agent to resolve)

- Reuse otio-fcp-adapter or build xmeml directly? (Phase 2 spike)
- GUI in v1 or v1.1? (recommend v1.1)
- Auto-import plugin: UXP vs ExtendScript? (v2)
- Rust acceleration worth it? (benchmark first; default no)
