# Data curation log

First opened: 2026-04-17 03:09:47Z.
This file records what the curation scripts did to every file under `Data/`.

## Step 01 — raw hash manifest  _(run 2026-04-17 03:09:47Z)_

Scanned 450 files under `Data/`.
Wrote manifest to `Data/_meta/raw_manifest.csv`.

## Step 02 — Defi dedupe  _(run 2026-04-17 03:10:37Z)_

- No byte-identical duplicates found in `Data/Defi/`.

**Flagged for human review (not byte-identical, not touched):**
- Near-duplicate candidate group still present (different bytes, left untouched): `all_metrics_2026-04-17.csv` (sha=9d59687c005e), `all_metrics_2026-04-17 (1) volume.csv` (sha=77c64e35e0de)
- Near-duplicate candidate group still present (different bytes, left untouched): `ethereum_metrics_2026-04-17 (1).csv` (sha=da41c756d4be), `ethereum_metrics_2026-04-17 Fees and revenue.csv` (sha=6d732d3a1577), `ethereum_metrics_2026-04-17 volume.csv` (sha=06644b001306)

## Step 03 — merge Defi multi-part exports  _(run 2026-04-17 03:11:28Z)_

### stablecoin-mcap merge

Parts scanned:
  - `Defi/stablecoin-mcap-chart_combined_2026-04-17 (1) part 5.csv` ->  1981 rows x  25 data columns, 2020-11-14 .. 2026-04-17
  - `Defi/stablecoin-mcap-chart_combined_2026-04-17 (1) part 6.csv` ->  2102 rows x  25 data columns, 2020-07-16 .. 2026-04-17
  - `Defi/stablecoin-mcap-chart_combined_2026-04-17 (1) part 7.csv` ->  1934 rows x  25 data columns, 2020-12-31 .. 2026-04-17
  - `Defi/stablecoin-mcap-chart_combined_2026-04-17 part 1.csv` ->  3062 rows x  25 data columns, 2017-11-29 .. 2026-04-17
  - `Defi/stablecoin-mcap-chart_combined_2026-04-17 part 2.csv` ->  1963 rows x  25 data columns, 2020-12-02 .. 2026-04-17
  - `Defi/stablecoin-mcap-chart_combined_2026-04-17 part 3.csv` ->  2296 rows x  25 data columns, 2020-01-04 .. 2026-04-17
  - `Defi/stablecoin-mcap-chart_combined_2026-04-17 part 4.csv` ->  2776 rows x  25 data columns, 2018-09-11 .. 2026-04-17
  - `Defi/stablecoin-mcap-chart_combined_2026-04-17.csv` ->  1962 rows x  25 data columns, 2020-12-03 .. 2026-04-17

Merged output: `Defi/stablecoin_mcap_by_defillama_id__daily.csv` (3,062 rows x 200 id columns; 2017-11-29 .. 2026-04-17).
ID-to-name lookup written: `Defi/stablecoin_mcap_id_to_name.csv` (200 ids; 200 unresolved).

Archiving parts:
  - archived `Defi/stablecoin-mcap-chart_combined_2026-04-17 (1) part 5.csv` -> `Defi/_raw_parts/stablecoin_mcap/stablecoin-mcap-chart_combined_2026-04-17 (1) part 5.csv`
  - archived `Defi/stablecoin-mcap-chart_combined_2026-04-17 (1) part 6.csv` -> `Defi/_raw_parts/stablecoin_mcap/stablecoin-mcap-chart_combined_2026-04-17 (1) part 6.csv`
  - archived `Defi/stablecoin-mcap-chart_combined_2026-04-17 (1) part 7.csv` -> `Defi/_raw_parts/stablecoin_mcap/stablecoin-mcap-chart_combined_2026-04-17 (1) part 7.csv`
  - archived `Defi/stablecoin-mcap-chart_combined_2026-04-17 part 1.csv` -> `Defi/_raw_parts/stablecoin_mcap/stablecoin-mcap-chart_combined_2026-04-17 part 1.csv`
  - archived `Defi/stablecoin-mcap-chart_combined_2026-04-17 part 2.csv` -> `Defi/_raw_parts/stablecoin_mcap/stablecoin-mcap-chart_combined_2026-04-17 part 2.csv`
  - archived `Defi/stablecoin-mcap-chart_combined_2026-04-17 part 3.csv` -> `Defi/_raw_parts/stablecoin_mcap/stablecoin-mcap-chart_combined_2026-04-17 part 3.csv`
  - archived `Defi/stablecoin-mcap-chart_combined_2026-04-17 part 4.csv` -> `Defi/_raw_parts/stablecoin_mcap/stablecoin-mcap-chart_combined_2026-04-17 part 4.csv`
  - archived `Defi/stablecoin-mcap-chart_combined_2026-04-17.csv` -> `Defi/_raw_parts/stablecoin_mcap/stablecoin-mcap-chart_combined_2026-04-17.csv`

### cex-inflows merge

Parts scanned:
  - `Defi/cex-inflows-chart_combined_2026-04-17 part 1.csv` ->  1253 rows x  25 data columns, 2022-11-12 .. 2026-04-17
  - `Defi/cex-inflows-chart_combined_2026-04-17 part 2.csv` ->  1037 rows x  25 data columns, 2023-06-16 .. 2026-04-17
  - `Defi/cex-inflows-chart_combined_2026-04-17 part 3.csv` ->  1243 rows x  25 data columns, 2022-11-22 .. 2026-04-17

Merged output: `Defi/cex_net_inflows_by_exchange__daily.csv` (1,253 rows x 75 exchange columns; 2022-11-12 .. 2026-04-17).

Archiving parts:
  - archived `Defi/cex-inflows-chart_combined_2026-04-17 part 1.csv` -> `Defi/_raw_parts/cex_inflows/cex-inflows-chart_combined_2026-04-17 part 1.csv`
  - archived `Defi/cex-inflows-chart_combined_2026-04-17 part 2.csv` -> `Defi/_raw_parts/cex_inflows/cex-inflows-chart_combined_2026-04-17 part 2.csv`
  - archived `Defi/cex-inflows-chart_combined_2026-04-17 part 3.csv` -> `Defi/_raw_parts/cex_inflows/cex-inflows-chart_combined_2026-04-17 part 3.csv`

## Step 04 — normalize dates  _(run 2026-04-17 03:12:47Z)_

Per-source counts:
- **cryptoquant**: 342
- **artemis**: 47
- **farside**: 3
- **defi**: 12
- **defillama**: 6
- **tradingview**: 12
- **skip**: 1
- **snapshot**: 18
- **fail**: 5

**Failures / skipped non-snapshot files:**
- `Artemis/Artemis - Digital Asset Treasuries Overview.csv` (artemis): first column is `symbol`, skipped
- `CryptoQuant/BTC/Derivatives/Bitcoin Futures Taker CVD(Cumulative Volume Delta, 90-day) - Day.csv` (cryptoquant): no `Datetime` column, skipped
- `CryptoQuant/BTC/Market Indicator/Bitcoin Spot Taker CVD(Cumulative Volume Delta, 90-day) - Day.csv` (cryptoquant): no `Datetime` column, skipped
- `CryptoQuant/ETH/Derivatives/Ethereum Futures Taker CVD(Cumulative Volume Delta, 90-day) - Day.csv` (cryptoquant): no `Datetime` column, skipped
- `Defi/etf-history.csv` (defi): no recognized date column (first=`gecko_id`), skipped

## Step 04 — normalize dates  _(run 2026-04-17 03:13:44Z)_

Per-source counts:
- **cryptoquant**: 3
- **artemis**: 47
- **farside**: 3
- **defi**: 13
- **defillama**: 6
- **skip**: 1
- **snapshot**: 19
- **fail**: 354

**Failures / skipped non-snapshot files:**
- `CryptoQuant/BTC/Addresses/Bitcoin Active Addresses - Day.csv` (cryptoquant): EXCEPTION ValueError: cannot assemble with duplicate keys
- `CryptoQuant/BTC/Addresses/Bitcoin Active Receiving Addresses - Day.csv` (cryptoquant): EXCEPTION ValueError: cannot assemble with duplicate keys
- `CryptoQuant/BTC/Addresses/Bitcoin Active Sending Addresses - Day.csv` (cryptoquant): EXCEPTION ValueError: cannot assemble with duplicate keys
- `CryptoQuant/BTC/Derivatives/Bitcoin Estimated Leverage Ratio - All Exchanges - Day.csv` (cryptoquant): EXCEPTION ValueError: cannot assemble with duplicate keys
- `CryptoQuant/BTC/Derivatives/Bitcoin Funding Rates - All Exchanges - Day.csv` (cryptoquant): EXCEPTION ValueError: cannot assemble with duplicate keys
- `CryptoQuant/BTC/Derivatives/Bitcoin Long Liquidations - All Exchanges, All Symbol - Day.csv` (cryptoquant): EXCEPTION ValueError: cannot assemble with duplicate keys
- `CryptoQuant/BTC/Derivatives/Bitcoin Long Liquidations USD - All Exchanges, All Symbol - Day.csv` (cryptoquant): EXCEPTION ValueError: cannot assemble with duplicate keys
- `CryptoQuant/BTC/Derivatives/Bitcoin Open Interest - All Exchanges, All Symbol - Day.csv` (cryptoquant): EXCEPTION ValueError: cannot assemble with duplicate keys
- `CryptoQuant/BTC/Derivatives/Bitcoin Short Liquidations - All Exchanges, All Symbol - Day.csv` (cryptoquant): EXCEPTION ValueError: cannot assemble with duplicate keys
- `CryptoQuant/BTC/Derivatives/Bitcoin Short Liquidations USD - All Exchanges, All Symbol - Day.csv` (cryptoquant): EXCEPTION ValueError: cannot assemble with duplicate keys
- `CryptoQuant/BTC/Exchange Flows/Bitcoin Exchange Depositing Addresses - All Exchanges - Day.csv` (cryptoquant): EXCEPTION ValueError: cannot assemble with duplicate keys
- `CryptoQuant/BTC/Exchange Flows/Bitcoin Exchange Depositing Transactions - All Exchanges - Day.csv` (cryptoquant): EXCEPTION ValueError: cannot assemble with duplicate keys
- `CryptoQuant/BTC/Exchange Flows/Bitcoin Exchange In-House Flow (Mean) - All Exchanges - Day.csv` (cryptoquant): EXCEPTION ValueError: cannot assemble with duplicate keys
- `CryptoQuant/BTC/Exchange Flows/Bitcoin Exchange In-House Flow (Total) - All Exchanges - Day.csv` (cryptoquant): EXCEPTION ValueError: cannot assemble with duplicate keys
- `CryptoQuant/BTC/Exchange Flows/Bitcoin Exchange In-House Transactions - All Exchanges - Day.csv` (cryptoquant): EXCEPTION ValueError: cannot assemble with duplicate keys
- `CryptoQuant/BTC/Exchange Flows/Bitcoin Exchange Inflow (Mean) - All Exchanges - Day.csv` (cryptoquant): EXCEPTION ValueError: cannot assemble with duplicate keys
- `CryptoQuant/BTC/Exchange Flows/Bitcoin Exchange Inflow (Top10) - All Exchanges - Day.csv` (cryptoquant): EXCEPTION ValueError: cannot assemble with duplicate keys
- `CryptoQuant/BTC/Exchange Flows/Bitcoin Exchange Inflow (Total) - All Exchanges - Day.csv` (cryptoquant): EXCEPTION ValueError: cannot assemble with duplicate keys
- `CryptoQuant/BTC/Exchange Flows/Bitcoin Exchange Inflow - Spent Output Age Bands - All Exchanges - Day.csv` (cryptoquant): EXCEPTION ValueError: cannot assemble with duplicate keys
- `CryptoQuant/BTC/Exchange Flows/Bitcoin Exchange Inflow - Spent Output Value Bands - All Exchanges - Day.csv` (cryptoquant): EXCEPTION ValueError: cannot assemble with duplicate keys
- `CryptoQuant/BTC/Exchange Flows/Bitcoin Exchange Netflow (Total) - All Exchanges - Day.csv` (cryptoquant): EXCEPTION ValueError: cannot assemble with duplicate keys
- `CryptoQuant/BTC/Exchange Flows/Bitcoin Exchange Outflow (Mean) - All Exchanges - Day.csv` (cryptoquant): EXCEPTION ValueError: cannot assemble with duplicate keys
- `CryptoQuant/BTC/Exchange Flows/Bitcoin Exchange Outflow (Top10) - All Exchanges - Day.csv` (cryptoquant): EXCEPTION ValueError: cannot assemble with duplicate keys
- `CryptoQuant/BTC/Exchange Flows/Bitcoin Exchange Outflow (Total) - All Exchanges - Day.csv` (cryptoquant): EXCEPTION ValueError: cannot assemble with duplicate keys
- `CryptoQuant/BTC/Exchange Flows/Bitcoin Exchange Reserve - All Exchanges - Day.csv` (cryptoquant): EXCEPTION ValueError: cannot assemble with duplicate keys
- `CryptoQuant/BTC/Exchange Flows/Bitcoin Exchange Reserve USD - All Exchanges - Day.csv` (cryptoquant): EXCEPTION ValueError: cannot assemble with duplicate keys
- `CryptoQuant/BTC/Exchange Flows/Bitcoin Exchange Withdrawing Addresses - All Exchanges - Day.csv` (cryptoquant): EXCEPTION ValueError: cannot assemble with duplicate keys
- `CryptoQuant/BTC/Exchange Flows/Bitcoin Exchange Withdrawing Transactions - All Exchanges - Day.csv` (cryptoquant): EXCEPTION ValueError: cannot assemble with duplicate keys
- `CryptoQuant/BTC/Fees And Revenue/Bitcoin Block Rewards - Day.csv` (cryptoquant): EXCEPTION ValueError: cannot assemble with duplicate keys
- `CryptoQuant/BTC/Fees And Revenue/Bitcoin Block Rewards USD - Day.csv` (cryptoquant): EXCEPTION ValueError: cannot assemble with duplicate keys
- `CryptoQuant/BTC/Fees And Revenue/Bitcoin Fees (Total) - Day.csv` (cryptoquant): EXCEPTION ValueError: cannot assemble with duplicate keys
- `CryptoQuant/BTC/Fees And Revenue/Bitcoin Fees per Block (Mean) - Day.csv` (cryptoquant): EXCEPTION ValueError: cannot assemble with duplicate keys
- `CryptoQuant/BTC/Fees And Revenue/Bitcoin Fees per Block USD (Mean) - Day.csv` (cryptoquant): EXCEPTION ValueError: cannot assemble with duplicate keys
- `CryptoQuant/BTC/Fees And Revenue/Bitcoin Fees per Transaction (Mean) - Day.csv` (cryptoquant): EXCEPTION ValueError: cannot assemble with duplicate keys
- `CryptoQuant/BTC/Fees And Revenue/Bitcoin Fees per Transaction (Median) - Day.csv` (cryptoquant): EXCEPTION ValueError: cannot assemble with duplicate keys
- `CryptoQuant/BTC/Fees And Revenue/Bitcoin Fees per Transaction USD (Mean) - Day.csv` (cryptoquant): EXCEPTION ValueError: cannot assemble with duplicate keys
- `CryptoQuant/BTC/Fees And Revenue/Bitcoin Fees per Transaction USD (Median) - Day.csv` (cryptoquant): EXCEPTION ValueError: cannot assemble with duplicate keys
- `CryptoQuant/BTC/Fees And Revenue/Bitcoin Fees to Reward Ratio - Day.csv` (cryptoquant): EXCEPTION ValueError: cannot assemble with duplicate keys
- `CryptoQuant/BTC/Fees And Revenue/Bitcoin Fees USD (Total) - Day.csv` (cryptoquant): EXCEPTION ValueError: cannot assemble with duplicate keys
- `CryptoQuant/BTC/Flow Indicator/Bitcoin Exchange Inflow CDD - All Exchanges - Day.csv` (cryptoquant): EXCEPTION ValueError: cannot assemble with duplicate keys
- `CryptoQuant/BTC/Flow Indicator/Bitcoin Exchange Stablecoins Ratio - All Exchanges - Day.csv` (cryptoquant): EXCEPTION ValueError: cannot assemble with duplicate keys
- `CryptoQuant/BTC/Flow Indicator/Bitcoin Exchange Stablecoins Ratio USD - All Exchanges - Day.csv` (cryptoquant): EXCEPTION ValueError: cannot assemble with duplicate keys
- `CryptoQuant/BTC/Flow Indicator/Bitcoin Exchange Supply Ratio - All Exchanges - Day.csv` (cryptoquant): EXCEPTION ValueError: cannot assemble with duplicate keys
- `CryptoQuant/BTC/Flow Indicator/Bitcoin Exchange Whale Ratio - All Exchanges - Day.csv` (cryptoquant): EXCEPTION ValueError: cannot assemble with duplicate keys
- `CryptoQuant/BTC/Flow Indicator/Bitcoin Fund Flow Ratio - All Exchanges - Day.csv` (cryptoquant): EXCEPTION ValueError: cannot assemble with duplicate keys
- `CryptoQuant/BTC/Flow Indicator/Bitcoin Stablecoin Supply Ratio (SSR) - Day.csv` (cryptoquant): EXCEPTION ValueError: cannot assemble with duplicate keys
- `CryptoQuant/BTC/Fund Data/Bitcoin Coinbase Premium Gap - Day.csv` (cryptoquant): EXCEPTION ValueError: cannot assemble with duplicate keys
- `CryptoQuant/BTC/Fund Data/Bitcoin Coinbase Premium Index - Day.csv` (cryptoquant): EXCEPTION ValueError: cannot assemble with duplicate keys
- `CryptoQuant/BTC/Fund Data/Bitcoin Fund Holdings - All Symbol - Day.csv` (cryptoquant): EXCEPTION ValueError: cannot assemble with duplicate keys
- `CryptoQuant/BTC/Fund Data/Bitcoin Fund Market Premium - All Symbol - Day.csv` (cryptoquant): EXCEPTION ValueError: cannot assemble with duplicate keys
- `CryptoQuant/BTC/Fund Data/Bitcoin Fund Price (USD) - GBTC - Day.csv` (cryptoquant): EXCEPTION ValueError: cannot assemble with duplicate keys
- `CryptoQuant/BTC/Fund Data/Bitcoin Fund Volume - All Symbol - Day.csv` (cryptoquant): EXCEPTION ValueError: cannot assemble with duplicate keys
- `CryptoQuant/BTC/Fund Data/Bitcoin Korea Premium Index - Day.csv` (cryptoquant): EXCEPTION ValueError: cannot assemble with duplicate keys
- `CryptoQuant/BTC/Inter Entity Flows/Bitcoin Exchange to Exchange Flow (Mean) - All Exchanges, Spot Exchanges - Day.csv` (cryptoquant): EXCEPTION ValueError: cannot assemble with duplicate keys
- `CryptoQuant/BTC/Inter Entity Flows/Bitcoin Exchange to Exchange Flow (Total) - All Exchanges, Spot Exchanges - Day.csv` (cryptoquant): EXCEPTION ValueError: cannot assemble with duplicate keys
- `CryptoQuant/BTC/Inter Entity Flows/Bitcoin Exchange to Exchange Transactions - All Exchanges, Spot Exchanges - Day.csv` (cryptoquant): EXCEPTION ValueError: cannot assemble with duplicate keys
- `CryptoQuant/BTC/Inter Entity Flows/Bitcoin Miner to Miner Flow (Mean) - All Miners, 1THash - Day.csv` (cryptoquant): EXCEPTION ValueError: cannot assemble with duplicate keys
- `CryptoQuant/BTC/Inter Entity Flows/Bitcoin Miner to Miner Flow (Total) - All Miners, 1THash - Day.csv` (cryptoquant): EXCEPTION ValueError: cannot assemble with duplicate keys
- `CryptoQuant/BTC/Inter Entity Flows/Bitcoin Miner to Miner Transactions - All Miners, 1THash - Day.csv` (cryptoquant): EXCEPTION ValueError: cannot assemble with duplicate keys
- `CryptoQuant/BTC/Market Data/Bitcoin Average Cap - Day.csv` (cryptoquant): EXCEPTION ValueError: cannot assemble with duplicate keys
- `CryptoQuant/BTC/Market Data/Bitcoin Delta Cap - Day.csv` (cryptoquant): EXCEPTION ValueError: cannot assemble with duplicate keys
- `CryptoQuant/BTC/Market Data/Bitcoin Exchange Supply - Day.csv` (cryptoquant): EXCEPTION ValueError: cannot assemble with duplicate keys
- `CryptoQuant/BTC/Market Data/Bitcoin Geographical Supply Distribution by Entities - Day.csv` (cryptoquant): EXCEPTION ValueError: cannot assemble with duplicate keys
- `CryptoQuant/BTC/Market Data/Bitcoin Market Cap - Day.csv` (cryptoquant): EXCEPTION ValueError: cannot assemble with duplicate keys
- `CryptoQuant/BTC/Market Data/Bitcoin Price & Volume - Spot, All Exchanges, BTC-USD - Day.csv` (cryptoquant): EXCEPTION ValueError: cannot assemble with duplicate keys
- `CryptoQuant/BTC/Market Data/Bitcoin Price & Volume KRW - Spot - Day.csv` (cryptoquant): EXCEPTION ValueError: cannot assemble with duplicate keys
- `CryptoQuant/BTC/Market Data/Bitcoin Realized Cap - Day.csv` (cryptoquant): EXCEPTION ValueError: cannot assemble with duplicate keys
- `CryptoQuant/BTC/Market Data/Bitcoin Realized Cap - UTXO Age Bands (%) - Day.csv` (cryptoquant): EXCEPTION ValueError: cannot assemble with duplicate keys
- `CryptoQuant/BTC/Market Data/Bitcoin Realized Cap - UTXO Age Bands USD - Day.csv` (cryptoquant): EXCEPTION ValueError: cannot assemble with duplicate keys
- `CryptoQuant/BTC/Market Data/Bitcoin Realized Cap - UTXO Value Bands (%) - Day.csv` (cryptoquant): EXCEPTION ValueError: cannot assemble with duplicate keys
- `CryptoQuant/BTC/Market Data/Bitcoin Realized Cap - UTXO Value Bands USD - Day.csv` (cryptoquant): EXCEPTION ValueError: cannot assemble with duplicate keys
- `CryptoQuant/BTC/Market Data/Bitcoin Taker Buy Ratio - All Exchanges - Day.csv` (cryptoquant): EXCEPTION ValueError: cannot assemble with duplicate keys
- `CryptoQuant/BTC/Market Data/Bitcoin Taker Buy Sell Ratio - All Exchanges - Day.csv` (cryptoquant): EXCEPTION ValueError: cannot assemble with duplicate keys
- `CryptoQuant/BTC/Market Data/Bitcoin Taker Buy Volume - All Exchanges - Day.csv` (cryptoquant): EXCEPTION ValueError: cannot assemble with duplicate keys
- `CryptoQuant/BTC/Market Data/Bitcoin Taker Sell Ratio - All Exchanges - Day.csv` (cryptoquant): EXCEPTION ValueError: cannot assemble with duplicate keys
- `CryptoQuant/BTC/Market Data/Bitcoin Taker Sell Volume - All Exchanges - Day.csv` (cryptoquant): EXCEPTION ValueError: cannot assemble with duplicate keys
- `CryptoQuant/BTC/Market Data/Bitcoin Thermo Cap - Day.csv` (cryptoquant): EXCEPTION ValueError: cannot assemble with duplicate keys
- `CryptoQuant/BTC/Market Data/Bitcoin Trading Volume (KYC VS. Non-KYC) - Day.csv` (cryptoquant): EXCEPTION ValueError: cannot assemble with duplicate keys
- `CryptoQuant/BTC/Market Data/Bitcoin Trading Volume (Spot VS. Derivative) - Day.csv` (cryptoquant): EXCEPTION ValueError: cannot assemble with duplicate keys
- `CryptoQuant/BTC/Market Indicator/Bitcoin Adjusted SOPR (aSOPR) - Day.csv` (cryptoquant): EXCEPTION ValueError: cannot assemble with duplicate keys
- `CryptoQuant/BTC/Market Indicator/Bitcoin Average Dormancy - Day.csv` (cryptoquant): EXCEPTION ValueError: cannot assemble with duplicate keys
- `CryptoQuant/BTC/Market Indicator/Bitcoin Average Supply-Adjusted CDD - Day.csv` (cryptoquant): EXCEPTION ValueError: cannot assemble with duplicate keys
- `CryptoQuant/BTC/Market Indicator/Bitcoin Binary CDD - Day.csv` (cryptoquant): EXCEPTION ValueError: cannot assemble with duplicate keys
- `CryptoQuant/BTC/Market Indicator/Bitcoin Long Term Holder SOPR - Day.csv` (cryptoquant): EXCEPTION ValueError: cannot assemble with duplicate keys
- `CryptoQuant/BTC/Market Indicator/Bitcoin Mean Coin Age - Day.csv` (cryptoquant): EXCEPTION ValueError: cannot assemble with duplicate keys
- `CryptoQuant/BTC/Market Indicator/Bitcoin Mean Coin Dollar Age - Day.csv` (cryptoquant): EXCEPTION ValueError: cannot assemble with duplicate keys
- `CryptoQuant/BTC/Market Indicator/Bitcoin MVRV Ratio - Day.csv` (cryptoquant): EXCEPTION ValueError: cannot assemble with duplicate keys
- `CryptoQuant/BTC/Market Indicator/Bitcoin Net Unrealized Loss (NUL) - Day.csv` (cryptoquant): EXCEPTION ValueError: cannot assemble with duplicate keys
- `CryptoQuant/BTC/Market Indicator/Bitcoin Net Unrealized Profit (NUP) - Day.csv` (cryptoquant): EXCEPTION ValueError: cannot assemble with duplicate keys
- `CryptoQuant/BTC/Market Indicator/Bitcoin Net Unrealized Profit_Loss (NUPL) - Day.csv` (cryptoquant): EXCEPTION ValueError: cannot assemble with duplicate keys
- `CryptoQuant/BTC/Market Indicator/Bitcoin NVM Ratio - Day.csv` (cryptoquant): EXCEPTION ValueError: cannot assemble with duplicate keys
- `CryptoQuant/BTC/Market Indicator/Bitcoin NVT Golden Cross - Day.csv` (cryptoquant): EXCEPTION ValueError: cannot assemble with duplicate keys
- `CryptoQuant/BTC/Market Indicator/Bitcoin NVT Ratio - Day.csv` (cryptoquant): EXCEPTION ValueError: cannot assemble with duplicate keys
- `CryptoQuant/BTC/Market Indicator/Bitcoin Puell Multiple - Day.csv` (cryptoquant): EXCEPTION ValueError: cannot assemble with duplicate keys
- `CryptoQuant/BTC/Market Indicator/Bitcoin Realized Price - Day.csv` (cryptoquant): EXCEPTION ValueError: cannot assemble with duplicate keys
- `CryptoQuant/BTC/Market Indicator/Bitcoin Realized Price - UTXO Age Bands - Day.csv` (cryptoquant): EXCEPTION ValueError: cannot assemble with duplicate keys
- `CryptoQuant/BTC/Market Indicator/Bitcoin Short Term Holder SOPR - Day.csv` (cryptoquant): EXCEPTION ValueError: cannot assemble with duplicate keys
- `CryptoQuant/BTC/Market Indicator/Bitcoin SOPR Ratio (LTH-SOPR_STH-SOPR) - Day.csv` (cryptoquant): EXCEPTION ValueError: cannot assemble with duplicate keys
- `CryptoQuant/BTC/Market Indicator/Bitcoin Spent Output Age Bands (%) - Day.csv` (cryptoquant): EXCEPTION ValueError: cannot assemble with duplicate keys
- `CryptoQuant/BTC/Market Indicator/Bitcoin Spent Output Age Bands - Day.csv` (cryptoquant): EXCEPTION ValueError: cannot assemble with duplicate keys
- `CryptoQuant/BTC/Market Indicator/Bitcoin Spent Output Age Bands USD - Day.csv` (cryptoquant): EXCEPTION ValueError: cannot assemble with duplicate keys
- `CryptoQuant/BTC/Market Indicator/Bitcoin Spent Output Profit Ratio (SOPR) - Day.csv` (cryptoquant): EXCEPTION ValueError: cannot assemble with duplicate keys
- `CryptoQuant/BTC/Market Indicator/Bitcoin Spent Output Value Bands (%) - Day.csv` (cryptoquant): EXCEPTION ValueError: cannot assemble with duplicate keys
- `CryptoQuant/BTC/Market Indicator/Bitcoin Spent Output Value Bands - Day.csv` (cryptoquant): EXCEPTION ValueError: cannot assemble with duplicate keys
- `CryptoQuant/BTC/Market Indicator/Bitcoin Spent Output Value Bands USD - Day.csv` (cryptoquant): EXCEPTION ValueError: cannot assemble with duplicate keys
- `CryptoQuant/BTC/Market Indicator/Bitcoin Stock-to-Flow Ratio - Day.csv` (cryptoquant): EXCEPTION ValueError: cannot assemble with duplicate keys
- `CryptoQuant/BTC/Market Indicator/Bitcoin Stock-to-Flow Reversion - Day.csv` (cryptoquant): EXCEPTION ValueError: cannot assemble with duplicate keys
- `CryptoQuant/BTC/Market Indicator/Bitcoin Sum Coin Age - Day.csv` (cryptoquant): EXCEPTION ValueError: cannot assemble with duplicate keys
- `CryptoQuant/BTC/Market Indicator/Bitcoin Sum Coin Age Distribution (%) - Day.csv` (cryptoquant): EXCEPTION ValueError: cannot assemble with duplicate keys
- `CryptoQuant/BTC/Market Indicator/Bitcoin Sum Coin Age Distribution - Day.csv` (cryptoquant): EXCEPTION ValueError: cannot assemble with duplicate keys
- `CryptoQuant/BTC/Market Indicator/Bitcoin Sum Coin Dollar Age - Day.csv` (cryptoquant): EXCEPTION ValueError: cannot assemble with duplicate keys
- `CryptoQuant/BTC/Market Indicator/Bitcoin Supply Adjusted Dormancy - Day.csv` (cryptoquant): EXCEPTION ValueError: cannot assemble with duplicate keys
- `CryptoQuant/BTC/Market Indicator/Bitcoin Supply in Loss (%) - Day.csv` (cryptoquant): EXCEPTION ValueError: cannot assemble with duplicate keys
- `CryptoQuant/BTC/Market Indicator/Bitcoin Supply in Loss - Day.csv` (cryptoquant): EXCEPTION ValueError: cannot assemble with duplicate keys
- `CryptoQuant/BTC/Market Indicator/Bitcoin Supply in Profit (%) - Day.csv` (cryptoquant): EXCEPTION ValueError: cannot assemble with duplicate keys
- `CryptoQuant/BTC/Market Indicator/Bitcoin Supply in Profit - Day.csv` (cryptoquant): EXCEPTION ValueError: cannot assemble with duplicate keys
- `CryptoQuant/BTC/Market Indicator/Bitcoin Supply-Adjusted CDD - Day.csv` (cryptoquant): EXCEPTION ValueError: cannot assemble with duplicate keys
- `CryptoQuant/BTC/Miner Flows/Bitcoin Exchange to Miner Flow (Mean) - All Exchanges, All Miners - Day.csv` (cryptoquant): EXCEPTION ValueError: cannot assemble with duplicate keys
- `CryptoQuant/BTC/Miner Flows/Bitcoin Exchange to Miner Flow (Total) - All Exchanges, All Miners - Day.csv` (cryptoquant): EXCEPTION ValueError: cannot assemble with duplicate keys
- `CryptoQuant/BTC/Miner Flows/Bitcoin Exchange to Miner Transactions - All Exchanges, All Miners - Day.csv` (cryptoquant): EXCEPTION ValueError: cannot assemble with duplicate keys
- `CryptoQuant/BTC/Miner Flows/Bitcoin Miner Depositing Addresses - All Miners - Day.csv` (cryptoquant): EXCEPTION ValueError: cannot assemble with duplicate keys
- `CryptoQuant/BTC/Miner Flows/Bitcoin Miner Depositing Transactions - All Miners - Day.csv` (cryptoquant): EXCEPTION ValueError: cannot assemble with duplicate keys
- `CryptoQuant/BTC/Miner Flows/Bitcoin Miner In-House Flow (Mean) - All Miners - Day.csv` (cryptoquant): EXCEPTION ValueError: cannot assemble with duplicate keys
- `CryptoQuant/BTC/Miner Flows/Bitcoin Miner In-House Flow (Total) - All Miners - Day.csv` (cryptoquant): EXCEPTION ValueError: cannot assemble with duplicate keys
- `CryptoQuant/BTC/Miner Flows/Bitcoin Miner In-House Transactions - All Miners - Day.csv` (cryptoquant): EXCEPTION ValueError: cannot assemble with duplicate keys
- `CryptoQuant/BTC/Miner Flows/Bitcoin Miner Inflow (Mean) - All Miners - Day.csv` (cryptoquant): EXCEPTION ValueError: cannot assemble with duplicate keys
- `CryptoQuant/BTC/Miner Flows/Bitcoin Miner Inflow (Top10) - All Miners - Day.csv` (cryptoquant): EXCEPTION ValueError: cannot assemble with duplicate keys
- `CryptoQuant/BTC/Miner Flows/Bitcoin Miner Inflow (Total) - All Miners - Day.csv` (cryptoquant): EXCEPTION ValueError: cannot assemble with duplicate keys
- `CryptoQuant/BTC/Miner Flows/Bitcoin Miner Netflow Total - All Miners - Day.csv` (cryptoquant): EXCEPTION ValueError: cannot assemble with duplicate keys
- `CryptoQuant/BTC/Miner Flows/Bitcoin Miner Outflow (Mean) - All Miners - Day.csv` (cryptoquant): EXCEPTION ValueError: cannot assemble with duplicate keys
- `CryptoQuant/BTC/Miner Flows/Bitcoin Miner Outflow (Top10) - All Miners - Day.csv` (cryptoquant): EXCEPTION ValueError: cannot assemble with duplicate keys
- `CryptoQuant/BTC/Miner Flows/Bitcoin Miner Outflow (Total) - All Miners - Day.csv` (cryptoquant): EXCEPTION ValueError: cannot assemble with duplicate keys
- `CryptoQuant/BTC/Miner Flows/Bitcoin Miner Reserve - All Miners - Day.csv` (cryptoquant): EXCEPTION ValueError: cannot assemble with duplicate keys
- `CryptoQuant/BTC/Miner Flows/Bitcoin Miner Reserve USD - All Miners - Day.csv` (cryptoquant): EXCEPTION ValueError: cannot assemble with duplicate keys
- `CryptoQuant/BTC/Miner Flows/Bitcoin Miner Supply Ratio - All Miners - Day.csv` (cryptoquant): EXCEPTION ValueError: cannot assemble with duplicate keys
- `CryptoQuant/BTC/Miner Flows/Bitcoin Miner to Exchange Flow (Mean) - All Miners, All Exchanges - Day.csv` (cryptoquant): EXCEPTION ValueError: cannot assemble with duplicate keys
- `CryptoQuant/BTC/Miner Flows/Bitcoin Miner to Exchange Flow (Total) - All Miners, All Exchanges - Day.csv` (cryptoquant): EXCEPTION ValueError: cannot assemble with duplicate keys
- `CryptoQuant/BTC/Miner Flows/Bitcoin Miner to Exchange Transactions - All Miners, All Exchanges - Day.csv` (cryptoquant): EXCEPTION ValueError: cannot assemble with duplicate keys
- `CryptoQuant/BTC/Miner Flows/Bitcoin Miner Withdrawing Addresses - All Miners - Day.csv` (cryptoquant): EXCEPTION ValueError: cannot assemble with duplicate keys
- `CryptoQuant/BTC/Miner Flows/Bitcoin Miner Withdrawing Transactions - All Miners - Day.csv` (cryptoquant): EXCEPTION ValueError: cannot assemble with duplicate keys
- `CryptoQuant/BTC/Miner Flows/Bitcoin Miners' Position Index (MPI) - Day.csv` (cryptoquant): EXCEPTION ValueError: cannot assemble with duplicate keys
- `CryptoQuant/BTC/Network Indicator/Bitcoin Coin Days Destroyed (CDD) - Day.csv` (cryptoquant): EXCEPTION ValueError: cannot assemble with duplicate keys
- `CryptoQuant/BTC/Network Indicator/Bitcoin UTXO Age Bands (%) - Day.csv` (cryptoquant): EXCEPTION ValueError: cannot assemble with duplicate keys
- `CryptoQuant/BTC/Network Indicator/Bitcoin UTXO Age Bands - Day.csv` (cryptoquant): EXCEPTION ValueError: cannot assemble with duplicate keys
- `CryptoQuant/BTC/Network Indicator/Bitcoin UTXO Age Bands USD - Day.csv` (cryptoquant): EXCEPTION ValueError: cannot assemble with duplicate keys
- `CryptoQuant/BTC/Network Indicator/Bitcoin UTXO Count - Age Bands (%) - Day.csv` (cryptoquant): EXCEPTION ValueError: cannot assemble with duplicate keys
- `CryptoQuant/BTC/Network Indicator/Bitcoin UTXO Count - Age Bands - Day.csv` (cryptoquant): EXCEPTION ValueError: cannot assemble with duplicate keys
- `CryptoQuant/BTC/Network Indicator/Bitcoin UTXO Count - Value Bands (%) - Day.csv` (cryptoquant): EXCEPTION ValueError: cannot assemble with duplicate keys
- `CryptoQuant/BTC/Network Indicator/Bitcoin UTXO Count - Value Bands - Day.csv` (cryptoquant): EXCEPTION ValueError: cannot assemble with duplicate keys
- `CryptoQuant/BTC/Network Indicator/Bitcoin UTXO Value Bands (%) - Day.csv` (cryptoquant): EXCEPTION ValueError: cannot assemble with duplicate keys
- `CryptoQuant/BTC/Network Indicator/Bitcoin UTXO Value Bands - Day.csv` (cryptoquant): EXCEPTION ValueError: cannot assemble with duplicate keys
- `CryptoQuant/BTC/Network Indicator/Bitcoin UTXOs in Loss (%) - Day.csv` (cryptoquant): EXCEPTION ValueError: cannot assemble with duplicate keys
- `CryptoQuant/BTC/Network Indicator/Bitcoin UTXOs in Loss - Day.csv` (cryptoquant): EXCEPTION ValueError: cannot assemble with duplicate keys
- `CryptoQuant/BTC/Network Indicator/Bitcoin UTXOs in Profit (%) - Day.csv` (cryptoquant): EXCEPTION ValueError: cannot assemble with duplicate keys
- `CryptoQuant/BTC/Network Indicator/Bitcoin UTXOs in Profit - Day.csv` (cryptoquant): EXCEPTION ValueError: cannot assemble with duplicate keys
- `CryptoQuant/BTC/Network Stats/Bitcoin Block Interval (Mean) - Day.csv` (cryptoquant): EXCEPTION ValueError: cannot assemble with duplicate keys
- `CryptoQuant/BTC/Network Stats/Bitcoin Block Size (Mean) - Day.csv` (cryptoquant): EXCEPTION ValueError: cannot assemble with duplicate keys
- `CryptoQuant/BTC/Network Stats/Bitcoin Blocks Mined - Day.csv` (cryptoquant): EXCEPTION ValueError: cannot assemble with duplicate keys
- `CryptoQuant/BTC/Network Stats/Bitcoin Difficulty - Day.csv` (cryptoquant): EXCEPTION ValueError: cannot assemble with duplicate keys
- `CryptoQuant/BTC/Network Stats/Bitcoin Hashrate - Day.csv` (cryptoquant): EXCEPTION ValueError: cannot assemble with duplicate keys
- `CryptoQuant/BTC/Network Stats/Bitcoin UTXO Count - Day.csv` (cryptoquant): EXCEPTION ValueError: cannot assemble with duplicate keys
- `CryptoQuant/BTC/Network Stats/Bitcoin Velocity - Day.csv` (cryptoquant): EXCEPTION ValueError: cannot assemble with duplicate keys
- `CryptoQuant/BTC/Supply/Bitcoin New Supply - Day.csv` (cryptoquant): EXCEPTION ValueError: cannot assemble with duplicate keys
- `CryptoQuant/BTC/Supply/Bitcoin Total Supply - Day.csv` (cryptoquant): EXCEPTION ValueError: cannot assemble with duplicate keys
- `CryptoQuant/BTC/Transactions/Bitcoin Tokens Transferred (Mean) - Day.csv` (cryptoquant): EXCEPTION ValueError: cannot assemble with duplicate keys
- `CryptoQuant/BTC/Transactions/Bitcoin Tokens Transferred (Median) - Day.csv` (cryptoquant): EXCEPTION ValueError: cannot assemble with duplicate keys
- `CryptoQuant/BTC/Transactions/Bitcoin Tokens Transferred (Total) - Day.csv` (cryptoquant): EXCEPTION ValueError: cannot assemble with duplicate keys
- `CryptoQuant/BTC/Transactions/Bitcoin Transaction Count (Mean) - Day.csv` (cryptoquant): EXCEPTION ValueError: cannot assemble with duplicate keys
- `CryptoQuant/BTC/Transactions/Bitcoin Transaction Count (Total) - Day.csv` (cryptoquant): EXCEPTION ValueError: cannot assemble with duplicate keys
- `CryptoQuant/ETH/Addresses/Ethereum Active Addresses - Day.csv` (cryptoquant): EXCEPTION ValueError: cannot assemble with duplicate keys
- `CryptoQuant/ETH/Addresses/Ethereum Active Addresses - Internal, External, EOA - Day.csv` (cryptoquant): EXCEPTION ValueError: cannot assemble with duplicate keys
- `CryptoQuant/ETH/Addresses/Ethereum Active Receiving Addresses - Day.csv` (cryptoquant): EXCEPTION ValueError: cannot assemble with duplicate keys
- `CryptoQuant/ETH/Addresses/Ethereum Active Receiving Addresses - Internal, External, EOA - Day.csv` (cryptoquant): EXCEPTION ValueError: cannot assemble with duplicate keys
- `CryptoQuant/ETH/Addresses/Ethereum Active Sending Addresses - Day.csv` (cryptoquant): EXCEPTION ValueError: cannot assemble with duplicate keys
- `CryptoQuant/ETH/Addresses/Ethereum Active Sending Addresses - Internal, External, EOA - Day.csv` (cryptoquant): EXCEPTION ValueError: cannot assemble with duplicate keys
- `CryptoQuant/ETH/Derivatives/Ethereum Estimated Leverage Ratio - All Exchanges - Day.csv` (cryptoquant): EXCEPTION ValueError: cannot assemble with duplicate keys
- `CryptoQuant/ETH/Derivatives/Ethereum Funding Rates - All Exchanges - Day.csv` (cryptoquant): EXCEPTION ValueError: cannot assemble with duplicate keys
- `CryptoQuant/ETH/Derivatives/Ethereum Long Liquidations - All Exchanges, All Symbol - Day.csv` (cryptoquant): EXCEPTION ValueError: cannot assemble with duplicate keys
- `CryptoQuant/ETH/Derivatives/Ethereum Long Liquidations USD - All Exchanges, All Symbol - Day.csv` (cryptoquant): EXCEPTION ValueError: cannot assemble with duplicate keys
- `CryptoQuant/ETH/Derivatives/Ethereum Open Interest - All Exchanges, All Symbol - Day.csv` (cryptoquant): EXCEPTION ValueError: cannot assemble with duplicate keys
- `CryptoQuant/ETH/Derivatives/Ethereum Short Liquidations - All Exchanges, All Symbol - Day.csv` (cryptoquant): EXCEPTION ValueError: cannot assemble with duplicate keys
- `CryptoQuant/ETH/Derivatives/Ethereum Short Liquidations USD - All Exchanges, All Symbol - Day.csv` (cryptoquant): EXCEPTION ValueError: cannot assemble with duplicate keys
- `CryptoQuant/ETH/ETH 2.0/Ethereum Cumulative TXs to ETH 2.0 Contract - Day.csv` (cryptoquant): EXCEPTION ValueError: cannot assemble with duplicate keys
- `CryptoQuant/ETH/ETH 2.0/Ethereum ETH 2.0 Staking Rate (%) - Day.csv` (cryptoquant): EXCEPTION ValueError: cannot assemble with duplicate keys
- `CryptoQuant/ETH/ETH 2.0/Ethereum New Depositors - Day.csv` (cryptoquant): EXCEPTION ValueError: cannot assemble with duplicate keys
- `CryptoQuant/ETH/ETH 2.0/Ethereum Number of ETH 2.0 Deposits - Day.csv` (cryptoquant): EXCEPTION ValueError: cannot assemble with duplicate keys
- `CryptoQuant/ETH/ETH 2.0/Ethereum Number of Unique Depositors - Day.csv` (cryptoquant): EXCEPTION ValueError: cannot assemble with duplicate keys
- `CryptoQuant/ETH/ETH 2.0/Ethereum Phase 0 Success Rate (%) - Day.csv` (cryptoquant): EXCEPTION ValueError: cannot assemble with duplicate keys
- `CryptoQuant/ETH/ETH 2.0/Ethereum Staking Inflow Total - Day.csv` (cryptoquant): EXCEPTION ValueError: cannot assemble with duplicate keys
- `CryptoQuant/ETH/ETH 2.0/Ethereum Total Value Staked - Day.csv` (cryptoquant): EXCEPTION ValueError: cannot assemble with duplicate keys
- `CryptoQuant/ETH/Exchange Flows/Ethereum Exchange Depositing Addresses - All Exchanges - Day.csv` (cryptoquant): EXCEPTION ValueError: cannot assemble with duplicate keys
- `CryptoQuant/ETH/Exchange Flows/Ethereum Exchange Depositing Transactions - All Exchanges - Day.csv` (cryptoquant): EXCEPTION ValueError: cannot assemble with duplicate keys
- `CryptoQuant/ETH/Exchange Flows/Ethereum Exchange Inflow (Mean) - All Exchanges - Day.csv` (cryptoquant): EXCEPTION ValueError: cannot assemble with duplicate keys
- `CryptoQuant/ETH/Exchange Flows/Ethereum Exchange Inflow (Top10) - All Exchanges - Day.csv` (cryptoquant): EXCEPTION ValueError: cannot assemble with duplicate keys
- `CryptoQuant/ETH/Exchange Flows/Ethereum Exchange Inflow (Total) - All Exchanges - Day.csv` (cryptoquant): EXCEPTION ValueError: cannot assemble with duplicate keys
- `CryptoQuant/ETH/Exchange Flows/Ethereum Exchange Netflow (Total) - All Exchanges - Day.csv` (cryptoquant): EXCEPTION ValueError: cannot assemble with duplicate keys
- `CryptoQuant/ETH/Exchange Flows/Ethereum Exchange Outflow (Mean) - All Exchanges - Day.csv` (cryptoquant): EXCEPTION ValueError: cannot assemble with duplicate keys
- `CryptoQuant/ETH/Exchange Flows/Ethereum Exchange Outflow (Top10) - All Exchanges - Day.csv` (cryptoquant): EXCEPTION ValueError: cannot assemble with duplicate keys
- `CryptoQuant/ETH/Exchange Flows/Ethereum Exchange Outflow (Total) - All Exchanges - Day.csv` (cryptoquant): EXCEPTION ValueError: cannot assemble with duplicate keys
- `CryptoQuant/ETH/Exchange Flows/Ethereum Exchange Reserve - All Exchanges - Day.csv` (cryptoquant): EXCEPTION ValueError: cannot assemble with duplicate keys
- `CryptoQuant/ETH/Exchange Flows/Ethereum Exchange Reserve USD - All Exchanges - Day.csv` (cryptoquant): EXCEPTION ValueError: cannot assemble with duplicate keys
- `CryptoQuant/ETH/Exchange Flows/Ethereum Exchange Withdrawing Addresses - All Exchanges - Day.csv` (cryptoquant): EXCEPTION ValueError: cannot assemble with duplicate keys
- `CryptoQuant/ETH/Exchange Flows/Ethereum Exchange Withdrawing Transactions - All Exchanges - Day.csv` (cryptoquant): EXCEPTION ValueError: cannot assemble with duplicate keys
- `CryptoQuant/ETH/Fees And Revenue/Ethereum Fees (Total) - Day.csv` (cryptoquant): EXCEPTION ValueError: cannot assemble with duplicate keys
- `CryptoQuant/ETH/Fees And Revenue/Ethereum Fees Burnt (Total) - Day.csv` (cryptoquant): EXCEPTION ValueError: cannot assemble with duplicate keys
- `CryptoQuant/ETH/Fees And Revenue/Ethereum Fees Burnt per Transaction (Mean) - Day.csv` (cryptoquant): EXCEPTION ValueError: cannot assemble with duplicate keys
- `CryptoQuant/ETH/Fees And Revenue/Ethereum Fees Burnt per Transaction (Median) - Day.csv` (cryptoquant): EXCEPTION ValueError: cannot assemble with duplicate keys
- `CryptoQuant/ETH/Fees And Revenue/Ethereum Fees Burnt per Transaction USD (Mean) - Day.csv` (cryptoquant): EXCEPTION ValueError: cannot assemble with duplicate keys
- `CryptoQuant/ETH/Fees And Revenue/Ethereum Fees Burnt per Transaction USD (Median) - Day.csv` (cryptoquant): EXCEPTION ValueError: cannot assemble with duplicate keys
- `CryptoQuant/ETH/Fees And Revenue/Ethereum Fees Burnt USD (Total) - Day.csv` (cryptoquant): EXCEPTION ValueError: cannot assemble with duplicate keys
- `CryptoQuant/ETH/Fees And Revenue/Ethereum Fees per Transaction (Mean) - Day.csv` (cryptoquant): EXCEPTION ValueError: cannot assemble with duplicate keys
- `CryptoQuant/ETH/Fees And Revenue/Ethereum Fees per Transaction USD (Mean) - Day.csv` (cryptoquant): EXCEPTION ValueError: cannot assemble with duplicate keys
- `CryptoQuant/ETH/Flow Indicator/Ethereum Exchange Supply Ratio - All Exchanges - Day.csv` (cryptoquant): EXCEPTION ValueError: cannot assemble with duplicate keys
- `CryptoQuant/ETH/Fund Data/Ethereum Coinbase Premium Gap - Day.csv` (cryptoquant): EXCEPTION ValueError: cannot assemble with duplicate keys
- `CryptoQuant/ETH/Fund Data/Ethereum Coinbase Premium Index - Day.csv` (cryptoquant): EXCEPTION ValueError: cannot assemble with duplicate keys
- `CryptoQuant/ETH/Fund Data/Ethereum Fund Holdings - All Symbol - Day.csv` (cryptoquant): EXCEPTION ValueError: cannot assemble with duplicate keys
- `CryptoQuant/ETH/Fund Data/Ethereum Fund Market Premium - All Symbol - Day.csv` (cryptoquant): EXCEPTION ValueError: cannot assemble with duplicate keys
- `CryptoQuant/ETH/Fund Data/Ethereum Fund Price (USD) - ETHE - Day.csv` (cryptoquant): EXCEPTION ValueError: cannot assemble with duplicate keys
- `CryptoQuant/ETH/Fund Data/Ethereum Fund Volume - All Symbol - Day.csv` (cryptoquant): EXCEPTION ValueError: cannot assemble with duplicate keys
- `CryptoQuant/ETH/Fund Data/Ethereum Korea Premium Index - Day.csv` (cryptoquant): EXCEPTION ValueError: cannot assemble with duplicate keys
- `CryptoQuant/ETH/Market Data/Ethereum Market Cap - Day.csv` (cryptoquant): EXCEPTION ValueError: cannot assemble with duplicate keys
- `CryptoQuant/ETH/Market Data/Ethereum Price & Volume - Spot, All Exchanges, ETH-USD - Day.csv` (cryptoquant): EXCEPTION ValueError: cannot assemble with duplicate keys
- `CryptoQuant/ETH/Market Data/Ethereum Price & Volume KRW - Spot - Day.csv` (cryptoquant): EXCEPTION ValueError: cannot assemble with duplicate keys
- `CryptoQuant/ETH/Market Data/Ethereum Taker Buy Ratio - All Exchanges - Day.csv` (cryptoquant): EXCEPTION ValueError: cannot assemble with duplicate keys
- `CryptoQuant/ETH/Market Data/Ethereum Taker Buy Sell Ratio - All Exchanges - Day.csv` (cryptoquant): EXCEPTION ValueError: cannot assemble with duplicate keys
- `CryptoQuant/ETH/Market Data/Ethereum Taker Buy Volume - All Exchanges - Day.csv` (cryptoquant): EXCEPTION ValueError: cannot assemble with duplicate keys
- `CryptoQuant/ETH/Market Data/Ethereum Taker Sell Ratio - All Exchanges - Day.csv` (cryptoquant): EXCEPTION ValueError: cannot assemble with duplicate keys
- `CryptoQuant/ETH/Market Data/Ethereum Taker Sell Volume - All Exchanges - Day.csv` (cryptoquant): EXCEPTION ValueError: cannot assemble with duplicate keys
- `CryptoQuant/ETH/Network Stats/Ethereum Destroyed Contracts - Day.csv` (cryptoquant): EXCEPTION ValueError: cannot assemble with duplicate keys
- `CryptoQuant/ETH/Network Stats/Ethereum New Contracts - Day.csv` (cryptoquant): EXCEPTION ValueError: cannot assemble with duplicate keys
- `CryptoQuant/ETH/Network Stats/Ethereum Number of Contracts - Day.csv` (cryptoquant): EXCEPTION ValueError: cannot assemble with duplicate keys
- `CryptoQuant/ETH/Transactions/Ethereum Contract Calls (Mean) - Day.csv` (cryptoquant): EXCEPTION ValueError: cannot assemble with duplicate keys
- `CryptoQuant/ETH/Transactions/Ethereum Contract Calls (Total) - Day.csv` (cryptoquant): EXCEPTION ValueError: cannot assemble with duplicate keys
- `CryptoQuant/ETH/Transactions/Ethereum External Contract Calls (Mean) - Day.csv` (cryptoquant): EXCEPTION ValueError: cannot assemble with duplicate keys
- `CryptoQuant/ETH/Transactions/Ethereum External Contract Calls (Total) - Day.csv` (cryptoquant): EXCEPTION ValueError: cannot assemble with duplicate keys
- `CryptoQuant/ETH/Transactions/Ethereum Tokens Transferred (Mean) - Day.csv` (cryptoquant): EXCEPTION ValueError: cannot assemble with duplicate keys
- `CryptoQuant/ETH/Transactions/Ethereum Tokens Transferred (Median) - Day.csv` (cryptoquant): EXCEPTION ValueError: cannot assemble with duplicate keys
- `CryptoQuant/ETH/Transactions/Ethereum Tokens Transferred (Total) - Day.csv` (cryptoquant): EXCEPTION ValueError: cannot assemble with duplicate keys
- `CryptoQuant/ETH/Transactions/Ethereum Tokens Transferred - Internal, External, EOA (Mean) - Day.csv` (cryptoquant): EXCEPTION ValueError: cannot assemble with duplicate keys
- `CryptoQuant/ETH/Transactions/Ethereum Tokens Transferred - Internal, External, EOA (Median) - Day.csv` (cryptoquant): EXCEPTION ValueError: cannot assemble with duplicate keys
- `CryptoQuant/ETH/Transactions/Ethereum Tokens Transferred - Internal, External, EOA (Total) - Day.csv` (cryptoquant): EXCEPTION ValueError: cannot assemble with duplicate keys
- `CryptoQuant/ETH/Transactions/Ethereum Tokens Transferred Between EOA (Mean) - Day.csv` (cryptoquant): EXCEPTION ValueError: cannot assemble with duplicate keys
- `CryptoQuant/ETH/Transactions/Ethereum Tokens Transferred Between EOA (Total) - Day.csv` (cryptoquant): EXCEPTION ValueError: cannot assemble with duplicate keys
- `CryptoQuant/ETH/Transactions/Ethereum Tokens Transferred Between EOA USD (Mean) - Day.csv` (cryptoquant): EXCEPTION ValueError: cannot assemble with duplicate keys
- `CryptoQuant/ETH/Transactions/Ethereum Tokens Transferred Between EOA USD (Median) - Day.csv` (cryptoquant): EXCEPTION ValueError: cannot assemble with duplicate keys
- `CryptoQuant/ETH/Transactions/Ethereum Tokens Transferred Between EOA USD (Total) - Day.csv` (cryptoquant): EXCEPTION ValueError: cannot assemble with duplicate keys
- `CryptoQuant/ETH/Transactions/Ethereum Tokens Transferred by Contract Calls (Mean) - Day.csv` (cryptoquant): EXCEPTION ValueError: cannot assemble with duplicate keys
- `CryptoQuant/ETH/Transactions/Ethereum Tokens Transferred by Contract Calls (Median) - Day.csv` (cryptoquant): EXCEPTION ValueError: cannot assemble with duplicate keys
- `CryptoQuant/ETH/Transactions/Ethereum Tokens Transferred by Contract Calls (Total) - Day.csv` (cryptoquant): EXCEPTION ValueError: cannot assemble with duplicate keys
- `CryptoQuant/ETH/Transactions/Ethereum Tokens Transferred by Contract Calls USD (Mean) - Day.csv` (cryptoquant): EXCEPTION ValueError: cannot assemble with duplicate keys
- `CryptoQuant/ETH/Transactions/Ethereum Tokens Transferred by Contract Calls USD (Median) - Day.csv` (cryptoquant): EXCEPTION ValueError: cannot assemble with duplicate keys
- `CryptoQuant/ETH/Transactions/Ethereum Tokens Transferred by Contract Calls USD (Total) - Day.csv` (cryptoquant): EXCEPTION ValueError: cannot assemble with duplicate keys
- `CryptoQuant/ETH/Transactions/Ethereum Tokens Transferred by External Contract Calls (Mean) - Day.csv` (cryptoquant): EXCEPTION ValueError: cannot assemble with duplicate keys
- `CryptoQuant/ETH/Transactions/Ethereum Tokens Transferred by External Contract Calls (Median) - Day.csv` (cryptoquant): EXCEPTION ValueError: cannot assemble with duplicate keys
- `CryptoQuant/ETH/Transactions/Ethereum Tokens Transferred by External Contract Calls (Total) - Day.csv` (cryptoquant): EXCEPTION ValueError: cannot assemble with duplicate keys
- `CryptoQuant/ETH/Transactions/Ethereum Tokens Transferred by External Contract Calls USD (Mean) - Day.csv` (cryptoquant): EXCEPTION ValueError: cannot assemble with duplicate keys
- `CryptoQuant/ETH/Transactions/Ethereum Tokens Transferred by External Contract Calls USD (Median) - Day.csv` (cryptoquant): EXCEPTION ValueError: cannot assemble with duplicate keys
- `CryptoQuant/ETH/Transactions/Ethereum Tokens Transferred by External Contract Calls USD (Total) - Day.csv` (cryptoquant): EXCEPTION ValueError: cannot assemble with duplicate keys
- `CryptoQuant/ETH/Transactions/Ethereum Tokens Transferred USD (Mean) - Day.csv` (cryptoquant): EXCEPTION ValueError: cannot assemble with duplicate keys
- `CryptoQuant/ETH/Transactions/Ethereum Tokens Transferred USD (Median) - Day.csv` (cryptoquant): EXCEPTION ValueError: cannot assemble with duplicate keys
- `CryptoQuant/ETH/Transactions/Ethereum Tokens Transferred USD (Total) - Day.csv` (cryptoquant): EXCEPTION ValueError: cannot assemble with duplicate keys
- `CryptoQuant/ETH/Transactions/Ethereum Tokens Transferred USD - Internal, External, EOA (Mean) - Day.csv` (cryptoquant): EXCEPTION ValueError: cannot assemble with duplicate keys
- `CryptoQuant/ETH/Transactions/Ethereum Tokens Transferred USD - Internal, External, EOA (Median) - Day.csv` (cryptoquant): EXCEPTION ValueError: cannot assemble with duplicate keys
- `CryptoQuant/ETH/Transactions/Ethereum Tokens Transferred USD - Internal, External, EOA (Total) - Day.csv` (cryptoquant): EXCEPTION ValueError: cannot assemble with duplicate keys
- `CryptoQuant/ETH/Transactions/Ethereum Transaction Count (Mean) - Day.csv` (cryptoquant): EXCEPTION ValueError: cannot assemble with duplicate keys
- `CryptoQuant/ETH/Transactions/Ethereum Transaction Count (Total) - Day.csv` (cryptoquant): EXCEPTION ValueError: cannot assemble with duplicate keys
- `CryptoQuant/ETH/Transactions/Ethereum Transaction Count - Internal, External, EOA (Total) - Day.csv` (cryptoquant): EXCEPTION ValueError: cannot assemble with duplicate keys
- `CryptoQuant/ETH/Transactions/Ethereum Transactions Between EOA (Mean) - Day.csv` (cryptoquant): EXCEPTION ValueError: cannot assemble with duplicate keys
- `CryptoQuant/ETH/Transactions/Ethereum Transactions Between EOA (Total) - Day.csv` (cryptoquant): EXCEPTION ValueError: cannot assemble with duplicate keys
- `CryptoQuant/ETH/Transactions/Ethereum Transfer Count - Internal, External, EOA (Mean) - Day.csv` (cryptoquant): EXCEPTION ValueError: cannot assemble with duplicate keys
- `CryptoQuant/ETH/Transactions/Ethereum Transfer Count - Internal, External, EOA (Total) - Day.csv` (cryptoquant): EXCEPTION ValueError: cannot assemble with duplicate keys
- `CryptoQuant/ETH/Transactions/Ethereum Transfers Between EOA (Mean) - Day.csv` (cryptoquant): EXCEPTION ValueError: cannot assemble with duplicate keys
- `CryptoQuant/ETH/Transactions/Ethereum Transfers Between EOA (Total) - Day.csv` (cryptoquant): EXCEPTION ValueError: cannot assemble with duplicate keys
- `CryptoQuant/ETH/Transactions/Ethereum Transfers by Contract Calls (Mean) - Day.csv` (cryptoquant): EXCEPTION ValueError: cannot assemble with duplicate keys
- `CryptoQuant/ETH/Transactions/Ethereum Transfers by External Contract Calls (Mean) - Day.csv` (cryptoquant): EXCEPTION ValueError: cannot assemble with duplicate keys
- `CryptoQuant/ETH/Transactions/Ethereum Transfers by External Contract Calls (Total) - Day.csv` (cryptoquant): EXCEPTION ValueError: cannot assemble with duplicate keys
- `CryptoQuant/USDC/Addresses/USD Coin(ERC20) Active Addresses - Day.csv` (cryptoquant): EXCEPTION ValueError: cannot assemble with duplicate keys
- `CryptoQuant/USDC/Addresses/USD Coin(ERC20) Active Receiving Addresses (%) - Day.csv` (cryptoquant): EXCEPTION ValueError: cannot assemble with duplicate keys
- `CryptoQuant/USDC/Addresses/USD Coin(ERC20) Active Receiving Addresses - Day.csv` (cryptoquant): EXCEPTION ValueError: cannot assemble with duplicate keys
- `CryptoQuant/USDC/Addresses/USD Coin(ERC20) Active Sending Addresses (%) - Day.csv` (cryptoquant): EXCEPTION ValueError: cannot assemble with duplicate keys
- `CryptoQuant/USDC/Addresses/USD Coin(ERC20) Active Sending Addresses - Day.csv` (cryptoquant): EXCEPTION ValueError: cannot assemble with duplicate keys
- `CryptoQuant/USDC/Exchange Flows/USD Coin(ERC20) Exchange Depositing Addresses - All Exchanges - Day.csv` (cryptoquant): EXCEPTION ValueError: cannot assemble with duplicate keys
- `CryptoQuant/USDC/Exchange Flows/USD Coin(ERC20) Exchange Depositing Transactions - All Exchanges - Day.csv` (cryptoquant): EXCEPTION ValueError: cannot assemble with duplicate keys
- `CryptoQuant/USDC/Exchange Flows/USD Coin(ERC20) Exchange Inflow (Mean) - All Exchanges - Day.csv` (cryptoquant): EXCEPTION ValueError: cannot assemble with duplicate keys
- `CryptoQuant/USDC/Exchange Flows/USD Coin(ERC20) Exchange Inflow (Top10) - All Exchanges - Day.csv` (cryptoquant): EXCEPTION ValueError: cannot assemble with duplicate keys
- `CryptoQuant/USDC/Exchange Flows/USD Coin(ERC20) Exchange Inflow (Total) - All Exchanges - Day.csv` (cryptoquant): EXCEPTION ValueError: cannot assemble with duplicate keys
- `CryptoQuant/USDC/Exchange Flows/USD Coin(ERC20) Exchange Netflow (Total) - All Exchanges - Day.csv` (cryptoquant): EXCEPTION ValueError: cannot assemble with duplicate keys
- `CryptoQuant/USDC/Exchange Flows/USD Coin(ERC20) Exchange Outflow (Mean) - All Exchanges - Day.csv` (cryptoquant): EXCEPTION ValueError: cannot assemble with duplicate keys
- `CryptoQuant/USDC/Exchange Flows/USD Coin(ERC20) Exchange Outflow (Top10) - All Exchanges - Day.csv` (cryptoquant): EXCEPTION ValueError: cannot assemble with duplicate keys
- `CryptoQuant/USDC/Exchange Flows/USD Coin(ERC20) Exchange Outflow (Total) - All Exchanges - Day.csv` (cryptoquant): EXCEPTION ValueError: cannot assemble with duplicate keys
- `CryptoQuant/USDC/Exchange Flows/USD Coin(ERC20) Exchange Reserve - All Exchanges - Day.csv` (cryptoquant): EXCEPTION ValueError: cannot assemble with duplicate keys
- `CryptoQuant/USDC/Exchange Flows/USD Coin(ERC20) Exchange Withdrawing Addresses - All Exchanges - Day.csv` (cryptoquant): EXCEPTION ValueError: cannot assemble with duplicate keys
- `CryptoQuant/USDC/Exchange Flows/USD Coin(ERC20) Exchange Withdrawing Transactions - All Exchanges - Day.csv` (cryptoquant): EXCEPTION ValueError: cannot assemble with duplicate keys
- `CryptoQuant/USDC/Flow Indicator/USD Coin(ERC20) Exchange Supply Ratio - All Exchanges - Day.csv` (cryptoquant): EXCEPTION ValueError: cannot assemble with duplicate keys
- `CryptoQuant/USDC/Transactions/USD Coin(ERC20) Tokens Transferred (Mean) - Day.csv` (cryptoquant): EXCEPTION ValueError: cannot assemble with duplicate keys
- `CryptoQuant/USDC/Transactions/USD Coin(ERC20) Tokens Transferred (Total) - Day.csv` (cryptoquant): EXCEPTION ValueError: cannot assemble with duplicate keys
- `CryptoQuant/USDC/Transactions/USD Coin(ERC20) Transfer Event Count - Day.csv` (cryptoquant): EXCEPTION ValueError: cannot assemble with duplicate keys
- `CryptoQuant/USDT (TRX)/Addresses/Tether USD(TRC20) Active Addresses - Day.csv` (cryptoquant): EXCEPTION ValueError: cannot assemble with duplicate keys
- `CryptoQuant/USDT (TRX)/Addresses/Tether USD(TRC20) Active Receiving Addresses (%) - Day.csv` (cryptoquant): EXCEPTION ValueError: cannot assemble with duplicate keys
- `CryptoQuant/USDT (TRX)/Addresses/Tether USD(TRC20) Active Receiving Addresses - Day.csv` (cryptoquant): EXCEPTION ValueError: cannot assemble with duplicate keys
- `CryptoQuant/USDT (TRX)/Addresses/Tether USD(TRC20) Active Sending Addresses (%) - Day.csv` (cryptoquant): EXCEPTION ValueError: cannot assemble with duplicate keys
- `CryptoQuant/USDT (TRX)/Addresses/Tether USD(TRC20) Active Sending Addresses - Day.csv` (cryptoquant): EXCEPTION ValueError: cannot assemble with duplicate keys
- `CryptoQuant/USDT (TRX)/Exchange Flows/Tether USD(TRC20) Exchange Depositing Transactions - All Exchanges - Day.csv` (cryptoquant): EXCEPTION ValueError: cannot assemble with duplicate keys
- `CryptoQuant/USDT (TRX)/Exchange Flows/Tether USD(TRC20) Exchange Inflow (Mean) - All Exchanges - Day.csv` (cryptoquant): EXCEPTION ValueError: cannot assemble with duplicate keys
- `CryptoQuant/USDT (TRX)/Exchange Flows/Tether USD(TRC20) Exchange Inflow (Top10) - All Exchanges - Day.csv` (cryptoquant): EXCEPTION ValueError: cannot assemble with duplicate keys
- `CryptoQuant/USDT (TRX)/Exchange Flows/Tether USD(TRC20) Exchange Inflow (Total) - All Exchanges - Day.csv` (cryptoquant): EXCEPTION ValueError: cannot assemble with duplicate keys
- `CryptoQuant/USDT (TRX)/Exchange Flows/Tether USD(TRC20) Exchange Netflow (Total) - All Exchanges - Day.csv` (cryptoquant): EXCEPTION ValueError: cannot assemble with duplicate keys
- `CryptoQuant/USDT (TRX)/Exchange Flows/Tether USD(TRC20) Exchange Outflow (Mean) - All Exchanges - Day.csv` (cryptoquant): EXCEPTION ValueError: cannot assemble with duplicate keys
- `CryptoQuant/USDT (TRX)/Exchange Flows/Tether USD(TRC20) Exchange Outflow (Top10) - All Exchanges - Day.csv` (cryptoquant): EXCEPTION ValueError: cannot assemble with duplicate keys
- `CryptoQuant/USDT (TRX)/Exchange Flows/Tether USD(TRC20) Exchange Reserve - All Exchanges - Day.csv` (cryptoquant): EXCEPTION ValueError: cannot assemble with duplicate keys
- `CryptoQuant/USDT (TRX)/Exchange Flows/Tether USD(TRC20) Exchange Withdrawing Transactions - All Exchanges - Day.csv` (cryptoquant): EXCEPTION ValueError: cannot assemble with duplicate keys
- `CryptoQuant/USDT ETH/Addresses/Tether USD(ERC20) Active Addresses - Day.csv` (cryptoquant): EXCEPTION ValueError: cannot assemble with duplicate keys
- `CryptoQuant/USDT ETH/Addresses/Tether USD(ERC20) Active Receiving Addresses (%) - Day.csv` (cryptoquant): EXCEPTION ValueError: cannot assemble with duplicate keys
- `CryptoQuant/USDT ETH/Addresses/Tether USD(ERC20) Active Receiving Addresses - Day.csv` (cryptoquant): EXCEPTION ValueError: cannot assemble with duplicate keys
- `CryptoQuant/USDT ETH/Addresses/Tether USD(ERC20) Active Sending Addresses (%) - Day.csv` (cryptoquant): EXCEPTION ValueError: cannot assemble with duplicate keys
- `CryptoQuant/USDT ETH/Addresses/Tether USD(ERC20) Active Sending Addresses - Day.csv` (cryptoquant): EXCEPTION ValueError: cannot assemble with duplicate keys
- `CryptoQuant/USDT ETH/Exchange Flows/Tether USD(ERC20) Exchange Depositing Addresses - All Exchanges - Day.csv` (cryptoquant): EXCEPTION ValueError: cannot assemble with duplicate keys
- `CryptoQuant/USDT ETH/Exchange Flows/Tether USD(ERC20) Exchange Depositing Transactions - All Exchanges - Day.csv` (cryptoquant): EXCEPTION ValueError: cannot assemble with duplicate keys
- `CryptoQuant/USDT ETH/Exchange Flows/Tether USD(ERC20) Exchange Inflow (Mean) - All Exchanges - Day.csv` (cryptoquant): EXCEPTION ValueError: cannot assemble with duplicate keys
- `CryptoQuant/USDT ETH/Exchange Flows/Tether USD(ERC20) Exchange Inflow (Top10) - All Exchanges - Day.csv` (cryptoquant): EXCEPTION ValueError: cannot assemble with duplicate keys
- `CryptoQuant/USDT ETH/Exchange Flows/Tether USD(ERC20) Exchange Inflow (Total) - All Exchanges - Day.csv` (cryptoquant): EXCEPTION ValueError: cannot assemble with duplicate keys
- `CryptoQuant/USDT ETH/Exchange Flows/Tether USD(ERC20) Exchange Netflow (Total) - All Exchanges - Day.csv` (cryptoquant): EXCEPTION ValueError: cannot assemble with duplicate keys
- `CryptoQuant/USDT ETH/Exchange Flows/Tether USD(ERC20) Exchange Outflow (Mean) - All Exchanges - Day.csv` (cryptoquant): EXCEPTION ValueError: cannot assemble with duplicate keys
- `CryptoQuant/USDT ETH/Exchange Flows/Tether USD(ERC20) Exchange Outflow (Top10) - All Exchanges - Day.csv` (cryptoquant): EXCEPTION ValueError: cannot assemble with duplicate keys
- `CryptoQuant/USDT ETH/Exchange Flows/Tether USD(ERC20) Exchange Outflow (Total) - All Exchanges - Day.csv` (cryptoquant): EXCEPTION ValueError: cannot assemble with duplicate keys
- `CryptoQuant/USDT ETH/Exchange Flows/Tether USD(ERC20) Exchange Reserve - All Exchanges - Day.csv` (cryptoquant): EXCEPTION ValueError: cannot assemble with duplicate keys
- `CryptoQuant/USDT ETH/Exchange Flows/Tether USD(ERC20) Exchange Withdrawing Addresses - All Exchanges - Day.csv` (cryptoquant): EXCEPTION ValueError: cannot assemble with duplicate keys
- `CryptoQuant/USDT ETH/Exchange Flows/Tether USD(ERC20) Exchange Withdrawing Transactions - All Exchanges - Day.csv` (cryptoquant): EXCEPTION ValueError: cannot assemble with duplicate keys
- `CryptoQuant/USDT ETH/Flow Indicator/Tether USD(ERC20) Exchange Supply Ratio - All Exchanges - Day.csv` (cryptoquant): EXCEPTION ValueError: cannot assemble with duplicate keys
- `CryptoQuant/USDT ETH/Market Data/Tether USD(ERC20) Market Cap - Day.csv` (cryptoquant): EXCEPTION ValueError: cannot assemble with duplicate keys
- `CryptoQuant/USDT ETH/Supply/Tether USD(ERC20) Total Supply - Day.csv` (cryptoquant): EXCEPTION ValueError: cannot assemble with duplicate keys
- `CryptoQuant/USDT ETH/Transactions/Tether USD(ERC20) Tokens Transferred (Total) - Day.csv` (cryptoquant): EXCEPTION ValueError: cannot assemble with duplicate keys
- `CryptoQuant/USDT ETH/Transactions/Tether USD(ERC20) Transfer Event Count - Day.csv` (cryptoquant): EXCEPTION ValueError: cannot assemble with duplicate keys
- `CryptoQuant/WBTC/Addresses/Wrapped BTC Active Addresses - Day.csv` (cryptoquant): EXCEPTION ValueError: cannot assemble with duplicate keys
- `CryptoQuant/WBTC/Addresses/Wrapped BTC Active Receiving Addresses - Day.csv` (cryptoquant): EXCEPTION ValueError: cannot assemble with duplicate keys
- `CryptoQuant/WBTC/Addresses/Wrapped BTC Active Sending Addresses - Day.csv` (cryptoquant): EXCEPTION ValueError: cannot assemble with duplicate keys
- `CryptoQuant/WBTC/Transactions/Wrapped BTC Tokens Transferred (Mean) - Day.csv` (cryptoquant): EXCEPTION ValueError: cannot assemble with duplicate keys
- `CryptoQuant/WBTC/Transactions/Wrapped BTC Tokens Transferred (Median) - Day.csv` (cryptoquant): EXCEPTION ValueError: cannot assemble with duplicate keys
- `CryptoQuant/WBTC/Transactions/Wrapped BTC Tokens Transferred (Total) - Day.csv` (cryptoquant): EXCEPTION ValueError: cannot assemble with duplicate keys
- `CryptoQuant/WBTC/Transactions/Wrapped BTC Transaction Count (Mean) - Day.csv` (cryptoquant): EXCEPTION ValueError: cannot assemble with duplicate keys
- `CryptoQuant/WBTC/Transactions/Wrapped BTC Transaction Count (Total) - Day.csv` (cryptoquant): EXCEPTION ValueError: cannot assemble with duplicate keys
- `CryptoQuant/WBTC/Transactions/Wrapped BTC Transfer Count (Total) - Day.csv` (cryptoquant): EXCEPTION ValueError: cannot assemble with duplicate keys
- `Tradingview/BATS_ETHA_INDEX_ETHUSD, 1D_2f598.csv` (tradingview): no `time` column, skipped
- `Tradingview/BATS_IBIT_INDEX_BTCUSD, 1D_82cbc.csv` (tradingview): no `time` column, skipped
- `Tradingview/CME_DL_BTC1!, 1D_f2832.csv` (tradingview): no `time` column, skipped
- `Tradingview/CME_DL_BTC1!-INDEX_BTCUSD, 1D_bab18.csv` (tradingview): no `time` column, skipped
- `Tradingview/CME_DL_BTC1!_INDEX_BTCUSD, 1D_35ff1.csv` (tradingview): no `time` column, skipped
- `Tradingview/CME_DL_ETH1!, 1D_d7e37.csv` (tradingview): no `time` column, skipped
- `Tradingview/CME_DL_ETH1!-INDEX_ETHUSD, 1D_94468.csv` (tradingview): no `time` column, skipped
- `Tradingview/CME_DL_ETH1!_INDEX_ETHUSD, 1D_26513.csv` (tradingview): no `time` column, skipped
- `Tradingview/CME_DL_MBT1!, 1D_98b41.csv` (tradingview): no `time` column, skipped
- `Tradingview/CME_DL_MET1!, 1D_85ee4.csv` (tradingview): no `time` column, skipped
- `Tradingview/CME_DL_SOL1!, 1D_e1c21.csv` (tradingview): no `time` column, skipped
- `Tradingview/DERIBIT_DVOL, 1D_75dd9.csv` (tradingview): no `time` column, skipped

## Step 04 — normalize dates  _(run 2026-04-17 03:14:41Z)_

Per-source counts:
- **cryptoquant**: 345
- **artemis**: 47
- **farside**: 3
- **defi**: 13
- **defillama**: 6
- **tradingview**: 12
- **skip**: 1
- **snapshot**: 19

## Step 05 — rename TradingView  _(run 2026-04-17 03:15:19Z)_

- `Tradingview/BATS_ETHA_INDEX_ETHUSD, 1D_2f598.csv` -> `Tradingview/tradingview__ETHA_ETF_over_SPOT_ETH__daily.csv`
- `Tradingview/BATS_IBIT_INDEX_BTCUSD, 1D_82cbc.csv` -> `Tradingview/tradingview__IBIT_ETF_over_SPOT_BTC__daily.csv`
- `Tradingview/CME_DL_BTC1!, 1D_f2832.csv` -> `Tradingview/tradingview__CME_BTC_front_month_futures__daily.csv`
- `Tradingview/CME_DL_BTC1!-INDEX_BTCUSD, 1D_bab18.csv` -> `Tradingview/tradingview__CME_BTC_futures_minus_SPOT_BTC_basis__daily.csv`
- `Tradingview/CME_DL_BTC1!_INDEX_BTCUSD, 1D_35ff1.csv` -> `Tradingview/tradingview__CME_BTC_futures_over_SPOT_BTC_ratio__daily.csv`
- `Tradingview/CME_DL_ETH1!, 1D_d7e37.csv` -> `Tradingview/tradingview__CME_ETH_front_month_futures__daily.csv`
- `Tradingview/CME_DL_ETH1!-INDEX_ETHUSD, 1D_94468.csv` -> `Tradingview/tradingview__CME_ETH_futures_minus_SPOT_ETH_basis__daily.csv`
- `Tradingview/CME_DL_ETH1!_INDEX_ETHUSD, 1D_26513.csv` -> `Tradingview/tradingview__CME_ETH_futures_over_SPOT_ETH_ratio__daily.csv`
- `Tradingview/CME_DL_MBT1!, 1D_98b41.csv` -> `Tradingview/tradingview__CME_Micro_Bitcoin_futures__daily.csv`
- `Tradingview/CME_DL_MET1!, 1D_85ee4.csv` -> `Tradingview/tradingview__CME_Micro_Ether_futures__daily.csv`
- `Tradingview/CME_DL_SOL1!, 1D_e1c21.csv` -> `Tradingview/tradingview__CME_Solana_futures__daily.csv`
- `Tradingview/DERIBIT_DVOL, 1D_75dd9.csv` -> `Tradingview/tradingview__Deribit_BTC_volatility_index_DVOL__daily.csv`

## Step 06 — build inventory  _(run 2026-04-17 03:17:34Z)_

Summarized 445 CSV files.
Wrote 48 per-folder README.md files.
Wrote `Data/MASTER_DATA.md`.
Wrote `Data/MASTER_DATA.csv`.

## Step 07 — validation  _(run 2026-04-17 03:19:05Z)_

### Date-standardization check
- date normalization: 426 files OK, 1 failed.
  - `MASTER_DATA.csv`: first column is `source` (expected `date`)

### Merged-file sanity checks
- stablecoin_mcap merge: cols_union_match=True (merged=200, parts_union=200), dup_dates=0, date_range_match=True (2017-11-29 .. 2026-04-17)
- cex_net_inflows merge: cols_union_match=True (merged=75, parts_union=75), dup_dates=0, date_range_match=True (2022-11-12 .. 2026-04-17)

### CryptoQuant spot-checks (5 random files)
- [PASS] `CryptoQuant/USDT ETH/Exchange Flows/Tether USD(ERC20) Exchange Outflow (Total) - All Exchanges - Day.csv`: rows 3027 -> 3027, values preserved=True, ascending=True
- [PASS] `CryptoQuant/BTC/Inter Entity Flows/Bitcoin Miner to Miner Flow (Mean) - All Miners, 1THash - Day.csv`: rows 1903 -> 1903, values preserved=True, ascending=True
- [PASS] `CryptoQuant/BTC/Exchange Flows/Bitcoin Exchange Depositing Transactions - All Exchanges - Day.csv`: rows 6310 -> 6310, values preserved=True, ascending=True
- [PASS] `CryptoQuant/BTC/Miner Flows/Bitcoin Miner Withdrawing Addresses - All Miners - Day.csv`: rows 6302 -> 6302, values preserved=True, ascending=True
- [PASS] `CryptoQuant/BTC/Miner Flows/Bitcoin Miner In-House Flow (Total) - All Miners - Day.csv`: rows 6299 -> 6299, values preserved=True, ascending=True

### Curated hash manifest
- Wrote `Data/_meta/curated_manifest.csv` (504 files).

## Step 08 — consolidate Defi into DefiLlama  _(run 2026-04-17 03:28:02Z)_

### Consolidation moves

- renamed `DefiLlama/CSV/` -> `DefiLlama/TVL/`.

- moved `Defi/all_metrics_2026-04-17 (1) volume.csv` -> `DefiLlama/ChainMetrics/all_metrics_2026-04-17 (1) volume.csv`
- moved `Defi/all_metrics_2026-04-17.csv` -> `DefiLlama/ChainMetrics/all_metrics_2026-04-17.csv`
- moved `Defi/cex_net_inflows_by_exchange__daily.csv` -> `DefiLlama/CEX/cex_net_inflows_by_exchange__daily.csv`
- moved `Defi/dat-institutions.csv` -> `DefiLlama/DATs/dat-institutions.csv`
- moved `Defi/etf-history.csv` -> `DefiLlama/ETFs/etf-history.csv`
- moved `Defi/etf-overview.csv` -> `DefiLlama/ETFs/etf-overview.csv`
- moved `Defi/ethereum_metrics_2026-04-17 (1).csv` -> `DefiLlama/ChainMetrics/ethereum_metrics_2026-04-17 (1).csv`
- moved `Defi/ethereum_metrics_2026-04-17 Fees and revenue.csv` -> `DefiLlama/ChainMetrics/ethereum_metrics_2026-04-17 Fees and revenue.csv`
- moved `Defi/ethereum_metrics_2026-04-17 volume.csv` -> `DefiLlama/ChainMetrics/ethereum_metrics_2026-04-17 volume.csv`
- moved `Defi/rwa-category-chart_combined_2026-04-17.csv` -> `DefiLlama/RWA/rwa-category-chart_combined_2026-04-17.csv`
- moved `Defi/rwa-time-series-chart-active-mcap-all-2026-04-14.csv` -> `DefiLlama/RWA/rwa-time-series-chart-active-mcap-all-2026-04-14.csv`
- moved `Defi/rwa-time-series-chart-defi-active-tvl-all-2026-04-14.csv` -> `DefiLlama/RWA/rwa-time-series-chart-defi-active-tvl-all-2026-04-14.csv`
- moved `Defi/rwa-time-series-chart-onchain-mcap-all-2026-04-14.csv` -> `DefiLlama/RWA/rwa-time-series-chart-onchain-mcap-all-2026-04-14.csv`
- moved `Defi/solana_metrics_2026-04-17.csv` -> `DefiLlama/ChainMetrics/solana_metrics_2026-04-17.csv`
- moved `Defi/stablecoin_mcap_by_defillama_id__daily.csv` -> `DefiLlama/Stablecoins/stablecoin_mcap_by_defillama_id__daily.csv`
- moved `Defi/stablecoin_mcap_id_to_name.csv` -> `DefiLlama/Stablecoins/stablecoin_mcap_id_to_name.csv`
- moved `Defi/stablecoins-chains.csv` -> `DefiLlama/Stablecoins/stablecoins-chains.csv`
- moved `Defi/stablecoins.csv` -> `DefiLlama/Stablecoins/stablecoins.csv`
- moved `Defi/_raw_parts/cex_inflows/cex-inflows-chart_combined_2026-04-17 part 1.csv` -> `DefiLlama/_raw_parts/cex_inflows/cex-inflows-chart_combined_2026-04-17 part 1.csv`
- moved `Defi/_raw_parts/cex_inflows/cex-inflows-chart_combined_2026-04-17 part 2.csv` -> `DefiLlama/_raw_parts/cex_inflows/cex-inflows-chart_combined_2026-04-17 part 2.csv`
- moved `Defi/_raw_parts/cex_inflows/cex-inflows-chart_combined_2026-04-17 part 3.csv` -> `DefiLlama/_raw_parts/cex_inflows/cex-inflows-chart_combined_2026-04-17 part 3.csv`
- moved `Defi/_raw_parts/README.md` -> `DefiLlama/_raw_parts/README.md`
- moved `Defi/_raw_parts/stablecoin_mcap/stablecoin-mcap-chart_combined_2026-04-17 (1) part 5.csv` -> `DefiLlama/_raw_parts/stablecoin_mcap/stablecoin-mcap-chart_combined_2026-04-17 (1) part 5.csv`
- moved `Defi/_raw_parts/stablecoin_mcap/stablecoin-mcap-chart_combined_2026-04-17 (1) part 6.csv` -> `DefiLlama/_raw_parts/stablecoin_mcap/stablecoin-mcap-chart_combined_2026-04-17 (1) part 6.csv`
- moved `Defi/_raw_parts/stablecoin_mcap/stablecoin-mcap-chart_combined_2026-04-17 (1) part 7.csv` -> `DefiLlama/_raw_parts/stablecoin_mcap/stablecoin-mcap-chart_combined_2026-04-17 (1) part 7.csv`
- moved `Defi/_raw_parts/stablecoin_mcap/stablecoin-mcap-chart_combined_2026-04-17 part 1.csv` -> `DefiLlama/_raw_parts/stablecoin_mcap/stablecoin-mcap-chart_combined_2026-04-17 part 1.csv`
- moved `Defi/_raw_parts/stablecoin_mcap/stablecoin-mcap-chart_combined_2026-04-17 part 2.csv` -> `DefiLlama/_raw_parts/stablecoin_mcap/stablecoin-mcap-chart_combined_2026-04-17 part 2.csv`
- moved `Defi/_raw_parts/stablecoin_mcap/stablecoin-mcap-chart_combined_2026-04-17 part 3.csv` -> `DefiLlama/_raw_parts/stablecoin_mcap/stablecoin-mcap-chart_combined_2026-04-17 part 3.csv`
- moved `Defi/_raw_parts/stablecoin_mcap/stablecoin-mcap-chart_combined_2026-04-17 part 4.csv` -> `DefiLlama/_raw_parts/stablecoin_mcap/stablecoin-mcap-chart_combined_2026-04-17 part 4.csv`
- moved `Defi/_raw_parts/stablecoin_mcap/stablecoin-mcap-chart_combined_2026-04-17.csv` -> `DefiLlama/_raw_parts/stablecoin_mcap/stablecoin-mcap-chart_combined_2026-04-17.csv`
- removing old `Defi/README.md` (will be regenerated)
- removed empty `Data/Defi/` folder.

## Step 06 — build inventory  _(run 2026-04-17 03:30:18Z)_

Summarized 446 CSV files.
Wrote 54 per-folder README.md files.
Wrote `Data/MASTER_DATA.md`.
Wrote `Data/MASTER_DATA.csv`.

## Step 04 — normalize dates  _(run 2026-04-17 03:30:24Z)_

Per-source counts:
- **cryptoquant**: 345
- **artemis**: 47
- **farside**: 3
- **defi**: 13
- **defillama**: 6
- **tradingview**: 12
- **skip**: 3
- **snapshot**: 19

## Step 06 — build inventory  _(run 2026-04-17 03:30:54Z)_

Summarized 445 CSV files.
Wrote 53 per-folder README.md files.
Wrote `Data/MASTER_DATA.md`.
Wrote `Data/MASTER_DATA.csv`.

## Step 07 — validation  _(run 2026-04-17 03:30:56Z)_

### Date-standardization check
- date normalization: 426 files OK, 0 failed.

### Merged-file sanity checks
- stablecoin_mcap merge: OUTPUT OR PARTS MISSING
- cex_net_inflows merge: OUTPUT OR PARTS MISSING

### CryptoQuant spot-checks (5 random files)
- [PASS] `CryptoQuant/USDT ETH/Exchange Flows/Tether USD(ERC20) Exchange Outflow (Total) - All Exchanges - Day.csv`: rows 3027 -> 3027, values preserved=True, ascending=True
- [PASS] `CryptoQuant/BTC/Inter Entity Flows/Bitcoin Miner to Miner Flow (Mean) - All Miners, 1THash - Day.csv`: rows 1903 -> 1903, values preserved=True, ascending=True
- [PASS] `CryptoQuant/BTC/Exchange Flows/Bitcoin Exchange Depositing Transactions - All Exchanges - Day.csv`: rows 6310 -> 6310, values preserved=True, ascending=True
- [PASS] `CryptoQuant/BTC/Miner Flows/Bitcoin Miner Withdrawing Addresses - All Miners - Day.csv`: rows 6302 -> 6302, values preserved=True, ascending=True
- [PASS] `CryptoQuant/BTC/Miner Flows/Bitcoin Miner In-House Flow (Total) - All Miners - Day.csv`: rows 6299 -> 6299, values preserved=True, ascending=True

### Curated hash manifest
- Wrote `Data/_meta/curated_manifest.csv` (511 files).

## Step 07 — validation  _(run 2026-04-17 03:31:23Z)_

### Date-standardization check
- date normalization: 426 files OK, 0 failed.

### Merged-file sanity checks
- stablecoin_mcap merge: cols_union_match=True (merged=200, parts_union=200), dup_dates=0, date_range_match=True (2017-11-29 .. 2026-04-17)
- cex_net_inflows merge: cols_union_match=True (merged=75, parts_union=75), dup_dates=0, date_range_match=True (2022-11-12 .. 2026-04-17)

### CryptoQuant spot-checks (5 random files)
- [PASS] `CryptoQuant/USDT ETH/Exchange Flows/Tether USD(ERC20) Exchange Outflow (Total) - All Exchanges - Day.csv`: rows 3027 -> 3027, values preserved=True, ascending=True
- [PASS] `CryptoQuant/BTC/Inter Entity Flows/Bitcoin Miner to Miner Flow (Mean) - All Miners, 1THash - Day.csv`: rows 1903 -> 1903, values preserved=True, ascending=True
- [PASS] `CryptoQuant/BTC/Exchange Flows/Bitcoin Exchange Depositing Transactions - All Exchanges - Day.csv`: rows 6310 -> 6310, values preserved=True, ascending=True
- [PASS] `CryptoQuant/BTC/Miner Flows/Bitcoin Miner Withdrawing Addresses - All Miners - Day.csv`: rows 6302 -> 6302, values preserved=True, ascending=True
- [PASS] `CryptoQuant/BTC/Miner Flows/Bitcoin Miner In-House Flow (Total) - All Miners - Day.csv`: rows 6299 -> 6299, values preserved=True, ascending=True

### Curated hash manifest
- Wrote `Data/_meta/curated_manifest.csv` (511 files).

## Step 06 — build inventory  _(run 2026-04-17 03:33:09Z)_

Summarized 445 CSV files.
Wrote 53 per-folder README.md files.
Wrote `Data/MASTER_DATA.md`.
Wrote `Data/MASTER_DATA.csv`.

## Step 09 — reorganize Tradingview  _(run 2026-04-17 22:31:19Z)_

`Tradingview/BATS_ARKK, 1D_5ac9c.csv` -> `Tradingview/Daily/ARKK_innovation_etf__daily.csv` (2,873 rows)
`Tradingview/BATS_COIN, 1D_4dc12.csv` -> `Tradingview/Daily/COIN_coinbase_stock__daily.csv` (1,259 rows)
`Tradingview/BATS_COIN, 1W_b988a.csv` -> `Tradingview/Weekly/COIN_coinbase_stock__weekly.csv` (262 rows)
`Tradingview/BATS_CRCL, 1D_dfc61.csv` -> `Tradingview/Daily/CRCL_circle_stock__daily.csv` (218 rows)
`Tradingview/BATS_GLD, 1D_424f4.csv` -> `Tradingview/Daily/GLD_gold_etf__daily.csv` (4,798 rows)
`Tradingview/BATS_IWM, 1D_7b248.csv` -> `Tradingview/Daily/IWM_russell2000_etf__daily.csv` (4,330 rows)
`Tradingview/BATS_MARA, 1D_404d6.csv` -> `Tradingview/Daily/MARA_marathon_miner_stock__daily.csv` (3,351 rows)
`Tradingview/BATS_MSTR, 1D_c7fbe.csv` -> `Tradingview/Daily/MSTR_microstrategy_stock__daily.csv` (3,926 rows)
`Tradingview/BATS_MSTR, 1W_34c00.csv` -> `Tradingview/Weekly/MSTR_microstrategy_stock__weekly.csv` (771 rows)
`Tradingview/BATS_QQQ, 1D_8372e.csv` -> `Tradingview/Daily/QQQ_nasdaq100_etf__daily.csv` (4,716 rows)
`Tradingview/BATS_QQQ, 1W_06346.csv` -> `Tradingview/Weekly/QQQ_nasdaq100_etf__weekly.csv` (1,070 rows)
`Tradingview/BATS_RIOT, 1D_bf328.csv` -> `Tradingview/Daily/RIOT_riot_miner_stock__daily.csv` (3,797 rows)
`Tradingview/BATS_RIOT, 1W_ecfda.csv` -> `Tradingview/Weekly/RIOT_riot_miner_stock__weekly.csv` (1,204 rows)
`Tradingview/BATS_SMH, 1D_7eb28.csv` -> `Tradingview/Daily/SMH_vaneck_semiconductor_etf__daily.csv` (4,330 rows)
`Tradingview/BATS_SOXX, 1D_9233e.csv` -> `Tradingview/Daily/SOXX_ishares_semiconductor_etf__daily.csv` (4,766 rows)
`Tradingview/BATS_SPY, 1D_b62b8.csv` -> `Tradingview/Daily/SPY_sp500_etf__daily.csv` (3,512 rows)
`Tradingview/BATS_SPY, 1W_08055.csv` -> `Tradingview/Weekly/SPY_sp500_etf__weekly.csv` (1,734 rows)
`Tradingview/BATS_XLK, 1D_7d51a.csv` -> `Tradingview/Daily/XLK_tech_sector_etf__daily.csv` (4,808 rows)
`Tradingview/CME_DL_BTC1!, 1W_6395d.csv` -> `Tradingview/Weekly/CME_BTC1_continuous_futures__weekly.csv` (435 rows)
`Tradingview/CME_DL_ETH1!, 1W_69670.csv` -> `Tradingview/Weekly/CME_ETH1_continuous_futures__weekly.csv` (272 rows)
`Tradingview/CME_DL_MBT1!, 1W_22da0.csv` -> `Tradingview/Weekly/CME_Micro_Bitcoin_MBT1_continuous__weekly.csv` (350 rows)
`Tradingview/CME_DL_MET1!, 1W_566c8.csv` -> `Tradingview/Weekly/CME_Micro_Ether_MET1_continuous__weekly.csv` (229 rows)
`Tradingview/OANDA_XAUUSD, 1D_5955d.csv` -> `Tradingview/Daily/XAUUSD_gold_spot__daily.csv` (1,216 rows)
`Tradingview/OANDA_XAUUSD, 1W_e338a.csv` -> `Tradingview/Weekly/XAUUSD_gold_spot__weekly.csv` (1,748 rows)
`Tradingview/tradingview__CME_BTC_front_month_futures__daily.csv` -> `Tradingview/Daily/CME_BTC_front_month_futures__daily.csv` (2,096 rows)
`Tradingview/tradingview__CME_BTC_futures_minus_SPOT_BTC_basis__daily.csv` -> `Tradingview/Daily/CME_BTC_futures_minus_SPOT_BTC_basis__daily.csv` (2,102 rows)
`Tradingview/tradingview__CME_BTC_futures_over_SPOT_BTC_ratio__daily.csv` -> `Tradingview/Daily/CME_BTC_futures_over_SPOT_BTC_ratio__daily.csv` (2,102 rows)
`Tradingview/tradingview__CME_ETH_front_month_futures__daily.csv` -> `Tradingview/Daily/CME_ETH_front_month_futures__daily.csv` (1,307 rows)
`Tradingview/tradingview__CME_ETH_futures_minus_SPOT_ETH_basis__daily.csv` -> `Tradingview/Daily/CME_ETH_futures_minus_SPOT_ETH_basis__daily.csv` (1,308 rows)
`Tradingview/tradingview__CME_ETH_futures_over_SPOT_ETH_ratio__daily.csv` -> `Tradingview/Daily/CME_ETH_futures_over_SPOT_ETH_ratio__daily.csv` (1,308 rows)
`Tradingview/tradingview__CME_Micro_Bitcoin_futures__daily.csv` -> `Tradingview/Daily/CME_Micro_Bitcoin_futures__daily.csv` (1,685 rows)
`Tradingview/tradingview__CME_Micro_Ether_futures__daily.csv` -> `Tradingview/Daily/CME_Micro_Ether_futures__daily.csv` (1,099 rows)
`Tradingview/tradingview__CME_Solana_futures__daily.csv` -> `Tradingview/Daily/CME_Solana_futures__daily.csv` (274 rows)
`Tradingview/tradingview__Deribit_BTC_volatility_index_DVOL__daily.csv` -> `Tradingview/Daily/Deribit_BTC_volatility_index_DVOL__daily.csv` (1,850 rows)
`Tradingview/tradingview__ETHA_ETF_over_SPOT_ETH__daily.csv` -> `Tradingview/Daily/ETHA_ETF_over_SPOT_ETH__daily.csv` (435 rows)
`Tradingview/tradingview__IBIT_ETF_over_SPOT_BTC__daily.csv` -> `Tradingview/Daily/IBIT_ETF_over_SPOT_BTC__daily.csv` (567 rows)

**TVC_DXY daily pair**
  - differing bytes; picked widest date span: TVC_DXY, 1D_4f17d.csv rows=4768 span_d=6882, TVC_DXY, 1D_b5047.csv rows=4699 span_d=6783
  - `Tradingview/TVC_DXY, 1D_4f17d.csv` -> `Tradingview/Daily/DXY_us_dollar_index__daily.csv` (4,768 rows)
  - quarantined duplicate `Tradingview/TVC_DXY, 1D_b5047.csv`

**TVC_DXY weekly pair**
  - byte-identical duplicates: TVC_DXY, 1W_5f115.csv, TVC_DXY, 1W_def5e.csv
  - `Tradingview/TVC_DXY, 1W_5f115.csv` -> `Tradingview/Weekly/DXY_us_dollar_index__weekly.csv` (2,933 rows)
  - quarantined duplicate `Tradingview/TVC_DXY, 1W_def5e.csv`

## Step 10 — clean new DefiLlama files  _(run 2026-04-17 22:31:26Z)_

### Near-duplicate resolution
- near-dup group: winner `DefiLlama/ChainMetrics/all_metrics_2026-04-17.csv` (cols=40, size=935,846)
  - archived `DefiLlama/ChainMetrics/all_metrics_2026-04-17 (1) volume.csv` (cols=38) -> `DefiLlama/_raw_parts/duplicates/all_metrics_2026-04-17 (1) volume.csv`.
- near-dup group: winner `DefiLlama/ChainMetrics/ethereum_metrics_2026-04-17 volume.csv` (cols=48, size=1,014,042)
  - archived `DefiLlama/ChainMetrics/ethereum_metrics_2026-04-17 (1).csv` (cols=48) -> `DefiLlama/_raw_parts/duplicates/ethereum_metrics_2026-04-17 (1).csv`.
  - archived `DefiLlama/ChainMetrics/ethereum_metrics_2026-04-17 Fees and revenue.csv` (cols=48) -> `DefiLlama/_raw_parts/duplicates/ethereum_metrics_2026-04-17 Fees and revenue.csv`.
- near-dup group: winner `DefiLlama/RWA/rwa-time-series-chart-active-mcap-all-2026-04-17.csv` (cols=23, size=222,293)
  - archived `DefiLlama/RWA/rwa-time-series-chart-active-mcap-all-2026-04-14.csv` (cols=19) -> `DefiLlama/_raw_parts/duplicates/rwa-time-series-chart-active-mcap-all-2026-04-14.csv`.
- near-dup group: winner `DefiLlama/RWA/rwa-time-series-chart-onchain-mcap-all-2026-04-17.csv` (cols=25, size=244,258)
  - archived `DefiLlama/RWA/rwa-time-series-chart-onchain-mcap-all-2026-04-14.csv` (cols=22) -> `DefiLlama/_raw_parts/duplicates/rwa-time-series-chart-onchain-mcap-all-2026-04-14.csv`.

### Renames
- renamed `DefiLlama/ChainMetrics/all_metrics_2026-04-17.csv` -> `DefiLlama/ChainMetrics/all_chains_metrics__daily.csv`.
- renamed `DefiLlama/ChainMetrics/solana_metrics_2026-04-17.csv` -> `DefiLlama/ChainMetrics/solana_metrics__daily.csv`.
- renamed `DefiLlama/ChainMetrics/chains-dominance-2026-04-17.csv` -> `DefiLlama/ChainMetrics/chain_tvl_dominance__daily.csv`.
- renamed `DefiLlama/ChainMetrics/all dex metrics.csv` -> `DefiLlama/ChainMetrics/all_dex_metrics__daily.csv`.
- renamed `DefiLlama/ChainMetrics/all-chains-perp-volume-by-protocol-bar-absolute-stacked-daily-2026-04-17.csv` -> `DefiLlama/ChainMetrics/all_chains_perp_volume_by_protocol__daily.csv`.
- renamed `DefiLlama/RWA/rwa-time-series-chart-active-mcap-all-2026-04-17.csv` -> `DefiLlama/RWA/rwa_active_mcap_all__daily.csv`.
- renamed `DefiLlama/RWA/rwa-time-series-chart-onchain-mcap-all-2026-04-17.csv` -> `DefiLlama/RWA/rwa_onchain_mcap_all__daily.csv`.
- renamed `DefiLlama/RWA/rwa-time-series-chart-onchain-mcap-all-2026-04-17 platfrom breakdown.csv` -> `DefiLlama/RWA/rwa_onchain_mcap_by_platform__daily.csv`.
- renamed `DefiLlama/RWA/rwa-time-series-chart-defi-active-tvl-all-2026-04-14.csv` -> `DefiLlama/RWA/rwa_defi_active_tvl_all__daily.csv`.
- renamed `DefiLlama/RWA/rwa-category-chart_combined_2026-04-17.csv` -> `DefiLlama/RWA/rwa_mcap_by_category__daily.csv`.

## Step 11 — flatten Farside  _(run 2026-04-17 22:31:32Z)_

- moved `Farside ETF Data/BTC/bitcoin_etf_flow_all_data.csv` -> `Farside ETF Data/farside_btc_etf_flows__daily.csv` (579 rows).
- moved `Farside ETF Data/ETH/ethereum_etf_flow_all_data.csv` -> `Farside ETF Data/farside_eth_etf_flows__daily.csv` (441 rows).
- moved `Farside ETF Data/SOL/solana_etf_flow_all_data.csv` -> `Farside ETF Data/farside_sol_etf_flows__daily.csv` (12 rows).
- removed `Farside ETF Data/BTC/`.
- removed `Farside ETF Data/ETH/`.
- removed `Farside ETF Data/SOL/`.
- wrote consolidated `Farside ETF Data/README.md` covering 3 files.

## Step 04 — normalize dates  _(run 2026-04-17 22:32:04Z)_

Per-source counts:
- **cryptoquant**: 345
- **artemis**: 47
- **farside**: 3
- **defi**: 15
- **defillama**: 6
- **tradingview**: 38
- **simple**: 21
- **skip**: 5
- **snapshot**: 25
- **timestamp_utc columns dropped in sweep**: 0

## Step 06 — build inventory  _(run 2026-04-17 22:33:47Z)_

Summarized 502 CSV files.
Wrote 55 per-folder README.md files.
Wrote `Data/MASTER_DATA.md`.
Wrote `Data/MASTER_DATA.csv`.

## Step 07 — validation  _(run 2026-04-17 22:34:17Z)_

### Date-standardization check
- date normalization: 475 files OK, 0 failed.

### No timestamp_utc column check
- no-timestamp-utc check: 485 files checked, 0 violations.

### Merged-file sanity checks
- stablecoin_mcap merge: cols_union_match=True (merged=200, parts_union=200), dup_dates=0, date_range_match=True (2017-11-29 .. 2026-04-17)
- cex_net_inflows merge: cols_union_match=True (merged=75, parts_union=75), dup_dates=0, date_range_match=True (2022-11-12 .. 2026-04-17)

### CryptoQuant spot-checks (5 random files)
- [PASS] `CryptoQuant/USDT ETH/Exchange Flows/Tether USD(ERC20) Exchange Outflow (Total) - All Exchanges - Day.csv`: rows 3027 -> 3027, values preserved=True, ascending=True
- [PASS] `CryptoQuant/BTC/Inter Entity Flows/Bitcoin Miner to Miner Flow (Mean) - All Miners, 1THash - Day.csv`: rows 1903 -> 1903, values preserved=True, ascending=True
- [PASS] `CryptoQuant/BTC/Exchange Flows/Bitcoin Exchange Depositing Transactions - All Exchanges - Day.csv`: rows 6310 -> 6310, values preserved=True, ascending=True
- [PASS] `CryptoQuant/BTC/Miner Flows/Bitcoin Miner Withdrawing Addresses - All Miners - Day.csv`: rows 6302 -> 6302, values preserved=True, ascending=True
- [PASS] `CryptoQuant/BTC/Miner Flows/Bitcoin Miner In-House Flow (Total) - All Miners - Day.csv`: rows 6299 -> 6299, values preserved=True, ascending=True

### Curated hash manifest
- Wrote `Data/_meta/curated_manifest.csv` (570 files).

## Step 06 — build inventory  _(run 2026-04-17 22:35:17Z)_

Summarized 484 CSV files.
Wrote 54 per-folder README.md files.
Wrote `Data/MASTER_DATA.md`.
Wrote `Data/MASTER_DATA.csv`.

## Step 04 — normalize dates  _(run 2026-04-17 22:37:22Z)_

Per-source counts:
- **cryptoquant**: 345
- **artemis**: 47
- **farside**: 3
- **defi**: 15
- **defillama**: 6
- **tradingview**: 38
- **simple**: 21
- **skip**: 5
- **snapshot**: 25
- **timestamp_utc columns dropped in sweep**: 0

## Step 06 — build inventory  _(run 2026-04-17 22:37:33Z)_

Summarized 484 CSV files.
Wrote 54 per-folder README.md files.
Wrote `Data/MASTER_DATA.md`.
Wrote `Data/MASTER_DATA.csv`.

## Step 07 — validation  _(run 2026-04-17 22:37:36Z)_

### Date-standardization check
- date normalization: 475 files OK, 0 failed.

### No timestamp_utc column check
- no-timestamp-utc check: 485 files checked, 0 violations.

### Merged-file sanity checks
- stablecoin_mcap merge: cols_union_match=True (merged=200, parts_union=200), dup_dates=0, date_range_match=True (2017-11-29 .. 2026-04-17)
- cex_net_inflows merge: cols_union_match=True (merged=75, parts_union=75), dup_dates=0, date_range_match=True (2022-11-12 .. 2026-04-17)

### CryptoQuant spot-checks (5 random files)
- [PASS] `CryptoQuant/USDT ETH/Exchange Flows/Tether USD(ERC20) Exchange Outflow (Total) - All Exchanges - Day.csv`: rows 3027 -> 3027, values preserved=True, ascending=True
- [PASS] `CryptoQuant/BTC/Inter Entity Flows/Bitcoin Miner to Miner Flow (Mean) - All Miners, 1THash - Day.csv`: rows 1903 -> 1903, values preserved=True, ascending=True
- [PASS] `CryptoQuant/BTC/Exchange Flows/Bitcoin Exchange Depositing Transactions - All Exchanges - Day.csv`: rows 6310 -> 6310, values preserved=True, ascending=True
- [PASS] `CryptoQuant/BTC/Miner Flows/Bitcoin Miner Withdrawing Addresses - All Miners - Day.csv`: rows 6302 -> 6302, values preserved=True, ascending=True
- [PASS] `CryptoQuant/BTC/Miner Flows/Bitcoin Miner In-House Flow (Total) - All Miners - Day.csv`: rows 6299 -> 6299, values preserved=True, ascending=True

### Curated hash manifest
- Wrote `Data/_meta/curated_manifest.csv` (570 files).

## Step 06 — build inventory  _(run 2026-04-17 22:51:49Z)_

Summarized 484 CSV files.
Wrote 54 per-folder README.md files.
Wrote `Data/MASTER_DATA.md`.
Wrote `Data/MASTER_DATA.csv`.

## Step 07 — validation  _(run 2026-04-17 22:51:52Z)_

### Date-standardization check
- date normalization: 475 files OK, 0 failed.

### No timestamp_utc column check
- no-timestamp-utc check: 485 files checked, 0 violations.

### Merged-file sanity checks
- stablecoin_mcap merge: cols_union_match=True (merged=200, parts_union=200), dup_dates=0, date_range_match=True (2017-11-29 .. 2026-04-17)
- cex_net_inflows merge: cols_union_match=True (merged=75, parts_union=75), dup_dates=0, date_range_match=True (2022-11-12 .. 2026-04-17)

### CryptoQuant spot-checks (5 random files)
- [PASS] `CryptoQuant/USDT ETH/Exchange Flows/Tether USD(ERC20) Exchange Outflow (Total) - All Exchanges - Day.csv`: rows 3027 -> 3027, values preserved=True, ascending=True
- [PASS] `CryptoQuant/BTC/Inter Entity Flows/Bitcoin Miner to Miner Flow (Mean) - All Miners, 1THash - Day.csv`: rows 1903 -> 1903, values preserved=True, ascending=True
- [PASS] `CryptoQuant/BTC/Exchange Flows/Bitcoin Exchange Depositing Transactions - All Exchanges - Day.csv`: rows 6310 -> 6310, values preserved=True, ascending=True
- [PASS] `CryptoQuant/BTC/Miner Flows/Bitcoin Miner Withdrawing Addresses - All Miners - Day.csv`: rows 6302 -> 6302, values preserved=True, ascending=True
- [PASS] `CryptoQuant/BTC/Miner Flows/Bitcoin Miner In-House Flow (Total) - All Miners - Day.csv`: rows 6299 -> 6299, values preserved=True, ascending=True

### Curated hash manifest
- Wrote `Data/_meta/curated_manifest.csv` (567 files).

## Step 06 — build inventory  _(run 2026-04-18 02:22:07Z)_

Summarized 484 CSV files.
Wrote 54 per-folder README.md files.
Wrote `Data/MASTER_DATA.md`.
Wrote `Data/MASTER_DATA.txt`.
Wrote `Data/MASTER_DATA.csv`.

## Step 06 — build inventory  _(run 2026-04-19 01:01:17Z)_

Summarized 490 CSV files.
Wrote 54 per-folder README.md files.
Wrote `Data/MASTER_DATA.md`.
Wrote `Data/MASTER_DATA.txt`.
Wrote `Data/MASTER_DATA.csv`.

## Step 07 — validation  _(run 2026-04-19 01:03:29Z)_

### Date-standardization check
- date normalization: 481 files OK, 0 failed.

### No timestamp_utc column check
- no-timestamp-utc check: 491 files checked, 0 violations.

### Merged-file sanity checks
- stablecoin_mcap merge: cols_union_match=True (merged=200, parts_union=200), dup_dates=0, date_range_match=True (2017-11-29 .. 2026-04-17)
- cex_net_inflows merge: cols_union_match=True (merged=75, parts_union=75), dup_dates=0, date_range_match=True (2022-11-12 .. 2026-04-17)

### CryptoQuant spot-checks (5 random files)
- backup dir not configured or missing. Set `validate.backup_dir` in `config/curation_snapshots.yml` to enable CryptoQuant spot-checks. Skipping (non-fatal).

### Curated hash manifest
- Wrote `Data/_meta/curated_manifest.csv` (574 files).
