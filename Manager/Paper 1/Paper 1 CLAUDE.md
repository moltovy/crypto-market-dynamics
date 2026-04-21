# Paper 1: BTC/ETH Factor-Exposure Evolution — Deep-Dive Analysis

**Agent:** Claude Opus 4.6 (Thinking)
**Date:** 2026-04-19
**Stance:** Senior quantitative finance research lead, publication-focused
**Goal:** Transform v0.1 diagnostic draft into defensible v1.0 submission

---

## 1. Current State Assessment

### 1.1 What Exists and Works

| Component | Status | Evidence Path | Publication-Ready? | Grade |
|---|---|---|---|---|
| Research question | Exists, partially articulated | `reports/drafts/paper_v0.1_2026-04-18.md` §1 | No — buries the lead | B- |
| Master panel | Real, 2,293 × 58 | `reports/panels/master_daily.parquet` | Adequate for v0.1 | B+ |
| Static OLS (HAC) | Real, correct implementation | `src/cqresearch/modeling/ols.py`; `reports/tables/2026-04-18/static_ols_pre_post_etf.csv` | Needs method clarification | B+ |
| Rolling OLS + partial R² | Real, 180-day window | `src/cqresearch/modeling/rolling.py`; `reports/tables/2026-04-18/rolling_ols_*_180d.csv` | Label inaccuracy | B |
| Chow test at ETF date | Real, correct | `src/cqresearch/modeling/structural_breaks.py` L37-64 | Yes (honest null result) | A- |
| Sup-F sweep | Real, single-break | `src/cqresearch/modeling/structural_breaks.py` L75-115 | Label must say sup-F not Bai-Perron | B |
| Placebo permutation | Real, y-shuffle | `src/cqresearch/modeling/structural_breaks.py` L118-135 | Adequate for v0.1 | B |
| ETF flow regression | Real, but unit problem | `src/cqresearch/features/panel.py` L63-71; `reports/tables/2026-04-18/etf_flow_regression.csv` | No — denominator wrong | C |
| VAR/FEVD | Real, 8-variable | `src/cqresearch/modeling/var_fevd.py`; `reports/tables/2026-04-18/fevd_10d.csv` | Overparameterized, ordering undocumented | C+ |
| Event studies | Real, market-model CARs | `src/cqresearch/modeling/event_study.py`; `reports/tables/2026-04-18/event_studies.csv` | Benchmark questionable; placebo labeling issue | B- |
| Robustness R1-R6 | Real, automated | `scripts/05_robustness.py`; `reports/tables/2026-04-18/robustness/` | Useful but incomplete | B |
| Figures (11 total) | Real, diagnostic quality | `reports/figures/2026-04-18/F01-F10` | Not publication-ready | C |
| Draft v0.1 | Real, 390 lines, all numbers cited | `reports/drafts/paper_v0.1_2026-04-18.md` | Overclaims in several places | B- |
| Reproducibility | Excellent — deterministic pipeline | `scripts/run_full_pipeline.py`, seed=42 | A- |
| Citation discipline (internal) | Every table cited by CSV path | Draft throughout | A |
| Tests | Thin — 9 smoke tests | `tests/unit/` | D |
| Config-driven specs | Real, 4 YAML files | `config/factor_blocks.yml`, `events.yml`, `calendars.yml`, `chain_taxonomy.yml` | B+ |

### 1.2 What Is Broken or Mislabeled

**B1. ETF Flow Intensity Denominator (CONFIRMED DEFECT)**
- **File:** `src/cqresearch/features/panel.py` lines 63-71
- **Bug:** `btc_etf_intensity = panel["btc_etf_total"] / panel["btc_close"].shift(1)` divides flow by prior-day *price*, not market cap.
- **Impact:** The regressor is "dollars of flow per dollar of BTC price" — a dimensionally awkward quantity that scales with inverse price level. A $100M flow when BTC=$50K and $100M when BTC=$100K produce different intensity values despite identical economic significance relative to the market.
- **The docstring at line 8-9 says "Scale ETF flows by prior-day BTC (resp. ETH) market cap"** — this is factually wrong about what the code does. The comment at lines 64-67 acknowledges using close as a "scaling proxy."

**B2. Calendar/Fill Policy Conflict (CONFIRMED DEFECT)**
- **File:** `config/calendars.yml` line 13 says `ffill_limit: 0` for `calendar_daily`
- **File:** `src/cqresearch/data/calendars.py` line 65 has `ffill_limit_days: int = 4` as the default parameter
- **File:** Draft §2.2 says "forward-fill up to 4 days"
- **Impact:** Config and code disagree. The code's default (4 days) is what actually runs. The config's 0 would produce far more NaNs. Neither document governs the other programmatically — the config is not read by the code.

**B3. Method Label Inflation in Specs (CONFIRMED DEFECT)**
- **File:** `docs/specs/methods_spec.md` §5 describes "Bai-Perron multiple-break search" with "supF, UDmax, WDmax, break locations and 95% CIs"
- **Reality:** `src/cqresearch/modeling/structural_breaks.py` implements single-break sup-F sweep only. No dynamic programming, no UDmax/WDmax, no confidence intervals.
- **File:** `docs/specs/methods_spec.md` §2 says "partial R² per block (sequential + Shapley)"
- **Reality:** `src/cqresearch/modeling/rolling.py` lines 76-85 implement variable-drop partial R² (drop one regressor, refit, measure RSS increase). This is NOT Shapley decomposition, which requires evaluating all 2^k subsets.

**B4. Event-Study Placebo P-value Labeling (CONFIRMED DEFECT)**
- **File:** `scripts/02_run_analyses.py` lines 160-167 computes `placebo_cars()` with `window=(-5,5)` and assigns the resulting p-value to ALL CAR windows via `df["placebo_p_m5_p5"] = p5`
- **Impact:** The `[-1,+1]`, `[0,+5]`, and `[0,+30]` windows all show the placebo p-value computed on `[-5,+5]` only. This is misleading unless explicitly disclosed. The draft does disclose this partially ("Placebo p-values from 200 random date draws") but does not clarify the window mismatch.

**B5. VAR Cholesky Ordering Undocumented (CONFIRMED)**
- **File:** `src/cqresearch/modeling/var_fevd.py` — uses statsmodels default Cholesky ordering, which is the column order of the input DataFrame
- **File:** `scripts/02_run_analyses.py` line 132-133 sets column order as `["btc_ret", "eth_ret", "spy_ret", "gld_ret", "DGS10_d1", "VIXCLS_d1", "stables_total_usd_ret", "defi_tvl_usd_ret"]`
- **Impact:** BTC is first — meaning BTC contemporaneous shocks affect all others but is not contemporaneously affected by any. This is a strong identifying assumption that is nowhere discussed or justified. `docs/specs/methods_spec.md` §8 says ordering is "pending."

### 1.3 What Is Missing

| Missing Component | Importance for v1.0 | Effort |
|---|---|---|
| **On-chain factor block** — CryptoQuant BTC/ETH native metrics (exchange net flow, SOPR, MVRV, miner-to-exchange) | Critical differentiator from generic ETF studies | 2-3 days |
| **Business-day regression panel** — dropping weekends from headline regressions | Critical for calendar-artifact defense | 1 day |
| **Literature review** — positioning against existing ETF/crypto papers | Required for submission | 3-4 days |
| **Formal hypothesis statements** (H1-H3) | Standard for empirical finance | 1 day |
| **Limitations section** | Required for submission | 0.5 day |
| **Block-level nested F-tests** (macro-only vs institutional-only) | Needed for block comparison claims | 1 day |
| **Weekly robustness** (resample to W-FRI) | Addresses mixed-frequency concern | 1 day |
| **Window sensitivity** for rolling OLS (60, 120, 252 days) | `docs/specs/methods_spec.md` §3 specifies three windows; only 180-day implemented | 1 day |
| **True multiple-break detection** (Bai-Perron or `ruptures`) | Strengthens structural-break finding | 2 days |
| **Corrected ETF intensity** (market-cap denominator) | Fixes the unit problem | 0.5 day |
| **Publication-quality figures** | All 11 are diagnostic grade | 3-4 days |
| **External citations** (verified literature) | Zero external citations currently | 3-4 days |

### 1.4 What Is Overclaimed

| Draft Location | Overclaimed Text | Problem | Corrected Language |
|---|---|---|---|
| §1, point 2 | "ETFs are now the single most significant driver of daily BTC returns" | Contemporaneous regression, not causal identification. "Driver" implies causality. | "ETF flow intensity is the strongest contemporaneous correlate of daily BTC returns in the post-2024 sample" |
| §4.1, last sentence | "consistent with patient-institutional-holder flows dampening routine volatility without removing regime shocks" | Mechanistic causal claim with no supporting identification | "This pattern is observationally consistent with a maturing asset class, though we cannot attribute the volatility decline specifically to institutional holder behavior" |
| §4.4, last line | "the single tightest daily relationship" | Acceptable as written; not causal, just descriptive of fit. | Keep |
| §4.3, "Interpretation" | "The dominant structural inflection in the crypto-era factor profile was 2021, not 2024" | Well stated, honest. This is a strength. | Keep |
| §4.7, "BTC as banking hedge" | "the cleanest 'BTC as banking hedge' episode" | Over-interprets a single 5-day window. Placebo p=0.21 means it's not significant at 5%. | "suggestive of a flight-to-crypto response during banking stress, though the placebo p-value of 0.21 does not reject the null at conventional levels" |
| §2.3, ETF flow intensity | "scaling raw USD-M flows by prior-day BTC price so the regressor is stationary" | Mischaracterizes the scaling as economically motivated stationarity transformation; the real issue is the wrong denominator | "scaling raw USD-M flows by prior-day BTC close price. This produces a flow-per-unit-price regressor. A more standard approach would scale by market capitalization; see Limitations" |

---

## 2. Cross-Model Review Synthesis

### 2.1 Where All Three Reviewers Agree (Paper 1 Specific)

| # | Consensus Finding | Opus Citation | Gemini Citation | Codex Citation |
|---|---|---|---|---|
| C1 | **ETF flow intensity uses price not market cap — must fix** | §8 "Variable construction — ETF flow intensity: C" | §8 "Spurious Flow Intensity" | §8 "Verified defect" |
| C2 | **Method labels overclaim** (sup-F≠Bai-Perron, variable-drop≠Shapley) | §8 "Block partial R² claims: D+" | §8 "$R^2$ Stack Charts" | §8 "Verified defect" re Bai-Perron |
| C3 | **Calendar/fill policy conflicts between config and code** | §8 "Calendar handling: B-" | §9 "Weekend filling constraint" | §9 "Known conflict to resolve" |
| C4 | **Figures are diagnostic, not publication quality** | §8 "Figure quality: C" | §13 "Ditch basic matplotlib" | P0.10 "Visual QA Before Publication Figures" |
| C5 | **The 2021 structural break is the real finding, not 2024 ETF** | §8 "buries the lead" | §5 Direction 1 "ETF date may not be dominant break" | §8 "2021-01-04... not the ETF launch" |
| C6 | **Paper overclaims causality from contemporaneous regressions** | §8 "ETFs are the single most significant driver" | §8 "Volatility Dampening overclaim" | §8 "causal or mechanism language" |
| C7 | **VAR is overparameterized (8 variables for sample size)** | §8 "too many variables" | Not explicitly flagged (Gemini focused on 4-var) | §8 "current 8-variable" implicitly |
| C8 | **Tests are grossly inadequate** | §3 "Thin. 3 test files" | §3 "Sub-par" | §3 "Thin" |
| C9 | **Business-day regressions should be the headline** | §9 "Business-day for headline" | §9 "Do not force TRADFI and CRYPTO to a 24/7 calendar" | §9 "market-day panel for headline" |
| C10 | **On-chain CryptoQuant metrics should enter the model** | §6 Paper 1 "on-chain block needs variable selection" | §5 Direction 1 "CryptoQuant native data" | §6 Paper 1 protocol "selected BTC/ETH native CryptoQuant blocks" |

### 2.2 Where Reviewers Disagree (Paper 1 Specific)

**Disagreement 1: How to fix the structural break method**

| Agent | Position |
|---|---|
| Opus | Add `ruptures` (Python) for true Bai-Perron. Low implementation risk. |
| Gemini | Consider `rpy2` + R `strucchange`. Default: scale down the claim to Chow + sup-F. |
| Codex | "Relabel or implement." Either fix is acceptable. |

**My judgment:** Use `ruptures` in Python. R bridges (`rpy2`) add dependency complexity and cross-platform reproducibility issues for marginal benefit. `ruptures` provides kernel-change-point detection with BIC/penalty selection that is functionally equivalent to Bai-Perron for our case. If `ruptures` results differ from current sup-F, report both. Relabeling alone is insufficient for v1.0 — a true multiple-break search is needed to determine whether 2021+2022+2024 all jointly matter.

**Disagreement 2: Forward-fill limit for TradFi variables**

| Agent | Position |
|---|---|
| Opus | ffill ≤3 days (covers weekends + one Monday holiday) |
| Gemini | Never forward-fill traditional asset *returns* over a weekend |
| Codex | "No blind forward-fill of returns, flows, fees, addresses, volumes, or exchange flows" |

**My judgment:** All three are converging but Gemini and Codex are more precise. The correct policy is: (a) forward-fill *prices/levels* up to 3 days, then compute *returns* from the filled levels — this produces zero returns on weekends, which is correct for levels but problematic for return regressions; (b) therefore, run headline regressions on business-day-only observations where this issue vanishes. The current 4-day default in code should be changed to 3 to match Opus's recommendation, but the real fix is business-day regression panels.

**Disagreement 3: VAR system size**

| Agent | Position |
|---|---|
| Opus | 4-variable compact (BTC-ret, ETF-flow, stablecoin-growth, VIX) recommended |
| Gemini | 4-variable VAR explicitly (Paper 2 protocol) |
| Codex | Didn't explicitly recommend reducing |

**My judgment:** Use a 4-variable compact VAR for the headline: `[btc_ret, spy_ret, VIXCLS_d1, stables_total_usd_ret]`. The current 8-variable system (2,107 obs, lag 1, 8 variables = 72 parameters) is feasible but borderline. The 27.3% connectedness is weak precisely because the system is diluted. A tighter 4-variable system will produce clearer shock-transmission patterns. Report the 8-variable system as robustness.

### 2.3 Unique Contributions from Each Reviewer

**Opus uniquely identified:**
- The specific on-chain metrics to add: exchange net flow, miner-to-exchange flow, Coinbase premium, SOPR, MVRV, realized cap delta (§6 Paper 1)
- The overshoot-revert pattern in R1 (lag1 β=−0.98) as a genuine finding worthy of discussion (§8)
- The specific recommendation to use `plotnine` for publication figures (§13)
- The stale-plan drift prevention mechanism with per-paper `CODEX/paper_N_status.md` files (§14)

**Gemini uniquely identified:**
- Calendar leakage as a threat to Chow/Bai-Perron test integrity specifically (§8) — the other reviewers mentioned calendar issues generally but Gemini connected it to structural break test validity
- The mathematical argument for why flow/price scaling is dimensionally meaningless: "$10M flow on $50k BTC and $70k BTC generates scaling drift" (§8)
- The recommendation to use `DuckDB` for reproducible inventory audits (§13)

**Codex uniquely identified:**
- The event-study placebo p-value labeling defect: computed for `[-5,+5]` but attached to all windows (§8)
- The config path drift issue: `config/factor_blocks.yml` references paths that don't match actual file locations (P0.4)
- The inventory count discrepancy: 490 files (per `MASTER_DATA.csv`) vs 484 cited by Opus and Gemini (§3)
- The explicit metric dictionary schema with 20 fields per variable (data_calendar_metric_strategy_v0.md)

---

## 3. Hostile Referee Simulation

### 3.1 The Three Most Likely Referee Objections

**Objection 1: "Your main structural break is in 2021, not at the ETF date. So what does this paper actually contribute about the ETF era?"**

A skeptical JFE/RFS referee would write: *"The paper's title promises evidence about the spot-ETF regime shift, but Table 3 shows that the Chow test at the ETF date fails to reject for BTC (F=0.81, p=0.60) and barely rejects for ETH (p=0.024). The data-driven break is in 2021 for both assets. The paper then pivots to a different claim — about ETF flow intensity as a contemporaneous correlate — but this is a change of topic, not support for the headline thesis. The paper needs to decide: is it about ETF-date structural breaks (in which case, the null hypothesis is not rejected for BTC) or about factor composition evolution (in which case, 2021 and the Fed hiking cycle are the story, not ETFs)?"*

**Does the current draft address it?** Partially. §1 point 1 and §4.3 honestly report the negative Chow result and the 2021 break. §1 "what this means" paragraph attempts the compositional pivot. But §1 point 2 immediately pivots to "ETFs are now the single most significant driver" which undercuts the pivot's credibility.

**Changes needed:**
1. Reframe the paper around the **compositional evolution** story, not the ETF-as-structural-break story. The title should change to something like: "Factor-Block Recomposition in BTC and ETH: Evidence from a Six-Year Rolling Decomposition."
2. The 2021 break should be the headline finding. ETF flows are a *late-arriving compositional channel* that explains variance in the post-2024 period, not a regime break.
3. Add a formal discussion of why the 2021 break (COVID-stimulus institutional adoption wave) is economically sensible and more interesting than a clean ETF-date narrative.

**Objection 2: "ETF flow intensity is endogenous. You have a flow/return simultaneity problem, and your lagged-flow robustness check actually confirms it."**

A referee would write: *"Table 5 shows β=2.33 for same-day ETF intensity. But R1 shows that in a same-day + lag1 specification, the lag1 coefficient is −0.98 (t=−3.7) — a clear overshoot-and-revert pattern. This means about one-third of the same-day association is reversed the next day, which is classic price-pressure/mean-reversion, not fundamental value transmission. Without an instrument or a proper identification strategy, the 2.33 coefficient conflates fundamental information in flows with transient price pressure. The paper correctly notes 'this is not causal' in §4.4 but then §1 says 'ETFs are now the single most significant driver' — which IS a causal claim."*

**Does the current draft address it?** Partially. §4.4 includes a "this is not causal" disclaimer and §5.1 R1 honestly reports the overshoot-revert. But the executive summary language contradicts this.

**Changes needed:**
1. Make the overshoot-revert finding a featured result, not just a robustness footnote. It's genuinely interesting and distinguishes this paper from naive "flows drive prices" studies.
2. Replace all "driver" language with "correlate" or "contemporaneous associate."
3. Consider adding a structural discussion: the R1 finding is consistent with Kyle (1985) price-impact models where informed flow creates transient price pressure that partially reverts as liquidity providers adjust. Cite the literature (but verify citations independently).

**Objection 3: "Your 14% R² for BTC is not very impressive. Most of your variance is unexplained. What does the factor block decomposition really add beyond what's known?"**

A referee would write: *"BTC full-sample R² is 0.139. Post-ETF, it rises to 0.152 — a 1.3pp improvement that could well be noise. The rolling R² plot (F02) shows enormous time variation, including a collapse to 5-8% in 2023-2024. The honest summary is: most of the time, the identified factor blocks explain very little of BTC daily return variance. ETH is slightly better at 21% post-ETF. Why should readers care about a decomposition of 14-21% of variance? What are the other 79-86%?"*

**Does the current draft address it?** No. The draft treats R² levels as evidence without contextualizing them against the literature on daily return predictability for liquid assets.

**Changes needed:**
1. Add a paragraph contextualizing: daily R² of 10-20% for a liquid asset is actually high by cross-sectional standards. Individual US large-cap stocks have daily R² of 5-15% against the CAPM. For crypto, 14% against macro+institutional factors is economically meaningful.
2. Explicitly discuss the 2024 R²-collapse (median 7.8% for BTC) as a regime-transition feature, not a model failure. The fact that R² recovers to 32% in 2026 is the story — crypto temporarily decoupled from identifiable factors during the ETF-approval uncertainty period, then re-coupled more tightly.
3. Frame the paper's contribution as the *composition changes* across time, not the R² level. The block-partial-R² decomposition is the value-add.

### 3.2 Strongest vs Weakest Claims in v0.1

**Ranked by defensibility (strongest first):**

1. **The 2021 structural break is real and economically interpretable.** Evidence: sup-F argmax at 2021-01-04 (BTC) and 2021-05-12 (ETH), both with placebo p=0.00. Historical context (COVID stimulus, MicroStrategy, Coinbase IPO) is well-documented. **Grade: A.**

2. **The Chow test fails to reject stable loadings at the BTC ETF date.** Evidence: F=0.81, p=0.60. This is an honest null result, which is the paper's most credible finding. **Grade: A.**

3. **ETH experienced a larger regime shift than BTC.** Evidence: ETH R² jumped 5.6pp (15.4%→21.0%) vs BTC's 1.3pp. ETH Chow p=0.024 (marginal rejection). **Grade: B+.**

4. **ETF flow intensity has a strong contemporaneous association with BTC returns.** Evidence: β=2.33, t=8.7, R²=23.7%. The magnitude is robust across HAC lags and winsorization choices. **Grade: B** (strong association, but endogeneity weakens the interpretation).

5. **The R1 overshoot-revert pattern.** Evidence: same-day β=2.86 (t=9.6), lag1 β=−0.98 (t=−3.7). This is a genuine and novel finding. **Grade: B+** (well-documented, but economic interpretation needs development).

6. **BTC is the upstream asset in the VAR system.** Evidence: 99.5% own-FEVD at 10-day horizon. This is trivially true for any dominant asset in a Cholesky-first position. **Grade: C** (may be an artifact of ordering).

7. **"BTC as banking hedge" in SVB episode.** Evidence: +16.8% CAR, t=3.10, but placebo p=0.21. **Grade: C-** (not significant by placebo standard).

8. **"ETFs dampened routine volatility."** Evidence: SD dropped 22%. But this could be crypto maturation, macro environment, or composition effects. No identification. **Grade: D** (correlation, not causation).

### 3.3 Statistical Red Flags

1. **BTC R² increase of 1.3pp (14.0%→15.2%) is within noise.** With n=768 for post-ETF, the standard error of R² is roughly √(2/768) × R²(1-R²) ≈ ±1-2pp. The pre/post difference is not statistically distinguishable from zero. The paper should test this formally with a Vuong test or by reporting the F-statistic for the incremental R².

2. **Event study placebo p-values are all >0.10.** None of the five events produces a statistically significant placebo-adjusted CAR. The FTX collapse (p=0.11) is the closest. This means the events section contributes narrative color but no statistical significance. The paper should be transparent about this.

3. **VAR lag order = 1 is suspiciously low.** BIC selects lag=1 for an 8-variable daily system. This is common when the VAR is overparameterized — the penalty for additional lags outweighs the fit improvement because each lag adds 8² = 64 parameters. A 4-variable system would likely select lag=2-3, which is more informative.

4. **DY connectedness of 27.3% is low.** For comparison, equity markets typically show 60-80% connectedness. This means the 8-variable system is poorly connected — crypto and TradFi variables are largely independent at daily frequency. This is a finding (crypto remains partially decoupled) but the current 8-variable system dilutes the measurement.

5. **Full-sample winsorization at 1/99% applied before sub-period regressions.** Winsorization on the full sample may not respect sub-period return distributions. The 2020 COVID crash and 2022 FTX collapse are in the pre-ETF sample; these tail events are disproportionately trimmed in a way that affects pre-ETF estimates more than post-ETF. R2 checks this and finds minimal impact (β=2.39 vs 2.33), which is reassuring.

---

## 4. Research Design Evaluation

### 4.1 Research Question Assessment

The current question ("did factor loadings change around ETF launches?") is a good starting point but has two problems:

1. **It invites a binary answer that the data rejects for BTC.** The Chow test says "no" for BTC. This makes the paper awkward if it insists on the ETF-date framing.

2. **It buries the compositional story.** The more interesting and defensible question is: "How did the *composition* of BTC and ETH factor exposures evolve across multiple maturation milestones (2021 institutional adoption, 2022 Fed tightening, 2024 ETF launches), and what does the time-varying block R² decomposition reveal about crypto-market integration with traditional finance?"

**My recommendation:** Reframe to the compositional question. This makes the 2021 break a headline finding, the 2024 ETF flow channel a compositional addition (not a break), and the rolling block decomposition the paper's main exhibit.

### 4.2 Identification Strategy

**There is no clean identification strategy, and there doesn't need to be.** The paper's contribution is descriptive/diagnostic — mapping how factor exposures evolved over time. This is valuable if positioned correctly. The danger is implying causal claims that the design cannot support.

The paper can credibly claim:
- Association magnitudes and statistical significance
- Time variation in factor block explanatory power
- Compositional shifts across pre-specified break dates
- Structural break timing (data-driven, not ETF-date)

The paper cannot credibly claim:
- ETFs *caused* anything
- Institutional flows *drive* prices
- Volatility declined *because of* ETFs

### 4.3 Factor Block Architecture

The 5-block design in `config/factor_blocks.yml` is conceptually sound but operationally incomplete:

| Block | Current Implementation | Assessment |
|---|---|---|
| **Macro** (5 vars) | DGS10_d1, DGS2_d1, VIXCLS_d1, DTWEXBGS_d1, DFF_d1 | Good. Core yield/vol/dollar/policy channels. Could add oil (WTI is in the code but not in the block table in the draft). |
| **Institutional** (3 vars) | spy_ret, qqq_ret, gld_ret | Good but conventional. These are really "TradFi risk-appetite" proxies, not direct institutional variables. |
| **Liquidity** (2 vars) | defi_tvl_usd_ret, stables_total_usd_ret | Adequate. Could benefit from a stablecoin sub-basket split. |
| **Sentiment** (1 var) | fng_value_d1 | Thin. Fear & Greed is a single retail sentiment index. Consider adding social media or funding rate proxies if available. |
| **BTC/ETH-native** (1 var each) | cme_btc_basis_close_d1 / cme_eth_basis_close_d1 | **Critically underpopulated.** The CME basis is a futures-spot spread, which is really a derivatives-market variable. A proper on-chain block should include exchange net flow, SOPR, MVRV, or miner-to-exchange flow from the 345 CryptoQuant CSVs. This is the paper's biggest differentiation gap. |

**Recommendation:** Add 3-5 CryptoQuant BTC native metrics to the btc_native block. My top picks:
1. `Data/CryptoQuant/BTC/Exchange Flows/` — aggregate exchange net flow (inflow minus outflow)
2. `Data/CryptoQuant/BTC/Market Indicator/` — SOPR (Spent Output Profit Ratio) or MVRV
3. `Data/CryptoQuant/BTC/Miner Flows/` — miner-to-exchange flow

### 4.4 Sample Design

- **Start:** 2020-01-01. Adequate. Captures COVID crash, recovery, 2021 boom, 2022 bear, 2023 recovery, 2024-2026 ETF era.
- **End:** 2026-04-11. Good — recent enough for the post-ETF sample to be substantial.
- **Pre/Post split:** 2024-01-11 (BTC ETF launch), 2024-07-23 (ETH ETF launch). These are the right dates.
- **Pre-ETF n:** BTC 1,339; ETH 1,123. Adequate.
- **Post-ETF n:** BTC 768 (2.1 years); ETH 582 (1.6 years). Adequate for OLS; tight for VAR.
- **Issue:** The sample includes [2020-01-01, 2026-04-11] = 2,293 calendar days but only ~1,600 business days. If headline regressions switch to business-day, the sample shrinks by ~28%.

### 4.5 Dependent Variables

BTC and ETH daily log returns. No issues with the choice of dependent variable. Log returns are standard, stationary by construction at daily frequency for non-zero-price assets.

---

## 5. Method-by-Method Assessment

### 5.1 Static OLS with HAC

**Implementation quality: A-.**
The code at `src/cqresearch/modeling/ols.py` correctly calls `statsmodels.OLS().fit(cov_type="HAC", cov_kwds={"maxlags": 5})`. Bartlett kernel is the statsmodels default. The implementation is clean and correct.

**HAC lag choice: B.**
Fixed 5 lags is conservative for daily data (roughly 1 trading week). `docs/specs/methods_spec.md` §2 says "Andrews automatic rule" but the code uses fixed 5. The R3 robustness check shows stability across lags 5-40, which is reassuring. For v1.0, reporting Andrews automatic alongside fixed-5 results would strengthen the defense.

**R² interpretation: B-.**
BTC full-sample R²=0.139 is presented correctly. The pre/post comparison (14.0%→15.2% for BTC, 15.4%→21.0% for ETH) is interesting but the BTC difference is within sampling error. ETH's 5.6pp jump is more compelling. The draft does not test whether the R² change is statistically significant.

**What the results actually show:**
The factor model explains 14-21% of daily crypto return variance, with ETH being more responsive to institutional factors post-ETF. The compositional shifts (which blocks gain/lose R² share) are more informative than the level changes.

### 5.2 Rolling OLS and Block R² Attribution

**Implementation correctness: B+.**
The rolling OLS at `src/cqresearch/modeling/rolling.py` is correctly implemented. The `dropna_first=True` approach is sensible — it ensures each window has the same dense composition.

**Label accuracy: C.**
The partial R² computation (lines 76-85) drops one variable, refits, and measures the RSS increase divided by TSS. This is a standard "extra sum of squares" or "variable-drop" partial R². It is NOT:
- Shapley/Owen decomposition (requires evaluating all 2^k subsets — factorial complexity)
- Sequential/Type I partial R² (order-dependent)
- Semi-partial R² (different formula)

The current approach is defensible as long as it's correctly labeled. The label "partial R² by factor block" in the draft is acceptable, but the stacked area chart (F03, F04) implies these partial R² values are additive, which they are not — variable-drop partial R² values do not necessarily sum to total R².

**Window choice: B-.**
Only 180-day window is implemented. `docs/specs/methods_spec.md` §3 specifies 60, 120, and 252. For v1.0, at minimum add 252-day (1 year) as an alternative. The 180-day window is reasonable but the choice should be justified (roughly 6 months, capturing medium-term regime dynamics).

**What the rolling plots actually show:**
F02 (rolling R²) reveals a striking V-shape: R² peaks in 2022 (Fed hiking cycle, macro dominates), collapses to 5-8% in 2023-2024 (crypto-specific dynamics, ETF uncertainty), then recovers to 30%+ in 2025-2026 (post-ETF, renewed macro coupling). This is genuinely interesting and should be the paper's central figure.

F03/F04 (block decomposition stacks) show that macro (blue) dominated in 2022, sentiment/native dominated in 2021, and institutional (green) grew in 2025-2026. The visual is informative but cramped.

### 5.3 Structural Break Tests (Chow + Sup-F)

**Implementation correctness: A-.**
The Chow test at `structural_breaks.py` L37-64 is a textbook implementation. The sup-F sweep at L75-115 correctly iterates over the trimmed interior [15%, 85%] and computes the maximum Chow F. The placebo permutation at L118-135 shuffles y (preserving X covariance), which is the standard approach.

**Label accuracy: B+.**
The docstring (lines 6-9) correctly describes this as "Andrews 1993 sup-F" and explicitly says it "approximates the Bai-Perron (1998) single-break case without the dynamic-programming search." The code is honestly documented. The problem is in `docs/specs/methods_spec.md` §5, which describes full Bai-Perron with UDmax/WDmax as if implemented.

**What the 2021 break finding means:**
The sup-F argmax at 2021-01-04 (BTC) and 2021-05-12 (ETH) is a genuine empirical finding. It means the factor-loading structure changed most dramatically during the COVID-stimulus institutional adoption wave (MicroStrategy Oct 2020, Tesla Feb 2021, Coinbase IPO Apr 2021), not during the ETF launches. This is the paper's most honest and potentially most interesting contribution.

**Placebo protocol adequacy: B.**
300 permutations with y-shuffle is adequate for a p-value resolution of ~0.003. The p=0.00 result means the observed sup-F exceeds all 300 permutation values. A block-bootstrap placebo (preserving serial dependence) would be stronger, as the draft acknowledges in §5.2.

### 5.4 ETF Flow Intensity Regression

**Unit problem: CONFIRMED.**
Flow (USD millions) divided by price (USD) produces units of "BTC" — the number of bitcoins the flow could buy. This is interpretable but not standard. Dividing by market cap yields a dimensionless ratio (flow as a fraction of total market value), which is the standard institutional-flow scaling in the literature.

**The data to fix this exists:** `Data/CryptoQuant/BTC/Market Data/Bitcoin Market Cap - Day.csv` (confirmed by Opus review §8). Adding this to the panel and recomputing intensity as flow/market_cap is a 30-minute code change.

**Simultaneity:**
The R1 robustness check is genuinely informative. The overshoot-revert pattern (same-day β=2.86, lag1 β=−0.98) is consistent with:
- Positive: flows reflect informed trading that moves prices, with partial reversion as liquidity adjusts
- Negative: flows and returns are both responding to the same news; the reversion is mechanical (price overshoots on flow arrival, then corrects)

Neither interpretation supports a clean causal claim. But the pattern itself is a finding worth featuring.

**Economic interpretation:**
With corrected units (flow/market_cap), a 1bp increase in daily flow intensity (e.g., $100M on a $1T market cap) would be associated with a β×1bp change in log returns. The current β=2.33 on flow/price units cannot be directly compared to the literature. After fixing the denominator, re-estimation will produce a different β that should be compared to ETF flow-impact estimates in equity markets (cited appropriately).

### 5.5 VAR / FEVD

**Variable selection: C.**
The 8-variable system `[btc_ret, eth_ret, spy_ret, gld_ret, DGS10_d1, VIXCLS_d1, stables_total_usd_ret, defi_tvl_usd_ret]` is too wide. 8 variables × 1 lag × 8 equations = 72 parameters on ~2,107 observations. Adding a second lag would double this to 144 parameters — infeasible.

**Lag selection: B-.**
BIC selects lag=1, which is typical for overparameterized VARs. This means the VAR captures only 1-day dynamics, missing the 2-5 day transmission channels that are empirically important in crypto markets.

**Cholesky ordering: F.**
Undocumented. The current ordering places BTC first, meaning BTC shocks affect all others contemporaneously but is not affected by any other variable. This is an extremely strong assumption. In reality, SPY shocks (equity market openings) likely affect BTC contemporaneously. The ordering should be: `[DGS10_d1, VIXCLS_d1, spy_ret, gld_ret, stables_total_usd_ret, defi_tvl_usd_ret, eth_ret, btc_ret]` — slow-moving macro first, fast-moving crypto last. Or use generalized FEVD (Pesaran & Shin 1998) which is order-invariant.

**The 27.3% connectedness:**
This is low because the system includes many internally independent variables (GLD and stablecoins have near-zero off-diagonal FEVD entries). A 4-variable system `[btc_ret, spy_ret, VIXCLS_d1, stables_total_usd_ret]` would produce more meaningful connectedness estimates.

**FEVD interpretation:**
The finding that BTC has 99.5% own-variance at 10 days is partially an artifact of being first in the Cholesky ordering. If BTC were last, its own-variance share would be lower. The ETH finding (66.9% from BTC) is more robust to ordering and tells a real story: ETH is a BTC-beta asset at daily frequency.

### 5.6 Event Studies

**Benchmark choice: C+.**
Using SPY as the market benchmark for crypto assets is defensible but imperfect. A crypto-weighted market index would be better, but no such index exists in the panel. Using SPY measures *equity-market-adjusted* abnormal returns, which is appropriate for the question "did crypto behave differently from TradFi during these events?" but not for "did crypto have abnormal returns in absolute terms?"

**Estimation window: B.**
180 trading days ending 10 days before the event is standard. The 10-day gap prevents event contamination of the estimation window.

**Event window choices: B.**
`[-1,+1]`, `[-5,+5]`, `[0,+5]`, `[0,+30]` are standard. The asymmetric `[0,+30]` captures post-event drift, which is relevant for ETF launches (gradual flow regime change).

**Placebo interpretation: C.**
As noted in B4 above, the placebo p-values are computed on `[-5,+5]` and applied to all windows. More importantly, ALL placebo p-values are > 0.10. This means that by the placebo benchmark, none of the events are statistically significant. The draft partially acknowledges this ("placebo p-values are uniformly high") but should be more direct: "None of the five pre-registered events produces a placebo-adjusted significant CAR at the 5% level."

**The "sell-the-news" finding:**
BTC fell −8.2% in `[-1,+1]` around the BTC ETF launch. This is interesting narrative but placebo p=0.61 means it's well within random noise. The draft says "not significantly different from the average bad week" — which is correct and honest.

**The SVB "banking hedge" finding:**
+16.8% CAR in `[0,+5]`, t=3.10, but placebo p=0.21. The parametric t-stat is significant but the placebo test is not. This is a classic tension between parametric and nonparametric inference. The honest conclusion: "suggestive but not significant by nonparametric standards."

### 5.7 Robustness Suite

| Check | Addresses the Right Concern? | Assessment |
|---|---|---|
| **R1** (lagged flow) | Yes — directly addresses simultaneity | A-. The overshoot-revert finding is genuinely interesting. |
| **R2** (no winsorization) | Yes — checks sensitivity to tail trimming | B+. Result is robust. |
| **R3** (HAC lag sensitivity) | Yes — checks inference stability | A-. Clean result: t-stats stable or increase with lag. |
| **R4** (post-2021 subwindow) | Yes — checks whether 2020 COVID spike drives pre-ETF results | B. Useful but could be more precisely targeted. |
| **R5** (sup-F split) | Yes — uses data-driven break instead of ETF date | B+. Confirms that loadings differ across the 2021 break. |
| **R6** (common support) | Yes — ensures results aren't driven by unbalanced coverage | B. Important check, especially given F09 coverage gaps. |

**Missing robustness checks for v1.0:**
1. **Business-day regression panel** (drop weekends) — all three reviewers flagged this
2. **Weekly resampled panel** (W-FRI) — addresses mixed-frequency concerns
3. **Window sensitivity** for rolling OLS (60, 120, 252 days)
4. **Market-cap-scaled ETF intensity** (after fixing the denominator)
5. **4-variable vs 8-variable VAR** comparison
6. **Alternative Cholesky orderings** or generalized FEVD
7. **Cook's D outlier diagnostics** — `methods_spec.md` §11 lists this
8. **Monthly-vintage FRED data** to check look-ahead bias in monthly series

---

## 6. Data and Panel Evaluation

### 6.1 Data Sources for Paper 1

| Source | Role | Status | Issue |
|---|---|---|---|
| CryptoQuant BTC/ETH prices | Dependent variable | ✓ In panel | None |
| FRED macro panel | Macro block | ✓ In panel | Monthly series (CPI, UNRATE) may have look-ahead bias |
| TradingView SPY/QQQ/GLD/XLK/DXY | Institutional + dollar blocks | ✓ In panel | SPY/QQQ coverage starts ~2024-03 based on F09 — possible data gap |
| Farside ETF flows | ETF flow intensity | ✓ In panel | Unit problem (B1 above) |
| DefiLlama TVL + stablecoins | Liquidity block | ✓ In panel | `stables_total_usd` starts mid-2022 (F09 coverage chart) |
| AlternativeMe FNG | Sentiment block | ✓ In panel | Single source, no validation |
| TradingView CME basis/DVOL | Native block | ✓ In panel | CME basis starts 2020 with 8% missing |
| **CryptoQuant BTC on-chain** | **Missing native block** | ✗ Not in panel | 345 CryptoQuant CSVs available but none loaded |

### 6.2 Calendar and Fill Policy

**Current implementation:**
- Master calendar: crypto-7 (every UTC day), 2,293 rows
- Stock variables: ffill 4 days (code default; config says 0)
- Flow variables: zero-fill on non-trading days within active window
- Rate variables: ffill 4 days

**What it should be for Paper 1:**

| Variable Type | Fill Policy | Headline Calendar | Robustness Calendar |
|---|---|---|---|
| BTC/ETH prices | None (available 7/7) | Business-day | Calendar-day |
| SPY/QQQ/GLD prices | ffill ≤3 days (for computing returns) | Business-day (native) | Calendar-day (with zero weekend returns) |
| FRED rates | ffill ≤3 days | Business-day | Calendar-day |
| ETF flows | Zero-fill on non-trading days after listing date | Business-day | Calendar-day |
| DeFi TVL/stablecoins | None (available 7/7) | Business-day (drop weekends) | Calendar-day |
| CME basis | ffill ≤3 days | Business-day | Calendar-day |
| FNG | ffill ≤1 day | Business-day | Calendar-day |

**Specific recommendation:** Build `config/calendars.yml` into the operational code path. Change `src/cqresearch/data/calendars.py` line 65 default from 4 to 3. Add a `build_business_day_panel()` function that drops weekends/holidays and serves as the headline regression input.

### 6.3 Feature Construction Quality

**`panel.py` review:**
- **Log returns** (lines 48-52): Correct. Uses `log_return()` on price columns, correctly strips `_close` suffix.
- **First differences** (lines 54-57): Correct for rate/yield-type variables.
- **ETF flow intensity** (lines 63-71): Defective — uses close instead of market cap (see B1).
- **Winsorization** (called in `02_run_analyses.py` line 68): Applied at 1/99% on full sample before subsetting. This is acceptable but creates a subtle issue: wild returns in the pre-ETF sample (COVID, FTX) are trimmed using full-sample quantiles, which are influenced by the calmer post-ETF distribution.

**Missing features:**
- On-chain metrics from CryptoQuant
- Market-cap-based ETF intensity
- Stablecoin sub-basket split (fiat-backed vs crypto-backed)
- Exchange-flow indicators

### 6.4 Missing Variables / Factor Block Gaps

The btc_native and eth_native blocks are critically thin. Each has ONE variable (CME basis), which is a TradFi derivatives metric, not an on-chain native metric. This makes the paper's claim of being "crypto-native" hollow.

**Must-add for v1.0 (BTC native block):**
1. Exchange net flow (exchange inflow minus outflow) — measures BTC moving to/from exchanges for potential selling/buying
2. SOPR or MVRV — measures whether BTC holders are in profit/loss, a well-known on-chain sentiment indicator
3. Miner-to-exchange flow — captures miner selling pressure

**Nice-to-add (ETH native block):**
1. ETH staking ratio or validator count
2. ETH gas fees/burn rate (post-EIP-1559)

---

## 7. Figures and Tables — Publication Readiness

### 7.1 Figure-by-Figure Assessment

| Figure | Shows | Pub-Ready? | Issues | Priority |
|---|---|---|---|---|
| **F01** Cumulative returns | BTC/ETH log returns 2020-2026 with event annotations | **Needs work** | Annotation text overlaps near "BTC ETF" and "ETH ETF". Good data provenance footer. Color scheme is acceptable. | Medium |
| **F02** BTC rolling R² | 180-day rolling R² with mean line | **Needs work** | Missing ETF-date vertical line. Should mark the 2021 sup-F break date. Y-axis range [0.05, 0.40] good. Needs a panel companion for ETH. | High |
| **F03** BTC partial R² stack | Rolling block decomposition | **Needs work** | Visually cramped; 5 colors are hard to distinguish at print size. The stacked area implies additivity, which is not strictly true for variable-drop partial R². Needs annotation for key regime transitions. | **Critical** — this is the paper's signature figure |
| **F04** ETH partial R² stack | Same as F03 for ETH | **Needs work** | Same issues as F03. Starts later (~mid-2021) due to data availability. | High |
| **F05** Sup-F BTC | F-statistic across all candidate break dates | **Needs work** | No vertical lines for ETF date or 2021 argmax. The monotonically declining F after 2021 is visually clear. Needs trimming boundaries marked. | High |
| **F06** Sup-F ETH | Same for ETH | **Needs work** | Same issues. | High |
| **F07** FEVD heatmap | 10-day FEVD matrix | **Needs work** | X-axis label text overlaps ("stables_total_usd_ret" runs into "defi_tvl_usd_ret"). Variable names should be human-readable. Values display is good. | Medium |
| **F08** Event CARs | Horizontal bar chart of CARs with t-stats and placebo p | **Needs work** | Annotation text collides (top bar "ETH ETF 2024-07-23 t[+0,+30]p=0.92" is unreadable). Too many bars. Should consolidate to key windows only. | Medium |
| **F09** Coverage | Data availability heatmap | **Needs work** | Very informative for a data appendix. Y-axis labels are tiny but readable. The gap structure is clearly visible. Not needed in the main paper — move to appendix. | Low |
| **F10** BTC-TradFi correlation | Rolling 60-day correlation with SPY/GLD/DXY | **Needs work** | Good additional diagnostic. Should mark event dates. | Low |

**Recommended v1.0 main-text figures (6 max):**
1. F01 (cumulative returns, cleaned up) — context setting
2. F02 (rolling R², combined BTC+ETH panel, with event lines)
3. F03/F04 (block decomposition, redesigned as side-by-side panels)
4. F05/F06 (sup-F, combined panel with break date and ETF date markers)
5. A new ETF flow intensity scatter/time series figure
6. F10 (rolling correlation, cleaned up) — shows maturation narrative

**Move to appendix/online supplement:** F07 (FEVD), F08 (event CARs), F09 (coverage)

### 7.2 Table-by-Table Assessment

| Table | Shows | Correct? | Missing | Format Issues |
|---|---|---|---|---|
| **descriptive_stats.csv** | Summary stats pre/post | ✓ | Should add percentiles (5/25/50/75/95), Jarque-Bera test | Standard format |
| **static_ols_pre_post_etf.csv** | Pre/post OLS with HAC | ✓ | Missing F-test for R² equality across subsamples | Long format (melt) — needs pivot for publication |
| **block_r2_pre_post.csv** | Block R² decomposition | See label issue | Must relabel from "block R²" to "variable-drop partial R² contribution" | Standard |
| **structural_breaks_summary.csv** | Chow + sup-F | ✓ | Should add Andrews critical values alongside permutation p-values | Standard |
| **etf_flow_regression.csv** | ETF flow β | Unit problem | Must recompute with market-cap denominator | Standard |
| **event_studies.csv** | CARs + placebo p | Labeling issue | Placebo p should be per-window or clearly labeled as [-5,+5] benchmark | Wide — too many columns |
| **fevd_10d.csv** | FEVD matrix | ✓ but ordering issue | Must document and justify Cholesky ordering | Standard |
| **Robustness R1-R6** | Various checks | ✓ | Missing business-day, weekly, window-sensitivity checks | Standard |

### 7.3 Missing Figures and Tables for v1.0

1. **Source/coverage summary table** — which vendor, column, frequency, date range, missingness for each variable used
2. **Factor-block membership table** — regressors assigned to each block, with variable-selection justification
3. **Business-day vs calendar-day comparison table** — show headline results under both calendars
4. **Nested F-test table** — block-by-block explanatory power comparison
5. **ETF flow scatter plot** — intensity vs same-day BTC return, with lag-1 overlay
6. **On-chain factor block regression table** — once CryptoQuant metrics are added

---

## 8. Draft Prose Assessment

### 8.1 Narrative Structure

The draft tells a moderately coherent story but loses the reader in three places:

1. **The lead is buried.** The executive summary starts with the ETF-date structural break (which fails for BTC) before getting to the compositional story. It should lead with the compositional framing and the 2021 break as the headline.

2. **The ETF flow section (§4.4) feels disconnected** from the structural break section (§4.3). The paper says "the ETF date didn't cause a break" and then immediately says "but ETFs are the most important factor." This needs a bridge paragraph explaining that compositional evolution ≠ structural break.

3. **The event study (§4.7) is a narrative sidebar** with no statistically significant results. It should be shortened and positioned as descriptive context, not evidence.

### 8.2 Causal Language Audit

| Location | Problematic Text | Replacement |
|---|---|---|
| §1, point 2 | "ETFs are now the **single most significant driver** of daily BTC returns" | "ETF flow intensity is the strongest contemporaneous correlate of daily BTC returns in the post-2024 sample" |
| §4.1, last sentence | "consistent with **patient-institutional-holder flows dampening routine volatility** without removing regime shocks" | "consistent with a maturing asset class displaying lower quotidian volatility alongside heavier tails, though we do not attribute this pattern to any specific mechanism" |
| §4.4, paragraph 2 | "flow per USD of prior-day BTC close" | "flow per USD of prior-day BTC close (a flow-per-unit-price proxy; see §5.2 for discussion of alternative scalings)" |
| §4.7, "BTC as banking hedge" | "the cleanest 'BTC as banking hedge' episode" | "the largest positive abnormal return in our event sample, suggestive of but not statistically confirming a flight-to-crypto response" |
| §6, item 1 | "Re-run Table 5 with `btc_etf_intensity.shift(1)` as the primary regressor; add **issuer fixed effects**" | This suggests treating issuer variation as identification, which is reasonable, but calling it "fixed effects" for a single cross-section of 13 issuers is a stretch. Say "issuer-level decomposition" instead. |

### 8.3 Method-Label Accuracy in Prose

| Location | Problematic Text | Corrected Text |
|---|---|---|
| §4.3 title | "Structural-break tests (Table 3, `structural_breaks_summary.csv`; Figures F05, F06)" | Fine as is — the draft does not call it Bai-Perron. The draft correctly uses "sup-F search" language. |
| §6, item 5 | "Bai-Perron multiple breaks" | Correct in v0.1 — this is listed as FUTURE WORK, not claiming it's implemented. |
| F03/F04 title | "partial R² by factor block" | Change to "Variable-drop partial R² contribution by factor block" |
| §2.3, ETF flow intensity | "ETF flow intensity = flow_t / close_{t-1}, scaling raw USD-M flows by prior-day BTC price so the regressor is stationary" | "ETF flow intensity = flow_t / close_{t-1}. This is a flow-per-unit-price regressor, not a flow-relative-to-market-cap measure. See §5.2 for the corrected market-cap-scaled specification." |

### 8.4 Missing Sections for v1.0

1. **Abstract** (currently missing entirely)
2. **Literature review** (§1.5 or separate §2) — position against Bianchi et al., Liu & Tsyvinski (2021), Foley et al. (2023) type papers
3. **Formal hypothesis statements** (H1: factor loadings changed; H2: composition shifted toward institutional; H3: ETF flows add incremental explanatory power)
4. **Identification discussion** — explain what the paper can and cannot identify
5. **Limitations section** — calendar artifacts, endogeneity, single-country ETF sample, post-ETF sample length
6. **Conclusion** — summary of contributions and implications for portfolio managers, regulators, and researchers

---

## 9. Decisions Required

### Decision 1: ETF Flow Intensity Denominator

**The issue:** `panel.py` divides flow by prior-day BTC close price. Should it divide by market cap, AUM, volume, or remain as flow-per-price?

**Agent positions:**
- Opus: "Divide by prior-day market cap. The data exists (`Data/CryptoQuant/BTC/Market Data/Bitcoin Market Cap - Day.csv`)." (§17 Decision 2)
- Gemini: "Flow must strictly be scaled by Total Market Cap, Circulating Supply, or Spot Volume." (§8)
- Codex: "Label current ETF intensity as flow-per-price or rebuild it as flow/market cap, AUM, or volume." (P0.6)

**My recommendation:** Divide by prior-day market cap. Report flow-per-price as robustness.

**Reasoning:** Flow/market-cap is the standard institutional-flow scaling. It measures flow as a fraction of total market value, making the coefficient interpretable across assets and time periods with different price levels. Flow/price is dimensionally "number of BTC the flow could buy" — interpretable but non-standard. Flow/AUM is also defensible but AUM starts only at the ETF launch date. Flow/volume would be interpretable but introduces another simultaneity channel.

**Impact if wrong:** If market cap has data quality issues (e.g., CryptoQuant's BTC market cap uses a different circulating supply definition), the coefficient would be wrong. Mitigation: validate CryptoQuant market cap against price x known supply.

**Implementation:** `src/cqresearch/features/panel.py` line 69: add `btc_mcap` to the panel from `Data/CryptoQuant/BTC/Market Data/Bitcoin Market Cap - Day.csv`, then change to `panel["btc_etf_total"] / panel["btc_mcap"].shift(1)`. Same for ETH.

---

### Decision 2: Should the 2021 Structural Break Be the Headline?

**The issue:** The sup-F argmax is 2021-01-04 (BTC) and 2021-05-12 (ETH), not the ETF date. The paper's title references the ETF "regime shift."

**Agent positions:**
- Opus: "Yes, make the 2021 break the headline. Frame the ETF era as a compositional evolution, not a structural revolution." (§17 Decision 3)
- Gemini: "The Structural Break in BTC/ETH Factor Geometries" — uses "structural break" as the title, not "ETF regime shift." (§6 Paper 1)
- Codex: "did BTC and ETH factor exposures change across crypto market maturation and spot-ETF institutionalization, and are those changes better described as ETF-date breaks or gradual multi-regime evolution?" (Four paper protocols §Paper 1)

**My recommendation:** Yes. The 2021 break is the headline. Re-title the paper.

**Reasoning:** The data clearly supports a 2021 break and clearly does NOT support a BTC ETF-date break (Chow F=0.81, p=0.60). Publishing a paper titled "Factor-Block Evolution Around the Spot-ETF Regime Shift" when the Chow test fails to reject at the ETF date is a credibility risk. The compositional framing — where the ETF era is one chapter in a multi-epoch maturation — is both more honest and more interesting than "ETFs changed everything."

**Suggested new title:** "Factor-Block Recomposition in Crypto-Asset Returns: A Six-Year Rolling Decomposition of BTC and ETH" — with the ETF channel as a key finding within the story, not the headline.

**Impact if wrong:** The paper loses some marketing appeal. The "ETF" keyword is timely and attention-grabbing. But credibility with referees matters more than marketing.

**Implementation:** Update `reports/drafts/paper_v0.1_2026-04-18.md` title and framing throughout. Restructure §1 to lead with the 2021 break.

---

### Decision 3: Business-Day vs Calendar-Day Regression Sample

**The issue:** Calendar-day regressions include artificial zero returns on weekends for TradFi variables.

**Agent positions:**
- Opus: "Business-day for headline regressions (Papers 1-2); calendar-day as robustness." (§17 Decision 4)
- Gemini: "Do not force TRADFI and CRYPTO to a 24/7 calendar for regressions." (§9)
- Codex: "market-day panel for headline macro/ETF regressions." (§9)

**My recommendation:** Business-day for headline results. Calendar-day as robustness.

**Reasoning:** Forward-filling TradFi prices onto weekends creates zero returns on Saturday and Sunday. These artificial zeros mechanically reduce correlation estimates, dilute regression coefficients, and inflate R² denominators. All three reviewers agree. The sample loss (~28% from dropping weekends) is a worthwhile price for clean inference.

**Impact if wrong:** If crypto-specific weekend dynamics are economically important (weekend returns differ systematically from weekday returns), business-day regressions would miss this. Mitigation: report a weekend-returns diagnostic and crypto-only weekend regressions.

**Implementation:** Add `build_business_day_panel()` to `src/cqresearch/data/panel_builder.py`. Modify `scripts/02_run_analyses.py` to use it for headline results.

---

### Decision 4: Method Label Strategy (True Bai-Perron vs Relabel)

**My recommendation:** Implement `ruptures` for true multiple-break detection AND relabel current results as "Andrews (1993) sup-F single-break test."

**Reasoning:** Relabeling alone is insufficient for a v1.0 submission because a natural referee question is "why didn't you test for multiple breaks?" Having both single-break sup-F and k-break results strengthens the paper. `ruptures` is pure Python, pip-installable, well-documented, and low-risk.

**Implementation:** Add `ruptures>=1.1` to `pyproject.toml`. Create `src/cqresearch/modeling/multiple_breaks.py` with a thin `ruptures` wrapper. Run with `max_breaks=3` on BTC and ETH. Compare optimal break dates against current sup-F argmax.

---

### Decision 5: Block Partial R² Strategy (Shapley vs Relabel)

**My recommendation:** Relabel to "variable-drop partial R² contribution" for v1.0. Implement group-Shapley only if time permits.

**Reasoning:** Group-Shapley decomposition with 5 blocks requires 2^5 = 32 regressions per rolling window. With ~1,900 windows, that's ~61,000 regressions. Feasible but time-consuming to implement correctly. The variable-drop approach is perfectly defensible if correctly labeled. The stacked area charts (F03/F04) should include a footnote: "Variable-drop partial R² values do not necessarily sum to total R²; the stacked visualization is approximate."

**Implementation:** Rename all references from "block R²" to "variable-drop partial R² contribution." Add the non-additivity footnote to F03/F04.

---

### Decision 6: VAR System Size

**My recommendation:** 4-variable compact VAR for headline: `[btc_ret, spy_ret, VIXCLS_d1, stables_total_usd_ret]`. 8-variable as robustness.

**Reasoning:** The 4-variable system captures the three main transmission channels (equity risk appetite, volatility regime, crypto liquidity) with enough degrees of freedom for lag orders 2-3. The 8-variable system dilutes the signal and forces BIC to select lag=1. For a paper about BTC factor dynamics, we want to see how shocks from SPY, VIX, and stablecoins propagate to BTC — not every pairwise relationship.

**Implementation:** `scripts/02_run_analyses.py` line 132-133: change `cols` to `["btc_ret", "spy_ret", "VIXCLS_d1", "stables_total_usd_ret"]` for headline. Keep current 8-variable as robustness.

---

### Decision 7: VAR Cholesky Ordering

**My recommendation:** Use generalized FEVD (Pesaran & Shin 1998), which is order-invariant. If using Cholesky, order macro-first (slow to fast): `[DGS10_d1, VIXCLS_d1, spy_ret, stables_total_usd_ret, btc_ret]`.

**Reasoning:** The Cholesky ordering is a strong identifying assumption. For the 4-variable compact VAR, the economically defensible ordering is: bond yields (slowest-moving, institutional) -> equity volatility -> equity returns -> stablecoin liquidity -> BTC (fastest-moving, most informationally reactive). This is the standard "slow-to-fast" ordering in the SVAR literature. Alternatively, the generalized FEVD avoids the issue entirely.

**Implementation:** `src/cqresearch/modeling/var_fevd.py`: add a `generalized=True` option using `res.fevd(horizon).decomp` vs a custom GFEVD implementation.

---

### Decision 8: Event Study Benchmark

**My recommendation:** Keep SPY as primary benchmark. Add a "no benchmark" (raw returns) specification as robustness. Note the limitation in the paper.

**Reasoning:** There is no established crypto-market benchmark return. Using SPY measures equity-market-adjusted abnormal returns, which is actually the right question for an institutionalization paper: "Did crypto move differently from equities around these events?" Using raw returns (no benchmark) would show the absolute crypto impact.

**Implementation:** Add a raw-return CAR column to `event_studies.csv`. Discuss both in the paper.

---

### Decision 9: On-Chain Factor Block

**My recommendation:** Yes. Add exchange net flow, SOPR, and miner-to-exchange flow for BTC. Add ETH staking ratio for ETH.

**Reasoning:** This is the paper's biggest differentiation opportunity. The existing 345 CryptoQuant CSVs are the project's unique asset. Without on-chain variables, the paper is a generic "ETF and macro factors" study that anyone could replicate with public data. With on-chain variables, it becomes a crypto-native factor study that leverages proprietary data.

**Implementation:** Add a data-loading step for 3-4 CryptoQuant CSVs in `src/cqresearch/data/loaders.py`. Add them to the btc_native block in `config/factor_blocks.yml`. Rerun all analyses.

---

### Decision 10: Which CryptoQuant Metrics

**My recommendation:** Start with three for BTC:
1. **Exchange net flow** (`Data/CryptoQuant/BTC/Exchange Flows/`) — measures BTC flowing to/from exchanges
2. **SOPR** (`Data/CryptoQuant/BTC/Market Indicator/`) — spent output profit ratio
3. **Miner-to-exchange flow** (`Data/CryptoQuant/BTC/Miner Flows/`) — miner selling pressure

These three capture distinct on-chain information channels: trading intent (exchange flow), holder profitability (SOPR), and supply-side pressure (miner flow).

**Implementation:** Identify exact CSV filenames via `Data/MASTER_DATA.csv`, load, transform to daily first-differences or log-returns as appropriate, add to btc_native block.

---

### Decision 11: Winsorization

**My recommendation:** Keep 1/99% symmetric winsorization as the default. Add 0.5/99.5% and no-winsorization as robustness (R2 already does the latter).

**Reasoning:** 1/99% is standard in the empirical finance literature. Asymmetric winsorization would require justification (e.g., crypto returns are right-skewed, so trim more from the right). The current symmetric approach is defensible and the robustness R2 confirms stability.

**Implementation:** No change to the default. Add a 0.5/99.5% robustness check in `scripts/05_robustness.py`.

---

### Decision 12: HAC Lag Selection

**My recommendation:** Use fixed 5 for the headline. Report Andrews automatic and Newey-West optimal as robustness (R3 already does sensitivity). Add Andrews automatic to the `fit_ols` function as an option.

**Reasoning:** Fixed lag = 5 is a pragmatic choice for daily data. The R3 check shows t-statistics are stable across lags 5-40. `methods_spec.md` mentions Andrews automatic — implementing it is one line in statsmodels: `cov_kwds={"maxlags": None}` with `use_correction=True`.

**Implementation:** Add `hac_method: Literal["fixed", "andrews"] = "fixed"` parameter to `fit_ols()`. Report both in the main regression table.

---

### Decision 13: Python Version Pin

**My recommendation:** Pin to 3.11. Update `pyproject.toml` `requires-python` to `">=3.11"`.

**Reasoning:** `AGENTS.md` says 3.11+. `pyproject.toml` says >=3.10. `ruff` and `mypy` target py311. The active interpreter may be 3.10. Standardize on 3.11 — all current dependencies support it.

**Implementation:** Change `pyproject.toml` `requires-python`. Generate `uv.lock`.

---

### Decision 14: PCA Within Blocks

**My recommendation:** Not for v1.0 headline results. Use PCA as a robustness check if the on-chain block has >5 variables.

**Reasoning:** The current block sizes (5 macro, 3 institutional, 2 liquidity, 1 sentiment, potentially 4 BTC-native) don't require PCA — no block exceeds 5 variables. PCA would make coefficient interpretation harder. If we add 6+ native metrics, within-block PCA (as specified in `config/factor_blocks.yml` `pca_config`) becomes appropriate.

**Implementation:** Defer. If btc_native block grows beyond 5 variables, implement PCA using the config specification (2 components, full-sample fit).

---

### Decision 15: Forward-Fill Limit

**My recommendation:** 3 days for TradFi levels (covers weekends + Monday holiday). 0 for returns and flows. Read from `config/calendars.yml`.

**Reasoning:** 3 days is the minimum needed to bridge a standard 2-day weekend and occasional Monday holiday. 4 days (current code default) would bridge a 4-day gap (Thanksgiving week in the US), but this is too aggressive — it should produce NaN for such weeks. The config file should be the source of truth.

**Implementation:** Change `src/cqresearch/data/calendars.py` line 65: `ffill_limit_days: int = 3`. Update `config/calendars.yml` line 13: `ffill_limit: 3`. Make `align_to_master()` read from config.

---

## 10. Execution Plan: v0.1 -> v1.0

### Phase 1: Fix What's Broken (Days 1-3)

| # | Task | Files | Acceptance Criteria |
|---|---|---|---|
| 1.1 | **Fix ETF intensity denominator** | `src/cqresearch/features/panel.py` L63-71, `src/cqresearch/data/loaders.py` | btc_etf_intensity = flow / market_cap.shift(1); flow/price as alt column |
| 1.2 | **Reconcile calendar/fill policy** | `config/calendars.yml`, `src/cqresearch/data/calendars.py` L65 | Config says 3, code reads config, tests pass |
| 1.3 | **Build business-day panel function** | `src/cqresearch/data/panel_builder.py` | `build_business_day_panel()` drops weekends/holidays |
| 1.4 | **Relabel block partial R²** | `src/cqresearch/modeling/rolling.py` docstring, `scripts/03_make_figures.py` | All labels say "variable-drop partial R² contribution" |
| 1.5 | **Document VAR Cholesky ordering** | `scripts/02_run_analyses.py` L132, `docs/specs/methods_spec.md` §8 | Ordering justified and documented |
| 1.6 | **Fix event-study placebo labeling** | `scripts/02_run_analyses.py` L160-167 | Compute per-window placebos or clearly label as [-5,+5] benchmark |

### Phase 2: Add What's Missing (Days 4-7)

| # | Task | Files | Acceptance Criteria |
|---|---|---|---|
| 2.1 | **Add CryptoQuant on-chain metrics** | `src/cqresearch/data/loaders.py`, `config/factor_blocks.yml`, `scripts/02_run_analyses.py` | 3 BTC native metrics loaded, in btc_native block, regressions rerun |
| 2.2 | **Implement true multiple-break test** | `pyproject.toml`, `src/cqresearch/modeling/multiple_breaks.py` | `ruptures` installed; k-break search on BTC/ETH; results in tables |
| 2.3 | **Business-day headline regressions** | `scripts/02_run_analyses.py` | All headline tables rerun on business-day panel |
| 2.4 | **4-variable compact VAR** | `scripts/02_run_analyses.py` | 4-var FEVD table produced alongside 8-var robustness |
| 2.5 | **Add block-level nested F-tests** | `scripts/02_run_analyses.py` | Table comparing macro-only vs institutional-only vs full model |
| 2.6 | **Weekly robustness panel** | `scripts/05_robustness.py` | W-FRI resampled regressions for R7 |
| 2.7 | **Window sensitivity for rolling OLS** | `scripts/02_run_analyses.py` | 60, 120, 252-day windows alongside 180-day |

### Phase 3: Strengthen What's Weak (Days 8-12)

| # | Task | Files | Acceptance Criteria |
|---|---|---|---|
| 3.1 | **Redesign publication figures** | `scripts/03_make_figures.py` or new `viz/paper_figures.py` | 6 main-text figures at journal quality; SVG exports |
| 3.2 | **Write literature review** | Draft §2 | 15-25 verified citations positioned against existing work |
| 3.3 | **Write abstract, hypotheses, limitations** | Draft §0, §1.5, §6 | Formal H1-H3 stated; limitations explicit |
| 3.4 | **Reframe draft narrative** | Draft §1-§6 | 2021 break as headline; compositional framing; causal language fixed |
| 3.5 | **Expand test suite** | `tests/unit/` | 25+ tests covering calendar fills, ETF units, rolling math, break correctness |
| 3.6 | **Add metric dictionary** | `config/metric_dictionary.yml` | Every Paper 1 variable registered with metadata |

### Phase 4: Red-Team and Submit (Days 13-16)

| # | Task | Acceptance Criteria |
|---|---|---|
| 4.1 | **Independent hostile review** (different model than implementer) | Written review with objections ranked |
| 4.2 | **Citation verification** (web search every external reference) | Every DOI/SSRN/arXiv ID confirmed via durable URL |
| 4.3 | **Replication run** | Fresh `scripts/run_full_pipeline.py` on clean environment; all tables/figures match |
| 4.4 | **Language audit** | Zero instances of "driver", "caused", "proved", "Bai-Perron" (unless implemented), "Shapley" |
| 4.5 | **Final draft assembly** | Paper v1.0 in Quarto/Typst format with publication-quality PDF |

---

## 11. Risk Register

| Risk | Probability | Impact | Mitigation | Owner |
|---|---|---|---|---|
| Calendar fill artifacts change headline R² | **High** | **High** | Run business-day robustness NOW (Phase 1.3) | Data lead |
| 2021 break is the real story, not ETFs | **Confirmed** | **High** | Reframe paper narrative (Phase 3.4) | Research lead |
| Bai-Perron not implemented | **Confirmed** | **Medium** | Add `ruptures` (Phase 2.2); relabel if it fails | Methods lead |
| ETF flow intensity units wrong | **Confirmed** | **High** | Fix to market cap (Phase 1.1) | Features lead |
| On-chain metrics don't add explanatory power | **Medium** | **Medium** | Pre-screen via correlation; include regardless as differentiation | Research lead |
| Referee objects to SPY as crypto benchmark | **Medium** | **Low** | Add raw-return robustness (Decision 8) | Methods lead |
| VAR Cholesky ordering changes FEVD results | **High** | **Medium** | Implement generalized FEVD (Decision 7) | Methods lead |
| Literature review cites unverified sources | **Medium** | **High** | Web-verify every citation before inclusion (Phase 4.2) | Citation lead |
| Business-day panel reduces sample to ~1,600 obs | **Confirmed** | **Low** | This is a known cost; 1,600 is still adequate for OLS | Data lead |
| CryptoQuant BTC market cap data has gaps or quality issues | **Low** | **Medium** | Cross-validate against price x CirculatingSupply; use Artemis as backup | Data lead |
| `ruptures` results diverge significantly from sup-F | **Low** | **Medium** | Report both; discuss discrepancy honestly | Methods lead |
| Paper is scooped by concurrent ETF/crypto studies | **Medium** | **Medium** | Emphasize compositional decomposition and 2021 break as unique contributions | Research lead |

---

## 12. Quality Gate

**Inputs read:**
- `AGENTS.md` (provided in user rules)
- `Manager/Opus Manager/comprehensive_review.md` (910 lines, full read)
- `Manager/Gemini Manager/Project_Audit_Report.md` (232 lines, full read)
- `Manager/Codex Manager/codex_manager_review_2026-04-18.md` (251 lines, full read)
- `Manager/Codex Manager/four_paper_protocols_v0.md` (207 lines, full read)
- `Manager/Codex Manager/data_calendar_metric_strategy_v0.md` (145 lines, full read)
- `Manager/Codex Manager/p0_execution_backlog.md` (193 lines, full read)
- `reports/drafts/paper_v0.1_2026-04-18.md` (390 lines, full read)
- `reports/run_summaries/03_run_analyses.md` (66 lines, full read)
- `src/cqresearch/features/panel.py` (77 lines, full read)
- `src/cqresearch/modeling/ols.py` (90 lines, full read)
- `src/cqresearch/modeling/rolling.py` (100 lines, full read)
- `src/cqresearch/modeling/structural_breaks.py` (139 lines, full read)
- `src/cqresearch/modeling/var_fevd.py` (56 lines, full read)
- `src/cqresearch/modeling/event_study.py` (135 lines, full read)
- `src/cqresearch/data/calendars.py` (129 lines, full read)
- `scripts/02_run_analyses.py` (261 lines, full read)
- `scripts/05_robustness.py` (188 lines, full read)
- `config/factor_blocks.yml` (71 lines, full read)
- `config/events.yml` (59 lines, full read)
- `config/calendars.yml` (38 lines, full read)
- `docs/specs/methods_spec.md` (69 lines, full read)
- All 11 figures viewed (F01-F10 + F02_eth)

**Key findings (top 5 by importance):**
1. **The ETF intensity denominator is wrong** (flow/price not flow/market_cap) — must fix before any claim about ETF flow magnitude. This is the single highest-priority code fix.
2. **The 2021 structural break is the paper's best finding** — lean into it, don't bury it. Reframe the paper around compositional evolution with the ETF era as one episode.
3. **Business-day regressions must be the headline** — calendar-day regressions with artificial weekend zeros are indefensible as headline results. All three reviewers agree.
4. **The on-chain factor block is essentially empty** — with one CME basis variable, the paper cannot claim to be "crypto-native." Adding 3 CryptoQuant metrics is the best ROI improvement.
5. **All event study CARs fail the placebo test** — the draft must be transparent that no event produces statistically significant abnormal returns by the nonparametric benchmark.

**Decisions made by this agent (D1-D15 summary):**

| # | Decision | Recommendation |
|---|---|---|
| D1 | ETF flow denominator | Market cap |
| D2 | 2021 break as headline | Yes |
| D3 | Business-day vs calendar-day | Business-day headline, calendar-day robustness |
| D4 | Method labels | Implement `ruptures` AND relabel existing results |
| D5 | Block R² strategy | Relabel to "variable-drop partial R²" for now |
| D6 | VAR system size | 4-variable headline, 8-variable robustness |
| D7 | Cholesky ordering | Generalized FEVD preferred; if Cholesky, macro-first |
| D8 | Event study benchmark | SPY primary + raw-return robustness |
| D9 | On-chain block | Yes, add 3 BTC-native CryptoQuant metrics |
| D10 | Which metrics | Exchange net flow, SOPR, miner-to-exchange flow |
| D11 | Winsorization | Keep 1/99% symmetric; add 0.5/99.5% robustness |
| D12 | HAC lag | Fixed 5 headline; add Andrews automatic as alternative |
| D13 | Python version | Pin to 3.11 |
| D14 | PCA within blocks | Not for v1.0 unless btc_native exceeds 5 variables |
| D15 | Forward-fill limit | 3 days for levels, 0 for returns/flows; read from config |

**Confidence:** 87%.
- High confidence (>90%): defect identification (B1-B5), method assessments, decision recommendations D1-D5, D9.
- Medium confidence (75-90%): VAR recommendations (D6-D7) — depends on team's econometric perspective. Literature positioning — depends on what current papers exist.
- Lower confidence (<75%): execution timeline (16 days assumes full-time effort and no unexpected data quality issues).

**What I could not verify:**
- Whether the pipeline actually runs end-to-end (did not execute)
- Whether CryptoQuant BTC market cap CSV exists and is clean (referenced by Opus but not viewed)
- Whether `ruptures` produces comparable results to current sup-F
- Numerical correctness of all existing regression coefficients (would require re-execution)
- Whether SPY/QQQ coverage starts in 2024 (F09 shows possible gaps but image resolution is limited)

**Next agent:** Implementation builder to execute Phase 1 fixes. Recommended model: Codex/GPT-5.4 for precise code changes, followed by Claude Opus for draft prose rewrite. Human review required before executing Decision 2 (reframing the paper narrative) and Decision 9 (adding on-chain metrics to the baseline).
