# Feature Registry - Portfolio v2

**Status:** v1.0 portfolio registry  
**Source of truth:** `reports/panels/master_daily_meta.json`,
`Data/MASTER_DATA.csv`, and `config/factor_blocks.yml`

## Core Panel

The frozen master daily panel spans 2020-01-01 through 2026-04-11 with 2,293
rows and 63 columns. Portfolio v2 treats this panel as the reproducible core and
does not require live data refreshes.

## Factor Blocks

| Block | Representative columns | Portfolio use |
|---|---|---|
| Market prices | `btc_close`, `eth_close`, `spy_close`, `qqq_close`, `gld_close`, `dxy_tv_close` | Return construction and cross-asset comparison |
| Macro | `DGS10`, `DGS2`, `DFF`, `VIXCLS`, `DTWEXBGS`, `DCOILWTICO` | Rates, volatility, dollar, and macro stress controls |
| Institutional | `btc_etf_total`, `eth_etf_total`, ETF fund-level columns | ETF-flow intensity and market-plumbing diagnostics |
| Liquidity | `defi_tvl_usd`, `stables_total_usd` | DeFi/stablecoin liquidity proxy block |
| Sentiment | `fng_value`, `USEPUINDXD` | Risk appetite and policy-uncertainty context |
| BTC-native | `btc_exchange_netflow`, `btc_miner_to_exchange_flow`, `btc_mvrv` | BTC valuation and flow-state diagnostics |
| ETH-native | `cme_eth_basis_close` and ETH ETF columns | ETH comparison diagnostics |

## Portfolio v2.1 Derived Features

| Feature family | Columns / outputs | Portfolio use |
|---|---|---|
| Realized volatility | `btc_rv_30d`, `eth_rv_30d`, `spy_rv_30d` | Volatility targets and liquidity/RV figures |
| ETF lead-lag | lagged `btc_etf_intensity`, `eth_etf_intensity` | Market-plumbing association diagnostics |
| Stablecoin liquidity | z-scored `stables_total_usd_ret`, `defi_tvl_usd_ret`, `liquidity_composite` | Liquidity proxy context |
| Block partial R^2 | full-vs-reduced factor-block tables | Attribution discussion without Shapley/Owen claims |
| BTC-native lab | native ex-MVRV, MVRV-only, all-native groups | Separate valuation state from flow/state variables |

## Feature Construction Rules

- Price-like series use log returns.
- Rate, spread, sentiment, and selected native levels use first differences.
- ETF intensity equals USD ETF flow divided by prior-day USD market cap.
- Non-stationary levels should not be passed directly into regressions.
- Missingness and coverage must be disclosed in `data_atlas.md`.

## Optional Free Data Policy

New free data sources can be documented as optional add-ons, but they should not
be required for the frozen portfolio release unless they materially improve the
core story and can be cached reproducibly.
