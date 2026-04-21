# Four-Paper Protocols v0

Date: 2026-04-18

Purpose: convert the manager-review decision into paper-specific execution protocols without changing source code or data. These are planning artifacts until the human confirms portfolio and calendar policy.

## Portfolio Default

Recommended default portfolio:

1. Paper 1: BTC/ETH Factor-Exposure Evolution Around Institutionalization.
2. Paper 2: ETF Flow, Wrapper, Basis, and Market-Plumbing Transmission.
3. Paper 3: Stablecoins as Shadow Settlement Liquidity.
4. Paper 4: DeFi Credit, Lending, and RWA Rate-Arbitrage Bridge.

Fallback if Paper 4 fails data-quality checks: ETH staking, LST, and LRT collateral transformation.

Evidence: `AGENTS.md`; `Data/MASTER_DATA.csv`; `reports/run_summaries/03_run_analyses.md`; `Manager/Opus Manager/comprehensive_review.md`; `Manager/Gemini Manager/Project_Audit_Report.md`.

## Paper 1 Protocol

Working title: BTC/ETH Factor-Exposure Evolution Around Institutionalization.

Category: institutionalization / market evolution.

Question: did BTC and ETH factor exposures change across crypto market maturation and spot-ETF institutionalization, and are those changes better described as ETF-date breaks or gradual multi-regime evolution?

Minimum viable design:

- Build a paper-specific panel instead of relying on one universal master panel.
- Use market-day headline regressions for macro/ETF models.
- Use crypto-7 calendar diagnostics as robustness.
- Include weekly robustness to reduce fill artifacts.
- Use HAC OLS, rolling window diagnostics, and correctly labeled Chow/single-break sup-F unless true multiple-break code is implemented.
- Add or justify selected BTC/ETH native CryptoQuant blocks before publication.

Required data:

- BTC/ETH OHLCV and returns.
- FRED rates, VIX, dollar index, and macro risk controls.
- TradingView risk proxies and wrappers as needed.
- Farside ETF flows, DefiLlama ETF cross-check, Artemis AUM.
- DefiLlama stablecoin supply and TVL.
- Selected CryptoQuant BTC/ETH native metrics.

Evidence: `reports/panels/master_daily_meta.json`; `reports/tables/2026-04-18/`; `src/cqresearch/features/panel.py`; `config/events.yml`; `Data/CryptoQuant/`.

Required tables and figures:

- Data/source/coverage table.
- Factor-block definitions and source-precedence table.
- Static HAC OLS pre/post or regime table.
- Rolling block contribution figure.
- Structural-break table with method labels that match code.
- Calendar and weekly robustness table.
- Figure separating ETF-date markers from estimated break dates.

Kill risks:

- ETF date is not the dominant break.
- Native CryptoQuant metrics do not add robust explanatory content.
- Calendar/fill choices materially drive results.
- Method labels outrun implementation.

## Paper 2 Protocol

Working title: ETF Flow, Wrapper, Basis, and Market-Plumbing Transmission.

Category: institutionalization / ETF-adjacent bridge.

Question: how do spot ETF flows, issuer composition, AUM, basis, and listed wrappers relate to daily BTC/ETH market transmission after ETF launch?

Minimum viable design:

- Use business-day/trading-day sample.
- Use issuer-level Farside flows and aggregate flows.
- Add Artemis AUM and issuer composition.
- Add CME basis and TradingView wrapper/equity proxies where available.
- Run distributed lags and T+1 flow reporting sensitivity.
- Avoid "price discovery" unless intraday data are added.
- Treat all findings as daily transmission and association unless identification is added.

Required data:

- `Data/Farside ETF Data/`.
- `Data/DefiLlama/ETFs/` as flow validation.
- Artemis ETF AUM files.
- TradingView fund/equity/wrapper files.
- CME basis files already loaded in current panel.

Evidence: `Data/Farside ETF Data/`; `Data/DefiLlama/ETFs/etf-history.csv`; `Data/Artemis/`; `Data/Tradingview/Daily/`; `reports/tables/2026-04-18/etf_flow_regression.csv`.

Required tables and figures:

- Flow source reconciliation table.
- Issuer concentration and AUM composition figure.
- Distributed lag flow-return/flow-volatility table.
- T+0 vs T+1 reporting sensitivity.
- Basis/wrapper response figure.
- Placebo or pre-period falsification where defensible.

Kill risks:

- Same-day flow endogeneity dominates.
- Flow data timing is ambiguous.
- Daily data cannot support stronger mechanism language.
- Issuer-level sample is too short for stable estimates.

## Paper 3 Protocol

Working title: Stablecoins as Shadow Settlement Liquidity.

Category: non-ETF TradFi/crypto bridge.

Question: do stablecoin supply, chain composition, and exchange-flow metrics behave like crypto dollar-liquidity state variables?

Minimum viable design:

- Use DefiLlama daily stablecoin supply as primary aggregate.
- Use Artemis chain/token composition as robustness and decomposition.
- Use CryptoQuant USDT/USDC exchange-flow metrics for native-market checks.
- Use FRED rates and dollar controls.
- Avoid causal monetary language without identification.
- Compare aggregate supply growth, chain/token composition, and exchange-flow indicators.

Required data:

- `Data/DefiLlama/Stablecoins/`.
- `Data/Artemis/Chains - Stablecoin Supply.csv`.
- `Data/Artemis/Stablecoin Supply by Token.csv`.
- `Data/CryptoQuant/USDC/`.
- `Data/CryptoQuant/USDT ETH/`.
- `Data/CryptoQuant/USDT (TRX)/`.
- `Data/FRED/`.

Required tables and figures:

- Stablecoin source reconciliation table.
- Aggregate supply and composition figure.
- Rate/dollar/liquidity regression table.
- CryptoQuant exchange-flow validation table.
- Block horse race against ETF/macro/TVL controls.
- Robustness across DefiLlama vs Artemis definitions.

Kill risks:

- Vendor definitions cannot be reconciled.
- Supply changes are endogenous to crypto returns.
- Chain composition is too sparse or monthly for daily claims.
- Result becomes a generic stablecoin chart without a finance identification question.

## Paper 4 Protocol

Working title: DeFi Credit, Lending, and RWA Rate-Arbitrage Bridge.

Category: non-ETF TradFi/crypto bridge.

Question: are on-chain lending and tokenized asset metrics increasingly connected to TradFi rate, collateral, and liquidity conditions?

Minimum viable design:

- Use weekly panel as default due lending-frequency constraints.
- Use Artemis lending deposits, borrows, and interest fees.
- Use DefiLlama/Artemis RWA series after metadata checks.
- Use FRED short rates, term spread, dollar/risk controls, stablecoin supply, and BTC/ETH market controls.
- Treat RWA results as descriptive if sample is short.
- Keep DeFi yield claims conservative unless direct APR data are added.

Required data:

- `Data/Artemis/Lending Deposits by Protocol.csv`.
- `Data/Artemis/Lending Borrows by Protocol.csv`.
- `Data/Artemis/Lending Interest Fees by Protocol.csv`.
- `Data/DefiLlama/RWA/`.
- `Data/Artemis/RWA - Tokenized Market Cap.csv`.
- `Data/FRED/`.
- Stablecoin controls from DefiLlama/Artemis.

Required tables and figures:

- Lending/RWA coverage and missingness table.
- Weekly rate-sensitivity table.
- RWA growth and composition figure.
- Stablecoin/rate/DeFi credit panel figure.
- Robustness excluding short-history RWA variables.

Kill risks:

- No direct yield/APR data.
- RWA history is too short.
- Protocol-level definitions are unstable.
- Broad crypto beta explains all variation.

## Platform Protocol

The maximum-inventory work should become a shared factor library, not a fifth paper.

Required outputs later:

- Metric dictionary with source, concept, unit, frequency, first/last date, missingness, transformation, primary/robustness role, and paper assignment.
- Source overlap registry.
- Paper-specific panel manifests.
- Diagnostics dashboard or appendix.

Evidence: `Data/MASTER_DATA.csv`; `config/factor_blocks.yml`; `config/calendars.yml`.

