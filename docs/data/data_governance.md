# Data Governance

Raw and curated provider exports are local-only under `data_local/raw/` and are ignored by Git. Generated feature stores live under `data_local/processed/`; public-safe semantic tables, reports, metadata, figures, claims, and manifests live under `research/`.

Asset joins use canonical IDs where available. Selected major assets are defined in `config/assets.yml`; Toncoin is explicitly separated from Tokamak Network, and wrapped/productized assets are separated from governance/infrastructure risk assets.

No source should be silently substituted for a weaker dataset. If coverage is insufficient, the pipeline writes a qualified or skipped output rather than fabricating data.
