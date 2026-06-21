# Data Catalog

This folder is the public entry point for data coverage, provider disposition,
and reproducibility notes. Raw and curated provider exports are local-only and
ignored by Git.

Expected local layout for a reproducible source build:

```text
data_local/
  raw/
    cryptoquant/
    artemis/
    tradingview/
    defillama/
    farside/
    fred/
    alternativeme/
    market_structure/
  interim/
  processed/
  curated/
  metadata/
```

The public repository ships code, docs, derived semantic outputs, and
reproducibility instructions. Users with source access can recreate the local
provider buckets above; users without source access can still inspect the
derived outputs under `research/`.
