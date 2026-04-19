# Current Status Analysis

Audit date: 2026-04-18  
Repository: `C:\Dev\Projects\CryptoQuant`  
Reviewer stance: skeptical principal research engineer / quantitative finance reviewer / codebase auditor.

## Executive Judgment

**Verified.** The repository has moved beyond a planning-only state. It now contains a real Python package under `src/cqresearch`, analysis scripts, configs, a generated master panel, tables, figures, run summaries, a draft paper, tests, and a large normalized data inventory. The working direction is coherent: BTC/ETH factor exposure evolution around the January 2024 spot-ETF regime shift, with ETF flows, macro/TradFi variables, stablecoins, liquidity, and on-chain metrics as factor blocks. Evidence: `AGENTS.md`, `project_research_plan.md`, `config/factor_blocks.yml`, `config/events.yml`, `Data/MASTER_DATA.md`, `reports/run_summaries/03_run_analyses.md`, `reports/drafts/paper_v0.1_2026-04-18.md`, `src/cqresearch/`.

**Verified.** The repo is not yet publication-grade. It has a credible v0.1 analysis pipeline, but several headline claims in the paper/spec are stronger than what the current implementation supports. The largest gaps are: true Bai-Perron multiple-break evidence is not implemented; block partial R2 is not the Shapley/block decomposition described in the specs; calendar/fill handling conflicts with config intent; ETF flow intensity has weak economic units; tests are thin; and figures are diagnostic, not paper-ready. Evidence: `docs/specs/methods_spec.md`, `src/cqresearch/modeling/structural_breaks.py`, `src/cqresearch/modeling/rolling.py`, `src/cqresearch/features/panel.py`, `src/cqresearch/data/calendars.py`, `config/calendars.yml`, `tests/`, `reports/figures/2026-04-18/`.

**Inference.** The strongest defensible near-term project is still the ETF/institutionalization paper, but it should be framed more conservatively: "how BTC/ETH factor exposures and transmission diagnostics changed around ETF institutionalization" rather than "ETFs caused a new volatility regime." The current evidence is better suited to descriptive structural-break/factor-exposure diagnostics than to causal claims.

## Evidence Base Reviewed

**Canonical project/control files.**

- `AGENTS.md`
- `project_research_plan.md`
- `README.md`
- `HANDOFF.md`
- `pyproject.toml`
- `run_pipeline.py`
- `.cursor/rules/*.mdc`

**Context, manager, and spec documents.**

- `docs/context/00_project_context_and_goals.md`
- `docs/context/01_data_sources_and_variable_blocks.md`
- `docs/context/02_data_strategy_and_sample_design.md`
- `docs/context/03_quantitative_methods_and_analysis_menu.md`
- `docs/context/04_deliverables_and_agent_workflow.md`
- `docs/context/05_state_of_tooling_and_literature_suggestions.md`
- `docs/manager/Manager_Outline.md`
- `docs/manager/Manager_workflow.md`
- `docs/specs/research_spec.md`
- `docs/specs/methods_spec.md`
- `docs/specs/data_spec.md`

**Data, configs, code, and generated outputs.**

- `Data/MASTER_DATA.md`
- `Data/MASTER_DATA.csv`
- `config/factor_blocks.yml`
- `config/events.yml`
- `config/calendars.yml`
- `config/chain_taxonomy.yml`
- `src/cqresearch/`
- `scripts/`
- `reports/panels/`
- `reports/run_summaries/`
- `reports/tables/2026-04-18/`
- `reports/figures/2026-04-18/`
- `reports/drafts/paper_v0.1_2026-04-18.md`
- `tests/`

**Prior AI / previous synthesis outputs.**

- `Latest Output.txt`
- `reports/prior_ai_outputs/Beyond Correlation_ Quantifying Bitcoin's New Role in Financial Markets Through Structural Breaks, Flow Dynamics, and Systemic Risk.md`
- `reports/prior_ai_outputs/Crypto Research Agenda Development.md`
- `reports/prior_ai_outputs/deep-research-report.md`
- `reports/prior_ai_outputs/FINAL_SYNTHESIS_TOP5_PROJECTS.md`
- `reports/prior_ai_outputs/research_memo.md`
- `reports/prior_ai_outputs/txt output p2.md`
- `reports/prior_ai_outputs/txt output.md`

**References.**

- `references/FinancialEconometrics-master/FinancialEconometrics-master/`
- `references/cursor-ai-tips-main/cursor-ai-tips-main/`
- `references/awesome-cursor-skills-main/awesome-cursor-skills-main/`

## Repository Contents

**Verified.** The current top-level layout is materially more mature than the older manager docs imply. The repository contains:

- Project constitution and roadmap: `AGENTS.md`, `project_research_plan.md`, `README.md`, `HANDOFF.md`.
- Configs: `config/factor_blocks.yml`, `config/events.yml`, `config/calendars.yml`, `config/chain_taxonomy.yml`.
- Data inventory and source files: `Data/MASTER_DATA.md`, `Data/MASTER_DATA.csv`, and vendor subfolders under `Data/`.
- Research package: `src/cqresearch/` with data loading, calendar alignment, panel construction, feature transforms, OLS, rolling diagnostics, structural-break utilities, VAR/FEVD, event study, and visualization style modules.
- Execution scripts: `scripts/01_build_master_panel.py` through `scripts/05_robustness.py`, plus `scripts/run_full_pipeline.py`.
- Generated analysis outputs: `reports/panels/`, `reports/tables/2026-04-18/`, `reports/figures/2026-04-18/`, `reports/run_summaries/`, and `reports/drafts/paper_v0.1_2026-04-18.md`.
- Tests: `tests/`, currently focused on imports, config validity, and basic fixtures.
- Prior AI outputs: `reports/prior_ai_outputs/` and untracked `Latest Output.txt`.
- Workflow/method references: `references/`.

**Verified.** `CODEX/` existed and was empty before this audit output was written. `git status --short` showed only `?? "Latest Output.txt"` before the `CODEX/` files were created. That untracked status matters: `Latest Output.txt` should be treated as useful prior output but not canonical project state.

## What Is Well Structured

**Verified.** The mission is unusually clear for a research repo. `AGENTS.md` defines one non-negotiable paper target: BTC/ETH factor exposures around the January 2024 spot-ETF structural break, with rolling OLS + block partial R2 as the headline diagnostic, break tests for formal evidence, and compact VAR/FEVD for dynamic transmission. `project_research_plan.md` reinforces the same direction.

**Verified.** The project has a reasonable separation between mission, configs, data inventory, source code, execution scripts, generated outputs, and prior AI material:

- `config/factor_blocks.yml` gives a canonical five-block variable taxonomy.
- `config/events.yml` records pre-registered event dates.
- `Data/MASTER_DATA.md` provides broad source coverage and row/date summaries.
- `src/cqresearch/` isolates reusable logic from one-off scripts.
- `reports/run_summaries/` records executed pipeline outputs.
- `reports/prior_ai_outputs/` keeps earlier generated research material separate from current outputs.

**Verified.** The data inventory is strong enough to support serious work. `Data/MASTER_DATA.md` reports 484 CSV files and about 1.81 million rows across AlternativeMe, Artemis, CryptoQuant, DefiLlama, FRED, Farside ETF Data, and TradingView. That source mix can support macro, ETF, liquidity, stablecoin, on-chain, exchange, and market-structure blocks.

**Verified.** The current v0.1 pipeline produced tangible artifacts rather than only plans:

- `reports/panels/master_daily.parquet`
- `reports/panels/master_daily_coverage.csv`
- `reports/panels/master_daily_meta.json`
- `reports/tables/2026-04-18/`
- `reports/figures/2026-04-18/`
- `reports/run_summaries/01_inspect_core_files.md`
- `reports/run_summaries/02_build_master_panel.md`
- `reports/run_summaries/03_run_analyses.md`
- `reports/drafts/paper_v0.1_2026-04-18.md`

**Inference.** The codebase has crossed the threshold where the central risk is no longer "can we build anything?" The risk is now "are the labels, interpretation, and econometric claims disciplined enough for a defensible empirical-finance paper?"

## Weak Structure, Architecture, and Naming

**Verified.** There are two pipeline concepts that are not reconciled:

- `run_pipeline.py` appears to be the curation/inventory-oriented root pipeline.
- `scripts/run_full_pipeline.py` appears to run the current research/report pipeline.

`.cursor/rules/global-constitution.mdc` says all pipeline entry points should go through `run_pipeline.py`, but current research execution lives in `scripts/run_full_pipeline.py`. This is an architecture and workflow contradiction.

**Verified.** Specs are not yet sufficiently populated to act as binding implementation contracts. `docs/specs/research_spec.md`, `docs/specs/methods_spec.md`, and `docs/specs/data_spec.md` define useful intent, but the implemented code only partially matches them. The specs are closer to design targets than completed contracts.

**Verified.** Several analysis scripts hardcode project-critical choices that already exist in YAML configs. Examples include break dates, model factor lists, event choices, and calendar behavior in `scripts/02_run_analyses.py`, `scripts/04_descriptives_and_summaries.py`, and related scripts. `config/events.yml`, `config/factor_blocks.yml`, and `config/calendars.yml` should be the source of truth, but the current scripts do not consistently consume them.

**Verified.** Test coverage is too thin for the size of the claims. The repo has tests under `tests/`, but they mostly check imports, fixtures, and config parseability. They do not yet validate the math or data semantics behind structural breaks, rolling R2, event windows, calendar filling, ETF flow units, stablecoin aggregation, or table regeneration.

**Verified.** Naming around "partial R2", "block R2", and "Bai-Perron" is too loose. Current outputs can be useful diagnostics, but labels should distinguish:

- variable-drop partial R2,
- single-block standalone R2,
- Shapley/Owen-style block contribution,
- single unknown-break sup-F,
- true multiple-break Bai-Perron.

Those are not interchangeable.

## Major Contradictions and Misalignments

### Python Environment

**Verified.** `AGENTS.md` says Python 3.11+ is required and dependencies are managed by `uv`. `pyproject.toml` allows `requires-python = ">=3.10"`, and `HANDOFF.md` reports the active interpreter as Python 3.10.0. This should be resolved before the project is treated as reproducible.

### Break Evidence

**Verified.** The mission/spec asks for Bai-Perron plus Chow evidence. `src/cqresearch/modeling/structural_breaks.py` implements `chow_test`, `sup_f_sweep`, and `placebo_breaks`; its own docstring says the sup-F sweep approximates the Bai-Perron single-break case without dynamic-programming search for `k` unknown breaks. Therefore the current code does not implement true Bai-Perron multiple-break estimation.

**Implication.** The paper can say "Chow plus single-break sup-F diagnostic" today. It should not claim full Bai-Perron evidence unless that method is implemented and validated.

### Block Partial R2

**Verified.** `docs/specs/methods_spec.md` describes Shapley partial R2 and block-level attribution. Current rolling diagnostics in `src/cqresearch/modeling/rolling.py` and summary code in `scripts/04_descriptives_and_summaries.py` are simpler diagnostics. The block table appears closer to standalone block R2, and the rolling partial stacks appear closer to variable-drop partial contributions aggregated by block.

**Implication.** The current diagnostic is useful but should be labeled conservatively until the intended decomposition is implemented.

### Calendar and Fill Rules

**Verified.** `config/calendars.yml` emphasizes no forward fill for major daily calendars, with specific handling for ETF flows. Current code in `src/cqresearch/data/calendars.py` uses a hardcoded default forward-fill behavior, and `HANDOFF.md` says equity/macro series are forward-filled up to four days. Current flow alignment may also zero-fill missing flow observations within active windows. This is a substantive data-construction issue, not just a formatting detail.

**Implication.** Weekend and holiday handling can mechanically create zero returns/diffs or zero ETF flows. That affects daily regressions, event windows, Chow tests, and VAR dynamics. It needs an explicit design decision and tests.

### ETF Flow Intensity Units

**Verified.** `src/cqresearch/features/panel.py` comments say ETF flow intensity should be flow over prior-day market cap, but the actual implemented formula is `btc_etf_total / btc_close.shift(1)` and `eth_etf_total / eth_close.shift(1)`. The code comment acknowledges this is actually flow per unit price because circulating supply is absent from the panel.

**Implication.** Coefficients on ETF intensity are not clean "flow share of market cap" coefficients. The feature may be stationary and useful, but economic interpretation should be narrow.

### Manager Docs Versus Current Repo

**Verified.** `docs/manager/Manager_Outline.md` and `docs/manager/Manager_workflow.md` are useful workflow references but are partially stale. They refer to older paths and an earlier project state, including pre-pipeline scaffolding assumptions. The current repository already has `pyproject.toml`, config files, source modules, reports, and draft outputs.

**Implication.** The manager docs should be treated as planning history and workflow guidance, not as the current implementation map.

### Commit Message Rules

**Verified.** `AGENTS.md` requires commit messages like `<type>(<scope>): <summary>`. `.cursor/rules/03-defensive-commits.mdc` uses a different style, `<scope>: <short imperative summary>`. This is a small but real governance conflict.

## Current Outputs: Quality Review

### Paper Draft

File: `reports/drafts/paper_v0.1_2026-04-18.md`

**What is good.**

- **Verified.** The draft is tied to generated tables and figures rather than being pure narrative.
- **Verified.** It includes conservative language in places, including non-causal caveats.
- **Verified.** It surfaces uncomfortable findings rather than hiding them: Chow evidence at the BTC ETF date is weak, sup-F break dates land in 2021, and placebo diagnostics need care.
- **Inference.** It is a credible v0.1 scaffold for internal review.

**What is weak.**

- **Inference.** The volatility-dampening interpretation is too mechanistic. A lower post-ETF BTC return standard deviation does not identify "patient institutional holder" behavior without stronger evidence.
- **Verified.** The ETF flow driver claim relies on contemporaneous flow features whose scaling is not clean market-cap intensity. Same-day flow timing/reporting and endogeneity concerns are not resolved.
- **Verified.** The break evidence does not yet match the stated Bai-Perron ambition.
- **Inference.** Some 2021 break narratives risk story-fitting unless tied to pre-registered event dates or robustness checks.
- **Verified.** Native on-chain CryptoQuant blocks are underused relative to the stated five-block design.

### Figures

Directory: `reports/figures/2026-04-18/`

**Verified.** The figure set is useful for internal diagnostics:

- `F01_cumulative_returns.png`
- `F02_btc_rolling_r2.png`
- `F02_eth_rolling_r2.png`
- `F03_btc_partial_r2_stack.png`
- `F04_eth_partial_r2_stack.png`
- `F05_sup_f_btc.png`
- `F06_sup_f_eth.png`
- `F07_fevd_heatmap.png`
- `F08_event_cars.png`
- `F09_coverage.png`
- `F10_btc_tradfi_corr.png`

**Reviewer assessment.**

- `F03_btc_partial_r2_stack.png` and `F04_eth_partial_r2_stack.png`: informative, but the event lines need clearer labels, the legend is heavy, and the stacked clipped partial-R2 visual can imply additive decomposition even if the underlying statistic is not a Shapley/block decomposition.
- `F07_fevd_heatmap.png`: diagnostic but not publication-ready; axis/footer labeling is cramped, the diagonal dominates, and the figure needs clearer economic grouping.
- `F08_event_cars.png`: crowded; some annotations collide, and the event windows need cleaner separation if used in a paper.
- `F09_coverage.png`: good engineering diagnostic but not a paper figure; labels are dense and the visual lacks enough explanatory structure for readers.

**Inference.** The current plots signal that a real pipeline ran, but also signal low editorial polish. They should not be submitted as core paper figures without redesign.

## Prior AI Outputs: Quality and Authority

### Highest-Value Prior Inputs

**`reports/prior_ai_outputs/FINAL_SYNTHESIS_TOP5_PROJECTS.md`**

**Verified.** This is one of the better prior synthesis files. It converges on the same central direction as the current repo: ETF/institutionalization, factor exposure evolution, structural breaks, and dynamic transmission. It also correctly warns against treating repeated AI suggestions as evidence.

**Weakness.** It is partly stale and assumes future analyses that are not implemented. It references older inventory naming and proposes project protocols that do not exist in the current repo.

**Use.** Keep as planning input. Do not treat it as empirical evidence.

**`reports/prior_ai_outputs/research_memo.md`**

**Verified.** This is broad, detailed, and generally aligned with the repository's factor-block design. It has useful variable-mapping and project-portfolio thinking.

**Weakness.** It is too broad for the current single-paper mission and contains external literature/current-event claims that need verification before reuse.

**Use.** Keep as a structured idea bank. Do not let it expand the scope beyond the core paper.

### Citation-Risk Prior Inputs

**`reports/prior_ai_outputs/deep-research-report.md`**

**Verified.** It has useful thematic framing around flow regime, ETF institutionalization, stablecoins, and ETH collateral. However, it relies heavily on `turn...` citation placeholders rather than durable citations.

**Use.** Use only for framing hypotheses. Do not reuse citations without verification.

**`reports/prior_ai_outputs/Beyond Correlation_ Quantifying Bitcoin's New Role in Financial Markets Through Structural Breaks, Flow Dynamics, and Systemic Risk.md`**

**Verified.** It discusses structural breaks and rolling/dynamic methods, which are relevant. But `AGENTS.md` explicitly warns that this file contains unverified 2026 arXiv IDs. It also leans toward TVP-VAR/geopolitical/systemic-risk scope that is broader than the current canonical paper.

**Use.** Treat as speculative background only.

### Low-Authority Prior Input

**`reports/prior_ai_outputs/txt output p2.md`**

**Verified.** This file contains claims that do not match the current data inventory or project constitution, including claims about granular high-frequency order-book data, options surfaces, and ML/DML-centered project direction.

**Use.** Do not use as authority. It may be useful only as a negative example of scope drift.

### Latest Prior Opus Output

File: `Latest Output.txt`

**Verified.** The file describes a substantial v0.1 pipeline and appears consistent with many generated artifacts now present under `src/cqresearch`, `scripts`, `reports/tables/2026-04-18`, `reports/figures/2026-04-18`, and `reports/drafts/paper_v0.1_2026-04-18.md`.

**Good.**

- It created a real analytical scaffold rather than only prose.
- It produced a master panel, tables, figures, tests, run summaries, and a paper draft.
- It was appropriately cautious in places about not claiming causal ETF effects.
- It left a useful `HANDOFF.md`.

**Weak.**

- It overstates method completeness relative to specs: single-break sup-F is not full Bai-Perron; current partial R2 is not the promised block/Shapley decomposition; current VAR is larger than the compact four-variable system in the mission.
- It treats ETF flow intensity as usable without resolving its units or timing assumptions.
- It underuses the deeper CryptoQuant on-chain source coverage.
- It provides only thin test coverage relative to the paper claims.
- It produced figures that are serviceable but visibly not publication-ready.

**Authority.** Because `Latest Output.txt` is untracked, it should be treated as a prior operator memo, not a canonical repo artifact.

## References Review

**Verified.** `references/FinancialEconometrics-master/FinancialEconometrics-master/` is a Julia financial-econometrics course repository with notebooks and PDF notes covering OLS, diagnostics, non-iid OLS, model selection, LASSO, bootstrap, panel regression, VAR/time series, GARCH, DCC, and related methods.

**Use.** This can improve method hygiene and reviewer language. It should not drive project scope. It is educational material, not evidence about crypto markets.

**Verified.** `references/cursor-ai-tips-main/cursor-ai-tips-main/` and `references/awesome-cursor-skills-main/awesome-cursor-skills-main/` are workflow/agent-skill references. They contain many process ideas: planning, defensive commits, context management, testing, visual QA, parallel exploration, and skill construction.

**Use.** These references are relevant to autonomous workflow quality. They are not empirical research evidence. Some files contain time-sensitive tool/model claims and encoding artifacts, so they should be used selectively.

## Strongest Project-Direction Patterns

**Verified.** Across the constitution, project plan, context files, manager synthesis, configs, data inventory, prior AI outputs, current code, and v0.1 outputs, the strongest common direction is:

> BTC and ETH exposures to institutional, macro, liquidity, stablecoin, and native on-chain factors changed around the ETF era, and the paper should quantify that evolution with rolling OLS/block-level R2 diagnostics, pre-registered break tests, and compact dynamic transmission analysis.

**Verified.** ETF/institutionalization is the dominant, most repo-consistent headline. Evidence: `AGENTS.md`, `project_research_plan.md`, `docs/context/00_project_context_and_goals.md`, `docs/context/03_quantitative_methods_and_analysis_menu.md`, `config/events.yml`, `config/factor_blocks.yml`, `reports/prior_ai_outputs/FINAL_SYNTHESIS_TOP5_PROJECTS.md`, `reports/drafts/paper_v0.1_2026-04-18.md`.

**Inference.** The best non-ETF support themes are:

- stablecoin liquidity and supply composition,
- on-chain/network activity,
- TradFi/macro risk transmission,
- derivatives/liquidity conditions.

These should remain explanatory blocks or robustness modules unless the ETF paper is abandoned.

## Improvements To Make Later

No changes are made here; this is a prioritized improvement list.

1. **Reconcile canonical entry points.** Decide whether `run_pipeline.py` should orchestrate the research pipeline or whether the rule should be updated to recognize `scripts/run_full_pipeline.py`.

2. **Implement or relabel structural-break evidence.** Either implement actual Bai-Perron multiple-break detection with documented trimming and information criteria, or relabel the current method as Chow plus single-break sup-F.

3. **Implement the promised block contribution method.** If the paper claims block partial R2/Shapley, implement it directly and test it. Otherwise, rename current diagnostics.

4. **Resolve calendar/fill policy.** Make `config/calendars.yml` the operational source of truth, especially for weekends, holidays, ETF flows, macro/equity series, and CryptoQuant daily data.

5. **Fix ETF flow intensity.** Prefer flow over market cap, flow over AUM, or flow over realized volume. If price-scaling remains, label it as flow-per-price and avoid market-cap language.

6. **Increase tests.** Add math tests for OLS, rolling R2, structural-break routines, FEVD, event windows, and calendar fill behavior. Add data-construction tests for ETF and stablecoin aggregation.

7. **Harden citation discipline.** Prior AI citations should be audited before they enter any draft. Files with `turn...` placeholders or warned 2026 arXiv IDs are not citation-valid.

8. **Redesign figures.** Separate diagnostic engineering figures from paper figures. The paper should use fewer, cleaner, better-labeled figures.

9. **Populate specs.** Convert `docs/specs/` from partial design notes into binding implementation contracts.

10. **Clarify environment.** Align `AGENTS.md`, `pyproject.toml`, `uv.lock`, and actual interpreter version.

## Open Questions

- Should the paper formally target only BTC and ETH, or include SOL ETF data as a placebo/extension given `Data/Farside ETF Data/farside_sol_etf_flows__daily.csv`?
- Should daily regressions use calendar days with zero/filled market variables, or restrict to trading days for macro/TradFi blocks and handle crypto-native blocks separately?
- Should the headline dynamic system be the compact four-variable mission system or the broader eight-variable v0.1 system?
- Which ETF flow scaler is the economically defensible default: market cap, AUM, spot volume, realized volatility, or price-only proxy?
- Should native on-chain metrics enter the headline model or remain robustness due to interpretability/missingness?

## Quality Gate

**Inputs read.** Listed in the evidence base section above.

**Outputs written.**

- `CODEX/current_status_analysis.md`

**Confidence score.** 88%.

**Supporting evidence.** High confidence on repository structure, generated output existence, config/spec/code contradictions, and prior-output quality risks. Lower confidence on some data-construction implications because a full re-run and line-by-line model audit were outside this documentation-only task.

**Next agent.** Manager reviewer agent using `CODEX/Manager_Reviewer_Prompt.md`.
