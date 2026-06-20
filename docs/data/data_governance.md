# Data Governance

Tracked `Data/` files are treated as frozen/curated local sources. `data_cache/` is gitignored and reserved for raw API/cache payloads. Public outputs in `outputs/` are generated from code.

Asset joins use canonical IDs where available. Selected major assets are defined in `config/assets.yml`; Toncoin is explicitly separated from Tokamak Network, and wrapped/productized assets are separated from governance/infrastructure risk assets.

No source should be silently substituted for a weaker dataset. If coverage is insufficient, the pipeline writes a qualified or skipped output rather than fabricating data.
