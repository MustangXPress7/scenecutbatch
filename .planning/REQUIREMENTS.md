# Requirements — SceneCutBatch

## v1 Requirements

### Detection
- **CUT-01**: Scan a folder (recursively optional) and collect supported video
  files (mp4, mov, mxf, avi, mkv, webm) — case-insensitive.
- **CUT-02**: Detect hard scene cuts per clip using PySceneDetect ContentDetector.
- **CUT-03**: Default threshold = 27.0; default min scene length = 15 frames.
  Both configurable.
- **CUT-04**: Return, per clip: list of scenes with (start_tc, end_tc, duration,
  detection_score).
- **CUT-05**: One bad/unsupported/corrupt clip must NOT abort the batch; record
  error and continue.

### Output
- **OUT-01**: Write one FCP7 XML file per input clip.
- **OUT-02**: Output filename convention: `<clip_stem>_cuts.xml` in an output
  directory (default: alongside input or `--out-dir`).
- **OUT-03**: Each XML contains a master sequence with all detected cuts in
  timeline order.
- **OUT-04**: Each XML contains virtual subclips (one per detected scene) that
  reference the original media (no duplication).
- **OUT-05**: A professional video editor that reads FCP7 XML (Premiere Pro,
  DaVinci Resolve, ...) imports the XML without errors and creates a bin with
  master sequence + subclips.
- **OUT-06**: (Optional, v1.1) Export EDL in addition to FCP XML.

### Presentation (Phase 3 — UI polish & public copy)
- [ ] **PRES-01**: The GUI shows its complete interface (all controls, log, status)
  without clipping at the default window size, with the logo present.
- [ ] **PRES-02**: All user-facing copy uses editor-agnostic terminology: FCP7 XML
  importable by professional video editors. No Premiere-Pro-exclusive claims.
- [ ] **PRES-03**: No internal-development references (EsqueletoEdit, parent
  ecosystem, integration plans, internal phase status) in any repository text:
  code, READMEs, docs/, packaging metadata, GUI/CLI copy.
- [ ] **PRES-04**: Terminology and messaging consistent across GUI, CLI, READMEs,
  pyproject and package metadata (.deb/.rpm/.desktop).
- [ ] **PRES-05**: The GUI is bilingual English/Spanish: auto-detects the OS
  language on start and offers an in-app EN/ES switch that applies immediately.
- [ ] **PRES-06**: Studio signature "Hecho por JMW Studio" present in the GUI, the
  READMEs, the CLI about/output and package metadata (Maintainer).

### Progress & UX
- **UX-01**: Report progress per clip (index/total, clip name, ETA) to stdout
  and/or a progress file (JSON) for GUI/polling.
- **UX-02**: CLI supports `--json-progress` for machine-readable streaming
  (consistent with EsqueletoEdit).
- **UX-03**: Dry-run / preview mode lists detected cuts without writing files.
- **UX-04**: Configurable via CLI flags and a config file (YAML/TOML).

### Confidence (optional, v1.1)
- **CONF-01**: Compute a per-scene confidence score from detection score + scene
  duration + min-length proximity.
- **CONF-02**: Map score to Green (>=0.85) / Yellow (0.60-0.84) / Red (<0.60).
- **CONF-03**: Embed markers in XML with color + label so professional video
  editors display them.

### Packaging
- **PKG-01**: Pinokio one-click recipe (consistent with EsqueletoEdit).
- **PKG-02**: Standalone binary via Nuitka/PyInstaller.
- **PKG-03**: Model/dependency vendoring not required (PySceneDetect is pip).

### Integration (future)
- **INT-01**: Expose a Python API (`scenecutbatch.detect(folder, ...)`) reusable
  by EsqueletoEdit's unified tool.
- **INT-02**: Output schema documented so the unified tool can consume it.

## v2 Requirements (deferred)

- Soft-cut / dissolve detection.
- Premiere UXP auto-import plugin.
- ExtendScript automation.
- Rust acceleration for detection (benchmark first).
- Fountain/EDL round-trip.

## Out of Scope

- Script alignment, transcription, matching (EsqueletoEdit).
- Cloud processing.
- Media re-encoding.

## Traceability

| REQ | Phase | Status |
|-----|-------|--------|
| CUT-01..05 | Phase 1 | Complete |
| OUT-01..04 | Phase 1 | Complete |
| OUT-05 | Phase 2 | Pending (manual NLE smoke test) |
| UX-01..04 | Phase 1 | Complete |
| PRES-01..06 | Phase 3 | Pending |
| CONF-01..03 | Phase 4 | Pending |
| PKG-01..03 | Phase 5 | Pending |
| INT-01..02 | Phase 6 | Pending |
