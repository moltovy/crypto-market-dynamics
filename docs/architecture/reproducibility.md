# Reproducibility

## Local Verification

```powershell
uv sync --all-extras
uv run python scripts/run_all.py
uv run python scripts/build_public_figures.py
uv run pytest
uv run mypy src/cqresearch
uv run ruff check src/cqresearch scripts tests
uv run python scripts/check_public_surface.py
```

## Data Policy

The canonical source build reads local provider exports from `data_local/raw/`
and writes generated feature stores to `data_local/processed/`. Both folders
are ignored by Git. Public semantic outputs stay under `outputs/`.
