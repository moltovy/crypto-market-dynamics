# Market-Structure Limitations

- DefiLlama Pro-only datasets are skipped when key or plan access is missing.
- Binance does not provide historical market-cap rankings, so the Binance universe is liquidity-ranked only.
- Current order-book and ticker endpoints are snapshots and are not used as historical depth.
- Stablecoin supply and TVL are proxies, not proven causal drivers.
- CMC Fear & Greed live refresh requires `CMC_API_KEY`; cached history is included when present.
- Monthly market-cap snapshots support structure/composition diagnostics only; a full point-in-time daily OHLCV/mcap panel is required for survivorship-free altseason performance, breadth, volatility, beta, drawdown, dispersion, and event-return analysis.
- The current daily constituent lab uses a DefiLlama current-top50 exploratory cohort and should not be used as true historical top100 or primary altseason evidence.
