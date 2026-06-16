# Data Analysis: Overlapping Metrics Across Sources

Audit date: 2026-04-18  
Repository: `C:\Dev\Projects\CryptoQuant`

## Executive Judgment

**Verified.** The repository has enough vendor overlap to cross-check important metric families, especially ETF flows, ETF AUM, stablecoin supply, TVL, USD strength, and ETH market cap. Evidence: `Data/MASTER_DATA.md`, `Data/MASTER_DATA.csv`, `Data/Farside ETF Data/`, `Data/DefiLlama/`, `Data/Artemis/`, `Data/FRED/`, `Data/Tradingview/`, `Data/CryptoQuant/`.

**Verified.** Overlap does not mean interchangeability. Several files have similar economic labels but different units, frequencies, coverage universes, chain/issuer inclusion rules, or calendar conventions. The safest workflow is to choose one primary source per concept, use overlapping vendors as robustness or reconciliation checks, and avoid silent merges.

**Inference.** For the canonical ETF/factor-exposure paper, Farside should be primary for daily ETF event-flow analysis; DefiLlama should be primary for broad daily stablecoin market cap and total TVL; Artemis should be used for weekly/composition robustness; FRED should be primary for official macro variables; TradingView should be used for market-convention price series; and CryptoQuant should be primary for BTC/ETH-native asset metrics.

## Source Coverage Context

**Verified.** `Data/MASTER_DATA.md` reports 484 CSV files and about 1.81 million rows across seven source families:

| Source | Files | Rows | Date span | Main use |
|---|---:|---:|---|---|
| AlternativeMe | 1 | 2,994 | 2018-02-01 to 2026-04-17 | Fear/greed sentiment |
| Artemis | 48 | 75,302 | 2010-01-01 to 2026-04-30 | ETF, chain, stablecoin, RWA, DEX, lending |
| CryptoQuant | 345 | 1,181,712 | 2006-04-11 to 2026-04-12 | BTC/ETH native, exchange, miner, network metrics |
| DefiLlama | 28 | 306,856 | 2016-04-19 to 2026-04-19 | TVL, stablecoins, ETFs, CEX, chain metrics |
| FRED | 21 | 166,529 | 1947-01-01 to 2026-04-17 | Macro, rates, credit, dollar indexes |
| Farside ETF Data | 3 | 1,032 | 2024-01-11 to 2026-04-10 | Daily ETF issuer and total flows |
| TradingView | 38 | 79,809 | 1967-01-29 to 2026-04-17 | Market prices, ETFs, equities, CME futures/basis |

Evidence: `Data/MASTER_DATA.md`.

## Classification Key

- **Exact duplicate after unit conversion:** same concept and nearly identical values after converting units.
- **Near-duplicate:** same concept, high correlation, small but non-trivial level differences.
- **Related but definitionally different:** same economic family but different universe, construction, or frequency.
- **Different concept despite similar name:** should not be merged.
- **Not comparable yet:** needs additional metadata or reconciliation before use.

## Summary Recommendations

| Metric category | Classification | Primary source | Robustness / secondary source |
|---|---|---|---|
| BTC daily ETF flows | Exact duplicate after unit conversion | Farside | DefiLlama aggregate ETF history |
| ETH daily ETF flows | Exact duplicate after unit conversion | Farside | DefiLlama aggregate ETF history |
| BTC/ETH weekly ETF flows | Near-duplicate with week/cutoff differences | Farside daily resampled | Artemis weekly ETF flow files |
| ETF AUM | Related; issuer-sum and aggregate differ | Artemis aggregate crypto ETF AUM | Artemis issuer files after reconciliation |
| Total stablecoin supply | Related; universe/frequency differences | DefiLlama daily stablecoin market cap | Artemis token/monthly and selected-chain files |
| Total TVL | Near-exact within DefiLlama | DefiLlama all-chain TVL | DefiLlama chain-summed TVL |
| DEX TVL vs all-chain TVL | Different concepts | Artemis DEX TVL for DEX liquidity | DefiLlama all-chain TVL for total DeFi |
| USD strength | Related but different definitions | FRED broad dollar index | TradingView DXY |
| ETH market cap | Near-duplicate | CryptoQuant for ETH-native work | Artemis for cross-chain comparability |
| Open interest | Not comparable yet | CryptoQuant or Artemis depending question | Reconcile exchange/universe definitions |
| Fees / active addresses | Not comparable yet | CryptoQuant for BTC/ETH network metrics | Artemis for chain/ecosystem metrics |
| Exchange flows | Not comparable yet | CryptoQuant | DefiLlama CEX snapshots only if concept matches |

## ETF Flows

### BTC Daily ETF Flows: Farside vs DefiLlama

**Classification:** Exact duplicate after unit conversion.  
**Confidence:** High.

**Compared files.**

- `Data/Farside ETF Data/farside_btc_etf_flows__daily.csv`
- `Data/DefiLlama/ETFs/etf-history.csv`

**Verified comparison.**

- Overlap: 274 daily observations.
- Overlap window: 2024-01-11 to 2026-04-01.
- Transformation: Farside `Total` multiplied by 1,000,000 versus DefiLlama `total_flow_usd` for Bitcoin.
- Correlation: 1.000000.
- Median absolute difference: 0.
- Maximum absolute difference: approximately `1.19e-07`, consistent with floating-point/rounding noise.

**Interpretation.** These are the same aggregate daily BTC ETF flow concept after unit conversion. Farside has the advantage for daily event work because it carries issuer-level columns and is the natural source for ETF flow decomposition. DefiLlama is useful as an independent aggregate cross-check.

**Recommended use.** Use Farside as primary for BTC ETF flow event windows and issuer-level analysis. Use DefiLlama aggregate ETF history as a validation source.

### ETH Daily ETF Flows: Farside vs DefiLlama

**Classification:** Exact duplicate after unit conversion.  
**Confidence:** High.

**Compared files.**

- `Data/Farside ETF Data/farside_eth_etf_flows__daily.csv`
- `Data/DefiLlama/ETFs/etf-history.csv`

**Verified comparison.**

- Overlap: 263 daily observations.
- Overlap window: 2024-07-23 to 2026-04-10.
- Transformation: Farside `Total` multiplied by 1,000,000 versus DefiLlama `total_flow_usd` for Ethereum.
- Correlation: 1.000000.
- Median absolute difference: 0.
- Maximum absolute difference: approximately `5.96e-08`, consistent with rounding noise.

**Recommended use.** Use Farside as primary for ETH ETF flow event windows and issuer-level analysis. Use DefiLlama aggregate ETF history as a validation source.

### Weekly ETF Flows: Farside Daily Resample vs Artemis

**Classification:** Near-duplicate with material week-label/cutoff/vendor-revision differences.  
**Confidence:** Medium-high.

**Compared files.**

- `Data/Farside ETF Data/farside_btc_etf_flows__daily.csv`
- `Data/Farside ETF Data/farside_eth_etf_flows__daily.csv`
- `Data/Artemis/Crypto ETF Flows.csv`

**Verified comparison.**

BTC:

- Farside daily totals resampled to `W-SUN` versus Artemis weekly BTC flow.
- Overlap: 118 weekly observations.
- Correlation: 0.999718.
- Median absolute difference: 0.
- Maximum absolute difference: about $228.5 million.
- 95th percentile relative difference: about 6.7%.

ETH:

- Farside daily totals resampled to `W-SUN` versus Artemis weekly ETH flow.
- Overlap: 90 weekly observations.
- Correlation: 0.999838.
- Median absolute difference: 0.
- Maximum absolute difference: about $77.5 million.
- 95th percentile relative difference: about 7.1%.
- Largest observed ETH weekly discrepancy occurred around the week ending 2025-01-05, where Farside resampling and Artemis gave opposite signs.

**Interpretation.** The series are effectively the same economic object most weeks, but weekly alignment and revisions matter. The sign-flip week means weekly Artemis data should not be silently substituted for daily Farside data in event studies.

**Recommended use.** Use Farside daily flows as canonical. Use Artemis weekly flows only for lower-frequency robustness after documenting week-ending convention.

## ETF AUM

### Artemis Aggregate AUM vs Issuer-Summed AUM

**Classification:** Related but not safely interchangeable.  
**Confidence:** Medium-high.

**Compared files.**

- `Data/Artemis/Crypto ETFs AUM.csv`
- `Data/Artemis/Bitcoin ETFs AUM.csv`
- `Data/Artemis/Ethereum ETFs AUM.csv`

**Verified comparison.**

BTC:

- Issuer-level BTC ETF AUM sum, excluding the file's `Bitcoin` column, compared with aggregate `Bitcoin` in `Crypto ETFs AUM.csv`.
- Overlap: 825 observations.
- Correlation: 0.999429.
- Median absolute difference: about $1.984 billion.
- Maximum absolute difference: about $4.764 billion.
- Median relative difference: about 1.71%.
- 95th percentile relative difference: about 3.88%.

ETH:

- Issuer-level ETH ETF AUM sum, excluding the file's `Ethereum` column, compared with aggregate `Ethereum` in `Crypto ETFs AUM.csv`.
- Overlap: 631 observations.
- Correlation: 0.999640.
- Median absolute difference: about $603 million.
- Maximum absolute difference: about $2.069 billion.
- Median relative difference: about 6.16%.
- 95th percentile relative difference: about 10.42%.

**Important warning.** The `Bitcoin` column inside `Bitcoin ETFs AUM.csv` should not be treated as total issuer AUM. Compared with total issuer-summed AUM, it differs by a very large relative amount. The same caution applies to aggregate-looking columns in issuer files unless metadata confirms their meaning.

**Interpretation.** Aggregate and issuer-summed Artemis AUM files track each other closely but differ materially in level. Likely causes include coverage changes, aggregate methodology, price marks, issuer inclusion, or column semantics.

**Recommended use.** Use `Data/Artemis/Crypto ETFs AUM.csv` for asset-level aggregate AUM. Use issuer-level AUM files for composition only after reconciling included issuers and aggregate columns.

## Stablecoin Supply

### Artemis Chain Stablecoin Supply vs DefiLlama Stablecoin Market Cap

**Classification:** Related but definitionally different.  
**Confidence:** High.

**Compared files.**

- `Data/Artemis/Chains - Stablecoin Supply.csv`
- `Data/DefiLlama/Stablecoins/stablecoin_mcap_by_defillama_id__daily.csv`
- `Data/DefiLlama/Stablecoins/stablecoins.csv`
- `Data/DefiLlama/Stablecoins/stablecoin_mcap_id_to_name.csv`

**Verified comparison.**

- Artemis selected-chain stablecoin supply summed across available chain columns versus DefiLlama daily all-id stablecoin market cap.
- Overlap: 3,059 daily observations.
- Correlation: 0.987710.
- Median absolute difference: about $44.37 billion.
- Maximum absolute difference: about $365.14 billion.
- Median relative difference: about 33.5%.
- 95th percentile relative difference: about 45.9%.

**Interpretation.** These are not duplicates. The Artemis file covers selected chains visible in that file, while DefiLlama all-id market cap covers a broader stablecoin universe. Missing chains such as Tron, Base, BSC, or other venues can materially affect levels.

**Recommended use.** Use DefiLlama daily all-id stablecoin market cap for broad market liquidity. Use Artemis chain-level stablecoin supply for selected-chain allocation and chain-specific robustness.

### Artemis Token Stablecoin Supply vs DefiLlama Month-End Total

**Classification:** Related; mostly close in normal overlapping periods but frequency/current-period conventions matter.  
**Confidence:** Medium.

**Compared files.**

- `Data/Artemis/Stablecoin Supply by Token.csv`
- `Data/DefiLlama/Stablecoins/stablecoin_mcap_by_defillama_id__daily.csv`

**Verified comparison.**

- Artemis token-level monthly supply sum versus DefiLlama month-end total.
- Overlap: 102 monthly observations.
- Correlation: 0.982954.
- Median absolute difference: about $1.157 billion.
- Median relative difference: about 2.07%.
- Maximum absolute difference: about $151.88 billion.
- 95th percentile relative difference: about 22.38%.

**Interpretation.** Median differences are modest, but the tails are too large for blind substitution. The largest discrepancy appears around the current/incomplete April 2026 month-end convention, and early-history differences also matter.

**Data-quality note.** `Data/DefiLlama/Stablecoins/stablecoin_mcap_id_to_name.csv` appears weak for mapping because observed `name`, `symbol`, and `pegType` fields are blank in sampled rows. `Data/DefiLlama/Stablecoins/stablecoins.csv` has more usable snapshot metadata, but snapshot metadata may not fully describe historical composition.

**Recommended use.** Use DefiLlama for daily total stablecoin market cap. Use Artemis token supply for monthly composition after controlling for incomplete month-end observations.

## TVL

### DefiLlama Total TVL vs Chain-Summed TVL

**Classification:** Near-exact internal consistency check.  
**Confidence:** High.

**Compared files.**

- `Data/DefiLlama/TVL/tvl_all_chains_daily.csv`
- `Data/DefiLlama/TVL/tvl_by_chain_wide_daily.csv`

**Verified comparison.**

- Overlap: 3,122 daily observations.
- Correlation: 0.999996.
- Median absolute difference: about $10,885.
- Maximum absolute difference: about $1.334 billion.
- Median relative difference: about `4e-7`.
- 95th percentile relative difference: about 0.218%.

**Interpretation.** DefiLlama total TVL and chain-summed TVL are internally consistent for most purposes. Small residuals are likely from chain coverage changes, rounding, or aggregation details.

**Recommended use.** Use `tvl_all_chains_daily.csv` for total TVL. Use chain-wide/long files for decomposition.

### Artemis DEX TVL vs DefiLlama All-Chain TVL

**Classification:** Different concept despite related label.  
**Confidence:** High.

**Compared files.**

- `Data/Artemis/DEX - TVL.csv`
- `Data/DefiLlama/TVL/tvl_all_chains_daily.csv`

**Verified comparison.**

- Artemis DEX protocol TVL sum versus DefiLlama all-chain TVL.
- Overlap: 3,122 daily observations.
- Correlation: about 0.9592.
- Median relative difference: about 81.4%.

**Interpretation.** DEX TVL is a protocol-sector subset. All-chain TVL is a broad DeFi/chain total. They are related liquidity indicators, but they are not substitutes.

**Recommended use.** Use Artemis DEX TVL only for DEX liquidity or sector-specific robustness. Use DefiLlama all-chain TVL for broad crypto liquidity.

## USD Strength

### FRED Broad Dollar Index vs TradingView DXY

**Classification:** Related but definitionally different.  
**Confidence:** High.

**Compared files.**

- `Data/FRED/DTWEXBGS.csv`
- TradingView DXY file under `Data/Tradingview/`

**Verified comparison.**

- Overlap: 3,751 observations.
- Correlation: 0.971233.
- Median absolute difference: about 16.18 index points.
- Median relative difference: about 14.7%.
- 95th percentile relative difference: about 18.8%.

**Interpretation.** Both represent USD strength, but FRED `DTWEXBGS` is a broad trade-weighted dollar index, while DXY is the market-standard ICE dollar index with a narrower currency basket. The values differ materially even though they co-move.

**Recommended use.** Use FRED broad dollar index for official macro exposure. Use TradingView DXY for robustness when market convention is more important than broad trade weighting.

## ETH Market Cap

### Artemis ETH Market Cap vs CryptoQuant ETH Market Cap

**Classification:** Near-duplicate with methodology differences.  
**Confidence:** High.

**Compared files.**

- `Data/Artemis/Chains - Market Cap.csv`
- `Data/CryptoQuant/ETH/Market Data/Ethereum Market Cap - Day.csv`

**Verified comparison.**

- Overlap: 3,894 daily observations.
- Correlation: 0.999933.
- Median absolute difference: about $206 million.
- Median relative difference: about 0.38%.
- 95th percentile relative difference: about 7.42%.

**Interpretation.** These are essentially the same economic concept in recent periods, but early-history and methodology differences are non-trivial enough to avoid mixing them.

**Recommended use.** Use CryptoQuant ETH market cap when paired with CryptoQuant ETH-native metrics. Use Artemis ETH market cap when cross-chain comparability is the priority.

## Categories Requiring Further Reconciliation

### Open Interest

**Classification:** Not comparable yet.  
**Confidence:** Medium.

**Relevant sources.**

- Artemis central exchange / perpetuals open-interest files.
- CryptoQuant BTC/ETH open-interest files.
- TradingView CME futures/basis series.

**Issue.** These sources likely differ by instrument universe, venue set, contract type, quote currency, and asset scope. A single "open interest" label is not sufficient.

**Recommended next step.** Build an open-interest dictionary with columns for asset, venue, instrument type, contract type, quote currency, units, and frequency before comparing values.

### Fees and Active Addresses

**Classification:** Not comparable yet.  
**Confidence:** Medium.

**Relevant sources.**

- Artemis chain-level fees and activity files.
- CryptoQuant BTC/ETH network metrics.
- `config/chain_taxonomy.yml`.

**Issue.** Artemis chain files may reflect chain/ecosystem-level concepts, while CryptoQuant BTC/ETH files are asset/network-specific. `config/chain_taxonomy.yml` correctly warns against naive ETH L1/L2 user aggregation.

**Recommended next step.** Separate BTC network metrics, ETH L1 metrics, ETH L2 metrics, and broad Ethereum ecosystem metrics. Do not sum unique addresses across L1/L2.

### Exchange Flows and CEX Metrics

**Classification:** Not comparable yet.  
**Confidence:** Medium.

**Relevant sources.**

- CryptoQuant exchange inflow/outflow/reserve metrics.
- DefiLlama CEX-related files.

**Issue.** CryptoQuant exchange metrics are likely asset-specific time-series. DefiLlama CEX files may be broader entity/snapshot/chain views. They should not be merged without unit and universe checks.

**Recommended next step.** For BTC/ETH exchange-flow factor construction, prefer CryptoQuant and use DefiLlama CEX data only if its concept matches the research question.

### Reserve-Related Metrics

**Classification:** Not comparable yet.  
**Confidence:** Low-medium.

**Relevant sources.**

- CryptoQuant reserves.
- DefiLlama CEX or stablecoin reserves if available.
- TradingView market proxies.

**Issue.** "Reserve" can mean exchange reserves, stablecoin issuer reserves, treasury holdings, or protocol reserves. These are materially different concepts.

**Recommended next step.** Require explicit semantic names: `exchange_asset_reserve`, `stablecoin_issuer_reserve`, `protocol_treasury`, or `custodial_balance`.

## Implications for the Canonical Paper

**Verified.** ETF flow data are unusually strong for BTC and ETH because Farside and DefiLlama match exactly after unit conversion. This supports using ETF flows as a core institutionalization block. Evidence: `Data/Farside ETF Data/`, `Data/DefiLlama/ETFs/etf-history.csv`.

**Verified.** Stablecoin and TVL variables need more care. Broad DefiLlama totals and Artemis selected-chain/token files are not interchangeable. Evidence: `Data/DefiLlama/Stablecoins/`, `Data/Artemis/Chains - Stablecoin Supply.csv`, `Data/Artemis/Stablecoin Supply by Token.csv`, `Data/DefiLlama/TVL/`, `Data/Artemis/DEX - TVL.csv`.

**Verified.** Macro/TradFi factors should not silently mix FRED and TradingView versions of similar concepts. FRED broad dollar and DXY are related but materially different. Evidence: `Data/FRED/DTWEXBGS.csv`, `Data/Tradingview/`.

**Inference.** The cleanest empirical design is to define one primary source per factor block, then run robustness checks with alternative vendors. Silent averaging or substitution would weaken reviewer confidence.

## Source Selection Rules

1. **ETF flows:** Farside primary; DefiLlama aggregate cross-check; Artemis weekly robustness only after week convention reconciliation.
2. **ETF AUM:** Artemis aggregate primary for asset-level AUM; issuer files only for composition.
3. **Stablecoin total supply:** DefiLlama daily all-id market cap primary; Artemis for chain/token decomposition and robustness.
4. **TVL:** DefiLlama all-chain primary for broad TVL; Artemis DEX TVL only for DEX-sector liquidity.
5. **USD strength:** FRED broad dollar primary for macro regressions; TradingView DXY as market-index robustness.
6. **ETH market cap:** CryptoQuant primary for ETH-native analysis; Artemis for cross-chain comparable panels.
7. **On-chain/native BTC/ETH metrics:** CryptoQuant primary.
8. **Chain/ecosystem metrics:** Artemis primary when the research object is chain-level activity rather than BTC/ETH asset-native activity.

## Data Risks To Resolve Before Publication

- Calendar alignment and forward-fill rules can mechanically change daily returns, macro differences, ETF flow zeros, and event windows. Evidence: `config/calendars.yml`, `src/cqresearch/data/calendars.py`, `HANDOFF.md`.
- ETF flow intensity currently uses flow divided by prior close, not market cap. Evidence: `src/cqresearch/features/panel.py`.
- Stablecoin metadata mapping has quality issues in `stablecoin_mcap_id_to_name.csv`; use `stablecoins.csv` carefully and document snapshot limitations.
- Weekly ETF comparisons need explicit week-ending conventions.
- Similar metric names across vendors require a dictionary with units, universe, frequency, and construction rules.

## Quality Gate

**Inputs read.**

- `Data/MASTER_DATA.md`
- `Data/MASTER_DATA.csv`
- `Data/Farside ETF Data/`
- `Data/DefiLlama/ETFs/`
- `Data/DefiLlama/Stablecoins/`
- `Data/DefiLlama/TVL/`
- `Data/Artemis/`
- `Data/FRED/`
- `Data/Tradingview/`
- `Data/CryptoQuant/ETH/Market Data/`
- `config/calendars.yml`
- `config/chain_taxonomy.yml`
- `src/cqresearch/features/panel.py`

**Outputs written.**

- `CODEX/data_analysis.md`

**Confidence score.** 86%.

**Supporting evidence.** High confidence for ETF daily flow equivalence, DefiLlama TVL internal consistency, dollar-index definition difference, and ETH market-cap near-duplication. Medium confidence for weekly ETF and AUM interpretation because vendor metadata and week-ending conventions need additional documentation.

**Next agent.** Data/methods reconciliation agent to formalize a metric dictionary and source-precedence contract.
