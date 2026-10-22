#!/usr/bin/env bash
set -euo pipefail
cd "$(dirname "$0")"
if [ -f "dist/scenecutbatch" ]; then
    exec ./dist/scenecutbatch "$@"
elif [ -f "./scenecutbatch" ]; then
    exec ./scenecutbatch "$@"
else
    echo "ERROR: No se encontro el ejecutable scenecutbatch"
    echo "Ejecuta primero ./install.sh para construirlo."
    exit 1
fi
