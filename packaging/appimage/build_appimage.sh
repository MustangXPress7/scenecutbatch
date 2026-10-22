#!/usr/bin/env bash
# Construye la AppImage de Scene Cut Batch a partir del binario de PyInstaller.
#
# Uso (en Linux, tras compilar con PyInstaller):
#   ./packaging/appimage/build_appimage.sh <version> [ruta-binario]
#
# Salida: releases/SceneCutBatch-<version>-x86_64.AppImage
set -euo pipefail

VERSION="${1:?Uso: build_appimage.sh <version> [ruta-binario]}"
BINARY="${2:-dist/scenecutbatch}"
HERE="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
REPO="$(cd "$HERE/../.." && pwd)"
APPDIR="$HERE/AppDir"
OUT="$REPO/releases/SceneCutBatch-${VERSION}-x86_64.AppImage"

if [ ! -f "$REPO/$BINARY" ] && [ ! -f "$BINARY" ]; then
    echo "ERROR: no existe el binario '$BINARY'. Compila antes con:" >&2
    echo "  pyinstaller scenecutbatch.spec --clean --noconfirm" >&2
    exit 1
fi
BIN_PATH="$(cd "$(dirname "$REPO/$BINARY")" && pwd)/$(basename "$BINARY")"

mkdir -p "$APPDIR/usr/bin" \
         "$APPDIR/usr/share/applications" \
         "$APPDIR/usr/share/icons/hicolor/256x256/apps" \
         "$REPO/releases"

# Binario compilado como punto de entrada
install -m 0755 "$BIN_PATH" "$APPDIR/usr/bin/scenecutbatch"

# Icono (logo del proyecto)
cp "$REPO/assets/logo.png" "$APPDIR/usr/share/icons/hicolor/256x256/apps/scenecutbatch.png"
cp "$REPO/assets/logo.png" "$APPDIR/scenecutbatch.png"

# Entrada de escritorio
cp "$APPDIR/scenecutbatch.desktop" "$APPDIR/usr/share/applications/scenecutbatch.desktop"

chmod +x "$APPDIR/AppRun"

# appimagetool (se descarga si no está disponible)
if command -v appimagetool >/dev/null 2>&1; then
    APPIMAGETOOL="appimagetool"
else
    curl -fsSL -o /tmp/appimagetool \
        https://github.com/AppImage/AppImageKit/releases/download/continuous/appimagetool-x86_64.AppImage
    chmod +x /tmp/appimagetool
    APPIMAGETOOL="/tmp/appimagetool"
fi

ARCH=x86_64 APPIMAGE_EXTRACT_AND_RUN=1 "$APPIMAGETOOL" "$APPDIR" "$OUT"
echo "AppImage creada: $OUT"
