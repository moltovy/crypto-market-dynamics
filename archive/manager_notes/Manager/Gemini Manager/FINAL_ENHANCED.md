# CryptoQuant Research Program — Final Synthesis
**Synthesized from:** Opus Manager Review, Gemini Manager Review, Codex Manager Review
**Synthesis date:** 2026-04-18
**Synthesis agent:** Gemini 3.1 Pro (High)

---

## 1. Consensus Findings (All Three Agents Agree)

### 1.1 Repository State
- **Finding:** The repository is past the planning stage and contains functional pipelines, a large data inventory, and initial generated outputs (tables, figures, master panel). However, the current output is only `v0.1` diagnostic-grade, not publication-grade.
- **Tag:** [VERIFIED]
- **Evidence:** [Opus+Gemini+Codex] cite `src/cqresearch/`, `scripts/`, `reports/figures/`, and `reports/panels/master_daily.parquet`.

### 1.2 Governance Gaps
- **Finding:** There is a severe contradiction between `AGENTS.md` (which mandates a four-paper portfolio) and the rest of the repository (`project_research_plan.md`, `README.md`, `.cursor/rules/global-constitution.mdc`, `HANDOFF.md`), which all describe a single-paper project.
- **Tag:** [VERIFIED]
- **Evidence:** [Opus+Gemini+Codex] all point out this contradiction and demand an immediate rewrite of the stale governance docs to match `AGENTS.md`.

### 1.3 Method-Label Problems
- **Finding:** The current paper draft and specs overclaim the implemented methods. "Bai-Perron" is actually just a single-break unknown `sup-F` test. "Shapley block partial R²" is actually a simpler variable-drop pseudo R².
- **Tag:** [VERIFIED]
- **Evidence:** [Opus+Gemini+Codex] all verified this by reading `src/cqresearch/modeling/structural_breaks.py` and `rolling.py`.

### 1.4 Data Quality and Central Asset
- **Finding:** The curated data inventory across 7 vendors is the strongest asset of the repository, offering robust cross-vendor overlap verification. This data easily supports four papers.
- **Tag:** [VERIFIED]
- **Evidence:** [Opus+Gemini+Codex] cite `Data/MASTER_DATA.csv` and `CODEX/data_analysis.md`.

### 1.5 Calendar/Fill Problems
- **Finding:** The current calendar and fill policies are either undocumented, conflicting (e.g., config says 0-fill while code does 4-day forward fill), or cause artificial zeros on weekends that mathematically ruin regressions if mixed-frequency data are included.
- **Tag:** [VERIFIED]
- **Evidence:** [Opus+Gemini+Codex] confirm conflicts between `config/calendars.yml` and `src/cqresearch/data/calendars.py`.

### 1.6 Testing Gaps
- **Finding:** Testing is extremely thin. Running `pytest` gives 9 passing tests, but these only check basic imports and fixtures, completely ignoring numerical assertions, structural break correctness, or calendar fill edge cases.
- **Tag:** [VERIFIED]
- **Evidence:** [Opus+Gemini+Codex] verify tests cover only basic scaffolds (`tests/unit/`).

### 1.7 Prior AI Output Risks
- **Finding:** Certain quarantined AI outputs (e.g., `deep-research-report.md`, `Beyond Correlation...`) contain hallucinated citations for 2026/future arXiv IDs, false LinkedIn URLs, and method overreach (DML, etc.).
- **Tag:** [VERIFIED]
- **Evidence:** [Opus+Gemini+Codex] agree these files are a contamination risk to drafted text.

### 1.8 Maximum-Inventory Paper Feasibility
- **Finding:** Running a kitchen-sink regression with all 480+ CSVs into one paper is scientifically indefensible, leading to multiple testing problems and structural collinearity. A "Data Atlas" fits best as shared platform infrastructure, not a 5th paper.
- **Tag:** [DECISION-NEEDED] (Human approval needed to transition to a shared factor-library).
- **Evidence:** [Opus+Gemini+Codex] all agree the maximum inventory approach is only viable as an internal data dictionary/panel library.

---

## 2. Contradictions and Disagreements

### 2.1 Paper 4 Selection
- **The Issue:** What should the fourth paper be (the second non-ETF bridge paper)?
- **Opus:** "DeFi vs CEX Liquidity Fragmentation" (Artemis DEX volume, TVL composition, CEX inflows).
- **Gemini:** "Capital Flight in Microstructure: DeFi TVL vs Centralized Exchanges under Stress" (VIX tracking against DefiLlama TVL).
- **Codex:** "DeFi Credit, Lending, and RWA Rate-Arbitrage" (Artemis lending files, DefiLlama RWA history).
- **Strongest Evidence:** [Codex]. Opus and Gemini acknowledge in their own analyses that CEX and DeFi metrics are "not comparable yet" (citing `CODEX/data_analysis.md`), which carries a high risk of failure. Codex aligns its paper with concrete, verified `Artemis/Lending` files existing in the repo.
- **Resolution:** Proceed with Codex's recommendation (DeFi Credit/RWA), with ETH Staking LST/LRTs as a fallback.
- **Flag:** **HUMAN DECISION REQUIRED** 

### 2.2 Tooling Migration Aggressiveness
- **The Issue:** How heavily should the infrastructure be modernized?
- **Opus:** Conservative — add `plotnine` for visualization, `ruptures` for structural breaks, and `Quarto` for paper builds.
- **Gemini:** Aggressive — migrate to `Polars/DuckDB` entirely, use `rpy2` to execute R `strucchange` code, use `plotnine`/`Quarto`.
- **Codex:** Minimalist — fix governance completely first, delay dependencies. 
- **Strongest Evidence:** [Codex + Opus]. Gemini's recommendation for `rpy2` is extremely risky for Python reproducibility and team capabilities. Polars vs. Pandas isn't the bottleneck right now; governance is.
- **Resolution:** Adopt Codex's minimalist phase 1 (fix governance, use Python). Adopt Opus's pipeline additions (`plotnine`, pure Python `ruptures`, `Quarto`) after the protocols are approved.
- **Flag:** No human decision required; default to Codex/Opus convergence.

### 2.3 Calendar Strategy Details
- **The Issue:** How should the mixing of 5-day TradFi data with 7-day Crypto data be modeled?
- **Opus:** 7-day calendar for crypto, forward fill TradFi max 3 days, skip weekend returns if needed.
- **Gemini:** Completely drop weekends to run purely Business-Day panels for macro regression; "0% weekend returns are statistical poison."
- **Codex:** Market-day (5-day) calendar for Papers 1-2 macro regressions, calendar-day (7-day) for crypto-native diagnostics. 
- **Strongest Evidence:** [Gemini + Codex]. Forward filling stock prices/VIX across weekends creates zero-variance days mathematically, breaking the OLS/VAR integrity. 
- **Resolution:** For any paper incorporating Traditional Finance variables, strictly join on a 5-day Market Calendar filtering out crypto weekends.
- **Flag:** No human decision required; methodologically unambiguous.

### 2.4 Data Inventory Count (484 vs 490)
- **The Issue:** Opus and Gemini claim 484 CSV files. Codex claims 490.
- **Who is right:** [Codex] is right. 
- **Why:** Codex actually ran the verification and documented the precise sub-counts matching the latest `Data/MASTER_DATA.csv` states (345 CQ + 48 Artemis + etc = 490). Opus and Gemini relied on stale summaries. 
- **Resolution:** 490 is the canonical count.

### 2.5 CODEX Folder Naming
- **The Issue:** Renaming the `CODEX` directory.
- **Opus:** Keep as `CODEX`, add per-paper statuses.
- **Gemini:** Rename to `AUDIT/` or `QA_GATES/`.
- **Codex:** Keep as `CODEX`.
- **Resolution:** Keep as `CODEX` to preserve Git history and active path links in `.mdc` files.
- **Flag:** No human decision required.

### 2.6 Pipeline Entry Point Strategy
- **The Issue:** Resolving the conflict between `run_pipeline.py` and `scripts/run_full_pipeline.py`.
- **Opus:** Make `run_pipeline.py` the data curation entry, and `scripts/run_full_pipeline.py` the research analysis point.
- **Gemini:** Delete `scripts/run_full_pipeline.py` and force a single canonical entry to match `.cursor` rules. 
- **Codex:** Keep both, document the distinction.
- **Strongest Evidence:** [Opus + Codex]. `run_pipeline.py` targets `tools/data_collection`, while `scripts/run_full_pipeline.py` operates on `src/cqresearch/`. They do fundamentally different things.
- **Resolution:** Keep both. Update the `.cursor/rules/global-constitution.mdc` to clarify that one is for ETL/curation and the other is for research analysis.

### 2.7 VAR System Size
- **The Issue:** Appropriateness of the 8-variable VAR model.
- **Opus:** 8 variables is overparameterized for the sample size. Shrink to a 4-variable compact system.
- **Gemini:** Agrees, recommends a precise 4-variable VAR.
- **Codex:** Points out the identification/Cholesky ordering is missing entirely. 
- **Resolution:** Shrink to a 4-variable VAR with explicit Cholesky ordering documentation.
- **Flag:** No human decision required.

### 2.8 ETF Flow Intensity Fix
- **The Issue:** ETF Intensity is calculated as Flow divided by Price, which is economically meaningless since BTC prices change dynamically.
- **Opus:** Use Prior-Day Market Cap.
- **Gemini:** Use Market Cap or Total AUM. 
- **Codex:** Use Market Cap, AUM, or Volume. 
- **Resolution:** Divide by Prior-Day Market Cap (simplest, uses existing `CryptoQuant/BTC/Market Data/Bitcoin Market Cap - Day.csv`).

### 2.9 Prior AI Output Handling
- **The Issue:** What to do with the hallucination-prone AI reports in `reports/prior_ai_outputs/`.
- **Opus:** Salvage the variables, ignore citations.
- **Gemini:** Delete or physically isolate them immediately.
- **Codex:** Leave quarantined, run a citation audit before relying on anything. 
- **Resolution:** Isolate and quarantine. Write a strict test script `make check-citations` that rejects AI placeholder citations.

### 2.10 R-Bridge for Bai-Perron
- **The Issue:** Implement true Bai-Perron testing or relabel the method?
- **Gemini:** Port to R using `rpy2` and the `strucchange` package. 
- **Opus:** Use pure Python `ruptures` package. 
- **Codex:** Just fix the paper's text to accurately state `Chow Test and single-break sup-F` and avoid adding deps.
- **Strongest Evidence:** [Codex]. `rpy2` invokes massive C-level dependency chain headaches, completely risking reproducibility for a lightweight Python project.
- **Resolution:** Relabel the drafted results in the short-term to reflect accurate bounds (Chow/sup-F). If true Bai-Perron is demanded natively, use Python's `ruptures`, never R. 
- **Flag:** **HUMAN DECISION REQUIRED**.

---

## 3. Blind Spots (None of the Three Covered Adequately)

1. **Halving Confounding:** All agents accepted that 2024 institutionalization breaks were correlated with ETF launches. However, none explicitly raised the April 2024 Bitcoin Halving as a massive structural confounder to variance and flow modeling which happened precisely during the ETF absorption regime.
2. **True Test Quality:** The agents noted that `pytest` passed 9 configs in 0.61s. However, none specifically analyzed whether those tests guard against ETF flow variables projecting `NaN` values back into 2021 regressions simply because ETFs didn't exist then. Test assertions need to validate historical zero-fill logic before listing.
3. **`project_research_plan.md` bloat:** Opus noticed it was 1,099 lines long, but none suggested condensing it down into an actual roadmap.
4. **Data Overwrite Immutability:** Does the pipeline append or destructively overwrite `Data/MASTER_DATA.csv` when run? No agent checked the ETL append logic in `tools/`. 

---

## 4. Unified Four-Paper Portfolio

### **Paper 1: Factor-Block Evolution Around ETF Institutionalization**
- **Category:** Institutionalization / Market-Evolution
- **Core question:** Did the composition of BTC/ETH factor loadings fundamentally change around the ETF launches, or is the dominant structural break still located in 2021 (pre-ETF)? 
- **Required data:** BTC/ETH Returns, FRED macro, Farside ETF flows, TradingView proxies. `Data/CryptoQuant` factor blocks.
- **Required methods:** Rolling OLS block contribution, true Bai-Perron or properly labeled sup-F tests, static OLS comparisons.
- **Kill risks:** Method labels mismatching actual stats code; overclaiming causality; weekend-return filling altering rolling matrices.
- **Disagreements:** Whether to use 8 vs 4 VAR variables (consensus: 4).
- **Estimated time:** 2-3 weeks to defensible v1.0. 

### **Paper 2: ETF Flow, Wrapper, Basis, and Plumbing**
- **Category:** Institutionalization / ETF-Adjacent Bridge
- **Core question:** How do ETF flows, issuer composition (IBIT vs GBTC outflow), and CME basis structures transmit price impact daily? 
- **Required data:** `Data/Farside ETF Data/` issuer flows, `Data/Artemis/` AUM files, CME Basis.
- **Required methods:** Distributed lags, T+1 reporting sensitivity, 4-variable VAR FEVD.
- **Kill risks:** Issuer time-series is extremely short (post-Jan 2024); daily data lacks intraday causality resolution.

### **Paper 3: Stablecoins as Shadow Settlement Liquidity**
- **Category:** Non-ETF Bridge (Liquidity Plumbing)
- **Core question:** Are stablecoin supply expansions replacing fiat broader monetary transmission pipelines for crypto-asset valuations? 
- **Required data:** `Data/DefiLlama/Stablecoins/`, CryptoQuant USDC/USDT exchange netflows, FRED rates. 
- **Required methods:** IRFs/Local Projections mapping FRED shocks to stablecoin supply to crypto returns.
- **Kill risks:** High endogeneity between Crypto returns causing Stablecoin supply (rather than vice-versa). 

### **Paper 4: DeFi Credit, Lending, and RWA Rate-Arbitrage**
- **Category:** Non-ETF Bridge 
- **Core question:** Are on-chain crypto lending yields and RWA volumes structurally anchoring to TradFi short term rates? 
- **Required data:** `Data/Artemis/Lending/` files, `Data/DefiLlama/RWA/`, FRED short-rates.
- **Required methods:** Weekly panel regression, RWA growth composition analysis. 
- **Kill risks:** Signal weakness/length — RWA is historically young, lending data is weekly. 

---

## 5. Unified Priority Fix List

| Priority | What it fixes | Flagged By | Recommend Implementer | Est. Effort | Dependencies | Acceptance Criteria |
|---|---|---|---|---|---|---|
| **P0** | **Governance Reconciliation** | All 3 | Human / Codex Agent | 1 day | None | `README`, `.cursor/rules`, `AGENTS.md` all reflect 4-paper portfolio. |
| **P0** | **ETF Flow Units** | All 3 | Opus/Codex Agent | < 1 day | None | Intensity uses Prior-Day Cap calculation inside `panel.py`. |
| **P0** | **Calendar & 5-Day Business Joins** | All 3 | Codex Agent | 2 days | None | Macro models strictly drop weekends. |
| **P1** | **Method Labeling** | All 3 | Opus Reviewer | < 1 day | None | Bai-Perron renamed to sup-F/Chow in drafts. |
| **P1** | **Build Metric Index** | All 3 | Gemini Agent | 2-3 days | None | `config/metric_dictionary.yml` defines the specific 30-40 features used. |
| **P2** | **Publication Figures (plotnine)** | Opus | Opus Agent | 3 days | Governance fixes | Paper 1 diagnostic visuals separated from high-quality ggplot-styled charts. |

---

## 6. Human Decisions Required

**Decision 1: Confirm the Four-Paper Portfolio Selection.**
- **Opus/Gemini:** Suggested a "DeFi vs CEX Structure" Paper.
- **Codex:** Suggested "DeFi Credit and RWA Arbitrage" because it aligns with verified data geometries. 
- **Recommended Default:** **Option A** (Accept Codex's RWA/Lending Paper 4, as it requires less mapping manipulation).
- **Fallback:** If not confirmed, pipeline defaults to single Paper 1 anchor.
- **Risk:** Dropping DeFi vs CEX leaves liquidity microstructure untested, but protects against "Not comparable" vendor errors.

**Decision 2: Maximum-Inventory (490 CSVs) Execution Route.**
- **Summarized:** Building a 5th paper out of all 490 feature columns is scientifically hazardous.
- **Recommended Default:** **Option A** (Mandate the 490 CSV base exclusively acts as a Data Atlas/Platform foundation powering the four tight papers, not a paper itself).
- **Fallback:** Unsupervised overfitted analysis papers.
- **Risk:** Eliminates the opportunity to publish an "Atlas of Crypto." 

**Decision 3: Structural Break True Implementation (R-Bridge vs Text Relabel).**
- **Gemini:** Import `strucchange` via R into Python pipeline.
- **Codex:** Reject R dependencies. Fix the drafting text to accurately reflect what is built (Chow / sup-F).
- **Recommended Default:** **Option A** (Accept Codex's rule -> Change the draft text. Do not introduce R bridges). 
- **Fallback:** Implement pure-python `ruptures` search.

**How to Respond:**
Please respond with your choices in this format:
- "Decision 1: Option A."
- "Decision 2: Option A."
- "Decision 3: Option A." 

Once received, I will map the approvals explicitly into the execution `NEXT_STEPS.md` artifact.

---

## 7. Multi-LLM Operating Model (Unified)

To effectively orchestrate this framework:

1. **Strategic Audit & Hard Implementation (Codex / GPT-5.4-Class):** 
   - Uses strict repo boundaries. Writes `pytest` constraints. Re-aligns calendar logic. 
2. **Review & Architecture / Hostile Referee (Claude Opus-Class):** 
   - Reviews Codex PRs. Red-teams paper drafting logic. Specifically scans for hallucinated causal associations (e.g., claiming "Flow caused Price").
3. **Data/Context Scanning (Gemini-Class):** 
   - Deep metadata inspection. Validates overlaps, searches for external DOI paper matches, handles fast parsing of the 490 CSV inventory blocks.
4. **Action:**
   - **Quality Gates:** No single LLM executes `src/` changes and drafts the resulting analysis simultaneously. Separating Church (Implementation) and State (Review/Drafting) resolves the hallucination loops flagged in prior-AI output.

---

## 8. Confidence Assessment

**[VERIFIED] / High Confidence (95%+):**
- The repo is thoroughly built for a single paper, but improperly labeled.
- `AGENTS.md` is vastly misaligned with `global-constitution.mdc` and the README.
- `Data/MASTER_DATA.csv` explicitly holds a 490 file boundary.
- The econometric flow/price scaling bug is mathematically confirmed.

**[UNCERTAIN] / Moderate Confidence (70%):**
- Can the Artemis Lending yield data proxy deeply enough into bridging TradFi macro without direct APR variables for Paper 4? (Requires execution to test statistical power).
- The exact distribution of `NaN` behavior inside Farside flow matrices over obscure 2024 banking holidays. Requires robust tests built in Phase 2.

**Quality Gate Handoff:**
- **Inputs read:** Opus Review, Gemini Audit, Codex Review, four\_paper\_protocols\_v0, data\_calendar\_metric\_strategy\_v0, multi\_agent\_workflow, p0\_execution\_backlog.
- **Outputs written:** `Manager/FINAL_ENHANCED.md`.
- **Claims made:** Governance is broken (Code: 1 paper vs Auth: 4 papers); AI hallucination models exist in cache; Method labeling is decoupled from code truths.
- **Confidence score:** 92%.
- **Open questions:** Pending Human Approval on the 3 decisions. 
- **Next agent:** Human Project Manager -> respond with decisions for NEXT_STEPS.md generation. 
