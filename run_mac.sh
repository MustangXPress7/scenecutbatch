#!/usr/bin/env bash
# =============================================================================
# SceneCutBatch — Instalador Portable para Mac
# =============================================================================
# Este script instala las dependencias necesarias para ejecutar SceneCutBatch
# en macOS. Solo necesitas Python 3 (ya viene en macOS) y conexión a internet.
# =============================================================================

set -euo pipefail

echo "============================================="
echo " SceneCutBatch — Instalador (macOS)"
echo "============================================="
echo

# Verificar Python 3
if ! command -v python3 &> /dev/null; then
    echo "ERROR: Python 3 no encontrado."
    echo "Instala Python 3 desde https://python.org"
    exit 1
fi

echo "[1/4] Verificando Python 3..."
python3 --version

echo "[2/4] Instalando dependencias del proyecto..."
pip3 install -e .[dev]

echo "[3/4] Listo."
echo
echo "============================================="
echo "  INSTALACIÓN COMPLETADA"
echo "============================================="
echo
echo "  COMO USARLO:"
echo "    Ejecuta: ./run_mac.sh /ruta/a/tus/clips"
echo "    O desde la carpeta: ./run_mac.sh ."
echo
echo "  Opciones disponibles:"
echo "    --out-dir CARPETA     Carpeta de salida (defecto: <input>/cuts)"
echo "    --threshold 30        Umbral de detección (defecto: 27.0)"
echo "    --min-scene-len 15    Largo mínimo de escena en frames"
echo "    --recursive           Buscar en subcarpetas"
echo "    --dry-run             Solo listar cortes, no escribir archivos"
echo "    --json-progress       Progreso en JSON"
echo "    --version             Mostrar versión"
echo
echo "  OPCIÓN GUI (doble clic):"
echo "    Ejecuta: python3 src/scenecutbatch/gui.py"
echo
echo "  ffmpeg (opcional pero recomendado):"
echo "    brew install ffmpeg
echo "    (Si no lo tienes, la herramienta funciona igual pero asume 30 fps)"
echo
