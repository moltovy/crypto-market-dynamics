# Market-Structure Methodology

Raw optional payloads are stored in gitignored `data_cache/{defillama,binance,coinmarketcap}/raw`. Normalized release-ready CSVs are written under `Data/MarketStructure/`.

Point-in-time market-cap top100 universes require point-in-time market-cap source data. The pipeline refuses to backfill a historical top100 from a current list. Binance top100 outputs are labeled as exchange-liquidity ranks based on rolling quote volume.

CMC Fear & Greed uses the official `v3/fear-and-greed/historical` client when `CMC_API_KEY` is available. Once cached, the normalized CMC history can be rebuilt without the key. If no CMC cache exists, the tracked AlternativeMe series remains the baseline sentiment source.
