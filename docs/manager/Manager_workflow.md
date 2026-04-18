# Manager Workflow

This document defines how the project should be executed from initial setup to paper-ready outputs. It is designed for a three-student MSc Finance team working with a professor and using Cursor/Codex-style agents as implementation partners.

## Operating Principle

Every major task must produce a durable artifact:

- code
- data manifest
- cleaned dataset
- analytical panel
- figure
- table
- run summary
- decision note
- reviewer checklist

If a task only produces chat text, it is not complete.

## Default Tooling Decision

### Primary Language

Use Python as the primary project language.

Reasons:

- Best fit for ingestion, CSV processing, data validation, and reproducible pipelines.
- Strong support for `pandas`, `polars`, `numpy`, `statsmodels`, `scikit-learn`, `matplotlib`, `seaborn`, and `plotly`.
- Easier for Cursor/Codex agents to maintain across data engineering and econometrics.
- Easier to integrate with file manifests and test scripts.

### Optional R

Use R only if it adds clear value for a specific econometric method, especially:

- Bai-Perron / multiple structural breaks.
- `strucchange`-style diagnostics.
- specialized VAR/connectedness packages.

If R is used, keep it in `scripts/r/` and make it consume the same processed panels as Python. Do not create a parallel R data pipeline.

### Notebooks

Notebooks are allowed for exploration, but scripts are canonical.

Rules:

- Notebooks should read from `data/processed/` or `data/interim/`, not raw source folders.
- Notebooks should not contain the only copy of a transformation.
- Any result used in the paper must be reproducible from a script.

## Target Execution Phases

### Phase 0 - Governance and Repo Baseline

Goal:

Create the minimum structure needed for reproducible work and parallel agents.

Deliverables:

- `pyproject.toml` or `requirements.txt`
- `.env.example`
- target folder skeleton
- `config/project.yml`
- `config/sources.yml`
- `config/factors.yml`
- `config/samples.yml`
- `config/chain_taxonomy.yml`
- updated `.gitignore`
- `docs/decisions/0001_repo_operating_model.md`

Acceptance criteria:

- A new team member can see where raw data, processed data, outputs, docs, and scripts belong.
- `.env` remains ignored.
- Raw data commit policy is explicit.
- The repo can run at least one simple Python command in a controlled environment.

### Phase 1 - Data Intake Protocol

Goal:

Create a repeatable process for adding DefiLlama, Artemis, CryptoQuant, Farside, FRED, and market data.

Raw upload convention:

```text
data/raw/{source}/{YYYY-MM-DD}/
```

Examples:

```text
data/raw/cryptoquant/2026-04-12/
data/raw/defillama/manual_exports/2026-04-14/
data/raw/artemis/2026-04-xx/
data/raw/farside/2026-04-10/
```

Each raw upload should include or generate:

- original files
- `README_source.md`
- source URL or export description
- export date
- account/subscription used, if relevant
- unit notes
- coverage notes
- checksum manifest

Acceptance criteria:

- No raw file is edited in place.
- Every raw file has source, date, and checksum metadata.
- The project can tell whether a new upload changed the data.

### Phase 2 - Source Inventory

Goal:

Build source-level visibility before analysis.

Script:

```text
scripts/00_inventory_data.py
```

Outputs:

```text
data/manifests/source_files.csv
data/manifests/data_inventory.csv
data/manifests/data_quality_flags.csv
outputs/run_summaries/00_inventory_data_YYYY-MM-DD.md
```

Required inventory columns:

- `source`
- `raw_path`
- `file_name`
- `file_size_bytes`
- `sha256`
- `detected_date_column`
- `min_date`
- `max_date`
- `row_count`
- `column_count`
- `columns`
- `asset`
- `category`
- `frequency_guess`
- `unit_guess`
- `quality_flags`

Known flags to detect immediately:

- implausible start dates
- duplicate dates
- descending sort order
- all-zero leading periods
- missing date column
- mixed date formats
- empty files
- columns with all missing values
- columns with non-numeric values where numeric is expected

Acceptance criteria:

- Inventory covers all current `Data/`, `Defi/`, and future `data/raw/` files.
- BTC/ETH price files are recognized.
- Farside flow files are recognized with units US$m.
- DefiLlama ETF history is recognized with units USD.
- The 2006 BTC geographical-supply zero history is flagged.
- RWA files prefer `Date` over `Timestamp` for calendar date.

### Phase 3 - Data Dictionaries

Goal:

Create explicit metadata before building panels.

Files:

```text
data/dictionaries/source_dictionary.csv
data/dictionaries/unit_dictionary.csv
data/dictionaries/factor_dictionary.csv
```

`factor_dictionary.csv` should include:

- `factor_id`
- `source`
- `raw_file`
- `raw_column`
- `asset`
- `factor_block`
- `sub_block`
- `economic_concept`
- `raw_unit`
- `canonical_unit`
- `frequency`
- `transform_default`
- `transform_alternatives`
- `expected_sign_if_any`
- `start_date`
- `end_date`
- `include_baseline`
- `include_screening_pool`
- `notes`

Initial baseline factor count should be small:

- 5-8 macro factors.
- 3-6 institutional factors per asset.
- 5-10 crypto-liquidity factors.
- 6-10 BTC-native factors.
- 6-10 ETH-native/ecosystem factors.

Acceptance criteria:

- Every baseline variable has a factor block.
- Every baseline variable has a documented transformation.
- Variables with short histories are tagged as specialized, not core.
- Factor names are stable and machine-friendly.

### Phase 4 - Source-Specific Cleaned Tables

Goal:

Convert raw files into clean, source-specific interim tables.

Scripts:

```text
scripts/01_ingest_cryptoquant.py
scripts/02_ingest_defillama.py
scripts/03_ingest_artemis.py
scripts/04_ingest_farside.py
scripts/05_ingest_macro_market.py
```

Outputs:

```text
data/interim/cryptoquant/
data/interim/defillama/
data/interim/artemis/
data/interim/farside/
data/interim/macro/
```

Rules:

- Parse dates to canonical `date`.
- Keep original source date column as metadata if needed.
- Sort ascending.
- Standardize column names.
- Convert units explicitly.
- Do not impute at this stage.
- Preserve source-specific identifiers.

Acceptance criteria:

- Each source has a cleaned long-format table where practical.
- Each table has `date`, `source`, and stable variable identifiers.
- Date ranges match the manifest.
- Unit conversions are documented.

### Phase 5 - Factor Library Construction

Goal:

Build transformed variables from cleaned source tables.

Script:

```text
scripts/10_build_factor_library.py
```

Outputs:

```text
data/processed/factor_library/factors_daily_long.csv
data/processed/factor_library/factors_daily_wide.csv
data/processed/factor_library/factors_weekly_long.csv
data/processed/factor_library/factors_weekly_wide.csv
data/processed/diagnostics/factor_missingness.csv
data/processed/diagnostics/factor_coverage.csv
```

Transform standards:

- Prices -> log returns.
- TVL/supply/market cap -> log change and level z-score candidates.
- Flows -> scaled flow and z-score candidates.
- Yields -> basis-point changes.
- VIX -> change and percent change candidates.
- Funding -> levels and changes.
- Fees/revenue -> log change and rolling z-score candidates.
- Active addresses/transactions -> log change and share variables.

Acceptance criteria:

- No transformation is silent.
- Every factor maps back to a raw source.
- No factor has unexamined large missingness.
- Outlier flags exist for extreme values.

### Phase 6 - Analytical Panels

Goal:

Create model-ready panels with explicit sample definitions.

Script:

```text
scripts/20_build_panels.py
```

Required panels:

| Panel | Purpose |
| --- | --- |
| `btc_eth_daily_core.csv` | main BTC/ETH daily model without ETF-forced short sample |
| `btc_daily_long_reduced.csv` | BTC historical context |
| `eth_daily_ecosystem.csv` | ETH native plus L2/Artemis variables when available |
| `btc_etf_daily.csv` | BTC ETF-era institutional sample |
| `eth_etf_daily.csv` | ETH ETF-era institutional sample |
| `btc_eth_weekly_core.csv` | weekly robustness |
| `btc_eth_monthly_context.csv` | slow-variable context only |

Each panel must include:

- panel name
- sample start
- sample end
- inclusion rules
- variables included
- missingness summary
- dependent variable definition
- calendar type
- generated timestamp

Acceptance criteria:

- No model script builds its own sample ad hoc.
- Every result can point to one panel file.
- Daily and weekly panels are separately validated.

### Phase 7 - Descriptive Diagnostics

Goal:

Understand the data before formal modeling.

Script:

```text
scripts/30_descriptive_diagnostics.py
```

Required diagnostics:

- BTC/ETH price and return plots.
- Volatility plots.
- Factor coverage heatmap.
- Missingness heatmap.
- Correlation heatmaps by sample.
- Rolling correlations with SPY/QQQ, DXY, VIX, gold, and yields.
- Stablecoin and TVL overview.
- ETF flow overview.
- ETH L1 vs L2 activity overview after Artemis upload.

Acceptance criteria:

- Diagnostics identify which variables are plausible baseline candidates.
- Diagnostics identify which variables are too sparse or too short.
- No regression is run before coverage and missingness are visible.

### Phase 8 - Static Baseline Econometrics

Goal:

Estimate interpretable baseline relationships.

Script:

```text
scripts/40_static_regressions.py
```

Required models:

- BTC core daily.
- ETH core daily.
- BTC ETF-era daily.
- ETH ETF-era daily.
- Weekly core robustness.
- Volatility dependent-variable variants.

Rules:

- OLS with HAC/Newey-West errors.
- Report coefficient, standard error, t-stat, p-value, adjusted R-squared, sample dates, observations.
- Include factor-block labels in outputs.
- Run pre/post subperiods only where sample size supports it.

Acceptance criteria:

- Tables are reproducible from panel files.
- HAC lag choices are documented.
- Results do not claim causality.
- Multicollinearity diagnostics are reported.

### Phase 9 - Rolling Models and Partial R-Squared

Goal:

Quantify time-varying exposure and block-level explanatory importance.

Script:

```text
scripts/50_rolling_models.py
```

Default windows:

- 90 days for responsiveness.
- 180 days for main stability.
- 365 days for robustness where data length allows.

Use 60-day windows only as exploratory diagnostics because multi-factor regressions can become unstable in short windows.

Block-level partial R-squared:

```text
partial_r2_block = r2_full - r2_without_block
```

Also consider adjusted R-squared sensitivity for models with different block sizes.

Acceptance criteria:

- Rolling outputs include coefficient paths and confidence bands where feasible.
- Partial R-squared is computed consistently across BTC and ETH.
- Windows with insufficient observations are dropped and logged.
- Main figure is legible and paper-ready.

### Phase 10 - Structural Break Testing

Goal:

Test whether relationships changed statistically.

Script:

```text
scripts/60_structural_breaks.py
```

Candidate tests:

- Chow tests at pre-specified dates.
- CUSUM / recursive residual stability.
- Bai-Perron multiple break tests if implementation is reliable.

Pre-specified dates:

- BTC ETF launch: 2024-01-11.
- ETH ETF launch: 2024-07-23.
- BTC halving: 2024-04-20.
- Major stress windows selected only after literature/source review.

Acceptance criteria:

- Pre-specified and data-driven breaks are separated.
- Break tests state dependent variable and model specification.
- Results are not overclaimed as causal event effects.

### Phase 11 - VAR / Granger / FEVD

Goal:

Study small-system dynamics and shock transmission.

Script:

```text
scripts/70_var_fevd.py
```

Good systems:

- BTC return, BTC ETF flow, stablecoin growth, VIX change.
- ETH return, ETH ETF flow, ETH fees/TVL growth, VIX change.
- BTC return, ETH return, stablecoin growth, DXY/VIX.

Rules:

- Keep systems small.
- Use stationary transformations.
- Select lag length transparently.
- Report Granger tests, impulse responses, and FEVD.
- Treat VAR as support, not the main paper engine.

Acceptance criteria:

- Variables pass stationarity/transform checks.
- Lag selection is documented.
- Outputs are interpretable and not overfit.

### Phase 12 - Robustness

Goal:

Stress-test the main claims.

Script:

```text
scripts/80_robustness.py
```

Robustness layers:

- Weekly panels.
- Monthly context where sensible.
- Alternative transformations.
- Alternative rolling windows.
- Alternative ETF flow scaling.
- Excluding extreme stress windows.
- BTC-only long sample.
- ETH L1-only vs ETH L1+L2 ecosystem definitions.
- Baseline variables vs PCA block factors.

Acceptance criteria:

- Robustness supports or clearly limits the main claim.
- Failed robustness checks are documented.
- No result enters the paper if it only works under one fragile transformation.

### Phase 13 - Support Analytics

Goal:

Use ML-style tools for disciplined support tasks.

Script:

```text
scripts/85_support_analytics.py
```

Allowed:

- PCA within factor blocks.
- Sparse PCA if useful.
- Clustering on rolling correlations or rolling betas.
- Lasso/elastic net for variable screening.
- Random forest/boosting only for contemporaneous nonlinear diagnostics.
- SHAP only as exploratory interpretation, not headline evidence.

Not allowed:

- Predictive trading framing.
- Next-day return forecast paper.
- Black-box model as the central contribution.

Acceptance criteria:

- Support analytics explain or simplify the baseline.
- ML outputs do not replace econometric evidence.
- Variable screening decisions are recorded in a decision note.

### Phase 14 - Paper Artifact Export

Goal:

Generate clean outputs for drafting.

Script:

```text
scripts/90_export_paper_artifacts.py
```

Required artifacts:

- source coverage table
- factor dictionary table
- sample construction table
- missingness figure
- static regression tables
- rolling correlation figures
- rolling coefficient figures
- rolling partial R-squared figure
- structural break table
- VAR/FEVD appendix table
- robustness summary table
- result interpretation memo

Acceptance criteria:

- Every figure/table has a script source.
- Every figure/table has a panel source.
- Every promoted result has a caveat note.
- Outputs are professor-readable without opening code.

## Calendar and Missingness Policy

Use three daily variants:

1. `calendar_daily`: all UTC calendar days.
2. `market_day_daily`: NYSE-style trading days for macro/ETF alignment.
3. `hybrid_daily`: calendar days with explicit non-trading indicators.

Main macro regressions should start with `market_day_daily`. Crypto-native models can use `calendar_daily`. Weekly robustness should be used to reduce calendar mismatch.

Crypto trades on weekends. ETF and macro variables generally do not.

Acceptable approaches:

- Market-day panel: drop weekends for models requiring macro/ETF variables.
- Weekly panel: aggregate daily variables to weekly.
- Hybrid panel: include weekend indicators and avoid carrying forward returns/flows.

Unacceptable approaches:

- Blindly forward-filling equity returns.
- Treating every missing ETF value as zero without a trading calendar and listing-date logic.
- Mixing calendar and trading-day samples without documenting it.

Missing values must be categorized:

- pre-existence missing
- source unavailable
- market closed
- true zero
- not applicable
- failed parse
- unknown

## Artemis Upload Protocol

When Artemis data is uploaded locally:

1. Put original files under `data/raw/artemis/YYYY-MM-DD/`.
2. Do not rename originals unless needed for filesystem safety.
3. Add `README_source.md` describing export source, filters, date, metric definitions, and account context.
4. Run the inventory script.
5. Build an Artemis source dictionary.
6. Define chain taxonomy before aggregation.

### ETH L2 Aggregation Rules

Create `config/chain_taxonomy.yml` before using L2 data.

Minimum fields:

- `chain`
- `chain_slug`
- `ecosystem`
- `is_ethereum_l2`
- `is_rollup`
- `settlement_layer`
- `include_in_eth_core`
- `include_in_eth_broad`
- `notes`

Separate outputs:

- Ethereum L1 only.
- Ethereum canonical L2 sum.
- Ethereum broad ecosystem sum.
- L2 share of ecosystem.

Do not claim unique ecosystem users unless Artemis provides cross-chain deduplicated addresses.

## Deep Research Workflow

Deep research outputs should be saved, not just read.

Folder convention:

```text
docs/deep_research/YYYY-MM-DD_topic/
  prompt.md
  response.md
  citations.csv
  manager_takeaways.md
  decisions_or_tasks.md
```

### Inquiry 1 - Ten Feasible Paper Designs

Ask a deep research model to propose 10 publishable, feasible crypto market-structure paper designs using BTC/ETH, CryptoQuant, DefiLlama, Artemis, Farside, FRED, and market data.

Required evaluation columns:

- title
- research question
- dependent variable
- key factor blocks
- data sources
- sample frequency
- likely sample start
- main methods
- expected figures/tables
- feasibility
- novelty
- risk
- why it is not a trading/prediction paper

### Inquiry 2 - Literature Map

Map recent literature on BTC/ETH factor models, ETF flows, institutionalization, stablecoin liquidity, crypto-macro linkage, and on-chain indicators.

Required output:

- paper citation
- data
- methods
- variables
- findings
- limitations
- relevance to this project

### Inquiry 3 - ETH L2 Measurement

Determine best-practice measurement of ETH ecosystem activity after L2 migration.

Required output:

- which L2s to include
- how to avoid double counting
- active-address caveats
- fees/transactions/TVL alternatives
- recommended robustness variants

### Inquiry 4 - Econometric Design Review

Review rolling OLS, rolling partial R-squared, structural breaks, HAC, VAR/FEVD, and weekly robustness for this type of crypto panel.

Required output:

- recommended default specs
- failure modes
- diagnostics
- minimum sample sizes
- reviewer concerns

### Inquiry 5 - Data Source Definitions

Audit definitions and caveats for CryptoQuant, DefiLlama, Artemis, Farside, and FRED variables.

Required output:

- source
- metric
- exact definition
- unit
- frequency
- known caveats
- citation/source URL

## Agent Delegation Workflow

Agents are bounded workers, not independent project owners. The manager defines:

- objective
- owned files
- inputs
- outputs
- acceptance criteria
- constraints

The manager integrates and reviews.

### Local Cursor/Codex Agent

Best for:

- reading local raw data
- implementing scripts
- running pipelines
- creating figures/tables
- debugging
- maintaining repo structure

### Reviewer Agent

Best for:

- critiquing code changes
- checking econometric assumptions
- reviewing factor definitions
- finding missing tests
- challenging paper claims

### Background/Cloud Agent

Best for:

- code-only refactors
- docs cleanup
- tests against synthetic fixtures
- method module scaffolding
- independent review of committed diffs

Avoid cloud/background agents for:

- `.env` or API keys
- licensed raw data
- uncommitted private source files
- large local-only datasets unless explicitly approved

### Parallel Task Design

Good parallel work packages:

| Agent | Owned files | Task |
| --- | --- | --- |
| Data inventory agent | `scripts/00_inventory_data.py`, `src/cqresearch/io/` | build manifests and quality flags |
| CryptoQuant agent | `scripts/01_ingest_cryptoquant.py`, `src/cqresearch/ingest/cryptoquant.py` | parse CryptoQuant files |
| DefiLlama/Artemis agent | `scripts/02_ingest_defillama.py`, `scripts/03_ingest_artemis.py` | parse ecosystem data |
| Factor dictionary agent | `data/dictionaries/*`, `config/factors.yml` | map variables to blocks |
| Econometrics agent | `src/cqresearch/methods/`, `scripts/40_*`, `scripts/50_*` | implement models |
| Visualization agent | `src/cqresearch/viz/`, `scripts/90_*` | paper-ready figures |
| Reviewer agent | no writes, or `docs/reviews/` only | critique outputs |

Bad task prompt:

```text
Analyze the project and build everything.
```

Good task prompt:

```text
Implement scripts/00_inventory_data.py and src/cqresearch/io/inventory.py only.
Inputs: current Data/, Defi/, and future data/raw/.
Outputs: data/manifests/source_files.csv, data/manifests/data_inventory.csv, data/manifests/data_quality_flags.csv.
Acceptance criteria: detect date columns, row counts, date ranges, sha256, source guesses, frequency guesses, and quality flags. Do not move raw files. Do not edit other modules.
```

## Git and Collaboration Rules

Immediate policy:

- Do not commit `.env`.
- Do not commit raw data until data rights and size policy are decided.
- Keep code, configs, docs, and small test fixtures in git.
- Use branches for major work packages once the repo is stabilized.
- Do not let agents edit the same files simultaneously.

Recommended future policy:

- Use a private GitHub repository for code, configs, docs, prompts, manifests, synthetic fixtures, and paper artifacts if allowed.
- Keep raw data local unless licensing and size make Git LFS or DVC clearly worthwhile.
- Use remote/cloud agents only on code-safe branches or synthetic fixtures unless explicitly approved.

## Visualization Standards

Primary plotting stack:

- `matplotlib`
- `seaborn`
- optional `plotly` for exploratory interactive charts only

Paper figure outputs:

- `.png` at high DPI for drafts
- `.pdf` or `.svg` for final vector figures where possible
- source CSV for each figure if useful

Rules:

- Every figure needs title, axis labels, units, sample dates, and source note.
- Rolling figures must show window size.
- ETF launch markers must use exact dates.
- Do not overload one chart with too many lines.
- Use consistent colors for factor blocks.

Recommended factor-block colors:

- Macro / cross-asset: blue
- Institutional: green
- Crypto-liquidity: orange
- BTC-native: gray
- ETH-native/ecosystem: purple

## Result Promotion Checklist

A result can enter the paper only if:

- source data is identified
- unit is documented
- transformation is documented
- sample start/end are documented
- missingness is acceptable or explained
- regression spec is reproducible
- diagnostic output exists
- robustness check exists or limitation is stated
- reviewer pass is complete
- claim does not imply causality unless design supports it

## First Implementation Sprint

Do this next, in order:

1. Create folder skeleton and environment file.
2. Build `scripts/00_inventory_data.py`.
3. Run inventory on current `Data/`, `Defi/`, and root reference files.
4. Write `data/manifests/source_files.csv`.
5. Write `data/manifests/data_inventory.csv`.
6. Write `data/manifests/data_quality_flags.csv`.
7. Create initial dictionaries under `data/dictionaries/`.
8. Build minimal BTC/ETH price panel.
9. Generate first coverage and missingness report.
10. Decide raw-data git policy and migration plan.

The first sprint is successful when the team can answer:

- What data do we have?
- What dates does it cover?
- What units are used?
- Which variables are baseline candidates?
- Which variables are too short or too messy?
- What exact panel will the first regression use?

## Manager Cadence

For every major step, the manager should produce:

1. Plan.
2. Code changes.
3. Run output.
4. Saved artifacts.
5. Findings summary.
6. Risks and ambiguities.
7. Next highest-value step.

Weekly team rhythm:

- Day 1: data/pipeline progress.
- Day 2: diagnostics and figures.
- Day 3: econometric modules.
- Day 4: robustness and review.
- Day 5: professor-facing summary and next decisions.

This cadence can compress or expand, but the artifact discipline should not change.
