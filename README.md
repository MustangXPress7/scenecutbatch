# Scene Cut Batch

> Batch scene-cut detection for Adobe Premiere Pro — generates FCP7 XML files with virtual subclips so an editor can review and pick takes without re-encoding or duplicating media.

**Status:** Active development (Phase 2 — Launch prep & multi-platform)
**License:** Apache-2.0
**Parent ecosystem:** EsqueletoEdit (local AI editing platform). This module is being developed as an *independent program* first so it can be built and validated in isolation, with the clear intent of being integrated later as a native tool *inside* EsqueletoEdit.

---

## What this is

A small, focused, local-first CLI (and optional GUI) that:

1. Takes a folder of video clips.
2. For each clip, runs **PySceneDetect** (ContentDetector, threshold 27.0 default) to find hard cuts.
3. Emits **one FCP7 XML file per clip** that Premiere Pro can import directly.
4. Each XML creates a bin containing:
   - a **master sequence** with all detected cuts in order, and
   - **virtual subclips** pointing at the original media (no duplication).
5. Optionally tags ambiguous/short scenes with confidence markers (Green/Yellow/Red) so the editor knows what to double-check.

The point is to replace Premiere's slow, one-clip-at-a-time "Scene Edit Detection" with a background batch job over hundreds of clips.

---

## Features

| Feature | Description |
|---|---|
| Batch scan | Recursively scan folders of video clips (mp4, mov, mxf, avi, mkv, webm) |
| Hard-cut detection | PySceneDetect ContentDetector with configurable threshold and min scene length |
| FCP7 XML output | One `<clip_stem>_cuts.xml` per clip, Premiere-importable |
| Master sequence | Each XML contains a master sequence with all cuts in timeline order |
| Virtual subclips | One subclip per detected scene referencing original media (no duplication) |
| Error isolation | One bad/corrupt clip does not abort the batch |
| Progress reporting | Per-clip progress with ETA, JSONL stream via `--json-progress` |
| Dry-run mode | List detected cuts without writing files (`--dry-run`) |
| Config file | YAML config file via `--config` |
| Cross-platform | Windows, macOS, Linux |
| Local-first | No cloud, no telemetry, no network at runtime |

---

## Installation

### Windows

1. Install Python 3.10+ from https://python.org
2. Install ffmpeg (ffprobe must be on PATH)
3. Install dependencies:

   ```cmd
   pip install scenedetect[opencv]>=0.6.3,<0.7 typer>=0.12 rich>=13.0 pyyaml>=6.0
   ```

4. Run:

   ```cmd
   pip install -e .
   scenecutbatch detect "C:\Footage\Day1" --out-dir "C:\Footage\Day1\cuts"
   ```

Or use the bundled launcher:

```cmd
run.bat
```

Or install via the Windows installer:

```cmd
install.bat
```

### macOS

1. Install Python 3.10+ (e.g. via Homebrew: `brew install python@3.11`)
2. Install ffmpeg: `brew install ffmpeg`
3. Install dependencies:

   ```bash
   pip3 install scenedetect[opencv]>=0.6.3,<0.7 typer>=0.12 rich>=13.0 pyyaml>=6.0
   ```

4. Run:

   ```bash
   pip3 install -e .
   scenecutbatch detect "/Volumes/Footage/Day1" --out-dir "/Volumes/Footage/Day1/cuts"
   ```

Or double-click `SceneCutBatch.command` to launch.

### Linux

1. Install Python 3.10+ and ffmpeg:

   ```bash
   sudo apt update && sudo apt install -y python3 python3-pip ffmpeg
   ```

2. Install dependencies:

   ```bash
   pip3 install scenedetect[opencv]>=0.6.3,<0.7 typer>=0.12 rich>=13.0 pyyaml>=6.0
   ```

3. Run:

   ```bash
   pip3 install -e .
   scenecutbatch detect ~/Footage/Day1 --out-dir ~/Footage/Day1/cuts
   ```

Or use the Linux install script:

```bash
bash install_linux.sh
```

---

## Prebuilt releases

Binaries for all three platforms are built automatically by GitHub Actions
(`.github/workflows/release.yml`) and published to the
[Releases page](https://github.com/MustangXPress7/scenecutbatch/releases):

| Platform | Artifacts |
|---|---|
| Windows | `SceneCutBatch-<version>-Windows.zip` (contains `scenecutbatch.exe`, GUI + CLI) |
| macOS | `SceneCutBatch-<version>-macos.zip` (portable binary) + `SceneCutBatch-<version>-macOS.zip` (`.app` bundle) |
| Linux | `SceneCutBatch-<version>-linux.zip` + `.deb` + AppImage |

To publish a new release, push a version tag:

```bash
git tag v0.1.0
git push origin v0.1.0
```

PyInstaller does not cross-compile: each platform is built on its own runner
(windows-latest, macos-latest, ubuntu-latest). You can also trigger a build
manually from the Actions tab ("Run workflow") without publishing a release.

To build locally on the target OS:

```bash
pip install -e . && pip install "scenedetect[opencv]" pyinstaller
pyinstaller scenecutbatch.spec --clean --noconfirm
python scripts/make_release.py --version 0.1.0 --platform <windows|macos|linux>
```

---

## Usage

```bash
# Basic: detect cuts in a folder, write XML alongside input
scenecutbatch detect "/path/to/footage"

# Specify output directory
scenecutbatch detect "/path/to/footage" --out-dir "/path/to/output"

# Adjust detection sensitivity
scenecutbatch detect "/path/to/footage" --threshold 30 --min-scene-len 20

# Recurse into subfolders
scenecutbatch detect "/path/to/footage" --recursive

# Dry-run: list cuts without writing files
scenecutbatch detect "/path/to/footage" --dry-run

# Stream JSON progress for GUI/polling
scenecutbatch detect "/path/to/footage" --json-progress > progress.jsonl

# Use a YAML config file
scenecutbatch detect "/path/to/footage" --config config.yaml

# Print version
scenecutbatch --version
```

Exit codes:
- `0` — success (all clips processed, per-clip errors reported)
- `1` — usage error
- `2` — validation error (bad input dir, missing ffprobe)
- `3` — processing error (fatal)
- `4` — export error (fatal)

---

## Output

For each input clip `MyVideo.mp4`, the tool writes `MyVideo_cuts.xml` containing:

- A `<bin>` named after the clip
- A master `<sequence>` with all detected cuts in timeline order
- One virtual `<clip>` (subclip) per detected scene, referencing the original media via `file://localhost/` path URLs (no media duplication)

Premiere Pro imports the XML and creates a bin with the master sequence and subclips.

---

## Technology

| Layer | Technology |
|---|---|
| Language | Python 3.10+ |
| Cut detection | PySceneDetect 0.6.x (`scenedetect[opencv]`) |
| Video I/O | OpenCV (via PySceneDetect) |
| Media probing | ffprobe (ffmpeg) |
| Frame math | `fractions.Fraction` (exact rational, NTSC-safe) |
| XML | stdlib `xml.etree.ElementTree` (FCP7 xmeml v5) |
| CLI | Typer |
| Config | YAML (`pyyaml`) |
| Packaging | Pinokio + Nuitka/PyInstaller |
| Tests | pytest |

---

## License

Apache-2.0. See [`LICENSE`](LICENSE) for full text.
