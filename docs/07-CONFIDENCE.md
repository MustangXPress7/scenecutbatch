# 07 — Confidence (optional, v1.1)

## Score

Per scene, combine:
- `detection_score` (PySceneDetect, higher = stronger cut boundary).
- scene duration (very short scenes are suspicious).
- proximity to `min_scene_len` (scenes just above the floor are suspicious).

Suggested formula (tune in implementation):

```
conf = min(1.0, detection_score / 100.0)          # normalize
if duration_sec < 1.0: conf *= 0.5
if end_frame - start_frame <= min_scene_len + 2: conf *= 0.8
```

## Classification

- GREEN >= 0.85
- YELLOW 0.60–0.84
- RED < 0.60

G/Y/R bands are fixed for v1: GREEN >= 0.85, YELLOW 0.60–0.84, RED < 0.60.

## Embedding in XML

Add `<marker>` to the subclip (or master sequence) with:
- `<name>` = classification (GREEN/YELLOW/RED)
- `<comment>` = `score=0.92;dur=1.2s`
- `<in>`/`<out>` = scene range

Professional video editors display markers with color when `<color>` is supported; otherwise rely on the marker label.

## When to enable

Off by default (v1). Enable with `--confidence`. Keep detector output pure;
scoring is a separate pass.
