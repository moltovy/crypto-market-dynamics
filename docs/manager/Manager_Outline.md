# Manager Outline

Prepared after local repository audit on 2026-04-16.

## Executive Decision

This repository should be managed as a reproducible empirical research system, not as a collection of notebooks. The cleanest current project direction is a BTC/ETH time-varying factor-evolution paper:

> How did the relative importance of macro / cross-asset, institutional, crypto-liquidity, and native on-chain / ecosystem factors change for BTC and ETH in the post-ETF / institutionalized regime?

The project should use daily data as the main panel, weekly data as the main robustness layer, and event/subperiod designs as supporting evidence. The immediate goal is not to force a final claim. The immediate goal is to build a controlled data and methods foundation that lets the team compare several feasible paper designs without rebuilding the repo each time.

## Current Repository Audit

### Files Reviewed

- `Context/00_project_context_and_goals.md`
- `Context/01_research_framework_and_candidate_pathways.md`
- `Context/02_data_sources_factor_blocks_and_sample_design.md`
- `Context/03_quantitative_methods_and_analysis_menu.md`
- `Context/04_cursor_operating_model_and_agent_workflow.md`
- `Context/05_state_of_the_art_tooling_notes_2026-04-15.md`
- `06_master_meta_prompt_for_grok_4_20_expert.txt`
- `07_manager_model_selection_prompt.txt`
- `08_codex_or_cursor_manager_meta_prompt.txt`
- `crypto_quant_methods_meeting_note.pdf`
- `README.md`
- `tools/organize_cryptoquant_metrics.py`
- `tools/fetch_farside_etf_csv.py`
- `harvest_defillama_simple.py`
- DefiLlama documentation under `docs-master/docs-master`
- Available local CSV inventories under `Data/` and `Defi/`

### Prior Conversation Status

`Grok Convo.txt` is present but empty. There is no prior Grok conversation content to incorporate yet.

### PDF Meeting Note Summary

The PDF confirms the same central design:

- Factor-block framing: macro / cross-asset, institutional, crypto-liquidity, BTC-native, ETH-native.
- Main outputs: rolling correlations, structural break tests, static HAC regressions, rolling OLS, block-level partial R-squared, VAR / Granger / FEVD, event studies, volatility robustness, PCA, connectedness, and clustering.
- Cleanest angle: comparative BTC/ETH factor-evolution study around post-ETF market structure.

### Local Data Inventory Observed

CryptoQuant local exports under `Data/CryptoQuant`:

| Asset | CSV files | Observed coverage | Main categories |
| --- | ---: | --- | --- |
| BTC | 171 | mostly 2009-2026, with one geographical file starting at 2006 zeros | addresses, derivatives, exchange flows, fees, flow indicators, fund data, market data, market indicators, miner flows, network indicators, network stats, supply, transactions |
| ETH | 108 | 2015-2026 | addresses, derivatives, ETH 2.0, exchange flows, fees, fund data, market data, network stats, transactions |
| USDC | 21 | 2018-2026 | addresses, exchange flows, flow indicator, transactions |
| USDT TRX | 14 | 2019-2026 | addresses, exchange flows |
| USDT ETH | 22 | 2017-2026 | addresses, exchange flows, flow indicator, market data, supply, transactions |
| WBTC | 9 | 2018-2026 | addresses, transactions |

Farside ETF data under `Data/Farside ETF Data`:

| Asset | Rows | Date range | Unit |
| --- | ---: | --- | --- |
| BTC spot ETFs | 579 | 2024-01-11 to 2026-04-10 | US$m |
| ETH spot ETFs | 441 | 2024-07-23 to 2026-04-10 | US$m |
| SOL spot ETFs | 12 | 2026-03-25 to 2026-04-10 | US$m |

DefiLlama generated files under `Data/DefiLlama`:

| Dataset | Rows | Date range |
| --- | ---: | --- |
| Daily all-chain TVL | 3,122 | 2017-09-27 to 2026-04-14 |
| Daily chain TVL long | 419,303 | 2017-09-27 to 2026-04-14 |
| Daily chain TVL wide | 3,122 | 2017-09-27 to 2026-04-14 |
| Weekly all-chain TVL | 447 | 2017-10-01 to 2026-04-19 |
| Weekly chain TVL long | 60,392 | 2017-10-01 to 2026-04-19 |
| Weekly chain TVL wide | 447 | 2017-10-01 to 2026-04-19 |
| Current chain snapshot | 440 | snapshot, no date column |
| Current protocol snapshot | 7,317 | snapshot, not a model panel |

Additional root `Defi/` exports:

- `etf-history.csv`: 1,059 rows, 2024-01-11 to 2026-04-14, `total_flow_usd`.
- `etf-overview.csv`: 25 rows, current ETF overview snapshot.
- `dat-institutions.csv`: 86 rows, public-company crypto treasury / DAT snapshot.
- RWA time-series CSVs for active market cap, onchain market cap, and DeFi active TVL, dated 2026-04-14.

### Important Caveats Already Visible

- CryptoQuant files use `Datetime` and appear sorted descending. Canonical panels must parse UTC and sort ascending.
- Farside ETF CSVs use `Date` and units are US$m. DefiLlama ETF history uses USD. These cannot be merged without unit normalization.
- ETF flows are trading-day data. CryptoQuant and DefiLlama are calendar-day data. Weekend and holiday treatment must be explicit.
- Blank Farside cells may mean no flow, not applicable, or pre-listing depending on ticker and date. A listing-date matrix is needed before filling missing values.
- DefiLlama weekly files show week-ending labels. The current weekly files include 2026-04-19 even though source daily data runs through 2026-04-14, so weekly period labeling must be documented.
- RWA files contain both `Timestamp` and `Date`. Parsers should prefer `Date` for human calendar dates and keep `Timestamp` as metadata.
- Some CryptoQuant metrics have very short histories, especially several ETH transaction fields starting around 2025-04-11. These belong in specialized subpanels, not the core model.
- BTC geographical supply starts with zero rows in 2006, before BTC launch. The inventory process must flag implausible starts and non-informative leading zeros.
- The repo has a dirty git state: old tracked `CryptoQuant/` and `Farside ETF Data/` paths appear deleted while `Data/` is untracked. Do not revert this. Treat it as a migration-in-progress that needs a deliberate commit plan later.

## Project System Map

```text
Research question candidates
    -> source inventory and data rights
    -> raw data archive
    -> source-specific cleaned tables
    -> factor dictionary
    -> analytical panels
    -> descriptive diagnostics
    -> baseline econometrics
    -> time-varying and structural-change modules
    -> robustness and support analytics
    -> figures, tables, and paper-ready summaries
    -> professor / reviewer feedback loop
```

Every stage must write artifacts to disk. Chat summaries are not enough.

## Target Research Scope

### Primary Working Paper

**BTC and ETH Factor Evolution After Institutionalization**

Core contribution:

- Build a broad but disciplined factor library.
- Group factors into economically meaningful blocks.
- Estimate how block-level explanatory importance changed over time.
- Compare BTC and ETH rather than treating crypto as one homogeneous asset.
- Study the ETF/institutional era without reducing the whole paper to ETF flows.

### Research Question Selection Gate

Before locking the final paper, the team should generate a short list of 10 feasible paper variants through deep research. Each candidate must be evaluated on:

- data availability and start dates
- clear dependent variable
- clear mechanism
- publishability
- econometric feasibility
- figure/table potential
- risk of becoming a weak predictive/trading paper
- whether BTC and ETH comparison is meaningful
- whether results can survive robustness checks
- whether the professor can quickly understand the contribution

The final project should be selected only after the data inventory and first descriptive diagnostics exist.

### Candidate Designs To Keep Open

1. Main daily factor-evolution paper: daily BTC/ETH returns and volatility explained by factor blocks.
2. Weekly smoothed factor-evolution paper: weekly returns/volatility for noisy DeFi, chain, and ecosystem metrics.
3. ETF-era structural-change paper: pre/post institutionalization with ETF flows as one block, not the whole story.
4. Stablecoin-liquidity paper: stablecoin supply, chain allocation, exchange stablecoin ratios, and crypto market liquidity.
5. ETH ecosystem paper: ETH L1 plus L2 activity, DeFi activity, staking, fees, and ETF flows.
6. Dynamic transmission paper: small VAR/FEVD systems around ETF flows, stablecoins, macro shocks, and BTC/ETH returns.
7. Volatility-generation paper: realized volatility, absolute returns, and downside volatility as dependent variables.
8. Regime mapping paper: macro-dominant vs crypto-native-dominant regimes using rolling betas and clustering.
9. Institutionalization comparison paper: BTC vs ETH differences after their respective ETF launches.
10. Public-treasury / DAT extension: public-company crypto holdings as a secondary institutionalization channel.

These are not separate projects yet. They are controlled options to be evaluated with the same data foundation.

## Factor Block Architecture

### Dependent Variables

Primary:

- BTC daily log return.
- ETH daily log return.

Secondary:

- Weekly BTC and ETH log returns.
- Absolute daily returns.
- Realized volatility over rolling windows.
- Downside semivariance or negative-return volatility.
- Drawdown measures for robustness only.

### Macro / Cross-Asset Block

Likely variables:

- SPY or QQQ returns.
- DXY changes.
- 10Y Treasury yield changes.
- Real-yield proxy if available.
- VIX changes.
- Gold returns.
- Optional: oil, credit spreads, HYG/LQD proxies.

Rules:

- Use changes/returns rather than levels unless there is a clear stationary-level reason.
- Align to market trading days carefully.
- For daily crypto panels, create both calendar-day and market-day variants.

### Institutional Block

Likely variables:

- BTC ETF net flows.
- ETH ETF net flows.
- ETF cumulative flows.
- Flow scaled by market cap, ETF AUM, or rolling volume.
- Issuer concentration shares.
- Coinbase premium / fund premium metrics from CryptoQuant.
- DAT/public-company treasury holdings as a later extension.

Rules:

- Farside flows are in US$m.
- DefiLlama ETF history is in USD.
- ETF data starts late: BTC on 2024-01-11, ETH on 2024-07-23.
- Institutional variables should have short-window modules and should not force the whole project to start in 2024.

### Crypto-Liquidity Block

Likely variables:

- Total stablecoin market cap.
- USDT and USDC growth.
- Stablecoin supply ratio.
- Stablecoin exchange ratios.
- Stablecoin chain allocation.
- Chain TVL.
- DEX volume.
- Protocol / chain fees and revenue.
- Bridge or chain-migration metrics if Artemis/DefiLlama supports them cleanly.

Rules:

- Distinguish stock variables from flow variables.
- Use log changes or growth rates for supply and TVL when appropriate.
- Stablecoin activity on Ethereum, Tron, and other chains should be explicit rather than mixed into one opaque metric.

### BTC-Native Block

Likely variables:

- MVRV.
- SOPR / aSOPR.
- Exchange netflow.
- Exchange reserve.
- Whale ratio.
- Funding rates.
- Open interest.
- Estimated leverage ratio.
- Liquidations.
- Coinbase premium.
- Miner flow and reserve variables.

Rules:

- Avoid dumping all 171 BTC metrics into a regression.
- Start with a small canonical set, then use PCA/screening within block.
- Treat highly overlapping UTXO age/value metrics as dimensionality-reduction candidates.

### ETH-Native / Ecosystem Block

Likely variables:

- ETH active addresses.
- ETH transaction count and contract calls.
- ETH fees and fees burnt.
- Staking rate and total value staked.
- ETH exchange netflow/reserve.
- ETH derivatives metrics.
- Ethereum chain TVL.
- Ethereum L2 activity from Artemis once uploaded.
- L2 fees, active addresses, transactions, TVL, and DEX volumes where available.

Critical point:

ETH L1 active addresses alone may be misleading after L2 adoption. The ETH ecosystem block should maintain separate variables:

- `eth_l1_activity`
- `eth_l2_activity_sum`
- `eth_l1_plus_l2_activity_sum`
- `eth_l2_share_of_eth_ecosystem_activity`

Do not label summed L1/L2 active addresses as unique users unless the source supports cross-chain identity deduplication. Without identity resolution, this is a chain-day activity sum.

## Target Repository Architecture

The repo should migrate toward this structure gradually:

```text
CryptoQuant/
  README.md
  pyproject.toml
  .gitignore
  .env.example

  config/
    project.yml
    sources.yml
    factors.yml
    samples.yml
    chain_taxonomy.yml

  data/
    raw/
      cryptoquant/
      defillama/
      artemis/
      farside/
      fred/
      market/
      manual/
    interim/
    processed/
      factor_library/
      panels/
      diagnostics/
    manifests/
    dictionaries/

  src/cqresearch/
    io/
    ingest/
    transforms/
    panels/
    methods/
    viz/
    validation/
    utils/

  scripts/
    00_inventory_data.py
    01_ingest_cryptoquant.py
    02_ingest_defillama.py
    03_ingest_artemis.py
    04_ingest_farside.py
    05_ingest_macro_market.py
    10_build_factor_library.py
    20_build_panels.py
    30_descriptive_diagnostics.py
    40_static_regressions.py
    50_rolling_models.py
    60_structural_breaks.py
    70_var_fevd.py
    80_support_analytics.py
    90_export_paper_artifacts.py

  notebooks/
    00_scratch/
    01_data_checks/
    02_exploration/

  outputs/
    figures/
    tables/
    run_summaries/
    diagnostics/
    paper_exports/

  docs/
    context/
    methods/
    data_notes/
    decisions/
    deep_research/
    meetings/

  prompts/
    manager/
    agent_tasks/
    deep_research/

  tests/
```

Why this works:

- Raw data is separated from cleaned and analytical data.
- Manifests make the project auditable.
- Config files centralize source, factor, sample, and chain-taxonomy decisions.
- Scripts provide reproducible entry points.
- Notebooks are allowed but cannot become the canonical pipeline.
- Outputs are organized by artifact type for paper drafting.
- Agents can work in parallel because modules have clear ownership boundaries.

### Current-To-Target Mapping

| Current path | Target path |
| --- | --- |
| `Data/CryptoQuant/` | `data/raw/cryptoquant/` |
| `Data/Farside ETF Data/` | `data/raw/farside/` |
| `Data/DefiLlama/` | `data/raw/defillama/generated/` or `data/interim/defillama/` depending on provenance |
| `Defi/` | `data/raw/defillama/manual_exports/2026-04-14/` |
| `docs-master/` | `docs/source_docs/defillama/` or external reference cache |
| `Context/` | `docs/context/` |
| prompt text files | `prompts/manager/` |
| `harvest_defillama_simple.py` | `scripts/02_ingest_defillama.py` plus reusable code in `src/cqresearch/ingest/` |
| `tools/fetch_farside_etf_csv.py` | `scripts/04_ingest_farside.py` |
| `tools/organize_cryptoquant_metrics.py` | `scripts/01_ingest_cryptoquant.py` or one-time migration utility |

Do not perform this migration until the team approves the structure and decides how to handle raw data in git.

## Data Engineering Rules

### Raw Data

- Never edit raw files in place.
- Keep original filenames where possible.
- Store source, download date, script version, and checksum in manifests.
- If raw data is licensed or too large, keep it local and do not commit it.
- Commit only code, configs, dictionaries, and small synthetic fixtures unless data rights are clear.

### Date and Calendar Rules

- Use UTC date as the canonical daily key unless a source has a stronger convention.
- CryptoQuant `Datetime` should be parsed to UTC date.
- Farside ETF data should be treated as trading-day data.
- Macro market data should be treated as trading-day data.
- DefiLlama and Artemis chain metrics should be treated as calendar-day data.
- Build explicit calendars: `calendar_daily`, `market_trading_daily`, `weekly`, and `monthly_end`.

### Missing Data Rules

- Missing because the asset did not exist is not the same as missing because the source failed.
- Missing because an exchange or ETF did not trade is not the same as zero flow.
- Do not blanket forward-fill returns, flows, fees, or active addresses.
- Levels may be forward-filled only when economically valid and documented.
- Every panel must include missingness diagnostics by variable and date.

### Uneven Start Dates

Do not force one universal sample. Use modular samples:

| Sample | Purpose | Likely start |
| --- | --- | --- |
| Core BTC/ETH common sample | Main comparative daily model without ETF-forced short sample | around 2021, subject to audit |
| BTC long-history reduced sample | Historical context with fewer factors | 2017 or earlier if quality allows |
| ETH post-staking / ecosystem sample | ETH native and ecosystem variables | 2020-2021+ |
| BTC ETF sample | BTC institutional block | 2024-01-11+ |
| ETH ETF sample | ETH institutional block | 2024-07-23+ |
| Artemis L2 sample | ETH ecosystem expansion | determined after upload |
| Weekly robustness sample | Smoothed lower-noise design | source-dependent |

### Unit Rules

- Every variable needs a unit in `unit_dictionary.csv`.
- Flows must be normalized before comparison across BTC and ETH.
- Prefer scaled variables for institutional flows: flow / market cap, flow / ETF AUM, flow / spot volume, and flow z-score within window.

## Empirical Architecture

### Baseline Before Complexity

Order of methods:

1. Data inventory and missingness maps.
2. Factor dictionary and transformations.
3. Descriptive charts.
4. Rolling correlations.
5. Static OLS with HAC errors.
6. Subperiod regressions.
7. Rolling OLS.
8. Rolling block-level partial R-squared.
9. Structural break tests.
10. VAR / Granger / FEVD.
11. Weekly/monthly robustness.
12. PCA, clustering, and variable screening.

Do not start with ML. ML is support only.

### Main Regression Form

For asset `a` in BTC and ETH:

```text
y_a,t = alpha + beta_M M_t + beta_I I_a,t + beta_L L_t + beta_N N_a,t + error_t
```

Where:

- `M_t` is macro / cross-asset.
- `I_a,t` is institutional.
- `L_t` is crypto-liquidity.
- `N_a,t` is asset-native / ecosystem.

### Transform Rules

- Prices: log returns.
- Market levels: log changes or returns.
- Yields: changes in basis points.
- VIX: change or log change, with robustness.
- TVL and stablecoin supply: log changes, growth, and level z-scores as separate candidate transforms.
- ETF flows: net flow scaled by AUM/market cap/volume, and unscaled flow as sensitivity.
- Open interest: log change or level scaled by market cap.
- Funding rates: level and change depending on stationarity diagnostics.
- Exchange netflows: scale by market cap, circulating supply, or exchange reserve.
- Fees/revenue: log changes or rolling z-scores.
- Active addresses/transactions: log changes and ecosystem shares.

### Estimation Rules

- Use HAC/Newey-West errors for static daily regressions.
- Pre-register default lag choices before running all variants.
- Use a small number of economically motivated variables per block in baseline models.
- Use PCA or lasso only to screen or summarize within blocks.
- Standardize predictors within sample or rolling window when comparing coefficient magnitude.
- Report both coefficient paths and block-level explanatory shares.
- Keep dynamic systems small. VARs should not include a high-dimensional factor zoo.

## Deep Research LLM Strategy

Deep research tools should be used deliberately, with outputs saved into the repo and treated as external research notes.

Recommended folder:

```text
docs/deep_research/
  2026-04-xx_research_question_portfolio/
    prompt.md
    response.md
    citations.csv
    manager_takeaways.md
  2026-04-xx_literature_map_factor_models/
  2026-04-xx_eth_l2_activity_measurement/
  2026-04-xx_structural_break_best_practices/
  2026-04-xx_cryptoquant_metric_definitions/
```

Use Perplexity Pro for:

- Recent literature search with citations.
- Source discovery.
- Data-provider definitions.
- New papers on BTC/ETH ETFs and market structure.

Use Gemini / Google AI for:

- Long-context synthesis across papers, docs, and notes.
- Building literature matrices.
- Comparing candidate paper designs.

Use Grok as:

- Strategy and operating-model critic.
- Prompt and workflow reviewer.
- Alternative angle generator.

Use Cursor/Codex locally for:

- Code implementation.
- Data inventory.
- Pipeline construction.
- Regression modules.
- Reproducible artifacts.

Rules:

- Never paste API keys or private `.env` values into external tools.
- Treat LLM outputs as leads, not facts.
- Require citations or source links for literature claims.
- Convert useful LLM output into project decisions or tasks.
- Do not let deep research expand the project endlessly. It should narrow options.

## Agent Operating Model

### Lead Manager

One lead agent should own the repository plan, architecture, integration, and acceptance gates. In this environment, that is the role I should play when asked to implement.

Lead responsibilities:

- Maintain the structure.
- Assign work packages.
- Review outputs.
- Prevent duplicate abstractions.
- Keep scripts reproducible.
- Keep data and paper logic aligned.
- Summarize findings and next steps.

### Reviewer / Counterparty

A second frontier model should be used as a reviewer, not as an independent project owner.

Reviewer responsibilities:

- Critique the research design.
- Review data assumptions.
- Review econometric validity.
- Review code diffs.
- Challenge overclaiming.
- Identify missing robustness checks.

### Parallel Agents

Parallel agents are useful only when tasks have clear ownership boundaries.

Good parallel work packages:

- Data inventory and manifest generation.
- CryptoQuant parser and dictionary.
- DefiLlama/Artemis parser and dictionary.
- Farside/FRED/market data ingestion.
- Static regression module.
- Rolling model module.
- Structural break module.
- Figure/table export module.
- Reviewer pass on outputs.

Bad parallel work packages:

- Multiple agents editing the same pipeline file.
- Agents independently inventing folder structures.
- Agents creating overlapping factor names.
- Agents running broad exploratory notebooks without writing artifacts.

### Local vs Remote / Cloud Agents

Use local agents for:

- Raw data.
- API-key workflows.
- Large CSV processing.
- Anything involving licensed source files.
- Final integration.

Use remote/cloud/background agents for:

- Code-only tasks.
- Documentation drafting.
- Unit tests.
- Method scaffolds with synthetic data.
- Review of committed diffs.
- Long-running CI-style checks if the repo is private and data is excluded.

Before using cloud agents, decide:

- What data can be uploaded.
- Whether the GitHub repository is private.
- Whether raw data is gitignored.
- Whether a small synthetic fixture dataset exists for tests.

## Team Workflow

Recommended student split:

- Student 1: data engineering, source inventories, manifests, raw-to-clean pipelines.
- Student 2: econometrics and robustness modules.
- Student 3: literature, research question selection, figures, and paper drafting.

Professor feedback gates:

1. Research question selection.
2. Factor block and sample design.
3. Baseline regression output.
4. Rolling partial R-squared figures.
5. Structural break interpretation.
6. Final paper outline and claims.

Do not wait for professor feedback on basic data cleaning and reproducibility infrastructure.

## Paper Artifact Map

Expected final artifacts:

- Data source table.
- Factor dictionary table.
- Sample coverage table.
- Missingness heatmap.
- Descriptive BTC/ETH price and volatility figure.
- Rolling macro correlation figure.
- Static HAC regression tables.
- Pre/post ETF subperiod tables.
- Rolling coefficient figures.
- Rolling block-level partial R-squared figure.
- Structural break table.
- VAR/FEVD summary table.
- Weekly robustness table.
- ETH L1 vs L2 ecosystem robustness figure.
- Method appendix.
- Data appendix.
- Reproducibility appendix.

## Risks

### Research Risks

- Too many variables and no clear mechanism.
- ETH ecosystem measurement is harder than BTC measurement.
- ETF post periods are short, especially ETH.
- Macro variables do not trade on weekends.
- On-chain variables may be endogenous to price.
- Rolling regressions with too many variables can become unstable.
- Structural break tests can be overinterpreted if break dates are mined.

### Data Risks

- Source definitions differ across CryptoQuant, DefiLlama, Artemis, Farside, and FRED.
- Missingness may be source-driven rather than economically meaningful.
- Units can differ by source.
- Raw data licensing may limit what can be committed.
- Current repo state suggests a migration is underway but not finalized.

### Engineering Risks

- No current `pyproject.toml` or canonical environment file.
- Raw and processed data are not yet cleanly separated.
- Scripts currently write to older root-level paths.
- No automated data inventory exists yet.
- No tests exist yet for date parsing, transformation, or panel integrity.

## Must Do

- Create a canonical data inventory.
- Decide how raw data is stored and whether it is committed.
- Build factor and unit dictionaries before modeling.
- Build separate daily, weekly, and ETF-window panels.
- Use explicit calendars and missingness diagnostics.
- Implement transparent econometrics first.
- Save every figure, table, and run summary.
- Keep notebooks exploratory only.
- Add tests for parsing and panel integrity.

## Nice To Do

- Use R for specific structural break methods if Python support is weak.
- Add Quarto or LaTeX export later for paper production.
- Use DVC or Git LFS if raw data becomes too large or must be versioned.
- Add CI using small synthetic fixtures.
- Add a reviewer-agent checklist for every promoted result.

## Do Not Do

- Do not frame this as a trading strategy.
- Do not make next-day prediction the contribution.
- Do not run black-box ML as the headline result.
- Do not force all variables into one universal panel.
- Do not fill missing values silently.
- Do not commit `.env`.
- Do not let multiple agents edit the same files without ownership rules.
- Do not promote results to the paper without source, sample, and transformation documentation.

## Next Highest-Value Step

The next implementation sprint should create the reproducible foundation:

1. Add `pyproject.toml` or `requirements.txt`.
2. Create the target folders, without moving data yet.
3. Build `scripts/00_inventory_data.py`.
4. Generate `data/manifests/source_files.csv`.
5. Generate `data/manifests/data_inventory.csv`.
6. Create first drafts of `factor_dictionary.csv`, `source_dictionary.csv`, and `unit_dictionary.csv`.
7. Build a minimal BTC/ETH daily price panel.
8. Produce the first missingness and coverage report.
9. Then decide final raw-data migration and git policy.
