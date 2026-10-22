# SceneCutBatch AppImage packaging

## Overview
This directory contains the files needed to build an AppImage for SceneCutBatch,
enabling portable execution on any Linux distribution without system installation.

## Files

- `AppDir/` — AppImage directory structure
- `build_appimage.sh` — Script to assemble the AppImage using appimagetool

## Build Instructions

```bash
# Install appimagetool
wget https://github.com/AppImage/AppImageKit/releases/download/continuous/appimagetool-x86_64.AppImage
chmod +x appimagetool-x86_64.AppImage

# Build the AppImage
./build_appimage.sh

# Output: SceneCutBatch-0.1.0-x86_64.AppImage
```

## AppDir Structure

```
AppDir/
  usr/bin/scenecutbatch    # Entry point script
  usr/lib/scenecutbatch/   # Python package files
  scenecutbatch.desktop    # Desktop entry
  scenecutbatch.png        # Application icon
```

## Notes

- AppImage bundles all dependencies, so ffmpeg and Python are not required on the host
- Tested on Ubuntu 22.04+, Debian 11+, Fedora 35+
