#!/usr/bin/env bash
set -euo pipefail

echo "========================================"
echo " SceneCutBatch - Instalador (Linux)"
echo "========================================"
echo

# Verificar Python 3
if ! command -v python3 &> /dev/null; then
    echo "ERROR: Python 3 no encontrado. Instala Python 3.10+ desde https://python.org"
    exit 1
fi

PYTHON_VERSION=$(python3 --version 2>&1 | cut -d' ' -f2)
echo "Python detectado: $PYTHON_VERSION"

# Verificar ffmpeg (opcional pero recomendado para metadatos de FPS/duracion)
if ! command -v ffprobe &> /dev/null; then
    echo "ADVERTENCIA: ffprobe no encontrado. La herramienta funcionara pero"
    echo "             sin metadatos de FPS/duracion de cada clip."
    echo "   Para instalar ffmpeg en Debian/Ubuntu:"
    echo "     sudo apt update && sudo apt install -y ffmpeg"
    echo
else
    echo "ffprobe detectado: OK"
fi

echo "[1/3] Instalando dependencias del sistema..."
if command -v apt-get &> /dev/null; then
    sudo apt-get update
    sudo apt-get install -y python3-pip ffmpeg
elif command -v dnf &> /dev/null; then
    sudo dnf install -y python3-pip ffmpeg
elif command -v yum &> /dev/null; then
    sudo yum install -y python3-pip ffmpeg
else
    echo "ADVERTENCIA: No se detecto gestor de paquetes compatible (apt/dnf/yum)."
    echo "             Instala manualmente: python3-pip, ffmpeg"
fi

echo "[2/3] Instalando dependencias de Python..."
pip3 install -e .[dev]
pip3 install scenedetect[opencv]

echo "[3/3] Configurando permisos de ejecucion..."
chmod +x run.sh

echo
echo "========================================"
echo "  INSTALACION COMPLETADA"
echo "========================================"
echo
echo "  COMO USARLO:"
echo "   ./run.sh detect /ruta/a/tus/clips"
echo
echo "  Opciones utiles:"
echo "    --out-dir /ruta/salida     Carpeta de salida (defecto: <input>/cuts)"
echo "    --threshold 30             Umbral de deteccion (defecto: 27.0)"
echo "    --min-scene-len 15         Longitud minima de escena en frames"
echo "    --dry-run                  Solo lista cortes, no escribe archivos"
echo "    --json-progress            Progreso en JSON"
echo "    --config config.yaml       Archivo de configuracion YAML"
echo
