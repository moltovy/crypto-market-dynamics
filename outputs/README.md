# Canonical Outputs

`outputs/` is the canonical public artifact packet for Crypto Market Factor Lab. Historical release packets and internal planning material live under `archive/`.

## Reports

- `report/executive_summary.md`
- `report/technical_report.md`
- `report/methodology.md`
- `report/data_atlas.md`
- `report/limitations.md`
- `report/reorganization_summary.md`

## Figures

- `figures/F01_mvrv_sensitivity_by_regime.png`
- `figures/F02_same_support_ablation.png`
- `figures/F03_btc_ex_mvrv_strength.png`
- `figures/F04_etf_flow_lead_lag.png`
- `figures/F05_core_correlation_matrix.png`
- `figures/F06_rolling_correlations.png`
- `figures/F07_feature_strength_heatmap.png`
- `figures/F08_connectedness_robustness.png`
- `figures/gallery/G01_native_state_detail.png`
- `figures/gallery/G02_liquidity_context.png`

## Tables

- `tables/README.md`
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
- `tables/T11_results_at_a_glance.md`
- `tables/T12_regime_definitions.csv`
- `tables/T13_factor_dictionary.md`
- `tables/T13_factor_dictionary.csv`
- `tables/T14_feature_strength_btc_full.csv`
- `tables/T15_feature_strength_btc_ex_mvrv.csv`
- `tables/T16_feature_strength_eth.csv`
- `tables/T17_feature_strength_by_regime.csv`
- `tables/T18_block_strength_by_regime.csv`
- `tables/T19_same_support_ablation_btc.csv`
- `tables/T20_same_support_ablation_eth.csv`
- `tables/T21_top_correlations_btc.csv`
- `tables/T22_top_correlations_eth.csv`
- `tables/T23_core_correlation_matrix.csv`
- `tables/T24_pre_post_correlation_delta.csv`
- `tables/T25_mvrv_sensitivity_by_regime.csv`
- `tables/T26_etf_era_feature_strength.csv`
- `tables/T27_rolling_feature_rank_stability.csv`

## Dashboard

- `dashboard/index.html`

## Reproduce

```powershell
uv sync --all-extras
uv run pytest
uv run mypy src/cqresearch
uv run python scripts/run_all.py
```
