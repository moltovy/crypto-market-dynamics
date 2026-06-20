# Crypto Market Dynamics

## Factor, Liquidity, Leverage, and Market-Structure Research

Crypto Market Dynamics is a reproducible research-code project studying how crypto market behavior evolved from 2020-2026 across native valuation state, macro integration, ETF access, leverage, stablecoin/DeFi state, selected major assets, point-in-time market structure, and BTC/ETH event windows.

The project is descriptive. It is not a price-forecasting system, trading strategy, or causal-identification claim.

## Research Questions

1. How mechanically linked are MVRV and holder-profit metrics to BTC price/returns?
2. After removing mechanically linked valuation-state measures, how did BTC/ETH contemporaneous TradFi exposure and lagged-state associations evolve?
3. Are leverage and liquidation variables more informative for volatility/tail stress than average returns?
4. How did ETF access relate to market plumbing and risk integration?
5. How do stablecoin and DeFi state variables relate to BTC/ETH returns and BTC volatility?
6. How do selected major assets differ in volatility, drawdown, and beta after accounting for coverage?
7. How did PIT market composition, concentration, and turnover evolve?

## Results At A Glance

| question                  | finding                                                                                     | key_statistic                                                                                                                                                                                                               | sample_frequency                   | evidence_grade   | interpretation                                                               | caveat                                                | source_table                                 |
|:--------------------------|:--------------------------------------------------------------------------------------------|:----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------|:-----------------------------------|:-----------------|:-----------------------------------------------------------------------------|:------------------------------------------------------|:---------------------------------------------|
| MVRV mechanics            | MVRV is retained as a mechanically price-linked valuation-state diagnostic.                 | corr(BTC return, d-log MVRV)=0.9966; R2=0.9932; median abs residual / median abs BTC return=1.14e-07                                                                                                                        | 2020-2026 daily                    | B                | Use lagged state regimes; exclude same-day MVRV from primary BTC/ETH models. | Mechanical target overlap.                            | mvrv_mechanical_link_audit.csv               |
| TradFi exposure evolution | Contemporaneous exposure comparisons use synchronized business-date and Friday calendars.   | BTC equity block pre-BTC-ETF delta R2=0.0249 (n=797) vs BTC-ETF-era delta R2=0.0884 (n=436); ETH equity block pre-BTC-ETF delta R2=0.0193 (n=797) vs BTC-ETF-era delta R2=0.1076 (n=436); period comparison, not ETF effect | business-date daily; Friday weekly | B                | Period comparison of co-movement, not an ETF-effect estimate.                | Collinearity and overlapping rolling windows.         | block_delta_r2.csv                           |
| ETF plumbing              | ETF flow intensity is split into lag 0 and lag 1 on ETF trading dates.                      | BTC lag0 return corr=0.379 (n=820) vs lag1=0.049 (n=819); ETH lag0 return corr=0.226 (n=627) vs lag1=0.086 (n=626)                                                                                                          | ETF trading daily                  | B                | Market-plumbing association only.                                            | Short sample and reporting timing.                    | etf_flow_associations.csv                    |
| Leverage and tail stress  | Tail-day rates are reported for pre-specified Q1/Q3/Q5 leverage states.                     | Q1 low tail-day rate=7.06% (n=453); Q3 tail-day rate=4.20% (n=452); Q5 high tail-day rate=7.73% (n=453); read as U-shaped state pattern                                                                                     | daily                              | B                | U-shaped pattern, not only the highest-leverage quintile.                    | No liquidation initiation-cause claim.                | leverage_tail_risk_summary.csv               |
| Stablecoin/DeFi state     | Raw USD TVL is valuation-sensitive; stablecoin supply is the cleaner local liquidity proxy. | BTC same-week raw USD TVL corr=0.679 (n=327); ETH same-week raw USD TVL corr=0.761 (n=327); TVL labeled valuation-sensitive                                                                                                 | Sunday weekly                      | B                | Treat TVL as DeFi balance-sheet state, not pure inflow.                      | No price-adjusted TVL source is available locally.    | valuation_contamination_audit.csv            |
| PIT market structure      | PIT monthly snapshots support composition, concentration, and turnover evidence.            | 2026-06-16 partial snapshot (month=2026-06) top10 share=87.64%, HHI=0.334                                                                                                                                                   | monthly                            | A                | Use for market structure only.                                               | No daily PIT performance.                             | pit_market_structure_summary.csv             |
| Selected-major risk       | Selected-major risk is coverage-aware and reports comparable-window metrics.                | 10 assets comparable from 2024-11-30 to 2026-06-16; HYPE max-coverage n=564                                                                                                                                                 | daily current-source coverage      | B                | Compare risk only with coverage caveats.                                     | HYPE is short-history; TON is canonical-source only.  | selected_major_comparable_window_metrics.csv |
| Event atlas               | Configured BTC/ETH events use equal-length empirical placebo windows.                       | BTC,ETH event windows use block size=10; median eligible placebo windows=2007; convention +1 through +10                                                                                                                    | daily                              | C                | Descriptive event-window context.                                            | Not bootstrap causal inference.                       | event_inference.csv                          |
| Deferred PIT altseason    | True PIT historical altseason return analysis is deferred.                                  | No daily PIT constituent OHLCV/mcap history is available.                                                                                                                                                                   | not available                      | C                | Monthly PIT supports structure, not daily performance.                       | Current-cohort daily outputs are survivorship-biased. | claim_inventory.csv                          |


## Data

The build uses local curated data under `Data/`: CryptoQuant, Artemis, DefiLlama, FRED, Farside, TradingView, AlternativeMe/CMC, and a monthly DefiLlama PIT market-universe file. This repository is not affiliated with those providers. Data-use caveats are separated in [DATA_LICENSE.md](DATA_LICENSE.md), but that file does not resolve provider redistribution rights. Source coverage is summarized in [data_source_coverage.csv](outputs/tables/data_source_coverage.csv), provider release risk is classified in [provider_data_disposition.csv](outputs/tables/provider_data_disposition.csv), and TVL/OI price-content risk is audited in [valuation_contamination_audit.csv](outputs/tables/valuation_contamination_audit.csv).

## MVRV Mechanics And On-Chain State

![MVRV mechanics](outputs/figures/public/01_mvrv_mechanics.png)

MVRV is a valuation-state diagnostic with mechanical price-state content. Same-day `d_log_mvrv` is excluded from the primary BTC/ETH exposure models; lagged MVRV state appears as conditioning context. The audit reports same-interval identity residuals and a residual-to-return scale comparison.

Source: [mvrv_mechanical_link_audit.csv](outputs/tables/mvrv_mechanical_link_audit.csv)

## BTC/ETH Ex-MVRV Exposure Evolution

![Factor strength by regime](outputs/figures/public/02_factor_strength_by_regime.png)

The exposure tables split economically distinct families: contemporaneous TradFi co-movement models, lagged-state association models, and ETF-era augmented market-plumbing models. Daily TradFi models use common business-date BTC/ETH returns; weekly TradFi models use Friday-to-Friday returns. Every full/reduced comparison uses one complete-case sample with same-support checks. Drop-block delta R-squared is reported separately from conventional partial R-squared.

![TradFi integration over time](outputs/figures/public/03_tradfi_integration_over_time.png)

Source: [block_delta_r2.csv](outputs/tables/block_delta_r2.csv), [rolling_tradfi_exposures.csv](outputs/tables/rolling_tradfi_exposures.csv)

## ETF Institutionalization And Market Plumbing

![ETF market plumbing](outputs/figures/public/04_etf_market_plumbing.png)

ETF flows are market-plumbing variables with reporting-timing caveats. ETF-era augmented models include flow intensity separately at lag 0 and lag 1. Flow-return grids and absorption ratios are descriptive associations, not causal valuation statements.

Source: [etf_market_plumbing_summary.csv](outputs/tables/etf_market_plumbing_summary.csv)

## Leverage And Liquidation Stress

![Leverage and liquidation stress](outputs/figures/public/05_leverage_liquidation_stress.png)

Leverage, funding, OI, and liquidation variables are evaluated as stress and volatility-state measures. Lagged leverage/funding/OI states are separated from same-day liquidation signatures and post-event responses. Liquidations are shown as percent of prior-day OI or basis points of prior-day market cap.

Source: [leverage_tail_risk_summary.csv](outputs/tables/leverage_tail_risk_summary.csv)

## Stablecoin And DeFi Liquidity

![Stablecoin and DeFi liquidity](outputs/figures/public/06_stablecoin_defi_liquidity.png)

Stablecoin and DeFi metrics use the Sunday-ended crypto weekly panel. Stablecoin supply is the cleaner local liquidity-state proxy; raw USD TVL growth is labeled `valuation_sensitive_defi_tvl_growth` because USD TVL embeds deposited-asset price effects. The project does not call proxy changes exogenous liquidity shocks.

Source: [stablecoin_defi_liquidity_summary.csv](outputs/tables/stablecoin_defi_liquidity_summary.csv)

## Point-In-Time Market Structure

![Point-in-time market structure](outputs/figures/public/07_point_in_time_market_structure.png)

The monthly PIT top-200 source is used for composition, concentration, and turnover. It is not used for daily historical altseason performance.

Source: [pit_market_structure_summary.csv](outputs/tables/pit_market_structure_summary.csv)

## Selected Major Assets

![Selected major asset risk](outputs/figures/public/08_selected_major_asset_risk.png)

Selected major assets use canonical IDs and explicit coverage windows. Current daily constituent coverage begins 2022-12-31/2023 for most selected assets, HYPE is short-history, and Toncoin is sourced only from the canonical `coingecko:the-open-network` local series when present. Comparable-window metrics are reported separately.

Source: [selected_major_risk_metrics.csv](outputs/tables/selected_major_risk_metrics.csv)

## Cycle And Event Atlas

![Event response matrix](outputs/figures/public/09_event_response_matrix.png)

Event windows are descriptive empirical placebo-window tests. The post-10-day convention is `+1` through `+10`, placebo windows have the same block length, and registered-event overlaps are excluded. The small number of events is not enough for forecast rules or causal structural claims.

Source: [event_response_matrix.csv](outputs/tables/event_response_matrix.csv)

## Methods And Evidence Standards

Public claims map to [evidence_ledger.csv](outputs/tables/evidence_ledger.csv) and claim dispositions are summarized in [claim_inventory.csv](outputs/tables/claim_inventory.csv). Evidence grades follow the project charter in [research_charter.md](docs/decisions/research_charter.md).

## Limitations

No causal claims are made. MVRV is a valuation-state diagnostic with mechanical price-state content. ETF and liquidation variables are timing-sensitive. Stablecoin/DeFi variables are proxies. Current-top50 daily cohort analysis is exploratory and survivorship-biased. True PIT historical altseason performance is deferred until constituent daily data exists. Provider data redistribution rights remain a public-release risk where marked uncertain/restricted.

## Reproduce

```powershell
uv sync --all-extras
uv run ruff check src/cqresearch scripts tests
uv run mypy src/cqresearch
uv run python scripts/run_all.py
uv run pytest
uv run python scripts/check_public_surface.py
```

## Repository Structure

- `Data/` curated local source data.
- `config/` asset, event, feature, and figure registries.
- `src/cqresearch/` maintained data, feature, modeling, analysis, reporting, visualization, and pipeline code.
- `scripts/` thin CLI entry points.
- `outputs/` generated public tables, figures, reports, and model cards.
- `docs/` methodology, data, architecture, and decisions.
- `archive/` historical material excluded from public indexing.
