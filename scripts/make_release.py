"""Script de empaquetado de releases de Scene Cut Batch por sistema operativo.

Genera un archivo .zip por plataforma conteniendo el ejecutable y los
archivos necesarios para ejecutar la aplicación sin instalación previa.

Uso:
    python scripts/make_release.py --version 0.1.0 --platform windows
    python scripts/make_release.py --version 0.1.0 --platform all
"""

from __future__ import annotations

import argparse
import shutil
import sys
import zipfile
from pathlib import Path
from typing import Optional

REPO_ROOT = Path(__file__).resolve().parent.parent
DIST_DIR = REPO_ROOT / "dist"
RELEASE_DIR = REPO_ROOT / "releases"


def _exe_name(platform: str) -> str:
    if platform == "windows":
        return "scenecutbatch.exe"
    return "scenecutbatch"


def _files_for_platform(platform: str) -> list[tuple[Path, str]]:
    """Devuelve lista de (origen, destino_en_zip) para cada plataforma."""
    files: list[tuple[Path, str]] = []

    exe = DIST_DIR / _exe_name(platform)
    if exe.exists():
        files.append((exe, _exe_name(platform)))

    # Scripts de lanzamiento por plataforma
    launchers = {
        "windows": ["run.bat", "install.bat"],
        "macos": ["run_mac.sh", "SceneCutBatch.command", "install.sh"],
        "linux": ["run.sh", "install_linux.sh"],
    }
    for launcher in launchers.get(platform, []):
        p = REPO_ROOT / launcher
        if p.exists():
            files.append((p, launcher))

    # Documentación
    for doc in ["README.md", "LICENSE", "pyproject.toml"]:
        p = REPO_ROOT / doc
        if p.exists():
            files.append((p, doc))

    # Carpeta assets (logo)
    assets_dir = REPO_ROOT / "assets"
    if assets_dir.exists():
        for f in assets_dir.iterdir():
            if f.is_file():
                files.append((f, f"assets/{f.name}"))

    # Carpeta src (código fuente, para modo desarrollo)
    src_dir = REPO_ROOT / "src"
    if src_dir.exists():
        for f in src_dir.rglob("*"):
            if f.is_file() and f.suffix == ".py":
                files.append((f, f"src/{f.relative_to(src_dir)}"))

    return files


def make_release(version: str, platform: str) -> Optional[Path]:
    """Crea un release zip para la plataforma indicada."""
    release_name = f"SceneCutBatch-{version}-{platform.capitalize()}"
    zip_path = RELEASE_DIR / f"{release_name}.zip"

    RELEASE_DIR.mkdir(parents=True, exist_ok=True)

    files = _files_for_platform(platform)
    if not files:
        print(f"No files found for platform '{platform}'", file=sys.stderr)
        return None

    print(f"Creando release: {zip_path.name}")
    with zipfile.ZipFile(zip_path, "w", zipfile.ZIP_DEFLATED) as zf:
        for src, arcname in files:
            zf.write(src, arcname)
            print(f"  + {arcname}")

    print(f"Release listo: {zip_path}")
    return zip_path


def main() -> None:
    parser = argparse.ArgumentParser(description="Empaqueta releases de Scene Cut Batch")
    parser.add_argument("--version", required=True, help="Versión del release (ej. 0.1.0)")
    parser.add_argument(
        "--platform",
        choices=["windows", "macos", "linux", "all"],
        default="all",
        help="Plataforma objetivo (default: all)",
    )
    args = parser.parse_args()

    platforms = ["windows", "macos", "linux"] if args.platform == "all" else [args.platform]

    for platform in platforms:
        make_release(args.version, platform)


if __name__ == "__main__":
    main()
