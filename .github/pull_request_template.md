## Summary

- 

## Portfolio Packets

- [ ] `reports/portfolio_v2/` baseline packet remains intact
- [ ] `reports/portfolio_v2_1/` polished release packet is current
- [ ] `reports/portfolio_v2_2/` advanced diagnostics packet is current, if applicable
- [ ] `reports/portfolio_showcase/` public showcase docs are current
- [ ] Optional data scaffolding remains outside core reproduction

## Verification

- [ ] `uv run pytest`
- [ ] `uv run mypy src/cqresearch`
- [ ] `uv run python scripts/run_portfolio_v2_1_pipeline.py`
- [ ] `uv run python scripts/run_portfolio_v2_2_pipeline.py`
- [ ] Focused Ruff pass from `Makefile`
- [ ] `git status --short -- Data` returns no output

## Guardrails

- [ ] No raw `Data/` files modified
- [ ] No paid/live data dependency added to core releases
- [ ] No causal ETF-flow claims
- [ ] No current structural-break output labeled full Bai-Perron
- [ ] No drop-one attribution mislabeled as Shapley/Owen

## Reviewer Notes

- 
