# Research Surface

This directory is the canonical public research surface for Crypto Market Dynamics. It organizes the 2020-2026 descriptive and associational evidence into self-contained modules with methods, findings, interpretation, limitations, tables, figures, and manifests.

## Module Map

| Module | Title | Question |
|---|---|---|
| [00_data_foundation](00_data_foundation/README.md) | Data Foundation | What data, units, timing, coverage, identity, and release-risk constraints govern every later result? |
| [01_returns_risk_regimes](01_returns_risk_regimes/README.md) | Returns, Risk, and Regimes | How do BTC and ETH return distributions, volatility, drawdown, and tail behavior vary across transparent regimes? |
| [02_macro_cross_asset_exposure](02_macro_cross_asset_exposure/README.md) | Macro and Cross-Asset Exposure | How does crypto co-movement with equities, volatility, rates, dollar, and gold vary by asset, calendar, and period? |
| [03_derivatives_leverage_liquidations](03_derivatives_leverage_liquidations/README.md) | Derivatives, Leverage, and Liquidations | Where do leverage, funding, open-interest scaling, and liquidation stress appear in volatility and tail outcomes? |
| [04_etf_institutional_plumbing](04_etf_institutional_plumbing/README.md) | ETF and Institutional Plumbing | How do ETF flow intensity and absorption measures line up with contemporaneous and lagged crypto outcomes? |
| [05_stablecoin_defi_liquidity](05_stablecoin_defi_liquidity/README.md) | Stablecoin and DeFi Liquidity State | What do stablecoin supply and DeFi TVL proxies say about liquidity-state associations after unit and valuation audits? |
| [06_onchain_valuation_holder_state](06_onchain_valuation_holder_state/README.md) | On-Chain Valuation and Holder State | Which on-chain valuation and holder-state measures are diagnostics versus admissible lagged state variables? |
| [07_chain_fundamentals](07_chain_fundamentals/README.md) | Chain Fundamentals | Which chain-level activity measures have enough coverage and definition clarity for descriptive panel analysis? |
| [08_relative_major_asset_risk](08_relative_major_asset_risk/README.md) | Relative Major-Asset Risk | How do selected major crypto assets compare on matched-window risk, downside, drawdown, and beta measures? |
| [09_market_concentration_state](09_market_concentration_state/README.md) | Market Concentration State | How do monthly point-in-time concentration, turnover, and rank-persistence states relate to market-structure conditions? |
| [10_event_sensitivity](10_event_sensitivity/README.md) | Event Sensitivity | How do registered event windows compare with empirical placebo windows under fixed window conventions? |
| [11_cross_module_synthesis](11_cross_module_synthesis/README.md) | Cross-Module Synthesis | Which findings remain strongest after comparing outcome, coverage, timing, uncertainty, and measurement-risk evidence? |

## Root Figure Set

![Later-sample equity co-movement is higher for BTC and ETH.](02_macro_cross_asset_exposure/figures/01_tradfi_exposure_shift.png)

Source: `research/02_macro_cross_asset_exposure/tables/block_delta_r2.csv`. Boundary: Period comparison, not ETF-effect identification.

![Leverage states are stress diagnostics.](03_derivatives_leverage_liquidations/figures/03_leverage_tail_stress.png)

Source: `research/03_derivatives_leverage_liquidations/tables/leverage_tail_risk_summary.csv; research/03_derivatives_leverage_liquidations/tables/tail_risk_models.csv`. Boundary: No liquidation initiation-cause claim.

![ETF flow intensity is reported as market plumbing.](04_etf_institutional_plumbing/figures/02_etf_market_plumbing.png)

Source: `research/04_etf_institutional_plumbing/tables/etf_flow_associations.csv; research/04_etf_institutional_plumbing/tables/etf_absorption_metrics.csv`. Boundary: Timing and simultaneity limit interpretation.

![Selected-major risk is coverage-aware.](08_relative_major_asset_risk/figures/05_selected_major_asset_risk.png)

Source: `research/08_relative_major_asset_risk/tables/selected_major_risk_metrics.csv; research/08_relative_major_asset_risk/tables/selected_major_comparable_window_metrics.csv`. Boundary: Short histories limit cross-asset comparability.

![PIT data supports monthly concentration and turnover state analysis.](09_market_concentration_state/figures/market_concentration_state.png)

Source: `research/09_market_concentration_state/tables/pit_market_structure_summary.csv`. Boundary: No daily constituent-performance claim.

## Data-Usage Status Counts

- `diagnostic_only`: 69
- `excluded_definition_or_unit_ambiguity`: 101
- `excluded_insufficient_coverage`: 2
- `primary_analysis`: 25
- `robustness_or_sensitivity`: 2

Every local raw or engineered feature discovered by the data-foundation module is assigned one usage or exclusion status in [`00_data_foundation/tables/feature_usage_matrix.csv`](00_data_foundation/tables/feature_usage_matrix.csv).

## Provenance

- Root manifest: [`manifest.json`](manifest.json)
- Figure specifications: [`figure_specs.csv`](figure_specs.csv)
- Cross-module evidence ledger: [`11_cross_module_synthesis/tables/evidence_ledger.csv`](11_cross_module_synthesis/tables/evidence_ledger.csv)

## Rebuild

```bash
uv run python scripts/run_research.py --module all
uv run python scripts/build_research_figures.py --module all
uv run python scripts/check_research_surface.py --module all
```
