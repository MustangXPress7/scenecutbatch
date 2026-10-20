# 01 — Requirements (pointer)

Full requirements with REQ-IDs, acceptance criteria and traceability live in
[`../.planning/REQUIREMENTS.md`](../.planning/REQUIREMENTS.md). This file is a
short human-facing summary.

## v1 in one paragraph

Scan a folder of video clips, detect hard cuts per clip with PySceneDetect, and
write one Premiere-importable FCP7 XML per clip (master sequence + virtual
subclips pointing at original media, no duplication), with progress reporting,
configurable thresholds, and optional Green/Yellow/Red confidence markers.
Batch must survive individual clip failures.

See `.planning/REQUIREMENTS.md` for REQ-IDs (CUT-*, OUT-*, UX-*, CONF-*, PKG-*, INT-*).
