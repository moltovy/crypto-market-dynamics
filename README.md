# Crypto Market Factor Lab

> A reproducible Python analytics system for BTC/ETH factor regimes, ETF-flow
> market plumbing, stablecoin liquidity, cross-asset connectedness, and
> crypto-native market structure using a frozen 2020-2026 multi-source panel.

![Crypto Market Factor Lab summary](outputs/figures/F00_project_summary_card.png)

## Overview

Crypto Market Factor Lab converts curated crypto, macro, ETF-flow, DeFi,
stablecoin, sentiment, and on-chain data into a reproducible BTC/ETH research
panel and a set of reduced-form analytics modules.

The project is designed as a clean GitHub research system: one canonical output
packet, one reproducible command path, explicit model cards, and clear
interpretation guardrails. It does not claim that ETF flows caused BTC or ETH
returns. ETF-flow results are treated as association, exposure, lead-lag, and
market-plumbing diagnostics.

All public artifacts live in [`outputs/`](outputs/), including the generated
static dashboard at [`outputs/dashboard/index.html`](outputs/dashboard/index.html).

## Data

The public artifact packet uses a frozen daily panel from 2020-01-01 through
2026-04-11 with 2,293 rows and 63 columns. Frozen data keeps the project
reproducible without paid data, live API calls, or source refresh drift.

| Source | Role |
|---|---|
| CryptoQuant | BTC/ETH native, on-chain, and market-structure indicators |
| Farside ETF Data | BTC and ETH ETF flows |
| DefiLlama | TVL, stablecoin, and DeFi liquidity context |
| FRED | Macro, rates, dollar, and volatility variables |
| TradingView | Cross-asset market data |
| Artemis | ETF, DeFi, and chain context |
| AlternativeMe | Sentiment |

The clean catalog entry point is [`docs/data/catalog/`](docs/data/catalog/).
The historical source-data tree remains under `Data/` for compatibility with
existing scripts.

## Methodology

- Feature engineering for returns, differences, ETF-flow intensity, realized
  volatility, and BTC-native variables.
- HAC OLS for reduced-form BTC/ETH factor exposure.
- Full-vs-reduced block partial R2 for factor-block attribution.
- ETF-flow and stablecoin lead-lag regressions with explicit lag convention.
- Rolling cross-asset correlations and pre/post event deltas.
- Stablecoin supply and DeFi TVL liquidity proxy diagnostics.
- BTC-native factor registry, correlations, and ablations.
- Chow tests and single-break sup-F scans for structural-break diagnostics.
- VAR/FEVD connectedness and event-study diagnostics.
- Advanced diagnostics: PCA blocks, exact block Shapley R2, exploratory CUSUM,
  FEVD-order sensitivity, rolling connectedness, and robustness grids.

Method details live in [`docs/methodology/`](docs/methodology/).

## Key Results

| Question | Diagnostic | Output |
|---|---|---|
| Which factor blocks matter? | Block attribution and ablation | [`T03_block_attribution.csv`](outputs/tables/T03_block_attribution.csv) |
| Do ETF flows line up with returns? | ETF lead-lag grid | [`T04_etf_lead_lag.csv`](outputs/tables/T04_etf_lead_lag.csv) |
| How do correlations evolve? | Rolling and pre/post correlation diagnostics | [`T05_correlation_regime.csv`](outputs/tables/T05_correlation_regime.csv) |
| What does liquidity look like? | Stablecoin and TVL proxies | [`T06_stablecoin_liquidity.csv`](outputs/tables/T06_stablecoin_liquidity.csv) |
| How do BTC-native variables behave? | Native registry and ablation | [`T07_native_factor_ablation.csv`](outputs/tables/T07_native_factor_ablation.csv) |
| Are there regime breaks? | Chow and single-break sup-F | [`T08_structural_breaks.csv`](outputs/tables/T08_structural_breaks.csv) |
| How connected are BTC, ETH, and TradFi variables? | VAR/FEVD connectedness | [`T09_connectedness.csv`](outputs/tables/T09_connectedness.csv) |
| Are results robust to modeling choices? | Sensitivity grid | [`T10_robustness.csv`](outputs/tables/T10_robustness.csv) |

Main findings:

1. BTC full-stack fit is heavily influenced by native valuation and flow-state
   variables, especially MVRV-style valuation state.
2. ETF-flow intensity has strong same-day association, but daily data cannot
   identify causal flow impact.
3. Rolling correlations show time-varying BTC/ETH integration with TradFi and
   volatility variables.
4. Stablecoin supply and TVL are useful liquidity context, not identified
   liquidity shocks.
5. Structural-break diagnostics are Chow and single-break sup-F diagnostics,
   not full multi-break identification.
6. Advanced attribution and robustness diagnostics are available in the
   methodology appendix and model cards.

## Figures

The public figures are rendered as dark institutional research cards from the
canonical output tables. The full contact sheet is
[`outputs/figures/visual_gallery.png`](outputs/figures/visual_gallery.png).

### Data Coverage

![Frozen BTC/ETH multi-source panel](outputs/figures/F01_data_coverage.png)

Source: [`T01_source_inventory.csv`](outputs/tables/T01_source_inventory.csv) and
[`T02_panel_coverage.csv`](outputs/tables/T02_panel_coverage.csv). Model card:
[`factor_exposure.md`](outputs/model_cards/factor_exposure.md).

### BTC Factor Attribution

![BTC factor attribution](outputs/figures/F02_btc_block_attribution.png)

Source: [`T03_block_attribution.csv`](outputs/tables/T03_block_attribution.csv)
and [`T03_rolling_block_partial_r2_btc_180d.csv`](outputs/tables/T03_rolling_block_partial_r2_btc_180d.csv).
Model card: [`block_attribution.md`](outputs/model_cards/block_attribution.md).

### ETF Flow Lead-Lag

![BTC ETF-flow lead-lag](outputs/figures/F03_btc_etf_lead_lag.png)

Source: [`T04_etf_lead_lag.csv`](outputs/tables/T04_etf_lead_lag.csv). Model
card: [`etf_flow_lead_lag.md`](outputs/model_cards/etf_flow_lead_lag.md).
Lag convention: `lag < 0` means flow is shifted earlier and leads the target
return. This is association, not causality.

### Rolling Correlations

![BTC rolling correlations](outputs/figures/F04_btc_rolling_correlations.png)

Source: [`T05_rolling_correlations.csv`](outputs/tables/T05_rolling_correlations.csv)
and [`T05_correlation_regime.csv`](outputs/tables/T05_correlation_regime.csv).
Model card: [`rolling_correlations.md`](outputs/model_cards/rolling_correlations.md).

### Liquidity And Native Factors

![Stablecoin supply and TVL](outputs/figures/F05_stablecoin_supply_tvl.png)

Source: [`T06_stablecoin_liquidity.csv`](outputs/tables/T06_stablecoin_liquidity.csv).
Model card: [`stablecoin_liquidity.md`](outputs/model_cards/stablecoin_liquidity.md).

![BTC-native dashboard](outputs/figures/F06_btc_native_dashboard.png)

Source: [`T07_native_factor_ablation.csv`](outputs/tables/T07_native_factor_ablation.csv)
and [`T07_btc_native_correlations.csv`](outputs/tables/T07_btc_native_correlations.csv).
Model card: [`btc_native_factors.md`](outputs/model_cards/btc_native_factors.md).

### Connectedness And Robustness

![Connectedness](outputs/figures/F07_connectedness.png)

Source: [`T09_connectedness.csv`](outputs/tables/T09_connectedness.csv) and
[`T09_rolling_connectedness.csv`](outputs/tables/T09_rolling_connectedness.csv).
Model card: [`connectedness.md`](outputs/model_cards/connectedness.md).

![Robustness](outputs/figures/F08_robustness_grid.png)

Source: [`T10_robustness.csv`](outputs/tables/T10_robustness.csv). Model card:
[`robustness.md`](outputs/model_cards/robustness.md).

The compact result-card view is
[`F09_key_results_cards.png`](outputs/figures/F09_key_results_cards.png), and
the styled table card is
[`T00_key_results_table.png`](outputs/figures/T00_key_results_table.png).

## Reproduce

```powershell
uv sync --all-extras
uv run python scripts/make_hero_figures.py
uv run pytest
uv run mypy src/cqresearch
uv run python scripts/run_all.py
```

## Repository Structure

```text
README.md              public project overview
Data/                  frozen source-data tree
docs/                  methodology, architecture, data, and decisions
outputs/               canonical reports, figures, tables, model cards, manifest
scripts/               reproducible entry points and legacy-compatible pipelines
src/cqresearch/        reusable Python package
tests/                 unit tests
archive/               retained provenance, not the public workflow
```

## Outputs

- Reports: [`outputs/report/`](outputs/report/)
- Figures: [`outputs/figures/`](outputs/figures/)
- Tables: [`outputs/tables/`](outputs/tables/)
- Model cards: [`outputs/model_cards/`](outputs/model_cards/)
- Manifest: [`outputs/manifest.json`](outputs/manifest.json)

## Limitations

- Daily data cannot identify intraday mechanisms or order flow.
- ETF-flow, stablecoin, and native-factor outputs are reduced-form diagnostics,
  not causal identification.
- Stablecoin supply and TVL are proxies, not proven liquidity shocks.
- Structural-break diagnostics use Chow and single-break sup-F tests, not full
  Bai-Perron multiple-break estimation.
- Advanced attribution depends on block definitions and the selected feature
  set.
- Frozen data makes the project reproducible, but it is not a live market
  monitor.

## Data And License Notes

Code and generated artifacts are organized for reproducible research review.
External datasets and third-party references retain their upstream terms. See
the source catalog under [`docs/data/catalog/`](docs/data/catalog/) for the
frozen data inventory.
