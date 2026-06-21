# Reproducibility

## Local Verification

```powershell
uv sync --all-extras
uv run python scripts/run_research.py --module all
uv run python scripts/build_research_figures.py --module all
uv run pytest
uv run mypy src/cqresearch
uv run ruff check src/cqresearch scripts tests
uv run python scripts/check_research_surface.py --module all
```

## Data Policy

The canonical source build reads local provider exports from `data_local/raw/`
and writes generated feature stores to `data_local/processed/`. Both folders
are ignored by Git. Public semantic outputs stay under `research/`.
