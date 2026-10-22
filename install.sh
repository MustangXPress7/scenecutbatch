#!/usr/bin/env bash
set -euo pipefail

echo "========================================"
echo " SceneCutBatch - Instalador (Mac/Linux)"
echo "========================================"
echo

# Verificar Python
if ! command -v python3 &> /dev/null; then
    echo "ERROR: Python 3 no encontrado. Instala Python 3.10+ desde https://python.org"
    exit 1
fi

echo "[1/4] Instalando dependencias del proyecto..."
pip3 install -e .[dev]

echo "[2/4] Instalando PyInstaller..."
pip3 install pyinstaller

echo "[3/4] Construyendo ejecutable (puede tardar unos minutos)..."
pyinstaller scenecutbatch.spec --clean --noconfirm

echo "[4/4] Listo."
echo
echo "========================================"
echo "  EJECUTABLE CREADO"
echo "========================================"
echo
echo "   Ruta: dist/scenecutbatch"
echo
echo "  COMO USARLO:"
echo "   ./dist/scenecutbatch detect /ruta/a/tus/clips"
echo
echo "  Opciones utiles:"
echo "    --out-dir /ruta/salida     Carpeta de salida (defecto: <input>/cuts)"
echo "    --threshold 30             Umbral de deteccion (defecto: 27.0)"
echo "    --min-scene-len 15         Longitud minima de escena en frames"
echo "    --dry-run                  Solo lista cortes, no escribe archivos"
echo "    --json-progress            Progreso en JSON"
echo "    --config config.yaml       Archivo de configuracion YAML"
echo
echo "  NOTA: ffmpeg no es obligatorio. Si no lo tienes, la herramienta funciona"
echo "         igual pero sin metadatos de FPS/duracion de cada clip."
echo
echo "  Para instalar ffmpeg en Mac:"
echo "    brew install ffmpeg
echo
echo "  En Mac puedes necesitar: chmod +x dist/scenecutbatch"
