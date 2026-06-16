# Data Atlas - Portfolio v2

## Frozen Panel

- Date range: 2020-01-01 through 2026-04-11
- Rows: 2,293
- Columns: 63
- Source files in inventory: 490
- Machine-readable inventory: `Data/MASTER_DATA.csv`
- Human-readable inventory: `Data/MASTER_DATA.md`
- Curation log: `Data/_meta/curation_log.md`

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

## Highest Missingness Columns

These are not necessarily data-quality failures. ETF columns are structurally
missing before product launch, while newer funds can have very short live
histories.

| column        | first      | last       |   missing_pct |
|:--------------|:-----------|:-----------|--------------:|
| btc_etf_msbt  | 2026-04-08 | 2026-04-09 |         99.91 |
| eth_etf_ethb  | 2026-03-11 | 2026-04-10 |         98.65 |
| btc_etf_btc   | 2024-07-31 | 2026-04-10 |         73    |
| eth_etf_ethe  | 2024-07-23 | 2026-04-10 |         72.66 |
| eth_etf_total | 2024-07-23 | 2026-04-10 |         72.66 |
| eth_etf_qeth  | 2024-07-23 | 2026-04-10 |         72.66 |
| eth_etf_etha  | 2024-07-23 | 2026-04-10 |         72.66 |
| eth_etf_ezet  | 2024-07-23 | 2026-04-10 |         72.66 |
| eth_etf_feth  | 2024-07-23 | 2026-04-10 |         72.66 |
| eth_etf_ethv  | 2024-07-23 | 2026-04-10 |         72.66 |
| eth_etf_teth  | 2024-07-23 | 2026-04-10 |         72.66 |
| eth_etf_eth   | 2024-07-23 | 2026-04-10 |         72.66 |

## Core Feature Blocks

| Block | Examples | Use |
|---|---|---|
| Macro | Treasury yields, VIX, DXY, oil, policy rates | Risk and macro controls |
| Institutional | BTC/ETH ETF flows and market proxies | ETF-flow and TradFi plumbing |
| Liquidity | DeFi TVL and stablecoin supply | Crypto-dollar and funding proxy |
| Sentiment | Fear & Greed and uncertainty | Risk-appetite context |
| BTC-native | MVRV, exchange netflow, miner-to-exchange flow | BTC valuation and flow state |
| ETH-native | CME ETH basis and ETH ETF variables | ETH comparison state |

## Data Add-On Decision

Portfolio v2 keeps the frozen data as core. Free APIs such as DefiLlama, FRED,
CoinGecko, and Binance should remain optional unless they add a material,
cached, reproducible variable that is not already represented.
