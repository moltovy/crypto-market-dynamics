## Summary

- 

## Public Surface

- [ ] README remains a clean project overview.
- [ ] Canonical artifacts live under `outputs/`.
- [ ] Historical or internal material stays under `archive/`.
- [ ] Public docs avoid career/job-application framing.

## Verification

- [ ] `uv run pytest`
- [ ] `uv run mypy src/cqresearch`
- [ ] `uv run python scripts/run_all.py`
- [ ] `uv run python scripts/build_public_figures.py`
- [ ] `uv run ruff check src/cqresearch scripts tests`
- [ ] `uv run python scripts/check_public_surface.py`

## Guardrails

- [ ] Raw provider exports remain local-only under ignored `data_local/`.
- [ ] No paid/live data dependency added to the canonical output path.
- [ ] No causal ETF-flow claims.
- [ ] Drop-block delta R-squared is not labeled conventional partial R-squared.
- [ ] Public README surface has exactly six canonical figures.

## Reviewer Notes

- 
