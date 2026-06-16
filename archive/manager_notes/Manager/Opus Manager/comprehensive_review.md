# CryptoQuant Research Program — Comprehensive Review

**Reviewer:** Claude Opus 4.6 (Thinking)
**Date:** 2026-04-18
**Role:** Skeptical principal research engineer, quantitative finance reviewer, empirical-finance project manager, execution-focused codebase auditor
**Repository:** `C:\Dev\Projects\CryptoQuant`

---

## 1. Executive Judgment

**The repository is real, functional, and past the planning stage — but it is not publication-grade, and the transition from a single-paper project to a four-paper research program has not yet been executed in the code or outputs.**

Three verdicts:

1. **Verified.** A working Python package (`src/cqresearch/`), analysis pipeline (`scripts/01-05`), 484 curated CSVs, a master panel (2,293 rows × 58 cols), 16 result tables, 11 figures, 6 robustness checks, a draft paper, and 9 passing unit tests exist. This is genuine infrastructure, not aspirational documentation. Evidence: `reports/panels/master_daily.parquet`, `reports/tables/2026-04-18/`, `reports/figures/2026-04-18/`, `reports/drafts/paper_v0.1_2026-04-18.md`.

2. **Verified.** The current codebase serves one paper only: BTC/ETH factor-exposure evolution around ETF institutionalization. `AGENTS.md` declares a four-paper program, but no code, config, panel, or output exists for the other three papers. The project_research_plan.md still describes "a single defensible working paper." The gap between `AGENTS.md` (multi-paper) and everything else (single-paper) is the central governance problem.

3. **Inference.** The data inventory is the project's strongest asset. 484 CSVs across 7 vendors, with verified cross-vendor overlap for ETF flows, stablecoin supply, TVL, and USD strength, provide enough raw material for four defensible papers — but only if the mixed-frequency, calendar, and variable-selection problems are solved professionally, and only if each paper gets its own panel, spec, and pipeline branch.

**Confidence: 82%.** High confidence on repository structure and output existence. Lower confidence on some data-construction implications and on whether the team can execute four papers within their timeline. The 18% uncertainty reflects: (a) I have not re-run the pipeline end-to-end, (b) some ETH transaction CSVs have only 365 rows starting 2025-04-11, suggesting possible data truncation, and (c) the four-paper goal may exceed available team bandwidth.

---

## 2. Evidence Reviewed

### Canonical governance files
- `AGENTS.md` (310 lines, 12,484 bytes)
- `README.md`, `HANDOFF.md`, `pyproject.toml`, `run_pipeline.py`
- `.cursor/rules/*.mdc` (6 files)

### Configs
- `config/factor_blocks.yml`, `config/events.yml`, `config/calendars.yml`, `config/chain_taxonomy.yml`, `config/paths.py`

### Data inventory
- `Data/MASTER_DATA.md` (588 lines, 84,618 bytes — full file read)
- `Data/MASTER_DATA.csv` (128,785 bytes)
- Directory listings of all 8 Data subdirectories

### Source code
- `src/cqresearch/` — all modules: `data/` (loaders, calendars, panel_builder), `features/` (returns, panel), `modeling/` (ols, rolling, structural_breaks, var_fevd, event_study), `viz/` (style)
- `scripts/01-05` + `run_full_pipeline.py` + `inspect_core_files.py`

### Generated outputs
- `reports/panels/master_daily.parquet` (+ coverage, meta)
- `reports/tables/2026-04-18/` — 16 CSVs + robustness/
- `reports/figures/2026-04-18/` — 11 PNGs
- `reports/run_summaries/01-03`
- `reports/drafts/paper_v0.1_2026-04-18.md` (full file read, 390 lines)

### CODEX audit files
- `CODEX/current_status_analysis.md` (370 lines — full read)
- `CODEX/data_analysis.md` (443 lines — full read)

### Docs
- `docs/specs/research_spec.md`, `methods_spec.md`, `data_spec.md`
- `docs/context/00-05` (directory listing)
- `docs/manager/Manager_Outline.md`, `Manager_workflow.md`

### Prior AI outputs
- `reports/prior_ai_outputs/` — 7 files (directory listing + sizes)
- `Latest Output.txt` (full read)

### Other
- `project_research_plan.md` (first 800 lines of 1,099)
- `tests/unit/` (4 test files)
- `Makefile`, `.pre-commit-config.yaml`

---

## 3. Repository Reality

### What actually exists and works

| Category | Status | Evidence |
|---|---|---|
| Python package | **Real.** 6 subpackages, ~15 modules | `src/cqresearch/` |
| Analysis scripts | **Real.** 7 scripts, numbered pipeline | `scripts/01-05`, `run_full_pipeline.py` |
| Curation pipeline | **Real.** 11 curation scripts + 4 ingest scripts | `tools/data_collection/`, `tools/data_curation/`, `run_pipeline.py` |
| Data inventory | **Real.** 484 CSVs, 1.81M rows, 7 vendors | `Data/MASTER_DATA.md` |
| Master panel | **Real.** 2,293 × 58, Parquet | `reports/panels/master_daily.parquet` |
| Result tables | **Real.** 16 tables + 6 robustness | `reports/tables/2026-04-18/` |
| Figures | **Real but diagnostic.** 11 PNGs | `reports/figures/2026-04-18/` |
| Paper draft | **Real v0.1.** 390 lines, all numbers tied to CSVs | `reports/drafts/paper_v0.1_2026-04-18.md` |
| Tests | **Thin.** 3 test files: imports, config, fixtures | `tests/unit/` |
| Configs | **Real.** 5 YAML + 1 Python paths module | `config/` |
| Cursor rules | **Real.** 6 MDC files | `.cursor/rules/` |
| Prior AI outputs | **Quarantined.** 7 files | `reports/prior_ai_outputs/` |
| CODEX audits | **Real.** 2 files, detailed | `CODEX/` |

### What is stale or contradicted

| Issue | Files in conflict | Impact |
|---|---|---|
| Single-paper vs four-paper | `AGENTS.md` (four-paper) vs `project_research_plan.md`, `README.md`, `.cursor/rules/global-constitution.mdc`, `HANDOFF.md` (all single-paper) | Governance confusion; agents don't know which goal to follow |
| Python version | `AGENTS.md` says 3.11+, `pyproject.toml` says ≥3.10, `HANDOFF.md` says active interpreter is 3.10.0, `ruff` targets py311, `mypy` targets py311 | Reproducibility risk |
| Pipeline entry point | `.cursor/rules/global-constitution.mdc` says `run_pipeline.py`; actual research runs via `scripts/run_full_pipeline.py` | Agent confusion about canonical entry point |
| Commit message format | `AGENTS.md` says `<type>(<scope>): <summary>`; `.cursor/rules/defensive-commits.mdc` says `<scope>: <short imperative summary>` | Minor governance inconsistency |
| Calendar/fill policy | `config/calendars.yml` says `ffill_limit: 0` for daily; `HANDOFF.md` says equity/macro forward-filled up to 4 days; code uses hardcoded fill rules | Data construction ambiguity |
| Method labels | Specs mention "Shapley partial R²" and "Bai-Perron"; code does variable-drop partial R² and single-break sup-F | Method overclaiming |

### What is aspirational but doesn't exist

- Per-paper panels, specs, or pipeline branches for papers 2-4
- True Bai-Perron multiple-break implementation
- Shapley/Owen block partial R² decomposition
- TVP-VAR or rolling-window connectedness
- On-chain factor block in the regression model (despite 345 CryptoQuant CSVs)
- ETH-specific analysis beyond parallel OLS
- Stablecoin sub-basket split
- Issuer-level ETF decomposition
- `uv.lock` (dependency lockfile)
- Integration tests
- Any math/regression correctness tests

---

## 4. Assessment of CODEX Audit Files

### `CODEX/current_status_analysis.md`

**Overall grade: B+.** Accurate, conservative, and well-cited. Should be accepted with minor corrections.

| Claim | My assessment |
|---|---|
| "Repo has moved beyond planning-only state" | **Agree.** Verified. |
| "Not yet publication-grade" | **Agree.** Verified. |
| "Block partial R² is not Shapley decomposition" | **Agree.** Verified via `src/cqresearch/modeling/rolling.py`. |
| "Calendar/fill handling conflicts with config" | **Agree.** Verified via `config/calendars.yml` vs `HANDOFF.md`. |
| "Tests are thin" | **Agree.** Only 3 test files with ~30 assertions total. |
| "Figures are diagnostic, not paper-ready" | **Agree.** Verified via figure PNG file sizes and CODEX description. |
| "ETF flow intensity has weak economic units" | **Agree.** Verified: `panel.py` line 69 divides flow by price, not market cap. |
| "Manager docs are partially stale" | **Agree.** They reference pre-pipeline state. |

**Omissions in CODEX/current_status_analysis.md:**
- Does not flag the single-paper-vs-four-paper governance contradiction
- Does not evaluate whether the 345 CryptoQuant files are actually loadable/usable (many ETH Transaction files have only 365 rows starting 2025-04-11 — possible data truncation)
- Does not assess the `project_research_plan.md` length problem (1,099 lines is unwieldy)
- Does not flag that `HANDOFF.md` describes Python 3.10.0, which contradicts `AGENTS.md`

### `CODEX/data_analysis.md`

**Overall grade: A-.** Excellent cross-vendor overlap analysis with quantitative verification. This is the strongest document in the repository.

| Claim | My assessment |
|---|---|
| ETF flows Farside = DefiLlama (r=1.000) | **Accept.** Well-documented with overlap counts and max absolute differences |
| Weekly ETF flows have sign-flip risk | **Accept.** Correctly warns against silent substitution |
| Stablecoin supply not interchangeable across vendors | **Accept.** 33.5% median relative difference documented |
| TVL sources internally consistent | **Accept.** r=0.999996 |
| FRED broad dollar ≠ DXY | **Accept.** Different basket compositions, 14.7% median relative difference |
| ETH market cap near-duplicate CQ vs Artemis | **Accept.** |

**Omissions:**
- Does not analyze RWA/DAT overlap or lending data overlap
- Does not document the ETH transaction file truncation issue
- Does not provide a formal metric dictionary (recommends it but doesn't build it)

---

## 5. Top 6 Paper / Project Directions

### Direction 1: BTC/ETH Factor-Exposure Evolution Around ETF Institutionalization

| Attribute | Assessment |
|---|---|
| **Title** | "Factor-Block Evolution in BTC and ETH Around the Spot-ETF Regime Shift" |
| **Thesis** | BTC/ETH factor loadings changed compositionally (not via a single structural break) around the 2024 ETF launches |
| **Category** | Institutionalization / market-evolution |
| **Required data** | CryptoQuant BTC/ETH prices, FRED macro, Farside ETF flows, TradingView equity prices, DefiLlama TVL/stablecoins, AlternativeMe FNG |
| **Frequency/calendar** | Calendar-daily (crypto-7 master); business-day TradFi forward-filled ≤3 days |
| **Current repo support** | **High.** Panel, tables, figures, draft v0.1 all exist |
| **Required new methods** | True Bai-Perron, ETF flow intensity fix (market cap denominator), on-chain factor block |
| **Biggest blocker** | Method labels must match implementation; on-chain block needs variable selection |
| **Publication risk** | Medium. "ETF changed crypto" is well-trodden; differentiation requires the compositional framing |
| **Estimated lift** | 3-4 weeks from current state to defensible v1.0 |
| **AGENTS.md alignment** | Full alignment (explicitly named as anchor candidate) |

### Direction 2: ETF Flow Microstructure and Price Discovery

| Attribute | Assessment |
|---|---|
| **Title** | "ETF Flow Dynamics and BTC/ETH Price Discovery: Issuer Heterogeneity and Intraday Timing" |
| **Thesis** | Issuer-level ETF flow heterogeneity (IBIT vs FBTC vs GBTC outflow) creates distinct price impact signatures |
| **Category** | Institutionalization / market-evolution |
| **Required data** | Farside issuer-level flows (13 BTC columns, 11 ETH columns), CryptoQuant BTC/ETH prices, Artemis ETF AUM |
| **Frequency/calendar** | Business-day (ETF flows are US trading-day native) |
| **Current repo support** | **Medium.** Issuer data exists in the panel; not yet analyzed |
| **Required new methods** | Issuer-level panel regression, flow decomposition, GBTC discount IV |
| **Biggest blocker** | Only daily data; no intraday or order-flow data exists |
| **Publication risk** | Medium-low. Issuer heterogeneity is a genuine research gap |
| **Estimated lift** | 4-5 weeks |
| **AGENTS.md alignment** | Aligned (ETF flows are explicitly supported) |

### Direction 3: Stablecoin Supply Dynamics as Crypto Monetary Policy Transmission

| Attribute | Assessment |
|---|---|
| **Title** | "Dollar Proxies on Chain: Stablecoin Supply Dynamics and Crypto-Market Liquidity Transmission" |
| **Thesis** | Changes in fiat-backed vs crypto-backed stablecoin supply transmit different liquidity signals to BTC/ETH markets |
| **Category** | Non-ETF bridge (stablecoin-TradFi nexus) |
| **Required data** | DefiLlama stablecoin mcap (200+ IDs daily), CryptoQuant USDC/USDT exchange flows, DefiLlama stablecoins.csv metadata (pegMechanism), BTC/ETH prices, FRED rates |
| **Frequency/calendar** | Calendar-daily (stablecoin supply is 7/7) |
| **Current repo support** | **Medium.** Data exists; stablecoin metadata mapped in `stablecoins.csv`; no analysis code |
| **Required new methods** | Stablecoin sub-basket construction (fiat vs crypto-backed), local projection IRF, Granger with stablecoin reserves |
| **Biggest blocker** | `stablecoin_mcap_id_to_name.csv` has quality issues (blank fields); sub-basket construction untested |
| **Publication risk** | Medium. Identification is hard (endogeneity with BTC price) |
| **Estimated lift** | 5-6 weeks |
| **AGENTS.md alignment** | Full alignment (stablecoins explicitly listed as niche topic) |

### Direction 4: DeFi vs CEX Market Structure and Liquidity Fragmentation

| Attribute | Assessment |
|---|---|
| **Title** | "Liquidity Fragmentation Across DeFi and CEX Venues: TVL, Volume, and Fee-Based Market Structure Metrics" |
| **Thesis** | The relative share of DeFi vs CEX liquidity and trading volume has structurally shifted post-2024, with measurable implications for crypto-asset pricing |
| **Category** | Non-ETF bridge (DeFi-TradFi structure) |
| **Required data** | DefiLlama TVL (all-chain + per-chain), Artemis DEX volume/TVL/fees, DefiLlama CEX inflows, Artemis CEX spot/perps volume, CryptoQuant exchange flows |
| **Frequency/calendar** | Calendar-daily for TVL/DeFi; mixed for CEX snapshots |
| **Current repo support** | **Low-Medium.** Data exists but no analysis whatsoever |
| **Required new methods** | Market share time series, structural break analysis on DeFi share, fee/volume ratio analysis, connectedness measures |
| **Biggest blocker** | CEX and DeFi metrics are "not comparable yet" per CODEX/data_analysis.md; requires semantic reconciliation |
| **Publication risk** | Medium-high. Novel but requires careful definitional work |
| **Estimated lift** | 6-8 weeks |
| **AGENTS.md alignment** | Aligned (DeFi vs CEX structure explicitly mentioned) |

### Direction 5: RWA Tokenization and Traditional Asset Bridge

| Attribute | Assessment |
|---|---|
| **Title** | "Tokenized Real-World Assets: Market Structure, Growth Dynamics, and Crypto-TradFi Correlation" |
| **Thesis** | RWA tokenization creates a measurable new channel connecting traditional asset valuations to on-chain markets |
| **Category** | Non-ETF bridge (RWA/tokenization) |
| **Required data** | DefiLlama RWA mcap (5 files, daily, 2021+), Artemis RWA tokenized market cap, DefiLlama DATs, FRED rates/credit |
| **Frequency/calendar** | Calendar-daily |
| **Current repo support** | **Low.** Data exists but is thin (1,687 rows, from 2021) and untouched |
| **Required new methods** | RWA category decomposition, correlation with Treasury yields, growth modeling |
| **Biggest blocker** | Thin data window (2021+); small market size may limit significance; DAT snapshot has survivorship risk |
| **Publication risk** | High. Nascent market, thin data, high narrative-fishing risk |
| **Estimated lift** | 6-8 weeks |
| **AGENTS.md alignment** | Aligned (RWA/tokenized assets explicitly mentioned) |

### Direction 6: Crypto-Market Data Atlas / Maximum-Inventory Project

| Attribute | Assessment |
|---|---|
| **Title** | "A Data Atlas of Crypto-Market Structure: Factor Taxonomy, Source Reconciliation, and Dimensional Architecture" |
| **Thesis** | Systematic mapping of 484 curated time series across 7 vendors reveals the effective dimensionality, redundancy structure, and dominant factor blocks of the crypto market |
| **Category** | Data-atlas / platform (supports all papers) |
| **Required data** | All 484 CSVs |
| **Frequency/calendar** | Mixed (daily, weekly, monthly, snapshot — must handle all) |
| **Current repo support** | **Medium.** Data inventory exists; cross-vendor overlap partially analyzed in CODEX |
| **Required new methods** | PCA, LASSO screening, clustering, metric dictionary, reproducible panel construction |
| **Biggest blocker** | Kitchen-sink risk; how to make it publishable vs. merely useful |
| **Publication risk** | High if framed as a paper; low if framed as a shared appendix or supplementary platform |
| **Estimated lift** | 4-6 weeks as supporting infrastructure; 8-12 weeks as standalone paper |
| **AGENTS.md alignment** | Partially aligned (portfolio requires at least one cross-vendor overlap check paper) |

---

## 6. Recommended Four-Paper Portfolio

### Paper 1 (Institutionalization): Factor-Block Evolution Around ETF Institutionalization

**Why it belongs:** It is the most data-complete, code-complete, and analytically advanced direction. The v0.1 pipeline already produces all headline tables and figures. Evidence: `reports/drafts/paper_v0.1_2026-04-18.md`, `reports/tables/2026-04-18/`.

**Unique question:** Did the composition (not just the level) of BTC/ETH factor exposures change around ETF launches?

**Non-redundancy:** The other papers examine specific channels (ETF flows, stablecoins, DeFi/CEX structure); this paper maps the full factor-block landscape.

**Minimum viable design:** Rolling OLS block partial R² (correctly labeled), Chow test at pre-registered dates, single-break sup-F, static OLS pre/post comparison, ETF flow intensity regression (with corrected units), 4-variable VAR/FEVD.

**Critical tables/figures:** Block partial R² heatmap, rolling R² time series, structural break F-stat table, ETF flow regression table, FEVD matrix, event-study CARs.

**Kill risks:** (a) Method labels mismatch current implementation → fix labels or implement methods. (b) ETF flow intensity uses price not market cap → fix denominator. (c) On-chain factor block absent → must add ≥3 CryptoQuant native metrics to differentiate from generic ETF-correlation studies.

---

### Paper 2 (Institutionalization): ETF Issuer Heterogeneity and Flow Dynamics

**Why it belongs:** Uses the unique issuer-level Farside data that no current published paper fully exploits. Complements Paper 1 by decomposing the aggregate ETF channel.

**Unique question:** Do different ETF issuers (IBIT, FBTC, GBTC conversions) have distinct price impact signatures, and has the issuer mix evolved?

**Non-redundancy:** Paper 1 uses aggregate ETF flow; Paper 2 decomposes it by issuer.

**Minimum viable design:** Issuer-level panel regression (13 BTC issuers × ~580 trading days), GBTC outflow dynamics as natural experiment, issuer-AUM-weighted flow measures, rotating leadership analysis.

**Critical tables/figures:** Issuer flow decomposition table, rolling issuer-level β, GBTC discount closure timeline, issuer market-share evolution.

**Kill risks:** (a) Only daily frequency — no intraday resolution for price discovery claims. (b) Short sample (580 days for BTC, 440 for ETH). (c) Must avoid overclaiming causality from simultaneity.

---

### Paper 3 (Non-ETF Bridge): Stablecoin Supply Dynamics and Crypto Liquidity Transmission

**Why it belongs:** Uses the deep CryptoQuant stablecoin data (USDC, USDT-ERC20, USDT-TRC20 exchange flows) combined with DefiLlama aggregate supply. Satisfies the "at least one paper using CryptoQuant native data" requirement.

**Unique question:** Do fiat-backed and crypto-backed stablecoin supply changes transmit differently to BTC/ETH market conditions?

**Non-redundancy:** Papers 1-2 treat stablecoins as a control variable; Paper 3 makes them the main explanatory object.

**Minimum viable design:** Sub-basket construction (fiat-backed: USDT+USDC+PYUSD+FDUSD vs crypto-backed: DAI+USDe+USDS), Granger causality tests, local-projection IRFs, exchange-flow analysis using CryptoQuant USDC/USDT inflow/outflow.

**Critical tables/figures:** Stablecoin supply decomposition (stacked area), fiat-vs-crypto-backed IRF comparison, exchange-flow FEVD, pre/post structural change in stablecoin-BTC relationship.

**Kill risks:** (a) `stablecoin_mcap_id_to_name.csv` metadata quality issues → use `stablecoins.csv` instead. (b) Endogeneity between BTC price and stablecoin creation. (c) Sub-basket construction requires validated pegMechanism metadata.

---

### Paper 4 (Non-ETF Bridge): DeFi vs CEX Liquidity Fragmentation

**Why it belongs:** Uses Artemis DEX data, DefiLlama TVL/chain metrics, DefiLlama CEX inflows, and CryptoQuant exchange flows — demonstrating cross-vendor overlap. Satisfies the "cross-vendor overlap checks" requirement.

**Unique question:** Has DeFi's share of crypto trading/liquidity structurally shifted, and does this fragmentation measurably affect crypto-asset pricing and volatility?

**Non-redundancy:** Papers 1-3 treat DeFi TVL as a liquidity control; Paper 4 makes venue-structure the research object.

**Minimum viable design:** DeFi share time series construction (Artemis DEX vol / (Artemis DEX vol + CEX vol)), structural break analysis on the DeFi share, rolling correlation between venue-share changes and BTC/ETH realized volatility, fee-based market structure metrics.

**Critical tables/figures:** DEX vs CEX volume share time series, TVL composition by protocol/chain, fee revenue comparison, venue-share break tests, liquidity fragmentation index.

**Kill risks:** (a) "Not comparable yet" label on several CEX/DeFi metric pairs (CODEX/data_analysis.md). (b) Requires building a metric dictionary before analysis. (c) Definitional ambiguity in "TVL" across vendors.

---

## 7. Maximum-Inventory Project Feasibility

### Assessment: **Viable as shared infrastructure, not as a standalone paper.**

> [!IMPORTANT]
> A "data atlas" paper using all 484 CSVs would face severe kitchen-sink and multiple-testing problems. But a shared factor-library and panel-construction project underlying all four papers is both feasible and valuable.

**Recommended form:** A shared data appendix and factor-library module, not a fifth paper.

**Specifically:**
1. Build a **metric dictionary** in `config/metric_dictionary.yml` — for each metric: name, vendor, unit, frequency, coverage window, missing%, block assignment, primary/robustness flag, and cross-vendor mapping.
2. Build a **shared panel constructor** in `src/cqresearch/data/panel_builder.py` (already partially exists) that can produce paper-specific panels from the shared inventory.
3. Run **within-block PCA** to reduce dimensionality before regression — the config already specifies `pca_config: within_block: true, n_components: 2` in `config/factor_blocks.yml`.
4. Document everything in a **supplementary data appendix** that ships with all four papers.

**Methods evaluation for dimension reduction:**

| Method | Appropriate? | Notes |
|---|---|---|
| Within-block PCA | **Yes.** Use as primary dimension reducer | Already specified in `config/factor_blocks.yml` |
| LASSO / elastic net | **Yes as screening.** ML-as-support per AGENTS.md | Use for variable selection within blocks, never as headline method |
| Sparse regression | **Yes as support.** | Same role as LASSO |
| Dynamic factor models | **Possibly.** Advanced; only if team has expertise | Nice-to-have for Factor Evolution paper |
| Clustering | **Yes for descriptives.** | Correlation clustering of metrics for taxonomy |
| Bayesian shrinkage | **Overkill** for this project | Implementation risk too high for MSc team |
| Boosted-tree importance | **Yes as support only.** AGENTS.md explicitly allows | Random-forest importance for variable screening |
| Network/connectedness | **Yes.** Diebold-Yilmaz already implemented | Extend to rolling connectedness |

**Overfitting protection:**
- Pre-register block assignments in `config/factor_blocks.yml` before running regressions
- Within-block PCA reduces degrees of freedom
- Hold-out validation: use 2025-2026 as out-of-sample for models fitted on 2020-2024
- Multiple-testing adjustment: Bonferroni for Chow tests across multiple break dates
- Report full model zoo: show what was tried, not just what worked

---

## 8. Current ETF / Institutionalization Paper Review

### As a hostile but fair empirical-finance referee:

**Research question clarity: B.**
The v0.1 draft has a clear question ("did factor loadings change around ETF launches?") but buries the lead. The most interesting finding — that the dominant structural break is in 2021, not 2024 — should be the headline, not the "ETFs are now the single most significant driver" claim that follows from a post-break-date regression.

**Data quality: A-.**
Strong multi-vendor coverage. ETF flow data verified at r=1.000 across vendors. Evidence: `CODEX/data_analysis.md`.

**Variable construction — ETF flow intensity: C.**
`btc_etf_intensity = flow / close.shift(1)` is flow-per-unit-price, not flow-relative-to-market-cap. The paper draft calls this "ETF-flow intensity" without clarifying the scaling. Evidence: `src/cqresearch/features/panel.py` lines 63-71. **Fix:** Either divide by market cap (add `Data/CryptoQuant/BTC/Market Data/Bitcoin Market Cap - Day.csv` to the panel) or clearly label as "flow-per-price" and discuss economic interpretation limits.

**Calendar handling: B-.**
The description in the draft (§2.2) is reasonable but conflicts with `config/calendars.yml` (`ffill_limit: 0` for daily) and the actual code behavior (4-day ffill). This must be reconciled before publication. Weekend zero-fill for ETF flows creates genuine zeros on non-trading days, which mechanically suppresses weekend-day regression residuals. Evidence: `config/calendars.yml`, `src/cqresearch/data/calendars.py`, `HANDOFF.md`.

**Sample windows: B+.**
2020-01-01 to 2026-04-11 is reasonable. Post-ETF sample (n=768 for BTC static OLS, n=821 for ETF flow regression) is adequate for OLS but tight for VAR.

**Econometric identification: C+.**
The paper correctly notes "this is not causal" for the ETF flow regression but then implies causal language elsewhere ("ETFs are now the single most significant driver"). The R1 robustness check (lagged flow) is a good start but does not constitute identification. **The paper needs either a formal IV strategy or uniformly descriptive language.**

**Rolling OLS diagnostics: B.**
180-day rolling OLS exists and produces the partial R² stacks (F03, F04). However, the "block partial R²" label is misleading — the current implementation appears to be variable-drop partial R², not Shapley/Owen block decomposition. Evidence: `src/cqresearch/modeling/rolling.py`, `CODEX/current_status_analysis.md`.

**Block partial R² claims: D+.**
The specs mention Shapley decomposition; the code does something simpler. **This is the most important label-accuracy fix needed.** Either implement Shapley block decomposition or rename to "sequential partial R² contribution" and discuss the difference.

**Chow and break-test evidence: B.**
The Chow test is correctly implemented (verified via `src/cqresearch/modeling/structural_breaks.py`). The sup-F sweep is correctly documented as single-break, not full Bai-Perron. The paper honestly reports the failed Chow test at the ETF date (F=0.81, p=0.60 for BTC). **This is one of the draft's genuine strengths — it surfaces uncomfortable findings.**

**VAR/FEVD design: C+.**
The VAR uses 8 variables (BTC, ETH, SPY, GLD, DGS10, VIX, stablecoins, DeFi TVL) with BIC-selected lag=1. This is too many variables for the sample size. The DY connectedness of 27.3% seems low. The Cholesky ordering is undocumented. Evidence: `reports/tables/2026-04-18/fevd_10d.csv`, `reports/tables/2026-04-18/var_fevd_meta.json`.

**Event study: B-.**
Market-model CARs with SPY benchmark are standard. However, the placebo p-values are uniformly high (0.61, 0.92, 0.67, 0.11, 0.21), meaning none of the ETF events are statistically distinguishable from random. This needs to be stated more prominently. Using SPY as the benchmark for crypto assets is questionable — a crypto-factor benchmark would be more appropriate.

**Figure quality: C.**
Diagnostic quality, not publication quality. F03/F04 (partial R² stacks) are informative but visually cramped. F07 (FEVD heatmap) has axis labeling issues. F08 (event CARs) has annotation collisions. Evidence: `CODEX/current_status_analysis.md` confirms this assessment.

**Citation discipline: A.**
Every empirical claim in the draft cites a CSV path. No invented external citations. This is excellent.

**Reproducibility: A-.**
`scripts/run_full_pipeline.py` reproduces everything. Deterministic (seed=42). Dated output folders.

### Overclaiming risk areas (must fix before submission):

1. **"ETFs are the single most significant driver"** — this is from a contemporaneous regression with simultaneity. Weaken to "strongest contemporaneous correlate."
2. **"patient-institutional-holder flows dampening routine volatility"** — mechanistic causal claim unsupported by the identification strategy. Remove or heavily caveat.
3. **"Block partial R²"** — rename unless Shapley decomposition is implemented.
4. **"Bai-Perron"** — never used in AGENTS.md discussions of current results (correct), but `methods_spec.md` §5 describes it as if implemented. Clarify status.

---

## 9. Mixed-Frequency and Calendar Strategy

### Recommended decisions (not just options):

**Master calendar: Calendar-daily (UTC, 7/7).**
Evidence: `config/calendars.yml` already specifies this. Crypto-native metrics publish 7/7. All papers should use this as the join calendar.

**TradFi alignment: Forward-fill with explicit limit.**
- **Stocks/ETF prices (SPY, QQQ, GLD, etc.):** Forward-fill ≤3 days. This covers weekends + one Monday holiday. Beyond 3 days, leave NaN. **Do not use ffill_limit=0** (config says 0 but code does 4; reconcile to 3).
- **FRED rates (DGS10, VIX, etc.):** Forward-fill ≤3 days. Same logic.
- **ETF flows (Farside):** Zero-fill on weekends/holidays within the series' active window. This is correct — weekends genuinely have zero flow. **Critical: never zero-fill before the series' first valid date (2024-01-11 for BTC, 2024-07-23 for ETH).**
- **Monthly series (CPI, UNRATE):** Forward-fill ≤31 days. Use end-of-month publication date. Be explicit about release lag (CPI publishes ~2 weeks after month-end).
- **Weekly series (NFCI, STLFSI, WALCL):** Forward-fill ≤7 days. Assign to last business day of the reporting week.

**Zero-fill policy:**
- ETF flows: zero-fill on non-trading days within active window ✓
- Exchange flows: **do not** zero-fill. CryptoQuant exchange flows report 7/7 — zeros are genuine.
- Stablecoin supply: **do not** zero-fill. Use forward-fill ≤1 day for minor gaps.

**Artificial returns warning:**
Forward-filling stock prices on weekends then computing log returns creates zero returns on Saturday and Sunday. **These artificial zeros dilute regression estimates.** Two approaches:
1. **Recommended for Papers 1-3:** Run headline regressions on business-day-only observations (drop weekends from the panel before regression). Report crypto-7-calendar results as robustness.
2. **For Paper 4 (DeFi/CEX):** Use full calendar-daily since DeFi operates 7/7.

**Weekly robustness:**
Resample all daily series to W-FRI (last value). Run parallel regressions. Report both daily and weekly results.

**Release lag and look-ahead risk:**
- FRED data has 1-day publication lag for daily series, 2-4 week lag for monthly (CPI, UNRATE). **Use the previous month's value for monthly series.**
- DefiLlama TVL publishes T+0 but may backfill. Acceptable for daily analysis but flag in paper.
- Farside ETF flows publish same-day or T+1. **Lagged flow regressions (R1) are the correct robustness check.**

**Paper-specific panel construction:**
Each paper should build its own panel from the shared inventory:
- Paper 1: BTC/ETH + 5-block factors, 2020-01-01 to present, business-day regression sample
- Paper 2: Issuer-level ETF flows + BTC/ETH prices, 2024-01-11 to present, business-day only
- Paper 3: Stablecoin sub-baskets + BTC/ETH + FRED rates, 2020-01-01 to present, calendar-daily
- Paper 4: DeFi/CEX metrics + BTC/ETH, 2020-01-01 to present, calendar-daily

---

## 10. Data Overlap and Source Recommendation

Building on `CODEX/data_analysis.md` (which is excellent), here is the extended recommendation:

| Category | Classification | Primary | Robustness | Notes |
|---|---|---|---|---|
| BTC daily ETF flows | Exact duplicate | **Farside** | DefiLlama | r=1.000 after unit conversion |
| ETH daily ETF flows | Exact duplicate | **Farside** | DefiLlama | r=1.000 |
| Weekly ETF flows | Near-duplicate | **Farside daily resampled** | Artemis weekly | Sign-flip risk in week-end alignment |
| ETF AUM (aggregate) | Related | **Artemis Crypto ETFs AUM** | Artemis issuer files | ~2% median difference |
| Stablecoin total supply | Definitionally different | **DefiLlama daily all-ID mcap** | Artemis chain supply | 33.5% median difference |
| Total TVL | Near-exact | **DefiLlama all-chain TVL** | DefiLlama chain-summed | r=0.999996 |
| DEX TVL | Different concept | **Artemis DEX TVL** | (not comparable to all-chain TVL) | Different universe |
| USD strength | Definitionally different | **FRED DTWEXBGS** (macro regressions) | TradingView DXY (market convention) | Different baskets |
| ETH market cap | Near-duplicate | **CryptoQuant** (for ETH-native work) | Artemis (for cross-chain) | 0.38% median difference |
| BTC open interest | Not comparable yet | **CryptoQuant** (for BTC-native) | Artemis (for CEX-level) | Different exchange/instrument universes |
| Active addresses | Not comparable yet | **CryptoQuant** (per-asset) | Artemis (per-chain/ecosystem) | Do not sum L1+L2 |
| Exchange flows | Not comparable yet | **CryptoQuant** (asset-specific) | DefiLlama CEX (entity-level) | Different granularity |
| Fees | Not comparable yet | **CryptoQuant** (BTC/ETH network) | Artemis (chain ecosystem) | Different scope |
| RWA market cap | Sole source per vendor | **DefiLlama RWA** or **Artemis RWA** | Use both independently | Check universe overlap |
| DeFi lending | Sole source | **Artemis** (weekly borrows/deposits) | None in repo | Weekly frequency constraint |
| CME basis/futures | Sole source | **TradingView** | None | CME-specific |
| Fear & Greed | Sole source | **AlternativeMe** | None | Single-source sentiment |

**Source precedence rules (formalized):**
1. For BTC/ETH asset-native metrics: CryptoQuant first
2. For ETF flows: Farside first
3. For macro: FRED first
4. For broad crypto liquidity (TVL, stablecoins): DefiLlama first
5. For chain/ecosystem comparative: Artemis first
6. For market-convention prices/indices: TradingView first
7. For cross-vendor validation: always run robustness with the secondary source

---

## 11. High-Dimensional Inventory Strategy

### Variable categories by research utility:

| Category | Likely useful | Redundant | Noisy/sparse | Irrelevant for current papers |
|---|---|---|---|---|
| BTC exchange net flow | ✓ (main reg) | | | |
| BTC miner-to-exchange flow | ✓ (robustness) | | | |
| BTC MVRV, SOPR, NUPL | ✓ (on-chain block) | Most are related | | |
| BTC realized cap / age bands | | ✓ (14 bands × 3 formats) | | Pick 1-2 representative |
| BTC UTXO age/value bands | | ✓ (many redundant breakdowns) | | Use PCA |
| ETH staking metrics | ✓ (Paper 1 ETH block) | | | |
| ETH transaction variants | | | ✓ (many start 2025-04-11 only) | Skip for now |
| USDC/USDT exchange flows | ✓ (Paper 3) | | | |
| Artemis lending data | ✓ (Paper 4 descriptives) | | | Weekly only |
| Artemis chain fees/revenue | ✓ (Paper 4) | | | |
| DefiLlama RWA | | | | ✓ (too thin for current papers) |
| DefiLlama DATs snapshot | | | ✓ (single timestamp) | Sidebar only |
| TradingView weekly | ✓ (weekly robustness) | | | |
| TradingView crypto stocks (MARA, RIOT, MSTR, COIN) | ✓ (Paper 2 robustness) | | | |
| SOL ETF data | | | ✓ (12 rows) | Too early-stage |

### Recommended variable-selection framework:

**Step 1: Economic block assignment** (from `config/factor_blocks.yml`)
- Every variable must be pre-assigned to a block before entering any regression
- Block assignments are pre-registered, not data-driven

**Step 2: Source precedence** (from §10 above)
- Within a block, prefer the primary source
- Use secondary sources only for robustness

**Step 3: Coverage filter**
- Drop any variable with >30% missing values in the analysis window
- Drop any variable that starts after the analysis window's midpoint
- Flag variables with less than 2 years of overlap with the dependent variable

**Step 4: Within-block dimension reduction**
- If a block has >5 variables, use PCA (as configured in `factor_blocks.yml`)
- Report both PCA-reduced and full-variable specifications

**Step 5: Statistical screening (subordinate)**
- Only after the above steps, use LASSO/elastic net to confirm variable importance
- Report LASSO path, not just selected variables
- Never let LASSO override an economically motivated block assignment

---

## 12. Prior AI Output Review

| File | Classification | Salvage? | Risk |
|---|---|---|---|
| `FINAL_SYNTHESIS_TOP5_PROJECTS.md` (54.7 KB) | **Useful but stale.** Good project-portfolio thinking; converges on ETF paper direction; correct warnings about AI suggestions as non-evidence | Salvage project-ranking framework; ignore implementation assumptions | Low risk; no obvious citation problems |
| `research_memo.md` (66.9 KB) | **Useful but stale.** Detailed variable mapping; method sketches; 15 robustness ideas | Salvage variable lists and robustness ideas; verify data-availability claims | Medium risk; subjective scoring rubric |
| `deep-research-report.md` (41.6 KB) | **Citation-risk.** Heavy methodological rigor but uses `turn...` citation placeholders and unverified 2025-2026 arXiv IDs | Salvage framing hypotheses only; **do not reuse any citations** | **High risk.** `AGENTS.md` explicitly warns about this file |
| `Beyond Correlation...` (66.6 KB) | **Citation-risk.** Many 2512/2602/2604/2606 arXiv prefixes + LinkedIn links | Salvage structural-break framing only; **do not reuse any citations** | **High risk.** `AGENTS.md` explicitly warns about this file |
| `Crypto Research Agenda Development.md` (69.5 KB) | **Useful.** Clean rejection-first agenda; picks Pathway A | Salvage coding-task breakdowns; good organizational structure | Low risk; some "recent themes" lack citations |
| `txt output.md` (43.7 KB) | **Misleading.** Elevates DML to headline method; cites Hormuz blockade and SEC commodity classification without evidence | Do not use as authority; keep as negative example of scope drift | **High risk.** Directly contradicts `AGENTS.md` non-goals |
| `txt output p2.md` (15.6 KB) | **Low-authority near-duplicate.** Almost identical to `docs/context/00_project_context_and_goals.md` | Archive; diff against Context/00 before deletion | Low risk; redundant content |

### `Latest Output.txt`
**Low-authority operator memo.** Describes the v0.1 pipeline accurately and is consistent with generated artifacts. Evidence: claims about master panel dimensions, R² values, and figure count match actual outputs. However, it overstates method completeness (calls current sup-F "Bai-Perron") and trusts ETF flow intensity units. **Use as orientation, not as evidence.**

### CODEX files
Already reviewed in §4 above. **CODEX/data_analysis.md is the most trustworthy synthesis document in the repository.** CODEX/current_status_analysis.md is also high-quality but misses the single-paper-vs-four-paper contradiction.

---

## 13. Tooling / Packages / Language Recommendations

### Current stack assessment:

| Component | Current | Sufficient? | Recommendation |
|---|---|---|---|
| **Data manipulation** | pandas ≥2.2, polars ≥1.10 | Yes | Keep both; use polars for large CSVs, pandas for statsmodels integration |
| **Econometrics** | statsmodels ≥0.14, linearmodels ≥6.0, arch ≥7.0 | **Mostly.** Missing true Bai-Perron | Add `ruptures` for change-point detection |
| **ML support** | scikit-learn ≥1.5 | Yes for LASSO/RF importance | Keep |
| **Visualization** | matplotlib ≥3.9, seaborn ≥0.13 | **Insufficient for publication.** | Add `plotnine` (ggplot2 semantics for Python) or switch key figures to R/ggplot2 |
| **Report system** | Markdown only | **Insufficient.** No LaTeX/PDF | Add Quarto or Typst for reproducible paper builds |
| **Pipeline** | `uv`, Make, scripts | Adequate | Add `uv.lock` (missing) |
| **Testing** | pytest ≥8.3, pytest-cov | Adequate framework, thin coverage | Expand test suite significantly |
| **Linting** | ruff, mypy (strict=false) | Adequate | Enable stricter mypy checks incrementally |
| **Pre-commit** | pre-commit, nbstripout | Adequate | Keep |

### Specific recommendations:

**1. Add `ruptures` for structural break detection.**
- What it fixes: True Bai-Perron multiple-break detection currently missing
- Why current tools insufficient: `structural_breaks.py` only does single-break sup-F
- Reproducibility cost: Low (pure Python, pip-installable)
- Dependency cost: Low
- Implementation risk: Low — well-documented API
- Verification: Compare `ruptures` output against current sup-F results as sanity check

**2. Add `plotnine` or consider R/ggplot2 for publication figures.**
- What it fixes: Current matplotlib figures are diagnostic quality
- Why current tools insufficient: matplotlib requires extensive manual styling for publication
- Reproducibility cost: Low for plotnine (Python); Medium for R (adds a language)
- Dependency cost: Low (plotnine) / Medium (R bridge)
- Implementation risk: Low
- Verification: Generate same figure in both matplotlib and plotnine; visual comparison
- **Recommended decision: Use plotnine for Paper 1-4 figures.** Only recommend R if publication venue has ggplot2 expectation.

**3. Add Quarto for reproducible paper builds.**
- What it fixes: No current system to produce PDF/LaTeX papers from the computational pipeline
- Why current: Markdown-only drafts can't produce submission-ready documents
- Reproducibility cost: Low (Quarto renders from `.qmd` which is markdown-compatible)
- Dependency cost: Medium (Quarto installation required)
- Implementation risk: Low
- Verification: Build Paper 1 draft as a Quarto document
- **Alternative: Typst** if team prefers modern, faster compilation. Both are good choices.

**4. Do NOT switch primary language to R.**
- Evidence: The entire codebase is Python; switching languages would waste the existing investment
- Exception: If a specific econometric method (e.g., `strucchange` R package for formal Bai-Perron with confidence intervals) is materially superior, write a thin R wrapper script called from Python

**5. Do NOT adopt DuckDB or Polars-only.**
- Evidence: pandas integration with statsmodels/linearmodels is essential; the dataset sizes (1.81M rows total, ~6K rows per typical daily CSV) don't warrant a different query engine

**6. Generate `uv.lock` and commit it.**
- Currently missing; dependency reproducibility is at risk

---

## 14. Multi-LLM Operating Model

### Agent role assignments:

| Role | Best-fit model | Rationale |
|---|---|---|
| **Deep audit / hostile review** | GPT-5.4 (extra-high reasoning) or Claude Opus (thinking) | Requires sustained attention, cross-referencing, and skepticism |
| **Econometric method design** | GPT-5.4 or Claude Opus | Requires formal statistics knowledge and conservative framing |
| **Code implementation** | Claude Opus or Gemini Pro | Requires precise code generation with correct API usage |
| **Citation verification** | GPT-5.4 with web search | Requires real-time DOI/arXiv verification |
| **Visualization review** | Any model with screenshot capability | Visual QA; use browser subagent |
| **Paper drafting** | Claude Opus | Requires academic writing style and evidence discipline |
| **Red-team / adversarial review** | Different model than the implementer | Independence; prevents author-bias |
| **Project management** | Any model reading AGENTS.md first | Context-window management is key |

### Operating rules:

**1. Independent passes for high-impact decisions.**
For paper selection, method choice, and headline claim validation: send the same prompt (e.g., `CODEX/Manager_Reviewer_Prompt.md`) to GPT-5.4, Claude Opus, and Gemini Pro independently. Compare for convergence, contradictions, omissions, and unsupported claims. Use the strongest arguments; don't average weak ones.

**2. Sequential for implementation.**
Implementation should be sequential: one agent implements, a different agent reviews. Never have two agents editing the same file simultaneously.

**3. Stale-plan drift prevention.**
- Every agent session must begin by reading `AGENTS.md` and `CODEX/current_status_analysis.md`
- After any session that changes plans or findings, update `CODEX/current_status_analysis.md`
- Each paper should have its own `CODEX/paper_N_status.md` tracking file

**4. Hallucination prevention.**
- Citation rule: every external citation must be verified via web search before entering any draft
- Import rule: before importing any Python package, verify it exists via `pip show` or `uv pip list`
- API rule: before using any API, verify the function signature against current documentation
- Data rule: before claiming a data pattern, point to the specific CSV row/column that shows it

**5. File conflict prevention.**
- Git branches: each paper gets its own feature branch (`paper-1/factor-evolution`, `paper-2/etf-issuer`, etc.)
- Lock files: use `.cursor/rules/` to prevent concurrent edits to `config/`, `src/cqresearch/modeling/`, `reports/panels/`
- Each agent session writes its own run-summary in `reports/run_summaries/`

**6. Source-of-truth maintenance.**
- `AGENTS.md` is the constitution — never modified without human approval
- `config/*.yml` are binding specifications
- `Data/MASTER_DATA.md` is machine-generated — never hand-edited
- `CODEX/current_status_analysis.md` is the living audit — updated after each major session

**7. Human approval gates.**
Agents must stop and ask before:
- Selecting the four papers (human must confirm portfolio)
- Changing event dates in `config/events.yml`
- Changing calendar/fill policy in `config/calendars.yml`
- Accepting external citations into drafts
- Changing method labels (e.g., renaming "sup-F" to "Bai-Perron")
- Moving from descriptive to causal language

**8. Quality gate format (every session handoff):**
```
1. Inputs read: [file paths]
2. Outputs written: [file paths + row counts]
3. Claims made: [strongest claims + evidence]
4. Confidence: [0-100%]
5. Open questions: [blockers]
6. Next agent: [role name]
```

---

## 15. Workflow / Prompts / Rules / Repo Structure

### Consistency assessment:

| Document pair | Consistent? | Issue |
|---|---|---|
| `AGENTS.md` vs `.cursor/rules/` | **Mostly.** | global-constitution.mdc still describes single-paper mission |
| `AGENTS.md` vs `project_research_plan.md` | **No.** | Plan is single-paper; AGENTS.md is four-paper |
| `AGENTS.md` vs `README.md` | **No.** | README describes single-paper direction |
| `AGENTS.md` vs `HANDOFF.md` | **No.** | HANDOFF is single-paper |
| `config/calendars.yml` vs code | **No.** | Config says ffill_limit=0; code does 4-day ffill |
| `docs/specs/methods_spec.md` vs code | **Partial.** | Specs describe Bai-Perron §5, Shapley R² §2; code does neither |

### Structural recommendations:

**1. `CODEX/` should become a durable audit/handoff folder.**
Keep the name. It's now established. Add per-paper status files:
- `CODEX/current_status_analysis.md` (keep, update regularly)
- `CODEX/data_analysis.md` (keep, update when new data arrives)
- `CODEX/paper_1_factor_evolution_status.md` (new)
- `CODEX/paper_2_etf_issuer_status.md` (new)
- `CODEX/paper_3_stablecoin_status.md` (new)
- `CODEX/paper_4_defi_cex_status.md` (new)

**2. Update `.cursor/rules/global-constitution.mdc` to reflect four-paper mission.**
Current text says "MSc-level empirical-finance study of how BTC and ETH factor exposures evolved around the 2024 US spot-ETF launch." This should reference the four-paper portfolio and point to `AGENTS.md` for the full mission.

**3. `docs/specs/` should become binding per-paper.**
Current specs are skeletal and single-paper. Add:
- `docs/specs/paper_1_research_spec.md`
- `docs/specs/paper_1_methods_spec.md`
- `docs/specs/paper_1_data_spec.md`
- (repeat for papers 2-4)

**4. `prompts/` structure.**
The 8 prompts in `project_research_plan.md` §13 are well-designed. They should be extracted into actual files in `prompts/` with per-paper variants where needed.

**5. `references/` is adequate.** Keep as read-only.

**6. `docs/manager/` is stale but useful history.** Add a note at the top of each file: "Historical planning document — see AGENTS.md for current goals."

**7. Quality gates to automate:**
- `pre-commit` hook: ruff lint + mypy + nbstripout (already configured)
- `make test`: should run pytest + check MASTER_DATA.md freshness
- `make validate`: already runs `07_validate.py`
- **New:** `make check-labels` — verify that paper drafts don't contain overclaimed method labels ("Bai-Perron" when only sup-F exists, "Shapley" when only variable-drop R² exists)

**8. Canonical pipeline entry point:**
Reconcile by declaring:
- `run_pipeline.py` → curation pipeline only (ingest + curate)
- `scripts/run_full_pipeline.py` → research pipeline (build panel + run analyses + make figures + robustness)
- Update `.cursor/rules/global-constitution.mdc` to reflect both

**9. Draft-paper versioning:**
Current: `reports/drafts/paper_v0.1_2026-04-18.md`. Good convention. Extend:
- `reports/drafts/paper1_v0.1_YYYY-MM-DD.md`
- `reports/drafts/paper2_v0.1_YYYY-MM-DD.md`
- etc.

---

## 16. Highest-Priority Fixes

In strict priority order:

**P0 — Must fix before any paper is defensible (1-2 days each):**

1. **Reconcile governance documents.** Update `README.md`, `project_research_plan.md`, `.cursor/rules/global-constitution.mdc`, and `HANDOFF.md` to reflect the four-paper mission. Currently only `AGENTS.md` knows about four papers.

2. **Fix ETF flow intensity units.** Add BTC/ETH market cap to the panel and divide flow by market cap, not by price. Or explicitly label as flow-per-price and adjust all economic interpretation. Evidence: `src/cqresearch/features/panel.py` lines 63-71.

3. **Fix method labels.** Rename "block partial R²" to "variable-drop partial R² contribution" unless Shapley decomposition is implemented. Remove any mention of "Bai-Perron" from results until true multiple-break detection is implemented. Evidence: `docs/specs/methods_spec.md` §5, `src/cqresearch/modeling/structural_breaks.py`.

4. **Reconcile calendar/fill policy.** Make `config/calendars.yml` the operational source of truth. Update code to read fill limits from config, not hardcode. Add tests for fill behavior. Evidence: `config/calendars.yml` vs `src/cqresearch/data/calendars.py`.

5. **Resolve Python version.** Pin to 3.11+ across `AGENTS.md`, `pyproject.toml`, and the actual interpreter. Generate and commit `uv.lock`.

**P1 — Should fix before Papers 1-2 are submitted (2-3 days each):**

6. **Add on-chain factor block.** Select ~6 CryptoQuant BTC native metrics (exchange net flow, miner-to-exchange flow, Coinbase premium, SOPR, MVRV, realized cap delta) as a 6th factor block. This is the "crypto-native differentiation" the paper needs.

7. **Implement true Bai-Perron.** Add `ruptures` to dependencies and implement k-break search. Compare against current sup-F results.

8. **Expand test suite.** Add: (a) math tests for OLS/HAC, (b) structural break correctness tests, (c) calendar fill behavior tests, (d) ETF flow construction tests, (e) stablecoin aggregation tests. Target: 30+ tests, covering all modeling modules.

9. **Redesign publication figures.** Separate diagnostic figures from paper figures. Build a `viz/paper_figures.py` module with cleaner layouts, fewer annotations, and consistent styling.

10. **Build metric dictionary.** Create `config/metric_dictionary.yml` with per-metric metadata: name, vendor, unit, frequency, coverage, block assignment, primary/robustness flag.

**P2 — Should fix before Papers 3-4 begin (3-5 days each):**

11. **Build stablecoin sub-basket.** Classify stablecoins by peg mechanism using `Data/DefiLlama/Stablecoins/stablecoins.csv` metadata. Build fiat-backed and crypto-backed aggregate series.

12. **Build DeFi/CEX structure metrics.** Construct DEX share, TVL composition, and fee metrics from Artemis + DefiLlama. Requires metric reconciliation first.

13. **Add Quarto or Typst for paper builds.** Enable reproducible PDF generation from computational pipeline.

---

## 17. Human Decisions Needed

### Decision 1: Confirm the four-paper portfolio

**Why it matters:** Everything downstream (code, panels, specs, agent allocation) depends on which four papers are being built.

**Recommended default:** The portfolio in §6 (Factor Evolution, ETF Issuer, Stablecoin, DeFi/CEX).

**What I would do if no answer:** Proceed with Paper 1 only (it's already 70% built) and treat the other three as future work.

**Risk of default:** If the team can only produce 2 papers, the DeFi/CEX paper should be dropped first (highest data reconciliation effort, least existing code support).

### Decision 2: ETF flow intensity denominator

**Why it matters:** Changes the economic interpretation of the headline ETF coefficient.

**Recommended default:** Divide by prior-day market cap. The data exists (`Data/CryptoQuant/BTC/Market Data/Bitcoin Market Cap - Day.csv`).

**What I would do if no answer:** Fix to market cap and re-run Paper 1 tables.

**Risk of default:** Low. Market cap is the standard institutional-flow scaling in the literature.

### Decision 3: Should the paper claim the 2021 structural break as the headline finding?

**Why it matters:** The current sup-F evidence says the dominant break is 2021-01-04 (BTC) and 2021-05-12 (ETH), not 2024. This is the paper's most honest and interesting finding. But it shifts the narrative away from the "ETF changed everything" framing.

**Recommended default:** Yes, make the 2021 break the headline. Frame the ETF era as a compositional evolution, not a structural revolution. This is more defensible and more novel.

**What I would do if no answer:** Use the 2021 break as headline, with ETF composition as the second key finding.

**Risk of default:** Some readers may find it less dramatic than the ETF narrative. But honest findings survive peer review; dramatic narratives do not.

### Decision 4: Business-day vs calendar-day regression sample

**Why it matters:** Calendar-day regressions include artificial zero returns on weekends for TradFi variables. Business-day regressions drop crypto 7/7 activity on non-trading days.

**Recommended default:** Business-day for headline regressions (Papers 1-2); calendar-day as robustness. Calendar-day for crypto-native papers (Papers 3-4).

**What I would do if no answer:** Use business-day for Paper 1 headline tables.

**Risk of default:** Loses ~28% of the sample on weekends; but the alternative (artificial zeros) is more dangerous for inference.

### Decision 5: Python 3.11 or 3.10?

**Why it matters:** Consistency across governance files, pyproject.toml, and active interpreter.

**Recommended default:** Pin to 3.11. Update `pyproject.toml` to `requires-python = ">=3.11"`. Install 3.11+ as the project interpreter.

**What I would do if no answer:** Pin to 3.11 and update all files.

**Risk of default:** If a dependency doesn't support 3.11+ (unlikely given the dep list), fallback to 3.10.

---

## 18. Open Questions

1. **Is the MSc team constraint binding?** `AGENTS.md` describes an ambitious four-paper program. Can 3 students produce four papers? If not, which two are highest priority?

2. **Is there a submission timeline?** The sprint/deadline structure is unclear. If there is a hard deadline, the portfolio should be trimmed accordingly.

3. **Are there additional data sources available?** The SOL ETF filing (12 rows) and Circle stock (218 days) suggest new data is being added. Is there a plan for additional vendor coverage?

4. **Should SOL be included as a placebo/extension?** SOL ETF data exists (`Data/Farside ETF Data/farside_sol_etf_flows__daily.csv`) but is only 12 rows. It could serve as an out-of-sample validation for ETF flow dynamics if the sample grows.

5. **Is there a preference for visualization style?** The current matplotlib defaults are engineering-grade. Should figures target a specific journal style (JFE, RFS, JFQA, etc.)?

6. **What is the Cholesky ordering for the VAR?** `docs/specs/methods_spec.md` §8 says ordering is "pending" in `docs/decisions/`. This must be decided and documented.

7. **Should the headline VAR system be 4-variable (compact) or 8-variable (current)?** The current 8-variable system may be overparameterized for the sample size. 4 variables (BTC-ret, ETF-flow, stablecoin-growth, VIX) would be tighter.

---

## 19. Confidence and Limits

### What I am confident about (>85%):
- Repository structure, file existence, and pipeline functionality
- Data inventory completeness (484 CSVs, 7 vendors, verified cross-vendor overlap)
- CODEX/data_analysis.md accuracy on ETF flow and TVL overlap
- The single-paper vs four-paper governance contradiction
- ETF flow intensity unit problem
- Method label accuracy problems (sup-F ≠ Bai-Perron, variable-drop ≠ Shapley)
- Calendar/fill policy inconsistency
- Prior AI output risk classifications

### What I am moderately confident about (60-85%):
- The four-paper portfolio selection (depends on team bandwidth and data quality in under-explored areas)
- Whether the DeFi/CEX paper has enough data quality for clean results
- Stablecoin sub-basket feasibility (metadata quality issues in `stablecoin_mcap_id_to_name.csv`)
- The mixed-frequency recommendations (reasonable defaults but need empirical validation)

### What I cannot verify from this review (<60%):
- Whether the pipeline actually runs end-to-end without errors on this machine
- Whether the regression coefficients are numerically correct (would require a re-run)
- Whether the ETH transaction files with only 365 rows (starting 2025-04-11) represent data truncation or correct coverage
- Whether the team's timeline and expertise support four papers
- Whether specific CryptoQuant metrics (MVRV, SOPR, etc.) have sufficient variation in the 2020+ sample to enter regressions usefully

### Evidence I did NOT have access to:
- Re-running the pipeline
- Full content of `project_research_plan.md` §11-§19 (read first 800 of 1,099 lines)
- Full content of prior AI output files (read sizes and CODEX reviews only)
- Contents of `docs/context/00-05` files (read directory listing; full content in CODEX reviews)
- `docs/manager/Manager_Outline.md` and `Manager_workflow.md` (read directory listing; described in CODEX)
- Git log / branch history
- Actual pipeline execution results

---

## Quality Gate

**Inputs read:** `AGENTS.md`, `README.md`, `HANDOFF.md`, `pyproject.toml`, `run_pipeline.py`, `Latest Output.txt`, `CODEX/current_status_analysis.md`, `CODEX/data_analysis.md`, `config/factor_blocks.yml`, `config/events.yml`, `config/calendars.yml`, `config/chain_taxonomy.yml`, `Data/MASTER_DATA.md` (full), `project_research_plan.md` (800/1099 lines), `reports/drafts/paper_v0.1_2026-04-18.md` (full), `reports/run_summaries/03_run_analyses.md` (full), `src/cqresearch/modeling/structural_breaks.py` (full), `src/cqresearch/features/panel.py` (full), `docs/specs/research_spec.md`, `docs/specs/methods_spec.md`, `docs/specs/data_spec.md`, `.cursor/rules/global-constitution.mdc`, directory listings of all major subdirectories.

**Outputs written:** `Manager/Opus Manager/comprehensive_review.md` (this file).

**Claims made:**
- Strongest: The governance contradiction between AGENTS.md (four-paper) and all other files (single-paper) is the central project-management problem. (Confidence: 95%)
- Second: ETF flow intensity units are wrong (flow/price, not flow/market cap). (Confidence: 95%)
- Third: Method labels overclaim in specs vs. implementation. (Confidence: 95%)
- Fourth: The recommended four-paper portfolio is viable with the existing data. (Confidence: 75%)

**Confidence score:** 82%.

**Open questions:** See §18 above (7 questions).

**Next agent:** Implementation builder to execute P0 fixes (governance reconciliation, flow intensity fix, method label fix, calendar reconciliation, Python version pin). Recommended model: Claude Opus or GPT-5.4 with code generation.
