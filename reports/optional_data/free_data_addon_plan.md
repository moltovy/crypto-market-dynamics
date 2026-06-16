# Free-Data Add-On Plan

## Purpose

The optional data layer gives the project a public roadmap for refreshes without
making the current portfolio releases depend on live endpoints.

## Current Implementation

- URL builders for DefiLlama, CoinGecko, Binance public klines, and FRED.
- Response normalizers that accept caller-supplied payload dictionaries/lists.
- Static unit tests with inline payloads.
- Offline scripts:
  - `uv run python scripts/optional_data/print_optional_urls.py`
  - `uv run python scripts/optional_data/write_source_registry.py`

## Guardrails

- No paid source is required.
- No network call is made by tests.
- No `Data/` file is modified.
- Optional refreshes should write to a separate cache/versioned folder, not to
  curated frozen raw data.

## Recommended Next Step

If a future sprint wants live refreshes, start with a small DefiLlama audit
against existing TVL coverage because it has high source overlap and low
maintenance burden.
