# 05 — CLI Spec

## Command

```
scenecutbatch detect INPUT_DIR [OPTIONS]
```

(Single `detect` command; `--version` is eager.)

## Options

| Flag | Type | Default | Description |
|------|------|---------|-------------|
| `INPUT_DIR` | path | (required) | Folder of clips |
| `--out-dir` | path | INPUT_DIR/cuts | Output directory |
| `--threshold` | float | 27.0 | ContentDetector threshold |
| `--min-scene-len` | int | 15 | Min scene length in frames |
| `--recursive` | bool | false | Recurse into subfolders |
| `--extensions` | str | (default set) | Comma-separated |
| `--dry-run` | bool | false | List cuts, write nothing |
| `--json-progress` | bool | false | Stream JSON events to stdout |
| `--config` | path | none | YAML/TOML config file |
| `--confidence` | bool | false | Enable G/Y/R markers |
| `--version` | | | Print version |

## Exit codes

- 0 success (all clips processed, possibly with per-clip errors reported)
- 1 usage error
- 2 validation error (bad input dir, missing ffprobe)
- 3 processing error (fatal)
- 4 export error (fatal)

## Examples

```
scenecutbatch detect "D:\Footage\Day1" --out-dir "D:\Footage\Day1\cuts" --threshold 30
scenecutbatch detect "D:\Footage" --recursive --json-progress > progress.jsonl
scenecutbatch detect "D:\Footage" --dry-run
```

## Python API (Phase 6)

```python
from scenecutbatch import detect_folder
result = detect_folder(input_dir, out_dir, config)
```
