# Market-Structure Methodology

Raw optional payloads are stored in gitignored `data_cache/{defillama,binance,coinmarketcap}/raw`. Normalized release-ready CSVs are written under `Data/MarketStructure/`.

Point-in-time market-cap top100 universes require point-in-time market-cap source data. The pipeline refuses to backfill a historical top100 from a current list. Binance top100 outputs are labeled as exchange-liquidity ranks based on rolling quote volume.

When `data_cache/defillama/crypto_universe_monthly_2020_2026.csv` is present, `scripts/ingest_defillama_monthly_universe.py` validates and normalizes it into `Data/MarketStructure/DefiLlama/`. The build then constructs full, ex-stable, and clean-risk top100 universes using internal classifications rather than upstream risk labels.

CMC Fear & Greed uses the official `v3/fear-and-greed/historical` client when `CMC_API_KEY` is available. Once cached, the normalized CMC history can be rebuilt without the key. If no CMC cache exists, the tracked AlternativeMe series remains the baseline sentiment source.

When `data_cache/defillama/top50_current_ex_stable_daily_ohlcv_2020_2026.csv` is present, `scripts/ingest_defillama_daily_constituents.py` validates and normalizes it into `Data/MarketStructure/DefiLlama/`. The resulting daily lab is explicitly labeled as `current_top50_exploratory_current_cohort`, not a point-in-time top100/top200 universe.
