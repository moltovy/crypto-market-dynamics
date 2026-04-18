# CryptoQuant Project Research Plan

**Document version:** 1.0  
**Last updated:** 2026-04-18  
**Status:** Approved plan; execution in sprint 1.  
**Primary authors:** Manager agent (Opus 4.7, high-reasoning) with four parallel explore subagents (Data Cartographer, Prior-AI Synthesizer, Workflow Architect, Tools & Pipeline Auditor).  
**Intended reader:** The 3-person MSc Finance team, any subsequent LLM agent that joins the project, and a future reviewer (professor or journal referee).

---

## Table of Contents

1. Executive Summary
2. Method and Provenance
3. Source Inventory
4. Inferred Project Objective
5. Current State of Evidence
6. Dataset Catalog
7. Prior AI Output Synthesis
8. Cursor Workflow Lessons Applied
9. Recommended Research Questions
10. Best-of-N Strategy Comparison
11. Analysis Plan
12. Agent/Subagent Operating Plan
13. Concrete Next-Agent Prompts
14. Recommended Folder and Context Structure
15. Figure and Table Plan
16. Risks, Weaknesses, and Red-Team Findings
17. Execution Roadmap
18. Final Recommendation
19. Reorganization Specification (migration from current tree to canonical layout)

---

## 1. Executive Summary

**What the project is.** The CryptoQuant project is an MSc-level empirical-finance research program aimed at producing a single defensible working paper on **how Bitcoin and Ethereum's factor exposures evolved around the 2024 launch of US spot-ETFs**. The team has curated ~484 daily time series across seven sources (on-chain metrics, TradFi macro, institutional flow, DeFi aggregates, sentiment, ETF flows, and crypto-linked equities), written extensive context and manager documents, and collected six prior AI-generated research memos that converge on the same flagship angle.

**What data exists.** 484 curated CSVs, all standardized to an ISO `date` first column with UTC calendar (enforced by a reproducible 11-step curation pipeline in [tools/data_curation/](tools/data_curation/)). The canonical inventory is in [Data/MASTER_DATA.md](Data/MASTER_DATA.md) (with an LLM-friendly mirror at [Data/MASTER_DATA.txt](Data/MASTER_DATA.txt)) and the full provenance/audit trail lives in [Data/_meta/curation_log.md](Data/_meta/curation_log.md). See §3 and §6 for the source-by-source breakdown and §16 for quality flags.

**What prior AI outputs say.** Seven memos in [AI Outputs/](AI%20Outputs/) — `FINAL_SYNTHESIS_TOP5_PROJECTS.md`, `research_memo.md`, `Crypto Research Agenda Development.md`, `deep-research-report.md`, `Beyond Correlation_ Quantifying Bitcoin's New Role *.md`, `txt output.md`, and `txt output p2.md` — plus the two manager docs [Manager_Outline.md](Manager_Outline.md) and [Manager_workflow.md](Manager_workflow.md) — independently converge on one flagship paper:

> **BTC (and ETH) factor-block evolution around the January 2024 spot-ETF launch, measured primarily by rolling OLS + block-level partial R² as the headline figure, hardened with pre-specified Bai-Perron / Chow break tests, and extended by small VAR / FEVD systems (BTC-return × ETF-flow × stablecoin-growth × VIX).** See §7 for the convergence evidence and §16 for the only significant dissenter ([AI Outputs/txt output.md](AI%20Outputs/txt%20output.md), which elevates Double Machine Learning as the headline — directly contradicting [Context/00_project_context_and_goals.md](Context/00_project_context_and_goals.md) and the explicit "ML only as support" rule in [Context/03_quantitative_methods_and_analysis_menu.md](Context/03_quantitative_methods_and_analysis_menu.md)).

**Best path forward.** Execute Strategy A (Empirical Factor-Evolution Paper) with rolling OLS + block partial R² as the anchor figure, Bai-Perron + Chow as formal break tests, and a compact 4-variable VAR/FEVD as dynamic confirmation. Reject Strategy D (dashboard/data product) and treat Strategies B (ETF-flow ARDL) and C (stablecoin monetary-channel) as optional robustness pillars or follow-on papers. Rationale, scoring, and alternatives are in §10. Confidence in this recommendation: **92%** (five of seven AI outputs + six Context files + both manager docs agree; the residual 8% reflects (a) the unresolved TVP-VAR-vs-rolling-OLS methodological fork flagged in §16 and (b) the small but non-trivial citation-hallucination risk in two of the longer memos).

**Immediate first-sprint outcome.** Within two weeks, the team should hold: (i) a written `research_spec.md` + `methods_spec.md` locked in [docs/specs/](docs/specs/), (ii) three analytical panels (BTC-native daily, ETH-native daily, cross-asset daily) materialized as Parquet, (iii) a replicable block partial-R² heatmap at 180-day and 365-day rolling windows, (iv) a first Bai-Perron run with pre-specified 2024-01-11 / 2024-07-23 / 2024-04-20 break candidates, and (v) agent operating plumbing in place (`.cursor/rules/`, `prompts/`, `AGENTS.md`). See §17 for the roadmap.

---

## 2. Method and Provenance

This plan was produced by a manager agent (Opus 4.7) using a four-subagent parallel-exploration pattern (see §8). Each subagent received a scoped assignment with an explicit no-write contract and returned a structured report with file-path citations and confidence flags.

**How each subagent was scoped:**

| Subagent | Assignment | Files read (approx.) | Output |
|---|---|---|---|
| Data Cartographer | Recursive map of `Data/` with schema samples and quality flags | 13+ READMEs, 3 CSV samples, [Data/MASTER_DATA.md](Data/MASTER_DATA.md), [Data/_meta/curation_log.md](Data/_meta/curation_log.md) | Hierarchical tree, per-source summary, CSV schema samples, 10 quality flags |
| Prior-AI Synthesizer | All `AI Outputs/` + all `Context/` + manager docs | 7 AI outputs, 6 Context files, 2 Manager docs, `Grok Convo.txt` (sampled) | Per-file thesis/claims/weaknesses, cross-output convergence and contradictions |
| Workflow Architect | `cursor-ai-tips-main/` and `awesome-cursor-skills-main/resources/` | ~15 tips + ~12 SKILL.md files | Top-10 patterns, 6-file `.cursor/rules/` recommendation |
| Tools & Pipeline Auditor | `tools/` + `harvest_defillama_simple.py` + `.gitignore` + `FinancialEconometrics-master/` | 15 Python scripts | Pipeline order, gaps, 5 concrete remediations |

**What was sampled vs. read in full.** All markdown files under `AI Outputs/`, `Context/`, and the manager docs were read in full. The `tools/` Python scripts were all read in full (≤700 LOC each). CSV schemas were sampled (first ~10 rows of 3 representative files). The PDF at [crypto_quant_methods_meeting_note.pdf](crypto_quant_methods_meeting_note.pdf) was **not** directly parsed (PDF extraction not run in this environment); its content is summarized second-hand via [Manager_Outline.md](Manager_Outline.md) (§"PDF Meeting Note Summary"). The Julia teaching notebooks under [FinancialEconometrics-master/FinancialEconometrics-master/](FinancialEconometrics-master/FinancialEconometrics-master/) were **not** read (reference material only; 27 `.ipynb` files and 33 `.jl` source files).

**How claims are cited.** Every evidence-based claim in this plan cites at least one file path using a markdown link. Claims that originate from prior AI outputs are tagged **[AI-output claim]** and treated as hypothesis until verified. Claims with <90% confidence list the specific evidence that is missing. The verification queue is consolidated in §5.

**What was not done in this plan and why.**

- No new data was ingested, no CSV was modified, no analysis was executed.
- No citations in `AI Outputs/Beyond Correlation_ *.md` or `AI Outputs/deep-research-report.md` were independently verified (flagged as a P1 task in §17).
- No duplicates were deleted. In particular, the near-duplicate pair [AI Outputs/txt output p2.md](AI%20Outputs/txt%20output%20p2.md) ≈ [Context/00_project_context_and_goals.md](Context/00_project_context_and_goals.md) was left intact (dedupe is a P2 ticket in §17 so no content is silently lost).
- No `.env` file was read.

---

## 3. Source Inventory

This section is a map-of-maps. Detailed schemas are in §6; detailed AI-output synthesis is in §7.

### 3.1 Data — `C:\Dev\Projects\CryptoQuant\Data\`

484 curated CSVs across 7 sources, ~1.81M total rows (per [Data/MASTER_DATA.md](Data/MASTER_DATA.md)). All files enforce the contract: first column is `date` (ISO `YYYY-MM-DD`, UTC, ascending); no `timestamp_utc`; daily granularity unless the underlying series is natively weekly/monthly.

| Source folder | File count | Coverage | Representative file |
|---|---:|---|---|
| [Data/AlternativeMe/](Data/AlternativeMe/) | 1 | Crypto sentiment, daily 2018-02 → present | `fear_greed_index__daily.csv` |
| [Data/Artemis/](Data/Artemis/) | 48 | ETF AUM, DEX, perps, lending, RWA, stablecoins | `Bitcoin ETFs AUM.csv`, `Chains - Stablecoin Supply.csv` |
| [Data/CryptoQuant/](Data/CryptoQuant/) | 345 | On-chain BTC/ETH/USDC/USDT/WBTC, daily | `Bitcoin Price & Volume - Spot, All Exchanges, BTC-USD - Day.csv` |
| [Data/DefiLlama/](Data/DefiLlama/) | ~28 | TVL, stablecoin mcap, CEX flows, chain metrics, RWA, ETFs | `tvl_by_chain_long_daily.csv`, `stablecoin_mcap_by_defillama_id__daily.csv` |
| [Data/FRED/](Data/FRED/) | 21 | Macro: rates curve, credit, vol, FX, commodity, policy | `DFF__daily.csv`, `VIXCLS__daily.csv`, `fred_macro_panel__daily.csv` |
| [Data/Farside ETF Data/](Data/Farside%20ETF%20Data/) | 3 | US spot ETF daily net flows (BTC, ETH, SOL) | `farside_btc_etf_flows__daily.csv` |
| [Data/Tradingview/](Data/Tradingview/) | 38 | CME futures, DVOL, equity/index/semis/miners/crypto-eqs | `CME_BTC_front_month_futures__daily.csv`, `MSTR_microstrategy_stock__daily.csv` |
| [Data/_meta/](Data/_meta/) | 3 | Manifests + curation log | `curation_log.md`, `raw_manifest.csv`, `curated_manifest.csv` |

### 3.2 AI Outputs — `C:\Dev\Projects\CryptoQuant\AI Outputs\`

Seven markdown memos. The canonical decision memo is [AI Outputs/FINAL_SYNTHESIS_TOP5_PROJECTS.md](AI%20Outputs/FINAL_SYNTHESIS_TOP5_PROJECTS.md), which compresses the other five long memos into a ranked top-5. Full per-file analysis is in §7.

### 3.3 Context — `C:\Dev\Projects\CryptoQuant\Context\`

Six numbered files (00..05) that collectively form the project spec:

- [Context/00_project_context_and_goals.md](Context/00_project_context_and_goals.md) — team, constraints, do/do-not list.
- [Context/01_research_framework_and_candidate_pathways.md](Context/01_research_framework_and_candidate_pathways.md) — 5-block factor architecture, four candidate pathways (A preferred).
- [Context/02_data_sources_factor_blocks_and_sample_design.md](Context/02_data_sources_factor_blocks_and_sample_design.md) — modular 3-sample design (A common, B BTC-long, C specialized-short).
- [Context/03_quantitative_methods_and_analysis_menu.md](Context/03_quantitative_methods_and_analysis_menu.md) — 11-method catalogue from descriptive to advanced (ML only as support).
- [Context/04_cursor_operating_model_and_agent_workflow.md](Context/04_cursor_operating_model_and_agent_workflow.md) — lead-reviewer agent roles, 7-phase workflow.
- [Context/05_state_of_the_art_tooling_notes_2026-04-15.md](Context/05_state_of_the_art_tooling_notes_2026-04-15.md) — tooling landscape snapshot (dated 2026-04-15).

### 3.4 Manager & Meeting documents — repo root

- [Manager_Outline.md](Manager_Outline.md) — authoritative PM-level synthesis: paper direction, target repo layout, data-engineering rules, student split, risks, first sprint.
- [Manager_workflow.md](Manager_workflow.md) — 14-phase execution playbook (setup → paper-ready artifacts) with per-phase script paths and acceptance criteria.
- [crypto_quant_methods_meeting_note.pdf](crypto_quant_methods_meeting_note.pdf) — meeting minutes confirming the same factor-block / Bai-Perron / comparative BTC/ETH angle (read second-hand via Manager_Outline).
- [Grok Convo.txt](Grok%20Convo.txt) — Grok-4.20 Cursor-Pro mastery session; proposes an alternative (flatter) folder layout and a 5-repo reference corpus.

### 3.5 Workflow references — repo root (to be moved to `references/` in §19)

- [cursor-ai-tips-main/](cursor-ai-tips-main/) — 40+ workflow tips; most valuable files in §8.
- [awesome-cursor-skills-main/](awesome-cursor-skills-main/) — ~60 `SKILL.md` files under `resources/`; shortlist in §8.

### 3.6 Tools — `C:\Dev\Projects\CryptoQuant\tools\`

| Folder | Purpose |
|---|---|
| [tools/data_collection/](tools/data_collection/) | Ad-hoc ingesters: `fetch_fred.py`, `fetch_fear_greed.py`, `fetch_farside_etf_csv.py`, `organize_cryptoquant_metrics.py`; plus root-level [harvest_defillama_simple.py](harvest_defillama_simple.py) |
| [tools/data_curation/](tools/data_curation/) | 11 numbered curation scripts 01..11 + shared `_common.py`; produces `MASTER_DATA.{md,txt,csv}` via script `06_build_inventory.py` |

### 3.7 Unread or Skipped Files

| File / folder | Reason |
|---|---|
| [crypto_quant_methods_meeting_note.pdf](crypto_quant_methods_meeting_note.pdf) | PDF extraction not run; summarized second-hand via Manager_Outline. P1: parse with `pypdf` and verify summary. |
| [FinancialEconometrics-master/FinancialEconometrics-master/](FinancialEconometrics-master/FinancialEconometrics-master/) | External Julia teaching material (Söderlind UNISG MSc course); 27 notebooks not read. Not a runtime dependency — keep as `references/` reading library. |
| [defillama-api (2).json](defillama-api%20%282%29.json) | 552 KB OpenAPI spec consumed by the DefiLlama harvester; not read cell-by-cell. Not an analysis artifact. |
| [Data/DefiLlama/_raw_parts/](Data/DefiLlama/_raw_parts/) | 16 archived multi-part downloads + 5 near-duplicates explicitly quarantined in `curation_log.md` step 03 / step 10. Do not analyze. |
| Individual CSVs in Data (beyond 3 sampled) | Schema inferred from standardized contract and [Data/MASTER_DATA.md](Data/MASTER_DATA.md); full content to be loaded on-demand during analysis. |

---

## 4. Inferred Project Objective

### 4.1 Primary objective (recommended)

> **Document and explain the time-varying factor-block composition of BTC and ETH daily returns around the 2024 spot-ETF institutionalization event, using rolling OLS with block-level partial R² as the headline diagnostic, Bai-Perron / Chow break tests with pre-specified event dates as formal break evidence, and a compact VAR / FEVD system as dynamic confirmation.**

This objective satisfies the project's hard constraints in [Context/00_project_context_and_goals.md](Context/00_project_context_and_goals.md): it is quantitative/statistical (not ML-predictive), TradFi↔crypto bridging, uses existing data only, is explanatory rather than trading-strategic, and does not overclaim causality. It is supported by five of seven AI outputs, all six Context files, both manager docs, and the meeting note (second-hand).

Confidence: **92%**. Residual uncertainty stems from:

- The methodological fork between "rolling OLS + Bai-Perron" (preferred by [Manager_Outline.md](Manager_Outline.md), [AI Outputs/Crypto Research Agenda Development.md](AI%20Outputs/Crypto%20Research%20Agenda%20Development.md), [AI Outputs/research_memo.md](AI%20Outputs/research_memo.md)) and "TVP-VAR with stochastic volatility" (preferred by [AI Outputs/deep-research-report.md](AI%20Outputs/deep-research-report.md), [AI Outputs/Beyond Correlation_ Quantifying Bitcoin's New Role in Financial Markets Through Structural Breaks, Flow Dynamics, and Systemic Risk.md](AI%20Outputs/Beyond%20Correlation_%20Quantifying%20Bitcoin%27s%20New%20Role%20in%20Financial%20Markets%20Through%20Structural%20Breaks%2C%20Flow%20Dynamics%2C%20and%20Systemic%20Risk.md)). Resolution in §10 and §16.
- Citation-verification risk in the two TVP-VAR memos.

### 4.2 Plausible alternative objectives

| Alternative | Core question | Supporting file(s) | Why not primary |
|---|---|---|---|
| **Alt-1: ETF-flow price-impact paper** | Do daily Farside ETF flows Granger-cause BTC/ETH returns & volatility? ARDL + FEVD + event study. | [AI Outputs/FINAL_SYNTHESIS_TOP5_PROJECTS.md](AI%20Outputs/FINAL_SYNTHESIS_TOP5_PROJECTS.md) (ranked #2), [AI Outputs/deep-research-report.md](AI%20Outputs/deep-research-report.md) (Proposal 2) | Narrower scope; less methodologically differentiated than factor-evolution; best kept as robustness pillar for primary. |
| **Alt-2: Stablecoin shadow-money channel** | Does USDT/USDC supply growth transmit macro monetary policy into crypto vol and BTC returns? Panel FE + local projections. | [AI Outputs/FINAL_SYNTHESIS_TOP5_PROJECTS.md](AI%20Outputs/FINAL_SYNTHESIS_TOP5_PROJECTS.md) (ranked #3), [AI Outputs/deep-research-report.md](AI%20Outputs/deep-research-report.md) (Proposal 3), [AI Outputs/Beyond Correlation_ ....md](AI%20Outputs/Beyond%20Correlation_%20Quantifying%20Bitcoin%27s%20New%20Role%20in%20Financial%20Markets%20Through%20Structural%20Breaks%2C%20Flow%20Dynamics%2C%20and%20Systemic%20Risk.md) (Proposal 3) | Econometric identification harder (endogeneity, simultaneity with policy); data on FX-denominated usage is sparse. |
| **Alt-3: DAT / MSTR premium collapse event study** | Did the digital-asset-treasury premium decouple from NAV, and how did the market price equity-based BTC exposure? | [AI Outputs/FINAL_SYNTHESIS_TOP5_PROJECTS.md](AI%20Outputs/FINAL_SYNTHESIS_TOP5_PROJECTS.md) (ranked #5), [Data/DefiLlama/DATs/](Data/DefiLlama/DATs/) | High novelty but thin data window (post-2023); survivorship risk in DAT snapshot; better as sidebar. |
| **Alt-4: Liquidation-cascade event study** | Characterize the funding-rate / OI / taker-ratio dynamics around stress events (2022-06, 2022-11, 2024-08). | [AI Outputs/FINAL_SYNTHESIS_TOP5_PROJECTS.md](AI%20Outputs/FINAL_SYNTHESIS_TOP5_PROJECTS.md) (ranked #4), [Data/CryptoQuant/BTC/Derivatives/](Data/CryptoQuant/BTC/Derivatives/) | Event identification is subjective; high narrative value but not the strongest statistical anchor. |

### 4.3 Why the primary wins

- **Evidence fit.** The inventory already contains: macro panel ([Data/FRED/fred_macro_panel__daily.csv](Data/FRED/fred_macro_panel__daily.csv)), institutional flow ([Data/Farside ETF Data/](Data/Farside%20ETF%20Data/), [Data/Artemis/Bitcoin ETFs AUM.csv](Data/Artemis/Bitcoin%20ETFs%20AUM.csv)), liquidity ([Data/DefiLlama/ChainMetrics/](Data/DefiLlama/ChainMetrics/), [Data/Artemis/DEX - Spot Volume.csv](Data/Artemis/DEX%20-%20Spot%20Volume.csv)), BTC-native ([Data/CryptoQuant/BTC/](Data/CryptoQuant/BTC/)), ETH-native ([Data/CryptoQuant/ETH/](Data/CryptoQuant/ETH/)). All five factor blocks are populated before any analysis begins.
- **Methodological defensibility.** Rolling OLS + block partial R² is a ubiquitous, reviewer-legible diagnostic; Bai-Perron is a standard break test with pre-registered dates; FEVD is a standard impulse-decomposition tool. No method in this spine is exotic, controversial, or dependent on Bayesian priors that require defense.
- **Narrative fit.** "Institutionalization changed Bitcoin's factor structure" is a publishable, socially legible story that maps directly onto the 2024-01-11 BTC-ETF launch (and 2024-07-23 ETH-ETF launch as a second break candidate).
- **Time budget.** A 3-person MSc team can produce block partial-R² plots and Bai-Perron tables in the 6-week window [Context/00](Context/00_project_context_and_goals.md) implies; TVP-VAR with stochastic volatility (the main competing approach) is at the edge of feasibility without heavy Bayesian-econometrics specialization.

---

## 5. Current State of Evidence

A four-way classification of everything we "know" so far:

### 5.1 Directly observed (from raw files, verified by subagent reads)

- `Data/` contains 484 standardized CSVs across 7 sources — verified via [Data/MASTER_DATA.md](Data/MASTER_DATA.md) and schema sample of 3 CSVs.
- All time-series CSVs use `date` first column, ISO format — verified on [Data/CryptoQuant/BTC/Market Data/Bitcoin Price & Volume - Spot, All Exchanges, BTC-USD - Day.csv](Data/CryptoQuant/BTC/Market%20Data/), [Data/FRED/VIXCLS__daily.csv](Data/FRED/VIXCLS__daily.csv), [Data/AlternativeMe/fear_greed_index__daily.csv](Data/AlternativeMe/fear_greed_index__daily.csv).
- Pre-specified event dates are: **BTC spot-ETF launch 2024-01-11, ETH spot-ETF launch 2024-07-23, Bitcoin halving 2024-04-20** (per [Manager_workflow.md](Manager_workflow.md) §Phase 10).
- Five factor blocks are documented with specific variables in [Context/02](Context/02_data_sources_factor_blocks_and_sample_design.md) and [Manager_Outline.md](Manager_Outline.md).
- Tool pipeline has: path bugs in [tools/data_collection/fetch_farside_etf_csv.py](tools/data_collection/fetch_farside_etf_csv.py) line 135 and [tools/data_collection/organize_cryptoquant_metrics.py](tools/data_collection/organize_cryptoquant_metrics.py) lines 16-17, absolute backup path in [tools/data_curation/07_validate.py](tools/data_curation/07_validate.py) line 34, hardcoded `2026-04-17` date globs in `02_dedupe_defi.py`, `03_merge_defi_parts.py`, `10_clean_new_defi.py`.
- Near-duplicates intentionally quarantined at [Data/DefiLlama/_raw_parts/duplicates/](Data/DefiLlama/_raw_parts/duplicates/) per [Data/_meta/curation_log.md](Data/_meta/curation_log.md) Steps 02 & 10.

### 5.2 Prior-AI claims (treat as hypothesis until verified)

- **[AI-output claim]** "Spot-BTC-ETF launch (2024-01-11) is the single most important structural break in post-2020 BTC return dynamics." — [AI Outputs/FINAL_SYNTHESIS_TOP5_PROJECTS.md](AI%20Outputs/FINAL_SYNTHESIS_TOP5_PROJECTS.md). To verify: run Bai-Perron with unknown-break dates and confirm 2024-01-11 ± 10 days appears as statistically significant (§9 Q1).
- **[AI-output claim]** "BTC's correlation with SPY/QQQ/Nasdaq has risen structurally post-ETF." — implicit across memos. To verify: rolling 60/180-day Pearson ρ(BTC-return, SPY-return) with Chow break at 2024-01-11 (§15 Figure F2).
- **[AI-output claim]** "Stablecoin supply growth Granger-causes BTC volatility." — [AI Outputs/deep-research-report.md](AI%20Outputs/deep-research-report.md) Proposal 3, [AI Outputs/Beyond Correlation_ ...md](AI%20Outputs/Beyond%20Correlation_%20Quantifying%20Bitcoin%27s%20New%20Role%20in%20Financial%20Markets%20Through%20Structural%20Breaks%2C%20Flow%20Dynamics%2C%20and%20Systemic%20Risk.md). To verify: small VAR with [Data/DefiLlama/Stablecoins/stablecoin_mcap_by_defillama_id__daily.csv](Data/DefiLlama/Stablecoins/stablecoin_mcap_by_defillama_id__daily.csv) against a BTC realized-vol series.
- **[AI-output claim]** "Miner→exchange flows have decoupled from price since 2023." — [AI Outputs/research_memo.md](AI%20Outputs/research_memo.md). To verify: rolling correlation of [Data/CryptoQuant/BTC/Miner Flows/Bitcoin Miner to Exchange Flow (Total) - All Miners, All Exchanges - Day.csv](Data/CryptoQuant/BTC/Miner%20Flows/) vs. BTC return.

### 5.3 Claims needing verification (higher priority)

- **Citation audit — P0.** All 2026 arXiv IDs and LinkedIn links in [AI Outputs/Beyond Correlation_ ...md](AI%20Outputs/Beyond%20Correlation_%20Quantifying%20Bitcoin%27s%20New%20Role%20in%20Financial%20Markets%20Through%20Structural%20Breaks%2C%20Flow%20Dynamics%2C%20and%20Systemic%20Risk.md) and [AI Outputs/deep-research-report.md](AI%20Outputs/deep-research-report.md). Manager_Outline explicitly treats deep-research outputs as "hypothesis until citation-verified". Do not reuse any of these citations in a draft paper until each DOI/arXiv ID is resolved through Context7 or scholar.
- **Hormuz-blockade / SEC-commodity-classification events** in [AI Outputs/txt output.md](AI%20Outputs/txt%20output.md). No corroborating evidence in the repo. Treat as unsupported until a dated press release or academic citation is produced.
- **ETH L1-vs-L2 aggregation policy**. [Manager_Outline.md](Manager_Outline.md) warns against summing L1 and L2 addresses as "unique users" and prescribes separate outputs. No L2-specific data table exists yet in [Data/CryptoQuant/ETH/](Data/CryptoQuant/ETH/); need to build from [Data/DefiLlama/ChainMetrics/](Data/DefiLlama/ChainMetrics/) (Arbitrum, Optimism, Base, zkSync, etc.).
- **PDF meeting note content**. Second-hand via Manager_Outline. Parse [crypto_quant_methods_meeting_note.pdf](crypto_quant_methods_meeting_note.pdf) directly with `pypdf` and confirm alignment.

### 5.4 Open questions

- Should the primary dependent variable be BTC log-return, excess BTC log-return (over T-bill), or annualized realized vol? (Multiple YZs in the memos. Recommendation: both return and realized vol as separate panels.)
- Which rolling window should be the headline? [Manager_workflow.md](Manager_workflow.md) §Phase 9 specifies 90 / 180 / 365 days with 180 as main and 60 as exploratory-only. Lock this in `methods_spec.md`.
- What is the common sample start date for Sample A? Defaults: 2021-01-01 (per [Context/02](Context/02_data_sources_factor_blocks_and_sample_design.md)) but some ETF and RWA series begin later. Need a missingness-adjusted cutoff.
- How is "post-ETF" operationalized — strictly 2024-01-11+ or a buffer around it? Pre-register in `research_spec.md`.
- Is `AI Outputs/txt output p2.md` ≈ `Context/00_project_context_and_goals.md` truly byte-for-byte duplicate or does one have content unique to it? Diff before removing.

---

## 6. Dataset Catalog

A table of every source folder, anchored in schema samples and the `MASTER_DATA` catalog. Confidence reflects the subagent's verification depth (READMEs read + schema samples for three). Dates are from the per-source `MASTER_DATA` entries.

| Dataset / file group | Type | Description | Key fields | Date range | Quality notes | Potential use | Confidence |
|---|---|---|---|---|---|---|---:|
| [Data/AlternativeMe/fear_greed_index__daily.csv](Data/AlternativeMe/fear_greed_index__daily.csv) | Sentiment | Crypto Fear & Greed composite 0-100 | date, fng_value, fng_classification | 2018-02-01 → present | None; simple 3-col | Sentiment factor in Block 1 (macro); robustness control | 95% |
| [Data/Artemis/](Data/Artemis/) | Cross-chain + institutional | 48 CSVs: ETF AUM (BTC/ETH/SOL), DEX volume, perps OI, lending, RWA, stablecoin supply | date (per file), metric-specific numerics | Mostly 2020+ | One snapshot file (`Artemis - Digital Asset Treasuries Overview.csv`) has `symbol` not `date` — exclude from date-normalized joins | Institutional block (ETFs, perps OI); DeFi block | 85% |
| [Data/CryptoQuant/BTC/](Data/CryptoQuant/BTC/) | On-chain BTC | 14 subfolders, ~200 CSVs: Addresses, Derivatives, Exchange Flows, Market Indicator, Miner Flows, Network Indicator, Supply, Transactions, Fund Data, Inter Entity Flows | date, metric-specific | 2009+ (pre-exchange rows empty) | Early rows (pre-2012) have empty OHLC / zero volume — filter by first non-null | BTC-native block (entire spine of primary objective) | 95% |
| [Data/CryptoQuant/ETH/](Data/CryptoQuant/ETH/) | On-chain ETH | 10 subfolders, ~100 CSVs incl. unique `ETH 2.0/` | date, metric-specific | Genesis (2015) + | L1 only — no L2 data here. Need DefiLlama/Artemis for L2 | ETH-native block | 95% |
| [Data/CryptoQuant/USDC/](Data/CryptoQuant/USDC/), [USDT (TRX)/](Data/CryptoQuant/USDT%20%28TRX%29/), [USDT ETH/](Data/CryptoQuant/USDT%20ETH/), [WBTC/](Data/CryptoQuant/WBTC/) | Stablecoins + wrapped | Address/flow/transaction metrics per stablecoin chain variant | date, metric-specific | 2018-2020+ | **Asymmetric coverage**: USDT(TRX) has only Addresses + Exchange Flows; USDT-ETH has 6 subfolders; USDC has 4; WBTC has 2. Null-handling required for any join across these. | Stablecoin monetary-channel analysis (Strategy C) | 80% |
| [Data/DefiLlama/TVL/Daily/](Data/DefiLlama/TVL/Daily/) | Cross-chain TVL | `tvl_all_chains_daily.csv`, `tvl_by_chain_{long,wide}_daily.csv` | date, chain, tvl_usd (or wide) | 2020+ | None notable | Liquidity block; chain-dominance robustness | 90% |
| [Data/DefiLlama/TVL/Snapshot/](Data/DefiLlama/TVL/Snapshot/) | Cross-chain snapshot | `tvl_chains_current.csv`, `tvl_protocols_current.csv` | chain/protocol, tvl | Single-timestamp | **Snapshot, not time-series** — exclude from date-joined panels | One-off cross-section tables | 95% |
| [Data/DefiLlama/Stablecoins/](Data/DefiLlama/Stablecoins/) | Stablecoin mcap | `stablecoin_mcap_by_defillama_id__daily.csv` (merged from 7 parts) | date, per-issuer-id mcap | 2021+ | Merged by [tools/data_curation/03_merge_defi_parts.py](tools/data_curation/03_merge_defi_parts.py); parts archived at `_raw_parts/stablecoin_mcap/` (do not use directly) | Stablecoin block; Strategy C core | 90% |
| [Data/DefiLlama/CEX/cex_net_inflows_by_exchange__daily.csv](Data/DefiLlama/CEX/cex_net_inflows_by_exchange__daily.csv) | CEX flows | Net inflows by exchange (merged 3 parts) | date, per-exchange net_flow | 2021+ | Same provenance caveat as stablecoins | Institutional/liquidity robustness | 85% |
| [Data/DefiLlama/ChainMetrics/](Data/DefiLlama/ChainMetrics/) | Chain metrics daily | 7 CSVs: `all_chains_metrics__daily.csv`, `chain_tvl_dominance__daily.csv`, `ethereum_metrics__daily.csv`, `solana_metrics__daily.csv`, `all_dex_metrics__daily.csv`, `all_chains_perp_volume_by_protocol__daily.csv` | date, chain, metrics | 2020+ | None notable | ETH L1 vs. L2 via this source (+ Arbitrum, OP, Base); liquidity block | 85% |
| [Data/DefiLlama/RWA/](Data/DefiLlama/RWA/) | RWA mcap | 5 CSVs: onchain/active mcap all, by category | date, mcap | 2021+ | None notable | Thematic sidebar; not main spine | 80% |
| [Data/DefiLlama/ETFs/](Data/DefiLlama/ETFs/) | DefiLlama ETF overview | `etf-overview.csv`, `etf-history.csv` | date, ticker, aum/flow | 2024+ | Overlaps with Farside; cross-check values | Cross-validation vs Farside | 75% |
| [Data/DefiLlama/DATs/dat-institutions.csv](Data/DefiLlama/DATs/dat-institutions.csv) | Digital-Asset Treasuries | Snapshot of listed DATs | institution, metrics | Snapshot | Survivorship and entry-date issues; thin | Strategy D sidebar | 65% |
| [Data/FRED/fred_macro_panel__daily.csv](Data/FRED/fred_macro_panel__daily.csv) | Macro combined | Business-day-aligned wide panel of 19 series | date + 19 cols | Per-series; 1962+ for DGS10 | Daily panel has many natural NaNs (weekends, monthly series reindexed) — use `ffill` or calendar reindex pre-join | Macro block (rates, VIX, DXY, CPI, UNRATE, WTI, NFCI, STLFSI4, EPU, SOFR, RRP) | 95% |
| [Data/FRED/BAMLH0A0HYM2__daily.csv](Data/FRED/BAMLH0A0HYM2__daily.csv) | Credit spread | HY OAS | date, value | 2023-04-18 → 2026-04-16 | **Short window vs. FRED history (1996+)** — possible truncated download; re-fetch if we want longer sample | Credit-stress robustness | 60% |
| [Data/Farside ETF Data/farside_btc_etf_flows__daily.csv](Data/Farside%20ETF%20Data/farside_btc_etf_flows__daily.csv) | Institutional flow | Net daily $m flows per BTC ETF ticker (IBIT, FBTC, BITB, ARKB, …) | date, per-ticker flow | 2024-01-11+ | Trading-day calendar (US); outflows negative | Institutional block (main ETF signal) | 95% |
| [Data/Farside ETF Data/farside_eth_etf_flows__daily.csv](Data/Farside%20ETF%20Data/farside_eth_etf_flows__daily.csv) | Institutional flow | ETH ETFs | date, per-ticker flow | 2024-07-23+ | Same | Institutional block (ETH) | 95% |
| [Data/Farside ETF Data/farside_sol_etf_flows__daily.csv](Data/Farside%20ETF%20Data/farside_sol_etf_flows__daily.csv) | Institutional flow | SOL ETFs | date, per-ticker flow | 2026-03-25 → 2026-04-10 (12 rows) | **Very thin series** — not usable for 2024 analysis | Future work | 60% |
| [Data/Tradingview/Daily/](Data/Tradingview/Daily/) | TradFi + crypto-eq daily | 27 CSVs: CME futures (BTC/ETH/SOL/Micro), DVOL, DXY, SPY, QQQ, IWM, XLK, SMH, SOXX, MARA, RIOT, MSTR, COIN, CRCL, GLD, XAUUSD, basis ratios | date, OHLCV | Per-asset | Tradingview naming was fixed by [tools/data_curation/09_reorg_tradingview.py](tools/data_curation/09_reorg_tradingview.py); DXY duplicates quarantined | Macro / equity cross-asset block | 90% |
| [Data/Tradingview/Weekly/](Data/Tradingview/Weekly/) | TradFi weekly | 11 CSVs: continuous futures, major indices weekly | date, OHLCV | Per-asset | — | Weekly robustness sample | 90% |

**Implications for analysis:**

1. **Core primary-objective panel** requires (a) BTC daily return and realized vol ([Data/CryptoQuant/BTC/Market Data/](Data/CryptoQuant/BTC/Market%20Data/)), (b) 5-block regressor set: macro ([Data/FRED/fred_macro_panel__daily.csv](Data/FRED/fred_macro_panel__daily.csv)), institutional ([Data/Farside ETF Data/farside_btc_etf_flows__daily.csv](Data/Farside%20ETF%20Data/farside_btc_etf_flows__daily.csv) + [Data/Artemis/Bitcoin ETFs AUM.csv](Data/Artemis/Bitcoin%20ETFs%20AUM.csv)), liquidity ([Data/DefiLlama/ChainMetrics/all_chains_metrics__daily.csv](Data/DefiLlama/ChainMetrics/all_chains_metrics__daily.csv) + [Data/DefiLlama/TVL/Daily/tvl_all_chains_daily.csv](Data/DefiLlama/TVL/Daily/tvl_all_chains_daily.csv) + [Data/Artemis/DEX - Spot Volume.csv](Data/Artemis/DEX%20-%20Spot%20Volume.csv)), BTC-native ([Data/CryptoQuant/BTC/Exchange Flows/](Data/CryptoQuant/BTC/Exchange%20Flows/), [Data/CryptoQuant/BTC/Miner Flows/](Data/CryptoQuant/BTC/Miner%20Flows/), [Data/CryptoQuant/BTC/Market Indicator/](Data/CryptoQuant/BTC/Market%20Indicator/)), ETH-native ([Data/CryptoQuant/ETH/](Data/CryptoQuant/ETH/)).
2. **Sample window for headline figure**: 2021-01-01 → 2026-04-15, daily, ~1,600 obs. Sample A (common).
3. **Sample B (BTC long-history)**: 2014-01-01 → 2026-04-15, daily, ~4,500 obs, reduced regressor set (exclude ETF, stablecoin, DeFi that begin later).

---

## 7. Prior AI Output Synthesis

Per-file analysis of the seven memos in [AI Outputs/](AI%20Outputs/). Classifications: **PubReady** / **Reusable** / **Exploratory** / **Weak** / **Verify**.

| File | Main topic | Main claims | Useful content | Weaknesses | Verification needed | Reuse | Confidence |
|---|---|---|---|---|---|---|---:|
| [AI Outputs/FINAL_SYNTHESIS_TOP5_PROJECTS.md](AI%20Outputs/FINAL_SYNTHESIS_TOP5_PROJECTS.md) | Ranked decision memo across 5 prior model outputs | Flagship = factor-break paper on BTC+ETH around ETF launch; ranked #2 ETF-flow, #3 stablecoin, #4 liquidation, #5 DAT | Consolidated project plan; shared panel `panel_daily_2020-11_2026-04.parquet` specification | No independent estimation shown; consensus across unnamed models | Verify the convergence holds once individual memos are audited | Reusable (planning artifact) | 90% |
| [AI Outputs/research_memo.md](AI%20Outputs/research_memo.md) | 12-idea ranked menu → 3 final proposals | M1 ETF break = best; M3 DAT premium; M5 ETF-flow impact | DV/IV lists; method sketches (Bai-Perron, rolling OLS+HAC, FEVD); 15 robustness ideas | Subjective 1-5 scoring (no rubric); data-availability claims depend on MASTER_DATA being accurate | Cross-check with actual data coverage; rubric-ize the scoring | Reusable, verify | 85% |
| [AI Outputs/Crypto Research Agenda Development.md](AI%20Outputs/Crypto%20Research%20Agenda%20Development.md) | Rejection-first agenda: picks Pathway A, rejects pure-ETF / pure-ML / pure-DAT | Final proposal A = time-varying factor blocks; B = ETF flows + CME basis; C = stablecoin plumbing | Clean coding-task breakdown for Proposal A | "Recent themes" listed without per-item citations | External citation audit | Reusable | 88% |
| [AI Outputs/deep-research-report.md](AI%20Outputs/deep-research-report.md) | 15-paper TVP-VAR-forward agenda | #1 Bitcoin's New Normal (TVP-VAR-SV); #2 ETF-flow ARDL+FEVD; #3 Stablecoin monetary channel | Heavy methodological rigor; literature synthesis | 2026 arXiv IDs unverified; TVP-VAR-SV is much harder than rolling OLS | Citation audit; method feasibility check vs. team bandwidth | Reusable (method framing), verify (bibliography) | 75% |
| [AI Outputs/Beyond Correlation_ Quantifying Bitcoin's New Role ... .md](AI%20Outputs/Beyond%20Correlation_%20Quantifying%20Bitcoin%27s%20New%20Role%20in%20Financial%20Markets%20Through%20Structural%20Breaks%2C%20Flow%20Dynamics%2C%20and%20Systemic%20Risk.md) | Dual-approach methodology essay + 15-paper shortlist | Combine structural-break + rolling/TVP-VAR; Top-3: TVP-VAR #1, ETF-flow ARDL #2, stablecoin #3 | Strong methodological framing | Many citations have 2512 / 2602 / 2604 / 2606 arXiv prefixes + LinkedIn links (unverifiable in-repo) | Full citation audit; replace unverified sources | Reusable (framing only) | 70% |
| [AI Outputs/txt output.md](AI%20Outputs/txt%20output.md) | Causal-ML-forward agenda: DML #1, Hormuz #2, stablecoin velocity #3 | Treats exogenous 2025-26 shocks (Hormuz, SEC) as primary identification | Novel framing | **Directly contradicts Context/00 and Context/03** ("no ML headline"); Hormuz/SEC events unsourced | Evidence for the cited exogenous shocks; reconcile with Context | Exploratory; DML OK as *support*, not headline | 40% |
| [AI Outputs/txt output p2.md](AI%20Outputs/txt%20output%20p2.md) | Near-duplicate of Context/00 | Team profile + do/do-not + 7-day plan | Acts as a second copy of the project brief | Duplicate content to Context/00 | Diff against Context/00; archive duplicate or merge into single source | Reusable but consolidate | 85% |

**Cross-output convergence.** Five of seven memos agree on the flagship direction (factor-evolution around ETF launch). Six of seven agree rolling OLS + partial R² is the right headline diagnostic. Six of seven agree with Bai-Perron + pre-specified dates as formal break evidence. Five of seven mention ETF flows as a secondary paper.

**Cross-output contradictions.**

1. **ML-as-headline vs. support.** [AI Outputs/txt output.md](AI%20Outputs/txt%20output.md) elevates DML to #1; all other files demote ML to support-only. **Decision: follow Context/00 & Context/03 (ML as support).**
2. **Rolling OLS vs. TVP-VAR-SV.** Two memos prefer TVP-VAR-SV; four memos + Manager_Outline prefer rolling OLS + Bai-Perron. **Decision: rolling OLS + Bai-Perron as headline; TVP-VAR-SV optional robustness only if a team member has working Bayesian implementation.**
3. **Stablecoin-as-channel feasibility.** "Needs proprietary data" ([AI Outputs/Beyond Correlation_ ...md](AI%20Outputs/Beyond%20Correlation_%20Quantifying%20Bitcoin%27s%20New%20Role%20in%20Financial%20Markets%20Through%20Structural%20Breaks%2C%20Flow%20Dynamics%2C%20and%20Systemic%20Risk.md)) vs. "fully supported by inventory" ([AI Outputs/deep-research-report.md](AI%20Outputs/deep-research-report.md)). **Decision: current inventory supports a supply-side channel study; reserve regional-usage breakdowns as future work.**
4. **DAT/MSTR feasibility.** Survivorship risk contested. **Decision: treat as sidebar only.**

**Strongest single narrative emerging.** Exactly the one adopted as the primary objective in §4.1.

---

## 8. Cursor Workflow Lessons Applied

From [cursor-ai-tips-main/](cursor-ai-tips-main/) and [awesome-cursor-skills-main/resources/](awesome-cursor-skills-main/awesome-cursor-skills-main/resources/), the following patterns are adopted. Non-research / web-dev patterns (React, deploy, CSS, auth, etc.) are dropped.

### 8.1 Top 10 adopted patterns

1. **Spec-First Research** — [cursor-ai-tips-main/tips/spec-first-workflow.md](cursor-ai-tips-main/cursor-ai-tips-main/tips/spec-first-workflow.md). `research_spec.md` + `methods_spec.md` live in [docs/specs/](docs/specs/) and must be read before any analysis.
2. **Research-First 5-Phase Protocol** — [cursor-ai-tips-main/tips/workflows.md](cursor-ai-tips-main/cursor-ai-tips-main/tips/workflows.md). Discovery → Plan → Critique → Execute → Audit; Discovery is no-code.
3. **Parallel Exploration** — [awesome-cursor-skills-main/resources/parallel-exploring/SKILL.md](awesome-cursor-skills-main/awesome-cursor-skills-main/resources/parallel-exploring/SKILL.md). Applied in this very plan (four subagents).
4. **Best-of-N** — [awesome-cursor-skills-main/resources/best-of-n-solving/SKILL.md](awesome-cursor-skills-main/awesome-cursor-skills-main/resources/best-of-n-solving/SKILL.md). Applied to the strategy comparison in §10; will be applied to method bake-offs (rolling OLS vs. TVP-VAR).
5. **Confidence Scoring** — [cursor-ai-tips-main/tips/confidence-scoring.md](cursor-ai-tips-main/cursor-ai-tips-main/tips/confidence-scoring.md). Every empirical claim in this plan has a confidence score; the `evidence-and-confidence.mdc` rule enforces it going forward.
6. **Parallel Red-Team Review** — [awesome-cursor-skills-main/resources/parallel-code-review/SKILL.md](awesome-cursor-skills-main/awesome-cursor-skills-main/resources/parallel-code-review/SKILL.md). Repurposed lenses: statistical validity, data integrity, reproducibility, economic interpretation.
7. **Workspace Memory** — [awesome-cursor-skills-main/resources/saving-workspace-context/SKILL.md](awesome-cursor-skills-main/awesome-cursor-skills-main/resources/saving-workspace-context/SKILL.md). Formalizes the existing [Context/](Context/) folder with "load-first, save-as-you-go" behavior; dated entries.
8. **ADRs** — [awesome-cursor-skills-main/resources/architecture-decision-records/SKILL.md](awesome-cursor-skills-main/awesome-cursor-skills-main/resources/architecture-decision-records/SKILL.md). `docs/decisions/NNN-*.md` for hard-to-reverse choices (break-test family, ETH L1/L2 policy, sample design).
9. **Systematic Debugging** — [awesome-cursor-skills-main/resources/systematic-debugging/SKILL.md](awesome-cursor-skills-main/awesome-cursor-skills-main/resources/systematic-debugging/SKILL.md). For anomalous results: reproduce → isolate → hypothesize → probe → fix. No feature-stacking to chase symptoms.
10. **Python TDD with uv** — [awesome-cursor-skills-main/resources/python-tdd-with-uv/SKILL.md](awesome-cursor-skills-main/awesome-cursor-skills-main/resources/python-tdd-with-uv/SKILL.md). Every reusable helper in [src/cqresearch/](src/cqresearch/) has a failing-test wrapper.

### 8.2 `.cursor/rules/` set (6 files — exact names and purposes)

| File | `alwaysApply` | `globs` | Purpose |
|---|---|---|---|
| `00-global-research-constitution.mdc` | true | * | Mission, non-goals, stack, naming; "Concise Architect" + "Security First" meta-rules |
| `01-spec-compliance.mdc` | true | * | Must read `docs/specs/research_spec.md` + `methods_spec.md` before any analysis; ask-before-deviating |
| `02-evidence-and-confidence.mdc` | true | * | Every empirical claim cites file:line; confidence score mandatory; if <90% list missing evidence |
| `03-data-integrity.mdc` | false | `["Data/**","src/cqresearch/data/**","scripts/**"]` | No silent mutation; preserve raw; shout-on-change |
| `04-notebook-hygiene.mdc` | false | `["notebooks/**","scripts/**","src/cqresearch/analysis/**"]` | One notebook per hypothesis; header cell with spec+vintage+seed; no hidden state |
| `05-defensive-commits.mdc` | false | * | Checkpoint before multi-file edits; ≤3 files per commit; interface-freeze for new modules |

### 8.3 `.cursor/skills/` (3 project-specific skills)

- `data-quality-check/SKILL.md` — triggers on any data-loading code; runs the curation-log invariants (date first column, ISO, no `timestamp_utc`, no duplicate dates) and returns a report.
- `structural-break-runner/SKILL.md` — triggers on "run Bai-Perron / Chow / CUSUM"; standardizes pre-specified dates from [config/events.yml](config/events.yml).
- `figure-template/SKILL.md` — triggers on "build a figure / chart"; applies the 5-block color palette and the paper-publication matplotlib rcParams.

### 8.4 Other Cursor-native practices adopted

- **Fresh-chat rule** ([cursor-ai-tips-main/tips/common-mistakes.md](cursor-ai-tips-main/cursor-ai-tips-main/tips/common-mistakes.md)): after ~20 messages, start a new chat to avoid context pollution.
- **`.env` gitignored + `.env.example` listed** ([cursor-ai-tips-main/rules/cursorrules-2026-best-practices.md](cursor-ai-tips-main/cursor-ai-tips-main/rules/cursorrules-2026-best-practices.md) §Security-First).
- **Anti-hallucination**: before importing a package, verify via `pip show` / `uv pip list`.
- **Shout protocol** ([cursor-ai-tips-main/tips/advanced-cursorrules.md](cursor-ai-tips-main/cursor-ai-tips-main/tips/advanced-cursorrules.md)): loud announcement on any edit to curated data or `_meta/` files.
- **Screenshot debugging** for charts: when figure output looks wrong, ship a PNG to the review agent alongside source code.
- **Context7 MCP** for library-doc lookups (statsmodels, arch, linearmodels) to fight hallucinated API usage.

---

## 9. Recommended Research Questions

Q-IDs are referenced throughout §11 and §15.

| ID | Question | Why it matters | Required data | Method | Expected output | Difficulty | Risks | Priority | Confidence |
|---|---|---|---|---|---|---|---|---|---:|
| **Q1** | Did BTC (ETH) daily-return factor loadings break around 2024-01-11 (2024-07-23)? | Core primary-objective question | [Data/CryptoQuant/BTC/Market Data/](Data/CryptoQuant/BTC/Market%20Data/) + 5-block regressor panel (see §6) | Rolling 180-day OLS+HAC; block partial R²; Bai-Perron with pre-spec dates | Heatmap Fig F1 + Table T1 (break-date F-stats) | Medium | Multicollinearity within blocks → rotate PCs | P0 | 92% |
| **Q2** | Has BTC's correlation with SPX / NDX / DXY / Gold risen or fallen post-ETF? | Direct test of institutionalization narrative | [Data/Tradingview/Daily/](Data/Tradingview/Daily/) + [Data/FRED/](Data/FRED/) | Rolling 60/180/365-day ρ; Chow break at 2024-01-11 | Fig F2 (4-panel rolling correlation lines) | Low | Serial correlation → use HAC SEs | P0 | 95% |
| **Q3** | Do daily ETF net flows Granger-cause BTC return/vol, and what is their FEVD share? | Institutional-channel identification | [Data/Farside ETF Data/farside_btc_etf_flows__daily.csv](Data/Farside%20ETF%20Data/farside_btc_etf_flows__daily.csv) + BTC return + VIX + stablecoin-growth | 4-variable VAR with HQ lag selection; Granger + 20-day FEVD | Fig F3 (FEVD stack); Table T2 (Granger p-values) | Medium | Sample starts 2024-01-11 → ~560 obs only | P0 | 85% |
| **Q4** | Does USDT/USDC supply growth lead BTC realized vol? | Stablecoin shadow-money channel | [Data/DefiLlama/Stablecoins/stablecoin_mcap_by_defillama_id__daily.csv](Data/DefiLlama/Stablecoins/stablecoin_mcap_by_defillama_id__daily.csv) + BTC realized vol | Bi-directional Granger; local-projection IRF 0..20 | Fig F4 (IRF); Table T3 | Medium | Endogeneity w/ BTC returns → use log-diff of supply | P1 | 75% |
| **Q5** | Do ETH-L1 and ETH-L2 factor exposures diverge post-Dencun (2024-03-13)? | ETH-specific institutionalization angle | [Data/CryptoQuant/ETH/](Data/CryptoQuant/ETH/) + [Data/DefiLlama/ChainMetrics/](Data/DefiLlama/ChainMetrics/) (Arbitrum, OP, Base, zkSync) | Rolling OLS per chain; Chow at 2024-03-13 | Fig F5 (L1 vs L2 factor panels); Table T4 | High | L2 data consistency across DefiLlama series | P1 | 65% |
| **Q6** | Has the miner→exchange flow decoupled from BTC price since 2023? | Native-block supply shift; potential break evidence | [Data/CryptoQuant/BTC/Miner Flows/Bitcoin Miner to Exchange Flow (Total) - All Miners, All Exchanges - Day.csv](Data/CryptoQuant/BTC/Miner%20Flows/) + BTC price | Rolling corr + Bai-Perron on coefficient | Fig F6; Table T5 | Low | Halving confound (2024-04-20) | P2 | 80% |
| **Q7** | Event study: 5-day CARs around BTC-ETF, ETH-ETF, halving, and 2024-08-05 crash | Sanity check on primary breaks | BTC/ETH log returns + ETF flow + realized vol | Classic event study (Brown-Warner style) with HAC | Table T6 (event-window CARs + t-stats) | Low | Small-sample CI | P1 | 90% |
| **Q8** | Diebold-Yilmaz spillover index: BTC, ETH, SPX, gold, USDT-supply, DXY pre- vs post-ETF | Cross-asset connectedness | Daily returns panel | 10-var VAR → GFEVD → spillover index; rolling 200-day | Fig F7 (rolling spillover); Table T7 (directional net) | High | Lag-selection sensitivity | P2 | 70% |

Q1 + Q2 + Q3 form the headline spine. Q4..Q8 are robustness / secondary. Dropped candidates (with reasoning) live in §10.

---

## 10. Best-of-N Strategy Comparison

Four strategies evaluated on seven dimensions. Scoring: 1-5 (5 = best); confidence is the subagent's confidence in the score.

| Dimension | **A: Factor-Evolution Paper** | **B: ETF-Flow Dynamic Paper** | **C: Stablecoin Monetary Channel** | **D: Dashboard / Data Product** |
|---|---|---|---|---|
| Evidence fit | 5 (all five blocks populated; BTC+ETH+macro+institutional+DeFi data ready) | 4 (Farside clean; sample only 2024+) | 3 (supply data ready; usage data sparse) | 4 (MASTER_DATA already a meta-inventory) |
| Novelty | 4 (factor-break angle is known; block-level partial-R² framing less so) | 3 (widely studied) | 4 (less published for USDT specifically) | 3 (many dashboards exist) |
| Feasibility (6 weeks, 3 students) | 5 (rolling OLS, Bai-Perron, VAR are standard) | 4 (short sample stretches ARDL) | 3 (LP-IRF + identification is harder) | 5 (streamlit scaffolding is easy) |
| Data requirements | Met in-repo | Met in-repo | Met in-repo; marginal (FX) | Met in-repo |
| Research value | 5 (publishable working paper) | 4 (publishable but narrower) | 4 (publishable if ID credible) | 2 (non-publishable artifact) |
| Risk of overclaiming | 3 (cross-sectional causal claims tempting — mitigate via language) | 4 (endogeneity between flow and price) | 4 (reverse causality strong) | 2 (descriptive only) |
| Deliverable quality ceiling | 5 (strong paper + figures + tables) | 4 (strong working paper) | 4 (strong working paper) | 2 (dashboard is supporting, not primary) |
| **Weighted score** | **32** | **26** | **25** | **21** |
| Confidence in scoring | 90% | 85% | 75% | 90% |

**Recommendation: Strategy A (Factor-Evolution Paper).**

Hybrid: A-primary, B-as-robustness-chapter, C-as-extension/future-work, D-rejected. The block partial-R² heatmap becomes the paper's signature figure; ETF-flow VAR/FEVD becomes the "mechanism" section; stablecoin local projection becomes an appendix robustness (or is promoted to a second paper if the team has time).

**Why D (dashboard) is rejected.** The [Context/00](Context/00_project_context_and_goals.md) do-want list explicitly asks for a "strong quantitative/statistical paper," not a product. Building a data product would consume time that should go into the paper, and no stakeholder in this project is asking for a dashboard. A run-summary README + publication-ready figures folder captures the reproducibility value without the build cost.

---

## 11. Analysis Plan

Nine workstreams. Each is an atomic unit of work with a single owner-agent role (§12). Ordering is partially parallel; dependencies shown.

### WS-1 Data Cleaning & Validation

| | |
|---|---|
| Tasks | Rerun [tools/data_curation/run_pipeline.py](run_pipeline.py) dry-run; verify 484-CSV count; check MASTER_DATA.{md,txt,csv} parity; resolve the duplicate `txt output p2.md` vs `Context/00` |
| Inputs | [Data/](Data/), [tools/](tools/), [Data/_meta/curation_log.md](Data/_meta/curation_log.md) |
| Outputs | `reports/run_summaries/WS1_run_<date>.md` + fresh `Data/_meta/curated_manifest.csv` hash-match |
| Owner agent | Data Cleaning Agent |
| Dependencies | None |
| Definition of Done | `07_validate.py` returns 0 errors; run summary committed |

### WS-2 Factor-Block Panel Build

| | |
|---|---|
| Tasks | Materialize 3 panels (A: 2021+, B: 2014+ BTC-only, C: 2024+ ETF-era) as Parquet with joined regressors | 
| Inputs | All 7 source folders |
| Outputs | [reports/panels/panel_A_daily.parquet](reports/panels/), `panel_B_btc_long.parquet`, `panel_C_etf_era.parquet` + a missingness report |
| Owner | Exploratory Analysis Agent |
| Dependencies | WS-1 |
| DoD | Each panel has no duplicate dates; block columns labeled per [config/factor_blocks.yml](config/factor_blocks.yml); row counts published in the missingness report |

### WS-3 Descriptive Diagnostics

| | |
|---|---|
| Tasks | Summary statistics, rolling correlations (60/180/365-day), regime-colored return scatters, PCA within-block |
| Inputs | WS-2 panels |
| Outputs | `notebooks/10_block_correlations.ipynb`, `reports/figures/F2_rolling_corr.*`, `reports/tables/T0_summary_stats.csv` |
| Owner | Exploratory Analysis Agent |
| Dependencies | WS-2 |
| DoD | Rolling-correlation figure compiled to PNG + SVG; PCA within each of 5 blocks produces first 2 PCs |

### WS-4 Static Regressions (Baseline)

| | |
|---|---|
| Tasks | OLS + HAC on Sample A with full block regressors; Sample B for BTC long history; Sample C for ETF-era short panel |
| Inputs | WS-2 panels |
| Outputs | `reports/tables/T_static_regressions.csv` |
| Owner | Quant Methods Agent |
| Dependencies | WS-2 |
| DoD | Regression table with 3 samples × 4 DVs (BTC ret, BTC RV, ETH ret, ETH RV); HAC SEs at Newey-West(5) |

### WS-5 Rolling Regressions & Block Partial R²

| | |
|---|---|
| Tasks | Rolling OLS with 180-day window (main) + 90/365 robustness; block partial R² computed from residualization (Frisch-Waugh) |
| Inputs | WS-2 panel A |
| Outputs | Fig F1 (block partial-R² heatmap), `reports/tables/T_rolling_coefs.csv`, one figure per block |
| Owner | Quant Methods Agent |
| Dependencies | WS-4 |
| DoD | Heatmap shows 5 rows (blocks) × 1,600 cols (days); partial-R² sums to total R² per date within tolerance |

### WS-6 Structural Break Tests

| | |
|---|---|
| Tasks | Chow tests at pre-spec dates (2024-01-11, 2024-07-23, 2024-04-20); Bai-Perron with unknown breaks; CUSUM OLS visual |
| Inputs | WS-2 panel A + panel C |
| Outputs | Table T1 (F-stat per break candidate × model), Fig F_breaks (CUSUM plots per model) |
| Owner | Quant Methods Agent |
| Dependencies | WS-5 |
| DoD | Bai-Perron identified breaks within ±30d of pre-spec dates for at least 2 of 4 models |

### WS-7 VAR / FEVD / Event Studies

| | |
|---|---|
| Tasks | 4-var VAR (BTC-ret, ETF-flow, stablecoin-growth, VIX); HQ lag; Granger; 20-day FEVD; event CARs for 4 events |
| Inputs | WS-2 panel C |
| Outputs | Fig F3 (FEVD stack), Table T2 (Granger), Table T6 (event CARs) |
| Owner | Quant Methods Agent |
| Dependencies | WS-6 |
| DoD | VAR passes stability test (all roots inside unit circle); Granger table includes Wald χ² and HAC-adjusted p-values |

### WS-8 Robustness & Support ML

| | |
|---|---|
| Tasks | Weekly sample robustness; outlier-robust OLS; LASSO-gated variable screening to justify the block-regressor choices; permutation Chow (Hansen-Johansen-style) |
| Inputs | WS-2..WS-7 outputs |
| Outputs | `reports/appendix/A_robustness.md` + tables A1..A6 |
| Owner | Quant Methods Agent (ML subtask: ML Support Agent) |
| Dependencies | WS-5..WS-7 |
| DoD | Every headline finding is reproduced with ≥1 alternative specification |

### WS-9 Writing, Red-Team Review, Packaging

| | |
|---|---|
| Tasks | Draft paper sections (intro, data, methods, results, discussion, conclusion); red-team on each section; final figures/tables package; ADRs for every non-trivial decision; run-summary README |
| Inputs | WS-1..WS-8 |
| Outputs | `reports/drafts/paper_v1.md`, `reports/figures/`, `reports/tables/`, `docs/decisions/*.md` |
| Owner | Writing Agent + Red-Team Reviewer + Final Synthesis Agent |
| Dependencies | All |
| DoD | Red-team pass with zero unresolved severity-high findings; final artifact list reproducible via `make paper` |

---

## 12. Agent/Subagent Operating Plan

### 12.1 Roles

| Role | Primary input | Primary output | Confidence threshold | Citation rule |
|---|---|---|---|---|
| **Data Cartographer** | Data source folders | Inventory reports, manifests | 90% | Every file listed with full path |
| **Data Cleaning Agent** | `tools/`, `Data/_meta/` | Validated pipeline, run summaries | 95% | Cite curation_log.md step IDs |
| **Exploratory Analysis Agent** | Panels | Notebooks, descriptive figures | 85% | Cite CSV paths, panel parquet paths |
| **Quant Methods Agent** | Panels | Regression tables, model outputs | 90% | Cite every model assumption to [Context/03](Context/03_quantitative_methods_and_analysis_menu.md) |
| **Visualization Agent** | Model outputs | PNG / SVG figures + LaTeX tables | 95% | Cite output source data file |
| **Writing Agent** | Figures, tables, ADRs | Paper draft sections | 85% | Every empirical claim cites a table/figure path |
| **Red-Team Reviewer** | Any artifact | Severity-ranked findings | 95% | Cite contradicted evidence |
| **Cursor Workflow/Rules Agent** | References, project state | `.cursor/rules/`, `.cursor/skills/` updates | 90% | Cite the source pattern file |
| **Final Synthesis Agent** | All above | Integrated paper + packaging | 95% | Cite section ADRs and run summaries |

### 12.2 Quality gates

Every agent hand-off includes:

1. **Inputs read** (file paths).
2. **Outputs written** (file paths with row counts and hashes).
3. **Confidence score** with evidence.
4. **Open questions / unknowns** (hand-off-forward list).
5. **Next agent** explicitly named.

### 12.3 Integration rule

Results enter the main project only after passing:

- [ ] At least one Red-Team Reviewer pass.
- [ ] Reproducible via a single script/notebook invocation.
- [ ] Cited in a markdown artifact in `reports/` or `docs/`.
- [ ] Committed on a branch that passes `make test` + `make lint`.

### 12.4 Disallowed

- Running TVP-VAR-SV as the headline model (demoted to optional robustness).
- Using citations from `AI Outputs/Beyond Correlation_ ...md` or `AI Outputs/deep-research-report.md` in paper drafts without verification.
- Modifying any file under `Data/` without a curation-log entry.
- Committing secrets or `.env` files.

---

## 13. Concrete Next-Agent Prompts

Eight ready-to-paste prompts, each specific to this repo. Keep each in [prompts/](prompts/) and version-control with the `.md` suffix + leading 2-digit number.

### 13.1 `prompts/10_data_cleaning_agent.md`

```
Role: Data Cleaning Agent.

Goal: Verify the curated data pipeline is reproducible on this machine.

Tasks (exactly in order):
1. Read Data/_meta/curation_log.md end-to-end. Note the expected final state.
2. Run `python tools/data_curation/01_snapshot_raw_hashes.py` and diff the output against the existing Data/_meta/raw_manifest.csv. Report hash mismatches.
3. Invoke the orchestrator: `python run_pipeline.py --dry-run`. Report any missing inputs/outputs.
4. Invoke `python tools/data_curation/06_build_inventory.py` and diff the new Data/MASTER_DATA.md against the committed copy. Report any size/row-count drift.
5. Invoke `python tools/data_curation/07_validate.py`. Paste the full output.
6. Produce a one-page run summary at reports/run_summaries/WS1_<YYYY-MM-DD>.md with the 5 checks and pass/fail per check.

Constraints:
- Do not modify any file in Data/ beyond regenerating MASTER_DATA.{md,txt,csv}.
- If any script fails, fix by editing the script (not the data), commit the patch to a feature branch, and state the fix in the run summary.
- Cite curation-log step IDs (01..11) in the summary.
- Confidence threshold: 95%. If confidence <95%, list what evidence is missing.
```

### 13.2 `prompts/20_exploratory_analysis_agent.md`

```
Role: Exploratory Analysis Agent.

Goal: Produce Panel A (2021+ common sample) as a Parquet file with all 5 factor blocks joined on a common daily calendar.

Pre-reads (mandatory):
- docs/specs/data_spec.md — calendar policy & missingness taxonomy
- config/factor_blocks.yml — block-to-file mapping
- Data/MASTER_DATA.md — canonical file list

Task spec:
- Sample start: 2021-01-01. Sample end: max available (latest common across selected files).
- Calendar: calendar_daily (every day) — join with ffill limit 5 for weekly/monthly macro series, no ffill for daily on-chain.
- Blocks: macro (FRED 19-series), institutional (Farside BTC flows + Artemis BTC ETF AUM), liquidity (DefiLlama ChainMetrics all_chains + TVL all_chains + Artemis DEX volume), BTC-native (Exchange Netflow, Miner-to-Exchange, Taker ratio, NUPL, Realized Cap), ETH-native (Active Addresses, Fees Burnt, Transactions).
- Target: BTC log-return, BTC 30-day annualized realized vol, ETH log-return, ETH 30-day realized vol.
- Output: reports/panels/panel_A_daily.parquet; a companion missingness report at reports/panels/panel_A_missingness.md with % NaN per column.
- Verify: no duplicate dates; strictly ascending; no rows before 2021-01-01; date column is `date` and dtype is date.

Constraints:
- Use src/cqresearch/data/loaders for every CSV read — do NOT read with vanilla pandas.read_csv.
- Add unit tests in tests/unit/test_panel_build.py for at least: date-monotonicity, no-duplicates, block-column presence.
- Confidence threshold: 90%. Cite every source CSV path in the missingness report.
```

### 13.3 `prompts/30_quant_methods_agent.md`

```
Role: Quant Methods Agent.

Goal: Produce the headline block partial-R² heatmap (Fig F1) from Panel A.

Pre-reads:
- docs/specs/methods_spec.md
- src/cqresearch/modeling/rolling_ols.py + partial_r2.py
- config/events.yml (for vertical-line annotations)

Task spec:
- Dependent variable: BTC log-return at daily frequency from Panel A.
- Regressors: 5 blocks × ~4 regressors/block (pre-registered in docs/specs/research_spec.md). Do NOT add variables ad hoc.
- Window: 180 trading days (main). Produce 90 and 365 as robustness.
- Compute block partial R² via Frisch-Waugh: for each block B, regress the block on other blocks, then regress the residuals of Y on residuals of B.
- Output Fig F1 to reports/figures/F1_block_partial_r2_180d.png at 300 DPI using src/cqresearch/viz/palette.py block colors (macro=blue, institutional=green, liquidity=orange, btc-native=gray, eth-native=purple).
- Also emit reports/tables/T_rolling_coefs_180d.csv with the rolling coefficients for each regressor.
- Annotate the figure with vertical lines for 2024-01-11, 2024-04-20, 2024-07-23.

Constraints:
- Use Newey-West SEs with 5 lags on all reported t-stats in the companion table.
- Do not use ML for the headline specification.
- Confidence threshold: 90%. Report the tolerance of partial-R² summation vs. overall R² in a footnote in the figure caption.
```

### 13.4 `prompts/40_visualization_agent.md`

```
Role: Visualization Agent.

Goal: Produce paper-quality figures F1..F7 per §15 of project_research_plan.md.

Inputs: table/panel paths listed in §15.

Standards:
- Matplotlib; no seaborn defaults. rcParams fixed in src/cqresearch/viz/rcparams.py (serif font for paper, sans for dashboard).
- Palette: src/cqresearch/viz/palette.py with block colors locked per §15.
- All figures: 300 DPI, <= 6.5 x 4.5 in, tight_layout=True, optional LaTeX rendering off by default (opt-in for paper build).
- Every figure output has a sibling .svg and a .json metadata file with source data path + git commit hash.

Constraints:
- Never hand-craft matplotlib axes; use the helpers in src/cqresearch/viz/helpers.py.
- Confidence threshold: 95%. Each figure must reference its data source in the caption.
```

### 13.5 `prompts/50_writing_agent.md`

```
Role: Writing Agent.

Goal: Draft paper sections in reports/drafts/sections/.

Pre-reads:
- docs/specs/research_spec.md
- docs/specs/methods_spec.md
- reports/tables/*.csv
- reports/figures/*.png

Sections to draft (in order):
- 01_introduction.md  (motivation, hypotheses, contributions, roadmap)
- 02_data.md          (sources, sample windows, cleaning, block composition)
- 03_methods.md       (rolling OLS, partial R², Bai-Perron, VAR/FEVD, event study)
- 04_results.md       (Q1..Q3 with figures F1..F3, tables T1..T3)
- 05_robustness.md    (Q4..Q8, appendix tables)
- 06_discussion.md    (economic interpretation, limits)
- 07_conclusion.md    (one page)

Constraints:
- Every empirical claim cites a file path in reports/figures/ or reports/tables/.
- No unverified external citations. If a 2026 arXiv link is relied on, verify through Context7 or Google Scholar first.
- Do not use hedged-claim templates ("may", "could"). State what the evidence shows and bound the claim.
- Confidence threshold: 85%. End each section with an "Evidence and Limits" paragraph listing each claim's supporting artifact.
```

### 13.6 `prompts/60_cursor_rules_agent.md`

```
Role: Cursor Workflow / Rules Agent.

Goal: Maintain the .cursor/rules/ and .cursor/skills/ under this project.

Tasks:
1. Each sprint, review sessions for repeated corrections (2+ times). If a pattern emerges, propose a new or amended .mdc rule in .cursor/rules/.
2. When a new reusable workflow emerges (3+ uses), propose a new SKILL.md under .cursor/skills/ following awesome-cursor-skills conventions (description ends with a trigger phrase, globs scoped, alwaysApply off by default).
3. Keep AGENTS.md in sync with any rule change.
4. Never delete an existing rule without an ADR in docs/decisions/.

Constraints:
- .cursor/rules/*.mdc must pass the frontmatter schema (name, description, alwaysApply, globs, priority).
- Confidence threshold: 90%. Link each proposal to the underlying observation.
```

### 13.7 `prompts/70_red_team_reviewer.md`

```
Role: Red-Team Reviewer.

Goal: Break the current paper draft. Find what is wrong before the referee does.

Lenses (run all four, label findings by lens):
- Statistical validity (specification, standard errors, multiple testing, look-ahead)
- Data integrity (vintage, joins, survivorship, date alignment)
- Reproducibility (can I rerun this from scratch? Are seeds fixed? Are data vintages pinned?)
- Economic interpretation (does the causal language match the identification?)

Output format:
- A severity-ranked findings table: High / Medium / Low per lens.
- For each High finding: reproduce the failure with a minimal script in tests/integration/test_redteam_<date>_<slug>.py.

Constraints:
- Do not invent hypothetical failures; only report reproducible or cite-backed issues.
- Confidence threshold per finding: >= 80%. Below 80% → label "Possible" and move to Low.
- Deliver a 1-page executive summary at reports/run_summaries/redteam_<date>.md.
```

### 13.8 `prompts/80_final_synthesis_agent.md`

```
Role: Final Synthesis Agent.

Goal: Integrate all sprint artifacts into a ship-ready paper package.

Tasks:
1. Verify each figure/table in reports/ has a referenced draft section.
2. Run `make paper` and fix any build failures.
3. Produce reports/run_summaries/final_<date>.md with artifact list + hashes + reproduction command.
4. Update README.md quick-start and project_research_plan.md §17 with progress check-marks.
5. Open a PR with one commit per section.

Constraints:
- Every High-severity red-team finding must be addressed or explicitly accepted with rationale in docs/decisions/.
- Confidence threshold: 95%. If below, block the release and escalate.
```

---

## 14. Recommended Folder and Context Structure

The full canonical tree is in §19. The critical categorical split:

- **`Data/`** — raw and curated CSVs; UNCHANGED from current state; machine-managed by `tools/`.
- **`config/`** — single source of truth for paths, calendars, events, factor blocks, chain taxonomy, curation snapshots.
- **`src/cqresearch/`** — Python package: `data`, `features`, `modeling`, `analysis`, `viz`, `utils`. All reusable code lives here, under test.
- **`scripts/`** — numbered top-level orchestration scripts (00..99). Invoke `src/cqresearch/` modules; never contain core logic.
- **`notebooks/`** — exploratory only; one notebook per hypothesis.
- **`tests/`** — unit + integration + fixtures.
- **`tools/`** — ingestion & curation pipeline (unchanged in structure; script internals updated per §19.B.3).
- **`prompts/`** — versioned agent prompts; templates at `prompts/templates/`.
- **`reports/`** — research artifacts: `prior_ai_outputs/` (moved from `AI Outputs/`), `deep_research/` (deep-research session outputs), `drafts/`, `figures/`, `tables/`, `appendix/`, `run_summaries/`, `panels/`.
- **`docs/`** — `onboarding/`, `specs/`, `decisions/` (ADRs), `context/` (moved from `Context/`), `manager/` (moved Manager_* files + PDF), `literature/`.
- **`references/`** — `FinancialEconometrics-master/`, `cursor-ai-tips-main/`, `awesome-cursor-skills-main/` — third-party read-only material.
- **`archive/`** — `Grok Convo.txt` and OpenAPI spec; retained for provenance, not an active input.
- **`.cursor/`** — `rules/` (6 .mdc), `skills/` (3 SKILL.md), `mcp.json` (stub).

**Do not move or rename `Data/`** — the tool pipeline hardcodes this name and any move cascades into multiple script edits with low benefit.

---

## 15. Figure and Table Plan

Figures F1..F7 and tables T0..T7 define the paper's artifact surface. Everything ships to `reports/figures/` and `reports/tables/`.

### 15.1 Figures

| ID | Title | Purpose | Source data | Method | Priority | Notes |
|---|---|---|---|---|---|---|
| F1 | Block partial-R² heatmap (BTC, 180d rolling) | Headline figure | Panel A, Q1 | Frisch-Waugh rolling OLS | P0 | 5 rows (blocks) × ~1,600 cols (days); 2024-01-11 vertical line |
| F2 | BTC rolling correlation with SPX / NDX / DXY / Gold | Direct institutionalization test | Panel A | Rolling 60/180/365-day ρ | P0 | 4-panel grid; Chow break markers |
| F3 | ETF-flow VAR FEVD stack | Institutional-channel decomposition | Panel C | 4-var VAR → FEVD | P0 | 20-day horizon; share of BTC-ret variance from each shock |
| F4 | Local-projection IRF: stablecoin supply → BTC realized vol | Stablecoin channel | Panel A / C | LP-IRF 0..20d | P1 | HAC bands |
| F5 | ETH L1 vs. L2 factor-loading panels | ETH-specific angle | Panel A + DefiLlama L2 | Rolling OLS per chain | P1 | Small multiples |
| F6 | Miner→exchange flow vs. BTC-price rolling correlation | Native decoupling | [Data/CryptoQuant/BTC/Miner Flows/](Data/CryptoQuant/BTC/Miner%20Flows/) | Rolling corr + Bai-Perron coef | P2 | |
| F7 | Diebold-Yilmaz rolling spillover index | Cross-asset connectedness | Panel A + TradingView | 10-var VAR → GFEVD | P2 | 200-day rolling |
| F8 | CUSUM OLS plots for 4 main regression models | Visual break evidence | Panel A | Recursive residuals | P1 | Appendix |
| F9 | Event-study CAR bars (4 events × BTC/ETH) | Sanity check | Panel A | Standard event study | P1 | Appendix |
| F10 | ETF AUM vs. BTC price overlay | Narrative figure (intro) | [Data/Artemis/Bitcoin ETFs AUM.csv](Data/Artemis/Bitcoin%20ETFs%20AUM.csv), [Data/CryptoQuant/BTC/Market Data/](Data/CryptoQuant/BTC/Market%20Data/) | Dual-axis line | P1 | Intro visual |
| F11 | Stablecoin mcap stacked area (USDT/USDC/DAI/FDUSD) | Context visual (intro) | [Data/DefiLlama/Stablecoins/stablecoin_mcap_by_defillama_id__daily.csv](Data/DefiLlama/Stablecoins/stablecoin_mcap_by_defillama_id__daily.csv) | Stacked area | P2 | |
| F12 | Correlation matrix heatmap (all regressors × Y) | Data-section figure | Panel A | Full correlation | P2 | |
| F13 | Missingness heatmap across Panel A | Data-section figure | Panel A | % NaN | P2 | |
| F14 | Realized vol time series (BTC vs. ETH vs. SPX) | Data-section figure | Panel A + Tradingview | 30-day RV | P2 | |
| F15 | Block-factor PCA scree + first-PC trajectories | Block structure diagnostic | Panel A | PCA within-block | P2 | |

### 15.2 Tables

| ID | Title | Purpose | Source | Method | Priority |
|---|---|---|---|---|---|
| T0 | Sample summary statistics | Data section | Panel A | `describe` + skewness/kurtosis | P0 |
| T1 | Break-test F-stats × model | Primary finding | Q1 | Chow + Bai-Perron | P0 |
| T2 | Granger-causality p-values (4-var VAR) | Q3 | Panel C | Wald χ² | P0 |
| T3 | FEVD share at 5, 10, 20 days | Q3 | Panel C | VAR decomposition | P0 |
| T4 | ETH L1 vs. L2 loading comparison | Q5 | Panel A | Rolling OLS snapshots | P1 |
| T5 | Miner-flow vs. price rolling-corr Bai-Perron coef | Q6 | Panel A | Bai-Perron | P2 |
| T6 | Event-study CARs (4 events × BTC/ETH × ±5d) | Q7 | Panel A | CAR | P1 |
| T7 | Diebold-Yilmaz directional net spillovers (pre vs. post ETF) | Q8 | Panel A | DY index | P2 |
| T8 | Missingness report per column of Panel A | Data integrity | Panel A | `isna().mean()` | P0 |

### 15.3 Style standards

- Matplotlib with a serif-font paper profile and sans-font dashboard profile (opt-in via rcParams).
- Block color palette (fixed): macro=`#1f77b4` (blue), institutional=`#2ca02c` (green), liquidity=`#ff7f0e` (orange), BTC-native=`#7f7f7f` (gray), ETH-native=`#9467bd` (purple).
- Every figure saved as `.png` (300 DPI) + `.svg` + `.json` metadata (source data path, git commit hash, method signature).
- Every table saved as `.csv` + `.tex` (booktabs) + `.md` (for notebook embed).

---

## 16. Risks, Weaknesses, and Red-Team Findings

### 16.1 Data risks

| Risk | Specific evidence | Impact | Mitigation |
|---|---|---|---|
| Asymmetric stablecoin coverage across chains | [Data/CryptoQuant/USDT (TRX)/](Data/CryptoQuant/USDT%20%28TRX%29/) only has Addresses + Exchange Flows; [Data/CryptoQuant/USDT ETH/](Data/CryptoQuant/USDT%20ETH/) has 6 subfolders | Any cross-stablecoin join drops variables | Null-handling policy in [docs/specs/data_spec.md](docs/specs/data_spec.md); use DefiLlama stablecoin_mcap as primary, CryptoQuant as secondary |
| Short windows for new series | [Data/FRED/BAMLH0A0HYM2__daily.csv](Data/FRED/BAMLH0A0HYM2__daily.csv) only 2023-04+ (FRED native 1996+); SOL ETF only 12 rows | Breaks long-history comparisons | Re-fetch full FRED history in next run of [tools/data_collection/fetch_fred.py](tools/data_collection/fetch_fred.py); exclude SOL ETF from primary analysis |
| Snapshot files mixed with time-series | [Data/Artemis/Artemis - Digital Asset Treasuries Overview.csv](Data/Artemis/) (`symbol` not `date` column); [Data/DefiLlama/TVL/Snapshot/](Data/DefiLlama/TVL/Snapshot/) | Wrong files pulled into panels | `config/factor_blocks.yml` whitelists time-series files only; curation step 04 already excludes them |
| Raw-parts and duplicates on disk | [Data/DefiLlama/_raw_parts/](Data/DefiLlama/_raw_parts/) + [_raw_parts/duplicates/](Data/DefiLlama/_raw_parts/duplicates/) | Naive globs pull superseded files | All loaders in `src/cqresearch/data/loaders.py` must scope to specific subfolders; never use `Data/**/*.csv` |
| Tool pipeline bugs | [tools/data_collection/fetch_farside_etf_csv.py](tools/data_collection/fetch_farside_etf_csv.py) line 135 + [tools/data_collection/organize_cryptoquant_metrics.py](tools/data_collection/organize_cryptoquant_metrics.py) lines 16-17 write to `tools/…` not `Data/…`; [tools/data_curation/07_validate.py](tools/data_curation/07_validate.py) line 34 hardcodes local backup path | Future refreshes silently land in wrong folder / skip validation | Fixed in §19.B.3 |
| Hardcoded snapshot dates | `2026-04-17` / `2026-04-14` in `02_dedupe_defi.py`, `03_merge_defi_parts.py`, `10_clean_new_defi.py` | Next refresh breaks | Moved to [config/curation_snapshots.yml](config/curation_snapshots.yml) in §19.B.3 |
| `MASTER_DATA.md` vs `MASTER_DATA.txt` drift | Both written by `06_build_inventory.py`; manual edits to either desync them | Downstream LLM reads outdated text | Never hand-edit; always rebuild via `make inventory` |
| ETH L2 data ambiguity | Manager_Outline warns against summing L1+L2 addresses; no L2 tables in [Data/CryptoQuant/ETH/](Data/CryptoQuant/ETH/); L2 data must be assembled from [Data/DefiLlama/ChainMetrics/](Data/DefiLlama/ChainMetrics/) | Policy-dependent results | [config/chain_taxonomy.yml](config/chain_taxonomy.yml) fixes membership; outputs always include L1-only, L2-sum, and L2-share |

### 16.2 Method risks

| Risk | Impact | Mitigation |
|---|---|---|
| Multicollinearity within macro block (DFF, DGS10, T10Y2Y, SOFR, RRP all related) | Block partial R² could become unstable | Use within-block PCA (first 2 PCs) as robustness; report VIF per regressor |
| Look-ahead in rolling estimation | Invalid inference | Rolling window uses strictly ≤t-1 information; seeds fixed; CV only for robustness ML |
| Break-test multiple testing | Bai-Perron already controls but Chow tests at 3 pre-spec dates should be adjusted | Bonferroni-adjust Chow p-values in T1 caption; pre-register in `research_spec.md` |
| Short Sample C (2024+) for VAR | Small-sample bias in FEVD | Report 5%/95% bootstrap CIs on FEVD; supplement with Sample A run starting 2021 |
| TVP-VAR complexity if adopted | Implementation bugs, convergence issues | Do not adopt for headline; if a team member adds as robustness, use an existing well-tested package (e.g., `pyflux`, `statsmodels.tsa.statespace`) |
| Event-date misalignment (US trading day vs. UTC) | 1-day offset contaminates event studies | Use NYSE trading calendar for events, UTC for daily returns; document offset in T6 notes |

### 16.3 Interpretation risks

| Risk | Mitigation |
|---|---|
| Correlation-causation slippage | [Context/00](Context/00_project_context_and_goals.md) explicitly forbids overclaim; every causal language ("causes", "drives") in drafts must be flagged by red-team |
| Overfitting stories to observed breaks | Pre-register break dates in [docs/specs/research_spec.md](docs/specs/research_spec.md); distinguish confirmatory (pre-spec) from exploratory (Bai-Perron unknown) results |
| Narrative convenience ("ETF changed everything") | Add a placebo break at a randomly-chosen date and show it does not produce comparable evidence |

### 16.4 AI hallucination risks

| Source | Specific issue | Action |
|---|---|---|
| [AI Outputs/Beyond Correlation_ ...md](AI%20Outputs/Beyond%20Correlation_%20Quantifying%20Bitcoin%27s%20New%20Role%20in%20Financial%20Markets%20Through%20Structural%20Breaks%2C%20Flow%20Dynamics%2C%20and%20Systemic%20Risk.md) | 2026 arXiv IDs with 2512/2602/2604/2606 prefixes, LinkedIn links | P0 citation audit; do not quote in draft |
| [AI Outputs/deep-research-report.md](AI%20Outputs/deep-research-report.md) | Similar external-citation concerns | P0 citation audit |
| [AI Outputs/txt output.md](AI%20Outputs/txt%20output.md) | Hormuz-blockade & SEC-commodity events not corroborated in repo; DML-as-headline contradicts Context | Treat as unverified; do not use as evidence |
| [Grok Convo.txt](Grok%20Convo.txt) | 5-repo "reference corpus" GitHub URLs not verified | P1 verify each repo exists; treat as suggestion |

### 16.5 Reproducibility risks

| Risk | Evidence | Mitigation |
|---|---|---|
| No `pyproject.toml` / `requirements.txt` | Tools & Pipeline Auditor report | `pyproject.toml` with `uv.lock` created in §19.B.4 |
| Path resolution drift across scripts | `_common.py` uses `parents[2]`; harvester uses `parent`; two fetchers use `parents[1]` (bug) | `config/paths.py` centralizes; two fetchers fixed |
| Absolute backup path in step 07 | `C:/Dev/Projects/CryptoQuant_Data_backup_2026-04-16` | Moved to `config/curation_snapshots.yml` |
| No orchestrator | Scripts invoked manually in non-obvious order | `run_pipeline.py` with `--dry-run` / `--from-step` / `--to-step` |
| Notebooks capture session state | No header-cell discipline | `notebooks/_template.ipynb` with mandatory header cell; `nbstripout` in pre-commit |

---

## 17. Execution Roadmap

Priorities: **P0** required for the flagship paper; **P1** important; **P2** useful; **P3** optional.

### 17.1 Immediate next steps (this week)

- **P0** Execute §19 reorganization; land on new tree with `git mv` history preserved.
- **P0** Write `docs/specs/research_spec.md` (hypotheses, samples, pre-registered events) and `docs/specs/methods_spec.md` (11-method menu locked from [Context/03](Context/03_quantitative_methods_and_analysis_menu.md)) and `docs/specs/data_spec.md` (calendar policy, missingness taxonomy, unit dictionary).
- **P0** Set up `pyproject.toml` via `uv init` + `uv add` the listed deps; commit `uv.lock`.
- **P0** Fix the 2 tool path bugs ([tools/data_collection/fetch_farside_etf_csv.py](tools/data_collection/fetch_farside_etf_csv.py) line 135; [tools/data_collection/organize_cryptoquant_metrics.py](tools/data_collection/organize_cryptoquant_metrics.py) lines 16-17) and the backup path in `07_validate.py`.
- **P1** Write `run_pipeline.py` orchestrator; smoke-test with `--dry-run`.
- **P1** Write the first three ADRs: 000 (choose Python stack), 001 (break-test family: Chow + Bai-Perron over TVP-VAR-SV), 002 (ETH L1/L2 policy).

### 17.2 Short-term milestones (weeks 2-3)

- **P0** WS-1 Data cleaning / pipeline validation complete; `reports/run_summaries/WS1_*` committed.
- **P0** WS-2 Panels A, B, C built; missingness report published.
- **P0** WS-3 Descriptive diagnostics notebook + Fig F2 + Table T0 + T8.
- **P0** First citation-audit pass on [AI Outputs/Beyond Correlation_ *.md](AI%20Outputs/Beyond%20Correlation_%20Quantifying%20Bitcoin%27s%20New%20Role%20in%20Financial%20Markets%20Through%20Structural%20Breaks%2C%20Flow%20Dynamics%2C%20and%20Systemic%20Risk.md) + [AI Outputs/deep-research-report.md](AI%20Outputs/deep-research-report.md); results saved to `docs/literature/citation_audit_<date>.md`.
- **P1** Parse PDF meeting note with `pypdf`; cross-check Manager_Outline summary.
- **P1** Resolve `AI Outputs/txt output p2.md` vs `Context/00` duplication (ADR or merge).

### 17.3 Medium-term milestones (weeks 4-5)

- **P0** WS-4 + WS-5: static and rolling regressions; Fig F1 published; Table T_rolling_coefs published.
- **P0** WS-6: structural-break tests; Table T1 published.
- **P0** WS-7: 4-var VAR / FEVD / event studies; Fig F3 + Tables T2, T3, T6 published.
- **P1** WS-8: robustness + LASSO-gated screening.
- **P1** First draft of paper sections 01 (intro), 02 (data), 03 (methods).
- **P2** Q5 ETH L1/L2 panels; Q6 miner-flow decoupling; Q8 DY spillover.

### 17.4 Final milestones (week 6)

- **P0** WS-9: full first draft; red-team pass; revisions; ADRs for every non-trivial decision.
- **P0** `make paper` produces a reproducible artifact bundle.
- **P1** Dashboard-lite: one Streamlit notebook mirroring F1..F3 (optional, not required for paper).
- **P2** Weekly robustness re-run; appendix tables A1..A6.

### 17.5 Final deliverables

1. `reports/drafts/paper_v1.md` — primary working paper.
2. `reports/figures/` — Figs F1..F15.
3. `reports/tables/` — Tables T0..T8.
4. `reports/appendix/A_robustness.md` — robustness results.
5. `reports/run_summaries/final_<date>.md` — artifact list with hashes and reproduction command.
6. `docs/decisions/` — ADRs for every material decision.

---

## 18. Final Recommendation

**Execute Strategy A (Factor-Evolution Paper) as the primary deliverable.** Build three analytical panels on the existing curated data (2021+ common, BTC long, ETF-era short). Use rolling OLS with block partial R² as the headline diagnostic (Figure F1). Use Chow tests at pre-registered dates (2024-01-11 BTC-ETF, 2024-07-23 ETH-ETF, 2024-04-20 halving) plus Bai-Perron with unknown breaks as formal break evidence (Table T1). Confirm dynamic transmission with a compact 4-variable VAR/FEVD on the ETF-era sample (Figure F3, Tables T2-T3). Support with event studies (Table T6) and rolling cross-asset correlations (Figure F2). Promote stablecoin / miner / connectedness analyses to robustness chapters or follow-on papers. Reject headline ML (demote to support-only). Keep TVP-VAR-SV as optional robustness — not headline.

Operationally: lock the spec in `docs/specs/`, fix the two tool path bugs, move every prior AI output to `reports/prior_ai_outputs/` without altering content, adopt the six `.cursor/rules/` and three `.cursor/skills/`, and run the eight prompts in `prompts/` sequentially. The first-sprint exit criterion is Fig F1 + Table T1 + Table T0 at publication-ready quality, with every finding backed by a file-path-cited artifact and a confidence score.

---

## 19. Reorganization Specification

This section specifies the migration from the current tree into a publication-grade canonical layout. The user has confirmed that `Data/` stays in place and that `tools/` scripts will be updated.

### 19.1 Target canonical tree

```
CryptoQuant/
├── .cursor/
│   ├── rules/               # 6 .mdc rules (see §19.B.4)
│   ├── skills/              # 3 project SKILL.md (see §19.B.4)
│   └── mcp.json             # stub (context7, postgres, github) — optional
├── .env.example             # FRED_API_KEY, DEFILLAMA_API_KEY
├── .gitignore               # expanded
├── .pre-commit-config.yaml  # ruff, mypy, nbstripout
├── AGENTS.md                # single agent operating constitution (root)
├── README.md                # real README (replaces 1-line placeholder)
├── Makefile
├── pyproject.toml           # uv-managed deps
├── uv.lock
├── run_pipeline.py          # orchestrator
├── project_research_plan.md # THIS DOCUMENT
│
├── Data/                    # UNCHANGED (484 curated CSVs + _meta + MASTER_DATA.*)
│
├── config/
│   ├── paths.py
│   ├── calendars.yml
│   ├── chain_taxonomy.yml
│   ├── factor_blocks.yml
│   ├── events.yml
│   └── curation_snapshots.yml
│
├── src/
│   └── cqresearch/
│       ├── __init__.py
│       ├── data/        # loaders, calendars, missingness, panel builders
│       ├── features/    # factor library (macro, institutional, liquidity, btc_native, eth_native)
│       ├── modeling/    # static_ols_hac, rolling_ols, partial_r2, structural_breaks, var_fevd, event_study, vol_models, dcc_connectedness, pca
│       ├── analysis/    # orchestrators that glue features + models into panels/tables
│       ├── viz/         # palette, rcparams, helpers, templates
│       └── utils/       # io, logging, hashing, config loader, citation helpers
│
├── scripts/
│   ├── 00_inventory_data.py
│   ├── 10_build_factor_library.py
│   ├── 20_build_panels.py
│   ├── 30_descriptives.py
│   ├── 40_static_regressions.py
│   ├── 50_rolling_and_partial_r2.py
│   ├── 60_structural_breaks.py
│   ├── 70_var_fevd.py
│   ├── 80_robustness.py
│   ├── 90_support_ml.py
│   └── 99_export_paper_artifacts.py
│
├── notebooks/
│   ├── 00_data_profile.ipynb
│   ├── 10_block_correlations.ipynb
│   ├── 20_structural_break_viz.ipynb
│   └── _template.ipynb      # mandatory header cell
│
├── tools/                   # UPDATED (see §19.B.3)
│   ├── data_collection/
│   ├── data_curation/
│   └── README.md
│
├── tests/
│   ├── unit/
│   ├── integration/
│   └── fixtures/
│
├── prompts/
│   ├── 00_research_spec_writer.md
│   ├── 10_data_cleaning_agent.md
│   ├── 20_exploratory_analysis_agent.md
│   ├── 30_quant_methods_agent.md
│   ├── 40_visualization_agent.md
│   ├── 50_writing_agent.md
│   ├── 60_cursor_rules_agent.md
│   ├── 70_red_team_reviewer.md
│   ├── 80_final_synthesis_agent.md
│   └── templates/           # prompt-engineering templates
│
├── reports/
│   ├── prior_ai_outputs/    # moved from `AI Outputs/` (git mv — content preserved verbatim)
│   ├── deep_research/       # future deep-research session outputs (folder-per-inquiry)
│   ├── drafts/              # paper drafts (sections/*.md, paper_v1.md)
│   ├── figures/             # PNG + SVG + JSON metadata
│   ├── tables/              # CSV + LaTeX + MD
│   ├── appendix/            # robustness outputs
│   ├── panels/              # Parquet panels + missingness reports
│   └── run_summaries/       # dated run logs
│
├── docs/
│   ├── onboarding/          # DATA_ONBOARDING.md, AGENT_ONBOARDING.md, PAPER_ONBOARDING.md
│   ├── specs/               # research_spec.md, methods_spec.md, data_spec.md
│   ├── decisions/           # ADRs NNN-*.md
│   ├── context/             # moved from top-level Context/
│   ├── manager/             # Manager_Outline.md, Manager_workflow.md, crypto_quant_methods_meeting_note.pdf
│   └── literature/          # external references index + citation audit log
│
├── references/              # third-party read-only
│   ├── FinancialEconometrics-master/
│   ├── cursor-ai-tips-main/
│   └── awesome-cursor-skills-main/
│
└── archive/
    ├── grok_convo_2026-04-16.txt
    └── defillama_openapi_2026-04-14.json
```

### 19.2 Migration operations (`git mv` wherever possible)

| From | To | Notes |
|---|---|---|
| `Context/` | `docs/context/` | Whole directory |
| `AI Outputs/` | `reports/prior_ai_outputs/` | Whole directory; content byte-identical |
| `Manager_Outline.md` | `docs/manager/Manager_Outline.md` | |
| `Manager_workflow.md` | `docs/manager/Manager_workflow.md` | |
| `crypto_quant_methods_meeting_note.pdf` | `docs/manager/crypto_quant_methods_meeting_note.pdf` | |
| `Grok Convo.txt` | `archive/grok_convo_2026-04-16.txt` | Rename to date-stamped |
| `defillama-api (2).json` | `archive/defillama_openapi_2026-04-14.json` | Harvester `--spec` default updated |
| `FinancialEconometrics-master/` | `references/FinancialEconometrics-master/` | Whole directory |
| `cursor-ai-tips-main/` | `references/cursor-ai-tips-main/` | Whole directory |
| `awesome-cursor-skills-main/` | `references/awesome-cursor-skills-main/` | Whole directory |
| `harvest_defillama_simple.py` | `tools/data_collection/harvest_defillama.py` | File + default `--spec` path updated |

`Data/` is not touched.

### 19.3 Tool updates required

| File | Change |
|---|---|
| [tools/data_curation/_common.py](tools/data_curation/_common.py) | Re-anchor `ROOT` via `config/paths.py`; re-export `PROJECT_ROOT`, `DATA_DIR`, `REPORTS_DIR`, `ARCHIVE_DIR` |
| [tools/data_curation/07_validate.py](tools/data_curation/07_validate.py) | Replace absolute `BACKUP_DIR` (line 34) with `config/curation_snapshots.yml` lookup, fail-soft |
| [tools/data_curation/02_dedupe_defi.py](tools/data_curation/02_dedupe_defi.py), [03_merge_defi_parts.py](tools/data_curation/03_merge_defi_parts.py), [10_clean_new_defi.py](tools/data_curation/10_clean_new_defi.py) | Read hardcoded `2026-04-17` / `2026-04-14` date globs from `config/curation_snapshots.yml` |
| [tools/data_collection/fetch_farside_etf_csv.py](tools/data_collection/fetch_farside_etf_csv.py) line 135 | Fix `parents[1]` → use `config.paths.DATA_DIR / "Farside ETF Data"` |
| [tools/data_collection/organize_cryptoquant_metrics.py](tools/data_collection/organize_cryptoquant_metrics.py) lines 16-17 | Same fix; add deprecation header |
| `tools/data_collection/harvest_defillama.py` (after rename) | Default `--spec` to `archive/defillama_openapi_2026-04-14.json` (or configurable) |
| **NEW** `run_pipeline.py` | Orchestrator invoking curation steps in the correct **execution** order (01, 02, 03, 04, 05, 08, 09, 10, 11, 06, 07); flags `--dry-run`, `--from-step`, `--to-step` |
| **NEW** `tools/README.md` | Documents pipeline run order, idempotency, secrets, refresh checklist |

### 19.4 New files to create

**Root:**

- `AGENTS.md` — consolidated agent operating constitution. References `docs/context/*`, `docs/manager/*`, 6 `.cursor/rules/*.mdc`.
- `README.md` — replaces 1-line placeholder.
- `.env.example` — `FRED_API_KEY=`, `DEFILLAMA_API_KEY=`
- `.gitignore` — expanded (`.env`, `__pycache__`, `.venv`, `.pytest_cache`, `.ruff_cache`, `.mypy_cache`, `outputs/`, `.ipynb_checkpoints/`, `*.parquet` under `reports/panels/`? no — keep panels committed for reproducibility via `git-lfs`; defer).
- `.pre-commit-config.yaml` — ruff, mypy, nbstripout.
- `Makefile` — targets: `setup`, `ingest`, `curate`, `inventory`, `validate`, `pipeline`, `test`, `lint`, `figures`, `paper`, `clean`.
- `pyproject.toml` — `uv`-managed; runtime: `pandas`, `polars`, `numpy`, `statsmodels`, `scikit-learn`, `arch`, `linearmodels`, `matplotlib`, `seaborn`, `python-dotenv`, `requests`, `beautifulsoup4`, `pyyaml`, `pyarrow`, `tqdm`, `pypdf`; dev: `pytest`, `pytest-cov`, `ruff`, `mypy`, `nbstripout`, `pre-commit`, `ipykernel`.
- `run_pipeline.py`.

**`config/`:**

- `paths.py` — single source for every project path.
- `calendars.yml` — `calendar_daily` / `market_trading_daily` / `weekly` / `monthly_end`.
- `chain_taxonomy.yml` — L1 / canonical-L2 / broad-ecosystem membership + aggregation rules.
- `factor_blocks.yml` — 5-block factor architecture with CSV paths per block.
- `events.yml` — pre-specified break dates.
- `curation_snapshots.yml` — replaces hardcoded `2026-04-17`/`2026-04-14` strings.

**`.cursor/rules/`:** 6 `.mdc` files per §8.2.

**`.cursor/skills/`:** `data-quality-check/SKILL.md`, `structural-break-runner/SKILL.md`, `figure-template/SKILL.md`.

**`docs/specs/`:** skeletons for `research_spec.md`, `methods_spec.md`, `data_spec.md`.

**`prompts/`:** 8 numbered prompts per §13, plus `templates/` with confidence-scoring, spec-first, research-first, best-of-N templates.

**`src/cqresearch/`:** package skeleton with `__init__.py` in each sub-package.

**`scripts/`:** 11 numbered orchestration scripts (skeletons; logic lives in `src/cqresearch/`).

**`notebooks/`:** `_template.ipynb` + 3 starter notebooks.

**`tests/`:** `unit/conftest.py`, `fixtures/` tiny CSVs, one smoke test per `src/cqresearch/` sub-package.

### 19.5 Non-destructive guarantees

- `Data/` is not touched.
- `AI Outputs/` content is preserved byte-identical after `git mv`.
- All moves are reversible by a single `git revert`.
- No analysis is run during the reorg.
- No secret files are committed.

### 19.6 Execution order

1. Create `project_research_plan.md` at repo root (this file).
2. Create new folder skeleton with `.gitkeep` stubs.
3. `git mv` the 9 relocations listed in §19.2.
4. Author all new files listed in §19.4.
5. Apply the 6 tool-script edits in §19.3.
6. Smoke-test `run_pipeline.py --dry-run` (optional — requires a working Python env).
7. Commit with a structured commit message: `chore(reorg): reorganize into publication-grade layout (Data/ unchanged)`.

---

## Confidence Summary

| Claim | Confidence |
|---|---:|
| Primary objective (§4.1) is correct | 92% |
| Data is sufficient for the primary objective | 93% |
| Rolling OLS + partial R² + Bai-Perron is the right headline method | 88% |
| TVP-VAR-SV should NOT be the headline | 85% |
| No unverified citations leak into drafts before audit | 95% (contingent on enforcing §13.5 constraint) |
| Reorg is non-destructive | 95% |
| Tool-script edits will not break the pipeline | 85% (smoke-test needed) |
| The 6-week timeline is feasible for the 3-student team | 75% |

Items below 90% list their residual evidence gap in the corresponding section.

---

*End of plan.*
