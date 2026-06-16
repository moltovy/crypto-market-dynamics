# Canonical Outputs

`outputs/` is the canonical public artifact packet for Crypto Market Factor
Lab. Historical release packets and internal planning material live under
`archive/`.

## Reports

- `report/executive_summary.md`
- `report/technical_report.md`
- `report/methodology.md`
- `report/data_atlas.md`
- `report/limitations.md`
- `report/reorganization_summary.md`

## Figures

- `figures/F00_project_summary_card.png`
- `figures/F01_data_coverage.png`
- `figures/F02_btc_block_attribution.png`
- `figures/F03_btc_etf_lead_lag.png`
- `figures/F04_btc_rolling_correlations.png`
- `figures/F05_stablecoin_supply_tvl.png`
- `figures/F06_btc_native_dashboard.png`
- `figures/F07_connectedness.png`
- `figures/F08_robustness_grid.png`
- `figures/F09_key_results_cards.png`
- `figures/T00_key_results_table.png`
- `figures/visual_gallery.png`

## Tables

- `tables/README.md`
- `tables/key_results.md`
- `tables/key_results.html`
- `tables/T01_source_inventory.csv`
- `tables/T02_panel_coverage.csv`
- `tables/T03_block_attribution.csv`
- `tables/T03_rolling_block_partial_r2_btc_180d.csv`
- `tables/T04_etf_lead_lag.csv`
- `tables/T05_correlation_regime.csv`
- `tables/T05_rolling_correlations.csv`
- `tables/T06_stablecoin_liquidity.csv`
- `tables/T07_native_factor_ablation.csv`
- `tables/T07_native_factor_registry.csv`
- `tables/T07_btc_native_correlations.csv`
- `tables/T08_structural_breaks.csv`
- `tables/T09_connectedness.csv`
- `tables/T09_rolling_connectedness.csv`
- `tables/T10_robustness.csv`

## Dashboard

- `dashboard/index.html`
- `dashboard/README.md`

## Visual QA

- `report/visual_audit.md`
- `report/visual_quality_check.md`

## Reproduce

```powershell
uv sync --all-extras
uv run pytest
uv run mypy src/cqresearch
uv run python scripts/run_all.py
```
