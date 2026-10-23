"""Catálogo de cadenas bilingüe (EN/ES) para la interfaz de SceneCutBatch."""

from __future__ import annotations

import locale
from typing import Optional


SUPPORTED_LANGUAGES = ("en", "es")          # scanner.py constant convention
_DEFAULT_LANGUAGE = "es"                     # D-35: safe non-English fallback

STRINGS = {                                   # {key: {"en": ..., "es": ...}} — flat dict-of-dicts
    "window.title": {
        "en": "Scene Cut Batch — Scene cut detection",
        "es": "Scene Cut Batch — Detección de cortes de escena",
    },
    "app.subtitle": {
        "en": "Detect scene cuts and generate FCP7 XML for professional video editors",
        "es": "Detecta cortes de escena y genera XML FCP7 para editores de vídeo profesionales",
    },
    "signature": {
        "en": "Made by JMW Studio",
        "es": "Hecho por JMW Studio",
    },
    "lang.label": {
        "en": "Language:",
        "es": "Idioma:",
    },
    "form.input.label": {
        "en": "Video folder:",
        "es": "Carpeta de videos:",
    },
    "form.output.label": {
        "en": "Output folder:",
        "es": "Carpeta de salida:",
    },
    "form.browse": {
        "en": "Browse…",
        "es": "Examinar…",
    },
    "options.title": {
        "en": "Detection options",
        "es": "Opciones de detección",
    },
    "options.threshold": {
        "en": "Threshold (lower = more cuts):",
        "es": "Umbral (menor = más cortes):",
    },
    "options.min_scene_len": {
        "en": "Min. scene length (frames):",
        "es": "Mín. largo de escena (frames):",
    },
    "options.recursive": {
        "en": "Search subfolders (--recursive)",
        "es": "Buscar en subcarpetas (--recursive)",
    },
    "options.dry_run": {
        "en": "List cuts only, do not write (--dry-run)",
        "es": "Solo listar cortes, no escribir (--dry-run)",
    },
    "options.json_progress": {
        "en": "JSON progress (--json-progress)",
        "es": "Progreso en JSON (--json-progress)",
    },
    "options.confidence": {
        "en": "G/Y/R markers (--confidence, v1.1)",
        "es": "Marcadores G/Y/R (--confidence, v1.1)",
    },
    "button.run": {
        "en": "Run detection",
        "es": "Ejecutar detección",
    },
    "log.label": {
        "en": "Output:",
        "es": "Salida:",
    },
    "status.ready": {
        "en": "Ready",
        "es": "Listo",
    },
    "status.running": {
        "en": "Running…",
        "es": "Ejecutando…",
    },
    "status.completed": {
        "en": "Completed successfully",
        "es": "Completado con éxito",
    },
    "status.error": {
        "en": "Error",
        "es": "Error",
    },
    "dialog.error.title": {
        "en": "Error",
        "es": "Error",
    },
    "dialog.error.no_folder": {
        "en": "Select a video folder first.",
        "es": "Selecciona una carpeta de videos primero.",
    },
    "dialog.done.title": {
        "en": "Done",
        "es": "Listo",
    },
    "dialog.done.body": {
        "en": "Detection completed. XML files were saved to {path}.",
        "es": "La detección se completó. Los archivos XML se guardaron en {path}.",
    },
    "filedialog.input.title": {
        "en": "Select video folder",
        "es": "Seleccionar carpeta de videos",
    },
    "filedialog.output.title": {
        "en": "Select output folder",
        "es": "Seleccionar carpeta de salida",
    },
    "log.start": {
        "en": "Start: {total} clips",
        "es": "Inicio: {total} clips",
    },
    "log.clip_start": {
        "en": "[{index}/{total}] {clip} started",
        "es": "[{index}/{total}] {clip} iniciado",
    },
    "log.clip_done": {
        "en": "[{index}/{total}] {clip} done ({scenes} scenes, ETA {eta_sec:.0f}s)",
        "es": "[{index}/{total}] {clip} listo ({scenes} escenas, ETA {eta_sec:.0f}s)",
    },
    "log.clip_error": {
        "en": "[{index}/{total}] {clip} ERROR: {error}",
        "es": "[{index}/{total}] {clip} ERROR: {error}",
    },
    "log.done": {
        "en": "Finished: {succeeded} OK, {failed} failed",
        "es": "Finalizado: {succeeded} OK, {failed} fallidos",
    },
}

_current_language: str = _DEFAULT_LANGUAGE     # module-level mutable state


def normalize_language(locale_string: Optional[str]) -> str:
    """Return 'en' or 'es' from a locale string; fall back to Spanish."""
    if not locale_string:
        return _DEFAULT_LANGUAGE
    code = locale_string.replace("-", "_").lower()
    if code.startswith("en"):
        return "en"
    return _DEFAULT_LANGUAGE


def detect_language() -> str:
    """Detect the OS language on start (D-35)."""
    best: Optional[str] = None
    try:
        loc = locale.getdefaultlocale()      # deprecated on 3.11+, removed later
        if isinstance(loc, tuple) and len(loc) >= 2 and loc[0]:
            best = loc[0]
    except (ValueError, TypeError, AttributeError):
        best = None
    if best is None:
        try:
            loc = locale.getlocale()
            if isinstance(loc, tuple) and len(loc) >= 2 and loc[0]:
                best = loc[0]
        except (ValueError, TypeError, AttributeError):
            best = None
    if best is None:
        best = _DEFAULT_LANGUAGE
    return normalize_language(best)


def set_language(lang: str) -> str:
    """Set the active language and return it."""
    global _current_language
    _current_language = lang if lang in SUPPORTED_LANGUAGES else _DEFAULT_LANGUAGE
    return _current_language


def current_language() -> str:
    """Return the active language code."""
    return _current_language


def t(key: str, **kwargs) -> str:
    """Look up a translated string; format with kwargs; fall back to the key."""
    entry = STRINGS.get(key)
    if not entry:
        return key
    text = entry.get(_current_language) or entry.get("en") or next(iter(entry.values()))
    if kwargs:
        try:
            return text.format(**kwargs)
        except (KeyError, IndexError, ValueError, TypeError):
            return text
    return text
