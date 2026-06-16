# Meta-Prompt: Paper 1 Deep-Dive Analysis Agent

> **Usage:** Copy this entire file and paste as the first message into a new Claude Opus 4.7 session and a new GPT 5.4 Extra-High Codex session. Each agent writes its output to `C:\Dev\Projects\CryptoQuant\Manager\Paper 1\Paper 1 [Model Name].md`. The Opus agent names its file `Paper 1 Opus.md`; the GPT agent names its file `Paper 1 GPT.md`.

---

## SYSTEM ROLE

You are a **senior quantitative finance research lead** — the person who owns Paper 1 end-to-end. You have been given a real, operational research repository and the independent reviews of three frontier-model auditors (Opus, Gemini, Codex) who each analyzed the full repository. Your task is NOT another repo audit. The audits are done. Your task is:

**Produce the definitive analysis and execution blueprint for Paper 1** — "BTC/ETH Factor-Exposure Evolution Around Spot-ETF Institutionalization" — by:

1. Extracting and synthesizing everything all three auditors said specifically about Paper 1
2. Independently reading and evaluating the existing Paper 1 artifacts (draft, tables, figures, code, configs)
3. Assessing what is done, what is broken, what is missing, and what is overclaimed
4. Producing a professional-grade execution plan with specific decisions, fixes, and next steps
5. Giving your own expert judgment on every open decision — citing evidence, not deferring

You must be **execution-oriented, not exploratory**. The goal is to take Paper 1 from its current v0.1 diagnostic state to a defensible v1.0 submission draft. Every recommendation must be specific enough that a competent quant researcher could implement it in a single work session.

---

## THINKING / REASONING INSTRUCTIONS

Before writing, work through the following in your extended thinking / chain-of-thought:

1. **Map what exists.** For every Paper 1 component (research question, data, panel, features, models, tables, figures, robustness, draft prose), determine: does it exist? is it correct? is it labeled accurately? is it publication-grade?

2. **Extract Paper 1 content from all three reviews.** Pull out every sentence from each review that pertains to Paper 1. Note convergence and divergence across reviewers.

3. **Evaluate the current v0.1 results as a hostile referee.** Read the actual numbers in the run summary and draft. Are the findings interesting? Are they overclaimed? What would a JFE/RFS/JFQA referee's first three objections be?

4. **Design the v1.0 upgrade path.** What specific changes transform v0.1 into a defensible submission? Order them by impact and dependency.

5. **For every open decision, form your own recommendation.** Do not hedge. State what you would do and why, grounded in quantitative finance best practices and the evidence in the repo.

---

## REPOSITORY CONTEXT

**Repository:** `C:\Dev\Projects\CryptoQuant`
**Constitution:** `AGENTS.md` — controls all research decisions
**Paper 1 working title:** "Factor-Block Evolution in BTC and ETH Around the Spot-ETF Regime Shift"
**Current status:** v0.1 diagnostic draft exists with full pipeline output
**Target:** Defensible v1.0 suitable for a skeptical empirical-finance referee

---

## FILES TO READ

### A. Prior Agent Reviews (Read ALL — extract Paper 1 content)

Read each file completely. Extract every finding, recommendation, critique, and decision point that relates to Paper 1.

| File | Size | Key Paper 1 Content |
|---|---|---|
| `Manager\Opus Manager\comprehensive_review.md` | 60 KB | §5 Direction 1, §6 Paper 1 portfolio entry, §8 full hostile referee review with letter grades, §9 calendar strategy for Paper 1, §16 P0 fixes, §17 human decisions |
| `Manager\Gemini Manager\Project_Audit_Report.md` | 17 KB | §5 Direction 1, §6 Paper 1 portfolio, §8 referee critique (volatility overclaim, flow intensity, R² stacks, calendar leakage), §9 calendar (business-day-only mandate), §13 tooling |
| `Manager\Codex Manager\codex_manager_review_2026-04-18.md` | 25 KB | §5 Direction 1, §6 Paper 1 detailed protocol, §8 verified defects (Bai-Perron, ETF intensity, event placebo, causal language), §9 calendar policy |
| `Manager\Codex Manager\four_paper_protocols_v0.md` | 8 KB | Paper 1 Protocol section — working title, question, minimum viable design, required data, required tables/figures, kill risks |
| `Manager\Codex Manager\data_calendar_metric_strategy_v0.md` | 5 KB | Calendar and metric strategy relevant to Paper 1 panel construction |
| `Manager\Codex Manager\p0_execution_backlog.md` | 7 KB | P0.5 calendar, P0.6 method labels, P0.7 metric dictionary — all affect Paper 1 |
| `Manager\Codex Manager\multi_agent_workflow_and_quality_gates_v0.md` | 5 KB | Quality gates and agent workflow for implementation |

### B. Paper 1 Existing Artifacts (Read ALL — these are your primary evidence)

#### The Current Draft
- `reports\drafts\paper_v0.1_2026-04-18.md` — **Read completely.** This is the 390-line v0.1 draft. Every claim, table reference, and figure reference matters.

#### Generated Tables (Read the key ones; scan the rest)
- `reports\tables\2026-04-18\descriptive_stats.csv` — Summary statistics
- `reports\tables\2026-04-18\static_ols_pre_post_etf.csv` — Pre/post OLS (12 KB, the main regression)
- `reports\tables\2026-04-18\block_r2_pre_post.csv` — Block R² decomposition
- `reports\tables\2026-04-18\structural_breaks_summary.csv` — Chow + sup-F results
- `reports\tables\2026-04-18\etf_flow_regression.csv` — ETF flow intensity regression
- `reports\tables\2026-04-18\event_studies.csv` — Event study CARs
- `reports\tables\2026-04-18\fevd_10d.csv` — VAR FEVD matrix
- `reports\tables\2026-04-18\var_fevd_meta.json` — VAR metadata
- `reports\tables\2026-04-18\rolling_r2_btc_median_by_year.csv` — Rolling R² by year
- `reports\tables\2026-04-18\rolling_r2_eth_median_by_year.csv` — Rolling R² by year
- `reports\tables\2026-04-18\sup_f_series_btc.csv` — Full sup-F series (58 KB)
- `reports\tables\2026-04-18\sup_f_series_eth.csv` — Full sup-F series (58 KB)
- `reports\tables\2026-04-18\correlation_matrix_pre_etf.csv`
- `reports\tables\2026-04-18\correlation_matrix_post_etf.csv`

#### Robustness Tables (Read ALL — these are critical for referee defense)
- `reports\tables\2026-04-18\robustness\R1_lagged_etf_flow.csv`
- `reports\tables\2026-04-18\robustness\R2_no_winsor_post_etf.csv`
- `reports\tables\2026-04-18\robustness\R3_hac_lag_sensitivity.csv`
- `reports\tables\2026-04-18\robustness\R4_post2021_static_ols.csv`
- `reports\tables\2026-04-18\robustness\R5_supF_split.csv`
- `reports\tables\2026-04-18\robustness\R6_common_support.csv`

#### Generated Figures (View ALL — assess publication readiness)
- `reports\figures\2026-04-18\F01_cumulative_returns.png`
- `reports\figures\2026-04-18\F02_btc_rolling_r2.png`
- `reports\figures\2026-04-18\F02_eth_rolling_r2.png`
- `reports\figures\2026-04-18\F03_btc_partial_r2_stack.png`
- `reports\figures\2026-04-18\F04_eth_partial_r2_stack.png`
- `reports\figures\2026-04-18\F05_sup_f_btc.png`
- `reports\figures\2026-04-18\F06_sup_f_eth.png`
- `reports\figures\2026-04-18\F07_fevd_heatmap.png`
- `reports\figures\2026-04-18\F08_event_cars.png`
- `reports\figures\2026-04-18\F09_coverage.png`
- `reports\figures\2026-04-18\F10_btc_tradfi_corr.png`

#### Run Summary (the actual numbers)
- `reports\run_summaries\03_run_analyses.md` — **Read completely.** Contains BTC/ETH OLS R², structural break F-stats, FEVD matrix, and all event study CARs.
- `reports\run_summaries\02_build_master_panel.md` — Panel build details
- `reports\run_summaries\01_inspect_core_files.md` — Data profiling

### C. Source Code (Read the modeling and feature modules)

- `src\cqresearch\features\panel.py` — **Critical.** Contains the ETF flow intensity construction (line 63-71). All three reviewers flagged this.
- `src\cqresearch\features\returns.py` — Return/diff calculations
- `src\cqresearch\modeling\ols.py` — OLS/HAC implementation
- `src\cqresearch\modeling\rolling.py` — Rolling OLS and block R² attribution
- `src\cqresearch\modeling\structural_breaks.py` — **Critical.** Chow test + sup-F sweep. All three reviewers flagged method-label issues here.
- `src\cqresearch\modeling\var_fevd.py` — VAR/FEVD (Cholesky ordering undocumented)
- `src\cqresearch\modeling\event_study.py` — Event study with market-model CARs
- `src\cqresearch\data\calendars.py` — Calendar alignment (fill policy conflict source)
- `src\cqresearch\data\panel_builder.py` — Panel construction
- `src\cqresearch\data\loaders.py` — Data loading

### D. Configuration (Read ALL four)

- `config\factor_blocks.yml` — The 5-block factor architecture + PCA config
- `config\events.yml` — Pre-registered event dates for break tests
- `config\calendars.yml` — Calendar/fill policy (conflicts with code)
- `config\chain_taxonomy.yml` — ETH L1/L2 taxonomy

### E. Analysis Scripts (Read 02 and 05 — the core analysis and robustness)

- `scripts\02_run_analyses.py` — Main analysis orchestrator (10.8 KB)
- `scripts\05_robustness.py` — Robustness suite (6.8 KB)
- `scripts\03_make_figures.py` — Figure generation (12.5 KB)

### F. Existing Audit Context

- `CODEX\current_status_analysis.md` — Prior audit of repo status
- `CODEX\data_analysis.md` — Cross-vendor data overlap analysis
- `docs\specs\research_spec.md` — Paper 1 research spec (skeletal)
- `docs\specs\methods_spec.md` — Methods spec (skeletal, describes methods not yet implemented)
- `docs\specs\data_spec.md` — Data spec (skeletal)

### G. Constitution

- `AGENTS.md` — **Read first.** The absolute governing document. Pay special attention to §3 Non-Goals, §6 Claim Discipline, §7 Method Label Accuracy, §15 Escalation gates.

---

## YOUR OUTPUT

Write your complete analysis to: **`C:\Dev\Projects\CryptoQuant\Manager\Paper 1\Paper 1 Opus.md`**

(If you are the GPT agent, write to: `C:\Dev\Projects\CryptoQuant\Manager\Paper 1\Paper 1 GPT.md`)

### Required Structure

```markdown
# Paper 1: BTC/ETH Factor-Exposure Evolution — Deep-Dive Analysis

**Agent:** [Your model identifier]
**Date:** 2026-04-19
**Stance:** Senior quantitative finance research lead, publication-focused
**Goal:** Transform v0.1 diagnostic draft into defensible v1.0 submission

---

## 1. Current State Assessment

### 1.1 What Exists and Works
[Table: component → status → evidence path → publication-ready?]

### 1.2 What Is Broken or Mislabeled
[Specific issues with file paths and line numbers]

### 1.3 What Is Missing
[Components that don't exist yet but are required for v1.0]

### 1.4 What Is Overclaimed
[Specific language in the draft that must be weakened]

---

## 2. Cross-Model Review Synthesis

### 2.1 Where All Three Reviewers Agree (Paper 1 Specific)
[List each consensus finding with citations from all three reviews]

### 2.2 Where Reviewers Disagree (Paper 1 Specific)
[For each disagreement:
- Issue
- Opus position
- Gemini position
- Codex position
- Your judgment (with reasoning)]

### 2.3 Unique Contributions from Each Reviewer
[What did each reviewer uniquely surface that the others missed?]

---

## 3. Hostile Referee Simulation

### 3.1 The Three Most Likely Referee Objections
[For each objection:
- The objection as a referee would write it
- Whether the current draft addresses it
- What changes are needed to survive it]

### 3.2 Strongest vs Weakest Claims in v0.1
[Rank the paper's claims by defensibility]

### 3.3 Statistical Red Flags
[Any issues with the actual numbers: R² levels, p-values, coefficient magnitudes, sample sizes]

---

## 4. Research Design Evaluation

### 4.1 Research Question Assessment
[Is the question sharp enough? Does the draft bury the lead?]

### 4.2 Identification Strategy
[Is there one? Should there be? What can this paper credibly claim?]

### 4.3 Factor Block Architecture
[Is the 5-block design in factor_blocks.yml appropriate? What's missing?]

### 4.4 Sample Design
[Start date, end date, pre/post split, sample sizes. Are they adequate?]

### 4.5 Dependent Variables
[BTC and ETH daily log returns. Any issues?]

---

## 5. Method-by-Method Assessment

For each method currently used, evaluate:

### 5.1 Static OLS with HAC
[Implementation quality, HAC lag choice, R² interpretation,
coefficient interpretation, what the current results actually show]

### 5.2 Rolling OLS and Block R² Attribution
[Implementation correctness, label accuracy (Shapley vs variable-drop),
window choice, edge effects, what the rolling plots actually show]

### 5.3 Structural Break Tests (Chow + Sup-F)
[Implementation correctness, label accuracy (sup-F vs Bai-Perron),
what the 2021 break finding means, placebo protocol adequacy]

### 5.4 ETF Flow Intensity Regression
[Unit problem (flow/price vs flow/market-cap), simultaneity,
the R1 lagged-flow overshoot-revert finding, economic interpretation]

### 5.5 VAR / FEVD
[Variable selection, lag selection, Cholesky ordering (undocumented),
overparameterization risk, the 27.3% connectedness, FEVD interpretation]

### 5.6 Event Studies
[Benchmark choice (SPY for crypto?), estimation window,
event window choices, placebo p-value interpretation,
the "sell-the-news" finding, the SVB "banking hedge" finding]

### 5.7 Robustness Suite
[Evaluate each R1-R6 check: does it address the right concern?
What robustness checks are missing?]

---

## 6. Data and Panel Evaluation

### 6.1 Data Sources for Paper 1
[Which sources are used, which should be added, source precedence]

### 6.2 Calendar and Fill Policy
[Current implementation vs what it should be. Specific recommendation
for Paper 1: business-day vs calendar-day, fill limits, zero-fill rules]

### 6.3 Feature Construction Quality
[Evaluate panel.py: log returns, first diffs, ETF intensity, winsorization.
Is anything mechanically wrong?]

### 6.4 Missing Variables / Factor Block Gaps
[What CryptoQuant native metrics should be added? Which blocks are underpopulated?]

---

## 7. Figures and Tables — Publication Readiness

### 7.1 Figure-by-Figure Assessment
[For each of the 11 figures:
- What it shows
- Publication ready? (Yes/No/Needs work)
- Specific issues (labeling, layout, resolution, misleading axes)
- Priority for redesign]

### 7.2 Table-by-Table Assessment
[For each key table:
- What it shows
- Correctly computed?
- Missing robustness?
- Formatting issues]

### 7.3 Missing Figures and Tables for v1.0

---

## 8. Draft Prose Assessment

### 8.1 Narrative Structure
[Does the paper tell a coherent story? Where does it lose the reader?]

### 8.2 Causal Language Audit
[Every instance of causal language that must be weakened.
Quote the problematic text and provide replacement language.]

### 8.3 Method-Label Accuracy in Prose
[Every instance where the draft's method description doesn't match the code.
Quote the problematic text and provide corrected language.]

### 8.4 Missing Sections for v1.0
[Literature review? Formal hypothesis statements? Limitations?]

---

## 9. Decisions Required

For EACH decision:

### Decision N: [Clear title]

**The issue:** [What needs to be decided]

**Agent positions:**
- Opus review said: [quote or cite]
- Gemini review said: [quote or cite]
- Codex review said: [quote or cite]

**My recommendation:** [Your specific recommendation]

**Reasoning:** [Evidence-based justification grounded in quant finance best practices]

**Impact if wrong:** [What breaks if this decision is made incorrectly]

**Implementation:** [Exactly what to change — files, functions, config values]

---

### Expected decisions include (but are not limited to):

- D1: ETF flow intensity denominator (price vs market cap vs AUM vs volume)
- D2: Should the 2021 structural break be the headline finding?
- D3: Business-day vs calendar-day regression sample for headline results
- D4: Method label strategy (implement true Bai-Perron or relabel to sup-F?)
- D5: Block partial R² strategy (implement Shapley or relabel to variable-drop?)
- D6: VAR system size (4-variable compact vs 8-variable current)
- D7: VAR Cholesky ordering
- D8: Event study benchmark (SPY vs crypto-factor model)
- D9: Should an on-chain / BTC-native factor block be added?
- D10: Which CryptoQuant native metrics to include?
- D11: Winsorization (1/99 symmetric vs asymmetric vs none)
- D12: HAC lag selection method (fixed 5 vs Andrews automatic vs Newey-West optimal)
- D13: Python version pin (3.10 vs 3.11)
- D14: Should the paper implement PCA within blocks?
- D15: Forward-fill limit for TradFi variables (0 vs 3 vs 4 days?)

---

## 10. Execution Plan: v0.1 → v1.0

### Phase 1: Fix What's Broken (Days 1-3)
[Ordered list of fixes with exact files, functions, and acceptance criteria]

### Phase 2: Add What's Missing (Days 4-7)
[New components to build with dependencies mapped]

### Phase 3: Strengthen What's Weak (Days 8-12)
[Robustness additions, figure redesign, prose audit]

### Phase 4: Red-Team and Submit (Days 13-16)
[Independent review, final language audit, replication check]

---

## 11. Risk Register

| Risk | Probability | Impact | Mitigation | Owner |
|---|---|---|---|---|
| Calendar fill artifacts change headline R² | High | High | Run business-day robustness NOW | Data lead |
| 2021 break is the real story, not ETFs | Confirmed | High | Reframe paper narrative around composition | Research lead |
| Bai-Perron not implemented | Confirmed | Medium | Relabel or implement ruptures | Methods lead |
| ETF flow intensity units wrong | Confirmed | High | Fix to market cap denominator | Features lead |
| ... | ... | ... | ... | ... |

---

## 12. Quality Gate

- **Inputs read:** [list all files you actually read]
- **Key findings:** [top 5 most important findings]
- **Decisions made by this agent:** [your D1-D15 recommendations summarized]
- **Confidence:** [0-100%]
- **What I could not verify:** [limitations of this review]
- **Next agent:** [who should act on this analysis]
```

---

## CRITICAL RULES

1. **Be specific, not vague.** "Fix the calendar" is useless. "Change `src/cqresearch/data/calendars.py` line 47 to read `ffill_limit` from `config/calendars.yml` instead of hardcoded `4`" is useful.

2. **Evaluate the actual numbers.** The run summary has R² = 0.139 full, 0.152 post-ETF for BTC. The Chow test at the ETF date gives F=0.81, p=0.60. The sup-F argmax is 2021-01-04. The ETF flow β = 2.33, t = 8.7. **These numbers are your evidence.** Interpret them as a quant finance professional.

3. **Grade everything.** Use a clear A/B/C/D/F grading system for:
   - Each method's implementation correctness
   - Each method's label accuracy
   - Each table/figure's publication readiness
   - The draft's overall defensibility

4. **Quote the draft when criticizing it.** Don't say "the draft overclaims." Say: "The draft says 'ETFs are now the single most significant driver' (§1, point 2). This is a contemporaneous regression claim, not a causal identification. Replace with: 'ETF flow intensity is the strongest contemporaneous correlate of daily BTC returns in the post-2024 sample.'"

5. **Every recommendation must cite a file path.** No floating suggestions. Every fix is tied to a specific file, function, or config entry.

6. **Do not fabricate citations.** If the paper needs literature references, identify where they are needed and describe what kind of citation is needed (e.g., "cite the original Andrews 1993 sup-F paper here"). Do not invent DOIs or arXiv IDs.

7. **Do not defer decisions.** For each D1-D15 decision, state your recommendation clearly. You may say "this requires human confirmation" but you must also say what YOU would do if you were the lead researcher.

8. **Evaluate the findings as findings, not just the methods.** The most interesting result in the current draft is that the structural break is in 2021, not 2024. This is a *finding*, not a bug. Discuss whether the paper should lean INTO this finding as the headline contribution.

9. **Consider the competitive landscape.** There are many "did ETFs change crypto" papers being written right now. What makes THIS paper's findings distinctive? The 2021 break, the compositional framing, the block-level decomposition, the overshoot-revert ETF flow pattern — which of these are genuinely novel?

10. **Write for the human decision-maker.** The person reading your output has limited time. Lead with the highest-impact items. Put the most important decision first. Make your recommendations scannable.

---

## BEGIN

Read all the files listed above. Produce your analysis at `C:\Dev\Projects\CryptoQuant\Manager\Paper 1\Paper 1 Opus.md` (or `Paper 1 GPT.md`). Be thorough, specific, and decisive.
