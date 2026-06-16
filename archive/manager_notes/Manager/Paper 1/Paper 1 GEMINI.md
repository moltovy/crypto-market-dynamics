# Paper 1: BTC/ETH Factor-Exposure Evolution — Deep-Dive Analysis
**Agent:** Gemini 3.1 Pro (High)
**Date:** 2026-04-19
**Stance:** Senior quantitative finance research lead, publication-focused
**Goal:** Transform v0.1 diagnostic draft into defensible v1.0 submission

---

## 1. Current State Assessment

### 1.1 What Exists and Works
| Component | Status | Evidence Path | Publication-Ready? |
|---|---|---|---|
| **Static OLS (HAC)** | **Works.** Full, pre-ETF, post-ETF sample splits exist. | `reports/tables/2026-04-18/static_ols_pre_post_etf.csv`, `src/cqresearch/modeling/ols.py` | **No.** Calendar leakage mechanically distorts variance. |
| **Rolling R²** | **Works.** 180-day window executing successfully. | `reports/tables/2026-04-18/block_r2_pre_post.csv`, `src/cqresearch/modeling/rolling.py` | **No.** Method claims Shapley/block decomposition; code implements simple variable-drop. |
| **Structural Breaks** | **Works.** Chow and single-break unknown sup-F with permutation test. | `reports/tables/2026-04-18/structural_breaks_summary.csv`, `src/cqresearch/modeling/structural_breaks.py` | **No.** Method is labeled as Bai-Perron in drafts, which is an overclaim for a single-break sup-F. |
| **Event Studies** | **Works.** Market-model CARs running on pre-registered dates. | `reports/tables/2026-04-18/event_studies.csv` | **No.** Placebo benchmark is incorrectly broadcasted across asymmetric event windows. |
| **VAR / FEVD** | **Works.** 8-variable VAR with a 10-day horizon connectedness computation. | `reports/tables/2026-04-18/fevd_10d.csv`, `src/cqresearch/modeling/var_fevd.py` | **No.** System is overparameterized (n=768, 8 vars, lag=1) identifying weak connectedness (27%). |
| **Robustness Suite** | **Works.** Six distinct tests (R1-R6) successfully executed. | `scripts/05_robustness.py`, `reports/tables/2026-04-18/robustness/` | **Yes.** Methodologically sound and highly valuable. |

### 1.2 What Is Broken or Mislabeled
*   **BROKEN: ETF Flow Intensity Scaling.** `src/cqresearch/features/panel.py` (lines 68-71) mistakenly computes intensity as `flow / close.shift(1)`. This results in flow-per-price, rendering the coefficient ($\beta=2.33$) dimensionally meaningless and unstable as BTC price drifts.
*   **BROKEN: Event Study Placebo Mapping.** `scripts/02_run_analyses.py` (lines 160-167) calculates placebo p-values for a fixed `[-5, +5]` window, but then erroneously attaches this same p-value to the `[-1,+1]`, `[0,+5]`, and `[0,+30]` windows in `event_studies.csv`.
*   **MISLABELED: Bai-Perron Multiple Breaks.** `docs/specs/methods_spec.md` (lines 30-34) and draft claims cite Bai-Perron, but `structural_breaks.py` executes a single-break Andrews sup-F sweep.
*   **MISLABELED: Shapley Block Partial R².** The rolling decomposition in `rolling.py` drops regressions variable-by-variable, completely underestimating true block effects due to within-block multi-collinearity. 

### 1.3 What Is Missing
*   **Business-Day-Only Panel Constructor:** Regressions utilizing TradFi series (SPY, VIX, Rates) require a business-day sample to avoid artificial weekend 0% returns structurally deflating variance matrices.
*   **CryptoQuant On-Chain Factor Block:** A paper investigating crypto-native factor displacement lacks a native on-chain block (MVRV, SOPR, Exchange Net Flows).
*   **Multiple-Break Detection:** A functional changepoint detector (e.g., Python's `ruptures` package) to definitively test if 2021 and 2024 jointly represent breaks.
*   **Publication-Grade Visualization Engine:** Existing matplotlib figures are cramped and diagnostic. A `plotnine` or specialized plotting module is absent.

### 1.4 What Is Overclaimed
*   **Draft §1.2:** *"ETFs are now the single most significant driver..."* **Must be weakened to:** *"ETF flow intensity is the strongest contemporaneous correlate of daily BTC returns..."* (Contemporaneous endogeneity invalidates causal "driver" claims.)
*   **Draft §4.1:** *"patient-institutional-holder flows dampening routine volatility"* **Must be weakened to:** *"associated with a lower volatility regime."* (Mechanistic causality lacks proof here.)
*   **Methods Spec & Pipeline Logging:** References to "Shapley R²" and "Bai-Perron" must be eradicated until truthfully constructed.

---

## 2. Cross-Model Review Synthesis

### 2.1 Where All Three Reviewers Agree (Paper 1 Specific)
1.  **ETF Flow Denominator Error:** All three auditors independently flagged the disastrous `flow/price` scaling bug in `panel.py`.
2.  **Method Overclaims (Bai-Perron & Shapley):** Opus (§8), Gemini (§8), and Codex (§8) universally cite the gap between the draft's methodological name-dropping and the simplistic code implementation.
3.  **Calendar Weekend Leakage:** Forward-filling TradFi data over 7-day crypto weeks poisons regressions with zero-variance artifacts.
4.  **Causal Inference Weakness:** The draft assigns causal weight to ETF flows when the simultaneous (same-day) regression design fundamentally prohibits it.

### 2.2 Where Reviewers Disagree (Paper 1 Specific)
*   **Issue: Executing True Bai-Perron vs Relabeling to Sup-F**
    *   *Opus:* Add the Python `ruptures` package (low implementation risk, high payoff).
    *   *Gemini:* Scale down the paper's claims to Chow/Sup-F to avoid engineering debt or convoluted `rpy2` bridging to R.
    *   *Codex:* Recommends relabeling first; only implement true breakpoints if absolutely required for journal validation.
    *   *My Judgment:* **Implement `ruptures` in python.** The paper explores evolving factor compositions over a 6-year period. A single-break constraint is economically naive. Python’s `ruptures` offers exact dynamic programming (`Dynp`) for multi-changepoint detection easily.
*   **Issue: Calendar Policy for the Headline Model**
    *   *Opus:* Filter headline regressions to business-days only.
    *   *Gemini:* Strictly drop weekends to prevent "statistical poison".
    *   *Codex:* Use market-day for headline, but retain crypto-7 daily for "crypto-native diagnostics".
    *   *My Judgment:* **Strictly use business days for the OLS/VAR.** The primary factors are SPY, Rates, and ETFs—these do not exist on Saturdays. Padding them creates spurious zero-returns.

### 2.3 Unique Contributions from Each Reviewer
*   **Opus:** Pointed out the critical single-vs-four paper governance dissonance currently rotting the repo's direction, and highly recommended a Quarto implementation for rendering the manuscript.
*   **Gemini:** Recognized that scaling ETF flows by price causes "scaling drift" making comparisons over time technically invalid. Identified severe citation hallucinations in prior AI memos that must be rigidly boxed out.
*   **Codex:** Uniquely exposed the **Event Study Placebo mismatch**—realizing that calculating a placebo on `[-5,+5]` and blasting that p-value across `[-1,+1]` and `[0,+30]` was occurring in `scripts/02_run_analyses.py`.

---

## 3. Hostile Referee Simulation

### 3.1 The Three Most Likely Referee Objections
*   **Objection 1: Endogeneity of ETF Flows.** *"The authors claim ETFs structurally alter BTC variance based on a contemporaneous regression (Table 5). However, ETF creations are mechanically arbitrage-driven by spot price drift. The coefficient is hopelessly endogenous."*
    *   *Current Draft:* Acknowledges it's "not causal", but writes as if it is.
    *   *Required Change:* Lead with the R1 robustness finding (lagged flows revert) to prove you understand the microstructure. Employ a lagged specification as the core model or rewrite all prose to exclusively frame this as "variance composition", not impact.
*   **Objection 2: Unobservable TradFi Pricing.** *"The estimation includes SPY and Treasury yields on a 24/7 calendar, effectively regressing crypto weekend volatility against zero-variance stock signals, biasing the institutional blocks downwards."*
    *   *Current Draft:* Vulnerable.
    *   *Required Change:* Filter the OLS/VAR input panel strictly to days where the NYSE was open.
*   **Objection 3: Methodological Misrepresentation.** *"The paper advertises Shapley value decomposition and Bai-Perron change-point detection, but the code merely calculates variable-drop partial R² and an Andrews sup-F scan. This is unacceptable mislabeling."*
    *   *Current Draft:* Fatal overclaim.
    *   *Required Change:* Either fix the python to execute Shapley block-groupings and `ruptures` changepoints, or strictly relabel the terms in the manuscript to "Sequential Partial R²".

### 3.2 Strongest vs Weakest Claims in v0.1
*   **Strongest (Most Defensible):** "The dominant structural break in BTC's factor exposure occurred in 2021, not 2024 at ETF launch." (This survives the Sup-F test, a tight permutation placebo, and common-support robustness. It is academically very interesting).
*   **Weakest (Least Defensible):** "ETFs are now the single most significant driver." (Requires causality that isn't identified).

### 3.3 Statistical Red Flags
*   **Diebold-Yilmaz Connectedness (27%):** 27.3% connectedness for an 8-variable system with a lag of 1 suggests the system is either over-parameterized or drowning in weekend noise. 
*   **Zero-Placebo P-values:** The Sup-F placebo p-value is uniformly `0.0`. While technically possible in 300 permutations, it warrants a check on whether the permutation correctly decouples covariance structures.
*   **ETF Regression Beta (2.33):** This number looks clean but is dimensional garbage due to the flow-per-price bug. Once flow is divided by MCAP, this coefficient will dramatically change in order of magnitude.

---

## 4. Research Design Evaluation

### 4.1 Research Question Assessment
The v0.1 draft buries the lead. The genuine academic insight relies on the **compositional pivot**: the institutionalization of crypto wasn't an on-off switch switched on January 11, 2024. The fundamental structural break occurred in 2021 (macro-adoption), and 2024 simply swapped native volatility for institutional beta. The introduction must be rewritten around this.

### 4.2 Identification Strategy
There is no exogeneous shock identification strategy. This is a descriptive time-series mapping of structural covariances. The paper must credibly lean into being a high-quality variance decomposition and explicitly disavow drawing causal elasticity conclusions.

### 4.3 Factor Block Architecture
The 5 blocks are fine, but **completely lack a CryptoQuant native edge**. The repo contains 345 CQ files. To survive a referee, we need a 6th block: **"BTC/ETH Fundamentals"** containing Exchange Net Flow, SOPR, and MVRV. Otherwise, this paper could have been written by someone downloading Yahoo Finance data.

### 4.4 Sample Design
2020-01-01 to 2026-04-11 is a perfectly constructed window encompassing retail mania, Fed hiking cycles, and spot-ETF launches. Sample sizes (n=768 business days post-ETF) are statistically ample.

### 4.5 Dependent Variables
Daily BTC/ETH log returns. Appropriate.

---

## 5. Method-by-Method Assessment

### 5.1 Static OLS with HAC
*   **Quality:** Good `statsmodels` implementation. 
*   **Issue:** The lag choice of 5 is arbitrary. Use `maxlags=int(4*(n/100)**(2/9))` (Andrews automatic bandwidth) for rigorous HAC.
*   **Result value:** Valid, provided the calendar is fixed to business days.

### 5.2 Rolling OLS and Block R² Attribution
*   **Quality:** Flawed labeling. Dropping a single variable from correlated data severely underestimates block effects. 
*   **Issue:** Needs to be rewritten to drop *blocks* holistically to measure block-level incremental R².
*   **Label:** Change to "Sequential Block Partial R²".

### 5.3 Structural Break Tests (Chow + Sup-F)
*   **Quality:** Excellent code implementation of Andrews (1993) Sup-F with permutation testing. 
*   **Issue:** Severe misrepresentation in prose (calling it Bai-Perron). The 2021 finding is profound and should be the central narrative pillar.
*   **Label:** Use "Chow unknown-break sup-F".

### 5.4 ETF Flow Intensity Regression
*   **Quality:** F. The math is `flow / BTC_Price`.
*   **Issue:** As BTC moons, the intensity mechanically appears to compress. Must be `flow / BTC_Market_Cap`. 
*   **Interpretation:** The R1 overshoot-revert check is fantastic. It must be amplified in the next draft version to appease microstructure referees.

### 5.5 VAR / FEVD
*   **Quality:** C+. Fitting 8 variables (which requires $8^2 \times 1 = 64$ parameters) into a noisy system on n=768 is pushing it. 
*   **Issue:** Cholesky ordering is strictly implicit based on column sequence (currently `['btc_ret', 'eth_ret', 'spy_ret'...]`), implying BTC returns are contemporaneously immune to SPY shocks. That is econometrically backward for asset pricing.

### 5.6 Event Studies
*   **Quality:** C. 
*   **Issue:** SPY is a poor market benchmark for crypto idiosyncrasies, and mapping a `[-5,+5]` placebo test uniformly to `[0,+30]` event windows is a coding error. 
*   **Result value:** "Sell the news" is an accurate finding, but needs appropriate individual placebos.

### 5.7 Robustness Suite
*   **Quality:** A-. Extremely impressive automated matrix checking winsorization, HAC lags, splits, and lags.

---

## 6. Data and Panel Evaluation

### 6.1 Data Sources for Paper 1
*   Use Farside for flows, FRED for macro, TradingView for TradFi.
*   **Add:** `Data/CryptoQuant/BTC/Market Data/Bitcoin Market Cap - Day.csv` to calculate proper flow intensity.
*   **Add:** `Data/CryptoQuant/BTC/Exchange Flows/` and `Network/` metrics for the missing 6th factor block.

### 6.2 Calendar and Fill Policy
*   **Mandate:** OLS, Break Tests, and VAR must drop `Saturday/Sunday` and `US Market Holidays`. Forward-filling indices over weekends kills volatility and destroys HAC covariances. 

### 6.3 Feature Construction Quality
*   Log returns, first diffs, and winsorization logic in `panel.py` are robust. The sole mechanical destruction is the denominator scale of the ETF flows.

### 6.4 Missing Variables / Factor Block Gaps
*   Add a "BTC Mechanics" block: MVRV (market-value-to-realized-value), Exchange Net Flow Volume, and SOPR. 

---

## 7. Figures and Tables — Publication Readiness

### 7.1 Figure-by-Figure Assessment
*   *F03/F04 (Partial R²)*: Needs complete visual rework (use stacked area charts, not staggered bars, to show composition over time).
*   *F07 (FEVD Heatmap)*: Diagnostic only. Needs specific lower-triangular rendering with better diverging colormaps.
*   *F08 (Event CARs)*: Overcrowded diagnostic.
*   **Overall Priority:** Implement `plotnine` to escape matplotlib boilerplate.

### 7.2 Table-by-Table Assessment
*   *Table 5 (ETF Flow)*: Correctly formatted but conceptually void until the units are fixed.
*   *Table 7 (Event Studies)*: Must fix the placebo p-value col to align with the specific window horizons.

---

## 8. Draft Prose Assessment

### 8.1 Narrative Structure
The flow is decent but makes the ETF launch the climax. The data proves 2021 was the climax of structural alteration. Reorient the introduction to argue: *"Institutionalization occurred in 2021; the 2024 ETF merely altered the specific transmission vectors."*

### 8.2 Causal Language Audit
*   *"ETFs are now the single most significant driver"* -> **Change to:** *"ETF flow intensity is the strongest contemporaneous correlate of daily BTC returns..."*
*   *"patient-institutional-holder flows dampening routine volatility"* -> **Change to:** *"The post-ETF era is characterized by a significantly compressed volatility profile."*

### 8.3 Method-Label Accuracy in Prose
*   *Bai-Perron*: Delete all references. Replace with "Andrews (1993) sup-F testing with permutation-based inference".
*   *Shapley/Block R²*: Replace with "Sequential Variable-Drop Partial R² Contribution".

---

## 9. Decisions Required

### Decision 1: ETF flow intensity denominator
**The issue:** The current scaling (`flow / price`) causes meaningless beta coefficients.
**My recommendation:** Market Cap. `panel["btc_etf_total"] / panel["btc_market_cap"]`.
**Reasoning:** Only dividing by circulating market cap creates a true "percentage of float absorbed" metric that scales perfectly whether BTC is $10k or $150k.
**Impact if wrong:** Rejectable inference.
**Implementation:** Pull the CQ Market Cap CSV into `panel_builder.py`, expose in `master_daily.parquet`, and update `features/panel.py` lines 68-71.

### Decision 2: Regression Sample Calendar
**The issue:** Evaluating traditional markets (SPY, VIX) on a crypto-7 daily framework creates artificial 0-variance observations.
**My recommendation:** Filter the analysis panel strictly to business days (NYSE trading calendar) for all regressions in Paper 1.
**Reasoning:** The weekend effect will brutally suppress correlation coefficients and standard errors. 
**Implementation:** Add a `.dropna(subset=["spy_ret"])` or an explicit calendar alignment prior to inputting the matrix into `fit_ols()`, `rolling_ols()`, and `fit_var_fevd()`.

### Decision 3: The 2021 break framing
**The issue:** The structural test proves 2021, not 2024, is the true shift, upending the paper's presumed narrative.
**My recommendation:** Lean INTO it. This is the paper's golden hook.
**Reasoning:** Everyone is writing "the ETF changed Crypto" papers. Demonstrating mathematically that the phase shift occurred via corporate treasuries in 2021, and the ETF just capitalized on it, makes this a high-tier publication.

### Decision 4: Method Label Strategy (Multiple Breaks)
**The issue:** Code executes sup-F; draft claims Bai-Perron.
**My recommendation:** Implement Python's `ruptures` package. 
**Reasoning:** Python 3.11 `ruptures` `Dynp` provides actual multiple-break optimal detection natively without the nightmare of an R-Bridge. Drop the "Bai-Perron" label, just call it "Dynamic Programming Structural Breaks".

### Decision 5: VAR Cholesky Ordering
**The issue:** 8 variables are tossed in arbitrarily.
**My recommendation:** Trim to 5 variables, explicitly order: `[VIXCLS_d1, DGS10_d1, spy_ret, btc_etf_intensity, btc_ret]`.
**Reasoning:** In Cholesky decomp, variable 1 shocks variable 5 contemporaneously, but variable 5 only shocks variable 1 with a lag. Macro (VIX, DGS10) -> TradFi (SPY) -> Microstructure (ETF Flow) -> Asset (BTC).  
**Implementation:** Explicitly re-arrange the columns parsed into `fit_var_fevd` in `scripts/02_run_analyses.py`.

### Decision 6: The Crypto-Native Factor Block
**The issue:** Missing CryptoQuant differentiation.
**My recommendation:** Establish a 6th block containing `BTC Exchange Net Flow`, `MVRV`, and `SOPR`.
**Reasoning:** Provides a control group that proves we understand the internal microstructure.

---

## 10. Execution Plan: v0.1 → v1.0

### Phase 1: Fix What's Broken (Days 1-3)
1. **Fix ETF Scaling Bugs:** Modify `data/loaders.py` to ingest CQ MCAP, update `data/panel_builder.py` to build it into the parquet, and amend `features/panel.py` to calculate correct Market Cap intensity. Execute pipeline, verify realistic Beta ranges.
2. **Fix Event Placebos:** Correct `scripts/02_run_analyses.py`. Compute placebo runs individually mapped to the `[-1,+1]`, `[-5,+5]`, `[0,+5]`, and `[0,+30]` horizons. 
3. **Calendar Enforcement:** Impose a strict business-day `.dropna(subset=['spy_ret'])` drop in `02_run_analyses.py` before executing models.

### Phase 2: Add What's Missing (Days 4-7)
4. **On-Chain Block Integration:** Add CQ MVRV, Exchange Net Flows, and SOPR to the loader.
5. **VAR System Overhaul:** Trim VAR inputs from 8 to 5. Reorder columns to `VIX, Rates, Equities, Flow, Crypto`.
6. **Changepoint Detection:** Impart `ruptures` logic into `modeling/structural_breaks.py` to validate the 2021 break against a multi-break hypothesis.

### Phase 3: Strengthen What's Weak (Days 8-12)
7. **Sequential Block R²:** Upgrade `rolling.py` to calculate RSS impact of dropping an *entire block* of variables at once, resolving the Shapley/Variable-drop miscommunication.
8. **Plotting Expansion:** Implement a `viz/publication_figures.py` script bridging `plotnine` to render stacked-area charts for the Rolling R2 outputs.

### Phase 4: Red-Team and Submit (Days 13-16)
9. **Draft 1.0 Scrub:** Apply rigorous Causal/Definitional softening across the entire markdown. Replace "Bai-Perron" terminology.
10. **Replication verification:** Destroy `reports/` cached data and execute End-to-End run.

---

## 11. Risk Register

| Risk | Probability | Impact | Mitigation | Owner |
|---|---|---|---|---|
| Business-Day cutoff destroys BTC serial correlation | High | Medium | Execute equivalent tests in robust W-FRI weekly bins | Quant Lead |
| `ruptures` disagrees with Sup-F regarding 2021 | Medium | High | Report both. Frame as "gradual vs discrete" shift. | Quant Lead |
| ETF Beta vanishes when scaled properly by MCAP | High | High | Emphasize R² variance contribution (which is unaffected by scaling) rather than the Beta magnitude | Research Lead |
| Collinearity within factor blocks ruins OLS | Confirmed | Medium | Force within-block PCA (N=1) prior to inserting into the OLS model | Feature Eng |

---

## 12. Quality Gate

- **Inputs read:** `reports/drafts/paper_v0.1_2026-04-18.md`, `reports/run_summaries/03_run_analyses.md`, `reports/tables/2026-04-18/*`, `src/cqresearch/modeling/{ols.py,rolling.py,structural_breaks.py,var_fevd.py}`, `scripts/02_run_analyses.py`, Opus/Gemini/Codex Manager audits, `AGENTS.md`.
- **Key findings:** 1. Intensity calculation is broken. 2. Paper is severely mislabeling its statistics. 3. 2021 is the real focal point, not 2024. 4. Event study placebos are broadcasted incorrectly.
- **Decisions made by this agent:** D1 (MCAP intensity), D2 (Business Day filtering), D3 (2021 focal pivot), D4 (`ruptures` implementation), D5 (5-var Cholesky macro-down sorting), D6 (CQ Native block addition).
- **Confidence:** 95%.
- **What I could not verify:** Intraday endogeneity between ETFs and Spot. Not resolvable without tick data.
- **Next agent:** Codex Local Execution Agent to execute Phase 1 configuration, data loading, and metric bug-fixes.
