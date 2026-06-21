# Data License And Source Notes

The repository code is licensed separately under `LICENSE`.

Raw/provider exports are local-only under `data_local/` and are not redistributed by this repository. `DATA_LICENSE.md` documents known caveats but does not grant provider redistribution rights.

This project is not affiliated with, endorsed by, or published on behalf of CryptoQuant, Artemis, TradingView, DefiLlama, Farside, AlternativeMe, FRED, or any other data provider.

- FRED macro series are public Federal Reserve Economic Data series with attribution.
- DefiLlama, AlternativeMe, and Farside inputs may be public web/API sources, but public availability is not the same as redistribution permission.
- CryptoQuant, Artemis, and TradingView exports may carry provider-specific or licensed redistribution restrictions. The public repository keeps those raw inputs local-only.
- Local caches, raw exports, interim panels, and generated feature stores stay under ignored `data_local/`.

Public users can run smoke validation against committed semantic outputs without provider data. A full local rebuild requires legally obtained provider inputs placed under `data_local/raw/`. See `outputs/report/provider_data_disposition.md` for provider-group disposition and release recommendations.
