# Scene Cut Batch — Guía de uso (aplicación ejecutable)

![Scene Cut Batch logo](assets/logo.png)


## ¿Qué es?

SceneCutBatch detecta cortes de escena en carpeta de videos y genera archivos
FCP7 XML (xmeml) que importan los editores de vídeo profesionales. Cada XML crea un
contenedor con:

- **Secuencia maestra** con todos los cortes en orden
- **Subclips virtuales** (uno por escena) que apuntan al medio original
  (no duplica nada)

Ideal para editores que pasan horas pasando clip por clip por la detección uno a uno; salida en FCP7 XML (xmeml v5).

---

## 1. Instalación (una sola vez)

### Windows

1. Descarga/clona esta carpeta en tu PC.
2. Haz doble clic en **`install.bat`**.
3. El script instala Python dependencias, PyInstaller y construye el
   ejecutable en `dist/scenecutbatch.exe`.

### macOS

**Opción A — Homebrew (recomendado):**

macOS se distribuye exclusivamente vía Homebrew tap:

```bash
brew tap MustangXPress7/tap
brew install scenecutbatch
```

Luego ejecuta:

```bash
scenecutbatch detect "/ruta/a/tus/clips"
```

**Opción B — Desde código fuente:**

1. Abre Terminal en la carpeta del proyecto.
2. Ejecuta:

   ```bash
   pip3 install -e .
   ```

3. Ejecuta el ejecutable:

   ```bash
   ./dist/scenecutbatch /ruta/a/tus/clips
   ```

> **ffmpeg (opcional pero recomendado):** La herramienta funciona sin ffmpeg,
> pero con ffmpeg obtiene los FPS exactos de cada video (timecodes precisos).
> - Windows: `winget install ffmpeg`
> - Mac: `brew install ffmpeg`

---

## 2. Uso

### Windows

Haz doble clic en **`run.bat`**, o desde la terminal:

```cmd
dist\scenecutbatch.exe "C:\Footage\Dia1"
dist\scenecutbatch.exe "C:\Footage\Dia1" --out-dir "D:\Salida\Cuts"
dist\scenecutbatch.exe "C:\Footage" --recursive --threshold 30 --dry-run
```

### macOS / Linux

```bash
./dist/scenecutbatch /ruta/a/tus/clips
./dist/scenecutbatch /ruta/a/tus/clips --out-dir /ruta/salida/cuts
./dist/scenecutbatch /ruta/a/tus/clips --recursive --threshold 30
```

### Banderas principales

| Bandera | Qué hace | Valor por defecto |
|---------|----------|-------------------|
| `INPUT_DIR` | Carpeta con los videos (requerida) | — |
| `--out-dir` | Carpeta donde se escriben los XML | `<input>/cuts` |
| `--threshold` | Sensibilidad de detección (menor = más cortes) | `27.0` |
| `--min-scene-len` | Longitud mínima de escena en frames | `15` |
| `--recursive` | Buscar videos en subcarpetas | `false` |
| `--extensions` | Extensiones a procesar (coma separada) | `mp4,mov,mxf,avi,mkv,webm` |
| `--dry-run` | Listar cortes detectados sin escribir archivos | `false` |
| `--json-progress` | Progreso en formato JSON (para GUI/automatización) | `false` |
| `--config` | Archivo YAML con configuración | — |
| `--confidence` | Activar marcadores G/Y/R (v1: no-op, se añade en v1.1) | `false` |
| `--version` | Mostrar versión y salir | — |

---

## 3. Qué produce

Por cada video `vacacion.mp4` se genera un archivo `vacacion_cuts.xml` en la
carpeta de salida. Al importarlo en tu editor de vídeo:

- Se crea un **contenedor (bin)** con el nombre del clip.
- Dentro, una **secuencia maestra** con todos los cortes en línea de tiempo.
- **Subclips virtuales** — uno por escena detectada — que apuntan al archivo
  original (sin duplicar medios ni ocupar espacio extra).

---

## 4. Ejemplo de salida

```
C:\Footage\
 ├─ vacacion.mp4
  └─ cuts\
       └─ vacacion_cuts.xml   ← importar este en tu editor
```

---

## 5. Solución de problemas

| Problema | Solución |
|----------|----------|
| `Python no encontrado` | Instala Python 3.10+ desde https://python.org y marca "Add Python to PATH" |
| `scenedetect no encontrado` | Vuelve a ejecutar `install.bat` / `install.sh` |
| El ejecutable no abre / se cierra rápido | Ejecuta desde terminal para ver el mensaje de error real |
| Los XML no se escriben | Verifica que la carpeta de salida exista y tengas permisos de escritura |
| Timecodes parecen incorrectos | Instala ffmpeg (proporciona FPS reales del video) |
| Tu editor no importa el XML | Abre el XML con un editor de texto y verifica que empiece con `<?xml version="1.0" encoding="UTF-8"?>` y `<xmeml version="5">` |

---

## 6. Tecnología

- **Python 3.10+**, empaquetado con **PyInstaller**
- **PySceneDetect 0.6.x** — detección de cortes por diferencia de contenido
- **OpenCV** — backend de lectura de video
- **Typer** — interfaz de línea de comandos
- **xml.etree.ElementTree** — generación de XML FCP7 (xmeml v5)
- Licencia: Apache-2.0

**Hecho por JMW Studio.**

---

¿Necesitas algo más? Puedo ayudarte a crear un instalador más elaborado (Inno Setup para Windows, .pkg para Mac) o a añadir una interfaz gráfica simple.
