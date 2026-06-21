## Summary

- 

## Public Surface

- [ ] README remains a clean project overview.
- [ ] Canonical artifacts live under `research/`.
- [ ] Historical or internal process material is absent from the public surface.
- [ ] Public docs avoid private-process framing.

## Verification

- [ ] `uv run ruff check src/cqresearch scripts tests`
- [ ] `uv run ruff format --check src/cqresearch scripts tests`
- [ ] `uv run mypy src/cqresearch`
- [ ] `uv run pytest -q`
- [ ] `uv run python scripts/check_research_surface.py --module all`
- [ ] `uv run python scripts/run_research.py --module all` when local provider inputs are present
- [ ] `uv run python scripts/build_research_figures.py --module all` when figures are regenerated

## Guardrails

- [ ] Raw provider exports remain local-only under ignored `data_local/`.
- [ ] No paid/live data dependency added to the canonical output path.
- [ ] No causal ETF-flow claims.
- [ ] Drop-block delta R-squared is not labeled conventional partial R-squared.
- [ ] Public README surface has four to six canonical figures.

## Reviewer Notes

- 
