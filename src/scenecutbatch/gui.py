"""Interfaz gráfica simple para Scene Cut Batch (Tkinter)."""

from __future__ import annotations

import sys
import threading
import tkinter as tk
from pathlib import Path
from tkinter import filedialog, messagebox, scrolledtext, ttk
from typing import Optional

from .core.batch import detect_folder
from .core.models import DetectConfig
from .i18n import SUPPORTED_LANGUAGES, current_language, detect_language, set_language, t


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


class SceneCutBatchGUI(tk.Tk):
    """Ventana principal de SceneCutBatch."""

    def __init__(self) -> None:
        super().__init__()

        # Auto-detect OS language before building the UI (D-35).
        self._lang = detect_language()
        set_language(self._lang)

        self.title(t("window.title"))
        self.geometry("880x740")
        self.minsize(820, 700)

        # Variables de estado — created once in __init__ so they survive
        # the language-switch rebuild (never moved into _build_ui).
        self.input_dir = tk.StringVar(value="")
        self.output_dir = tk.StringVar(value="")
        self.threshold = tk.DoubleVar(value=27.0)
        self.min_scene_len = tk.IntVar(value=15)
        self.recursive = tk.BooleanVar(value=False)
        self.dry_run = tk.BooleanVar(value=False)
        self.json_progress = tk.BooleanVar(value=False)
        self.confidence = tk.BooleanVar(value=False)
        self.is_running = False

        self._container: Optional[ttk.Frame] = None
        self._icon_image = None
        self._logo_image = None

        self._set_window_icon()
        self._build_ui()

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

    # ------------------------------------------------------------------ #
    # Construcción de la interfaz (idempotente)
    # ------------------------------------------------------------------ #

    def _build_ui(self) -> None:
        """Build (or rebuild) the whole interface. Safe to call repeatedly."""
        # Destroy previous container on rebuild so the interface never stacks.
        if self._container is not None:
            self._container.destroy()

        self._container = ttk.Frame(self, padding="12")
        self._container.pack(fill=tk.BOTH, expand=True)

        # --- Horizontal header: logo left, title/subtitle/signature right ---
        header = ttk.Frame(self._container)
        header.pack(fill=tk.X, pady=(0, 12))

        logo_path = _asset_path("assets/logo.png")
        if logo_path.exists():
            try:
                logo_img = tk.PhotoImage(file=str(logo_path))
                # Escalar a ~96 px de ancho para la cabecera
                if logo_img.width() > 96:
                    ratio = max(1, logo_img.width() // 96)
                    logo_img = logo_img.subsample(ratio, ratio)
                logo_label = ttk.Label(header, image=logo_img)
                logo_label.image = logo_img  # mantener referencia para evitar GC
                self._logo_image = logo_img
                logo_label.pack(side=tk.LEFT, padx=(0, 12))
            except tk.TclError:
                pass  # Si no se puede cargar la imagen, se omite silenciosamente

        # Right-hand block: title, subtitle, signature, language switch
        text_block = ttk.Frame(header)
        text_block.pack(side=tk.LEFT, fill=tk.X, expand=True)

        title = ttk.Label(
            text_block,
            text=t("window.title"),
            font=("Segoe UI", 16, "bold"),
        )
        title.pack(anchor="w")

        subtitle = ttk.Label(
            text_block,
            text=t("app.subtitle"),
            font=("Segoe UI", 10),
            foreground="#555555",
        )
        subtitle.pack(anchor="w", pady=(2, 0))

        signature = ttk.Label(
            text_block,
            text=t("signature"),
            font=("Segoe UI", 8),
            foreground="#555555",
        )
        signature.pack(anchor="w", pady=(4, 0))

        # Language switch (D-35): seeded from current_language, rebuilds on change.
        lang_frame = ttk.Frame(text_block)
        lang_frame.pack(anchor="w", pady=(8, 0))

        ttk.Label(
            lang_frame,
            text=t("lang.label"),
            font=("Segoe UI", 9),
        ).pack(side=tk.LEFT, padx=(0, 6))

        _lang_values = ["English", "Español"]
        _current_value = _lang_values[0] if current_language() == "en" else _lang_values[1]
        lang_combo = ttk.Combobox(
            lang_frame,
            values=_lang_values,
            state="readonly",
            width=9,
        )
        lang_combo.set(_current_value)
        lang_combo.pack(side=tk.LEFT)
        lang_combo.bind("<<ComboboxSelected>>", lambda _e: self._on_language_change(lang_combo.get()))

        # --- Carpeta de entrada ---------------------------------------
        row = ttk.Frame(self._container)
        row.pack(fill=tk.X, pady=4)
        ttk.Label(row, text=t("form.input.label"), width=18).pack(side=tk.LEFT)
        ttk.Entry(row, textvariable=self.input_dir, width=50).pack(
            side=tk.LEFT, padx=(6, 6), fill=tk.X, expand=True
        )
        ttk.Button(row, text=t("form.browse"), command=self._browse_input).pack(
            side=tk.LEFT
        )

        # --- Carpeta de salida ----------------------------------------
        row = ttk.Frame(self._container)
        row.pack(fill=tk.X, pady=4)
        ttk.Label(row, text=t("form.output.label"), width=18).pack(side=tk.LEFT)
        ttk.Entry(row, textvariable=self.output_dir, width=50).pack(
            side=tk.LEFT, padx=(6, 6), fill=tk.X, expand=True
        )
        ttk.Button(row, text=t("form.browse"), command=self._browse_output).pack(
            side=tk.LEFT
        )

        # --- Opciones de detección ------------------------------------
        opts = ttk.LabelFrame(self._container, text=t("options.title"), padding="10")
        opts.pack(fill=tk.X, pady=8)

        row = ttk.Frame(opts)
        row.pack(fill=tk.X, pady=3)
        ttk.Label(row, text=t("options.threshold"), width=26).pack(
            side=tk.LEFT
        )
        ttk.Entry(row, textvariable=self.threshold, width=10).pack(side=tk.LEFT)

        row = ttk.Frame(opts)
        row.pack(fill=tk.X, pady=3)
        ttk.Label(row, text=t("options.min_scene_len"), width=26).pack(
            side=tk.LEFT
        )
        ttk.Entry(row, textvariable=self.min_scene_len, width=10).pack(side=tk.LEFT)

        row = ttk.Frame(opts)
        row.pack(fill=tk.X, pady=3)
        ttk.Checkbutton(
            row, text=t("options.recursive"), variable=self.recursive
        ).pack(side=tk.LEFT)
        ttk.Checkbutton(
            row, text=t("options.dry_run"),
            variable=self.dry_run,
        ).pack(side=tk.LEFT, padx=(20, 0))

        row = ttk.Frame(opts)
        row.pack(fill=tk.X, pady=3)
        ttk.Checkbutton(
            row, text=t("options.json_progress"), variable=self.json_progress
        ).pack(side=tk.LEFT)
        ttk.Checkbutton(
            row, text=t("options.confidence"),
            variable=self.confidence,
        ).pack(side=tk.LEFT, padx=(20, 0))

        # --- Botón ejecutar -------------------------------------------
        btn_frame = ttk.Frame(self._container)
        btn_frame.pack(pady=12)
        self.btn_run = ttk.Button(
            btn_frame, text=t("button.run"), command=self._on_run, width=22
        )
        self.btn_run.pack()

        # --- Barra de progreso ----------------------------------------
        self.progress = ttk.Progressbar(self._container, mode="indeterminate")
        self.progress.pack(fill=tk.X, pady=(4, 0))

        # --- Log ------------------------------------------------------
        ttk.Label(self._container, text=t("log.label"), anchor="w").pack(
            fill=tk.X, pady=(10, 2)
        )
        self.log = scrolledtext.ScrolledText(self._container, height=12, wrap=tk.WORD)
        self.log.pack(fill=tk.BOTH, expand=True)

        # Estado
        self.status = ttk.Label(self._container, text=t("status.ready"), anchor="w")
        self.status.pack(fill=tk.X, pady=(6, 0))

    # ------------------------------------------------------------------ #
    # Callbacks
    # ------------------------------------------------------------------ #

    def _on_language_change(self, value: str) -> None:
        """Switch language and rebuild the UI immediately (D-35)."""
        code = "en" if value == "English" else "es"
        set_language(code)
        self._lang = code
        self._build_ui()

    def _browse_input(self) -> None:
        d = filedialog.askdirectory(title=t("filedialog.input.title"))
        if d:
            self.input_dir.set(d)
            if not self.output_dir.get():
                self.output_dir.set(str(Path(d) / "cuts"))

    def _browse_output(self) -> None:
        d = filedialog.askdirectory(title=t("filedialog.output.title"))
        if d:
            self.output_dir.set(d)

    def _log(self, message: str) -> None:
        self.log.insert(tk.END, message + "\n")
        self.log.see(tk.END)
        self.update_idletasks()

    def _on_run(self) -> None:
        if not self.input_dir.get():
            messagebox.showerror(t("dialog.error.title"), t("dialog.error.no_folder"))
            return

        if self.is_running:
            return

        self.is_running = True
        self.btn_run.state(["disabled"])
        self.progress.start(10)
        self.status.config(text=t("status.running"))
        self.log.delete("1.0", tk.END)

        thread = threading.Thread(target=self._run_worker, daemon=True)
        thread.start()

    def _run_worker(self) -> None:
        try:
            input_dir = Path(self.input_dir.get())
            out_dir = Path(self.output_dir.get()) if self.output_dir.get() else None

            cfg = DetectConfig(
                threshold=self.threshold.get(),
                min_scene_len_frames=self.min_scene_len.get(),
                recursive=self.recursive.get(),
                confidence_enabled=self.confidence.get(),
            )

            def progress(event: dict) -> None:
                ev = event.get("event")
                if ev == "start":
                    msg = t("log.start", total=event.get("total"))
                    self.after(0, lambda m=msg: self._log(m))
                elif ev == "clip_start":
                    msg = t(
                        "log.clip_start",
                        index=event.get("index"),
                        total=event.get("total"),
                        clip=event.get("clip"),
                    )
                    self.after(0, lambda m=msg: self._log(m))
                elif ev == "clip_done":
                    msg = t(
                        "log.clip_done",
                        index=event.get("index"),
                        total=event.get("total"),
                        clip=event.get("clip"),
                        scenes=event.get("scenes"),
                        eta_sec=event.get("eta_sec"),
                    )
                    self.after(0, lambda m=msg: self._log(m))
                elif ev == "clip_error":
                    msg = t(
                        "log.clip_error",
                        index=event.get("index"),
                        total=event.get("total"),
                        clip=event.get("clip"),
                        error=event.get("error"),
                    )
                    self.after(0, lambda m=msg: self._log(m))
                elif ev == "done":
                    msg = t(
                        "log.done",
                        succeeded=event.get("succeeded"),
                        failed=event.get("failed"),
                    )
                    self.after(0, lambda m=msg: self._log(m))

            detect_folder(input_dir, cfg, progress=progress, write_xml=not self.dry_run.get())

            self.after(
                0, lambda: self.status.config(text=t("status.completed"))
            )
            self.after(
                0,
                lambda: messagebox.showinfo(
                    t("dialog.done.title"),
                    t("dialog.done.body", path=str(out_dir or input_dir / "cuts")),
                ),
            )
        except Exception as exc:  # noqa: BLE001
            self.after(0, lambda: self.status.config(text=t("status.error")))
            self.after(
                0,
                lambda: messagebox.showerror(t("dialog.error.title"), str(exc)),
            )
        finally:
            self.after(0, lambda: self.progress.stop())
            self.after(0, lambda: self.btn_run.state(["!disabled"]))
            self.is_running = False


def main() -> None:
    app = SceneCutBatchGUI()
    app.mainloop()


if __name__ == "__main__":
    main()
