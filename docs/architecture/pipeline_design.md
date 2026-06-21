# Pipeline Design

The public reproduction path is intentionally short:

```powershell
uv sync --all-extras
uv run pytest
uv run python scripts/run_research.py --module all
uv run python scripts/check_research_surface.py --module all
```

`scripts/run_research.py` delegates to the maintained
`src/cqresearch/pipelines/research.py` orchestration path, which builds the
canonical `research/` module surface with tables, figures, claims, docs, and
manifests.

Legacy portfolio/release packet builders are not active maintained source. The
public workflow is the `scripts/run_research.py --module all` orchestration path.
