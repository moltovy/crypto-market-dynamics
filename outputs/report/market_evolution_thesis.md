# Market Evolution Thesis

The market-structure extension adds a public, reduced-form context layer around the factor lab: DeFi TVL, stablecoin supply, CEX/DEX activity, sentiment, BTC dominance/cycle markers, RWA/DAT growth, and optional Binance liquidity ranks.

The release is designed to work without paid/live data. It uses the frozen tracked dataset first and enriches from `data_cache/` only when optional DefiLlama, Binance, or CoinMarketCap cache is available. Generated feature rows across the public market-structure tables: 7421.

Point-in-time market-cap universe outputs remain skipped until `data_cache/defillama/crypto_universe_monthly_2020_2026.csv` is supplied and ingested.

Monthly snapshots support composition, concentration, rank turnover, and cycle-phase structure. Daily OHLCV is still required for returns, breadth, volatility, beta, drawdowns, dispersion, and event-response analysis.

Interpretation stays descriptive. Binance ranks are exchange-liquidity ranks, stablecoin/TVL variables are liquidity proxies, and ETF-flow language remains contemporaneous association rather than causal identification.
