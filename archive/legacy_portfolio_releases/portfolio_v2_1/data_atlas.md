# Portfolio v2.1 Data Atlas

## Frozen Panel

- Date range: 2020-01-01 through 2026-04-11
- Rows: 2,293
- Columns: 63
- Source inventory rows: 490
- Machine-readable inventory: `Data/MASTER_DATA.csv`
- Human-readable inventory: `Data/MASTER_DATA.md`

## Source Inventory

| source           |   files |    rows |
|:-----------------|--------:|--------:|
| CryptoQuant      |     345 | 1181712 |
| Artemis          |      48 |   75302 |
| Tradingview      |      44 |   92157 |
| DefiLlama        |      28 |  306856 |
| FRED             |      21 |  166529 |
| Farside ETF Data |       3 |    1032 |
| AlternativeMe    |       1 |    2994 |

## New v2.1 Feature Families

| Family | Examples | Output |
|---|---|---|
| Block partial R^2 | Macro, TradFi, Liquidity, BTC native ex MVRV, MVRV, ETF Flow | `block_partial_r2_*.csv` |
| Lead-lag market plumbing | ETF intensity and stablecoin growth lags | `*_lead_lag_*.csv` |
| Rolling correlations | BTC/ETH vs TradFi, VIX, liquidity proxies | `rolling_correlations.csv` |
| Realized volatility | `btc_rv_30d`, `eth_rv_30d`, `spy_rv_30d` | `stablecoin_liquidity_features.csv` |
| BTC-native registry | basis, exchange flow, miner flow, valuation state | `native_factor_registry.csv` |

## Liquidity Feature Audit

| feature               |   count |   mean |    std |     min |     25% |     50% |    75% |    max |
|:----------------------|--------:|-------:|-------:|--------:|--------:|--------:|-------:|-------:|
| stables_total_usd_ret |    2292 | 0.0017 | 0.0048 | -0.0071 | -0.0005 |  0.0006 | 0.0024 | 0.0274 |
| defi_tvl_usd_ret      |    2292 | 0.0025 | 0.0265 | -0.0848 | -0.0108 |  0.0021 | 0.0163 | 0.0795 |
| liquidity_composite   |    2292 | 0      | 0.7666 | -2.5692 | -0.4045 | -0.1103 | 0.3233 | 4.148  |
| btc_rv_30d            |    2263 | 0.5368 | 0.1723 |  0.1876 |  0.407  |  0.5174 | 0.6506 | 1.0551 |
| eth_rv_30d            |    2263 | 0.719  | 0.2224 |  0.1738 |  0.5542 |  0.6975 | 0.8689 | 1.5389 |

## Data Policy

Portfolio v2.1 uses only the frozen committed panel and derived feature
transforms. No raw `Data/` file is modified and no live or paid source is
required for regeneration.
