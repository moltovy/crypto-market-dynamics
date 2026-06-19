# Market Evolution Thesis

The market-structure extension adds a public, reduced-form context layer around the factor lab: DeFi TVL, stablecoin supply, CEX/DEX activity, sentiment, BTC dominance/cycle markers, RWA/DAT growth, and optional Binance liquidity ranks.

The release is designed to work without paid/live data. It uses the frozen tracked dataset first and enriches from `data_cache/` only when optional DefiLlama, Binance, or CoinMarketCap cache is available. Generated feature rows across the public market-structure tables: 4365.

Interpretation stays descriptive. Binance ranks are exchange-liquidity ranks, stablecoin/TVL variables are liquidity proxies, and ETF-flow language remains contemporaneous association rather than causal identification.
