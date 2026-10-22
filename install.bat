@echo off
chcp 65001 >nul
setlocal enabledelayedexpansion

echo ========================================
echo  SceneCutBatch - Instalador (Windows)
echo ========================================
echo.

:: Verificar Python
python --version >nul 2>&1
if %ERRORLEVEL% neq 0 (
    echo ERROR: Python no encontrado. Instala Python 3.10+ desde https://python.org
    pause
    exit /b 1
)

echo [1/4] Instalando dependencias del proyecto...
pip install -e .[dev]
if %ERRORLEVEL% neq 0 (
    echo ERROR: Fallo al instalar dependencias del proyecto.
    pause
    exit /b 1
)

echo [2/4] Instalando PyInstaller...
pip install pyinstaller
if %ERRORLEVEL% neq 0 (
    echo ERROR: Fallo al instalar PyInstaller.
    pause
    exit /b 1
)

echo [3/4] Construyendo ejecutable (puede tardar unos minutos)...
pyinstaller scenecutbatch.spec --clean --noconfirm
if %ERRORLEVEL% neq 0 (
    echo ERROR: Fallo al construir el ejecutable.
    pause
    exit /b 1
)

echo [4/4] Listo.
echo.
echo ========================================
echo  EJECUTABLE CREADO
echo ========================================
echo.
echo   Ruta: dist\scenecutbatch.exe
echo.
echo  COMO USARLO:
echo   dist\scenecutbatch.exe detect "C:\ruta\a\tus\clips"
echo.
echo   Opciones utiles:
echo     --out-dir "D:\salida"      Carpeta de salida (por defecto: <input>/cuts)
echo     --threshold 30             Umbral de deteccion (defecto: 27.0)
echo     --min-scene-len 15         Longitud minima de escena en frames
echo     --dry-run                  Solo lista los cortes, no escribe archivos
echo     --json-progress            Progreso en JSON (para integracion)
echo     --config config.yaml       Archivo de configuracion YAML
echo.
echo  NOTA: ffmpeg no es obligatorio. Si no lo tienes instalado, la herramienta
echo         funciona igual pero sin metadatos de FPS/duracion de cada clip.
echo.
echo  Para instalar ffmpeg en Windows:
echo     winget install ffmpeg   (o descarga desde https://ffmpeg.org)
echo.
pause
endlocal
