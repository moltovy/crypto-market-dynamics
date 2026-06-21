# Maintained Architecture

The maintained public build path is:

- `src/cqresearch/pipelines/research.py` for orchestration.
- `scripts/run_research.py --module all` for the complete public module build.
- `scripts/build_research_figures.py --module all` for public module figures.
- `scripts/check_research_surface.py --module all` for module, claims, figure, and manifest guardrails.
- `research/` for the canonical module surface.

Legacy portfolio and versioned release workflows are not part of the maintained public surface.
