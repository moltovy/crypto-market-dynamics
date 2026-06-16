# CryptoQuant Manager Review

Date: 2026-04-18

Reviewer stance: skeptical principal research engineer, quantitative finance reviewer, empirical-finance project manager, and execution-focused codebase auditor.

## 1. Executive Judgment

**Verified.** The controlling project goal is a four-paper research program. Older files still describe a one-paper BTC/ETH ETF and factor-exposure project, but `AGENTS.md` explicitly supersedes those files. Evidence: `AGENTS.md`; `README.md`; `HANDOFF.md`; `project_research_plan.md`; `.cursor/rules/global-constitution.mdc`.

**Verified.** The repository is real and operational, but current empirical outputs are v0.1 diagnostics, not publication-grade evidence. The current inventory has 490 CSV files across seven sources; the current master analysis panel is 2,293 rows by 58 columns. Evidence: `Data/MASTER_DATA.csv`; `reports/run_summaries/02_build_master_panel.md`; `src/cqresearch/data/loaders.py`.

**Verified.** Independent manager reports under `Manager/Gemini Manager/` and `Manager/Opus Manager/` converge on the same central warning: the project has real infrastructure, but governance, calendar policy, method labels, and the four-paper transition are not yet executed in code. They also contain stale 484-file inventory counts that now conflict with `Data/MASTER_DATA.csv`. Evidence: `Manager/Gemini Manager/Project_Audit_Report.md`; `Manager/Opus Manager/comprehensive_review.md`; `Data/MASTER_DATA.csv`.

**Decision.** Do not pursue a maximum-inventory standalone paper. Build a shared data atlas, metric dictionary, and paper-specific panel library, then distribute variables across focused papers. A kitchen-sink paper would invite multiple testing, calendar artifacts, source-definition confusion, and narrative fishing. Evidence: `AGENTS.md`; `Data/MASTER_DATA.csv`; `config/factor_blocks.yml`; `config/calendars.yml`; `src/cqresearch/features/panel.py`.

**Recommended four-paper portfolio.**

1. BTC/ETH factor-exposure evolution around ETF institutionalization.
2. ETF flow, wrapper, basis, and market-plumbing transmission.
3. Stablecoins as shadow settlement liquidity and crypto dollar plumbing.
4. DeFi credit, lending, and RWA rate-arbitrage bridge.

## 2. Evidence Reviewed

Read or inspected in this implementation pass: `AGENTS.md` content supplied by the user, `Data/MASTER_DATA.csv`, `reports/run_summaries/02_build_master_panel.md`, `reports/run_summaries/03_run_analyses.md`, `src/cqresearch/features/panel.py`, `scripts/02_run_analyses.py`, `Manager/Gemini Manager/Project_Audit_Report.md`, and `Manager/Opus Manager/comprehensive_review.md`.

Prior review context covered: `README.md`, `HANDOFF.md`, `pyproject.toml`, `run_pipeline.py`, `.cursor/rules/*.mdc`, `config/*.yml`, `Data/MASTER_DATA.md`, `CODEX/current_status_analysis.md`, `CODEX/data_analysis.md`, `project_research_plan.md`, `docs/context/*.md`, `docs/manager/*.md`, `docs/specs/*.md`, `src/cqresearch/*`, `scripts/*`, `tests/*`, `reports/tables/2026-04-18/*`, `reports/figures/2026-04-18/*`, `reports/drafts/paper_v0.1_2026-04-18.md`, `reports/prior_ai_outputs/*`, `Latest Output.txt`, and representative `references/` files.

Checks run in this implementation pass: `python -m pytest -q`, 9 passed in 0.61 seconds.

Outputs written in this pass: files under `Manager/Codex Manager/` only.

## 3. Repository Reality

**Verified.** Active modules exist under `src/cqresearch/`: data loaders, calendar alignment, panel construction, return features, OLS/HAC, rolling OLS, Chow/sup-F, VAR/FEVD, event study, and visualization style. Evidence: `src/cqresearch/data/loaders.py`; `src/cqresearch/data/calendars.py`; `src/cqresearch/modeling/`; `src/cqresearch/viz/`.

**Verified.** The repo has two active pipeline concepts: root `run_pipeline.py` for collection/curation and `scripts/run_full_pipeline.py` for research analysis. This conflicts with older Cursor rules that imply a single root pipeline entry point. Evidence: `run_pipeline.py`; `scripts/run_full_pipeline.py`; `.cursor/rules/global-constitution.mdc`.

**Verified.** Current data inventory is 490 CSV files: AlternativeMe 1, Artemis 48, CryptoQuant 345, DefiLlama 28, Farside ETF Data 3, FRED 21, Tradingview 44. Current frequency counts are daily 436, weekly 31, monthly 13, snapshot 9, and `~4d` 1. Evidence: `Data/MASTER_DATA.csv`.

**Verified.** Generated outputs exist for the current anchor paper: master panel, run summaries, dated tables/figures, robustness CSVs, and a v0.1 draft. Evidence: `reports/panels/`; `reports/run_summaries/`; `reports/tables/2026-04-18/`; `reports/figures/2026-04-18/`; `reports/drafts/paper_v0.1_2026-04-18.md`.

**Verified.** Tests are thin. They pass, but they cover smoke/config/fixture behavior, not calendar semantics, flow units, event-window p-values, structural-break math, rolling block attribution, or FEVD stability. Evidence: `tests/unit/`; `python -m pytest -q`.

**Verified.** `Manager/Gemini Manager/` and `Manager/Opus Manager/` contain independent AI review outputs. Treat them as useful review evidence, not canonical source of truth. Evidence: `Manager/Gemini Manager/Project_Audit_Report.md`; `Manager/Opus Manager/comprehensive_review.md`; `AGENTS.md`.

## 4. Assessment of CODEX Audit Files

**Accept with corrections.** `CODEX/current_status_analysis.md` is directionally accurate on method-label inflation, weak tests, calendar/fill risk, ETF-flow scaling, and stale manager docs. It is incomplete on the four-paper transition, generated-output overwrite behavior, event-study placebo-window labeling, and config path drift. Evidence: `CODEX/current_status_analysis.md`; `scripts/02_run_analyses.py`; `scripts/03_make_figures.py`; `AGENTS.md`.

**Accept with corrections.** `CODEX/data_analysis.md` is useful on overlap and source precedence, but inventory counts have drifted. The current controlling inventory is 490 CSV files in `Data/MASTER_DATA.csv`, not 484. Evidence: `CODEX/data_analysis.md`; `Data/MASTER_DATA.csv`.

**Correction to independent manager outputs.** Gemini and Opus reports are valuable but also stale on the 484 inventory count. The current inventory count should be updated before either report is treated as a planning artifact. Evidence: `Manager/Gemini Manager/Project_Audit_Report.md`; `Manager/Opus Manager/comprehensive_review.md`; `Data/MASTER_DATA.csv`.

## 5. Top 6 Paper / Project Directions

| Rank | Direction | Category | Thesis | Current repo support | Biggest blocker | Lift |
|---:|---|---|---|---|---|---|
| 1 | BTC/ETH factor-exposure evolution | Institutionalization / market evolution | Factor-block explanatory power changed across crypto institutionalization, but the ETF date may not be the dominant break. | Strong: prices, macro, ETF flows, stablecoins, TVL, CryptoQuant inventory, v0.1 pipeline. | Calendar policy, method labels, native-block construction. | Medium |
| 2 | ETF flow, wrapper, basis, and plumbing | Institutionalization / ETF-adjacent | ETF flows transmit through AUM, issuer composition, wrappers, CME basis, and trading-calendar frictions. | Strong: Farside, Artemis AUM, TradingView wrappers, CME basis. | Same-day endogeneity and daily data limitations. | Medium |
| 3 | Stablecoins as shadow settlement liquidity | Non-ETF bridge | Stablecoin supply and flows are crypto dollar-liquidity state variables connecting offshore crypto markets to dollar conditions. | Strong: DefiLlama, Artemis, CryptoQuant USDT/USDC, FRED. | Vendor definitions and endogeneity. | Medium |
| 4 | DeFi credit, lending, and RWA rate-arbitrage | Non-ETF bridge | DeFi credit and tokenized assets increasingly reflect TradFi yield and collateral conditions. | Moderate: Artemis lending, DefiLlama/Artemis RWA, FRED rates. | Weekly cadence, short RWA history, missing direct APR panel. | Medium-high |
| 5 | ETH staking, LST, and LRT collateral transformation | Market evolution / bridge | ETH's staking and liquid-staking stack changes float, collateral, fees, and basis behavior. | Moderate-strong: CryptoQuant ETH, Artemis LST/LRT TVL, fees, derivatives. | Confounding with ETH ETF and staking mechanics. | Medium |
| 6 | Crypto-market data atlas / factor library | Platform / data atlas | A curated source-precedence and factor-library layer supports all papers without forcing all variables into one paper. | Strong inventory, weak dictionary. | Must be framed as infrastructure, not a standalone causal paper. | Medium |

Evidence: `AGENTS.md`; `Data/MASTER_DATA.csv`; `config/factor_blocks.yml`; `reports/run_summaries/03_run_analyses.md`; `Manager/Opus Manager/comprehensive_review.md`; `Manager/Gemini Manager/Project_Audit_Report.md`.

## 6. Recommended Four-Paper Portfolio

**Paper 1: BTC/ETH Factor-Exposure Evolution Around Institutionalization.** It belongs because it is the current anchor and has the most existing code and outputs. Its unique question is whether BTC/ETH factor relationships shifted across market maturation and ETF institutionalization. Minimum viable design: paper-specific market-day and weekly panels; static HAC OLS; rolling block contribution; correctly labeled Chow and single-break sup-F or a true multiple-break implementation; BTC/ETH staggered comparison. Credible exhibits: source/coverage table, factor-block table, pre/post regressions, rolling block figure, break-test table, robustness grid. Kill risks: weak block movement, underused CryptoQuant native data, uncorrected calendar/fill artifacts. Evidence: `reports/tables/2026-04-18/`; `reports/run_summaries/03_run_analyses.md`; `src/cqresearch/modeling/`.

**Paper 2: ETF Flow, Wrapper, Basis, and Market-Plumbing Transmission.** It belongs because it isolates the institutional transmission mechanism rather than broad factor evolution. Minimum design: Farside issuer flows, Artemis AUM, CME basis, wrapper equities/funds, distributed lags, flow surprise proxies, issuer concentration, trading-day calendar, and T+1 reporting sensitivity. Kill risks: same-day flow endogeneity, overclaiming "price discovery" from daily data, and missing issuer-level robustness. Evidence: `Data/Farside ETF Data/`; `Data/Artemis/`; `Data/Tradingview/Daily/`; `src/cqresearch/features/panel.py`.

**Paper 3: Stablecoins as Shadow Settlement Liquidity.** It belongs because it diversifies the portfolio away from ETFs while still bridging crypto and dollar-market structure. Minimum design: DefiLlama daily supply primary; Artemis chain/token composition; CryptoQuant USDT/USDC exchange-flow checks; FRED rate/dollar controls; block horse race against ETF, macro, and TVL. Kill risks: stablecoin supply endogeneity, definitional mismatch between vendors, and overclaiming monetary causality. Evidence: `Data/DefiLlama/Stablecoins/`; `Data/Artemis/Chains - Stablecoin Supply.csv`; `Data/Artemis/Stablecoin Supply by Token.csv`; `Data/CryptoQuant/USDC/`; `Data/CryptoQuant/USDT ETH/`; `Data/CryptoQuant/USDT (TRX)/`.

**Paper 4: DeFi Credit, Lending, and RWA Rate-Arbitrage Bridge.** It belongs because it targets the TradFi/crypto credit and collateral bridge. Minimum design: weekly panel using Artemis lending deposits/borrows/interest fees, DefiLlama/Artemis RWA market cap, FRED short rates, stablecoin supply, and broad crypto controls. Kill risks: weak direct yield data, short RWA series, and broad crypto beta absorbing the result. Evidence: `Data/Artemis/Lending Deposits by Protocol.csv`; `Data/Artemis/Lending Borrows by Protocol.csv`; `Data/Artemis/Lending Interest Fees by Protocol.csv`; `Data/DefiLlama/RWA/`; `Data/Artemis/RWA - Tokenized Market Cap.csv`; `Data/FRED/`.

## 7. Maximum-Inventory Project Feasibility

**Decision: feasible as shared infrastructure, not as a standalone paper.** A standalone maximum-inventory paper would be too broad and methodologically fragile. The correct output is a shared data atlas, factor library, metric dictionary, source-overlap registry, and per-paper panel constructor. Evidence: `Data/MASTER_DATA.csv`; `config/calendars.yml`; `config/factor_blocks.yml`.

Recommended methods:

- Use dimensionality reduction only within pre-defined economic blocks.
- Use PCA, clustering, sparse regression, elastic net, or partial least squares as diagnostics after economic design.
- Use boosted-tree importance only as exploratory support, not a headline result.
- Avoid "all variables into one model" designs.
- Control multiple testing with pre-registered blocks, horizons, transformations, and primary outcomes.

## 8. Current ETF / Institutionalization Paper Review

**Verified.** Current v0.1 results report BTC Chow at 2024-01-11 as insignificant, BTC sup-F argmax at 2021-01-04, ETH Chow at 2024-07-23 as significant, ETH sup-F argmax at 2021-05-12, and Diebold-Yilmaz connectedness at 27.3 percent in the current 8-variable VAR. Evidence: `reports/run_summaries/03_run_analyses.md`; `reports/tables/2026-04-18/structural_breaks_summary.csv`; `reports/tables/2026-04-18/var_fevd_meta.json`.

**Verified defect.** "Bai-Perron" is not implemented. The code implements Chow plus single-break sup-F sweep. Evidence: `src/cqresearch/modeling/structural_breaks.py`.

**Verified defect.** Current ETF intensity is flow divided by prior close, not market cap, AUM, or volume. The file comment now acknowledges flow-per-unit-price, but downstream interpretation still needs tightening. Evidence: `src/cqresearch/features/panel.py`.

**Verified defect.** Event-study placebo p-values are computed for `[-5,+5]` and then attached to all CAR windows. This is acceptable only if explicitly labeled as a single placebo benchmark; it is misleading if read as window-specific inference. Evidence: `scripts/02_run_analyses.py`; `reports/tables/2026-04-18/event_studies.csv`.

**Inference.** The v0.1 paper overclaims when it uses causal or mechanism language around ETF flows and institutional holders. The current design supports associations and diagnostics, not causal driver claims. Evidence: `reports/drafts/paper_v0.1_2026-04-18.md`; `reports/tables/2026-04-18/etf_flow_regression.csv`; `AGENTS.md`.

## 9. Mixed-Frequency and Calendar Strategy

Recommended policy:

1. Use a market-day panel for headline macro/ETF regressions in Papers 1 and 2.
2. Use calendar-day panels for crypto-native-only diagnostics and DeFi/CEX questions where weekend activity is part of the object.
3. Use weekly panels as robustness and for weekly-native lending/RWA variables.
4. Do not forward-fill monthly variables into daily regressions unless release-date aligned and explicitly framed.
5. Do not blindly fill returns, flows, fees, active addresses, volumes, or exchange-flow metrics.
6. Zero-fill ETF flows only for confirmed non-trading days inside active fund windows, with listing-date metadata.
7. Preserve snapshots for descriptive exhibits, not time-series regressions.
8. Build paper-specific panels from a shared inventory instead of one universal master panel.

Evidence: `config/calendars.yml`; `src/cqresearch/data/calendars.py`; `src/cqresearch/data/panel_builder.py`; `HANDOFF.md`.

## 10. Data Overlap and Source Recommendation

| Category | Classification | Primary source | Robustness or restricted use |
|---|---|---|---|
| BTC/ETH ETF daily flows | Exact duplicate after unit conversion and asset filter between Farside and DefiLlama aggregate | Farside | DefiLlama ETF history as cross-check; Artemis for weekly/AUM context |
| ETF AUM | Related and highly correlated, with level differences across aggregate and issuer files | Artemis aggregate | Artemis issuer files for composition |
| Stablecoin supply | Related but definitionally different across vendors | DefiLlama daily market cap | Artemis chain/token supply for composition |
| TVL | DefiLlama total and chain sum near-duplicate; Artemis DEX TVL is different concept | DefiLlama all-chain TVL | Artemis DEX TVL for DEX-sector liquidity |
| USD strength | Related but different definitions | FRED broad dollar index | TradingView DXY as market-convention robustness |
| ETH market cap | Near duplicate after unit alignment | CryptoQuant for ETH-native work | Artemis for cross-chain panels |
| Open interest | Not comparable without venue/instrument mapping | CryptoQuant BTC/ETH asset OI | Artemis platform OI after mapping |
| Fees and active addresses | Related but not duplicate | CryptoQuant for BTC/ETH-native questions | Artemis chain/ecosystem metrics |
| Exchange flows and CEX | Related but different concepts | CryptoQuant asset exchange flows | DefiLlama CEX net inflows for exchange-level structure |
| RWA / tokenized assets | Related, metadata-sensitive | DefiLlama RWA time series | Artemis tokenized market cap for issuer/composition |
| DeFi lending/yields | Proxy coverage, not a direct yield panel | Artemis lending deposits/borrows/interest fees | FRED rates and RWA panels as bridge controls |

Evidence: `Data/MASTER_DATA.csv`; `Data/Farside ETF Data/`; `Data/DefiLlama/`; `Data/Artemis/`; `Data/FRED/`; `Data/Tradingview/`; `Data/CryptoQuant/`.

## 11. High-Dimensional Inventory Strategy

Use this selection order:

1. Economic block first.
2. Source precedence second.
3. Missingness and coverage third.
4. Frequency compatibility fourth.
5. Statistical screening last.

Likely main-regression categories: returns, macro/risk factors, ETF flows/AUM, stablecoin total supply growth, TVL growth, selected basis/funding/OI, and selected BTC/ETH native metrics. Robustness categories: alternative vendor versions, lagged flows, weekly aggregation, issuer decompositions, and market-day/calendar-day variants. Descriptive or appendix categories: long-tail CryptoQuant bands, wide chain/protocol columns, snapshots, monthly composition, and short RWA subcategories. Evidence: `Data/MASTER_DATA.csv`; `config/factor_blocks.yml`; `docs/context/02_data_sources_factor_blocks_and_sample_design.md`.

## 12. Prior AI Output Review

| File | Classification | Salvage | Ignore or risk |
|---|---|---|---|
| `reports/prior_ai_outputs/FINAL_SYNTHESIS_TOP5_PROJECTS.md` | High-value synthesis but stale | Portfolio thinking and warnings | Five-paper framing and unverified literature |
| `reports/prior_ai_outputs/research_memo.md` | Useful but citation-risk | Idea bank and method candidates | External claims until verified |
| `reports/prior_ai_outputs/deep-research-report.md` | Citation-risk | Thematic framing | `turn...` citations and broad claims |
| `reports/prior_ai_outputs/Beyond Correlation_ Quantifying Bitcoin's New Role in Financial Markets Through Structural Breaks, Flow Dynamics, and Systemic Risk.md` | Speculative / citation-risk | Gradual-versus-discrete shift warnings | TVP-VAR headline and unverified current claims |
| `reports/prior_ai_outputs/txt output p2.md` | Low-authority | Scope-drift warnings | Claims about data not in repo |
| `reports/prior_ai_outputs/txt output.md` | Useful but stale | Factor-block and calendar warnings | External source claims |
| `Latest Output.txt` | Useful operator memo | Pipeline map and v0.1 output reminders | Method-completeness language |

Evidence: `reports/prior_ai_outputs/`; `Latest Output.txt`; `AGENTS.md`.

## 13. Tooling / Packages / Language Recommendations

Keep Python as the primary stack for now. The current packages are adequate for v0.2 if the team fixes governance, calendars, method labels, and tests first. Evidence: `pyproject.toml`; `src/cqresearch/`.

Selective additions:

- DuckDB: useful for reproducible inventory and CSV/Parquet audits. Add after metric dictionary design.
- Polars Lazy: already present; use for inventory scans and wide transformations, not a rewrite.
- R `strucchange`: use only if true Bai-Perron or CUSUM validation is required; avoid creating a parallel R data pipeline.
- Quarto: useful for reproducible manuscripts, citations, and paper builds after protocols stabilize.
- plotnine or a stronger matplotlib template: useful for publication figures; do not start by rewriting all visualization code.

Do not add TVP-VAR, Bayesian state-space, or ML-heavy machinery until the conservative pipeline is correct.

## 14. Multi-LLM Operating Model

Use LLMs as independent reviewers and bounded builders, not silent project owners.

- Codex/GPT-5.4 class: repo-grounded audits, implementation, tests, reproducibility, pipeline fixes.
- Claude Opus class: hostile method/code review, paper-claim review, alternative design critique.
- Gemini/Deep Research class: external literature discovery and citation trails, not repo-state claims.
- Cursor background agents: bounded branch tasks with explicit file ownership.

Reconciliation rule: compare evidence, contradictions, and unsupported claims. Do not vote-count agent recommendations.

Human approval remains required for final portfolio selection, event-date changes, calendar/fill policy, Data changes, citation acceptance, method-label changes, and core figure replacement. Evidence: `AGENTS.md`; `Manager/Gemini Manager/Project_Audit_Report.md`; `Manager/Opus Manager/comprehensive_review.md`.

## 15. Workflow / Prompts / Rules / Repo Structure

`AGENTS.md` should remain controlling. `.cursor/rules/` should be reconciled to the four-paper mission, Python 3.11+, current commit style, and current pipeline split. Evidence: `AGENTS.md`; `.cursor/rules/*.mdc`.

Minimal recommended structure later:

- Keep root `run_pipeline.py` for curation or make it orchestrate both curation and analysis; document the distinction explicitly.
- Make configs executable and consumed by scripts.
- Add per-paper protocol files before new modeling.
- Keep `reports/prior_ai_outputs/` quarantined.
- Use `Manager/` for independent agent reports and synthesis only.
- Add citation audit artifacts before accepting prior AI citations.
- Separate diagnostic figures from publication figures.

## 16. Highest-Priority Fixes

1. Freeze the four-paper portfolio and write short protocols.
2. Correct config path drift and clarify pipeline entry points.
3. Decide calendar/fill policy and rebuild paper-specific panels.
4. Build metric dictionary and source-precedence registry.
5. Relabel or implement methods: true multiple breaks, block attribution, event-study placebo windows, FEVD identification.
6. Add tests for calendar fills, ETF units, event windows, rolling contribution math, structural breaks, and overlap checks.
7. Redesign figures before any draft promotion.
8. Audit all external citations from prior AI outputs.

Evidence: `AGENTS.md`; `config/factor_blocks.yml`; `src/cqresearch/`; `scripts/`; `tests/unit/`; `reports/drafts/paper_v0.1_2026-04-18.md`.

## 17. Human Decisions Needed

1. Confirm the four-paper portfolio. Default: the four papers above. Risk: Paper 4 may fail if RWA/lending signal quality is too weak; fallback is ETH staking/LST/LRT collateral transformation.
2. Approve calendar policy. Default: market-day headline regressions for Papers 1-2; crypto-7 for crypto-native diagnostics and Paper 4; weekly robustness. Risk: v0.1 headline values will change.
3. Approve maximum-inventory project as atlas/library, not a standalone paper. Default: shared infrastructure. Risk: weaker "uses everything" story but stronger review defensibility.
4. Approve selective DuckDB/Quarto/R additions only after protocols. Default: delay dependency additions. Risk: slower reporting modernization.
5. Decide whether core repo docs should be updated now or after the human reviews these manager artifacts. Default: wait for approval, because governance and calendar changes are high-impact.

## 18. Open Questions

- Are Farside flows reported with a consistent timing convention that requires T+1 alignment?
- Which market-day calendar should be canonical: NYSE, ETF listing exchange, or observed Farside dates?
- Does Artemis DAT contain durable time series or mostly snapshots?
- Are Artemis lending files sufficient as credit/yield proxies without direct APR?
- Should BTC/ETH native CryptoQuant metrics enter Paper 1 baseline or only robustness?
- Should SOL ETF data be excluded from main analysis because the sample is too short?

## 19. Confidence and Limits

Confidence: 84 percent.

High confidence: repo structure, current inventory count, generated-output existence, v0.1 method gaps, config/calendar risk, prior-output authority, and need for a factor library rather than a maximum-inventory paper.

Medium confidence: recommended Paper 4, because DeFi lending/RWA signal quality has not yet been modeled.

Low confidence: any external literature claim not re-verified through durable sources in a citation audit.

Quality gate:

- Inputs read: listed in section 2.
- Outputs written: this file and companion files under `Manager/Codex Manager/`.
- Tests run: `python -m pytest -q`, 9 passed.
- Strongest claims: four-paper mission supersedes one-paper docs; current inventory is 490 CSVs; current empirical outputs are diagnostic; maximum-inventory paper should become atlas/library.
- Next agent: human portfolio/calendar decision, then implementation builder for P0 fixes.

