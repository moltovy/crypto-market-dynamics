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

- `figures/F01_mvrv_sensitivity_by_regime_v2.png`
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

## Market-Structure Extension

The additive market-structure layer integrates tracked DefiLlama/AlternativeMe/TradingView context with optional DefiLlama, Binance, and CoinMarketCap cache. It does not require API keys for the public build.

Reports:

- `report/market_evolution_thesis.md`
- `report/market_structure_modeling_thesis.md`
- `report/market_structure_methodology.md`
- `report/market_structure_data_inventory.md`
- `report/market_structure_limitations.md`
- `report/market_structure_fetch_diagnostics.md`

Figures:

- `figures/F30_market_structure_dashboard.png`
- `figures/F31_stablecoin_tvl_regimes.png`
- `figures/F32_sentiment_comparison.png`
- `figures/F33_cex_dex_activity.png`
- `figures/F34_binance_liquidity_universe.png`
- `figures/F35_btc_dominance_cycle_overlay.png`
- `figures/F36_rwa_dat_growth.png`
- `figures/F37_market_cap_top100_gap.png`
- `figures/F38_market_structure_composition.png`
- `figures/F39_top100_concentration.png`
- `figures/F40_rank_turnover.png`
- `figures/F41_cycle_phase_market_structure.png`
- `figures/F42_market_evolution_dashboard.png`
- `figures/F43_market_structure_monthly_features.png`
- `figures/F44_market_structure_return_regimes.png`
- `figures/F45_market_structure_composition_shift.png`
- `figures/F46_market_structure_turnover_by_phase.png`
- `figures/F47_market_structure_modeling_dashboard.png`

Tables:

- `tables/T28_market_structure_source_capabilities.csv`
- `tables/T29_asset_classification.csv`
- `tables/T30_binance_liquidity_top100.csv`
- `tables/T31_sentiment_comparison.csv`
- `tables/T32_stablecoin_tvl_regimes.csv`
- `tables/T33_cex_dex_activity.csv`
- `tables/T34_btc_cycle_overlay.csv`
- `tables/T35_rwa_dat_growth.csv`
- `tables/T36_market_cap_top100_gap.csv`
- `tables/T37_market_structure_feature_panel.csv`
- `tables/T38_fear_greed_blended_daily.csv`
- `tables/T39_fear_greed_source_overlap_summary.csv`
- `tables/T40_crypto_universe_monthly.csv`
- `tables/T41_clean_risk_top100_monthly.csv`
- `tables/T42_market_structure_composition.csv`
- `tables/T43_rank_turnover.csv`
- `tables/T44_cycle_phase_market_structure.csv`
- `tables/T45_market_evolution_summary.md`
- `tables/T46_market_structure_monthly_features.csv`
- `tables/T47_market_structure_daily_context.csv`
- `tables/T48_market_structure_return_regimes.csv`
- `tables/T49_market_structure_composition_shift.csv`
- `tables/T50_market_structure_turnover_by_phase.csv`
- `tables/T51_market_structure_modeling_summary.md`

Guardrails:

- Binance top100 is exchange-liquidity based, not historical market-cap rank.
- CMC live fetch requires `CMC_API_KEY`; cached CMC history is included when present.
- Monthly universe snapshots support composition and turnover analysis, not daily performance or event-return claims.
- Raw source responses stay in gitignored `data_cache/`.
