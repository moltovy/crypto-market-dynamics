# Data Spec - Legacy Draft

> **Legacy warning:** this v0.1 data spec is retained for provenance only.
> The current portfolio v2 data contract is summarized in
> [`feature_registry.md`](./feature_registry.md) and the generated
> `reports/portfolio_v2/data_atlas.md`.

**Status:** LEGACY DRAFT - v0.1 (2026-04-18)

## 1. Sources

- CryptoQuant: on-chain BTC/ETH/USDC/USDT/WBTC files under `Data/CryptoQuant/`.
- FRED: macro rates, credit, volatility, FX, policy, and stress files under
  `Data/FRED/`.
- DefiLlama: TVL, chain metrics, stablecoin market caps, RWA, ETF, and DAT files
  under `Data/DefiLlama/`.
- Farside: BTC/ETH/SOL spot-ETF flow files under `Data/Farside ETF Data/`.
- AlternativeMe: Fear & Greed under `Data/AlternativeMe/`.
- Artemis: chain, ETF, perpetuals, DEX, lending, stablecoin, and RWA exports.
- TradingView: CME futures, price candles, DXY, and related market files.

## 2. Calendar

- Default master calendar: UTC daily crypto-7 calendar.
- TradFi alignment: business-day source series are aligned onto the daily panel
  according to `config/calendars.yml`.

## 3. Current Portfolio Contract

Portfolio v2 uses the frozen master panel documented by
`reports/panels/master_daily_meta.json`, `reports/panels/master_daily_coverage.csv`,
and `Data/MASTER_DATA.csv`. It does not require live data refreshes or paid data.

## 4. Historical Design Notes

Earlier notes about parallel `<feature>__status` columns and richer feature
catalogs were design goals, not current portfolio output claims. Any future
implementation should update `feature_registry.md` and the generated data atlas.
