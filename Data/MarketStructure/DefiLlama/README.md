# DefiLlama Market-Structure Curated Layer

Contains endpoint capability files and normalized public summaries derived from local DefiLlama cache when available. Pro-only datasets are skipped unless `DEFILLAMA_API_KEY` and plan access are present at runtime.

The optional `crypto_universe_monthly_2020_2026.csv` file is a local point-in-time monthly top200 market-cap universe. It is ingested from `data_cache/defillama/` only after validation and supports composition, concentration, clean-risk universe, rank-turnover, and cycle-phase structure diagnostics.

The optional `top50_current_ex_stable_daily_ohlcv_2020_2026.csv` file is a current-top50 exploratory daily OHLCV cohort. It supports current-cohort breadth, rotation, beta, dispersion, and event-response diagnostics, but it is survivorship-biased, not point-in-time, and not the primary altseason backtest.
