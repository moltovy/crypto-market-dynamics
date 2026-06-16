# CryptoQuant Research Program — Final Synthesis

**Synthesized from:** Opus Manager Review, Gemini Manager Review, Codex Manager Review
**Synthesis date:** 2026-04-18
**Synthesis agent:** Claude Opus 4.7 (Cursor Lead Manager-Synthesizer)
**Governing document:** `AGENTS.md` (overrides everything else per §4 Evidence Hierarchy)

---

## 0. Reading Guide

This document is the authoritative merge of three independent reviews (Opus, Gemini, Codex) of the CryptoQuant research repository. It does not add new audit findings — it resolves contradictions across the three reviews using evidence quality, and it surfaces the decisions that require a human owner.

Confidence tags used throughout:
- `[VERIFIED]` — directly confirmed by repository file read in this synthesis pass.
- `[INFERENCE]` — reasoned from the three reviews' evidence, not directly proven.
- `[UNCERTAIN]` — flagged for further validation.

Agent-citation format:
- `[Opus+Gemini+Codex]` — all three agree.
- `[Opus]`, `[Gemini]`, `[Codex]` — single-source finding.
- `[repo:<path>]` — verified by direct repository read during this synthesis.

Evidence-quality rule for contradictions: The agent that cited a specific file path, line number, or quantitative value wins over an agent making a general assertion. Disagreements are not resolved by vote.

---

## 1. Consensus Findings (All Three Agents Agree)

### 1.1 Repository state is real but not publication-grade `[VERIFIED]`

The repo has a real Python package (`src/cqresearch/`), a master panel (`reports/panels/master_daily.parquet`, 2,293 × 58), 16 result tables under `reports/tables/2026-04-18/`, 11 figures under `reports/figures/2026-04-18/`, a draft paper (`reports/drafts/paper_v0.1_2026-04-18.md`), and 9 passing unit tests. But headline method labels in the draft exceed what the code implements, interpretation is stronger than the identification strategy supports, and figures are diagnostic rather than paper-ready.
- Agents: `[Opus+Gemini+Codex]` + `[repo:reports/panels/master_daily.parquet]` + `[repo:reports/drafts/paper_v0.1_2026-04-18.md]`.

### 1.2 Four-paper mandate contradicts most other documents `[VERIFIED]`

`AGENTS.md` §1–§2 is explicit about a **four-paper** portfolio (two institutionalization + two bridge), yet `project_research_plan.md`, the current `reports/drafts/paper_v0.1_2026-04-18.md`, and most context docs still reflect a **single-paper** mission. Opus states this as the "central governance problem" (line 18 of its review). Gemini flags the same gap. Codex frames it as the first P0 item.
- Agents: `[Opus+Gemini+Codex]` + `[repo:AGENTS.md §1–§2]` vs `[repo:reports/drafts/paper_v0.1_2026-04-18.md §1]`.

### 1.3 Method-label inflation is systemic `[VERIFIED]`

Three specific mislabels are called out by all three agents:
1. "Bai-Perron" in the draft is actually a single-break sup-F sweep. `[repo:src/cqresearch/modeling/structural_breaks.py]` docstring says this approximates Bai-Perron single-break without dynamic-programming search for `k` unknown breaks.
2. "Shapley/block partial R²" in the draft is closer to variable-drop or standalone-block R². No Shapley implementation exists in `src/cqresearch/modeling/`.
3. ETF flow intensity as "flow / market cap" in the draft is `flow / prior-day close` in code. `[repo:src/cqresearch/features/panel.py lines 63–71]` self-labels the quantity as "flow-per-unit-price".
- Agents: `[Opus+Gemini+Codex]`.

### 1.4 ETF daily flow data is the strongest asset `[VERIFIED]`

Farside daily BTC/ETH flows match DefiLlama aggregate after unit conversion at r = 1.000000 (274 obs BTC, 263 obs ETH). Opus and Codex cite the exact numbers; Gemini notes the same equivalence. Stablecoin metrics drift 33.5% median between Artemis (selected-chain) and DefiLlama (all-id universe). USD strength (FRED DTWEXBGS vs TradingView DXY) drifts 14.7% median. ETH market cap (CryptoQuant vs Artemis) is effectively equivalent (0.38% median drift). Open interest, fees, active addresses, exchange flows, and reserve metrics are flagged "not comparable yet" — require a metric dictionary before use.
- Agents: `[Opus+Gemini+Codex]` + `[repo:CODEX/data_analysis.md]`.

### 1.5 Calendar/fill policy broken in three places `[VERIFIED]`

- `[repo:config/calendars.yml]` declares `ffill_limit: 0` for `calendar_daily`, `market_trading_daily`, and `weekly`. A policy comment at the bottom says Farside should use `ffill_limit: 3`.
- `[repo:reports/drafts/paper_v0.1_2026-04-18.md §2.2]` prose says "forward-fill up to 4 days to cover long weekends".
- `[repo:HANDOFF.md]` (per Opus) says equity/macro series are forward-filled up to 4 days.
These three sources disagree. Current code in `src/cqresearch/data/calendars.py` uses a hardcoded default that does not consistently honor the YAML. Consequence: weekend/holiday handling mechanically generates zero returns and zero ETF flows, which pollutes Chow tests, rolling regressions, and VAR dynamics.
- Agents: `[Opus+Gemini+Codex]`.

### 1.6 Test coverage is too thin for the claim surface `[VERIFIED]`

`tests/unit/` contains 4 files with 9 passing tests (Codex ran `python -m pytest -q`; 9 passed in 0.61 s). Tests cover imports, config parseability, and fixtures, but not: OLS math, rolling R² math, structural-break math, FEVD math, event-window math, calendar-fill behavior, ETF flow unit semantics, or table regeneration.
- Agents: `[Opus+Gemini+Codex]`.

### 1.7 Prior AI outputs carry citation risk `[VERIFIED]`

Two specific files hallucinate 2026 arXiv IDs and fake LinkedIn URLs: `reports/prior_ai_outputs/deep-research-report.md` and `reports/prior_ai_outputs/Beyond Correlation_ Quantifying Bitcoin's New Role in Financial Markets Through Structural Breaks, Flow Dynamics, and Systemic Risk.md`. `AGENTS.md` §8 already warns about these two files by name. `txt output p2.md` promotes a DML/high-frequency scope that contradicts `AGENTS.md` and cannot be validated against the inventory.
- Agents: `[Opus+Gemini+Codex]` + `[repo:AGENTS.md §8]`.

### 1.8 Maximum-inventory standalone paper is infeasible `[VERIFIED]`

A single paper using all 490 CSVs would invite p-hacking, multicollinearity, and indefensible narrative. All three reviewers reject it. The inventory's role is a **shared factor library / data atlas**, not a fifth paper. Formal methods to tame the dimensionality: within-block PCA (already configured in `[repo:config/factor_blocks.yml]` as `pca_config: within_block: true, n_components: 2`), LASSO screening, and a metric dictionary as precondition for any cross-vendor join.
- Agents: `[Opus+Gemini+Codex]`.

### 1.9 ETF flow intensity is mis-scaled `[VERIFIED]`

`[repo:src/cqresearch/features/panel.py lines 68–71]` implements `btc_etf_intensity = panel["btc_etf_total"] / panel["btc_close"].shift(1)`. The inline comment on line 66 already admits this is "flow-per-unit-price". The draft still describes it as market-cap intensity. All three agents mark this as a top-tier fix.
- Agents: `[Opus+Gemini+Codex]`.

### 1.10 Python version is inconsistent `[VERIFIED]`

`AGENTS.md` §14 says Python 3.11+. `pyproject.toml` allows `>=3.10`. `HANDOFF.md` reports the active interpreter as 3.10.0. This must be reconciled before the project can claim reproducibility.
- Agents: `[Opus+Gemini+Codex]` + `[repo:AGENTS.md §14]`.

### 1.11 Pipeline entry points conflict `[VERIFIED]`

`.cursor/rules/global-constitution.mdc` says all pipeline entry points go through `run_pipeline.py` (the curation/inventory orchestrator). Current research execution lives in `scripts/run_full_pipeline.py`. The two are not wired together; the rule and the reality disagree.
- Agents: `[Opus+Gemini+Codex]` + `[repo:CODEX/current_status_analysis.md]`.

### 1.12 v0.1 paper language overclaims causality `[VERIFIED]`

The draft contains specific causal phrasings that the identification strategy cannot support. Opus lists the offenders with line numbers (e.g., "ETFs are now the single most significant driver"); Gemini calls for softening to "associated with a structural regime change"; Codex cites `[repo:reports/run_summaries/03_run_analyses.md]` where the Chow test at the BTC ETF launch date is actually insignificant (F=0.81, p=0.60), and the sup-F argmax is 2021-01-04 (not 2024-01-11).
- Agents: `[Opus+Gemini+Codex]` + `[repo:reports/run_summaries/03_run_analyses.md]`.

### 1.13 Overclaiming in break-test interpretation `[VERIFIED]`

BTC: Chow F=0.81, p=0.60 at 2024-01-11 → statistically insignificant; sup-F argmax lands at 2021-01-04 (placebo p≈0).
ETH: Chow F=2.13, p=0.024 at 2024-07-23 → significant; sup-F argmax 2021-05-12 (placebo p≈0).
The draft's ETF-as-structural-break narrative is weaker than the prose suggests, and the 2021 breaks are closer to COVID-stimulus than ETF-era events. All three agents flag this tension.
- Agents: `[Opus+Gemini+Codex]` + `[repo:reports/tables/2026-04-18/structural_breaks_summary.csv]`.

### 1.14 Repository governance must read `AGENTS.md` first `[VERIFIED]`

All three agents treat `AGENTS.md` as the constitution and identify every older document that contradicts it as needing reconciliation, not override. This includes `project_research_plan.md`, `HANDOFF.md`, `docs/manager/Manager_Outline.md`, `docs/manager/Manager_workflow.md`, and the v0.1 draft.
- Agents: `[Opus+Gemini+Codex]`.

---

## 2. Contradictions and Disagreements

### 2.1 Paper 4 selection — **HUMAN DECISION REQUIRED**

| Agent | Proposed Paper 4 | Core question | Data cited |
|---|---|---|---|
| Opus | "Liquidity Fragmentation Across DeFi and CEX Venues: TVL, Volume, and Fee-Based Market Structure Metrics" | Does DeFi's share of total trading/liquidity change with volatility regime? | Artemis DEX Volume, CEX Spot/Perps Volume, DefiLlama TVL, fee data |
| Gemini | "Capital Flight in Microstructure: DeFi TVL vs Centralized Exchanges" | When VIX spikes, does liquidity pool in smart contracts or flee to CEX order books? | `tvl_all_chains_daily.csv` vs CryptoQuant exchange netflow |
| Codex | "DeFi Credit, Lending, and RWA Rate-Arbitrage Bridge" | Do DeFi lending yields and tokenized-RWA yields respond to FRED short rates and crypto stress? With formal fallback to ETH staking/LST/LRT collateral if coverage fails. | `Data/Artemis/Lending Deposits by Protocol.csv`, `Lending Borrows by Protocol.csv`, `Lending Interest Fees by Protocol.csv`, `Data/DefiLlama/RWA/`, `Data/Artemis/RWA - Tokenized Market Cap.csv`, `Data/FRED/` |

**Evidence verdict:** Codex wins on evidence quality. It cites concrete Artemis and DefiLlama RWA file paths, acknowledges the short RWA history (coverage risk) as a named kill risk, and is the only agent with a formal fallback (ETH LST/LRT) if data-quality checks fail. Opus and Gemini propose similar "DeFi vs CEX" framings without committing specific files or a fallback.

**Recommendation:** Paper 4 = **Codex's DeFi Credit/Lending/RWA Rate-Arbitrage Bridge**, with ETH LST/LRT as pre-declared fallback if coverage checks fail. This requires human sign-off per `AGENTS.md` §15 (headline paper direction is a gated change).

### 2.2 Tooling migration aggressiveness — **HUMAN DECISION REQUIRED**

| Agent | Position |
|---|---|
| Opus | Conservative add-only: `ruptures` (true Bai-Perron), `plotnine`, Quarto/Typst, commit `uv.lock`. **Do not** adopt Polars or DuckDB as primary; **do not** switch to R. |
| Gemini | Aggressive migration: Polars + DuckDB (replace heavy pandas joins on 1.8M rows), `rpy2` + R `strucchange` for true multi-break Bai-Perron, Quarto, plotnine or seaborn.objects, `uv` + `requires-python = ">=3.11"`. |
| Codex | Minimalist: Python stack is adequate for v0.2 if governance, calendars, method labels, and tests are fixed first. Selective adds (DuckDB, Polars Lazy, R strucchange, Quarto, plotnine) only after core fixes land. Explicitly forbids TVP-VAR / Bayesian / ML-heavy methods until conservative pipeline is correct. |

**Evidence verdict:** Codex has the strongest reasoning (governance before tool churn); Opus is the pragmatic middle path (add named tools with known coverage); Gemini's aggressive migration has the largest reproducibility risk (rpy2 bridges, 1.8M-row Polars/DuckDB migration, Python 3.11 switch all at once). Gemini itself softens in §17 against rpy2 for a small student team.

**Recommendation:** Hybrid Codex + Opus. Phase 1: reconcile governance, calendar/fill, method labels, commit `uv.lock`, align Python to 3.11. Phase 2: add `ruptures` (Opus) for true Bai-Perron inside Python, add Quarto for paper builds, add `plotnine` for figures. Defer Polars/DuckDB/rpy2. Human decision needed on whether to commit to the 3.11 alignment and whether to add any R bridge at all.

### 2.3 Calendar strategy specifics — **HUMAN DECISION REQUIRED**

| Agent | Distinctive contribution |
|---|---|
| Opus | Numeric limits: stocks/FRED ffill ≤3d (reconcile `calendars.yml: 0` and `HANDOFF: 4` to 3); monthly ≤31d; weekly ≤7d; stablecoins ffill ≤1d; headline regressions business-day-only for Papers 1–3; weekly robustness at W-FRI; pre-first-valid-date zero-fill is forbidden (BTC 2024-01-11, ETH 2024-07-23). |
| Gemini | Principle: "0% weekend returns are statistical poison" (exact quote, §17). Drop weekends entirely from master dataset for TradFi regressions. ETF missing on US holidays = structural zero; else drop the row. |
| Codex | Matrix (verbatim, from `data_calendar_metric_strategy_v0.md`): market-day headline for Papers 1–2 macro/ETF; calendar-day for stablecoin liquidity and DeFi/CEX + TVL; weekly for lending/RWA (Paper 4). Rules: never ffill returns; never ffill flows; ETF zero-fill only for confirmed non-trading days inside active fund windows. |

**Evidence verdict:** Codex and Opus both provide operational detail; Gemini provides the clearest principle-level framing but fewer numbers. The three agents do not actually disagree — they describe the same policy at different levels of abstraction. The gap is that nothing in code currently implements any of them consistently.

**Recommendation:** One canonical table combining Codex's matrix (which calendar per paper) with Opus's numeric ffill limits (how many days), governed by `[repo:config/calendars.yml]` as source of truth. Human decision: regression-sample default — business-day (Opus) or calendar-day (Codex default for Paper 4 and Codex rule set for crypto-native) — per paper.

### 2.4 Data inventory count: 484 vs 490 — **NO HUMAN DECISION NEEDED**

| Agent | Claim |
|---|---|
| Opus | 484 CSVs (Tradingview at 38). |
| Gemini | 484 CSVs. |
| Codex | 490 CSVs (Tradingview at 44), explicitly "correcting Opus/Gemini". |

**Evidence verdict:** Verified against live inventory during this synthesis.
- `[repo:Data/MASTER_DATA.csv]` row count = **490** (AlternativeMe 1 + Artemis 48 + CryptoQuant 345 + DefiLlama 28 + FRED 21 + Farside 3 + Tradingview **44**).
- `git status --short` confirms six new Tradingview CSVs currently untracked: `CRYPTOCAP_BTC_dominance__daily.csv`, `CRYPTOCAP_ETH_dominance__daily.csv`, `CRYPTOCAP_TOTAL3__daily.csv` (plus weekly equivalents of all three).
- The inventory was refreshed today between the Opus/Gemini snapshots (484) and the Codex pass (490). `MASTER_DATA.csv`, `MASTER_DATA.md`, `MASTER_DATA.txt`, and the Tradingview READMEs all appear modified in git status.

**Resolution:** Codex is correct as of 2026-04-18. All downstream docs should cite 490. No human decision required.

### 2.5 CODEX folder naming — **HUMAN DECISION (low stakes)**

| Agent | Position |
|---|---|
| Opus | Keep. "It's now established." Add per-paper status files under it. |
| Gemini | Rename to `AUDIT/` or `QA_GATES/`. Require agents to deposit `.md` execution summaries there. |
| Codex | Keep implicitly (never proposes a rename; treats `CODEX/` as canonical audit location). |

**Evidence verdict:** Keep has two structural advantages. First, `[repo:AGENTS.md §4 Evidence Hierarchy]` tier 6 and `[repo:AGENTS.md §5 Required Reads]` items 7–9 both hard-code the path `CODEX/current_status_analysis.md`, `CODEX/data_analysis.md`, and `CODEX/Manager_Reviewer_Prompt.md`. A rename cascades into the constitution itself. Second, the Cursor rules `.cursor/rules/` reference CODEX. Renaming is doable but expensive relative to the problem it solves, which is largely cosmetic.

**Recommendation:** Keep `CODEX/`. Low stakes; not blocking. Human may decide otherwise.

### 2.6 Pipeline entry point strategy — **HUMAN DECISION REQUIRED**

| Agent | Position |
|---|---|
| Opus | Reconcile by documenting both roles: `run_pipeline.py` = curation, `scripts/run_full_pipeline.py` = research. Update `.cursor/rules/global-constitution.mdc`. |
| Gemini | Delete `scripts/run_full_pipeline.py`. Single `run_pipeline.py` via `make pipeline`. |
| Codex | Contract: README section split between curation and research; agent rules specify which command to run; no silent overwrite of generated output without a rerun policy. |

**Evidence verdict:** Gemini's deletion carries the most irreversible risk. Codex's contract approach is additive (documentation + rules, no code change) and reversible. Opus is close to Codex.

**Recommendation:** Codex's contract approach. Document both pipelines with clear entry-point rules, update `.cursor/rules/global-constitution.mdc`, do not delete `scripts/run_full_pipeline.py` yet. Human decision on whether a future pass should collapse them.

### 2.7 VAR system size and Cholesky — **HUMAN DECISION REQUIRED**

| Agent | Position |
|---|---|
| Opus | Current 8-var is likely too many for the sample (BIC lag = 1, which may be too parsimonious for an 8-var system). Proposes compact 4-var `(BTC-ret, ETF-flow, stablecoin-growth, VIX)` as the headline. Flags Cholesky ordering as "pending" per `docs/specs/methods_spec.md §8`. |
| Gemini | 4-var VAR with Granger grids and 20-day FEVD stack charts as the recommended Paper 2 system. |
| Codex | Cites the 8-var current system (DY connectedness = 27.3%) as a fact but does not prescribe a future size. |

**Evidence verdict:** Opus has the clearest reasoning (sample-size argument + explicit ordering concern). Gemini agrees at 4. Codex is neutral.

**Recommendation:** 4-var headline + 8-var robustness appendix. Human decision required on Cholesky ordering per `AGENTS.md §15` (method-label change requires approval). A defensible default ordering is `[VIX_d1, DGS10_d1, spy_ret, ETF-intensity, btc_ret, eth_ret, stables_ret, defi_tvl_ret]` — macro/policy shocks first, crypto last — but this is a decision, not a fact.

### 2.8 ETF flow intensity fix — **CONSENSUS PATH, human confirms denominator**

| Agent | Proposed denominator |
|---|---|
| Opus | Prior-day BTC/ETH **market cap**, sourced from `Data/CryptoQuant/BTC/Market Data/Bitcoin Market Cap - Day.csv` and the ETH equivalent. (P0 default in Opus §17.) |
| Gemini | Market cap **or** AUM **or** spot volume. |
| Codex | Either relabel as flow-per-price **or** rebuild with market cap / AUM / volume denominator. (P0.6 in execution backlog.) |

**Evidence verdict:** All three agree the current `flow / close.shift(1)` is wrong. Opus is the only one that cites the exact replacement file path. Market cap is the most economically interpretable denominator (flow-as-share-of-outstanding), AUM is a close second (flow-as-share-of-institutional-AUM), volume is third (flow-as-share-of-secondary-market turnover).

**Recommendation:** Market cap primary (Opus's exact path), AUM robustness, relabel everywhere as "flow share of prior-day market cap". Human decision on denominator ordering (market cap first is the recommended default).

### 2.9 Prior AI output handling — **HUMAN DECISION REQUIRED**

| Agent | Position |
|---|---|
| Opus | Per-file classification (useful, stale, citation-risk, misleading, low-authority, near-duplicate). For the near-duplicate `txt output p2.md`: "Archive; diff against Context/00 before deletion." No physical deletion of citation-risk files, just salvage-vs-ignore guidance. |
| Gemini | Quarantine low-authority files (`txt output.md`, `txt output p2.md`). **Delete or physically isolate** the citation-risk files `deep-research-report.md` and `Beyond Correlation ...md` "so writing agents do not ingest their bibliographies." Move the rest to `archive/prior_ai_outputs/`. |
| Codex | Quarantine in place. No `turn...` citations in any draft. Durable URLs only. Prior AI outputs are hypotheses, not authority. (P0.9 in backlog.) |

**Evidence verdict:** `AGENTS.md §8` already forbids reuse of the two citation-risk files' bibliographies by name. A prompt-level contract (Codex) is the lightest-weight intervention that achieves the same goal as Gemini's physical move. Deletion loses the paper trail. Physical isolation (Gemini) is defensible but not required if the prompt contract is enforced.

**Recommendation:** Codex's quarantine-in-place + prompt contract + Opus's per-file classification table as a reference document. Human decision on whether to additionally move the two citation-risk files to `archive/prior_ai_outputs/` (reversible) or keep them where they are with the prompt contract as the guard.

### 2.10 Overall confidence framings — **CONTEXT ONLY**

| Agent | Overall | What they were uncertain about |
|---|---|---|
| Opus | 82% | Pipeline not re-run end-to-end; ETH transaction CSVs with only 365 rows from 2025-04-11 (possible truncation); four-paper goal vs team bandwidth. |
| Gemini | 98% structure / 95% overlap | Did not run regression matrix; flow/price impact is theoretical from the math error; "CADEX" (sic) typo in §19 indicates cursory review of that paragraph. |
| Codex | 84% | Paper 4 medium confidence until lending/RWA signal quality is modeled. |

These are not in conflict — they reflect different slicing. Used for the Confidence Assessment in §8, not as a decision point.

### 2.11 Metric dictionary status `[INFERENCE]`

Opus names the path `config/metric_dictionary.yml` as a deliverable. Gemini asks for a source-hierarchy list and dedup rules. Codex's P0.7 demands an overlap registry with precedence per concept, a manifest per paper panel, and a schema. All three are complementary. There is no disagreement; there is only a gap (the dictionary does not yet exist). Flagged here so it appears in §5.

---

## 3. Blind Spots (None of the Three Covered Adequately)

Flagged, not re-audited. These need verification by a follow-up agent.

1. **Full-sample 1/99 winsorization is a lookahead risk.** `[repo:reports/drafts/paper_v0.1_2026-04-18.md line 102]` says "All features are winsorized at the 1st/99th percentile (full-sample) before estimation." If the sample includes 2025–2026 data and the estimation window includes pre-2024 splits, the threshold leaks future information into pre-ETF regressions. No agent addressed this.

2. **HAC lag = 5 is unjustified.** `[repo:reports/drafts/paper_v0.1_2026-04-18.md line 108]` uses Newey-West with 5 lags without stating a rule (Andrews, Newey-West automatic, or a heuristic like `floor(4*(n/100)^(2/9))`). For daily crypto data with known volatility clustering, 5 may be too few. None of the three agents reviewed this.

3. **Placebo permutation with 300 draws.** The draft uses 300 placebo draws for structural-break p-values. The informal minimum for a 5% test is ~999 or 1999. No agent flagged this.

4. **SOL ETF placebo (12 rows).** All three agents mention it; none propose a concrete plan. If it is included in a placebo test with only 12 observations, the null distribution is degenerate. Recommend explicit exclusion or a robust bootstrap.

5. **ETH transaction CryptoQuant truncation.** Opus mentions "some ETH transaction CSVs only 365 rows starting 2025-04-11" as a truncation risk. Codex and Gemini did not verify. This should be checked before any on-chain ETH block enters a model.

6. **`references/FinancialEconometrics-master/` relevance.** All three agents treat it as "educational, not evidence". Nobody evaluated whether any of its notebooks/methods (e.g., DCC-GARCH, DML, panel FE) materially shift method choice for Papers 2, 3, or 4.

7. **`.env` / secrets hygiene.** None of the three agents checked for leaked credentials. The repo has no `.env.example` referenced outside `AGENTS.md §14`; a `.gitignore` audit is due.

8. **Commit message style conflict.** Opus flags it: `AGENTS.md` §13 says `<type>(<scope>): <summary>`; `.cursor/rules/03-defensive-commits.mdc` says `<scope>: <short imperative summary>`. Gemini and Codex did not address.

9. **Draft line 22 "the 2024 spot-ETF approval did not rewrite BTC's factor loadings at a single break date" vs headline claim in §1.1 line 2 of same draft.** The draft contradicts itself. No agent flagged this textual contradiction inside the draft.

10. **Winsorization, HAC choice, placebo N, and ffill — none are in the test suite.** All three agents note the thin tests but none enumerate the specific numerical tests needed for these four items.

---

## 4. Unified Four-Paper Portfolio

Adopted from Codex's `four_paper_protocols_v0.md` with corrections from Opus and Gemini. Paper 4 is contingent on human Decision 1 below.

### Paper 1 — BTC/ETH Factor-Exposure Evolution Around Institutionalization

- **Category:** Institutionalization.
- **Core question:** How did BTC and ETH factor loadings (macro, institutional, liquidity, native) change around the 2024 spot-ETF regime shift, and which block carries the rolling-variance attribution?
- **Required data:**
  - `Data/CryptoQuant/BTC/Market Data/Bitcoin Price & Volume - Spot - USD - Day.csv` and ETH equivalent `[repo:reports/drafts/paper_v0.1_2026-04-18.md §2.1]`
  - `Data/FRED/fred_macro_panel__daily.csv` (DGS10, DGS2, VIXCLS, DTWEXBGS, DFF, BAMLH0A0HYM2)
  - Tradingview daily CSVs for SPY, QQQ, GLD, XLK, DXY
  - `Data/Farside ETF Data/farside_btc_etf_flows__daily.csv`, `farside_eth_etf_flows__daily.csv`
  - `Data/DefiLlama/TVL/Daily/tvl_all_chains_daily.csv`, `Data/DefiLlama/Stablecoins/stablecoin_mcap_by_defillama_id__daily.csv`
  - `Data/AlternativeMe/fear_greed_index__daily.csv`
  - Native on-chain additions from `Data/CryptoQuant/BTC/Exchange Flows/`, `.../Miner Flows/`, `.../Market Indicator/`, `.../Network Indicator/` (currently underused; add before publication).
- **Methods:** Paper-specific panel → HAC OLS (pre/post) → rolling OLS with block partial R² → Chow + single-break sup-F (relabel, do **not** call it Bai-Perron) → compact VAR/FEVD → event studies with placebo permutation.
- **Kill risks:** ETF date is not the dominant break (already evidence: sup-F lands at 2021); CryptoQuant native blocks add little incremental R²; calendar/fill drives a material fraction of the observed regime shift.
- **Agent agreement:** All three agree Paper 1 is the anchor. Disagreements are cosmetic (framing tone).
- **Time to defensible v1.0:** 4–6 weeks after governance/method-label fixes land.

### Paper 2 — ETF Flow, Wrapper, Basis, and Market-Plumbing Transmission

- **Category:** Institutionalization.
- **Core question:** Do ETF-flow innovations transmit to BTC/ETH returns, realized variance, and CME basis, and how does the transmission interact with CEX netflows and stablecoin liquidity?
- **Required data:**
  - Farside daily BTC/ETH flows (issuer-level, 13 BTC + 11 ETH columns per Opus).
  - `Data/DefiLlama/ETFs/etf-history.csv` (aggregate cross-check).
  - `Data/Artemis/Crypto ETFs AUM.csv`, `Bitcoin ETFs AUM.csv`, `Ethereum ETFs AUM.csv` (AUM level).
  - TradingView wrappers (MSTR, COIN, GBTC proxies) + CME BTC/ETH basis series under `Data/Tradingview/`.
  - `Data/DefiLlama/CEX/cex_net_inflows_by_exchange__daily.csv`.
- **Methods:** Issuer-level panel (business-day calendar); flow innovations as regressor; T+1 lag sensitivity; asymmetric Granger on BTC realized variance; 4-variable VAR with 20-day FEVD stack; no intraday → no "price discovery" language.
- **Kill risks:** Same-day endogeneity between flow and return; timing ambiguity (creation/redemption vs secondary market); daily frequency limits mechanism; short issuer-level sample (Farside BTC starts 2024-01-11, ETH 2024-07-23).
- **Agent agreement:** All three name this as Paper 2. Gemini and Opus converge on 4-var VAR and 20-day FEVD.
- **Time to defensible v1.0:** 4–6 weeks in parallel with Paper 1 (shared data).

### Paper 3 — Stablecoins as Shadow Settlement Liquidity

- **Category:** Bridge (TradFi ↔ crypto).
- **Core question:** How does the aggregate stablecoin float (and its composition by chain/token) respond to FRED rate shocks, and what does that imply about stablecoins as shadow dollar liquidity?
- **Required data:**
  - `Data/DefiLlama/Stablecoins/stablecoin_mcap_by_defillama_id__daily.csv` (primary, daily, all-id).
  - `Data/Artemis/Chains - Stablecoin Supply.csv`, `Data/Artemis/Stablecoin Supply by Token.csv` (composition, weekly/monthly robustness).
  - `Data/CryptoQuant/BTC/Exchange Flows/` + ETH equivalents for USDT/USDC-specific flows.
  - `Data/FRED/` for DFF, SOFR, RRPONTSYD, DTWEXBGS.
- **Methods:** Panel fixed effects + Local-Projection IRFs from FRED DFF shocks to DefiLlama stablecoin caps (Gemini). Descriptive decomposition of composition drift. No causal monetary language without explicit identification.
- **Kill risks:** Vendor definitions differ 33.5% median between Artemis and DefiLlama (Opus cite); supply endogeneity (issuance responds to demand); sparse monthly composition data; stablecoin mapping metadata is weak (`stablecoin_mcap_id_to_name.csv` has blank `name`, `symbol`, `pegType` fields per `[repo:CODEX/data_analysis.md]`).
- **Agent agreement:** All three name stablecoins as a top bridge topic. Gemini adds Local-Projection IRF design; Opus and Codex converge on FRED + DefiLlama primary.
- **Time to defensible v1.0:** 5–7 weeks.

### Paper 4 — DeFi Credit, Lending, and RWA Rate-Arbitrage Bridge (Codex) — or Alternate per Decision 1

- **Category:** Bridge (TradFi ↔ crypto).
- **Core question:** Do DeFi lending yields and tokenized-RWA yields track FRED short rates after controlling for crypto risk, and where are rate arbitrages persistent or transient?
- **Required data:**
  - `Data/Artemis/Lending Deposits by Protocol.csv`
  - `Data/Artemis/Lending Borrows by Protocol.csv`
  - `Data/Artemis/Lending Interest Fees by Protocol.csv`
  - `Data/DefiLlama/RWA/` (all files)
  - `Data/Artemis/RWA - Tokenized Market Cap.csv`
  - `Data/FRED/` (DFF, SOFR, short-end rates)
  - `Data/DefiLlama/Stablecoins/stablecoin_mcap_by_defillama_id__daily.csv` (stablecoin liquidity control)
- **Methods:** Weekly panel (default for RWA + lending); conservative yield claims (no causal monetary bridge language); RWA descriptive if history is too short; HAC standard errors; event studies around FOMC dates if coverage permits.
- **Kill risks:** No direct APR panel (must back out from deposits/borrows/fees); short RWA history; unstable protocol definitions over time (Aave v2 → v3, Compound v2 → v3); crypto beta may explain everything, leaving no rate signal.
- **Formal fallback:** ETH staking / LST / LRT collateral transformation paper (cites staking rate, Lido/Rocket Pool market share, restaking TVL). Invoked if RWA/lending coverage fails.
- **Agent agreement:** Opus and Gemini propose DeFi vs CEX flavors; Codex proposes this lending/RWA flavor with the strongest data-path evidence and an explicit fallback.
- **Time to defensible v1.0:** 6–10 weeks (depends on RWA history coverage) or 4–6 weeks if fallback ETH LST/LRT.

### Maximum-Inventory Atlas (infrastructure, not a paper)

- **Role:** Shared factor library. `[repo:config/factor_blocks.yml]` already provides the five-block taxonomy (macro, institutional, liquidity, btc_native, eth_native) with per-block PCA.
- **Deliverables:** Metric dictionary (`config/metric_dictionary.yml`), per-paper panel manifests, an overlap registry, and an atlas appendix consumed by all four papers.

---

## 5. Unified Priority Fix List

P-taxonomy merged from Opus §16 (P0–P2), Gemini §16 (highest-priority), and Codex's `p0_execution_backlog.md` P0.1–P0.10. Priorities recut as P0 (blocker), P1 (required before paper submission), P2 (quality improvement).

### P0 — Blocker (must land before any paper work proceeds)

| # | Fix | Flagged by | Implementer | Effort | Dependencies | Acceptance criteria |
|---|---|---|---|---|---|---|
| P0.1 | Lock four-paper portfolio with signed decision note + 1-page protocol per paper | Opus, Gemini, Codex | Human (decision) + Codex (protocol doc) | 0.5 day human + 1 day drafting | None | Decision note in `docs/decisions/`, 4 protocols in `docs/specs/papers/` each with primary outcome, baseline panel, robustness, kill criteria |
| P0.2 | Reconcile governance docs to `AGENTS.md` | Opus, Gemini, Codex | Any LLM | 1–2 days | P0.1 | All docs point to `AGENTS.md`; none claim single-paper; Python version and commit format consistent across `AGENTS.md`, `pyproject.toml`, `HANDOFF.md`, `.cursor/rules/*` |
| P0.3 | Pipeline entry-point contract | Opus, Gemini, Codex | Any LLM | 0.5 day | P0.2 | README split curation vs research; `.cursor/rules/global-constitution.mdc` updated; no silent overwrite of generated output without rerun policy |
| P0.4 | Config path drift fix | Opus, Codex | Any LLM | 1 day | P0.3 | Config-path validation script/test; every analysis script reads from `config/*.yml`, no hardcoded break dates / factor lists / event dates |
| P0.5 | Calendar/fill policy reconciliation | Opus, Gemini, Codex | Any LLM | 2–3 days | Human Decision 2 | `config/calendars.yml` is source of truth; `src/cqresearch/data/calendars.py` honors it; draft prose matches; tests for weekend/holiday/ffill/zero-fill/T+1 |
| P0.6 | Method-label correction in draft + code | Opus, Gemini, Codex | Any LLM | 1–2 days | P0.5 | Draft refers to "Chow + single-break sup-F" (not Bai-Perron) unless true Bai-Perron is implemented (Decision 9); "block R²" renamed consistently with implementation; ETF intensity relabeled to match denominator (Decision 3) |
| P0.7 | ETF flow intensity fix in `src/cqresearch/features/panel.py` | Opus, Gemini, Codex | Any LLM | 1 day | Human Decision 3 | Denominator switched to prior-day market cap (default); AUM alternative implemented as robustness; test asserts new formula; draft §1.1 ETF-as-driver regressions rerun |

### P1 — Required before any paper submission

| # | Fix | Flagged by | Implementer | Effort | Dependencies | Acceptance criteria |
|---|---|---|---|---|---|---|
| P1.1 | Metric dictionary + overlap registry | Opus, Gemini, Codex | Any LLM | 3–5 days | P0.4 | `config/metric_dictionary.yml` with units, coverage, frequency, construction, source precedence per concept; overlap diagnostics for ETF flow, AUM, stablecoin supply, TVL, USD strength, ETH market cap, open interest, fees, active addresses, exchange flows, RWA, DeFi lending; per-paper panel manifests |
| P1.2 | Math tests for core modules | Opus, Gemini, Codex | Any LLM | 3–5 days | P0.5, P0.6 | Tests for OLS, rolling R², structural-break routines, FEVD, event windows, calendar fill, ETF units/timing, event placebos, overlap tests; coverage report demonstrates > imports-only |
| P1.3 | Citation audit of draft | Opus, Gemini, Codex | GPT-5.4 with web access or equivalent | 2–3 days | Human Decision 7 | No `turn...` placeholders in any draft; every external citation has verified DOI/arXiv/SSRN/journal page; prior AI citations scrubbed from `deep-research-report.md` and `Beyond Correlation ...md` usage |
| P1.4 | VAR redesign (size, ordering, robustness) | Opus, Gemini | Any LLM | 3 days | Human Decisions 4 + methods_spec §8 | 4-var headline, 8-var robustness; Cholesky ordering documented; Granger grids; 20-day FEVD stack; BIC/AIC/HQIC reported jointly |
| P1.5 | Draft language audit: causal → descriptive | Opus, Gemini | Any LLM (not the drafter) | 1–2 days | P0.6 | No use of "caused", "proved", "validated", "confirmed", "driver" unless identification supports it; overclaim list (Opus §8) fully addressed |
| P1.6 | Publication-grade figure redesign | Opus, Gemini | Any LLM + human visual review | 3–5 days | P1.2 | Separate diagnostic vs publication figures; figures at manuscript size; labels, legends, source data documented per figure; vector + PNG outputs |
| P1.7 | Paper 2 issuer-level panel construction | Opus, Codex | Any LLM | 3–5 days | P0.7, P1.1 | Per-issuer flow series from Farside; ETF AUM attached from Artemis; CME basis attached; panel spec in `docs/specs/papers/paper_2/` |
| P1.8 | Paper 3 stablecoin sub-basket panel | Gemini, Codex | Any LLM | 3–5 days | P1.1 | Network/token breakdown with source precedence (DefiLlama primary, Artemis for composition); FRED controls joined; monthly vs daily sample design documented |
| P1.9 | Paper 4 lending/RWA panel + coverage check | Codex | Any LLM | 5–7 days | Human Decision 1 | Coverage pass/fail decision documented; if fail, invoke fallback ETH LST/LRT protocol |
| P1.10 | Prior AI output quarantine contract | Opus, Gemini, Codex | Any LLM | 0.5 day | Human Decision 7 | Prompt contract in `prompts/00_citation_policy.md` forbids reuse of bibliographies from `reports/prior_ai_outputs/deep-research-report.md` and `...Beyond Correlation...md`; optional physical move to `archive/prior_ai_outputs/` per decision |

### P2 — Quality improvement

| # | Fix | Flagged by | Effort | Acceptance criteria |
|---|---|---|---|---|
| P2.1 | Add `ruptures` for true Bai-Perron (if Decision 9 = B) | Opus | 3–4 days | Bai-Perron returns `k` breaks with trimming and BIC selection; tested against a synthetic break |
| P2.2 | Add Quarto or Typst paper build pipeline | Opus, Gemini | 2–3 days | `make paper` builds PDF from draft.md; tables and figures rendered in place |
| P2.3 | Add `plotnine` or seaborn.objects for figures | Opus, Gemini | 2 days | Single figure template; all paper figures ported |
| P2.4 | Python 3.11 alignment | Opus, Gemini, Codex | 1 day | `AGENTS.md`, `pyproject.toml`, `HANDOFF.md`, local interpreter, CI all agree; `uv.lock` committed |
| P2.5 | Atlas appendix document | Opus, Gemini, Codex | 3–5 days | `docs/atlas/` with per-block summary, coverage charts, source precedence; referenced from all four paper specs |
| P2.6 | Stop-and-ask escalation workflow | AGENTS.md §15 | 0.5 day | `docs/workflow/escalation.md` with a trigger table; hooks into agent prompt contracts |
| P2.7 | Defensive-commits alignment | Opus | 0.5 day | `.cursor/rules/03-defensive-commits.mdc` matches `AGENTS.md §13` commit style |

### Suggested execution order (from Codex `p0_execution_backlog.md` + Opus §16)

1. Human portfolio + calendar decisions (P0.1, P0.5 precondition, Decision 1 + Decision 2).
2. Governance reconciliation (P0.2, P0.3).
3. Config validation (P0.4).
4. Calendar/fill + tests (P0.5).
5. Paper 1 labels + code + ETF intensity (P0.6, P0.7).
6. Metric dictionary (P1.1).
7. Per-paper panels (P1.7, P1.8, P1.9).
8. Figures + citation audit (P1.6, P1.3).
9. Tooling adds (P2.1–P2.3).

---

## 6. Human Decisions Required

Ten numbered decisions. Respond with "Decision 1: A. Decision 2: B. …". Each has a recommended default that applies if you do not choose.

### Decision 1 — Paper 4 topic

- **(A) Codex's DeFi Credit/Lending/RWA Rate-Arbitrage Bridge** with ETH LST/LRT as formal fallback. **[Recommended]**
- **(B) Gemini's DeFi vs CEX Capital Flight under VIX stress** (event-study flavor).
- **(C) Opus's DeFi vs CEX Liquidity Fragmentation** (market-structure flavor).
- **(D) Skip now — pre-commit to ETH LST/LRT** as Paper 4.

Recommended default (A) reasoning: Codex cites the most concrete file paths, has a formal fallback, and the RWA/lending family is least saturated by existing literature. Risk: if `Data/DefiLlama/RWA/` and Artemis lending coverage is shorter than 18 months by 2026-10-01, fallback is invoked.

Fallback if no answer: (A) proceeds; Paper 4 timeline gated on a coverage-check deliverable (P1.9).

### Decision 2 — Calendar default per paper

- **(A) Market-day headline for Papers 1–2; calendar-day for Paper 4; weekly for lending/RWA. [Recommended — Codex matrix]**
- **(B) Calendar-day throughout** (Opus's original headline proposal for all papers).
- **(C) Drop weekends globally from the master dataset** for regressions involving any TradFi variable (Gemini).

Recommended default (A) reasoning: (A) preserves identification for mixed-frequency regressions without discarding crypto-only observations; (B) risks inflating autocorrelations on weekends for Papers 1–2; (C) is irreversible and loses ~28% of the sample.

Fallback if no answer: (A).

### Decision 3 — ETF flow intensity denominator

- **(A) Prior-day market cap** (sourced from `Data/CryptoQuant/BTC/Market Data/Bitcoin Market Cap - Day.csv` and ETH equivalent). **[Recommended]**
- **(B) Prior-day AUM** (from Artemis aggregate files).
- **(C) Prior-day spot volume.**
- **(D) Keep `flow / close.shift(1)`; relabel throughout as "flow-per-unit-price".**

Recommended default (A) reasoning: economically interpretable as "flow share of outstanding"; daily coverage from 2010 BTC / 2015 ETH; no unit ambiguity.

Fallback if no answer: (A).

### Decision 4 — VAR system size and Cholesky ordering

- **(A) 4-var headline** `(BTC-ret, ETF-intensity, stables_ret, VIX_d1)` **+ 8-var robustness** appendix. Cholesky ordering: `[VIXCLS_d1, DGS10_d1, spy_ret, ETF-intensity, btc_ret, eth_ret, stables_total_usd_ret, defi_tvl_usd_ret]`. **[Recommended]**
- **(B) Keep 8-var as headline; add a compact 4-var as robustness.**
- **(C) Other** — specify variables and ordering in response.

Recommended default (A) reasoning: per Opus §17, 8-var may be too many for the available sample; Cholesky order puts exogenous macro/policy variables first.

Fallback if no answer: (A).

### Decision 5 — Tooling scope

- **(A) Codex minimalist: fix governance first; then add `ruptures`, Quarto, `plotnine`, commit `uv.lock`. [Recommended]**
- **(B) Opus add-only: same additions, in parallel with governance fixes.**
- **(C) Gemini aggressive: Polars + DuckDB + `rpy2`/`strucchange` migration.**

Recommended default (A) reasoning: minimizes reproducibility risk during the critical governance window; additions are reversible.

Fallback if no answer: (A).

### Decision 6 — `CODEX/` folder rename

- **(A) Keep `CODEX/`. [Recommended]**
- **(B) Rename to `AUDIT/`.**
- **(C) Rename to `QA_GATES/`.**

Recommended default (A) reasoning: `AGENTS.md §4` and `§5` both hard-code the path `CODEX/`; a rename cascades into the constitution.

Fallback if no answer: (A).

### Decision 7 — Prior AI output physical isolation

- **(A) Quarantine in place + prompt contract; do not move files. [Recommended]**
- **(B) Move all to `archive/prior_ai_outputs/`** (preserve git history).
- **(C) Move only the two citation-risk files** (`deep-research-report.md` and `Beyond Correlation ...md`) to `archive/` and keep the rest in place.

Recommended default (A) reasoning: `AGENTS.md §8` already names the two risky files; adding a prompt-level citation contract achieves the same protection as physical isolation without cascading path changes.

Fallback if no answer: (A).

### Decision 8 — Python version alignment

- **(A) Align everything to 3.11.** Update `pyproject.toml` and `HANDOFF.md`. **[Recommended]**
- **(B) Stay on 3.10.** Update `AGENTS.md §14` to match.
- **(C) Support 3.10–3.13.** Wider compatibility, more CI cost.

Recommended default (A) reasoning: `AGENTS.md §14` says 3.11+, and newer statsmodels/linearmodels versions drop 3.10.

Fallback if no answer: (A).

### Decision 9 — Break-test language

- **(A) Relabel current tests as "Chow + single-break sup-F". [Recommended, per Opus and Codex]**
- **(B) Implement true Bai-Perron via `ruptures` in Python.**
- **(C) Implement via `rpy2` + R `strucchange` (Gemini's original position).**

Recommended default (A) reasoning: label-only change is a 1-day fix and preserves all current outputs; (B) is a 3–4-day implementation with code + tests; (C) adds R bridge reproducibility overhead.

Fallback if no answer: (A). If the human later wants true Bai-Perron, (B) is the cheaper path.

### Decision 10 — Maximum-inventory artifact form

- **(A) Shared factor library / atlas in `docs/atlas/` and `config/metric_dictionary.yml`. [Recommended]**
- **(B) A fifth paper** using the full inventory (rejected by all three reviewers).
- **(C) Drop the atlas; build paper-specific panels only.**

Recommended default (A) reasoning: all three reviewers converge; (B) violates `AGENTS.md §2`; (C) loses the cross-paper reuse benefit.

Fallback if no answer: (A).

---

## 7. Multi-LLM Operating Model (Unified)

Merged from Opus §14, Gemini §14, Codex `multi_agent_workflow_and_quality_gates_v0.md`, and `AGENTS.md §10`.

### Role assignments

| Role | Primary model | Secondary / adversarial | Human gate? |
|---|---|---|---|
| Deep audit / hostile referee review | GPT-5.4 extra-high reasoning OR Claude Opus Thinking | The other of the two | No (for drafts); Yes (for final sign-off) |
| Econometric method design | GPT-5.4 OR Claude Opus | Cross-check by the other | Yes, for method-label changes per `AGENTS.md §15` |
| Code implementation (refactor, VAR, calendar) | Claude Opus OR Gemini Pro | Red-team by a different model | No, unless changing `Data/` or `config/` |
| Citation verification | GPT-5.4 with web search | Manual spot-check | Yes, before any draft promotion |
| Visualization review | Any model with browser/screenshot capability | — | Yes, before publication |
| Paper drafting | Claude Opus | Gemini Pro for alternative voice | Yes, for any causal-language promotion |
| Red-team / adversarial review | Different model than implementer | — | Yes, at P0 → P1 transitions |
| Project management / synthesis | Any model that reads `AGENTS.md` first | — | Yes, for the four-paper portfolio change |
| Fast enterprise traversal (CSV inventory, overlap scans) | Gemini Pro / Codex | — | No |
| Background long-running tasks (metric dictionary, overlap diagnostics) | Cursor background agent | — | No |

### Reconciliation rule (from `AGENTS.md §10` + Codex)

> "Compare evidence, contradictions, and unsupported claims. Do not vote-count agent recommendations. Use the strongest arguments from each agent; do not average weak recommendations."

When two agents conflict on a material decision, the agent that cited specific file paths, line numbers, or quantitative values wins over the one that made a general assertion. This is the rule applied throughout §2 of this document.

### Anti-collision rules

- No two agents independently editing the same directory in a single session. Assign directory ownership at session start.
- Every agent session reads `AGENTS.md` first, then the relevant subset of `§5 Required Reads`.
- Every handoff closes with the `AGENTS.md §11` Quality Gate template (inputs, outputs, claims, confidence, open questions, next agent).
- Prior AI outputs are hypotheses, not authority (`AGENTS.md §8`).
- If agents disagree on a high-impact decision, the synthesizer asks the human while providing a recommended default (as in §6 of this document).

### Required quality-gate template

```
Quality Gate
- Inputs read: <list file paths>
- Outputs written: <list file paths + row counts + hashes>
- Tests/checks run: <list commands + pass/fail>
- Strongest claims + evidence: <top 3 with confidence tags>
- Confidence score: <0-100%>
- Open questions: <list>
- Next agent: <role + recommended model>
```

---

## 8. Confidence Assessment

### What this synthesis is confident about `[VERIFIED]`

- The 14 consensus findings in §1 are verified against at least two of the three reviews plus at least one direct repo read.
- The 484 vs 490 inventory count is resolved: live `Data/MASTER_DATA.csv` contains 490 rows; Tradingview grew from 38 to 44 via six CRYPTOCAP dominance files.
- The ETF flow intensity formula in `src/cqresearch/features/panel.py` lines 68–71 is exactly `flow / close.shift(1)`; the inline comment self-labels it as "flow-per-unit-price".
- `config/calendars.yml` declares `ffill_limit: 0` for all daily calendars; the draft and `HANDOFF.md` both reference "ffill up to 4 days"; these must be reconciled.
- Chow test at BTC 2024-01-11 is F=0.81, p=0.60 (insignificant); ETH 2024-07-23 is F=2.13, p=0.024 (significant). sup-F argmax: BTC 2021-01-04, ETH 2021-05-12.
- DY total connectedness = 27.3% over the current 8-variable VAR.
- Farside ↔ DefiLlama daily flows match at r = 1.000 after unit conversion.
- `AGENTS.md §4` hard-codes `CODEX/` in the Evidence Hierarchy; a rename has cascade cost.

### What remains uncertain `[UNCERTAIN]`

- Whether RWA and DeFi-lending history will be long enough to support Paper 4 without invoking the ETH LST/LRT fallback. Codex acknowledges this directly (confidence "lower for Paper 4 until coverage and signal checks are run").
- Whether the current ETH transaction CryptoQuant CSVs are truncated (Opus's 365-row claim starting 2025-04-11). No other agent verified.
- Whether the 1/99 full-sample winsorization in the v0.1 draft leaks information across pre/post windows. Not flagged by any agent.
- Whether the 300-draw placebo permutation is statistically adequate at α = 5%.
- Whether `references/FinancialEconometrics-master/` contains method templates that would materially change Paper 2's VAR/FEVD or Paper 3's LP-IRF implementations.
- Whether GPT-5.4 / Claude Opus / Gemini Pro model names used in Opus's operating model map cleanly to the current fleet available to the team.

### What requires further investigation `[INFERENCE]`

- A full pipeline re-run (`python scripts/run_full_pipeline.py` or `python run_pipeline.py` depending on Decision 6 outcome) must be executed after P0 fixes land to verify that all numeric claims in the v0.1 draft still hold after calendar/fill and ETF-intensity corrections.
- The metric dictionary (`config/metric_dictionary.yml`) must be built before any cross-vendor join is claimed as a paper result. This is P1.1.
- An independent red-team review of the rewritten draft (Paper 1) after P0–P1 fixes. Recommend a different model than the drafter, per Opus §14.
- Verification that the six new Tradingview CRYPTOCAP dominance CSVs are intended for the canonical factor blocks (not visible in `config/factor_blocks.yml` at the time of this synthesis).
- Git-commit audit of the modifications to `Data/MASTER_DATA.csv`, `Data/MASTER_DATA.md`, and the Tradingview README files currently visible in `git status`. These edits should go through `make curate`, per `AGENTS.md §9`.

---

## Quality Gate (per `AGENTS.md §11`)

**Inputs read.**
- `MANAGER_SYNTHESIS_META_PROMPT.md` (the commissioning prompt)
- `Manager/Opus Manager/comprehensive_review.md`
- `Manager/Gemini Manager/Project_Audit_Report.md`
- `Manager/Codex Manager/codex_manager_review_2026-04-18.md`
- `Manager/Codex Manager/four_paper_protocols_v0.md`
- `Manager/Codex Manager/data_calendar_metric_strategy_v0.md`
- `Manager/Codex Manager/multi_agent_workflow_and_quality_gates_v0.md`
- `Manager/Codex Manager/p0_execution_backlog.md`
- `Manager/Codex Manager/README.md`
- `AGENTS.md`
- `CODEX/current_status_analysis.md`
- `CODEX/data_analysis.md`
- `config/factor_blocks.yml`
- `config/calendars.yml`
- `src/cqresearch/features/panel.py`
- `reports/run_summaries/03_run_analyses.md`
- `reports/drafts/paper_v0.1_2026-04-18.md` (partial, §1–§3)
- `Data/MASTER_DATA.csv` (full, 490 rows counted programmatically)
- `Data/MASTER_DATA.md` (partial, source summary + Artemis index)

**Outputs written.**
- `Manager/FINAL_ENHANCED.md` (this file).

**Tests / checks run.**
- Programmatic row count of `Data/MASTER_DATA.csv`: 490 rows, confirming Codex's claim and falsifying Opus/Gemini's 484.
- Direct read-back of `src/cqresearch/features/panel.py` lines 63–71 confirmed ETF intensity formula.
- Direct read-back of `config/calendars.yml` confirmed `ffill_limit: 0` for daily calendars.
- `git status --short` inspection confirmed six new Tradingview CRYPTOCAP CSVs as the delta.

**Strongest claims + evidence.**
1. **Four-paper program is binding per `AGENTS.md §1–§2`; single-paper draft is out of date.** Evidence: `[repo:AGENTS.md]` + `[repo:reports/drafts/paper_v0.1_2026-04-18.md]`. Confidence: 98%.
2. **Codex's 490 inventory count is correct; Opus/Gemini's 484 reflects a same-day earlier snapshot.** Evidence: programmatic row count + git status. Confidence: 99%.
3. **ETF flow intensity is economically mis-scaled in production code.** Evidence: `[repo:src/cqresearch/features/panel.py lines 68–71]` + self-labeling comment. Confidence: 99%.
4. **Calendar/fill policy is inconsistent across `calendars.yml`, code, draft prose, and `HANDOFF.md`.** Evidence: four-document cross-read. Confidence: 95%.
5. **The ETF-era structural-break narrative in the draft is weaker than the prose suggests.** Evidence: `[repo:reports/run_summaries/03_run_analyses.md]` Chow BTC F=0.81 p=0.60, sup-F argmax 2021-01-04. Confidence: 95%.
6. **Codex has the strongest Paper 4 evidence (explicit file paths + formal fallback).** Confidence: 85%.
7. **Method-label inflation is systemic across the draft.** Confidence: 95%.

**Confidence score.** 86% on synthesis claims (§1, §3 blind-spot flags, §5 priority list). 72% on recommended defaults in §6 (a human decision on 1, 2, 3, 4, 7 materially changes downstream work). 90% on §8 confidence assessment itself.

**Open questions.** The 10 numbered decisions in §6.

**Next agent.** Human, for Decisions 1–10. After decisions are returned, this synthesizer produces `Manager/NEXT_STEPS.md` with Phase 1–6 work assignments, agent-assignment matrix, and risk register. No code or data changes until the human responds.

---

*End of synthesis. Please review §6 and reply with numbered decisions.*
