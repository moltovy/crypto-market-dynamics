# Data Contract

Crypto Market Factor Lab uses a frozen daily panel spanning 2020-01-01 through
2026-04-11 with 2,293 rows and 63 columns. The frozen panel is the public
reproduction contract: public outputs can be regenerated without paid data,
live API calls, or raw-data mutation.

## Source Families

- CryptoQuant: BTC/ETH native, market-structure, and on-chain indicators.
- Farside ETF Data: BTC and ETH ETF-flow measures.
- DefiLlama: TVL, stablecoin, and DeFi liquidity context.
- FRED: macro, rates, dollar, and volatility variables.
- TradingView: cross-asset market data.
- Artemis: ETF, DeFi, and chain context.
- AlternativeMe: sentiment.

Raw and curated source files remain under `Data/` for compatibility. The clean
catalog entry point is `docs/data/catalog/`.
