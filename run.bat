@echo off
chcp 65001 >nul
cd /d "%~dp0"
set "EXE=dist\scenecutbatch.exe"
if not exist "%EXE%" set "EXE=scenecutbatch.exe"
if not exist "%EXE%" (
    echo ERROR: No se encontro scenecutbatch.exe ^(ni en dist\ ni en esta carpeta^)
    echo Ejecuta primero install.bat para construir el ejecutable.
    pause
    exit /b 1
)
"%EXE%" %*
