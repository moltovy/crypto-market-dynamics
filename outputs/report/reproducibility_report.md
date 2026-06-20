# Reproducibility Report

## Maintained commands

```powershell
uv sync --all-extras
uv run python scripts/run_all.py
uv run python scripts/check_public_surface.py
uv run pytest
uv run mypy src/cqresearch
uv run ruff check src/cqresearch scripts tests
```

## Data contract

The build reads tracked local source files under `Data/` and generated feature stores under `reports/panels/`. The only generated files written under `Data/` are `MASTER_DATA.csv`, `MASTER_DATA.md`, and `MASTER_DATA.txt`, which inventory the tracked source files.

## Determinism

`Data/MASTER_DATA.*` omits wall-clock timestamps so CI can check that rerunning the canonical build does not change the generated inventory after it is committed. `outputs/manifest.json` includes release metadata and the canonical public artifact list.
