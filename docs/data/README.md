# Data Catalog

This folder is the clean public entry point for the frozen data inventory. Raw
and curated source files remain under the historical `Data/` tree for backward
compatibility with existing scripts.

The canonical public output packet is `outputs/`.

Market-structure extension details are in `docs/data/market_structure.md`. The
tracked normalized extension files live under `Data/MarketStructure/`, while raw
optional API payloads stay in gitignored `data_cache/`.
