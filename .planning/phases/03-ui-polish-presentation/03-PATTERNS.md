# Phase 03: UI polish & public-facing presentation — Pattern Map

**Mapped:** 2026-10-23
**Files analyzed:** 22 (1 new code module + 1 new test file + 20 copy/layout modifications)
**Analogs found:** 21 / 22 (the new i18n module has no true analog — see "No Analog Found")

> **No research file exists for this phase.** All patterns below are extracted from
> git-tracked source in this repo. Every analog path listed was verified with
> `git ls-files -- <path>` (non-empty = tracked), so no gitignored mirror paths are emitted.

---

## File Classification

| New/Modified File | Role | Data Flow | Closest Analog | Match Quality |
|-------------------|------|-----------|----------------|---------------|
| `src/scenecutbatch/i18n.py` **(NEW)** | module (utility/config) | transform (lookup) | `src/scenecutbatch/media/scanner.py` | role-match |
| `tests/test_i18n.py` **(NEW)** | test | request-response | `tests/test_smoke.py` + `tests/conftest.py` | role-match |
| `src/scenecutbatch/gui.py` | component (Tk view) | event-driven | itself (lines 1-312) — restructure in place | exact (self-analog) |
| `src/scenecutbatch/cli.py` | controller (Typer) | request-response | itself (lines 17-20, 154-190, 206-213) | exact (self-analog) |
| `src/scenecutbatch/__init__.py` | package init (docstring) | static copy | itself (line 1) + `src/scenecutbatch/core/__init__.py` | exact |
| `src/scenecutbatch/export/xml_builder.py` | service (docstrings) | file-I/O | itself (lines 1, 20-23, 42-49) | exact |
| `src/scenecutbatch/media/scanner.py` | service (docstrings) | transform | itself (line 1) | exact |
| `README.md` | documentation copy | static | itself (lines 1-41, 194-202) | exact |
| `README_USO.md` | documentation copy (ES) | static | itself (lines 1-17, 87-97) | exact |
| `README_PORTABLE.md` | documentation copy (ES) | static | itself (lines 1-13, 76-84) | exact |
| `docs/01..10-*.md` | documentation copy | static | `docs/10-DECISIONS.md` (table form) | role-match |
| `docs/09-INTEGRATION-TO-ESQUELETOEDIT.md` | documentation (rework) | static | `docs/06-OUTPUT-FORMAT.md` | role-match |
| `pyproject.toml` | config metadata | static | itself (lines 6-11) | exact |
| `packaging/debian/DEBIAN/control` | packaging metadata | static | itself (lines 7-11) | exact |
| `packaging/rpm/scenecutbatch.spec` | packaging metadata | static | itself (lines 4-17, 49-50) | exact |
| `packaging/appimage/AppDir/scenecutbatch.desktop` | packaging metadata | static | itself (lines 1-8) | exact |
| `run.bat`, `run.sh` | launcher script | request-response | themselves | exact |
| `SceneCutBatch.command`, `run_mac.sh` | launcher script | request-response | themselves | exact |
| `install.bat`, `install.sh`, `install_linux.sh` | installer script | request-response | themselves | exact |
| `HANDOFF.md` | repo text (audit) | static | `docs/02-ARCHITECTURE.md` | role-match |
| `src/scenecutbatch/core/batch.py` | service (verify only) | streaming | itself (progress dict contract) | exact |

**Note on "self-analog":** most of this phase's work is re-editing *existing* files
in place. For those, the analog is the file's own current code — the excerpts below
pin the exact line ranges the planner must read and the exact anchors to replace.

---

## Pattern Assignments

### `src/scenecutbatch/i18n.py` (NEW — module, transform/lookup)

**Analog:** `src/scenecutbatch/media/scanner.py` (structural conventions for a small, stdlib-only package module) + `src/scenecutbatch/core/models.py` (typed-default conventions).

**Why this analog:** scanner.py is the codebase's canonical shape for a leaf module —
one-line docstring, `from __future__ import annotations`, stdlib-only imports, one
module-level constant, one public function that normalizes input the same way
`detect_language()` must normalize a locale string. It has zero third-party
imports, which matters because the i18n module must be importable before tkinter
and must not add a dependency to `pyproject.toml` (current deps: scenedetect,
typer, rich, pyyaml only).

**Module skeleton pattern — `media/scanner.py` lines 1-28:**
```python
"""Media scanning (reuse EsqueltoEdit patterns)."""   # ← line 1: one-line docstring

from __future__ import annotations

from pathlib import Path
from typing import List

from ..core.models import DetectConfig


SUPPORTED_EXTENSIONS = {".mp4", ".mov", ".mxf", ".avi", ".mkv", ".webm"}  # module-level constant


def scan_folder(input_dir: Path, config: DetectConfig) -> List[Path]:
    """Return list of video files in input_dir.

    TODO (Phase 1): implement recursive walk, extension filter (case-insensitive),
    ffprobe validation.
    """
    input_dir = Path(input_dir)
    exts = {e.lower().lstrip(".") for e in config.extensions}
    ...
```
Conventions to copy: `from __future__ import annotations` is line 3 in every module;
constants are UPPER_SNAKE at module scope after imports; every public function has
a Google-style one-line-summary docstring; private helpers use a leading underscore
(`_parse_extensions`, `_clean_text`, `_pathurl`).

**Decision-derived API skeleton (from CONTEXT.md D-35 — no research file exists):**
The catalog + `t()` API is locked by the user decision, so the planner writes it
directly rather than copying an analog. Required surface:
```python
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
    "signature": {"en": "Made by JMW Studio", "es": "Hecho por JMW Studio"},
    # ... one entry per GUI string, per D-35 scope:
    # title, subtitle, form labels, checkbox labels, buttons, dialogs, log prefixes,
    # progress event lines, status line, language switcher label, file-dialog titles
}

_current_language: str = _DEFAULT_LANGUAGE     # module-level mutable state


def normalize_language(locale_string: Optional[str]) -> str:
    """Return 'en' or 'es' from a locale string; fall back to Spanish.

    scanner.py normalization convention: strip/case-fold, tolerate None and
    malformed input without raising.
    """
    if not locale_string:
        return _DEFAULT_LANGUAGE
    code = locale_string.replace("-", "_").lower()
    if code.startswith("en"):
        return "en"
    return _DEFAULT_LANGUAGE


def detect_language() -> str:
    """Detect the OS language on start (D-35)."""
    try:
        loc = locale.getdefaultlocale()      # D-35: explicitly named method
    except (ValueError, TypeError):          # can raise on some platforms/Python 3.11+
        loc = None
    return normalize_language(loc[0] if isinstance(loc, tuple) else None)


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
        except (KeyError, IndexError):
            return text
    return text
```

**Do-not-regress constraints:**
- Do **not** add a third-party dependency (`gettext` from stdlib is fine if the planner prefers it over the dict; D-35 says "string catalog" so a dict is the simpler read).
- Persistence is **deferred** (D-35) — do not write a config file or registry key.
- The GUI rebuild must be instant; no background thread.

**Test analog for this module:** `tests/test_smoke.py` (see dedicated entry below).

---

### `tests/test_i18n.py` (NEW — test)

**Analog:** `tests/test_smoke.py` (exact) for simple no-fixture asserts; `tests/test_cli.py` lines 37-57 for capture/monkeypatch if needed.

**Function-based test pattern — `tests/test_smoke.py` (whole file, 14 lines):**
```python
"""Smoke tests for scaffold (Phase 1 scanner tests moved to test_scanner.py)."""

from scenecutbatch import __version__
from scenecutbatch.core.models import DetectConfig


def test_version():
    assert __version__ == "0.1.0"


def test_detect_config_defaults():
    c = DetectConfig()
    assert c.threshold == 27.0
    assert c.min_scene_len_frames == 15
```
Conventions: module docstring first; `from scenecutbatch.*` absolute imports (enabled by
`pythonpath = ["src"]` in `pyproject.toml` `[tool.pytest.ini_options]`); one `test_*`
function per behavior; plain `assert` with no test class; no `__init__.py` needed in `tests/`.

**Fixture + monkeypatch pattern — `tests/conftest.py` lines 23-32:**
```python
@pytest.fixture
def tmp_input_dir(tmp_path: Path) -> Path:
    """Empty temp directory used as scan_folder input."""
    return tmp_path


@pytest.fixture
def config() -> DetectConfig:
    """DetectConfig with v1 defaults (D-01)."""
    return DetectConfig()
```
Use this shape for a `fresh_i18n` fixture that calls `set_language(...)` and restores
state after the test (module-level `_current_language` is mutated by the API, so tests
must reset it or they will leak ordering-dependent state).

**Required assertions to plan for (no analog, derived from D-35 + PRES-05):**
- `detect_language()` returns `"en"` for an English locale and `"es"` otherwise/None.
- Every key in `STRINGS` has BOTH `en` and `es` entries (guard against half-translated catalogs — this is the most valuable test in the file).
- `t("missing.key")` returns the key itself (no crash).
- `t("key", name=...)` interpolates format placeholders.
- `set_language("xx")` falls back to `"es"` and does not raise.

---

### `src/scenecutbatch/gui.py` (component, event-driven — layout rework + i18n + signature)

**Analog:** the file itself (312 lines). **Read the whole file once; do not re-read ranges.**

**Imports + module docstring convention (lines 1-14):**
```python
"""Interfaz gráfica simple para Scene Cut Batch (Tkinter)."""

from __future__ import annotations

import json
import sys
import threading
import tkinter as tk
from pathlib import Path
from tkinter import filedialog, messagebox, scrolledtext, ttk
from typing import Optional

from .core.batch import detect_folder
from .core.models import DetectConfig
```
Convention to copy: `from __future__ import annotations` line 3; `from typing import
Optional` imported even though unused today (keep or remove, but match style);
relative sibling import `.core.batch`. New import to add: `from .i18n import t,
detect_language, set_language, SUPPORTED_LANGUAGES`.

**Asset resolution pattern — MUST be reused unchanged (lines 17-31):**
```python
def _asset_path(name: str) -> Path:
    """Resolve an asset path both in development and under PyInstaller."""
    # PyInstaller one-folder bundles assets next to the executable;
    # one-file extracts to sys._MEIPASS at runtime.
    if getattr(sys, "frozen", False):
        base = Path(sys.executable).parent
        candidates = [base / name, Path(sys._MEIPASS) / name]  # type: ignore[attr-defined]
    else:
        base = Path(__file__).resolve().parent.parent.parent  # repo root
        candidates = [base / name]
    for c in candidates:
        if c.exists():
            return c
    # Fallback: return the path even if missing (caller handles it)
    return base / name
```
Do not touch this function during the layout rework — it is verified working on Windows
per `.planning/STATE.md` and is the load-bearing piece for the PyInstaller bundles
(`datas=[('assets/logo.png', 'assets')]` in `scenecutbatch.spec` line 15).

**Window setup + state-variable pattern (lines 37-56):**
```python
    def __init__(self) -> None:
        super().__init__()

        self.title("Scene Cut Batch — Detección de cortes de escena")
        self.geometry("700x520")
        self.minsize(650, 450)

        # Variables de estado
        self.input_dir = tk.StringVar(value="")
        self.output_dir = tk.StringVar(value="")
        self.threshold = tk.DoubleVar(value=27.0)
        self.min_scene_len = tk.IntVar(value=15)
        self.recursive = tk.BooleanVar(value=False)
        self.dry_run = tk.BooleanVar(value=False)
        self.json_progress = tk.BooleanVar(value=False)
        self.confidence = tk.BooleanVar(value=False)
        self.is_running = False

        self._set_window_icon()
        self._build_ui()
```
This is the file section D-31/D-35 modify: add `self._lang = detect_language()` and
call `set_language(self._lang)` before `_build_ui()`; change title to
`self.title(t("window.title"))`; change `geometry`/`minsize` to the new fitting values.

**Widget-reference retention pattern (lines 58-90) — copy exactly:**
```python
    def _set_window_icon(self) -> None:
        """Aplica el logo como icono de ventana y barra de tareas."""
        logo_path = _asset_path("assets/logo.png")
        if logo_path.exists():
            try:
                icon = tk.PhotoImage(file=str(logo_path))
                self.iconphoto(True, icon)
                self._icon_image = icon  # mantener referencia para evitar GC
            except tk.TclError:
                pass
```
```python
        logo_path = _asset_path("assets/logo.png")
        if logo_path.exists():
            try:
                logo_img = tk.PhotoImage(file=str(logo_path))
                # Escalar si es demasiado grande (máx 200 px de ancho)
                if logo_img.width() > 200:
                    ratio = max(1, logo_img.width() // 200)
                    logo_img = logo_img.subsample(ratio, ratio)
                logo_label = ttk.Label(container, image=logo_img)
                logo_label.image = logo_img  # mantener referencia para evitar GC
                logo_label.pack(pady=(0, 10))
            except tk.TclError:
                pass  # Si no se puede cargar la imagen, se omite silenciosamente
```
**CRITICAL for the language switch (D-35):** the language switch *rebuilds the UI*.
Any new reference attribute (logo image, icon, language combobox, signature label)
must be re-assigned on each rebuild, using the same `self.<attr> = widget` /
`widget.image = img` retention idiom, or images get garbage-collected and the logo
vanishes on rebuild. Plan `_build_ui()` to be idempotent (destroy old children or
guard `if container is None`).

**Label / typography / spacing pattern (lines 92-106):**
```python
        # Título
        title = ttk.Label(
            container,
            text="Scene Cut Batch",
            font=("Segoe UI", 16, "bold"),
        )
        title.pack(pady=(0, 8))

        subtitle = ttk.Label(
            container,
            text="Detecta cortes de escena y genera XML para Premiere Pro",   # ← D-32 replace
            font=("Segoe UI", 10),
            foreground="#555555",
        )
        subtitle.pack(pady=(0, 16))
```
The signature credit line (D-36) reuses this exact style: `font=("Segoe UI", 8 or 9)`,
`foreground="#555555"`, `anchor="w"`, packed after the subtitle/logo block.

**Form-row pattern (lines 109-128):**
```python
        row = ttk.Frame(container)
        row.pack(fill=tk.X, pady=4)
        ttk.Label(row, text="Carpeta de videos:", width=18).pack(side=tk.LEFT)
        ttk.Entry(row, textvariable=self.input_dir, width=50).pack(
            side=tk.LEFT, padx=(6, 6), fill=tk.X, expand=True
        )
        ttk.Button(row, text="Examinar…", command=self._browse_input).pack(
            side=tk.LEFT
        )
```

**LabelFrame + checkbox pattern (lines 131-166):**
```python
        opts = ttk.LabelFrame(container, text="Opciones de detección", padding="10")
        opts.pack(fill=tk.X, pady=8)

        row = ttk.Frame(opts)
        row.pack(fill=tk.X, pady=3)
        ttk.Label(row, text="Umbral (menor = más cortes):", width=26).pack(
            side=tk.LEFT
        )
        ttk.Entry(row, textvariable=self.threshold, width=10).pack(side=tk.LEFT)
```

**Run button / progressbar / log / status pattern (lines 169-189):**
```python
        btn_frame = ttk.Frame(container)
        btn_frame.pack(pady=12)
        self.btn_run = ttk.Button(
            btn_frame, text="Ejecutar detección", command=self._on_run, width=22
        )
        self.btn_run.pack()

        self.progress = ttk.Progressbar(container, mode="indeterminate")
        self.progress.pack(fill=tk.X, pady=(4, 0))

        ttk.Label(container, text="Salida:", anchor="w").pack(
            fill=tk.X, pady=(10, 2)
        )
        self.log = scrolledtext.ScrolledText(container, height=12, wrap=tk.WORD)
        self.log.pack(fill=tk.BOTH, expand=True)

        self.status = ttk.Label(container, text="Listo", anchor="w")
        self.status.pack(fill=tk.X, pady=(6, 0))
```
D-31 layout rework: the top-level `container` is `ttk.Frame(self, padding="12")`
with `pack(fill=tk.BOTH, expand=True)`. Two packable regions compete for vertical
space — the `ScrolledText` has `expand=True` and the logo block has a fixed ~233 px
height. The fix must give the log a bounded/contracted height (e.g. fixed
`height=` without `expand=True`, or a `panedwindow`-free single column with the
header as a horizontal `ttk.Frame` holding logo-left/title-right per D-31) so
nothing is clipped at `minsize`. All widget strings become `t("...")` lookups.

**Thread-marshalling pattern — copy verbatim for every translated log line (lines 241-303):**
```python
            def progress(event: dict) -> None:
                ev = event.get("event")
                if ev == "start":
                    self.after(
                        0, lambda: self._log(f"Inicio: {event.get('total')} clips")
                    )
                elif ev == "clip_start":
                    self.after(
                        0,
                        lambda: self._log(
                            f"[{event.get('index')}/{event.get('total')}] "
                            f"{event.get('clip')} iniciado"
                        ),
                    )
                ...
```
Rule for the planner: every `self.*` mutation from `_run_worker`'s thread is wrapped in
`self.after(0, lambda: ...)`. New translated log lines use
`t("log.clip_start", index=..., total=..., clip=...)` inside the same wrapper.

**Error/dialog pattern (lines 212-219, 294-303):**
```python
    def _on_run(self) -> None:
        if not self.input_dir.get():
            messagebox.showerror("Error", "Selecciona una carpeta de videos primero.")
            return
```
```python
        except Exception as exc:  # noqa: BLE001
            self.after(0, lambda: self.status.config(text="Error"))
            self.after(
                0,
                lambda: messagebox.showerror("Error", str(exc)),
            )
        finally:
            self.after(0, lambda: self.progress.stop())
            self.after(0, lambda: self.btn_run.state(["!disabled"]))
            self.is_running = False
```

**Entry-point pattern (lines 306-312):**
```python
def main() -> None:
    app = SceneCutBatchGUI()
    app.mainloop()


if __name__ == "__main__":
    main()
```

**In-app language switch (D-35, new — no analog):** a `ttk.Combobox` or `ttk.Button`
pair in the header row `ttk.Frame`; `command=self._on_language_change` calls
`set_language(code)`, stores `self._lang`, then re-invokes `self._build_ui()` (preserving
`self.input_dir`/`self.output_dir` values — they live in `tk.StringVar`s created once
in `__init__`, so they survive a rebuild; the planner must keep the vars in `__init__`,
not inside `_build_ui()`). Combobox pattern to match existing `ttk` usage: plain
`ttk.Combobox(row, values=["English", "Español"], state="readonly", width=10)`.

**Known non-issue to note in the plan:** fonts hardcode `"Segoe UI"` (Windows-only,
falls back elsewhere) — keep, do not "fix" in this phase (deferred scope).

---

### `src/scenecutbatch/cli.py` (controller, request-response — version footer + help epilog)

**Analog:** the file itself. Relevant ranges only: 17-20, 154-190, 191, 206-213.

**`--version` callback — the D-36 signature insertion point (lines 17-20):**
```python
def _version_callback(value: bool) -> None:
    if value:
        typer.echo(f"Scene Cut Batch {__version__}")
        raise typer.Exit()
```
D-36 adds a footer line: `typer.echo(t("cli.version_footer"))`-equivalent
(`"Hecho por JMW Studio"` / made by) after the version line. **Regression guard:**
`tests/test_cli.py::test_cli_version_prints_0_1_0` asserts
`out.getvalue().strip() == "Scene Cut Batch 0.1.0"` (exact match, no extra lines).
Adding a footer **breaks that test** — the plan must update the assertion to
`in` (or assert both lines). Flag this in the plan's `<verification>` section.

**Option-help pattern (lines 154-190):**
```python
    input_dir: str,
    out_dir: Optional[str] = typer.Option(
        None, "--out-dir", help="Output directory (default: INPUT_DIR/cuts)"
    ),
    threshold: Optional[float] = typer.Option(
        None, "--threshold", help="ContentDetector threshold"
    ),
    ...
    confidence: bool = typer.Option(
        False, "--confidence", help="Enable G/Y/R markers (no-op in v1)"
    ),
```
D-34 (cross-surface consistency) + D-33: help strings are English already; verify none
mention Premiere/EsqueletoEdit and none mention internal phase status. Add the English
epilog via `@app/epilog`-style help text on the `detect` docstring
(`typer.rich_utils`/`@app.command(epilog=...)` equivalent) — D-35 says CLI stays
Spanish-first with an **English epilog**, so the copy goes in the `detect()`
docstring / option help, **not** into the i18n catalog.

**Command docstring — copy location (line 191):**
```python
    """Detect scene cuts in a folder of clips (Scene Cut Batch)."""
```

**stdout-encoding pattern — do not modify (lines 206-213):**
```python
def main() -> None:
    # Configure stdout to use UTF-8 with replace for Windows console compatibility
    import sys
    if hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    if hasattr(sys.stderr, "reconfigure"):
        sys.stderr.reconfigure(encoding="utf-8", errors="replace")
    typer.run(detect)
```
Leave intact — the "Hecho por JMW Studio" footer is already UTF-8-safe because of it.

---

### Copy-only modifications (grouped — role: documentation/config metadata, data flow: static)

These files share one pattern: **edit text in place, no structural change.** The
planner should group them into a single "public copy review" plan with grep-based
verification, not separate files.

**`src/scenecutbatch/__init__.py` line 1:**
```python
"""Scene Cut Batch — batch scene-cut detection for Premiere Pro."""
```
D-32 replacement target (editor-agnostic). Note lines 5-7 re-export the public API —
keep `__all__` untouched (`detect_clip`, `detect_folder`, `BatchResult`,
`DetectionResult`, `DetectConfig`, `Scene`, `__version__`); `tests/test_smoke.py`
asserts `__version__ == "0.1.0"`.

**`src/scenecutbatch/export/xml_builder.py` lines 1, 20-23, 42-49 — docstring-only edits:**
```python
"""FCP7 XML builder for virtual subclips — Premiere Pro compatible."""     # line 1

def _pathurl(path: Path) -> str:
    """Build a Premiere-compatible file://localhost/ pathurl (forward slashes)."""   # line 21

def build_xml(result: DetectionResult, config: Optional[DetectConfig] = None) -> str:
    """Return FCP7 xmeml v5 XML string compatible with Premiere Pro.

    Structure mirrors what Premiere Pro exports for scene-cut detection:
```
**Do not change `_pathurl`'s format** (`"file://localhost/" + absolute.as_posix()`,
line 22-23) — `docs/02-ARCHITECTURE.md` line 47 and `tests/test_xml_builder.py` depend
on it. Docstring only. The CI-red `test_xml_builder` failure is pre-existing and
unrelated (per STATE.md) — do not "fix" it here.

**`src/scenecutbatch/media/scanner.py` line 1:**
```python
"""Media scanning (reuse EsqueletoEdit patterns)."""
```
Direct D-33 hit. Body (lines 14-28) unchanged.

**`pyproject.toml` line 8:**
```toml
description = "Batch scene-cut detection for Adobe Premiere Pro (FCP7 XML virtual subclips)."
```
D-32 target. Keep line length/style; `version = "0.1.0"` (line 7) stays.

**`packaging/debian/DEBIAN/control` lines 7-11:**
```
Maintainer: Scene Cut Batch <maintainer@scenecutbatch.com>
Description: Batch scene-cut detection for Adobe Premiere Pro
 SceneCutBatch detects hard scene cuts across folders of video clips using
 PySceneDetect and emits Premiere-importable FCP7 XML files with virtual
 subclips referencing the original media (no duplication).
```
D-32 + D-36 both apply here (maintainer + description). Note Debian extended-
description continuation lines start with a single space.

**`packaging/rpm/scenecutbatch.spec` lines 4, 15-17, 49-50:**
```
Summary: Batch scene-cut detection for Adobe Premiere Pro          # line 4

 PySceneDetect and emits Premiere-importable FCP7 XML files with virtual
 subclips referencing the original media (no duplication).          # lines 16-17

 * Thu Oct 22 2026 Scene Cut Batch <maintainer@scenecutbatch.com> - 0.1.0-1   # line 49
```
RPM `%description` continuation lines start with a single space. D-36 changes the
`Packager`/changelog identity to JMW Studio.

**`packaging/appimage/AppDir/scenecutbatch.desktop` line 3:**
```
Comment=Batch scene-cut detection for Adobe Premiere Pro
```
Single-line value after `=`; keep `Name=Scene Cut Batch` (line 2) and
`Categories=AudioVideo;Video;` (line 8) untouched.

**`README.md` lines 3, 5, 7, 17, 23, 33, 202 — the D-33 sweep:**
```
> Batch scene-cut detection for Adobe Premiere Pro — ...            # line 3
**Status:** Active development (Phase 2 — Launch prep & multi-platform)   # line 5
**Parent ecosystem:** EsqueletoEdit (local AI editing platform). ...  # line 7
3. Emits **one FCP7 XML file per clip** that Premiere Pro can import directly.   # line 17
The point is to replace Premiere's slow, one-clip-at-a-time ...       # line 23
| FCP7 XML output | One `<clip_stem>_cuts.xml` per clip, Premiere-importable |  # line 33
Premiere Pro imports the XML and creates a bin with the master sequence and subclips.  # line 202
```
Line 5 (internal phase status) and line 7 ("Parent ecosystem") must be **removed or
rewritten as neutral marketing**, not merely reworded. Insert the EN signature line
(D-36: "Made by JMW Studio") near the license block (lines 223-225).

**`README_USO.md` lines 3, 9, 17, 90, 105, 119 and `README_PORTABLE.md` lines 3, 9, 79:**
```
FCP7 XML (xmeml) que Adobe Premiere Pro importa directamente.   # README_USO.md:9
nativa de Premiere.                                            # README_USO.md:17
Al importarlo en Premiere Pro:                                  # README_USO.md:90
└─ vacacion_cuts.xml   ← importar este en Premiere             # README_USO.md:105
| Premiere no importa el XML | ...                              # README_USO.md:119
```
Both keep the logo asset reference `![Scene Cut Batch logo](assets/logo.png)` (line 3
in both) untouched. Insert ES signature ("Hecho por JMW Studio") per D-36.

**`docs/01..10-*.md` — the full D-33 sweep (user explicitly included docs/).**
Map of hits (grep-confirmed):
- `docs/01-REQUIREMENTS.md` line 10 — "Premiere-importable FCP7 XML"
- `docs/02-ARCHITECTURE.md` lines 25, 47, 48, 56, 62, 73, 78 — reuse-EsqueletoEdit notes
- `docs/03-TECH-STACK.md` lines 5, 8, 10, 11, 13, 14 — "Consistent with EsqueletoEdit" column
- `docs/04-DATA-MODELS.md` line 75 — progress-schema consistency note
- `docs/05-CLI-SPEC.md` line 9 — Typer callback pattern reference
- `docs/06-OUTPUT-FORMAT.md` lines 5, 65, 71, 72
- `docs/07-CONFIDENCE.md` lines 24, 33
- `docs/09-INTEGRATION-TO-ESQUELETOEDIT.md` — **entire document** is internal (final-home narrative). Either rewrite as a neutral "API reuse / extensibility" doc or delete; D-33 says remove from repo text, `.planning/` retains the plan.
- `docs/10-DECISIONS.md` lines 5, 6, 8, 10, 13 — table rows citing EsqueletoEdit/Premiere-native.
  **Pattern to preserve:** the Markdown table form (3 columns `# | Decision | Rationale`) and the
  trailing `## Open questions` bullet list — the edit only changes cell text.

**`HANDOFF.md` lines 5, 10, 24, 34, 39, 44** — flagged by grep as containing
Premiere/EsqueletoEdit references. Not in CONTEXT.md's canonical file list, but it is
committed repository text (D-33: "ALL texts"). Planner should include it in the copy
sweep plan and confirm with the user if it is meant to survive publicly.

**`run.bat` (lines 1-12), `run.sh` (lines 1-12), `SceneCutBatch.command` (lines 1-48),
`run_mac.sh`, `install.bat`, `install.sh`, `install_linux.sh`, `scenecutbatch.spec`,
`packaging/appimage/build_appimage.sh`, `packaging/debian/DEBIAN/postinst`,
`packaging/appimage/AppDir/AppRun`** — grep-confirmed **no** Premiere/EsqueletoEdit
hits. Treat as **audit-only**: verify, expect zero edits. The launchers are Spanish-
language user messages (`"ERROR: No se encontro scenecutbatch.exe"`,
`"Gracias por usar SceneCutBatch"`) — D-33 covers internal references, not language,
so leave the language as-is (launcher i18n is out of scope).

---

### `src/scenecutbatch/core/batch.py` — verify only, no planned change

**Analog:** itself, lines 14-67 (progress-event contract).

```python
def detect_folder(input_dir, config: Optional[DetectConfig] = None,
                  progress: Optional[Callable[[dict], None]] = None,
                  write_xml: bool = True) -> BatchResult:
    """Process a folder of clips.
    ...
    """
```
**Why it's listed:** the GUI's translated log lines are driven by these event names
(`start`, `clip_start`, `clip_done`, `clip_error`, `done`) and their keys
(`index`, `total`, `clip`, `scenes`, `eta_sec`, `succeeded`, `failed`). The i18n
catalog's interpolation keys must match them 1:1. The planner should add a check that
`tests/test_batch.py` and `tests/test_cli.py::test_cli_json_progress_emits_json`
still pass (they pin the event contract) — **no behavior change is permitted** per
CONTEXT.md ("No detection/output behavior changes").

---

## Shared Patterns

### Module header convention (applies to every new/edited `.py`)
**Source:** `src/scenecutbatch/media/scanner.py` lines 1-11, `src/scenecutbatch/core/models.py` lines 1-6
**Apply to:** `src/scenecutbatch/i18n.py`, and every `.py` file touched
```python
"""One-line module docstring (Spanish, as in the rest of the package)."""

from __future__ import annotations

# stdlib imports, then relative package imports (from ..core.models / from .i18n)
```
Note: the package is Spanish-docstringed today (`media/scanner.py`, `gui.py`,
`cli.py` line 1 is English, `core/models.py` is English, `xml_builder.py` is English).
Convention is mixed — new `i18n.py` docstring may be Spanish to match `gui.py`
(its only consumer), but do **not** mass-rewrite existing docstring languages.

### Thread-marshalling (applies to all new GUI log/status code)
**Source:** `src/scenecutbatch/gui.py` lines 241-303
**Apply to:** every new translated log line and status update in `_run_worker`
```python
self.after(0, lambda: self._log(t("log.clip_done", index=..., total=..., clip=...)))
```

### Widget reference retention (applies to the language-switch rebuild)
**Source:** `src/scenecutbatch/gui.py` lines 64-87
```python
        self._icon_image = icon   # mantener referencia para evitar GC
        logo_label.image = logo_img  # mantener referencia para evitar GC
```

### Relative imports inside the package (applies to new module)
**Source:** `src/scenecutbatch/core/batch.py` lines 9-12, `src/scenecutbatch/export/xml_builder.py` line 12
```python
from ..core.models import BatchResult, DetectConfig, DetectionResult
from ..detection.detector import detect_clip
from ..export.xml_builder import write_xml as _write_xml
from ..media.scanner import scan_folder
```

### String interpolation for user-facing text (applies to i18n catalog)
**Source:** `src/scenecutbatch/core/batch.py` lines 38-62 (f-string interpolation into log messages)
and `src/scenecutbatch/cli.py` lines 66-82
```python
f"[{event.get('index')}/{event.get('total')}] {event.get('clip')} done "
f"({event.get('scenes')} scenes, eta {event.get('eta_sec'):.0f}s)"
```
Every translated string that embeds data must keep the same placeholders; the catalog
stores the template and `t(**kwargs)` performs the `.format()`.

### Test conventions (applies to `tests/test_i18n.py` and to the updated version test)
**Source:** `tests/test_smoke.py` (whole file), `tests/conftest.py` lines 23-32,
`tests/test_cli.py` lines 37-57
- Absolute imports `from scenecutbatch.*` (pytest `pythonpath = ["src"]`)
- Fixtures via `conftest.py` with `monkeypatch` for global state
- Assert with `pytest.raises(typer.exceptions.Exit)` for exit-code checks
- No test classes, no `__init__.py`

### Error contract — DO NOT change (applies to all plans)
**Source:** `.planning/REQUIREMENTS.md` / `docs/05-CLI-SPEC.md` — exit codes 0/1/2/3/4;
`src/scenecutbatch/cli.py` lines 99-138 (validation → `typer.Exit(code=2)`, processing
failure → `typer.Exit(code=3)`). This phase is copy/layout only: **no logic, no
detection, no output-format changes.**

---

## No Analog Found

| File | Role | Data Flow | Reason |
|------|------|-----------|--------|
| `src/scenecutbatch/i18n.py` | module (utility) | transform | No i18n/locale/translation code exists in the repo — grep for `locale`, `gettext`, `i18n` across `src/` returned zero matches. The API shape comes from user decision D-35 (`t("key")`, `locale.getdefaultlocale()`, EN/ES, non-persisted); only *structural* conventions are borrowed from `media/scanner.py` and `core/models.py`. |
| In-app language switch widget | component | event-driven | No combobox/readonly selector or view-model pattern exists (`gui.py` uses only `ttk.Frame`, `ttk.Label`, `ttk.Entry`, `ttk.Button`, `ttk.Checkbutton`, `ttk.LabelFrame`, `ttk.Progressbar`, `ScrolledText`). Planner invents the first one; match the `command=self._callback` idiom used by `_browse_input` (line 195). |
| `tests/test_i18n.py` | test | request-response | No existing test covers a pure string catalog; nearest shape is `tests/test_smoke.py` (function-based, no fixtures). Note `gui.py` has **no test coverage at all today** (no `tests/test_gui.py`) and GUI test automation is explicitly **deferred** per CONTEXT.md — do not add GUI automation to close a coverage gap in this phase. |

---

## Metadata

**Analog search scope:** `src/` (all subpackages), `tests/`, `packaging/`, `docs/`,
repo root (launchers, specs, pyproject, READMEs)
**Files scanned:** 34 (13 Python sources, 7 tests, 8 packaging/metadata, 10 docs/READMEs + 6 launchers)
**Pattern extraction date:** 2026-10-23
**Git-tracked gate:** all named analog paths verified tracked via `git ls-files` (no `.gsd/capabilities` mirrors exist in this repo)

### Regression flags for the planner (carry into plan `<verification>`)
1. `tests/test_cli.py::test_cli_version_prints_0_1_0` does an **exact** string match —
   the D-36 CLI footer will break it; update the assertion.
2. `tests/test_smoke.py::test_version` pins `__version__ == "0.1.0"` — do not bump version in this phase.
3. CI is already red on `test_xml_builder.py::test_build_xml_contains_master_and_subclips`
   (pre-existing, documented in STATE.md) — do not treat as a new failure, do not fix here.
4. `tests/test_cli.py::test_cli_json_progress_emits_json` and `tests/test_batch.py` pin the
   progress-event dict contract driving every translated GUI log line.
5. `_asset_path()` + `scenecutbatch.spec` `datas` bundle contract must survive the GUI
   layout rework unchanged (verified working on Windows at v0.1.0).
