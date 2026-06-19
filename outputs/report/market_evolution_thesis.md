# Market Evolution Thesis

The market-structure extension adds a public, reduced-form context layer around the factor lab: DeFi TVL, stablecoin supply, CEX/DEX activity, sentiment, BTC dominance/cycle markers, RWA/DAT growth, and optional Binance liquidity ranks.

The release is designed to work without paid/live data. It uses the frozen tracked dataset first and enriches from `data_cache/` only when optional DefiLlama, Binance, or CoinMarketCap cache is available. Generated feature rows across the public market-structure tables: 67933.

The local DefiLlama monthly point-in-time top200 universe is integrated for market-cap composition, concentration, clean-risk top100 construction, rank turnover, and cycle/ETF phase structure. When the frozen master daily panel is available, the build also creates a lagged/as-of monthly context layer and descriptive BTC/ETH return-regime diagnostics.

The available DefiLlama daily top50 ex-stablecoin OHLCV sample is integrated for exploratory altseason breadth, dispersion, rolling beta, rotation, and event-response diagnostics. It is explicitly labeled as a current-constituent sample rather than a point-in-time top100 panel.

Monthly snapshots support composition, concentration, rank turnover, and cycle-phase structure. A full point-in-time daily OHLCV/mcap constituent panel is still required for survivorship-free returns, breadth, volatility, beta, drawdowns, dispersion, and event-response analysis.

Interpretation stays descriptive. Binance ranks are exchange-liquidity ranks, stablecoin/TVL variables are liquidity proxies, and ETF-flow language remains contemporaneous association rather than causal identification.
