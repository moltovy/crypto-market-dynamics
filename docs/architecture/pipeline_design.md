# Pipeline Design

The public reproduction path is intentionally short:

```powershell
uv sync --all-extras
uv run pytest
uv run python scripts/run_all.py
```

`scripts/run_all.py` delegates to the maintained
`src/cqresearch/pipelines/final_research.py` orchestration path, which rebuilds
the canonical feature stores, tables, reports, figures, README, licenses, and
`outputs/manifest.json`.

Legacy portfolio/release packet builders are not active maintained source; use
Git history or `archive/` for historical context.
