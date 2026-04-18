# Data Spec — Sources, Calendar, Panel Contract

> Skeleton. Owned by the Data Lead. Fill in during Sprint 1 alongside agent 01 (data cleaning).

**Status:** DRAFT — v0.1 (2026-04-18)
**Canonical plan:** [`project_research_plan.md`](../../project_research_plan.md) §6, §11.1-§11.2

---

## 1. Sources
- CryptoQuant: on-chain BTC/ETH/USDC/USDT/WBTC (addresses, derivatives, flows, fees, supply, transactions). Files under `Data/CryptoQuant/`.
- FRED: macro (rates, credit, vol, FX, policy, stress). Files under `Data/FRED/`.
- DefiLlama: TVL, chain metrics, stablecoin mcaps, RWA, ETFs, DATs. Files under `Data/DefiLlama/`.
- Farside: BTC/ETH/SOL spot-ETF flows. Files under `Data/Farside ETF Data/`.
- AlternativeMe: Fear & Greed. Files under `Data/AlternativeMe/`.
- Artemis: chain metrics (optional). Files under `Data/Artemis/`.
- Tradingview: CME futures, price candles. Files under `Data/Tradingview/`.

## 2. Calendar
- Default: `calendar_daily` (UTC, 7-day). See `config/calendars.yml`.
- TradFi alignment: `market_trading_daily` (NYSE). Used when joining macro/FRED with CME futures.

## 3. Factor-block composition
Canonical: `config/factor_blocks.yml`. Any drift between `factor_blocks.yml` and `Data/MASTER_DATA.md` is a P0 bug for agent 01.

## 4. Panel contract
- `reports/panels/master_daily.parquet` — index = `date` (UTC, daily), columns = feature name + `<feature>__status`.
- `reports/panels/master_daily_columns.md` — machine-readable catalog: feature, source file, unit, block, imputation rule, date range, pct_null.

## 5. Aggregation rules
- BTC vs WBTC: NEVER sum. WBTC goes in its own column tagged `btc_ecosystem: wrapped_on_eth`.
- ETH L1 vs L2: NEVER sum as "users". Emit three columns: `eth_l1_only`, `eth_l2_sum`, `eth_l2_share_of_broad`.
- Stablecoin mcap: sum only within `stable_category` (USDT, USDC, other). See `Data/CryptoQuant/USDC/...` and `Data/DefiLlama/Stablecoins/`.

## 6. Missingness taxonomy
Every feature column emits a parallel `<feature>__status ∈ {ok, stale, structural, missing}`.
- **ok**: value observed today and no flag triggered.
- **stale**: value unchanged for > 3 consecutive days where variance > 0 historically.
- **structural**: observation not yet possible (e.g. ETF flow before 2024-01-11).
- **missing**: data provider outage (ETL retry recommended).

## 7. Units
- Prices in USD unless suffixed.
- Percents as decimals (0.05 not 5.0). Columns ending `_pct` or `_bps` state the unit.
- Flows in USD (positive = inflow to the labelled entity).

## 8. Snapshot dates (pinned)
See `config/curation_snapshots.yml`. Panels built from a snapshot are tagged in the filename: `master_daily__<snapshot>.parquet`.

## 9. Open issues (to be populated by agent 01)
- …
