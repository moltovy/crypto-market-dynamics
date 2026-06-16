# Optional Free-Data Source Decision Table

| Source | Value | Overlap | Auth / rate-limit notes | Maintenance | Recommendation |
|---|---|---|---|---|---|
| DefiLlama | Cross-check DeFi TVL and chain-level liquidity coverage. | High with existing DefiLlama curated CSVs. | No key for public endpoints; rate limits can change. | Low | Useful as an optional refresh or audit source, not core. |
| CoinGecko | Free market-cap, price, and volume history for crypto assets. | Medium; useful for benchmark expansion and sanity checks. | Free tier has rate limits; paid plans exist but are not required here. | Medium | Optional benchmark extension only. |
| Binance public klines | Exchange-native OHLCV for liquid symbols. | Medium with TradingView price history. | No key for spot klines; endpoint availability varies by jurisdiction. | Medium | Useful for reproducible microstructure appendices. |
| FRED | Macro rates, spreads, and risk proxies. | High with existing curated FRED inputs. | Free API key normally required for official endpoint. | Low | Keep as optional refresh scaffolding; do not require for core releases. |

## Core-Release Decision

Do not add these sources to v2.1 or v2.2 core reproduction. Use them only for a
future optional refresh workflow with explicit cache/versioning rules.
