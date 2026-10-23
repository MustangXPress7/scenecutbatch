# Scene Cut Batch — Guía Rápida (Portable)

![Scene Cut Batch logo](assets/logo.png)


## ¿Qué es?

SceneCutBatch detecta cortes de escena en carpetas de video y genera archivos
FCP7 XML que importan los editores de vídeo profesionales. Cada XML crea:

- **Secuencia maestra** con todos los cortes en orden
- **Subclips virtuales** que apuntan al medio original (sin duplicar nada)

---

## Versión Windows (portable — sin instalación)

Archivo: `SceneCutBatch-Windows-Portable.zip`

1. Descomprime el ZIP en cualquier carpeta.
2. Haz doble clic en `scenecutbatch.exe` → se abre la interfaz gráfica.
3. O ejecuta desde terminal:
   ```
   scenecutbatch.exe "C:\Footage\Dia1"
   scenecutbatch.exe "C:\Footage\Dia1" --out-dir "D:\Salida\Cuts"
   scenecutbatch.exe "C:\Footage" --recursive --threshold 30 --dry-run
   ```

No necesitas instalar Python ni nada más. El ejecutable lo trae todo incluido.

---

## Versión Mac (portable — usa Python 3 de macOS)

Archivos: `run_mac.sh`, `install_mac.sh`, `src/scenecutbatch/`

macOS ya trae Python 3. Solo necesitas instalar las librerías una vez:

1. Abre Terminal en la carpeta del proyecto.
2. Ejecuta:
   ```bash
   chmod +x run_mac.sh install_mac.sh
   ./install_mac.sh
   ```
3. Luego ejecuta:
   ```bash
   ./run_mac.sh /ruta/a/tus/clips
   ```
4. O abre la interfaz gráfica con doble clic en `gui.py` o:
   ```bash
   python3 src/scenecutbatch/gui.py
   ```

ffmpeg es opcional (recomendado para timecodes exactos): `brew install ffmpeg`

---

## Opciones de línea de comandos

| Bandera | Qué hace | Por defecto |
|---------|----------|-------------|
| `INPUT_DIR` | Carpeta de videos (requerida) | — |
| `--out-dir` | Carpeta de salida XML | `<input>/cuts` |
| `--threshold` | Sensibilidad (menor = más cortes) | `27.0` |
| `--min-scene-len` | Min largo escena (frames) | `15` |
| `--recursive` | Buscar en subcarpetas | `false` |
| `--extensions` | Extensiones separadas por coma | `mp4,mov,mxf,avi,mkv,webm` |
| `--dry-run` | Listar cortes, no escribir archivos | `false` |
| `--json-progress` | Progreso en JSON a stdout | `false` |
| `--config` | Archivo YAML de configuración | — |
| `--confidence` | Marcadores G/Y/R (v1: no-op) | `false` |
| `--version` | Mostrar versión y salir | — |

---

## Qué produce

Por cada `vacacion.mp4` se genera `vacacion_cuts.xml` que al importar en
un editor de vídeo profesional crea:

- Un contenedor (bin) con el nombre del clip
- Una secuencia maestra con todos los cortes en orden
- Subclips virtuales (uno por escena) apuntando al medio original

---

## Sin comprometer nada

- No se modifica el registro de Windows.
- No se instala nada en el sistema (solo librerías Python en el entorno local).
- Puedes borrar la carpeta y se desinstala por completo.
- Funciona sin conexión a internet (una vez instaladas las dependencias).

**Hecho por JMW Studio.**
