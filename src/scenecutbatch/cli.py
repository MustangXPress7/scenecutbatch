"""CLI for SceneCutBatch."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Optional

import typer
import yaml

from . import __version__
from .core.batch import detect_folder
from .core.models import DetectConfig

app = typer.Typer(help="Batch scene-cut detection for Premiere Pro.")


def _version_callback(value: bool) -> None:
    if value:
        typer.echo(__version__)
        raise typer.Exit()


def _load_config(path: str, cfg: DetectConfig) -> DetectConfig:
    """Load YAML config file and update DetectConfig fields (CLI overrides later)."""
    config_path = Path(path)
    if not config_path.is_file():
        typer.echo(f"error: config file not found: {path}", err=True)
        raise typer.Exit(code=2)
    try:
        with config_path.open("r", encoding="utf-8") as fh:
            data = yaml.safe_load(fh) or {}
    except yaml.YAMLError as exc:
        typer.echo(f"error: failed to parse config file {path}: {exc}", err=True)
        raise typer.Exit(code=2)
    if not isinstance(data, dict):
        return cfg
    for key in (
        "threshold",
        "min_scene_len_frames",
        "recursive",
        "extensions",
        "confidence_enabled",
        "output_naming",
    ):
        if key not in data:
            continue
        val = data[key]
        if key == "extensions":
            if isinstance(val, str):
                val = _parse_extensions(val)
            elif isinstance(val, (list, tuple)):
                val = tuple(_parse_extensions(",".join(str(v) for v in val)))
        setattr(cfg, key, val)
    return cfg


def _parse_extensions(value: str) -> tuple:
    """Parse a comma-separated extensions string into a normalized tuple."""
    return tuple(
        part.strip().lstrip(".").lower()
        for part in value.split(",")
        if part.strip()
    )


def _plain_event(event: dict) -> str:
    """Format a progress event as a plain-text line for stdout."""
    ev = event.get("event")
    if ev == "start":
        return f"start: {event.get('total')} clips in {event.get('input_dir')}"
    if ev == "clip_start":
        return f"[{event.get('index')}/{event.get('total')}] {event.get('clip')} started"
    if ev == "clip_done":
        return (
            f"[{event.get('index')}/{event.get('total')}] {event.get('clip')} done "
            f"({event.get('scenes')} scenes, eta {event.get('eta_sec'):.0f}s)"
        )
    if ev == "clip_error":
        return f"[{event.get('index')}/{event.get('total')}] {event.get('clip')} error: {event.get('error')}"
    if ev == "done":
        return f"done: {event.get('succeeded')} succeeded, {event.get('failed')} failed"
    return json.dumps(event)


def _run_detect(
    input_dir: Path,
    out_dir: Optional[Path],
    threshold: float,
    min_scene_len: int,
    recursive: bool,
    extensions: Optional[tuple],
    dry_run: bool,
    json_progress: bool,
    confidence: bool,
    config: Optional[str],
) -> None:
    """Core detect logic (exit codes raised as typer.Exit)."""

    # --- validation (exit code 2) ---------------------------------------
    input_path = Path(input_dir)
    if not input_path.exists() or not input_path.is_dir():
        typer.echo(
            f"error: input directory not found or not a directory: {input_dir}",
            err=True,
        )
        raise typer.Exit(code=2)

    # --- config: file first, then CLI flags override --------------------
    cfg = DetectConfig()
    if config:
        cfg = _load_config(config, cfg)

    cfg.threshold = threshold
    cfg.min_scene_len_frames = min_scene_len
    cfg.recursive = recursive
    cfg.confidence_enabled = confidence
    if extensions is not None:
        cfg.extensions = extensions

    resolved_out = out_dir if out_dir else input_path / "cuts"

    # --- progress callback ---------------------------------------------
    def progress(event: dict) -> None:
        if json_progress:
            typer.echo(json.dumps(event))
        else:
            typer.echo(_plain_event(event))

    # --- run detection --------------------------------------------------
    try:
        batch = detect_folder(
            input_path, cfg, progress=progress, write_xml=not dry_run
        )
    except Exception as exc:  # noqa: BLE001
        typer.echo(f"error: processing failed: {exc}", err=True)
        raise typer.Exit(code=3)

    # --- dry-run: list cuts, write no files -----------------------------
    if dry_run:
        for result in batch.succeeded:
            for scene in result.scenes:
                typer.echo(
                    f"{scene.start_tc} {scene.end_tc} {scene.duration_sec:.3f}s"
                )

    # --- summary ---------------------------------------------------------
    typer.echo(
        f"Batch done: {len(batch.succeeded)} succeeded, {len(batch.failed)} failed"
    )


@app.command()
def detect(
    input_dir: str = typer.Argument(..., help="Folder of clips"),
    out_dir: Optional[str] = typer.Option(
        None, "--out-dir", help="Output directory (default: INPUT_DIR/cuts)"
    ),
    threshold: float = typer.Option(
        27.0, "--threshold", help="ContentDetector threshold"
    ),
    min_scene_len: int = typer.Option(
        15, "--min-scene-len", help="Min scene length in frames"
    ),
    recursive: bool = typer.Option(
        False, "--recursive", help="Recurse into subfolders"
    ),
    extensions: Optional[str] = typer.Option(
        None, "--extensions", help="Comma-separated extensions (e.g. mp4,mov)"
    ),
    dry_run: bool = typer.Option(
        False, "--dry-run", help="List cuts, write nothing"
    ),
    json_progress: bool = typer.Option(
        False, "--json-progress", help="Stream JSON events to stdout"
    ),
    confidence: bool = typer.Option(
        False, "--confidence", help="Enable G/Y/R markers (no-op in v1)"
    ),
    config: Optional[str] = typer.Option(
        None, "--config", help="YAML config file path"
    ),
    version: bool = typer.Option(
        False,
        "--version",
        callback=_version_callback,
        is_eager=True,
        help="Print version and exit",
    ),
):
    """Detect scene cuts in a folder of clips."""
    _run_detect(
        Path(input_dir),
        Path(out_dir) if out_dir else None,
        threshold,
        min_scene_len,
        recursive,
        _parse_extensions(extensions) if extensions is not None else None,
        dry_run,
        json_progress,
        confidence,
        config,
    )


def main() -> None:
    app()


if __name__ == "__main__":
    main()
