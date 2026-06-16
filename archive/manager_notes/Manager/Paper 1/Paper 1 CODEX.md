# Paper 1: BTC/ETH Factor-Exposure Evolution - Deep-Dive Analysis
**Agent:** Codex (GPT-5)
**Date:** 2026-04-19
**Stance:** Senior quantitative finance research lead, publication-focused
**Goal:** Transform v0.1 diagnostic draft into defensible v1.0 submission

---

## Executive Lead Decision

**Verified:** Paper 1 has a real empirical core, but the v0.1 draft is not submission-ready. The defensible result is not that spot ETFs caused a 2024 structural break. The defensible result is that the largest estimated BTC/ETH factor-structure break occurs in early 2021, while the ETF period adds a strong but endogenous contemporaneous flow channel. Evidence: `reports/run_summaries/03_run_analyses.md`; `reports/tables/2026-04-18/structural_breaks_summary.csv`; `reports/tables/2026-04-18/etf_flow_regression.csv`.

**Verified:** BTC does not show a meaningful Chow break at the BTC spot-ETF launch date in v0.1: F=0.813998, p=0.603274. BTC single-break sup-F peaks at 2021-01-04. ETH does show a stronger ETF-date Chow statistic, p=0.024016, but ETH single-break sup-F still peaks at 2021-05-12. Evidence: `reports/run_summaries/03_run_analyses.md`; `reports/tables/2026-04-18/structural_breaks_summary.csv`.

**Verified:** The 2026-04-19 uncommitted run is not a clean publication upgrade yet. It changes BTC headline R2 from 0.139 to 0.921 after adding `btc_mvrv_d1`, with `btc_mvrv_d1` t=48.8238 in the BTC full-sample OLS. That is a red flag for mechanical price-content leakage, not a result to publish. Evidence: `reports/run_summaries/03_run_analyses.md`; `reports/tables/2026-04-19/static_ols_pre_post_etf.csv`; `src/cqresearch/features/panel.py:42-44`.

**Inference:** The competitive contribution should be "factor composition changed across crypto institutionalization, and the ETF era is a flow-transmission layer inside that longer evolution." That is more distinctive and more defensible than another event-date ETF paper. Evidence: `Manager/Opus Manager/comprehensive_review.md:370-397`; `Manager/Gemini Manager/Project_Audit_Report.md:125-128`; `Manager/Codex Manager/codex_manager_review_2026-04-18.md:93-101`.

---

## 1. Current State Assessment

### 1.1 What Exists and Works

| Component | Status | Evidence path | Publication-ready? |
|---|---|---|---|
| Governing research constitution | Strong. It explicitly requires claim discipline, method-label accuracy, no causal overclaiming, and no hand edits to `Data/`. | `AGENTS.md` | Yes |
| v0.1 draft | Exists and is coherent enough as a diagnostic narrative, but overclaims mechanisms and method strength. | `reports/drafts/paper_v0.1_2026-04-18.md` | No |
| v0.1 generated table package | Exists for static OLS, block R2, breaks, ETF flow, event studies, FEVD, rolling R2, correlations, robustness. | `reports/tables/2026-04-18/` | Diagnostic only |
| v0.1 generated figures | Exists: 11 PNGs covering cumulative returns, rolling R2, partial R2 stacks, sup-F, FEVD, events, coverage, correlations. | `reports/figures/2026-04-18/` | No |
| Main run summary | Strongest compact source of the v0.1 numbers: OLS R2, structural breaks, FEVD, event CARs. | `reports/run_summaries/03_run_analyses.md` | Yes as evidence, not as paper prose |
| Master panel build summary | Exists and documents panel dimensions and coverage. | `reports/run_summaries/02_build_master_panel.md`; `reports/panels/master_daily_meta.json` | Yes as reproducibility evidence |
| Factor-block concept | Economically sensible five-block design: macro, institutional, liquidity/DeFi/stablecoins, sentiment, native/on-chain. | `config/factor_blocks.yml`; `docs/specs/research_spec.md` | Needs execution alignment |
| Static OLS with HAC | Implemented and produces pre/post ETF tables. v0.1 R2 levels are plausible. | `src/cqresearch/modeling/ols.py`; `scripts/02_run_analyses.py`; `reports/tables/2026-04-18/static_ols_pre_post_etf.csv` | Needs calendar/native fixes |
| Rolling OLS | Implemented and useful for diagnostics. | `src/cqresearch/modeling/rolling.py`; `reports/tables/2026-04-18/rolling_ols_btc_180d.csv` | No, label issue |
| Chow and single-break sup-F | Implemented and now documented accurately in current code. | `src/cqresearch/modeling/structural_breaks.py:1-10`; `reports/tables/2026-04-18/structural_breaks_summary.csv` | Yes if labeled narrowly |
| ETF flow regression | Exists and shows strong same-day association in v0.1. | `reports/tables/2026-04-18/etf_flow_regression.csv` | No until denominator and timing are fixed |
| Event studies | Exists with CARs and placebo benchmark. | `src/cqresearch/modeling/event_study.py`; `reports/tables/2026-04-18/event_studies.csv` | No |
| VAR/FEVD | Exists and has a compact 4-variable uncommitted version in 2026-04-19 outputs. | `src/cqresearch/modeling/var_fevd.py`; `reports/tables/2026-04-19/var_fevd_meta_compact.json` | Needs ordering/stability |
| Robustness suite | Exists as R1-R6 and catches real weaknesses. | `scripts/05_robustness.py`; `reports/tables/2026-04-18/robustness/` | Incomplete |
| Calendar policy work | Current code now reads `calendar_daily.ffill_limit` from config and exposes `business_day_mask`. | `src/cqresearch/data/calendars.py:60-68`; `src/cqresearch/data/calendars.py:132-153`; `config/calendars.yml` | Needs tests and market-holiday upgrade |
| ETF denominator fix in code | Current uncommitted code uses flow USD divided by prior-day market cap. | `src/cqresearch/features/panel.py:68-79`; `src/cqresearch/data/loaders.py:97-105`; `src/cqresearch/data/panel_builder.py:101-104` | Code direction good; outputs need review |

### 1.2 What Is Broken or Mislabeled

| Issue | Grade | Evidence | Why it matters |
|---|---:|---|---|
| v0.1 ETF intensity used flow/price, not flow/market cap | D in v0.1; B- in current uncommitted code | `Manager/Opus Manager/comprehensive_review.md:376`; `Manager/Gemini Manager/Project_Audit_Report.md:15`; old outputs in `reports/tables/2026-04-18/etf_flow_regression.csv`; current fix in `src/cqresearch/features/panel.py:68-79` | v0.1 economic magnitudes are not interpretable as flow intensity. |
| "Block partial R2" is not Shapley/Owen attribution | D for label accuracy | `src/cqresearch/modeling/rolling.py:1-6`; `src/cqresearch/modeling/rolling.py:74-89`; `Manager/Opus Manager/comprehensive_review.md:388-391` | The current decomposition is conditional variable-drop R2, which can mislead under correlated factors. |
| Full Bai-Perron is not implemented | B for current code label; C for specs/draft ecosystem | `src/cqresearch/modeling/structural_breaks.py:1-10`; `docs/specs/methods_spec.md`; `Manager/Codex Manager/codex_manager_review_2026-04-18.md:95` | Results must be called Chow plus single-break sup-F unless true multi-break code is added. |
| Event-study placebo p-values are benchmark-window p-values, not window-specific p-values | C | `scripts/02_run_analyses.py:183-195`; `Manager/Codex Manager/codex_manager_review_2026-04-18.md:99` | Attaching one `[-5,+5]` placebo p-value to all windows can be misread as window-specific inference. |
| VAR/FEVD Cholesky identification is underdeclared | C | `reports/tables/2026-04-18/var_fevd_meta.json`; `reports/tables/2026-04-19/var_fevd_meta_compact.json`; `Manager/Opus Manager/comprehensive_review.md:397` | FEVD shares depend on ordering; "BTC is upstream" language is too strong. |
| Current 2026-04-19 BTC OLS appears mechanically dominated by MVRV | D as headline design | `reports/tables/2026-04-19/static_ols_pre_post_etf.csv`; `src/cqresearch/features/panel.py:42-44` | BTC R2=0.921 and `btc_mvrv_d1` t=48.8238 indicate a near-dependent price-containing regressor, not a publishable factor result. |
| Calendar still lacks a true NYSE/market-holiday calendar | B- | `src/cqresearch/data/calendars.py:68-73`; `config/calendars.yml` | `business_day_mask` is weekday-only, so market holidays are still not handled as exchange closures. |
| Config is not yet the full operational analysis source | C | `config/factor_blocks.yml`; `scripts/02_run_analyses.py:50-60` | Regressor lists are still hardcoded in scripts, limiting reproducibility and auditability. |

### 1.3 What Is Missing

| Missing item | Required for v1.0? | Evidence that it is missing or incomplete | Recommendation |
|---|---:|---|---|
| Paper-specific market-day panel | Yes | Current code has weekday filtering, not a full NYSE/Farside trading calendar. `src/cqresearch/data/calendars.py:68-73` | Add market-day panel builder using observed Farside/NYSE dates; keep crypto-7 and weekly robustness. |
| Window-specific event placebo p-values | Yes | `scripts/02_run_analyses.py:187-195` computes `[-5,+5]` only. | Compute placebo p-values for each event window or label one benchmark clearly. |
| Shapley/Owen block attribution | Yes if block decomposition is a headline exhibit | Current rolling attribution is drop-one marginal R2. `src/cqresearch/modeling/rolling.py:1-6` | Implement block-level Shapley/Owen across economic blocks. |
| ETH-native block | Yes | `scripts/02_run_analyses.py:60` only uses `cme_eth_basis_close_d1`; `docs/specs/paper_1_native_metrics.yml` currently lists only BTC metrics. | Add ETH exchange netflow/reserve, staking, fees, active addresses or basis metrics with a pre-registered dictionary. |
| Native metric leakage screen | Yes | 2026-04-19 BTC R2=0.921 after adding `btc_mvrv_d1`. | Classify price-derived native metrics separately; use lagged or appendix diagnostics only. |
| Crypto-market event benchmark | Yes | Event studies use SPY as benchmark. `scripts/02_run_analyses.py:183-187`; TOTAL3 exists at `Data/Tradingview/Daily/CRYPTOCAP_TOTAL3__daily.csv`. | Add TOTAL3 or crypto-factor benchmark; keep SPY as TradFi robustness. |
| FEVD stability and ordering sensitivity | Yes | Current metadata only documents column order. `reports/tables/2026-04-19/var_fevd_meta_compact.json` | Add stability checks and alternate ordering table. |
| Literature review with verified citations | Yes | Draft has minimal literature infrastructure. `reports/drafts/paper_v0.1_2026-04-18.md`; `AGENTS.md` citation discipline | Add verified sources only; do not import prior-AI citations. |
| Publication-grade figures | Yes | 2026-04-18 figures are diagnostic quality. `reports/figures/2026-04-18/` | Redesign F02-F08 around core claims. |

### 1.4 What Is Overclaimed

| Draft language | Evidence path | Problem | Replacement |
|---|---|---|---|
| "The 2024 spot-ETF approval did not rewrite BTC's factor loadings at a single date." | `reports/drafts/paper_v0.1_2026-04-18.md:22` | Mostly defensible for BTC, but "rewrite" is rhetorical and the paper should foreground the 2021 break. | "The BTC ETF launch date is not the dominant estimated break in this specification." |
| "ETFs are now the single most statistically significant driver of post-2024 BTC returns." | `reports/drafts/paper_v0.1_2026-04-18.md:28` | "Driver" implies causal force; v0.1 is contemporaneous OLS with unit-defective flow scaling. | "ETF flow intensity is the strongest contemporaneous correlate of daily BTC returns in the post-2024 sample, before addressing simultaneity." |
| "patient-institutional-holder flows dampening routine volatility" | `reports/drafts/paper_v0.1_2026-04-18.md:150` | Mechanism is not identified. | "Post-split volatility is lower in this sample; the design does not identify the investor-type mechanism." |
| "ETH experienced the larger regime shift" | `reports/drafts/paper_v0.1_2026-04-18.md:166` | Static R2 increase is not enough to call a regime shift without stronger break evidence and robustness. | "ETH has a larger post-ETF increase in static explanatory power in this specification." |
| "cleanest 'BTC as banking hedge' episode" | `reports/drafts/paper_v0.1_2026-04-18.md:285` | SVB CAR is positive, but placebo p-value is 0.211 in v0.1; "cleanest" overstates. | "The SVB window is the largest positive BTC CAR in this event set, but placebo evidence is not strong." |
| "a clean overshoot-and-revert pattern" | `reports/drafts/paper_v0.1_2026-04-18.md:301` | R1 supports a descriptive pattern, but "clean" overstates given same-day endogeneity and flow timing. | "The lag specification is consistent with same-day overshoot and next-day partial reversal." |
| "Bai-Perron multiple breaks" | `reports/drafts/paper_v0.1_2026-04-18.md:354-355` | Current code does not implement Bai-Perron. | "A true multiple-break Bai-Perron implementation remains future work; current results are Chow plus single-break sup-F." |

---

## 2. Cross-Model Review Synthesis

### 2.1 Where All Three Reviewers Agree (Paper 1 Specific)

| Consensus finding | Opus | Gemini | Codex | My judgment |
|---|---|---|---|---|
| Paper 1 is the anchor project because it has the most code, data, and outputs. | `Manager/Opus Manager/comprehensive_review.md:164-177`; `:264-276` | `Manager/Gemini Manager/Project_Audit_Report.md:93-96` | `Manager/Codex Manager/codex_manager_review_2026-04-18.md:60`; `:71` | Correct. It should be Paper 1, but the framing must change. |
| The dominant break evidence points to 2021, not the BTC ETF launch. | `Manager/Opus Manager/comprehensive_review.md:370`; `:807-813` | Implied by critique of ETF overclaim and break-test integrity, `Manager/Gemini Manager/Project_Audit_Report.md:125-128` | `Manager/Codex Manager/codex_manager_review_2026-04-18.md:93` | Correct. This is the headline. |
| ETF flow intensity in v0.1 is unit-defective. | `Manager/Opus Manager/comprehensive_review.md:376`; `:755` | `Manager/Gemini Manager/Project_Audit_Report.md:15`; `:126` | `Manager/Codex Manager/codex_manager_review_2026-04-18.md:97` | Correct for 2026-04-18 outputs. Current code appears partly fixed, but old tables/draft must not be reused. |
| Block partial R2 is mislabeled if treated as Shapley/Owen. | `Manager/Opus Manager/comprehensive_review.md:388-391`; `:415` | `Manager/Gemini Manager/Project_Audit_Report.md:127` | `Manager/Codex Manager/codex_manager_review_2026-04-18.md:209` | Correct. Implement Shapley/Owen or downgrade label. |
| Current break code is not full Bai-Perron. | `Manager/Opus Manager/comprehensive_review.md:416`; `:767` | `Manager/Gemini Manager/Project_Audit_Report.md:176`; `:207` | `Manager/Codex Manager/codex_manager_review_2026-04-18.md:95` | Correct. Relabel unless true multi-break is added. |
| Calendar policy is central, not cosmetic. | `Manager/Opus Manager/comprehensive_review.md:424-457`; `:759` | `Manager/Gemini Manager/Project_Audit_Report.md:136-137`; `:206` | `Manager/Codex Manager/codex_manager_review_2026-04-18.md:107-116` | Correct. Headline regressions should be market-day. |
| Native CryptoQuant metrics are underused. | `Manager/Opus Manager/comprehensive_review.md:276`; `:507`; `:765` | `Manager/Gemini Manager/Project_Audit_Report.md:161` | `Manager/Codex Manager/codex_manager_review_2026-04-18.md:71`; `:146`; `:230` | Correct, but price-derived native metrics must not mechanically absorb returns. |
| v0.1 figures are diagnostic, not publication-grade. | `Manager/Opus Manager/comprehensive_review.md:403` | Implied by chart and method critiques, `Manager/Gemini Manager/Project_Audit_Report.md:127` | `Manager/Codex Manager/p0_execution_backlog.md:109` | Correct. Redesign is required. |

### 2.2 Where Reviewers Disagree (Paper 1 Specific)

| Issue | Opus position | Gemini position | Codex position | My judgment |
|---|---|---|---|---|
| True Bai-Perron vs relabel current sup-F | Opus lists true Bai-Perron as a required method and P0 fix. `Manager/Opus Manager/comprehensive_review.md:174`; `:767` | Gemini recommends either R `strucchange` or scaling down claims, defaulting to scaling down. `Manager/Gemini Manager/Project_Audit_Report.md:176`; `:214` | Codex allows correctly labeled Chow/single-break sup-F or true implementation. `Manager/Codex Manager/four_paper_protocols_v0.md:34` | Relabel for v1.0 main text. Add true multiple-break only as appendix if a tested implementation is cheap. Do not introduce an R bridge on the critical path. |
| Calendar master vs headline sample | Opus keeps crypto-7 master but recommends business-day headline for Paper 1. `Manager/Opus Manager/comprehensive_review.md:424-441` | Gemini says drop weekends for TradFi regressions. `Manager/Gemini Manager/Project_Audit_Report.md:136-137` | Codex recommends market-day headline plus crypto-7 and weekly robustness. `Manager/Codex Manager/codex_manager_review_2026-04-18.md:107-109` | Use crypto-7 as storage/join master, but market-day headline regressions. Weekly robustness is mandatory. |
| PCA within blocks | Opus asks for on-chain block and mentions true method upgrades, less explicit on PCA. | Gemini mandates PCA for highly correlated blocks. `Manager/Gemini Manager/Project_Audit_Report.md:161`; `:216` | Codex recommends selected metrics and metric dictionary, not kitchen-sink. `Manager/Codex Manager/codex_manager_review_2026-04-18.md:146` | Use PCA only when a block has more than three correlated candidate metrics, and fit without full-sample lookahead. Do not PCA small macro/institutional blocks. |
| How much native data belongs in headline OLS | Opus says add at least 3 CryptoQuant native metrics. `Manager/Opus Manager/comprehensive_review.md:276` | Gemini supports PCA for dense native blocks. | Codex asks whether native metrics enter baseline or robustness. `Manager/Codex Manager/codex_manager_review_2026-04-18.md:230` | Native metrics belong in a native-block model, but price-derived variables like contemporaneous MVRV should be excluded from the headline return OLS or lagged/residualized. |
| VAR size | Opus recommends a 4-variable VAR/FEVD. `Manager/Opus Manager/comprehensive_review.md:272`; `:397` | Gemini calls for econometric cleanup but is less prescriptive. | Codex flags FEVD identification and method labels. | Use a compact 5-variable baseline if stablecoin liquidity is part of the paper: `[VIXCLS_d1, spy_ret, stables_total_usd_ret, btc_ret, eth_ret]`. Keep 4-variable core and 8-variable appendix as robustness. |

### 2.3 Unique Contributions from Each Reviewer

**Opus unique contributions**
- Strong hostile-referee framing that the draft buries the lead: the 2021 break is more interesting than the ETF-date regression. Evidence: `Manager/Opus Manager/comprehensive_review.md:370`.
- Clear P0 list tying Paper 1 defects to implementation changes: ETF units, labels, calendar, native block, tests, figures. Evidence: `Manager/Opus Manager/comprehensive_review.md:755-771`.
- Explicit human-decision framing for market-cap denominator, 2021 headline, and business-day headline. Evidence: `Manager/Opus Manager/comprehensive_review.md:801-823`.

**Gemini unique contributions**
- Strongest warning that calendar interpolation can destroy break-test integrity. Evidence: `Manager/Gemini Manager/Project_Audit_Report.md:128`; `:136-137`.
- Most practical recommendation to avoid an R bridge unless true Bai-Perron is absolutely required. Evidence: `Manager/Gemini Manager/Project_Audit_Report.md:176`; `:214`.
- Strongest push for PCA within highly correlated native blocks. Evidence: `Manager/Gemini Manager/Project_Audit_Report.md:161`.

**Codex Manager unique contributions**
- Most explicit statement that event placebo p-values are `[-5,+5]` benchmark p-values attached to all windows. Evidence: `Manager/Codex Manager/codex_manager_review_2026-04-18.md:99`.
- Clearest paper-specific protocol: market-day headline, crypto-7 diagnostics, weekly robustness, correctly labeled break tests, selected native metrics. Evidence: `Manager/Codex Manager/four_paper_protocols_v0.md:20-44`.
- Strongest governance framing: current tests do not cover calendar semantics, flow units, event-window p-values, rolling attribution, or FEVD stability. Evidence: `Manager/Codex Manager/codex_manager_review_2026-04-18.md:44`; `:210`.

---

## 3. Hostile Referee Simulation

### 3.1 The Three Most Likely Referee Objections

**Objection 1: "Your title says ETF institutionalization, but your own break tests reject the ETF-break story for BTC."**

- Current draft response: partly addressed but underemphasized. The draft reports the BTC Chow null and 2021 sup-F peak, but then pivots to "ETFs are now the single most statistically significant driver." Evidence: `reports/drafts/paper_v0.1_2026-04-18.md:22-35`; `reports/run_summaries/03_run_analyses.md`.
- Required change: make the 2021 break the first result. The ETF result becomes a post-2024 flow-channel result, not the structural-break headline.
- Survival standard: Table 1 should show ETF-date Chow and single-break sup-F side by side. Figure 1 should annotate 2021 argmax and ETF date separately.

**Objection 2: "ETF flows are endogenous to returns, your intensity units are wrong in v0.1, and same-day flow coefficients are not causal."**

- Current draft response: inadequate. v0.1 uses economic language like "driver" and "flows dampening volatility." Evidence: `reports/drafts/paper_v0.1_2026-04-18.md:28`; `:150`; `:301`.
- Required change: use market-cap-scaled flow as baseline, add lag/T+1 sensitivity, and explicitly label same-day regressions as contemporaneous association.
- Survival standard: flow table must have same-day, lagged, T+1, weekly aggregation, and AUM/volume scaling robustness. Same-day coefficients can be interpreted as flow-return comovement, not price impact.

**Objection 3: "Your factor decomposition is not a valid block attribution and your native metrics create mechanical return explanation."**

- Current draft response: not addressed. Current rolling code is drop-one marginal R2, not Shapley/Owen. The 2026-04-19 run shows BTC R2=0.921 after adding `btc_mvrv_d1`, a clear danger sign. Evidence: `src/cqresearch/modeling/rolling.py:1-6`; `reports/tables/2026-04-19/static_ols_pre_post_etf.csv`.
- Required change: implement block Shapley/Owen or rename the exhibit. Exclude contemporaneous price-derived native metrics from headline return OLS.
- Survival standard: a reviewer should not be able to say the paper explains BTC returns with a transformed BTC price variable.

### 3.2 Strongest vs Weakest Claims in v0.1

| Rank | Claim | Defensibility | Evidence | Judgment |
|---:|---|---|---|---|
| 1 | The dominant single-break statistic occurs in 2021, not the BTC ETF date. | A- | `reports/run_summaries/03_run_analyses.md`; `reports/tables/2026-04-18/structural_breaks_summary.csv` | Strongest and most distinctive result. |
| 2 | BTC ETF-date Chow break is not significant in v0.1. | A | `reports/run_summaries/03_run_analyses.md` | Direct and uncomfortable; keep it. |
| 3 | ETH has larger post-ETF static explanatory power than pre-ETF in v0.1. | B | `reports/tables/2026-04-18/static_ols_pre_post_etf.csv` | Descriptive; do not call it causal regime change. |
| 4 | ETF flow intensity is a strong same-day post-2024 BTC return correlate. | B- after denominator fix; C in v0.1 | `reports/tables/2026-04-18/etf_flow_regression.csv`; current code `src/cqresearch/features/panel.py:68-79` | Interesting, but needs corrected scaling and timing. |
| 5 | ETF flows dampen routine volatility via patient holders. | F | `reports/drafts/paper_v0.1_2026-04-18.md:150` | Mechanism not identified. Remove. |
| 6 | BTC is upstream in the FEVD system. | D | `reports/tables/2026-04-18/fevd_10d.csv`; `reports/tables/2026-04-19/var_fevd_meta_compact.json` | Cholesky ordering makes this too fragile. |
| 7 | SVB is the cleanest BTC banking-hedge episode. | D | `reports/drafts/paper_v0.1_2026-04-18.md:285`; `reports/tables/2026-04-18/event_studies.csv` | CAR is positive; placebo p-value is not strong. |

### 3.3 Statistical Red Flags

| Red flag | Evidence | Interpretation | Required action |
|---|---|---|---|
| BTC post-ETF R2 barely rises in v0.1: 0.140 pre to 0.152 post | `reports/run_summaries/03_run_analyses.md` | Weak support for an ETF-date structural-change headline. | Reframe around 2021 break and factor composition. |
| ETH R2 rise is larger but still descriptive: 0.154 pre to 0.210 post | `reports/run_summaries/03_run_analyses.md` | Better ETH evidence, still not causal. | Treat as asset comparison. |
| BTC ETF-date Chow p=0.603 | `reports/tables/2026-04-18/structural_breaks_summary.csv` | Directly rejects BTC ETF-date break narrative. | Put in abstract/results. |
| ETH ETF-date Chow p=0.024 while sup-F argmax is 2021-05-12 | `reports/tables/2026-04-18/structural_breaks_summary.csv` | ETH has ETF-date parameter instability, but dominant break still predates ETF launch. | Avoid single-event story. |
| v0.1 ETF flow beta is strong but same-day and old-unit | `reports/tables/2026-04-18/etf_flow_regression.csv` | Statistical strength is real; economic magnitude is not reliable. | Recompute with market cap and lag/T+1. |
| R1 lagged-only flow is insignificant, but same-day plus lag shows negative lag | `reports/tables/2026-04-18/robustness/R1_lagged_etf_flow.csv`; `reports/tables/2026-04-19/robustness/R1_lagged_etf_flow.csv` | Descriptive overshoot/reversal, not causal price impact. | Report as simultaneity evidence. |
| 2026-04-19 BTC R2=0.921 after MVRV | `reports/run_summaries/03_run_analyses.md`; `reports/tables/2026-04-19/static_ols_pre_post_etf.csv` | Likely mechanical price-content leakage. | Remove contemporaneous MVRV from headline OLS; use lagged/residualized appendix. |

---

## 4. Research Design Evaluation

### 4.1 Research Question Assessment

**Grade: B- in v0.1; A- after reframing.**

The current question, "did BTC/ETH factor exposures evolve around ETF institutionalization," is viable. The draft loses the reader because the title and flow section imply 2024 ETF transformation, while the break tests point to 2021. Evidence: `reports/drafts/paper_v0.1_2026-04-18.md:22-35`; `reports/tables/2026-04-18/structural_breaks_summary.csv`.

The v1.0 question should be:

> Did BTC and ETH factor exposures change discretely at spot-ETF launches, or did ETF institutionalization add a flow-transmission layer to a longer factor-structure evolution that began around the 2020-2021 institutional cycle?

That question fits the actual numbers and is harder for a referee to dismiss.

### 4.2 Identification Strategy

**Grade: C if framed causally; B if framed descriptively.**

There is no clean causal identification in the current design. The methods are observational: HAC OLS, rolling regressions, Chow/sup-F, event studies, and VAR/FEVD. `AGENTS.md` explicitly forbids converting correlation, event-study, VAR, FEVD, rolling OLS, or break-test evidence into causal claims. The paper can credibly claim changes in associations, explanatory shares, and break diagnostics. It cannot claim that ETFs caused volatility dampening, rewrote factor loadings, or made BTC a banking hedge.

### 4.3 Factor Block Architecture

**Grade: B conceptually; C+ operationally.**

The five-block architecture is appropriate: macro/rates, institutional/risk assets, liquidity/DeFi/stablecoins, sentiment, native/on-chain. Evidence: `config/factor_blocks.yml`; `docs/specs/research_spec.md`. The operational problem is that current scripts still hardcode regressors rather than fully consuming the config. Evidence: `scripts/02_run_analyses.py:50-60`.

The native block is the largest opportunity and largest risk. Current uncommitted code adds BTC-native metrics, but the resulting BTC R2=0.921 indicates that contemporaneous `btc_mvrv_d1` is not safe as a headline regressor. Evidence: `reports/tables/2026-04-19/static_ols_pre_post_etf.csv`; `docs/specs/paper_1_native_metrics.yml`.

### 4.4 Sample Design

**Grade: B- in v0.1.**

v0.1 uses a 2020-01-01 to 2026-04-11 daily sample. That is adequate for static OLS and break diagnostics, but the post-ETH ETF period is short for richer post-ETF models. Evidence: `src/cqresearch/data/calendars.py:28-30`; `reports/run_summaries/02_build_master_panel.md`; `reports/run_summaries/03_run_analyses.md`.

The sample must be split into:
- Market-day headline regressions for macro/ETF models.
- Crypto-7 robustness for native crypto behavior.
- Weekly W-FRI robustness to reduce fill/timing noise.

### 4.5 Dependent Variables

**Grade: A- for daily log returns; B for current native-regressor interactions.**

BTC and ETH daily log returns are the correct dependent variables for Paper 1. Evidence: `src/cqresearch/features/returns.py`; `src/cqresearch/features/panel.py`. The problem is not the dependent variable. The problem is allowing contemporaneous price-derived native variables, especially MVRV changes, to enter the right-hand side of same-day return regressions.

---

## 5. Method-by-Method Assessment

### 5.1 Static OLS with HAC

**Implementation correctness: B. Label accuracy: B. Publication readiness: C+ in v0.1; C- in 2026-04-19 until native leakage is fixed.**

The OLS/HAC machinery is adequate for descriptive regressions. v0.1 produces plausible R2 levels: BTC 0.139 full, 0.140 pre, 0.152 post; ETH 0.165 full, 0.154 pre, 0.210 post. Evidence: `reports/run_summaries/03_run_analyses.md`; `reports/tables/2026-04-18/static_ols_pre_post_etf.csv`.

The v0.1 interpretation should be modest: static explanatory power is low to moderate, with little BTC pre/post change and a larger ETH increase. It does not support "ETF transformed BTC factor loadings."

The 2026-04-19 run is a separate red flag. BTC R2 jumps to 0.921 because `btc_mvrv_d1` dominates the regression. Evidence: `reports/run_summaries/03_run_analyses.md`; `reports/tables/2026-04-19/static_ols_pre_post_etf.csv`. This should not be accepted as an improvement. MVRV embeds market value and is mechanically close to price; use lagged MVRV or exclude from headline return OLS.

### 5.2 Rolling OLS and Block R2 Attribution

**Implementation correctness: B for rolling OLS. Label accuracy: D if called Shapley/block attribution. Publication readiness: C.**

Rolling OLS is implemented in `src/cqresearch/modeling/rolling.py`. The code explicitly says it is "drop-one marginal R2 (not Shapley/Owen)" and computes `(RSS_minus_j - RSS_full) / TSS` per regressor. Evidence: `src/cqresearch/modeling/rolling.py:1-6`; `src/cqresearch/modeling/rolling.py:74-89`.

The diagnostic is useful, but the v1.0 headline should not call it block partial R2 unless block-level Shapley/Owen is implemented. Because factor-block evolution is the paper's contribution, I recommend implementing block Shapley/Owen for the main figure. If that is not done, rename the figure "drop-one marginal R2 diagnostics" and move it to appendix.

### 5.3 Structural Break Tests (Chow + Sup-F)

**Implementation correctness: B+. Label accuracy: B in current code; C in older specs. Publication readiness: B if reframed.**

Current code accurately documents the method: Chow at known breakpoints and single unknown-break sup-F sweep, not full Bai-Perron. Evidence: `src/cqresearch/modeling/structural_breaks.py:1-10`; `src/cqresearch/modeling/structural_breaks.py:75-138`.

The results are important:
- BTC ETF-date Chow: F=0.813998, p=0.603274.
- BTC sup-F argmax: 2021-01-04.
- ETH ETF-date Chow: F=2.132529, p=0.024016.
- ETH sup-F argmax: 2021-05-12.

Evidence: `reports/run_summaries/03_run_analyses.md`; `reports/tables/2026-04-18/structural_breaks_summary.csv`.

This is the paper's central result. The 2021 break is a finding, not a bug. The missing piece is serial-dependence-robust inference for the sup-F null; current placebo shuffles `y`, which is a simple benchmark, not a final econometric inference procedure.

### 5.4 ETF Flow Intensity Regression

**Implementation correctness: D in v0.1 outputs; B- in current code. Label accuracy: C. Publication readiness: C until rerun and timing robustness.**

v0.1 ETF flow results are statistically strong but economically mis-scaled. The v0.1 table reports `btc_etf_intensity` beta=2.3315, t=8.6948, R2=0.2365, N=821. Evidence: `reports/tables/2026-04-18/etf_flow_regression.csv`. But manager reviews verified that v0.1 used flow divided by prior close, not market cap. Evidence: `Manager/Opus Manager/comprehensive_review.md:376`; `Manager/Codex Manager/codex_manager_review_2026-04-18.md:97`.

Current uncommitted code fixes the denominator to flow USD divided by prior-day USD market cap. Evidence: `src/cqresearch/features/panel.py:68-79`; `src/cqresearch/data/loaders.py:97-105`. The current 2026-04-19 table reports beta=46.1324, t=8.6723, R2=0.2365. Evidence: `reports/tables/2026-04-19/etf_flow_regression.csv`. The t-stat and R2 survive the scaling change, but the coefficient magnitude changes units. Interpret only as return per unit of market-cap-scaled daily net flow.

R1 remains the important endogeneity warning: in the contemporaneous-plus-lag model, same-day flow is positive and lagged flow is negative. In 2026-04-19, same-day beta=56.6204 and lag1 beta=-19.4384. Evidence: `reports/tables/2026-04-19/robustness/R1_lagged_etf_flow.csv`. This supports a descriptive overshoot/reversal pattern, not causal price impact.

### 5.5 VAR / FEVD

**Implementation correctness: C+. Label accuracy: C. Publication readiness: C-.**

v0.1 uses an 8-variable VAR with BIC lag 1 and 10-day FEVD. It reports Diebold-Yilmaz connectedness of 27.3 percent. Evidence: `reports/tables/2026-04-18/fevd_10d.csv`; `reports/tables/2026-04-18/var_fevd_meta.json`.

Current 2026-04-19 outputs add a compact 4-variable system with DY connectedness 35.27 percent and columns `['btc_ret', 'eth_ret', 'spy_ret', 'VIXCLS_d1']`. Evidence: `reports/tables/2026-04-19/var_fevd_meta_compact.json`. This is cleaner, but the ordering is still not economically ideal because BTC and ETH appear before macro/risk variables in the listed order. The metadata says Cholesky ordering equals column order, so ordering must be part of the research design.

Recommendation: headline FEVD should use external-to-crypto ordering: `[VIXCLS_d1, spy_ret, stables_total_usd_ret, btc_ret, eth_ret]`, plus ordering sensitivity. The current 4-variable output can remain a market-core appendix.

### 5.6 Event Studies

**Implementation correctness: C+. Label accuracy: B- if placebo benchmark is clearly labeled; C if read as window-specific inference. Publication readiness: C-.**

Current event studies use SPY as the market benchmark. Evidence: `scripts/02_run_analyses.py:183-187`; `src/cqresearch/modeling/event_study.py`. BTC ETF launch has `[-1,+1]` CAR=-0.0822, t=-2.305, but `[-5,+5]` placebo p=0.6131. ETH ETF `[+0,+30]` CAR=-0.2932, t=-1.7626, placebo p=0.9246. Evidence: `reports/run_summaries/03_run_analyses.md`; `reports/tables/2026-04-18/event_studies.csv`.

The "sell-the-news" finding is descriptive at best. The SVB "banking hedge" language is too strong because the placebo p-value is not strong. Evidence: `reports/drafts/paper_v0.1_2026-04-18.md:285`; `reports/tables/2026-04-18/event_studies.csv`.

Recommendation: use a crypto-market benchmark for headline events. `Data/Tradingview/Daily/CRYPTOCAP_TOTAL3__daily.csv` exists and should be loaded as a broad ex-BTC/ETH crypto proxy. Keep SPY as a TradFi benchmark robustness check.

### 5.7 Robustness Suite

| Check | Grade | What it addresses | What it shows | Missing piece |
|---|---:|---|---|---|
| R1 lagged ETF flow | B | Same-day endogeneity and lag structure | Same-day positive, lagged negative in combined model. Evidence: `reports/tables/2026-04-18/robustness/R1_lagged_etf_flow.csv`; `reports/tables/2026-04-19/robustness/R1_lagged_etf_flow.csv` | Add T+1 reporting-time sensitivity and weekly aggregation. |
| R2 no winsor post-ETF | B | Sensitivity to winsorization | Similar flow result in v0.1. Evidence: `reports/tables/2026-04-18/robustness/R2_no_winsor_post_etf.csv` | Main tables should disclose winsor policy and avoid full-sample lookahead. |
| R3 HAC lag sensitivity | B | Inference robustness to HAC lag | Flow t-stats remain large. Evidence: `reports/tables/2026-04-18/robustness/R3_hac_lag_sensitivity.csv` | Add automatic bandwidth robustness. |
| R4 post-2021 static OLS | C+ | Whether post-ETF differs after 2021 break | BTC R2 is similar pre-2024 and post-2024 in v0.1, weakening ETF-change claims. Evidence: `reports/tables/2026-04-18/robustness/R4_post2021_static_ols.csv` | Needs market-day version and native leakage screen. |
| R5 supF split | B- | Model behavior around 2021 break | Useful but not enough to prove a 2021 economic mechanism. Evidence: `reports/tables/2026-04-18/robustness/R5_supF_split.csv` | Add formal alternative break/date sensitivity. |
| R6 common support | C | Missingness/sample consistency | In v0.1 it largely duplicates the main sample. Evidence: `reports/tables/2026-04-18/robustness/R6_common_support.csv` | Add true business-day and weekly common-support checks. |

Missing robustness for v1.0:
- Market-day vs crypto-7 vs weekly.
- Flow denominator: market cap, AUM, and spot volume.
- ETF flow timing: same-day, lag1, T+1 shifted Farside, weekly.
- Event benchmark: crypto market, SPY, BTC-as-market for ETH.
- VAR stability and ordering sensitivity.
- Native metric leakage screen and lagged-native alternative.
- Rolling window sensitivity: 120/180/252 trading days.

---

## 6. Data and Panel Evaluation

### 6.1 Data Sources for Paper 1

**Grade: A- inventory; B- current Paper 1 utilization.**

Paper 1 can draw on:
- Farside ETF flows for BTC/ETH spot ETF net flows. Evidence: `Data/Farside ETF Data/`; `src/cqresearch/data/loaders.py`.
- TradingView prices and market proxies including SPY, QQQ, GLD, DXY, TOTAL3. Evidence: `Data/Tradingview/Daily/`; `Data/Tradingview/Daily/CRYPTOCAP_TOTAL3__daily.csv`.
- FRED macro/rates/risk proxies. Evidence: `Data/FRED/`; `config/factor_blocks.yml`.
- DefiLlama stablecoin and TVL proxies. Evidence: `Data/DefiLlama/`; `src/cqresearch/data/loaders.py`.
- CryptoQuant BTC/ETH market cap and native metrics. Evidence: `Data/CryptoQuant/BTC/`; `Data/CryptoQuant/ETH/`; `Data/MASTER_DATA.csv`.

The repository inventory is strong. The Paper 1 problem is not lack of data; it is disciplined selection, unit handling, and avoiding price-derived leakage.

### 6.2 Calendar and Fill Policy

**Grade: C in v0.1; B- in current uncommitted code; A target.**

Current code now reads the master forward-fill limit from `config/calendars.yml`. Evidence: `src/cqresearch/data/calendars.py:60-67`; `src/cqresearch/data/calendars.py:132-153`. It also adds a `business_day_mask`, but that mask is weekdays only and does not remove US market holidays. Evidence: `src/cqresearch/data/calendars.py:68-73`.

Specific recommendation for Paper 1:
- Store/join on crypto-7 master for coverage and diagnostics.
- Run headline mixed TradFi/ETF regressions on a market-day panel.
- Use observed Farside dates or an NYSE calendar, not just weekdays.
- Never forward-fill returns.
- Never forward-fill flows.
- Zero-fill ETF flows only inside active listing windows on confirmed non-trading/non-reporting days; do not fabricate pre-history.
- Use weekly W-FRI robustness.

### 6.3 Feature Construction Quality

**Grade: B- current; C in v0.1 outputs.**

Good:
- Price-like variables are transformed to log returns. Evidence: `src/cqresearch/features/panel.py:24-31`; `src/cqresearch/features/panel.py:56-59`.
- Rate/sentiment/native levels are differenced. Evidence: `src/cqresearch/features/panel.py:33-45`; `src/cqresearch/features/panel.py:60-63`.
- Current code scales ETF flows by prior-day USD market cap. Evidence: `src/cqresearch/features/panel.py:68-79`.

Problems:
- v0.1 outputs were generated before the market-cap denominator fix and must not be interpreted as market-cap intensity.
- `btc_mvrv_d1` as a same-day regressor is too close to the dependent variable. Evidence: `src/cqresearch/features/panel.py:42-44`; `reports/tables/2026-04-19/static_ols_pre_post_etf.csv`.
- ETH-native feature construction remains thin. Evidence: `scripts/02_run_analyses.py:60`; `docs/specs/paper_1_native_metrics.yml`.

### 6.4 Missing Variables / Factor Block Gaps

| Gap | Evidence | Recommendation |
|---|---|---|
| ETH native block is nearly absent | `scripts/02_run_analyses.py:60`; `Data/CryptoQuant/ETH/Exchange Flows/`; `Data/CryptoQuant/ETH/ETH 2.0/`; `Data/CryptoQuant/ETH/Fees And Revenue/` | Add ETH exchange netflow/reserve, staking rate or value staked, fees burnt/total fees, active addresses, CME ETH basis. |
| Crypto-market benchmark absent from event study | `scripts/02_run_analyses.py:183-187`; `Data/Tradingview/Daily/CRYPTOCAP_TOTAL3__daily.csv` | Add TOTAL3 return benchmark. |
| ETF AUM/volume scaling absent | `reports/tables/2026-04-18/etf_flow_regression.csv`; `src/cqresearch/features/panel.py` | Add robustness denominators if data exists; otherwise document missing. |
| Market-day panel absent | `src/cqresearch/data/calendars.py:68-73` | Add exchange calendar or observed Farside calendar. |
| Metric dictionary incomplete | `docs/specs/paper_1_native_metrics.yml` only lists BTC metrics | Expand dictionary with units, source, frequency, transform, leakage risk, role. |

---

## 7. Figures and Tables - Publication Readiness

### 7.1 Figure-by-Figure Assessment

| Figure | What it shows | Grade | Publication ready? | Specific issues | Priority |
|---|---|---:|---|---|---:|
| F01 cumulative returns | BTC/ETH and market proxies over time | C+ | No | Event labels and series overlap; title/footer too diagnostic. Evidence: `reports/figures/2026-04-18/F01_cumulative_returns.png` | Medium |
| F02 BTC rolling R2 | 180d rolling BTC explanatory power | B- | Needs work | Useful but event markers need labels and regime shading. Evidence: `reports/figures/2026-04-18/F02_btc_rolling_r2.png` | High |
| F02 ETH rolling R2 | 180d rolling ETH explanatory power | B- | Needs work | Same issue as BTC; compare BTC/ETH in one panel. Evidence: `reports/figures/2026-04-18/F02_eth_rolling_r2.png` | High |
| F03 BTC partial R2 stack | Variable/drop-one contributions | D+ | No | Misleading if read as additive Shapley/block attribution. Evidence: `reports/figures/2026-04-18/F03_btc_partial_r2_stack.png`; `src/cqresearch/modeling/rolling.py:1-6` | Highest |
| F04 ETH partial R2 stack | Variable/drop-one contributions | D+ | No | Same as BTC; native block too thin. Evidence: `reports/figures/2026-04-18/F04_eth_partial_r2_stack.png` | Highest |
| F05 BTC sup-F | BTC single-break sweep | B- | Needs work | Add argmax label, ETF date marker, critical/null band. Evidence: `reports/figures/2026-04-18/F05_sup_f_btc.png` | High |
| F06 ETH sup-F | ETH single-break sweep | B- | Needs work | Same as BTC; annotate 2021-05-12 and 2024-07-23. Evidence: `reports/figures/2026-04-18/F06_sup_f_eth.png` | High |
| F07 FEVD heatmap | 8-variable FEVD | C- | No | Axis labels crowded; ordering underdeclared; diagonal dominates. Evidence: `reports/figures/2026-04-18/F07_fevd_heatmap.png` | Medium |
| F08 event CARs | Event-study CARs | D | No | Annotation collisions; repeated `[-5,+5]` p-values for all windows. Evidence: `reports/figures/2026-04-18/F08_event_cars.png`; `scripts/02_run_analyses.py:187-195` | High |
| F09 coverage | Data coverage diagnostic | C | Appendix only | Useful for reproducibility, not main paper. Evidence: `reports/figures/2026-04-18/F09_coverage.png` | Low |
| F10 BTC TradFi correlation | Rolling correlations | B- | Needs work | Add event labels/regime shading and confidence context. Evidence: `reports/figures/2026-04-18/F10_btc_tradfi_corr.png` | Medium |

### 7.2 Table-by-Table Assessment

| Table | Grade | What it shows | Correctly computed? | Missing robustness / formatting issue |
|---|---:|---|---|---|
| `descriptive_stats.csv` | B | Summary stats for feature variables | Mostly yes | Needs market-day and weekly variants. |
| `static_ols_pre_post_etf.csv` | B in v0.1; D for 2026-04-19 BTC headline | Main HAC OLS | v0.1 plausible; 2026-04-19 polluted by MVRV | Add market-day table and leakage screen. |
| `block_r2_pre_post.csv` | C | Standalone/block R2 by period | Useful diagnostic | Rename if not Shapley; add native block after leakage screen. |
| `structural_breaks_summary.csv` | B+ | Chow and single-break sup-F | Yes for implemented methods | Add robust inference and clear labels. |
| `etf_flow_regression.csv` | C in v0.1; B- in 2026-04-19 | ETF flow-return association | v0.1 unit issue; current scaling better | Add timing, denominator, and weekly robustness. |
| `event_studies.csv` | C | CARs around selected events | Basic market model yes | Add crypto benchmark and window-specific p-values. |
| `fevd_10d.csv` | C | 8-var FEVD | Mechanically computed | Move to appendix; add stability/order checks. |
| `fevd_10d_compact.csv` | B- | Compact FEVD | Cleaner | Reorder external-to-crypto and add stablecoin liquidity. |
| `rolling_r2_*_median_by_year.csv` | B- | Yearly rolling R2 medians | Useful | Add confidence bands and window sensitivity. |
| `sup_f_series_*.csv` | B | Full sup-F series | Useful | Add critical/null thresholds and top break-date table. |
| `correlation_matrix_pre/post_etf.csv` | B- | Correlation shifts | Useful descriptive | Add significance/CI or keep appendix. |
| R1-R6 robustness | B-/C+ | Robustness diagnostics | Mostly useful | Add missing market-day, event, VAR, native leakage checks. |

### 7.3 Missing Figures and Tables for v1.0

Required new exhibits:
1. Table: source/metric dictionary for Paper 1, with units, frequency, transform, missingness, and leakage risk.
2. Table: headline market-day static OLS, without contemporaneous price-derived native metrics.
3. Table: break tests with ETF-date Chow, 2021 sup-F argmax, and robustness across crypto-7/market-day/weekly.
4. Figure: rolling block Shapley/Owen contributions by asset, with 2021 and ETF dates marked.
5. Figure: sup-F series with argmax, ETF launch, and null/critical thresholds.
6. Table: ETF flow timing and denominator robustness.
7. Table: event studies with crypto benchmark, SPY robustness, and window-specific placebo p-values.
8. Table/Figure: compact FEVD with declared ordering and order-sensitivity appendix.
9. Appendix table: native metric leakage screen, including MVRV exclusion/lagged robustness.

---

## 8. Draft Prose Assessment

### 8.1 Narrative Structure

**Grade: C+ in v0.1.**

The draft has the right ingredients but the wrong center of gravity. It starts by saying the BTC ETF launch did not create a single-date rewrite, then immediately shifts to ETF flows as the "single most statistically significant driver." Evidence: `reports/drafts/paper_v0.1_2026-04-18.md:22-35`. That makes the paper sound like it wants a 2024 ETF thesis even though the strongest break evidence says 2021.

The v1.0 narrative should be:
1. Crypto factor structure changed most sharply around 2021.
2. Spot ETFs did not create the dominant BTC break, but they added a measurable flow-return channel.
3. BTC and ETH differ: ETH has stronger ETF-date instability, but its dominant break still predates spot ETF launch.
4. Native/on-chain variables help interpret composition only if leakage-controlled.

### 8.2 Causal Language Audit

| Problematic text | Replacement |
|---|---|
| "ETFs are now the single most statistically significant driver of post-2024 BTC returns." `reports/drafts/paper_v0.1_2026-04-18.md:28` | "ETF flow intensity is the strongest contemporaneous correlate of daily BTC returns in the post-2024 specification." |
| "patient-institutional-holder flows dampening routine volatility" `reports/drafts/paper_v0.1_2026-04-18.md:150` | "Volatility is lower in the post-split sample; the design does not identify the investor-holder mechanism." |
| "ETH experienced the larger regime shift" `reports/drafts/paper_v0.1_2026-04-18.md:166` | "ETH shows the larger post-ETF increase in static explanatory power." |
| "cleanest 'BTC as banking hedge' episode" `reports/drafts/paper_v0.1_2026-04-18.md:285` | "The SVB window is the largest positive BTC CAR in this event set, but placebo evidence is not strong." |
| "clean overshoot-and-revert pattern" `reports/drafts/paper_v0.1_2026-04-18.md:301` | "The lag specification is consistent with same-day flow-return comovement followed by partial next-day reversal." |
| Any use of "caused", "rewrote", "driver", "dampened", "banking hedge" | Replace with "associated with", "correlate", "estimated break", "composition shift", or "consistent with." |

### 8.3 Method-Label Accuracy in Prose

| Method label issue | Evidence | Correct language |
|---|---|---|
| "Bai-Perron multiple breaks" | `reports/drafts/paper_v0.1_2026-04-18.md:354-355`; `src/cqresearch/modeling/structural_breaks.py:1-10` | "single-break sup-F sweep with Chow tests at pre-registered dates" |
| "Block partial R2" if implying Shapley | `src/cqresearch/modeling/rolling.py:1-6`; `reports/figures/2026-04-18/F03_btc_partial_r2_stack.png` | "drop-one marginal R2 diagnostic" unless Shapley/Owen is implemented |
| "ETF-flow intensity" for v0.1 tables | `reports/tables/2026-04-18/etf_flow_regression.csv`; `Manager/Opus Manager/comprehensive_review.md:376` | "flow-per-price proxy" for old outputs; "flow divided by prior-day market cap" for regenerated outputs |
| Event placebo p-values | `scripts/02_run_analyses.py:187-195` | "placebo p-value for the `[-5,+5]` benchmark window" unless recomputed by window |
| FEVD directional language | `reports/tables/2026-04-19/var_fevd_meta_compact.json` | "under the stated Cholesky ordering" |

### 8.4 Missing Sections for v1.0

Required:
- Literature review with verified citations only.
- Data construction and calendar policy section.
- Hypotheses or testable predictions stated descriptively, not causally.
- Metric dictionary / source-precedence appendix.
- Methods section that exactly matches implementation.
- Limitations section: observational design, same-day ETF flow endogeneity, market-calendar choices, native metric leakage, FEVD ordering.
- Replication appendix with code paths and run summaries.

---

## 9. Decisions Required

### Decision 1: ETF Flow Intensity Denominator

**The issue:** v0.1 generated outputs used ETF flow divided by price, not a scale with economic meaning.

**Agent positions:**
- Opus review said the denominator should be prior-day market cap. Evidence: `Manager/Opus Manager/comprehensive_review.md:376`; `:801-803`.
- Gemini said flow/price is numerically meaningless and should use market cap, circulating supply, or spot volume. Evidence: `Manager/Gemini Manager/Project_Audit_Report.md:126`.
- Codex said current ETF intensity is flow/close and must be rebuilt or relabeled. Evidence: `Manager/Codex Manager/codex_manager_review_2026-04-18.md:97`.

**My recommendation:** Use daily ETF net flow USD divided by prior-day USD market cap as the baseline. Add AUM and spot-volume denominators as robustness if data is available.

**Reasoning:** Market cap gives a dimensionless flow share and is interpretable across BTC/ETH and across time. Current uncommitted code now implements this direction. Evidence: `src/cqresearch/features/panel.py:68-79`; `src/cqresearch/data/loaders.py:97-115`.

**Impact if wrong:** The paper will report economically meaningless flow magnitudes and invite immediate rejection.

**Implementation:** Keep `src/cqresearch/features/panel.py:68-79`; add tests for the 1e6 Farside conversion and prior-day denominator; regenerate `reports/tables/<date>/etf_flow_regression.csv`; update draft language.

---

### Decision 2: Should the 2021 Structural Break Be the Headline Finding?

**The issue:** The strongest break evidence points to 2021, not 2024.

**Agent positions:**
- Opus said the draft buries the lead and the 2021 break should be the headline. Evidence: `Manager/Opus Manager/comprehensive_review.md:370`; `:807-813`.
- Gemini focused on method and calendar integrity; its critique undermines a simple ETF-date headline. Evidence: `Manager/Gemini Manager/Project_Audit_Report.md:125-128`.
- Codex verified BTC/ETH sup-F argmax dates in 2021. Evidence: `Manager/Codex Manager/codex_manager_review_2026-04-18.md:93`.

**My recommendation:** Yes. Make 2021 the headline structural result. Frame ETFs as an institutional flow channel that appears after the dominant factor-structure break.

**Reasoning:** BTC ETF-date Chow p=0.603, while BTC sup-F peaks 2021-01-04. ETH ETF-date Chow is stronger, but ETH sup-F still peaks 2021-05-12. Evidence: `reports/run_summaries/03_run_analyses.md`.

**Impact if wrong:** A referee will quote the paper's own break table against its title.

**Implementation:** Rewrite abstract, introduction, and first results section in `reports/drafts/paper_v1.0_*.md`; make break table and sup-F figure the first empirical result.

---

### Decision 3: Business-Day vs Calendar-Day Regression Sample

**The issue:** Mixed TradFi/crypto regressions on a crypto-7 calendar can create weekend artifacts.

**Agent positions:**
- Opus recommends business-day headline regressions and crypto-7 robustness. Evidence: `Manager/Opus Manager/comprehensive_review.md:441-455`.
- Gemini says do not force TradFi and crypto to a 24/7 calendar for regressions. Evidence: `Manager/Gemini Manager/Project_Audit_Report.md:136-137`.
- Codex recommends market-day headline, calendar-day diagnostics, weekly robustness. Evidence: `Manager/Codex Manager/codex_manager_review_2026-04-18.md:107-109`.

**My recommendation:** Headline Paper 1 regressions and event studies should use a market-day panel. Crypto-7 and W-FRI weekly are robustness panels.

**Reasoning:** The research question mixes ETF flows, FRED/TradingView variables, and crypto returns. The native clock for ETF flow is a US trading/reporting calendar.

**Impact if wrong:** Weekend flat-lines and fill rules can distort correlations, rolling R2, and break tests.

**Implementation:** Extend `src/cqresearch/data/calendars.py` beyond weekday-only `business_day_mask`; add paper-specific panel construction in `src/cqresearch/data/panel_builder.py`; rerun `scripts/02_run_analyses.py` and `scripts/05_robustness.py`.

---

### Decision 4: Method Label Strategy

**The issue:** The current code is single-break sup-F, not full Bai-Perron.

**Agent positions:**
- Opus says implement true Bai-Perron or fix labels. Evidence: `Manager/Opus Manager/comprehensive_review.md:416`; `:767`.
- Gemini recommends scaling down claims rather than adding a fragile R bridge by default. Evidence: `Manager/Gemini Manager/Project_Audit_Report.md:176`; `:214`.
- Codex says use correctly labeled Chow/single-break sup-F unless true multiple-break code exists. Evidence: `Manager/Codex Manager/four_paper_protocols_v0.md:34`.

**My recommendation:** For v1.0, relabel to Chow plus single-break sup-F. Do not put true Bai-Perron on the critical path. Add multiple-break detection only as an appendix if implemented and tested.

**Reasoning:** The single-break result is already strong and interpretable. Adding a second language/runtime increases reproducibility risk.

**Impact if wrong:** Calling current output Bai-Perron is a method overclaim; adding untested code creates replication risk.

**Implementation:** Keep `src/cqresearch/modeling/structural_breaks.py` language; remove "Bai-Perron" from results text; update `docs/specs/methods_spec.md` to distinguish implemented vs planned.

---

### Decision 5: Block Partial R2 Strategy

**The issue:** The paper needs block composition, but current rolling attribution is drop-one marginal R2.

**Agent positions:**
- Opus says implement Shapley or rename. Evidence: `Manager/Opus Manager/comprehensive_review.md:388-391`.
- Gemini says rolling R2 stack charts imply additive Shapley-like decomposition and are misleading. Evidence: `Manager/Gemini Manager/Project_Audit_Report.md:127`.
- Codex flags method labels as a P0 issue. Evidence: `Manager/Codex Manager/p0_execution_backlog.md:105-109`.

**My recommendation:** Implement block-level Shapley/Owen attribution for headline figures. Keep drop-one diagnostics in appendix.

**Reasoning:** The paper's novelty depends on factor-block composition. A non-additive variable-drop chart is not strong enough for the headline.

**Impact if wrong:** A referee can dismiss the central exhibit as a mislabeled diagnostic.

**Implementation:** Add block attribution code in `src/cqresearch/modeling/rolling.py` or a new `block_attribution.py`; update `scripts/02_run_analyses.py` and `scripts/03_make_figures.py`; rename old `pr2_*` outputs.

---

### Decision 6: VAR System Size

**The issue:** v0.1 8-variable VAR is too large and identification-light for a headline table.

**Agent positions:**
- Opus recommends a 4-variable VAR/FEVD minimum design and criticizes 8 variables. Evidence: `Manager/Opus Manager/comprehensive_review.md:272`; `:397`.
- Gemini calls for econometric cleanup and avoiding overbuilt methods. Evidence: `Manager/Gemini Manager/Project_Audit_Report.md:176`.
- Codex flags FEVD identification and stability diagnostics. Evidence: `Manager/Codex Manager/p0_execution_backlog.md:109`.

**My recommendation:** Use a compact 5-variable headline VAR: `[VIXCLS_d1, spy_ret, stables_total_usd_ret, btc_ret, eth_ret]`. Keep the current 4-variable market-core and 8-variable system as appendix robustness.

**Reasoning:** Stablecoin liquidity is part of the factor architecture and should be represented, but 8 variables overcomplicates FEVD interpretation.

**Impact if wrong:** The FEVD section will look like kitchen-sink connectedness with arbitrary ordering.

**Implementation:** Update `VAR_COLS_COMPACT` in `scripts/02_run_analyses.py`; update `reports/tables/<date>/var_fevd_meta_compact.json`; add stability/order checks in `src/cqresearch/modeling/var_fevd.py`.

---

### Decision 7: VAR Cholesky Ordering

**The issue:** FEVD depends on column order.

**Agent positions:**
- Opus says Cholesky ordering is undocumented. Evidence: `Manager/Opus Manager/comprehensive_review.md:397`; `:851`.
- Gemini did not specify an ordering but raised econometric quality concerns. Evidence: `Manager/Gemini Manager/Project_Audit_Report.md:176`.
- Codex says FEVD assumptions must be described. Evidence: `Manager/Codex Manager/p0_execution_backlog.md:109`.

**My recommendation:** Use external-to-crypto ordering: risk/macro first, equity second, liquidity third, BTC fourth, ETH fifth. Baseline: `[VIXCLS_d1, spy_ret, stables_total_usd_ret, btc_ret, eth_ret]`.

**Reasoning:** The paper should not let BTC mechanically appear upstream by ordering it first.

**Impact if wrong:** FEVD statements about "from BTC" versus "to BTC" will be arbitrary.

**Implementation:** Reorder columns in `scripts/02_run_analyses.py`; document ordering in `var_fevd_meta*.json` and methods prose; add alternative-order appendix.

---

### Decision 8: Event Study Benchmark

**The issue:** SPY-only benchmark is not enough for crypto events.

**Agent positions:**
- Opus calls SPY benchmark questionable. Evidence: `Manager/Opus Manager/comprehensive_review.md:397-403`.
- Gemini emphasizes calendar and benchmark integrity. Evidence: `Manager/Gemini Manager/Project_Audit_Report.md:136-137`.
- Codex flags event placebo labeling and method accuracy. Evidence: `Manager/Codex Manager/codex_manager_review_2026-04-18.md:99`.

**My recommendation:** Use a crypto-market benchmark as headline, preferably TOTAL3 returns from `Data/Tradingview/Daily/CRYPTOCAP_TOTAL3__daily.csv`, with SPY as robustness. For ETH events, include BTC return as an additional robustness benchmark.

**Reasoning:** Crypto event CARs should not be benchmarked only to US equities.

**Impact if wrong:** Event CARs may capture broad crypto beta rather than event abnormal returns.

**Implementation:** Add TOTAL3 loader in `src/cqresearch/data/loaders.py`; add return feature in `src/cqresearch/features/panel.py`; update `src/cqresearch/modeling/event_study.py` or `scripts/02_run_analyses.py` to support benchmark selection.

---

### Decision 9: Should an On-Chain / BTC-Native Factor Block Be Added?

**The issue:** Without native metrics, Paper 1 is too generic; with naive native metrics, it risks mechanical return explanation.

**Agent positions:**
- Opus says absence of on-chain block is a kill risk. Evidence: `Manager/Opus Manager/comprehensive_review.md:276`.
- Gemini recommends PCA for high-dimensional native metrics. Evidence: `Manager/Gemini Manager/Project_Audit_Report.md:161`.
- Codex says selected native metrics are likely main-regression categories but asks whether baseline or robustness. Evidence: `Manager/Codex Manager/codex_manager_review_2026-04-18.md:146`; `:230`.

**My recommendation:** Add a small pre-registered native block, but exclude contemporaneous price-derived metrics from headline return OLS. Use MVRV only lagged, residualized, or in appendix.

**Reasoning:** The 2026-04-19 BTC OLS shows that `btc_mvrv_d1` can dominate the dependent variable mechanically. Evidence: `reports/tables/2026-04-19/static_ols_pre_post_etf.csv`.

**Impact if wrong:** The paper becomes a tautological regression of BTC returns on BTC-price-derived variables.

**Implementation:** Update `docs/specs/paper_1_native_metrics.yml`; adjust `BTC_NATIVE` in `scripts/02_run_analyses.py`; add a leakage-risk field to the metric dictionary.

---

### Decision 10: Which CryptoQuant Native Metrics to Include?

**The issue:** Native metrics must be relevant, sparse, and non-tautological.

**Agent positions:**
- Opus wants at least three CryptoQuant native metrics. Evidence: `Manager/Opus Manager/comprehensive_review.md:276`; `:765`.
- Gemini wants PCA for dense correlated metrics. Evidence: `Manager/Gemini Manager/Project_Audit_Report.md:161`.
- Codex recommends selected BTC/ETH native metrics and a metric dictionary. Evidence: `Manager/Codex Manager/four_paper_protocols_v0.md:35`; `:44`.

**My recommendation:** For BTC headline, use exchange netflow, miner-to-exchange flow, and CME basis. Put MVRV in lagged/appendix only. For ETH, add exchange netflow/reserve, staking rate or total value staked, fees burnt or total fees, active addresses, and CME ETH basis; reduce with PCA only if more than three ETH-native variables pass coverage.

**Reasoning:** Flow, miner, staking, fees, and basis variables have economic content not mechanically equal to same-day spot return. MVRV is useful but unsafe contemporaneously.

**Impact if wrong:** Native block either adds no differentiation or contaminates the regression with price-derived variables.

**Implementation:** Extend `src/cqresearch/data/loaders.py` for ETH paths under `Data/CryptoQuant/ETH/`; update `src/cqresearch/data/panel_builder.py`; update `src/cqresearch/features/panel.py`; expand `docs/specs/paper_1_native_metrics.yml`.

---

### Decision 11: Winsorization

**The issue:** Winsorization can stabilize estimates but may hide event tails.

**Agent positions:**
- Opus emphasizes robustness and diagnostic status. Evidence: `Manager/Opus Manager/comprehensive_review.md:369-409`.
- Gemini flags overclaims and method integrity. Evidence: `Manager/Gemini Manager/Project_Audit_Report.md:125-128`.
- Codex requires conservative interpretation and robustness. Evidence: `AGENTS.md`; `Manager/Codex Manager/p0_execution_backlog.md`.

**My recommendation:** Use non-winsorized results as the main table with HAC and influence diagnostics. Keep 1/99 symmetric winsorization as robustness.

**Reasoning:** ETF and crisis windows are tail-relevant. Main results should not depend on a preprocessing choice that can mute the object of study.

**Impact if wrong:** Referees may argue the paper trims away institutionalization/event information.

**Implementation:** Update `scripts/02_run_analyses.py` main pipeline; keep `reports/tables/<date>/robustness/R2_no_winsor_post_etf.csv`; document policy in methods.

---

### Decision 12: HAC Lag Selection

**The issue:** Fixed HAC lag 5 is simple but arbitrary.

**Agent positions:**
- Opus asks for method rigor and tests. Evidence: `Manager/Opus Manager/comprehensive_review.md:755-771`.
- Gemini prefers robust econometric tooling. Evidence: `Manager/Gemini Manager/Project_Audit_Report.md:176`.
- Codex includes method-label and tests in P0. Evidence: `Manager/Codex Manager/p0_execution_backlog.md:105-114`.

**My recommendation:** Keep lag 5 as the daily headline for comparability, report lag 10/20/40 and automatic bandwidth as robustness. Weekly regressions should use lag 4.

**Reasoning:** v0.1 R3 shows the ETF flow t-stat is not fragile to longer fixed lags. Evidence: `reports/tables/2026-04-18/robustness/R3_hac_lag_sensitivity.csv`.

**Impact if wrong:** Inference can look cherry-picked.

**Implementation:** Extend `src/cqresearch/modeling/ols.py` or `scripts/05_robustness.py` to include automatic bandwidth; report in robustness grid.

---

### Decision 13: Python Version Pin

**The issue:** Project standard is Python 3.11+, but active interpreter observed here is Python 3.10.0.

**Agent positions:**
- Opus flags Python version alignment as P0. Evidence: `Manager/Opus Manager/comprehensive_review.md:755-771`; `:829-835`.
- Gemini emphasizes tooling consistency. Evidence: `Manager/Gemini Manager/Project_Audit_Report.md:175-178`.
- Codex says current packages are adequate if governance and tests are fixed. Evidence: `Manager/Codex Manager/codex_manager_review_2026-04-18.md:164`.

**My recommendation:** Use Python 3.11 and `uv.lock`. Do not accept regenerated outputs from Python 3.10 as final replication artifacts.

**Reasoning:** `pyproject.toml` requires `>=3.11` and Ruff/mypy target `py311`; local `python --version` returned 3.10.0. Evidence: `pyproject.toml`; shell environment check.

**Impact if wrong:** Reproducibility and dependency behavior can diverge.

**Implementation:** Run pipeline through `uv run` with Python 3.11; include environment metadata in run summaries.

---

### Decision 14: Should the Paper Implement PCA Within Blocks?

**The issue:** Native blocks can become high-dimensional and collinear.

**Agent positions:**
- Opus emphasizes selected on-chain metrics and method rigor. Evidence: `Manager/Opus Manager/comprehensive_review.md:276`.
- Gemini mandates PCA for blocks with many variables. Evidence: `Manager/Gemini Manager/Project_Audit_Report.md:161`; `:216`.
- Codex recommends selected metrics and factor-library discipline. Evidence: `Manager/Codex Manager/codex_manager_review_2026-04-18.md:146`.

**My recommendation:** Use PCA only for blocks with more than three correlated native metrics after leakage screening. Do not use full-sample PCA for headline results; fit on pre-period or expanding windows.

**Reasoning:** PCA can reduce dimensionality but can introduce lookahead and interpretability problems.

**Impact if wrong:** The paper may replace economic factor blocks with opaque full-sample factors.

**Implementation:** Change `config/factor_blocks.yml` PCA policy from full-sample to pre-period/expanding if used; add PCA loadings output table.

---

### Decision 15: Forward-Fill Limit for TradFi Variables

**The issue:** Fill policy can create artifacts in mixed-frequency regressions.

**Agent positions:**
- Opus recommends TradFi stock/rate ffill <=3 days and business-day headline. Evidence: `Manager/Opus Manager/comprehensive_review.md:424-457`.
- Gemini says never forward-fill traditional asset returns over weekends for crypto regressions. Evidence: `Manager/Gemini Manager/Project_Audit_Report.md:136-137`.
- Codex recommends no blind fills and zero-fill flows only on confirmed non-trading days. Evidence: `Manager/Codex Manager/codex_manager_review_2026-04-18.md:107-116`.

**My recommendation:** For headline market-day regressions, do not rely on weekend fills. For crypto-7 diagnostics, allow level/rate forward-fill up to 3 days, never returns, never flows except confirmed ETF non-trading days inside listing windows.

**Reasoning:** This preserves crypto-native daily diagnostics without contaminating mixed TradFi regressions.

**Impact if wrong:** Calendar artifacts can drive rolling R2 and break tests.

**Implementation:** Keep `get_master_ffill_limit()` reading `config/calendars.yml`; add exchange-calendar logic; expand `tests/unit/test_calendars.py` to cover returns, flows, rates, pre-history, and holiday gaps.

---

## 10. Execution Plan: v0.1 to v1.0

### Phase 1: Fix What's Broken (Days 1-3)

1. Freeze and review dirty worktree.
   - Files affected include `src/cqresearch/features/panel.py`, `src/cqresearch/data/loaders.py`, `src/cqresearch/data/panel_builder.py`, `src/cqresearch/data/calendars.py`, `scripts/02_run_analyses.py`, `scripts/05_robustness.py`, `reports/tables/2026-04-19/`, and `reports/drafts/paper_v1.0_2026-04-19.md`.
   - Acceptance: a short handoff identifies which 2026-04-19 changes are accepted, revised, or rejected.

2. Protect ETF intensity unit fix.
   - Implement tests around `src/cqresearch/features/panel.py:68-79`.
   - Acceptance: a fixture with known ETF flow in USD millions and market cap in USD returns expected dimensionless intensity.

3. Fix native metric leakage before using 2026-04-19 results.
   - Remove contemporaneous `btc_mvrv_d1` from headline BTC OLS in `scripts/02_run_analyses.py`.
   - Acceptance: BTC full-sample R2 returns to a plausible range; MVRV is reported only lagged/appendix.

4. Lock method labels.
   - Replace "Bai-Perron" results language with "single-break sup-F".
   - Replace "partial R2" headline labels with "drop-one marginal R2" until Shapley/Owen exists.
   - Acceptance: no draft/result text claims methods that code does not implement.

5. Calendar tests.
   - Extend `tests/unit/test_calendars.py`.
   - Acceptance: tests cover pre-history NaN preservation, stock/rate ffill limit, flow zero-fill windows, and weekday/market-day filtering.

### Phase 2: Add What's Missing (Days 4-7)

1. Build Paper 1 market-day and weekly panels.
   - Files: `src/cqresearch/data/calendars.py`, `src/cqresearch/data/panel_builder.py`, `scripts/02_run_analyses.py`.
   - Acceptance: output tables include calendar label `market_day`, `crypto7`, or `weekly`.

2. Add crypto-market benchmark.
   - Load `Data/Tradingview/Daily/CRYPTOCAP_TOTAL3__daily.csv`.
   - Files: `src/cqresearch/data/loaders.py`, `src/cqresearch/features/panel.py`, `scripts/02_run_analyses.py`.
   - Acceptance: event table reports TOTAL3 benchmark and SPY benchmark separately.

3. Add ETH-native metrics.
   - Candidate sources: `Data/CryptoQuant/ETH/Exchange Flows/`, `Data/CryptoQuant/ETH/ETH 2.0/`, `Data/CryptoQuant/ETH/Fees And Revenue/`, `Data/CryptoQuant/ETH/Addresses/`.
   - Acceptance: `docs/specs/paper_1_native_metrics.yml` covers BTC and ETH metrics with units and leakage risk.

4. Implement block-level Shapley/Owen attribution.
   - Files: `src/cqresearch/modeling/rolling.py` or new module; `scripts/03_make_figures.py`.
   - Acceptance: main figure uses additive block contributions; old drop-one outputs are appendix.

### Phase 3: Strengthen What's Weak (Days 8-12)

1. Regenerate OLS, rolling, breaks, ETF flow, event studies, FEVD, and robustness under corrected panels.
2. Add ETF flow denominator robustness: market cap baseline, AUM if available, spot volume if available.
3. Add ETF flow timing robustness: same day, lag1, T+1 shifted Farside, weekly.
4. Add event window-specific placebo p-values.
5. Add compact 5-variable FEVD with declared external-to-crypto Cholesky ordering and order sensitivity.
6. Redesign F02-F08 as publication figures.
7. Rewrite v1.0 draft around the 2021 break plus ETF-era flow channel.

### Phase 4: Red-Team and Submit (Days 13-16)

1. Replicate from clean Python 3.11 environment using `uv run`.
2. Run tests for calendars, ETF intensity, event windows, rolling attribution, and structural breaks.
3. Perform citation audit with only verified durable sources.
4. Have a hostile methods reviewer focus on:
   - 2021 break robustness.
   - ETF flow timing/endogeneity.
   - Native metric leakage.
   - Shapley/Owen attribution.
   - FEVD ordering.
5. Finalize draft only after overclaim audit passes.

---

## 11. Risk Register

| Risk | Probability | Impact | Mitigation | Owner |
|---|---:|---:|---|---|
| Calendar fill artifacts change headline R2 | High | High | Run market-day headline and crypto-7/weekly robustness | Data lead |
| 2021 break is the real story, not ETFs | Confirmed | High | Reframe paper around 2021 factor repricing plus ETF flow channel | Research lead |
| Bai-Perron not implemented | Confirmed | Medium | Relabel to Chow plus single-break sup-F; optional appendix only if implemented | Methods lead |
| v0.1 ETF flow intensity units wrong | Confirmed for 2026-04-18 outputs | High | Use market-cap denominator and regenerate tables | Features lead |
| Same-day ETF flows endogenous | High | High | Use lag/T+1/weekly robustness and non-causal language | Research lead |
| Native MVRV mechanically explains BTC returns | Confirmed in 2026-04-19 outputs | High | Exclude contemporaneous MVRV from headline OLS; use lagged/appendix | Methods lead |
| Block attribution mislabeled | Confirmed | High | Implement Shapley/Owen or rename as drop-one diagnostic | Methods lead |
| Event-study benchmark too narrow | High | Medium | Add TOTAL3 crypto benchmark and SPY robustness | Research lead |
| FEVD ordering drives conclusions | High | Medium | Declare external-to-crypto ordering and report sensitivity | Methods lead |
| Python environment mismatch | Confirmed locally | Medium | Use Python 3.11 and `uv.lock` for final replication | Engineering lead |
| Figures remain diagnostic | High | Medium | Redesign core figures after corrected tables | Visualization lead |
| Prior-AI citations leak into draft | Medium | High | Verify every external citation through durable source | Citation reviewer |

---

## 12. Quality Gate

### Inputs read

Core governance and specs:
- `AGENTS.md`
- `Data/MASTER_DATA.md`
- `Data/MASTER_DATA.csv`
- `config/factor_blocks.yml`
- `config/events.yml`
- `config/calendars.yml`
- `config/chain_taxonomy.yml`
- `CODEX/current_status_analysis.md`
- `CODEX/data_analysis.md`
- `docs/specs/research_spec.md`
- `docs/specs/methods_spec.md`
- `docs/specs/data_spec.md`
- `docs/specs/paper_1_native_metrics.yml`

Prior manager reviews:
- `Manager/Opus Manager/comprehensive_review.md`
- `Manager/Gemini Manager/Project_Audit_Report.md`
- `Manager/Codex Manager/codex_manager_review_2026-04-18.md`
- `Manager/Codex Manager/four_paper_protocols_v0.md`
- `Manager/Codex Manager/data_calendar_metric_strategy_v0.md`
- `Manager/Codex Manager/p0_execution_backlog.md`
- `Manager/Codex Manager/multi_agent_workflow_and_quality_gates_v0.md`

Paper 1 artifacts:
- `reports/drafts/paper_v0.1_2026-04-18.md`
- `reports/drafts/paper_v1.0_2026-04-19.md` existence noted as untracked current worktree artifact
- `reports/run_summaries/01_inspect_core_files.md`
- `reports/run_summaries/02_build_master_panel.md`
- `reports/run_summaries/03_run_analyses.md`
- `reports/tables/2026-04-18/`
- `reports/tables/2026-04-18/robustness/`
- `reports/tables/2026-04-19/`
- `reports/tables/2026-04-19/robustness/`
- `reports/figures/2026-04-18/`

Code:
- `src/cqresearch/features/panel.py`
- `src/cqresearch/features/returns.py`
- `src/cqresearch/modeling/ols.py`
- `src/cqresearch/modeling/rolling.py`
- `src/cqresearch/modeling/structural_breaks.py`
- `src/cqresearch/modeling/var_fevd.py`
- `src/cqresearch/modeling/event_study.py`
- `src/cqresearch/data/calendars.py`
- `src/cqresearch/data/panel_builder.py`
- `src/cqresearch/data/loaders.py`
- `scripts/02_run_analyses.py`
- `scripts/03_make_figures.py`
- `scripts/04_descriptives_and_summaries.py`
- `scripts/05_robustness.py`
- `pyproject.toml`

### Outputs written

- `Manager/Paper 1/Paper 1 CODEX.md`

### Key findings

1. **Verified:** v0.1 does not support a BTC ETF-date structural-break headline. BTC ETF-date Chow p=0.603, while the single-break sup-F argmax is 2021-01-04. Evidence: `reports/run_summaries/03_run_analyses.md`.
2. **Verified:** ETH has stronger ETF-date evidence than BTC, but its dominant single-break sup-F argmax is still 2021-05-12. Evidence: `reports/tables/2026-04-18/structural_breaks_summary.csv`.
3. **Verified:** v0.1 ETF flow regression is statistically strong but same-day, endogenous, and generated from old flow/price scaling. Evidence: `reports/tables/2026-04-18/etf_flow_regression.csv`; `Manager/Opus Manager/comprehensive_review.md:376`.
4. **Verified:** current uncommitted code fixes ETF flow scaling direction, but the 2026-04-19 BTC OLS introduces a new native-metric leakage risk through `btc_mvrv_d1`. Evidence: `src/cqresearch/features/panel.py:68-79`; `reports/tables/2026-04-19/static_ols_pre_post_etf.csv`.
5. **Verified:** current method labels must remain conservative: Chow plus single-break sup-F, drop-one marginal R2 unless Shapley/Owen is implemented, FEVD under stated Cholesky ordering. Evidence: `src/cqresearch/modeling/structural_breaks.py:1-10`; `src/cqresearch/modeling/rolling.py:1-6`; `reports/tables/2026-04-19/var_fevd_meta_compact.json`.

### Decisions made by this agent

- D1: Use market-cap-scaled ETF flow as baseline; AUM/volume robustness.
- D2: Make 2021 break the headline structural result.
- D3: Use market-day headline regressions; crypto-7 and weekly robustness.
- D4: Relabel to Chow plus single-break sup-F; no Bai-Perron claim unless implemented.
- D5: Implement block Shapley/Owen for headline attribution.
- D6: Use compact 5-variable headline VAR; keep 4-var and 8-var as robustness.
- D7: Use external-to-crypto Cholesky ordering and report sensitivity.
- D8: Use crypto-market benchmark for event studies; SPY as robustness.
- D9: Add native block, but leakage-screen it.
- D10: Use BTC exchange netflow, miner-to-exchange flow, CME basis; MVRV only lagged/appendix; add parallel ETH native metrics.
- D11: Non-winsorized main results; 1/99 winsorization robustness.
- D12: HAC lag 5 headline; lag and automatic-bandwidth robustness.
- D13: Final replication must use Python 3.11 and `uv.lock`.
- D14: PCA only for dense native blocks, no full-sample lookahead.
- D15: No return/flow forward-fill; market-day headline avoids weekend fill artifacts.

### Confidence

**88%.** Confidence is high on v0.1 method/result assessment because the run summaries, generated tables, draft, source code, and three manager reviews converge. Confidence is lower on the 2026-04-19 uncommitted outputs because they appear to be active work-in-progress and have not been fully red-teamed.

### What I could not verify

- I did not verify external literature citations; none should be accepted until checked against durable sources.
- I did not visually re-review the new `reports/figures/2026-04-19/` artifacts; figure readiness judgments are based on the requested v0.1 figure set and prior visual inspection of `reports/figures/2026-04-18/`.
- I did not run a full clean replication under Python 3.11.
- I did not verify whether `reports/drafts/paper_v1.0_2026-04-19.md` already incorporates all corrections; it exists as an untracked worktree artifact and should be audited separately before use.

### Next agent

**Next agent:** Paper 1 implementation builder with methods-review discipline. The immediate task is not further strategy; it is to reconcile the dirty worktree, remove native metric leakage, regenerate corrected market-day outputs, implement or relabel block attribution, and rewrite the draft around the 2021 break plus ETF-era flow channel.
