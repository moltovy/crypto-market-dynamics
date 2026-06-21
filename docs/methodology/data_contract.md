# Data Contract

Crypto Market Dynamics uses local provider exports to generate derived semantic
tables, reports, and figures. Raw and curated provider files are not part of
the public Git contract; they live under ignored `data_local/` folders on
machines with source access.

## Source Families

- CryptoQuant: BTC/ETH native, market-structure, and on-chain indicators.
- Farside ETF Data: BTC and ETH ETF-flow measures.
- DefiLlama: TVL, stablecoin, and DeFi liquidity context.
- FRED: macro, rates, dollar, and volatility variables.
- TradingView: cross-asset market data.
- Artemis: ETF, DeFi, and chain context.
- AlternativeMe: sentiment.

Local raw provider buckets live under `data_local/raw/<provider>`. Generated
feature stores live under `data_local/processed/`. Final public semantic tables
live under `research/<module>/tables/`, with provider coverage and disposition
metadata tracked in `research/00_data_foundation/`.
