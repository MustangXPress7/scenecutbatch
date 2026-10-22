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

        self._build_ui()

    # ------------------------------------------------------------------ #
    # Construcción de la interfaz
    # ------------------------------------------------------------------ #

    def _build_ui(self) -> None:
        container = ttk.Frame(self, padding="12")
        container.pack(fill=tk.BOTH, expand=True)

        # --- Logo ---
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

        # Título
        title = ttk.Label(
            container,
            text="Scene Cut Batch",
            font=("Segoe UI", 16, "bold"),
        )
        title.pack(pady=(0, 8))

        subtitle = ttk.Label(
            container,
            text="Detecta cortes de escena y genera XML para Premiere Pro",
            font=("Segoe UI", 10),
            foreground="#555555",
        )
        subtitle.pack(pady=(0, 16))

        # --- Carpeta de entrada ---------------------------------------
        row = ttk.Frame(container)
        row.pack(fill=tk.X, pady=4)
        ttk.Label(row, text="Carpeta de videos:", width=18).pack(side=tk.LEFT)
        ttk.Entry(row, textvariable=self.input_dir, width=50).pack(
            side=tk.LEFT, padx=(6, 6), fill=tk.X, expand=True
        )
        ttk.Button(row, text="Examinar…", command=self._browse_input).pack(
            side=tk.LEFT
        )

        # --- Carpeta de salida ----------------------------------------
        row = ttk.Frame(container)
        row.pack(fill=tk.X, pady=4)
        ttk.Label(row, text="Carpeta de salida:", width=18).pack(side=tk.LEFT)
        ttk.Entry(row, textvariable=self.output_dir, width=50).pack(
            side=tk.LEFT, padx=(6, 6), fill=tk.X, expand=True
        )
        ttk.Button(row, text="Examinar…", command=self._browse_output).pack(
            side=tk.LEFT
        )

        # --- Opciones de detección ------------------------------------
        opts = ttk.LabelFrame(container, text="Opciones de detección", padding="10")
        opts.pack(fill=tk.X, pady=8)

        row = ttk.Frame(opts)
        row.pack(fill=tk.X, pady=3)
        ttk.Label(row, text="Umbral (menor = más cortes):", width=26).pack(
            side=tk.LEFT
        )
        ttk.Entry(row, textvariable=self.threshold, width=10).pack(side=tk.LEFT)

        row = ttk.Frame(opts)
        row.pack(fill=tk.X, pady=3)
        ttk.Label(row, text="Mín. largo de escena (frames):", width=26).pack(
            side=tk.LEFT
        )
        ttk.Entry(row, textvariable=self.min_scene_len, width=10).pack(side=tk.LEFT)

        row = ttk.Frame(opts)
        row.pack(fill=tk.X, pady=3)
        ttk.Checkbutton(
            row, text="Buscar en subcarpetas (--recursive)", variable=self.recursive
        ).pack(side=tk.LEFT)
        ttk.Checkbutton(
            row, text="Solo listar cortes, no escribir (--dry-run)",
            variable=self.dry_run,
        ).pack(side=tk.LEFT, padx=(20, 0))

        row = ttk.Frame(opts)
        row.pack(fill=tk.X, pady=3)
        ttk.Checkbutton(
            row, text="Progreso en JSON (--json-progress)", variable=self.json_progress
        ).pack(side=tk.LEFT)
        ttk.Checkbutton(
            row, text="Marcadores G/Y/R (--confidence, v1.1)",
            variable=self.confidence,
        ).pack(side=tk.LEFT, padx=(20, 0))

        # --- Botón ejecutar -------------------------------------------
        btn_frame = ttk.Frame(container)
        btn_frame.pack(pady=12)
        self.btn_run = ttk.Button(
            btn_frame, text="Ejecutar detección", command=self._on_run, width=22
        )
        self.btn_run.pack()

        # --- Barra de progreso ----------------------------------------
        self.progress = ttk.Progressbar(container, mode="indeterminate")
        self.progress.pack(fill=tk.X, pady=(4, 0))

        # --- Log ------------------------------------------------------
        ttk.Label(container, text="Salida:", anchor="w").pack(
            fill=tk.X, pady=(10, 2)
        )
        self.log = scrolledtext.ScrolledText(container, height=12, wrap=tk.WORD)
        self.log.pack(fill=tk.BOTH, expand=True)

        # Estado
        self.status = ttk.Label(container, text="Listo", anchor="w")
        self.status.pack(fill=tk.X, pady=(6, 0))

    # ------------------------------------------------------------------ #
    # Callbacks
    # ------------------------------------------------------------------ #

    def _browse_input(self) -> None:
        d = filedialog.askdirectory(title="Seleccionar carpeta de videos")
        if d:
            self.input_dir.set(d)
            if not self.output_dir.get():
                self.output_dir.set(str(Path(d) / "cuts"))

    def _browse_output(self) -> None:
        d = filedialog.askdirectory(title="Seleccionar carpeta de salida")
        if d:
            self.output_dir.set(d)

    def _log(self, message: str) -> None:
        self.log.insert(tk.END, message + "\n")
        self.log.see(tk.END)
        self.update_idletasks()

    def _on_run(self) -> None:
        if not self.input_dir.get():
            messagebox.showerror("Error", "Selecciona una carpeta de videos primero.")
            return

        if self.is_running:
            return

        self.is_running = True
        self.btn_run.state(["disabled"])
        self.progress.start(10)
        self.status.config(text="Ejecutando…")
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
                elif ev == "clip_done":
                    self.after(
                        0,
                        lambda: self._log(
                            f"[{event.get('index')}/{event.get('total')}] "
                            f"{event.get('clip')} listo "
                            f"({event.get('scenes')} escenas, ETA {event.get('eta_sec'):.0f}s)"
                        ),
                    )
                elif ev == "clip_error":
                    self.after(
                        0,
                        lambda: self._log(
                            f"[{event.get('index')}/{event.get('total')}] "
                            f"{event.get('clip')} ERROR: {event.get('error')}"
                        ),
                    )
                elif ev == "done":
                    self.after(
                        0,
                        lambda: self._log(
                            f"Finalizado: {event.get('succeeded')} OK, "
                            f"{event.get('failed')} fallidos"
                        ),
                    )

            detect_folder(input_dir, cfg, progress=progress, write_xml=not self.dry_run.get())

            self.after(
                0, lambda: self.status.config(text="Completado con éxito")
            )
            self.after(
                0,
                lambda: messagebox.showinfo(
                    "Listo",
                    "La detección se completó. Los archivos XML se guardaron en "
                    + str(out_dir or input_dir / "cuts"),
                ),
            )
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


def main() -> None:
    app = SceneCutBatchGUI()
    app.mainloop()


if __name__ == "__main__":
    main()
