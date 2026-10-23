# 03 — Tech Stack

| Concern | Choice | Notes |
|---------|--------|-------|
| Language | Python 3.10+ | modern typing, wide adoption |
| Cut detection | PySceneDetect 0.6.x (`scenedetect[opencv]`) | ContentDetector |
| Video I/O | OpenCV (via PySceneDetect) | |
| Media probing | ffprobe (ffmpeg) | JSON output, parsed in-process |
| Frame math | `fractions.Fraction` | Exact rational (24000/1001 etc.) |
| XML | stdlib `xml.etree.ElementTree` or `lxml` | FCP7 xmeml v5; validate by importing into a professional video editor |
| CLI | Typer | modern typing, wide adoption |
| GUI (opt) | Gradio | v1.1 |
| Progress | JSON to stdout/file | JSON progress schema, documented standalone |
| Packaging | Pinokio + Nuitka/PyInstaller | PyInstaller one-folder plus one-file |
| Tests | pytest | |
| License | Apache-2.0 | |

## Python dependencies (requirements.txt)

```
scenedetect[opencv]>=0.6.3
typer>=0.12
rich>=13.0
pyyaml>=6.0
ffmpeg-python>=0.2  # or subprocess ffprobe
```

Optional:
```
gradio>=4.0   # gui extra
lxml>=5.0     # faster XML
```

## External binaries

- `ffprobe` (ffmpeg) — must be on PATH or bundled.
- No ML models required (PySceneDetect is classical CV).

## Version pinning

Pin PySceneDetect and OpenCV together; document tested combination in
`docs/10-DECISIONS.md` once validated.
