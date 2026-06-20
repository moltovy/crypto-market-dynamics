# Reproducibility Report

## Maintained commands

```powershell
uv sync --all-extras
uv run ruff check src/cqresearch scripts tests
uv run mypy src/cqresearch
uv run python scripts/run_all.py
uv run pytest
uv run python scripts/check_public_surface.py
```

## Data contract

The build reads tracked local source files under `Data/` and generated feature stores under `reports/panels/`. The only generated files written under `Data/` are `MASTER_DATA.csv`, `MASTER_DATA.md`, and `MASTER_DATA.txt`, which inventory the tracked source files.

## Determinism

CI builds the canonical outputs before pytest so semantic-output tests run against freshly generated artifacts. A second in-run build hashes `Data/`, `outputs/`, and `reports/panels/` before and after regeneration, excluding only `outputs/manifest.json`, to verify deterministic semantic outputs within the runner. The final CI diff gate allows generated `outputs/`, `reports/panels/`, and `Data/MASTER_DATA.*` inventory files to differ from checked-in bytes because rendered figure files and floating-point text can vary by OS/font stack; it fails if the build mutates source files or raw `Data/` files outside the generated inventory.
