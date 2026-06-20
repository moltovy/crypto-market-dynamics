# Data License And Source Notes

The repository code is licensed separately under `LICENSE`.

Tracked data files come from a mix of public, provider-exported, and locally curated sources:

- FRED macro series are public Federal Reserve Economic Data series with attribution.
- DefiLlama, AlternativeMe, and Farside-derived files are public web/API sources; cite the providers and verify current terms before redistribution.
- CryptoQuant, Artemis, and TradingView exports may carry provider-specific or licensed redistribution restrictions. The repository uses them as curated research inputs and documents reproducibility caveats.
- `data_cache/` is gitignored and is for local raw API/cache payloads only.

No API keys are required for the final offline build. Public users can reproduce generated outputs from the committed curated data, subject to the source-specific redistribution caveats above.
