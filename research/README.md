# Research Surface

This directory is the canonical public research surface for Crypto Market Dynamics. It contains generated modules, tables, figures, manifests, and the root figure-selection audit.

## Module Map

| Module | Title | Tables | Figures |
|---|---|---:|---:|
| [00_data_measurement_foundation](00_data_measurement_foundation/README.md) | Data and Measurement Foundation | 11 | 2 |
| [01_cross_asset_dependence_regimes](01_cross_asset_dependence_regimes/README.md) | Cross-Asset Dependence and Regimes | 12 | 3 |
| [02_macro_tradfi_integration](02_macro_tradfi_integration/README.md) | Macro and TradFi Integration | 13 | 3 |
| [03_derivatives_leverage_liquidations](03_derivatives_leverage_liquidations/README.md) | Derivatives, Leverage, and Liquidations | 6 | 3 |
| [04_etf_institutional_flows](04_etf_institutional_flows/README.md) | ETF and Institutional Flows | 10 | 3 |
| [05_stablecoin_defi_liquidity](05_stablecoin_defi_liquidity/README.md) | Stablecoin and DeFi Liquidity State | 7 | 3 |
| [06_onchain_valuation_holder_behavior](06_onchain_valuation_holder_behavior/README.md) | On-Chain Valuation and Holder Behavior | 5 | 3 |
| [07_chain_fundamentals_sector_dynamics](07_chain_fundamentals_sector_dynamics/README.md) | Chain Fundamentals and Sector Dynamics | 10 | 3 |
| [08_relative_asset_risk_factor_structure](08_relative_asset_risk_factor_structure/README.md) | Relative Asset Risk and Factor Structure | 9 | 3 |
| [09_event_stress_cross_module_synthesis](09_event_stress_cross_module_synthesis/README.md) | Event Stress and Cross-Module Synthesis | 11 | 3 |

## Root Figure Set

![Common crypto dependence is broad on the matched selected-major panel.](01_cross_asset_dependence_regimes/figures/01_cross_asset_clustered_correlation.png)

Source: `research/01_cross_asset_dependence_regimes/tables/pearson_correlation_matrix.csv; research/01_cross_asset_dependence_regimes/tables/pca_variance_share.csv`. Boundary: Current-cohort selected-major daily data is survivorship-biased.

![Later-sample equity co-movement is higher for BTC and ETH.](02_macro_tradfi_integration/figures/02_tradfi_exposure_shift.png)

Source: `research/02_macro_tradfi_integration/tables/block_delta_r2.csv; research/02_macro_tradfi_integration/tables/rolling_tradfi_exposures.csv`. Boundary: Period comparison, not ETF-effect identification.

![Leverage states are stress diagnostics.](03_derivatives_leverage_liquidations/figures/03_leverage_tail_stress.png)

Source: `research/03_derivatives_leverage_liquidations/tables/leverage_tail_risk_summary.csv; research/03_derivatives_leverage_liquidations/tables/tail_risk_models.csv`. Boundary: No liquidation initiation-cause claim.

![ETF flow intensity is reported as a lag-response market-plumbing diagnostic.](04_etf_institutional_flows/figures/04_etf_lag_response.png)

Source: `research/04_etf_institutional_flows/tables/etf_lag_response.csv; research/04_etf_institutional_flows/tables/etf_pre_inception_plot_audit.csv`. Boundary: Timing and simultaneity limit interpretation.

![Selected-major matched-window risk separates common and idiosyncratic components.](08_relative_asset_risk_factor_structure/figures/08_common_idiosyncratic_risk_decomposition.png)

Source: `research/08_relative_asset_risk_factor_structure/tables/relative_factor_decomposition.csv; research/08_relative_asset_risk_factor_structure/tables/downside_expected_shortfall.csv`. Boundary: Current-cohort and short-history caveats limit historical interpretation.

## Data-Usage Status Counts

- `diagnostic_only`: 65
- `excluded_ambiguous_definition_or_unit`: 105
- `excluded_insufficient_coverage`: 2
- `primary_analysis`: 25
- `robustness_or_sensitivity`: 2

## Provenance

- Root manifest: [`manifest.json`](manifest.json)
- Figure specifications: [`figure_specs.csv`](figure_specs.csv)
- Root figure selection: [`root_figure_selection.csv`](root_figure_selection.csv)
- Cross-module evidence ledger: [`09_event_stress_cross_module_synthesis/tables/evidence_ledger.csv`](09_event_stress_cross_module_synthesis/tables/evidence_ledger.csv)

## Rebuild

```bash
uv run python scripts/run_research.py --module all
uv run python scripts/build_research_figures.py --module all
uv run python scripts/check_research_surface.py --module all
```
