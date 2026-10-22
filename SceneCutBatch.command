#!/bin/bash
# =============================================================================
# SceneCutBatch — Lanzador para Mac (doble clic para ejecutar)
# =============================================================================

# Obtener la carpeta donde está este script
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$SCRIPT_DIR"

echo "============================================="
echo "  SceneCutBatch — Detección de cortes"
echo "============================================="
echo ""

# 1. Verificar Python 3
if ! command -v python3 &> /dev/null; then
    echo "❌ Python 3 no encontrado."
    echo "   Instálalo desde https://python.org"
    echo ""
    read -p "Presiona Enter para salir..."
    exit 1
fi

echo "✓ Python 3 encontrado: $(python3 --version)"

# 2. Instalar dependencias si faltan
echo ""
echo "▶ Verificando dependencias..."
if ! python3 -c "import scenedetect" 2>/dev/null; then
    echo "   Instalando dependencias (solo la primera vez)..."
    pip3 install -e .[dev] 2>/dev/null || pip3 install scenedetect[opencv] typer rich pyyaml 2>/dev/null
    echo "   ✓ Listo"
else
    echo "   ✓ Dependencias ya instaladas"
fi

# 3. Lanzar la interfaz gráfica (prefiere el ejecutable empaquetado)
echo ""
if [ -f "dist/scenecutbatch" ]; then
    exec ./dist/scenecutbatch
elif [ -f "./scenecutbatch" ]; then
    exec ./scenecutbatch
fi
echo "▶ Iniciando interfaz gráfica (modo desarrollo)..."
python3 src/scenecutbatch/gui.py

echo ""
echo "Gracias por usar SceneCutBatch"
