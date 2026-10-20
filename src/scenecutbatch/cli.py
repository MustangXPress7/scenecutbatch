"""CLI for SceneCutBatch."""

from __future__ import annotations

import typer

app = typer.Typer(help="Batch scene-cut detection for Premiere Pro.")


@app.command()
def detect(
    input_dir: str,
    out_dir: str = None,
    threshold: float = 27.0,
    min_scene_len: int = 15,
    recursive: bool = False,
    dry_run: bool = False,
    json_progress: bool = False,
    confidence: bool = False,
):
    """Detect scene cuts in a folder of clips."""
    # TODO (Phase 3): wire to batch runner + progress reporting
    typer.echo("not implemented yet")


def main():
    app()


if __name__ == "__main__":
    main()
