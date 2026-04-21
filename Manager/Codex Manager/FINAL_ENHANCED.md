# CryptoQuant Research Program - Final Synthesis
**Synthesized from:** Opus Manager Review, Gemini Manager Review, Codex Manager Review
**Synthesis date:** 2026-04-18
**Synthesis agent:** Codex GPT-5 local synthesis

---

## 1. Consensus Findings (All Three Agents Agree)

### 1.1 Repository State

- [VERIFIED] The repository is real and operational, not merely a planning folder. All three reviewers cite the Python package, numbered scripts, generated panel, dated tables, dated figures, run summaries, tests, and draft as evidence. Agent support: [Opus+Gemini+Codex]. Repo evidence: `src/cqresearch/`, `scripts/`, `reports/panels/master_daily.parquet`, `reports/tables/2026-04-18/`, `reports/figures/2026-04-18/`, `reports/run_summaries/03_run_analyses.md`, `reports/drafts/paper_v0.1_2026-04-18.md`.
- [VERIFIED] Current generated research output is v0.1 diagnostic work, not publication-grade evidence. Agent support: [Opus+Gemini+Codex]. Repo evidence: `reports/drafts/paper_v0.1_2026-04-18.md`; `reports/figures/2026-04-18/`; `CODEX/current_status_analysis.md`.
- [VERIFIED] The current code and outputs primarily serve Paper 1: BTC/ETH factor-exposure evolution around institutionalization. No equivalent code, paper-specific panel, tables, or draft exists yet for Papers 2-4. Agent support: [Opus+Gemini+Codex]. Repo evidence: `scripts/01_build_master_panel.py` through `scripts/05_robustness.py`; `reports/tables/2026-04-18/`; `reports/drafts/paper_v0.1_2026-04-18.md`.
- [VERIFIED] The current master analysis panel has 2,293 rows and 58 columns. Agent support: [Opus+Codex]. Repo evidence: `reports/run_summaries/02_build_master_panel.md`; `reports/panels/master_daily_meta.json`.

### 1.2 Governance Gaps

- [VERIFIED] `AGENTS.md` is the controlling constitution and defines a four-paper research program, while older docs and rules still describe a single-paper BTC/ETH ETF/factor project. Agent support: [Opus+Gemini+Codex]. Repo evidence: `AGENTS.md`; `README.md`; `HANDOFF.md`; `project_research_plan.md`; `.cursor/rules/global-constitution.mdc`.
- [VERIFIED] Governance drift affects execution, not only prose. The project has two pipeline concepts, conflicting Python version guidance, stale manager docs, and inconsistent commit-message rules. Agent support: [Opus+Gemini+Codex]. Repo evidence: `run_pipeline.py`; `scripts/run_full_pipeline.py`; `pyproject.toml`; `HANDOFF.md`; `.cursor/rules/`.
- [INFERENCE] Governance reconciliation is a prerequisite for scaling from one analysis to four papers because future agents will otherwise follow stale single-paper instructions. Agent support: [Opus+Gemini+Codex]. Strongest evidence: Opus and Codex cite the specific conflicting files; Gemini states the same conflict more generally.

### 1.3 Method-Label Problems

- [VERIFIED] The current implementation does not support a full Bai-Perron multiple-break claim. It implements Chow tests and a single unknown-break sup-F sweep. Agent support: [Opus+Gemini+Codex]. Repo evidence: `src/cqresearch/modeling/structural_breaks.py`; `docs/specs/methods_spec.md`; `reports/run_summaries/03_run_analyses.md`.
- [VERIFIED] The current rolling contribution implementation is not a Shapley/Owen block decomposition. It is closer to variable-drop partial R2 contributions aggregated or interpreted by block. Agent support: [Opus+Gemini+Codex]. Repo evidence: `src/cqresearch/modeling/rolling.py`; `docs/specs/methods_spec.md`.
- [VERIFIED] Current event-study placebo p-values are not window-specific in the way a reader may infer unless explicitly labeled as a benchmark. Agent support: [Codex only]. Repo evidence: `scripts/02_run_analyses.py`; `reports/tables/2026-04-18/event_studies.csv`.
- [INFERENCE] The safest immediate action is relabeling and caveating existing methods before adding new econometric machinery. Agent support: [Opus+Gemini+Codex], with Codex strongest on implementation sequencing.

### 1.4 Data Quality

- [VERIFIED] The current inventory count is 490 CSV files across seven source families. Agent support: [Codex only for current count; Opus+Gemini support the broader inventory strength but used stale 484 counts]. Repo evidence: `Data/MASTER_DATA.csv`.
- [VERIFIED] Current source counts are AlternativeMe 1, Artemis 48, CryptoQuant 345, DefiLlama 28, Farside ETF Data 3, FRED 21, and Tradingview 44. Agent support: [Codex only]. Repo evidence: `Data/MASTER_DATA.csv`.
- [VERIFIED] Current frequency counts are daily 436, weekly 31, monthly 13, snapshot 9, and `~4d` 1. Agent support: [Codex only]. Repo evidence: `Data/MASTER_DATA.csv`.
- [VERIFIED] Cross-vendor overlap is strongest for BTC/ETH ETF flows, DefiLlama TVL internal consistency, ETH market cap, and several source-precedence checks. Agent support: [Opus+Gemini+Codex]. Repo evidence: `CODEX/data_analysis.md`.
- [VERIFIED] Similar labels across vendors are not interchangeable. Stablecoin supply, TVL, USD strength, ETF AUM, exchange flows, open interest, and fees need unit/universe/frequency documentation. Agent support: [Opus+Gemini+Codex]. Repo evidence: `CODEX/data_analysis.md`; `Data/MASTER_DATA.csv`.

### 1.5 Calendar/Fill Problems

- [VERIFIED] Calendar policy is a substantive empirical decision, not a code style issue. Weekend fills and zero returns can affect OLS, rolling R2, break tests, VARs, and event studies. Agent support: [Opus+Gemini+Codex]. Repo evidence: `config/calendars.yml`; `src/cqresearch/data/calendars.py`; `reports/drafts/paper_v0.1_2026-04-18.md`.
- [VERIFIED] `config/calendars.yml` says daily calendars use `ffill_limit: 0`, while `src/cqresearch/data/calendars.py` has hardcoded 4-day forward-fill defaults for stock/rate series. Agent support: [Opus+Gemini+Codex]. Repo evidence: `config/calendars.yml`; `src/cqresearch/data/calendars.py`.
- [INFERENCE] Headline regressions mixing TradFi and crypto variables should use market-day samples for Papers 1-2, with crypto-7 and weekly variants as robustness. Agent support: [Gemini+Codex]; Opus is close but allows calendar-daily join with bounded fills.

### 1.6 Testing Gaps

- [VERIFIED] Tests pass but are too thin for the empirical claims. Codex is the only reviewer that reports running `python -m pytest -q`, with 9 passing tests. Agent support: [Opus+Gemini+Codex on thinness; Codex only on actual run]. Repo evidence: `tests/unit/`; `Manager/Codex Manager/codex_manager_review_2026-04-18.md`.
- [VERIFIED] Existing tests do not adequately cover calendar/fill semantics, ETF flow scaling, event-window placebo logic, rolling contribution math, structural-break fixtures, VAR/FEVD stability, or source-overlap reproducibility. Agent support: [Opus+Gemini+Codex]. Repo evidence: `tests/unit/`; `src/cqresearch/modeling/`; `src/cqresearch/data/`.

### 1.7 Prior AI Output Risks

- [VERIFIED] Prior AI outputs are not authoritative under `AGENTS.md`; several files are explicitly citation-risk or low-authority. Agent support: [Opus+Gemini+Codex]. Repo evidence: `AGENTS.md`; `reports/prior_ai_outputs/`; `Latest Output.txt`.
- [VERIFIED] `deep-research-report.md` and `Beyond Correlation_ Quantifying Bitcoin's New Role in Financial Markets Through Structural Breaks, Flow Dynamics, and Systemic Risk.md` must not contribute external citations unless independently verified. Agent support: [Opus+Gemini+Codex]. Repo evidence: `AGENTS.md`; `reports/prior_ai_outputs/`.
- [INFERENCE] The right handling is quarantine plus citation audit, not deletion by default. Agent support: [Opus+Codex]. Gemini argues for delete or stronger physical isolation.

### 1.8 Maximum-Inventory Paper Feasibility

- [VERIFIED] All three reviewers reject a standalone kitchen-sink maximum-inventory paper as the main research object. Agent support: [Opus+Gemini+Codex]. Repo evidence: `AGENTS.md`; `Data/MASTER_DATA.csv`; `config/factor_blocks.yml`; `CODEX/data_analysis.md`.
- [INFERENCE] The maximum-inventory work is valuable as shared infrastructure: metric dictionary, source-overlap registry, paper-specific panels, factor library, and appendix. Agent support: [Opus+Gemini+Codex], with Codex giving the most implementable protocol in `Manager/Codex Manager/data_calendar_metric_strategy_v0.md`.

### 1.9 Current Paper 1 Interpretation

- [VERIFIED] Current run summaries report BTC Chow at 2024-01-11 as insignificant, ETH Chow at 2024-07-23 as significant, and sup-F argmax dates in 2021 for both BTC and ETH. Agent support: [Opus+Codex]; Gemini agrees directionally. Repo evidence: `reports/run_summaries/03_run_analyses.md`; `reports/tables/2026-04-18/structural_breaks_summary.csv`.
- [INFERENCE] The current evidence supports a descriptive "factor composition and market maturation" story more strongly than an "ETF launch caused a new regime" story. Agent support: [Opus+Gemini+Codex]. Repo evidence: `reports/drafts/paper_v0.1_2026-04-18.md`; `AGENTS.md`.

---

## 2. Contradictions and Disagreements

### 2.1 Paper 4 Selection

- [VERIFIED] Issue: The reviewers disagree on the second non-ETF bridge paper.
- [VERIFIED] Opus position: Paper 4 should be DeFi vs CEX liquidity fragmentation, using DefiLlama TVL, Artemis DEX volume/TVL/fees, DefiLlama CEX inflows, Artemis CEX spot/perps volume, and CryptoQuant exchange flows. Agent support: [Opus only]. Source: `Manager/Opus Manager/comprehensive_review.md`.
- [VERIFIED] Gemini position: Paper 4 should be DeFi TVL vs centralized exchange structure under stress, especially VIX/macro stress episodes and capital flight. Agent support: [Gemini only]. Source: `Manager/Gemini Manager/Project_Audit_Report.md`.
- [VERIFIED] Codex position: Paper 4 should be DeFi credit, lending, and RWA rate-arbitrage, using Artemis lending deposits/borrows/interest fees, DefiLlama/Artemis RWA, FRED rates, and stablecoin controls. Agent support: [Codex only]. Source: `Manager/Codex Manager/codex_manager_review_2026-04-18.md`; `Manager/Codex Manager/four_paper_protocols_v0.md`.
- [INFERENCE] Strongest evidence: Codex has the most implementation-ready evidence and explicit data paths for lending/RWA; Opus and Gemini choose a thematically attractive DeFi/CEX paper but both rely on metric families that `CODEX/data_analysis.md` classifies as not yet comparable without reconciliation.
- [INFERENCE] Recommended resolution: choose Codex's DeFi credit/lending/RWA Paper 4 as the default, with a required data-quality gate and fallback to ETH staking/LST/LRT if lending/RWA signal quality fails.
- [DECISION-NEEDED] Human decision required because this selects one of the four portfolio papers.

### 2.2 Tooling Migration Aggressiveness

- [VERIFIED] Issue: The reviewers disagree on how much tooling to add before research hardening.
- [VERIFIED] Opus position: Add selective tools such as `ruptures`, `plotnine`, and Quarto or Typst; do not switch primary language or adopt DuckDB/Polars-only. Agent support: [Opus only].
- [VERIFIED] Gemini position: More aggressive modernization with Polars/DuckDB, plotnine/Quarto, and possible `rpy2` bridge to R `strucchange`. Agent support: [Gemini only].
- [VERIFIED] Codex position: Delay dependency additions until governance, calendars, method labels, and tests are fixed; keep Python primary. Agent support: [Codex only].
- [INFERENCE] Strongest evidence: Codex and Opus, because the current blockers are governance/method/calendar/test defects rather than data-processing speed. Repo evidence: `pyproject.toml`; `src/cqresearch/`; `tests/unit/`.
- [INFERENCE] Recommended resolution: no broad migration in Phase 1. Add dependencies only after protocols specify a concrete need.
- [DECISION-NEEDED] Human decision only if the team wants immediate Quarto/plotnine/R migration; otherwise default is delay.

### 2.3 Calendar Strategy Details

- [VERIFIED] Issue: The reviewers agree calendar handling is urgent but differ on exact policy.
- [VERIFIED] Opus position: Use calendar-daily as master, bounded forward-fill up to 3 days for TradFi levels/rates, zero-fill ETF flows within active windows, and business-day headline regressions where needed. Agent support: [Opus only].
- [VERIFIED] Gemini position: Do not force TradFi variables to crypto-7 for regressions; weekend returns are "statistical poison"; use business-day samples for macro/ETF models. Agent support: [Gemini only].
- [VERIFIED] Codex position: Use market-day panels for headline macro/ETF regressions in Papers 1-2, calendar-day panels for crypto-native diagnostics, and weekly panels for lending/RWA or mixed-frequency robustness. Agent support: [Codex only].
- [INFERENCE] Strongest evidence: Codex gives the best portfolio-level policy and Gemini gives the clearest statistical warning. Repo evidence: `config/calendars.yml`; `src/cqresearch/data/calendars.py`.
- [INFERENCE] Recommended resolution: market-day headline regressions for Papers 1-2; calendar-day for stablecoin/DeFi questions where 7-day activity is the object; weekly for lending/RWA and robustness.
- [DECISION-NEEDED] Human approval required because `AGENTS.md` says calendar/fill policy changes require human approval.

### 2.4 Data Inventory Count: 484 vs 490

- [VERIFIED] Issue: Opus and Gemini report 484 CSVs; Codex reports 490.
- [VERIFIED] Opus position: 484 CSVs based on `Data/MASTER_DATA.md` at review time. Agent support: [Opus only].
- [VERIFIED] Gemini position: 484 CSVs based on the same stale inventory summary. Agent support: [Gemini only].
- [VERIFIED] Codex position: 490 CSVs, with source and frequency counts. Agent support: [Codex only]. Repo evidence: `Data/MASTER_DATA.csv`.
- [VERIFIED] Strongest evidence: Codex, because `Data/MASTER_DATA.csv` is higher in the evidence hierarchy than manager prose and currently enumerates 490 rows.
- [VERIFIED] Recommended resolution: use 490 as the current verified count; annotate 484 as stale.
- [VERIFIED] Human decision not required.

### 2.5 CODEX Folder Naming

- [VERIFIED] Issue: Whether to keep `CODEX/` or rename it to `AUDIT/` or `QA_GATES/`.
- [VERIFIED] Opus position: Keep `CODEX/` and add per-paper status files. Agent support: [Opus only].
- [VERIFIED] Gemini position: Rename to `AUDIT/` or `QA_GATES/`. Agent support: [Gemini only].
- [VERIFIED] Codex position: Keep `CODEX/`, use it for audits/status while keeping `Manager/` for independent reviews and synthesis. Agent support: [Codex only].
- [INFERENCE] Strongest evidence: Opus and Codex, because existing repo references already point to `CODEX/`, and a rename is broad churn with little empirical benefit.
- [INFERENCE] Recommended resolution: keep `CODEX/`; optionally add an explanatory README or per-paper status files after portfolio approval.
- [VERIFIED] Human decision not required unless the user wants a broad repo reorganization.

### 2.6 Pipeline Entry Point Strategy

- [VERIFIED] Issue: Root `run_pipeline.py` and `scripts/run_full_pipeline.py` are both present and serve different roles.
- [VERIFIED] Opus position: Document root `run_pipeline.py` as curation/collection and `scripts/run_full_pipeline.py` as research analysis. Agent support: [Opus only].
- [VERIFIED] Gemini position: Remove or collapse `scripts/run_full_pipeline.py` so one root entry point controls everything. Agent support: [Gemini only].
- [VERIFIED] Codex position: Keep both and document the distinction. Agent support: [Codex only].
- [INFERENCE] Strongest evidence: Opus and Codex, because root pipeline and research pipeline have different scopes today. Repo evidence: `run_pipeline.py`; `scripts/run_full_pipeline.py`; `.cursor/rules/global-constitution.mdc`.
- [INFERENCE] Recommended resolution: keep both; update docs/rules to define curation vs. research analysis entry points.
- [VERIFIED] Human decision not required unless deleting or reorganizing pipeline files.

### 2.7 VAR System Size and Identification

- [VERIFIED] Issue: Current v0.1 uses an 8-variable VAR/FEVD system, while specs and reviewers question size and ordering.
- [VERIFIED] Opus position: 8 variables may be overparameterized; consider a compact 4-variable system and document Cholesky ordering. Agent support: [Opus only].
- [VERIFIED] Gemini position: Use a precise 4-variable VAR/FEVD design for ETF transmission. Agent support: [Gemini only].
- [VERIFIED] Codex position: The current VAR/FEVD assumptions, identification, and stability diagnostics need documentation; current run reports 27.3 percent connectedness. Agent support: [Codex only]. Repo evidence: `reports/run_summaries/03_run_analyses.md`; `reports/tables/2026-04-18/var_fevd_meta.json`.
- [INFERENCE] Strongest evidence: Codex on current implementation; Opus/Gemini on econometric parsimony.
- [INFERENCE] Recommended resolution: relabel current 8-variable FEVD as diagnostic; choose a compact, pre-declared headline VAR with documented ordering and stability checks.
- [DECISION-NEEDED] Human should approve the headline VAR specification if it affects paper claims.

### 2.8 ETF Flow Intensity Fix

- [VERIFIED] Issue: Current ETF flow intensity divides flow by prior close, not market cap, AUM, or volume. Agent support: [Opus+Gemini+Codex]. Repo evidence: `src/cqresearch/features/panel.py`.
- [VERIFIED] Opus position: Use prior-day market cap or explicitly label the current measure as flow-per-price. Agent support: [Opus only].
- [VERIFIED] Gemini position: Use market cap, circulating supply, spot volume, or AUM rather than price. Agent support: [Gemini only].
- [VERIFIED] Codex position: Use market cap, AUM, or volume; current file comment acknowledges the flow-per-price limitation. Agent support: [Codex only].
- [INFERENCE] Strongest evidence: all agree on the defect; Opus gives the cleanest default denominator.
- [INFERENCE] Recommended resolution: use prior-day market cap for headline ETF intensity; retain AUM or realized volume as robustness if data support it; otherwise relabel current measure as flow-per-price and narrow interpretation.
- [DECISION-NEEDED] Human approval recommended because this changes headline coefficient interpretation and output values.

### 2.9 Prior AI Output Handling

- [VERIFIED] Issue: Whether to delete, quarantine, archive, or retain prior AI outputs.
- [VERIFIED] Opus position: Keep quarantined; salvage project-ranking and variable ideas; ignore citations unless verified. Agent support: [Opus only].
- [VERIFIED] Gemini position: Delete or physically isolate hallucination-prone AI notes to prevent ingestion. Agent support: [Gemini only].
- [VERIFIED] Codex position: Keep quarantined, classify risk, and add citation-audit gates before reuse. Agent support: [Codex only].
- [INFERENCE] Strongest evidence: Codex and Opus align with `AGENTS.md` without destructive deletion. Repo evidence: `AGENTS.md`; `reports/prior_ai_outputs/`.
- [INFERENCE] Recommended resolution: keep `reports/prior_ai_outputs/` quarantined; add citation checks; do not cite those files for empirical claims.
- [VERIFIED] Human decision not required unless files are moved or deleted.

### 2.10 R Bridge vs Pure Python vs Relabeling

- [VERIFIED] Issue: Whether to implement true Bai-Perron now, add R tooling, add Python change-point tooling, or relabel.
- [VERIFIED] Gemini position: Consider `rpy2` and R `strucchange` for true Bai-Perron. Agent support: [Gemini only].
- [VERIFIED] Opus position: Prefer pure-Python `ruptures` if true multiple-break detection is needed. Agent support: [Opus only].
- [VERIFIED] Codex position: Fix labels first; add methods only after governance and protocol decisions. Agent support: [Codex only].
- [INFERENCE] Strongest evidence: Codex for immediate execution safety; Opus for a future Python-native upgrade path.
- [INFERENCE] Recommended resolution: relabel current results now; defer true multiple-break implementation; avoid R bridge unless a later methods decision proves it necessary.
- [DECISION-NEEDED] Human decision required if the paper must retain a Bai-Perron claim.

### 2.11 Python Version and Lockfile

- [VERIFIED] Issue: Python guidance differs across repo files and no committed `uv.lock` is visible in the reviewed inventory. Agent support: [Opus+Gemini+Codex]. Repo evidence: `AGENTS.md`; `pyproject.toml`; `HANDOFF.md`.
- [VERIFIED] Opus position: Pin to Python 3.11+ and generate `uv.lock`. Agent support: [Opus only].
- [VERIFIED] Gemini position: Reinforce `uv` and configure `pyproject.toml` for Python 3.11+. Agent support: [Gemini only].
- [VERIFIED] Codex position: resolve environment guidance as part of governance/doc reconciliation. Agent support: [Codex only].
- [INFERENCE] Recommended resolution: standardize on Python 3.11+ unless a dependency check fails.
- [DECISION-NEEDED] Human decision may be needed if the active machine is pinned to 3.10.

### 2.12 Paper 1 Headline: 2021 Break vs ETF-Date Story

- [VERIFIED] Issue: Current sup-F maxima are in 2021, while the project framing emphasizes ETF institutionalization. Repo evidence: `reports/run_summaries/03_run_analyses.md`; `reports/tables/2026-04-18/structural_breaks_summary.csv`.
- [VERIFIED] Opus position: Make the 2021 break the honest headline and frame ETF as compositional evolution. Agent support: [Opus only].
- [VERIFIED] Gemini position: Warns against ETF-causal volatility and flow narratives; still frames Paper 1 around ETF-era factor geometry. Agent support: [Gemini only].
- [VERIFIED] Codex position: The ETF date may not be the dominant break; use conservative descriptive language. Agent support: [Codex only].
- [INFERENCE] Strongest evidence: Opus and Codex, because they cite the exact generated break results.
- [INFERENCE] Recommended resolution: headline "market maturation with ETF-era composition changes," not "ETF launch caused the regime break."
- [DECISION-NEEDED] Human decision required if this changes the headline paper direction.

### 2.13 Publication Figure and Reporting Stack

- [VERIFIED] Issue: Current figures are diagnostic and markdown drafts are not submission-ready. Agent support: [Opus+Gemini+Codex]. Repo evidence: `reports/figures/2026-04-18/`; `reports/drafts/paper_v0.1_2026-04-18.md`.
- [VERIFIED] Opus position: Add plotnine or possibly R/ggplot2, and add Quarto/Typst. Agent support: [Opus only].
- [VERIFIED] Gemini position: Move to plotnine/Quarto and away from raw markdown/PNG workflow. Agent support: [Gemini only].
- [VERIFIED] Codex position: useful later, but do not start by rewriting all visualization/reporting code. Agent support: [Codex only].
- [INFERENCE] Recommended resolution: defer reporting-stack migration until after governance/calendar/method fixes; separate diagnostic figures from paper figures immediately in planning.

---

## 3. Blind Spots (None of the Three Covered Adequately)

- [UNCERTAIN] None of the three fully validated regression coefficient correctness by rerunning the end-to-end research pipeline and comparing outputs. Codex ran unit tests only. Repo evidence needing future validation: `scripts/run_full_pipeline.py`; `reports/tables/2026-04-18/`.
- [UNCERTAIN] Paper 4 data feasibility remains under-tested. Codex gives concrete lending/RWA paths, but no reviewer modeled whether Artemis lending, RWA, and FRED variables contain enough overlapping variation for a defensible paper. Repo paths needing checks: `Data/Artemis/Lending Deposits by Protocol.csv`; `Data/Artemis/Lending Borrows by Protocol.csv`; `Data/Artemis/Lending Interest Fees by Protocol.csv`; `Data/DefiLlama/RWA/`.
- [UNCERTAIN] ETF flow timing remains unresolved. Reviewers note same-day endogeneity and possible T+1 reporting, but no one verifies Farside reporting-time conventions or constructs a definitive timing policy. Repo paths: `Data/Farside ETF Data/`; `reports/tables/2026-04-18/robustness/R1_lagged_etf_flow.csv`.
- [UNCERTAIN] The Cholesky ordering and identification assumptions for FEVD remain under-specified. The reviews flag this, but no final ordering is chosen. Repo evidence: `docs/specs/methods_spec.md`; `reports/tables/2026-04-18/var_fevd_meta.json`.
- [UNCERTAIN] The exact role of CryptoQuant native metrics in Paper 1 is unresolved. Reviewers agree native data are underused, but no validated shortlist has been tested for coverage, missingness, multicollinearity, and interpretability. Repo paths: `Data/CryptoQuant/BTC/`; `Data/CryptoQuant/ETH/`; `config/factor_blocks.yml`.
- [UNCERTAIN] Human bandwidth and timeline remain outside repo evidence. Opus raises feasibility concerns, but none of the reviews can verify team capacity for four papers.
- [UNCERTAIN] External literature and citation quality are not validated. Gemini is best suited for external citation search, but the current synthesis uses no external claims and no external citations.
- [UNCERTAIN] Figure quality was reviewed descriptively, not through formal visual QA at manuscript size. Repo paths: `reports/figures/2026-04-18/`; `scripts/03_make_figures.py`.
- [UNCERTAIN] Config path drift was identified by Codex, but the full validation matrix of config paths against `Data/MASTER_DATA.csv` has not been written or run. Repo paths: `config/factor_blocks.yml`; `Data/MASTER_DATA.csv`.

---

## 4. Unified Four-Paper Portfolio

### Paper 1: BTC/ETH Factor-Exposure Evolution Around Institutionalization

- [VERIFIED] Category: institutionalization / market evolution. Agent support: [Opus+Gemini+Codex].
- [VERIFIED] Core question: Did BTC and ETH factor exposures change across market maturation and spot-ETF institutionalization, and are the changes better described as ETF-date breaks or broader multi-regime evolution? Agent support: [Opus+Gemini+Codex].
- [VERIFIED] Required data: BTC/ETH prices and market data, FRED macro/rates/risk controls, TradingView risk proxies, Farside ETF flows, DefiLlama stablecoin supply and TVL, selected CryptoQuant native metrics. Repo paths: `Data/CryptoQuant/`; `Data/FRED/`; `Data/Tradingview/Daily/`; `Data/Farside ETF Data/`; `Data/DefiLlama/Stablecoins/`; `Data/DefiLlama/TVL/`.
- [INFERENCE] Required methods: static HAC OLS, rolling variable-drop or correctly implemented block contribution, Chow at pre-registered dates, single-break sup-F or true multiple-break implementation if approved, compact VAR/FEVD with documented ordering, event-study diagnostics.
- [VERIFIED] Kill risks: method labels outrun code, ETF intensity units are wrong, calendar/fill artifacts affect headline regressions, native CryptoQuant data remain underused, and current break maxima are in 2021 rather than ETF dates.
- [VERIFIED] Agreement/disagreement: all three agree Paper 1 is the anchor; Opus emphasizes 2021 break as headline, Gemini emphasizes business-day discipline, Codex emphasizes protocols, tests, and labels.
- [INFERENCE] Estimated time to defensible v1.0: 3-4 weeks after P0 fixes, assuming no new causal identification claim is added.

### Paper 2: ETF Flow, Wrapper, Basis, and Market-Plumbing Transmission

- [VERIFIED] Category: institutionalization / ETF-adjacent bridge. Agent support: [Opus+Gemini+Codex].
- [INFERENCE] Core question: How do ETF flows, issuer composition, AUM, basis, and listed wrapper proxies relate to daily BTC/ETH transmission after ETF launch without overclaiming intraday price discovery?
- [VERIFIED] Required data: Farside issuer-level BTC/ETH ETF flows, DefiLlama ETF aggregate cross-checks, Artemis ETF AUM, TradingView wrapper/fund/equity proxies, CME basis files where available. Repo paths: `Data/Farside ETF Data/`; `Data/DefiLlama/ETFs/`; `Data/Artemis/`; `Data/Tradingview/Daily/`.
- [INFERENCE] Required methods: market-day sample, distributed lags, issuer concentration/decomposition, T+0/T+1 reporting sensitivity, flow/AUM scaling checks, compact transmission VAR only if identification is documented.
- [VERIFIED] Kill risks: daily data cannot support intraday price-discovery claims, issuer-level sample is short, same-day flow endogeneity is severe, and Farside timing convention needs verification.
- [VERIFIED] Agreement/disagreement: all three support an ETF-flow institutionalization paper; Opus frames issuer heterogeneity most strongly, Gemini frames flow innovation and FEVD, Codex adds wrapper/basis/plumbing and T+1 sensitivity.
- [INFERENCE] Estimated time to defensible v1.0: 4-5 weeks after Paper 1 data/calendar foundations are stabilized.

### Paper 3: Stablecoins as Shadow Settlement Liquidity

- [VERIFIED] Category: non-ETF TradFi/crypto bridge. Agent support: [Opus+Gemini+Codex].
- [INFERENCE] Core question: Do stablecoin supply, chain/token composition, and exchange-flow metrics behave like crypto dollar-liquidity state variables connected to rates, dollar strength, and BTC/ETH market conditions?
- [VERIFIED] Required data: DefiLlama stablecoin market caps, Artemis chain/token stablecoin supply, CryptoQuant USDC/USDT exchange-flow metrics, FRED rates/dollar controls, BTC/ETH returns. Repo paths: `Data/DefiLlama/Stablecoins/`; `Data/Artemis/Chains - Stablecoin Supply.csv`; `Data/Artemis/Stablecoin Supply by Token.csv`; `Data/CryptoQuant/USDC/`; `Data/CryptoQuant/USDT ETH/`; `Data/CryptoQuant/USDT (TRX)/`; `Data/FRED/`.
- [INFERENCE] Required methods: stablecoin source reconciliation, fiat-backed versus crypto-backed sub-basket construction if metadata supports it, local projections or VAR diagnostics, block horse-race against ETF/macro/TVL controls, calendar-day and weekly robustness.
- [VERIFIED] Kill risks: vendor definitions differ materially, stablecoin supply is endogenous to crypto returns, DefiLlama mapping metadata has quality concerns, and monetary-causality language would overclaim.
- [VERIFIED] Agreement/disagreement: all three support stablecoins as a bridge paper; Opus emphasizes sub-baskets and exchange flows, Gemini emphasizes shadow money/rates, Codex emphasizes source precedence and conservative liquidity framing.
- [INFERENCE] Estimated time to defensible v1.0: 5-6 weeks after metric dictionary and stablecoin metadata validation.

### Paper 4: DeFi Credit, Lending, and RWA Rate-Arbitrage Bridge (Recommended Default)

- [DECISION-NEEDED] Category: non-ETF TradFi/crypto bridge. This is the recommended default but not a three-agent consensus choice.
- [INFERENCE] Core question: Are on-chain lending, borrowing, interest-fee, and tokenized-asset metrics increasingly connected to TradFi rates, collateral conditions, stablecoin liquidity, and broad crypto market controls?
- [VERIFIED] Required data: Artemis lending deposits, borrows, interest fees, DefiLlama RWA series, Artemis tokenized market cap, FRED short rates and controls, stablecoin controls. Repo paths: `Data/Artemis/Lending Deposits by Protocol.csv`; `Data/Artemis/Lending Borrows by Protocol.csv`; `Data/Artemis/Lending Interest Fees by Protocol.csv`; `Data/DefiLlama/RWA/`; `Data/Artemis/RWA - Tokenized Market Cap.csv`; `Data/FRED/`.
- [INFERENCE] Required methods: weekly panel by default, coverage/missingness table, rate-sensitivity regressions, RWA growth/composition descriptives, robustness excluding short-history RWA variables, conservative descriptive framing unless direct yield/APR data are added.
- [UNCERTAIN] Kill risks: no direct APR panel, short RWA history, protocol definitions may shift, weekly cadence limits event timing, broad crypto beta may absorb the signal.
- [VERIFIED] Agreement/disagreement: Codex recommends this paper; Opus and Gemini instead recommend DeFi vs CEX structure/capital flight. The key evidence-based reason to prefer Codex's default is that lending/RWA paths are concrete, while DeFi/CEX comparability is explicitly unresolved in `CODEX/data_analysis.md`.
- [INFERENCE] Estimated time to defensible v1.0: 6-8 weeks, with an early 1-week kill gate.

### Paper 4 Alternative: DeFi vs CEX Liquidity Structure

- [DECISION-NEEDED] This is the Opus/Gemini alternative.
- [INFERENCE] Core question: Does liquidity migrate between DeFi venues and centralized exchanges under macro or crypto stress?
- [VERIFIED] Required data candidates: DefiLlama TVL and CEX files, Artemis DEX volume/TVL/fees, Artemis CEX/perps metrics if semantically reconciled, CryptoQuant exchange flows. Repo paths: `Data/DefiLlama/TVL/`; `Data/DefiLlama/CEX/`; `Data/Artemis/`; `Data/CryptoQuant/`.
- [UNCERTAIN] Main kill risk: DeFi and CEX metrics are not comparable yet without a semantic dictionary, so this option is higher-risk despite stronger thematic clarity.

---

## 5. Unified Priority Fix List

| Priority | Item | Confidence | What it fixes | Flagged by | Recommended implementer | Effort | Dependencies | Acceptance criteria |
|---|---|---|---|---|---|---|---|---|
| P0 | Confirm portfolio and Paper 4 default | [DECISION-NEEDED] | Prevents building panels/specs for the wrong paper set | [Opus+Gemini+Codex] | Human owner | 15 min | Read Section 6 | Written decision note names Papers 1-4 and fallback |
| P0 | Reconcile governance docs | [VERIFIED] | Aligns four-paper mission and stale single-paper docs | [Opus+Gemini+Codex] | Codex builder, Opus review | 1-2 days | Portfolio decision | `README.md`, `HANDOFF.md`, `.cursor/rules/`, and plan front matter point to `AGENTS.md` |
| P0 | Decide calendar/fill policy | [DECISION-NEEDED] | Removes weekend/fill ambiguity from regressions | [Opus+Gemini+Codex] | Human owner, then Codex builder | 0.5-2 days | Portfolio decision | Policy documented; tests cover weekend, holiday, zero-fill, ffill limits |
| P0 | Fix or relabel ETF flow intensity | [VERIFIED] | Corrects headline ETF coefficient interpretation | [Opus+Gemini+Codex] | Codex builder, Opus method review | 1 day | Denominator decision | Uses prior-day market cap or labels flow-per-price everywhere |
| P0 | Relabel methods or implement methods | [VERIFIED] | Removes Bai-Perron/Shapley overclaims | [Opus+Gemini+Codex] | Codex builder, Opus review | 1-3 days | Method decision | Drafts/tables/specs match actual code; no unsupported method labels |
| P0 | Add config path validation | [VERIFIED] | Catches stale `factor_blocks.yml` paths and loader drift | [Codex only] | Codex builder | 1 day | None | Test/script validates config paths against `Data/MASTER_DATA.csv` |
| P0 | Expand tests for empirical semantics | [VERIFIED] | Moves beyond smoke tests | [Opus+Gemini+Codex] | Codex builder | 2-4 days | Calendar and method decisions | Tests cover calendar/fill, ETF scaling, structural breaks, rolling attribution, event windows |
| P0 | Build metric dictionary schema | [INFERENCE] | Governs 490-file inventory and source precedence | [Opus+Gemini+Codex] | Codex data builder; Gemini metadata reviewer | 2-3 days | Portfolio decision | Dictionary has source, unit, frequency, coverage, transform, fill policy, paper role |
| P1 | Build source-overlap registry | [VERIFIED] | Prevents silent vendor substitution | [Opus+Gemini+Codex] | Gemini/Codex data auditor | 2-4 days | Metric dictionary | ETF, stablecoin, TVL, dollar, ETH market cap, OI, fees, flows documented |
| P1 | Add Paper 1 native CryptoQuant block | [INFERENCE] | Differentiates Paper 1 from generic ETF/macro analysis | [Opus+Codex] | Codex builder, Opus review | 3-5 days | Metric dictionary | Selected BTC/ETH native metrics pass coverage/missingness and interpretation checks |
| P1 | Define compact VAR/FEVD spec | [INFERENCE] | Reduces overparameterization and identifies ordering | [Opus+Gemini+Codex] | Quant methods lead | 1-2 days | Method decision | Variables, lags, ordering, stability checks documented before rerun |
| P1 | Separate diagnostic vs publication figures | [VERIFIED] | Avoids submitting internal QA charts | [Opus+Gemini+Codex] | Visualization agent | 3-5 days | Method labels stabilized | Each paper figure has source data, dimensions, readable labels, and review note |
| P1 | Citation audit gate | [VERIFIED] | Blocks prior-AI citation contamination | [Opus+Gemini+Codex] | Gemini external-citation agent, Codex checks | 1-3 days | Draft promotion | No `turn...` placeholders; all external citations durable |
| P1 | Resolve Python/uv reproducibility | [VERIFIED] | Aligns environment and lockfile | [Opus+Gemini+Codex] | Codex builder | 1 day | Human if interpreter constrained | Python guidance consistent; lockfile policy documented |
| P2 | Bootstrap Paper 2 issuer/plumbing panel | [INFERENCE] | Starts second institutionalization paper | [Opus+Gemini+Codex] | Codex builder | 3-5 days | Calendar and metric dictionary | Issuer/AUM/basis panel with timing sensitivity exists |
| P2 | Bootstrap Paper 3 stablecoin panel | [INFERENCE] | Starts first non-ETF bridge paper | [Opus+Gemini+Codex] | Codex builder, Gemini metadata review | 4-6 days | Stablecoin source registry | Sub-baskets or documented fallback totals exist |
| P2 | Paper 4 kill-gate feasibility test | [DECISION-NEEDED] | Determines lending/RWA vs DeFi/CEX viability | [Opus+Gemini+Codex] | Codex data builder, Opus review | 1 week | Paper 4 decision | Coverage, overlap, missingness, baseline descriptives, and go/no-go note |

---

## 6. Human Decisions Required

Respond later in this format: `Decision 1: Default. Decision 2: Option B.`

### Decision 1: Confirm Paper 4 and the Four-Paper Portfolio

- [VERIFIED] Opus recommendation: Paper 4 as DeFi vs CEX liquidity fragmentation.
- [VERIFIED] Gemini recommendation: Paper 4 as DeFi vs CEX capital flight under stress.
- [VERIFIED] Codex recommendation: Paper 4 as DeFi credit, lending, and RWA rate-arbitrage, with ETH staking/LST/LRT fallback.
- [INFERENCE] Recommended default: Codex option, because it has concrete file paths and a formal fallback.
- [INFERENCE] If no decision: proceed only with Paper 1 hardening and defer Papers 2-4 panel work.
- [UNCERTAIN] Risk of Codex default: lending/RWA signal may be too weak or too short.
- [UNCERTAIN] Risk of Opus/Gemini alternative: DeFi/CEX comparability may fail without extensive metric reconciliation.

### Decision 2: Maximum-Inventory Route

- [VERIFIED] All three reject a standalone kitchen-sink maximum-inventory paper.
- [INFERENCE] Option A, recommended default: build a data atlas, metric dictionary, source-overlap registry, and per-paper panel library.
- [INFERENCE] Option B: attempt a standalone data-atlas paper only after the four papers have stable panels.
- [INFERENCE] If no decision: use maximum-inventory work only as infrastructure.
- [UNCERTAIN] Risk of Option A: less flashy than a standalone atlas paper.
- [UNCERTAIN] Risk of Option B: multiple testing, collinearity, and narrative-fishing risk.

### Decision 3: Calendar and Fill Policy

- [VERIFIED] Opus allows calendar-daily master with bounded fills.
- [VERIFIED] Gemini recommends dropping weekends for TradFi regressions.
- [VERIFIED] Codex recommends market-day headline panels for Papers 1-2, calendar-day panels for crypto-native diagnostics, and weekly panels for lending/RWA.
- [INFERENCE] Recommended default: Codex policy.
- [INFERENCE] If no decision: do not rerun headline analyses; treat v0.1 as diagnostic only.
- [UNCERTAIN] Risk of market-day default: excludes weekend crypto activity from Papers 1-2 headline tables.
- [UNCERTAIN] Risk of calendar-day default: artificial TradFi zero returns and fills may contaminate inference.

### Decision 4: Method Labels vs Method Upgrades

- [VERIFIED] Current code supports Chow and single-break sup-F, not full Bai-Perron.
- [VERIFIED] Current rolling contribution is not Shapley/Owen.
- [INFERENCE] Option A, recommended default: relabel current methods immediately and defer true method upgrades.
- [INFERENCE] Option B: add pure-Python multiple-break tooling later.
- [INFERENCE] Option C: add R bridge only if the team accepts reproducibility cost.
- [INFERENCE] If no decision: relabel conservatively.
- [UNCERTAIN] Risk of Option A: less ambitious method language.
- [UNCERTAIN] Risk of Option B/C: more code and validation work before paper results are stable.

### Decision 5: ETF Flow Intensity Denominator

- [VERIFIED] Current implementation uses flow divided by prior close. Repo evidence: `src/cqresearch/features/panel.py`.
- [INFERENCE] Option A, recommended default: scale by prior-day market cap.
- [INFERENCE] Option B: scale by ETF AUM or spot volume as robustness.
- [INFERENCE] Option C: keep flow-per-price but relabel and narrow interpretation.
- [INFERENCE] If no decision: do not use current ETF intensity for headline economic interpretation.
- [UNCERTAIN] Risk of Option A: requires adding/validating market-cap columns in the analysis panel.
- [UNCERTAIN] Risk of Option C: weak economic interpretation.

### Decision 6: Tooling Migration

- [VERIFIED] Opus recommends selective `ruptures`, plotnine, and Quarto/Typst.
- [VERIFIED] Gemini recommends broader Polars/DuckDB/R/Quarto migration.
- [VERIFIED] Codex recommends delaying dependency additions until protocols and P0 defects are fixed.
- [INFERENCE] Recommended default: delay broad migration; allow selective additions after an accepted protocol says why.
- [INFERENCE] If no decision: keep current Python stack.
- [UNCERTAIN] Risk of default: slower manuscript modernization.
- [UNCERTAIN] Risk of aggressive migration: reproducibility and refactor risk before empirical logic is stable.

### Decision 7: Governance Reconciliation Timing

- [VERIFIED] All three identify governance drift.
- [INFERENCE] Option A, recommended default: update stale docs immediately after portfolio/calendar decisions.
- [INFERENCE] Option B: leave stale docs but add warning banners pointing to `AGENTS.md`.
- [INFERENCE] If no decision: only `AGENTS.md` remains authoritative and agent confusion persists.
- [UNCERTAIN] Risk of Option A: touches several docs.
- [UNCERTAIN] Risk of Option B: stale instructions continue to mislead future agents.

### Decision 8: Paper 1 Headline Framing

- [VERIFIED] Generated outputs put the sup-F argmax in 2021 for BTC and ETH. Repo evidence: `reports/run_summaries/03_run_analyses.md`.
- [INFERENCE] Option A, recommended default: headline market maturation and 2021 break evidence, with ETF-era composition changes as a second result.
- [INFERENCE] Option B: keep ETF institutionalization as the headline but explicitly state the dominant estimated break predates ETF launches.
- [INFERENCE] If no decision: use conservative descriptive framing and avoid "ETF caused a regime break."
- [UNCERTAIN] Risk of Option A: less aligned with the original ETF narrative.
- [UNCERTAIN] Risk of Option B: higher hostile-review risk if language overstates ETF evidence.

---

## 7. Multi-LLM Operating Model (Unified)

- [VERIFIED] Repository evidence outranks AI summaries. Agent support: [Opus+Gemini+Codex]. Governance evidence: `AGENTS.md`.
- [VERIFIED] High-impact decisions require human approval: portfolio, calendar/fill policy, event dates, Data changes, external citation acceptance, method-label upgrades, and headline claims. Agent support: [Opus+Gemini+Codex]. Governance evidence: `AGENTS.md`.
- [INFERENCE] Recommended roles:
  - Codex/GPT-5-class local agent: repo-grounded implementation, tests, panels, reproducibility, and exact file edits.
  - Claude Opus-class reviewer: hostile method/code review, claim discipline, paper review, and interpretation red-team.
  - Gemini-class research agent: external literature discovery, durable citation trails, and broad metadata scans, not unchecked repo-state claims.
  - Human owner: final portfolio, calendar/fill, method-label, citation, and headline direction decisions.
- [INFERENCE] Recommended sequence:
  1. Codex inspects repo state and drafts implementation plan.
  2. Opus red-teams method and claim risk.
  3. Gemini validates external literature or package choices where current information matters.
  4. Codex implements scoped changes with tests.
  5. A different reviewer audits outputs, labels, and claims.
- [INFERENCE] File ownership rule: no two agents edit the same high-risk area concurrently. Assign disjoint surfaces such as `src/cqresearch/data/`, `src/cqresearch/modeling/`, `docs/specs/`, `reports/drafts/`, or `Manager/`.
- [INFERENCE] Required handoff fields for every future agent: inputs read, outputs written, tests/checks run, strongest claims and evidence, limitations, confidence, open questions, and next agent.
- [INFERENCE] Automated gates to add: config path check, method-label scan, citation scan, data-integrity check, calendar/fill tests, source-overlap tests, and figure QA.

---

## 8. Confidence Assessment

### Confident

- [VERIFIED] `AGENTS.md` controls and defines a four-paper program.
- [VERIFIED] Current code and outputs primarily support one paper, not all four.
- [VERIFIED] The current inventory count is 490 CSVs in `Data/MASTER_DATA.csv`.
- [VERIFIED] ETF intensity is currently flow divided by prior close, not market-cap intensity.
- [VERIFIED] Current structural-break code is Chow plus single-break sup-F, not full Bai-Perron.
- [VERIFIED] Current rolling contribution code is not Shapley/Owen.
- [VERIFIED] Calendar/fill policy is inconsistent between config, code, and draft description.
- [VERIFIED] Prior AI outputs must not be treated as empirical or citation authority.

### Uncertain

- [UNCERTAIN] Whether lending/RWA data can support Paper 4 after coverage and signal checks.
- [UNCERTAIN] Whether DeFi/CEX metrics can be reconciled enough to support the Opus/Gemini alternative Paper 4.
- [UNCERTAIN] Whether Paper 1 native CryptoQuant metrics add robust explanatory content after coverage and collinearity filters.
- [UNCERTAIN] Whether current coefficients reproduce exactly under a corrected market-day calendar and market-cap ETF intensity.
- [UNCERTAIN] Whether the team has enough time and reviewer bandwidth for four defensible papers.

### Requires Further Investigation

- [UNCERTAIN] Farside ETF flow timing and T+1 convention.
- [UNCERTAIN] Cholesky ordering and compact VAR specification.
- [UNCERTAIN] Stablecoin metadata reliability for sub-baskets.
- [UNCERTAIN] RWA and lending definition stability.
- [UNCERTAIN] External literature and citation verification.

---

## Quality Gate

**Inputs read**

- [VERIFIED] `AGENTS.md`
- [VERIFIED] `Manager/Opus Manager/comprehensive_review.md`
- [VERIFIED] `Manager/Gemini Manager/Project_Audit_Report.md`
- [VERIFIED] `Manager/Codex Manager/codex_manager_review_2026-04-18.md`
- [VERIFIED] `Manager/Codex Manager/four_paper_protocols_v0.md`
- [VERIFIED] `Manager/Codex Manager/data_calendar_metric_strategy_v0.md`
- [VERIFIED] `Manager/Codex Manager/multi_agent_workflow_and_quality_gates_v0.md`
- [VERIFIED] `Manager/Codex Manager/p0_execution_backlog.md`
- [VERIFIED] `CODEX/current_status_analysis.md`
- [VERIFIED] `CODEX/data_analysis.md`
- [VERIFIED] `config/factor_blocks.yml`
- [VERIFIED] `config/events.yml`
- [VERIFIED] `config/calendars.yml`
- [VERIFIED] `config/chain_taxonomy.yml`
- [VERIFIED] `src/cqresearch/features/panel.py`
- [VERIFIED] `src/cqresearch/modeling/structural_breaks.py`
- [VERIFIED] `src/cqresearch/modeling/rolling.py`
- [VERIFIED] `src/cqresearch/data/calendars.py`
- [VERIFIED] `reports/drafts/paper_v0.1_2026-04-18.md`
- [VERIFIED] `reports/run_summaries/03_run_analyses.md`
- [VERIFIED] `Data/MASTER_DATA.csv`
- [VERIFIED] `docs/specs/research_spec.md`
- [VERIFIED] `docs/specs/methods_spec.md`
- [VERIFIED] `docs/specs/data_spec.md`

**Outputs written**

- [VERIFIED] `Manager/Codex Manager/FINAL_ENHANCED.md`
- [VERIFIED] Row counts not applicable because this is a Markdown synthesis artifact.
- [UNCERTAIN] Output artifact hash should be computed after final write; do not embed a self-referential file hash inside this file.

**Claims made**

- [VERIFIED] The current verified data inventory is 490 CSVs, supported by `Data/MASTER_DATA.csv`.
- [VERIFIED] The current ETF intensity implementation is flow-per-price, supported by `src/cqresearch/features/panel.py`.
- [VERIFIED] The current structural-break implementation is Chow plus single-break sup-F, supported by `src/cqresearch/modeling/structural_breaks.py`.
- [VERIFIED] The current rolling contribution implementation is not Shapley/Owen, supported by `src/cqresearch/modeling/rolling.py`.
- [INFERENCE] Codex's DeFi lending/RWA Paper 4 is the recommended default because it has more concrete implementation paths and a defined fallback than the DeFi/CEX alternative.
- [INFERENCE] Maximum-inventory work should become shared infrastructure rather than a standalone paper.

**Confidence score**

- [INFERENCE] 88 percent. Confidence is high on repo-state, method-label, data-inventory, and governance claims because they are directly supported by repository files. Confidence is lower on Paper 4 selection, signal quality, and timeline feasibility because no paper-specific modeling has been run for those themes.

**Open questions**

- [DECISION-NEEDED] Which Paper 4 option should be built first?
- [DECISION-NEEDED] Should calendar/fill policy follow the recommended market-day/calendar-day/weekly split?
- [DECISION-NEEDED] Should ETF intensity be rebuilt as market-cap-scaled?
- [DECISION-NEEDED] Should current methods be relabeled now or upgraded before further drafting?
- [UNCERTAIN] Are Farside flow timing conventions T+0 or T+1 for the intended regressions?
- [UNCERTAIN] Does lending/RWA data pass the early kill gate?

**Next agent**

- [INFERENCE] Human project owner should answer the decisions in Section 6. After those decisions, a Codex implementation builder should create `Manager/Codex Manager/NEXT_STEPS.md` and then execute P0 governance, calendar, ETF-unit, method-label, and test fixes.

