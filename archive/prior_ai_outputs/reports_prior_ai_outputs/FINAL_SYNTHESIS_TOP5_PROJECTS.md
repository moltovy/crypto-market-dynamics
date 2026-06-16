# Final Synthesis & Top-5 Project Framework

**Prepared:** 2026-04-17
**Role:** Principal synthesis analyst / research adjudicator
**Purpose:** Single consolidated decision memo across the five model outputs (`research_memo.md`, `deep-research-report.md`, `Beyond-Correlation…md`, `txt-output-5.md`, `txt-output-p2-4.md`), cross-referenced against the data actually available in `MASTER_DATA-6.md`. This document is written to be the canonical brief that other agents/subagents (Cursor, Antigravity, etc.) will pick up and execute in parallel.

> **Rule of the house.** Frequency of repetition is not quality. A unique but strong idea is elevated. A widely repeated weak idea is still criticized. Everything below has been adjudicated, not averaged.

---

## 1. Executive Synthesis

**Center of gravity (real convergence, not cosmetic).** All five outputs — despite very different vocabularies — converge on a single flagship: a **factor-evolution / structural-break paper on BTC (and ETH) around the January 10, 2024 spot-ETF launch**, framed as *block-level explanatory reallocation* rather than causal price-prediction. Every model ranks some version of this at #1. The precise branding differs — "What the ETF Bought and What It Broke" (research_memo), "From Halving Cycle to Flow Regime" (deep-research), "Bitcoin's New Normal / TVP-VAR" (beyond-correlation), "Time-Varying Factor Blocks" (txt-5), "Institutionalization Revelation" (p2-4) — but the empirical object is identical: **how does the relative explanatory share of macro, institutional-flow, crypto-liquidity, and native on-chain blocks change around the ETF treatment window?**

**Real fault lines.** Four genuine disagreements survive synthesis:

1. **Method backbone.** research_memo + txt-5 + p2-4 favor conservative, transparent econometrics (rolling OLS, Bai-Perron, partial-R², Shapley-block, local projections). Beyond-Correlation centers on **TVP-VAR with stochastic volatility**. The conservative camp is methodologically safer; TVP-VAR is more powerful but harder to defend to a skeptical referee on sample-size grounds (~550 post-ETF trading days). **Verdict:** make the baseline conservative and use TVP-VAR as a robustness layer, not as the headline specification.
2. **BTC-only vs BTC/ETH comparative.** p2-4 leans BTC-only; everyone else argues for a BTC/ETH comparative design. The ETH ETF's later launch (July 23, 2024), stake-linked float dynamics, and different wrapper design provide a built-in natural-experiment structure. **Verdict:** BTC/ETH comparative is strictly dominant unless the team is tiny.
3. **Identification ambition.** deep-research and research_memo want real IV (issuer-idiosyncratic flows as supply shifter); Beyond-Correlation accepts reduced-form TVP-VAR; p2-4 settles for Chow/Bai-Perron. **Verdict:** IV belongs in the second paper (the flow-impact project), not the flagship. The flagship is a regime-reallocation paper, not a causal paper.
4. **Scope of the broader agenda.** Only research_memo offers a truly high-novelty non-ETF angle (DAT/MSTR premium collapse). Only deep-research offers a serious ETH-as-collateral angle. Only research_memo + deep-research take cash-and-carry transmission seriously. These unique contributions are not noise; they are the most interesting "side ideas" in the whole portfolio and should not be crowded out by the flagship.

**Portfolio shape.** Five parallel projects, with the flagship anchored and the other four chosen to (a) maximize distinctness from the flagship, (b) cover different risk/novelty profiles, and (c) each map cleanly to one subagent with a self-contained data slice.

---

## 2. Cross-Model Similarity Map

| Theme | research_memo | deep-research | Beyond-Correlation | txt-5 | p2-4 | Agreement quality |
|---|---|---|---|---|---|---|
| Post-ETF structural break in factor model | M1 (flagship) | #1 "Flow Regime" | Prop 1 TVP-VAR | M1 | Idea 1 (flagship) | **Substantive — all 5 pick same flagship** |
| ETF flow price impact / transmission | M5 (top-2) | #2 cash-and-carry | Prop 2 | M3 | part of Idea 1 | **Substantive — 5/5 flag it** |
| Stablecoins as macro-liquidity channel | M7, E13 | Track B #2 | Prop 3 | M4 | referenced | **Substantive — 4/5 flag as top-tier** |
| BTC/ETH comparative / asymmetry | M1 parallel | Track A #3 | implicit | M2, M8 | "ETH as placebo" | **Substantive — 4/5** |
| Liquidation / leverage cascade | M8 + E8 | absent | — | M5 | — | Partial — 2/5 strong |
| DAT / MSTR premium collapse | M3 + E10 fold | absent | absent | M7 (narrow) | absent | **Minority but uniquely strong (research_memo)** |
| Price discovery across venues / 24-7 | M4 (narrow) | "12/5 asset" | #9 | M3 hybrid | absent | Partial |
| On-chain conditional info content | M6 | implied | absent | subsumed in M1 | H3 of Idea 1 | Substantive but often folded into flagship |
| Staked-ETH as collateral | E5 (sub-block) | **Track B #1** | absent | M8/M10 | absent | Unique to deep-research |
| Geopolitical / China / sentiment | absent | absent | #6, #8, #10 | absent | absent | Unique to Beyond-Correlation — **weaker** |
| TVP-VAR as headline | absent | absent | Prop 1 + 2 | absent | absent | Unique to Beyond-Correlation — **medium strength** |

**Real agreement vs cosmetic:**
- The "post-ETF factor evolution" flagship is **real, substantive** agreement. All five outputs describe the same empirical object: block-wise explanatory reallocation with a sharp treatment date.
- "Stablecoins matter" is **real** agreement, but the models disagree on whether it is a separate paper (deep-research, Beyond-Corr, txt-5) or a companion/sub-block (research_memo).
- "ETF flow impact" agreement is **real** but blurry: some models treat it as reduced-form (txt-5), others as IV-identified (research_memo, deep-research).
- Agreement on "BTC is becoming more equity-like" is **mostly cosmetic** — everyone says it, but it is already over-documented in the 2025–2026 literature. The defensible contribution is block-level reallocation, not another correlation-creep chart.

---

## 3. Cross-Model Difference Map

### 3.1 Method: conservative econometrics vs TVP-VAR

**Disagreement.** Beyond-Correlation puts TVP-VAR with stochastic volatility at the center of its top two proposals. Everyone else treats rolling OLS + Bai-Perron + local projections as the main tool and leaves time-varying-parameter methods as at most a robustness check.

**Which is stronger.** The conservative camp wins. Reasons: (i) post-ETF sample is ~550 trading days — TVP-VAR with stochastic volatility is Bayesian and hungry for data; identifying time-variation from a short sample is exactly where its credibility is weakest; (ii) partial-R² / Shapley-block decomposition gives a cleaner mapping to the economic story ("which block gained explanatory share?") than TVP-VAR impulse responses, which will be noisier and less interpretable to a skeptical finance referee; (iii) Bai-Perron produces a testable break *date* — a headline result — while TVP-VAR produces a drifting coefficient plot that can always be called "a gradual process." **Use TVP-VAR only as a robustness layer, never as the main spec.**

### 3.2 BTC-only vs BTC/ETH comparative

**Disagreement.** p2-4 pushes BTC-only with ETH as placebo; all others want ETH as a co-treated asset, exploiting the 2024-07-23 ETH ETF launch as a natural second treatment.

**Which is stronger.** BTC/ETH comparative dominates. The later ETH ETF date creates a **staggered treatment design**, which directly neutralizes the most common objection to the flagship — "ETF launch is confounded with the April 2024 halving and a macro cycle." A staggered design lets you identify ETF-like effects from the ETH window that rule out BTC-halving explanations. Dropping ETH costs too much identification for too little simplification.

### 3.3 Identification ambition (reduced-form vs IV)

**Disagreement.** research_memo's M5 builds an issuer-idiosyncratic-flow IV; deep-research's #2 matches that spirit; Beyond-Correlation's Prop 2 uses ARDL/VAR with no causal identification; txt-5's M3 stops at distributed lags; p2-4 does not attempt causal identification.

**Which is stronger.** The IV-ambitious framing is stronger *for the flow-impact paper specifically* but **does not belong in the flagship**. Mixing a regime-change paper with a causal-identification paper makes both weaker. Keep them as two separate projects. The IV is defensible because cross-issuer idiosyncratic demand (the orthogonal component of each ETF's flow vs. the aggregate) is a credible supply-side shifter; the exclusion restriction is contestable but passes sensitivity analysis (Oster 2019).

### 3.4 Non-ETF angle: ETH-as-collateral vs DAT/MSTR vs stablecoins

**Disagreement.** Only deep-research elevates "Staked Ether as Collateral, Not Currency." Only research_memo elevates the DAT/MSTR premium collapse. Three of five elevate stablecoin plumbing.

**Which is stronger.** Each is defensible but they answer different questions. The DAT/MSTR paper is the **highest-novelty option in the entire portfolio** because the mNAV collapse (~4× → ~1.16 over 2024–2026) is a first-order 2025–2026 event and no peer-reviewed econometric work exists on it. Risk: n=1 cross-section (mitigated by Artemis DAT panel). The staked-ETH paper is conceptually elegant but endogeneity between price and staking rate is harder than it looks, and the "effective float" claim is not sharp. The stablecoin paper is safest and most replicable. **Portfolio choice:** run DAT/MSTR as a high-novelty subagent track, stablecoins as a safe-parallel subagent track, and integrate ETH-staking variables as a sub-block inside the flagship rather than its own paper.

### 3.5 Beyond-Correlation's unique ideas that should be rejected

Beyond-Correlation's #6 (news/sentiment with AI scores), #8 (Middle East March 2026 event study), #10 (China stimulus), #14 (Kalshi prediction markets), #15 (blockchain LLM agents) are **weaker** than any of the other four reports' candidate ideas. They either depend on data not in the inventory, rely on contestable narrative assumptions, or wade into crowded/thin literatures. **Reject as main projects.** Some (e.g., geopolitical event study) can sit as a sidebar/robustness check inside the flagship.

---

## 4. Top 5 Most-Mentioned Serious Ideas

| # | Short title | Models supporting (of 5) | Why recurring | Strongest form | Main weakness |
|---|---|---|---|---|---|
| 1 | **Post-ETF factor-block structural break (BTC + ETH)** | 5/5 | It is the empirical object everyone's data inventory is built for; the 2024-01-11 and 2024-07-23 treatment windows are now just long enough to identify | Block-wise partial-R² + Bai-Perron endogenous break + rolling Shapley-block with BTC/ETH staggered design; TVP-VAR as robustness | Short post-ETF sample (~550d BTC, ~430d ETH); break-date confounded with halving, macro cycle, Fed pivot |
| 2 | **ETF flow price impact with causal identification** | 5/5 (varying depth) | Headline practitioner β≈0.27 R²≈0.69 is econometrically sloppy and inviting rigorous work | Expected-vs-unexpected flow decomposition via ARIMA; issuer-idiosyncratic IV; Jordà local projections horizons 0–20; falsification on GLD + pre-ETF CME OI | Exclusion restriction on IV; reflexivity between price and flow |
| 3 | **Stablecoin shadow-money channel to crypto risk** | 4/5 | Stablecoin mcap ~$317B, BIS/IMF/ECB now treat as macro-financial; inventory is unusually deep here | Block-horse-race against ETF flows + macro, TVAR with VIX threshold, local projections to supply shocks, BTC vs ETH asymmetry | Stablecoin supply is endogenous to crypto demand; supply Δ is noisy liquidity proxy |
| 4 | **Liquidation-cascade event study + taxonomy (Oct-10-2025)** | 2/5 (strongly), 3/5 (partial) | Oct-10-2025 ($19–31B liquidated, ~86% long) is the cleanest natural experiment in recent crypto structure; 5 cascades available for pooled design | Single-event anatomy + 5-cascade pooled fixed-effects panel + pre-event leverage-warning logit + cross-cascade clustering | Small-n of cascades; event-day definition ambiguity; risk of "dashboard paper" feel without strong regime framing |
| 5 | **DAT / MSTR premium collapse and asymmetric beta** | 1/5 (primary), 1/5 (secondary) | Unique-but-strong. The mNAV compression from ~4× → ~1.16 is a first-order 2025–2026 event with no peer-reviewed econometric treatment | Multi-DAT panel from Artemis + Markov regime-switching β(MSTR, BTC) + industry-aggregate-dilution IV; n=1 risk addressed via panel | DAT-level granularity in Artemis must be verified week 1; reflexivity; MSTR-idiosyncratic confounds |

---

## 5. Best Unique / Under-Mentioned Ideas

These appeared only once (or weakly twice) but are strong enough to deserve elevation rather than burial:

1. **DAT / MSTR premium collapse (research_memo M3).** Highest-novelty item in the entire portfolio. Elevate to a standalone project (see §8, Project 5).

2. **Cash-and-carry / CME basis transmission mechanism (deep-research A2, research_memo adjacent).** Most ETF-flow work treats "price went up after flow" as the mechanism. The cleaner mechanism story is that ETF creations are absorbed by APs who hedge via CME short futures, compressing basis and drawing in cash-and-carry leverage — making CME basis, funding, and OI the true transmission channel. Elevate this to be *part of Project 2* (the flow-impact paper), not its own project.

3. **Coinbase Premium as AP-arbitrage footprint post-ETF (research_memo M12 + E15).** Sharp, publishable mechanism audit. Keep as a companion / robustness section inside Project 2.

4. **Basis vs. funding-rate divergence as institutional-vs-retail leverage wedge (research_memo E7).** Clean, novel, interpretable, and a pre-event warning signal for Project 4. Absorb into Project 4.

5. **Staked-ETH as collateral transformation (deep-research B1).** Real bridge to tradfi (float/carry/collateral). Reject as a standalone flagship (endogeneity is too heavy) but elevate the ETH-staking/LST/LRT variables into a dedicated **sub-block inside the flagship** (Project 1).

6. **On-chain conditional information content (research_memo M6).** The precise way to answer "did on-chain die?" Keep it as a **structural subsection of Project 1**, not a separate paper. Strongest form: Shapley-R² across 1d/1w/1m horizons with PCA-orthogonalized on-chain block.

---

## 6. Ideas to Reject or Downgrade

These all appeared with some prominence and should **not** drive the project:

| Idea | Source | Why rejected |
|---|---|---|
| Options "equity-ification" / put-skew (research_memo M9) | research_memo | DVOL-only data (no surface); headline claim needs 25-Δ skew / term structure; drop unless Deribit API is added |
| RWA growth → crypto beta compression (txt-5 M11, research_memo-adjacent) | txt-5, research_memo | Mechanism is indirect; RWA mcap is too small and too recent; likely spurious |
| Unified connectedness across all blocks (txt-5 M12, research_memo M2 pure form) | txt-5, research_memo | Close to methodology-for-its-own-sake; variable selection becomes the paper; fragile |
| News/social-media sentiment with AI-generated scores (Beyond-Corr #6) | Beyond-Correlation | Reliable AI-sentiment data not in the inventory; circularity with price; crowded in 2025 literature |
| Middle East / China / geopolitical event studies (Beyond-Corr #8, #10) | Beyond-Correlation | Single-event, narrative-dependent, confounded with macro; reviewers will push back |
| Prediction-market forecasts of crypto vol (Beyond-Corr #14) | Beyond-Correlation | Kalshi / Polymarket data not in inventory; off-topic |
| LLM agentic trading (Beyond-Corr #15) | Beyond-Correlation | Misplaced entirely — framework-development paper, not data research |
| Fragmented dollar liquidity across chains (deep-research B4) | deep-research | Cannot separate "fragmentation" from "product-market fit"; identification too hard |
| CEX→DEX stress migration (deep-research B5, txt-5 E6) | deep-research, txt-5 | Without order-book/slippage data, it becomes a dashboard paper |
| Bitcoin "12/5" asset hypothesis (deep-research A5) | deep-research | Needs intraday data we do not have; keep as robustness sidebar |
| Pure ML return-prediction framing | (several as anti-example) | Violates the brief; easy to criticize; all outputs already reject this |
| Full decade macro-beta study (research_memo M10) | research_memo | Incremental novelty; use as a subsection inside Project 1 |
| EPU-attention mediation (research_memo M11) | research_memo | F&G-as-mediator is reverse-causal; narrow as side paper at best |
| Korea Premium retail benchmark (research_memo M12 full form) | research_memo | Requires USD/KRW FX not in inventory |

---

## 7. Final Ranked Synthesis

**Top 3 overall directions:**

1. 🥇 **Post-ETF Factor Reallocation (BTC + ETH staggered design)** — flagship. Wins because (a) 5/5 convergence is real, (b) the inventory is purpose-built for it, (c) the BTC/ETH staggered-treatment design neutralizes the halving-confound critique, (d) methodology is conservative and defensible, (e) the paper can absorb multiple side ideas (on-chain-conditional, cash-and-carry mechanism as mechanism-of-reallocation, staked-ETH sub-block) as robustness layers. Best use of every strong piece of the dataset.

2. 🥈 **ETF Flow Price Impact with Proper Identification (cash-and-carry transmission)** — best runner-up. Econometrically sharper than the flagship but narrower in scope. IV-identified flow impact + cash-and-carry mechanism + falsification tests. Strongest "second paper" in the portfolio.

3. 🥉 **Stablecoin Shadow-Money Channel** — safest non-ETF project. Bridges BIS/IMF/ECB stablecoin macro-financial literature to crypto asset pricing. Data inventory is unusually strong here.

**Single best overall direction:** **Project 1 (flagship)** wins. Reasons are stated above in §7 item 1. No other project uses as much of the inventory, has as clean a treatment date, or is as robust to reviewer challenge.

**Why the others are weaker as flagships:**
- Project 2 is cleaner econometrically but narrower and forces the paper to live or die on the IV exclusion restriction.
- Project 3 is safe but endogeneity is an open wound; it is a better second-author paper than a flagship.
- Project 4 (cascade event study) is event-window-bound and has less sustained theoretical weight.
- Project 5 (DAT/MSTR) is the highest-novelty but has the thinnest cross-section and the most idiosyncratic reviewer risk.

**Portfolio recommendation:** run all five in parallel with different subagents, because the marginal cost of parallelization is low given the shared data stack, and the portfolio is deliberately constructed so each project succeeds or fails on independent risks.

---

## 8. The Top-5 Project Framework (for parallel subagent execution)

Each project below is self-contained: an agent can pick one up and execute with just this document + `MASTER_DATA-6.md`. All projects use the same pre-built daily panel (to be constructed once and shared as a parquet) to avoid duplicated data-wrangling.

### Standing rules for every project

- **Language of claims.** "Explanatory share," "block-level reallocation," "transmission consistent with X." **Never** "causes," "predicts," or "strategy returns."
- **Frequency.** Daily is the default. Weekly as robustness. No intraday unless a project explicitly marks it conditional.
- **Standard error treatment.** HAC (Newey-West, 5-lag baseline, 10-lag robustness). Cluster-robust for panels. Bootstrap with 5,000 reps for partial-R² comparisons.
- **Block orthogonalization.** Within-block PCA first component as a compression option; report both raw-variable and compressed specifications.
- **Pre-registration.** Every project freezes hypotheses and robustness battery before econometrics begins. Commit a `PROTOCOL.md` with a git hash.
- **ML policy.** ML is allowed as a **diagnostic** (LASSO for variable screening, permutation importance for nonlinearity flags, SHAP as exploratory). ML **never headlines** a specification.
- **Sample convention.** 2020-11-01 → 2026-04-17 as common daily window for BTC/ETH (ETH's CryptoQuant starts 2020-11). BTC-only extension back to 2018-01 as robustness.
- **Treatment dates.** BTC spot ETF: 2024-01-11. ETH spot ETF: 2024-07-23. SOL ETF: 2025-10-31 (too short to anchor, use only as descriptive overlay).
- **Weekend convention.** Crypto trades 7 days; US equity / ETF flows / FRED trade 5. Friday close → Monday close for weekend-straddled events; explicit `is_weekend` flag retained.

---

### PROJECT 1 — Flagship

#### "What the ETF Bought and What It Broke": Structural Reallocation in the BTC/ETH Factor Stack (2020–2026)

**One-line thesis.** The January-2024 spot-BTC-ETF launch (and the staggered July-2024 spot-ETH-ETF launch) caused a **reallocation of explanatory share** across macro, institutional-flow, crypto-liquidity, on-chain, and derivatives factor blocks for daily BTC and ETH returns and realized volatility — *not* a wholesale transformation. The paper quantifies the reallocation, dates it formally, and documents which blocks gained vs. lost incremental explanatory power.

**Hypotheses (pre-registered).**
- **H1.** Equity-block partial-R² for BTC/ETH returns rises statistically significantly after 2024-01-11 (BTC) and 2024-07-23 (ETH), relative to a pre-2024 baseline.
- **H2.** On-chain-block partial-R² for BTC returns declines conditional on flow-block and derivatives-block controls, and this is larger for BTC than ETH.
- **H3.** Flow-block partial-R² is zero pre-treatment (by construction) and strictly positive post-treatment; the magnitude is larger for BTC than ETH at 6 months post-launch.
- **H4.** Endogenous Bai-Perron break dates for BTC fall within a ±30 trading-day window of 2024-01-11; for ETH, within a ±30 trading-day window of 2024-07-23.
- **H5.** On-chain variables lose daily-horizon explanatory power but retain weekly and monthly explanatory power (horizon-heterogeneity).

**Dependent variables.** Daily log return of (BTC, ETH); 5-day realized volatility (RV5); 22-day RV; realized semivariance (downside). Weekly return as robustness.

**Factor blocks (pre-specified — freeze before modeling).**
1. **Macro / rates / liquidity.** ΔDGS10, ΔDGS2, ΔDFII10, ΔDXY, ΔVIX, ΔHY-OAS, NFCI, ANFCI, ΔWALCL, ΔRRP, ΔWTI. Source: `FRED/`, `Tradingview/Daily/DXY`.
2. **Equity.** SPY, QQQ, SMH, XLK, IWM, ARKK daily excess return. Source: `Tradingview/Weekly/` (filter for daily entries) + add SMH/XLK/ARKK if listed.
3. **Flow / institutional.** Daily net BTC ETF flow (total, Farside), daily net ETH ETF flow, ΔETF AUM, ΔDAT BTC holdings, IBIT NAV-premium, ETHA NAV-premium, SSR. Source: `Farside ETF Data/`, `Artemis/Bitcoin ETFs AUM.csv`, `Artemis/Ethereum ETFs AUM.csv`, `Artemis/BTC DATs - Bitcoin Count.csv`, `CryptoQuant/BTC/Flow Indicator/Bitcoin Stablecoin Supply Ratio (SSR) - Day.csv`.
4. **On-chain (BTC).** MVRV-Z, aSOPR, NUPL, Puell, exchange netflow (total), miner outflow, realized-cap UTXO age bands, Coinbase Premium Gap, Fund Holdings Δ. Source: `CryptoQuant/BTC/Market Indicator/`, `CryptoQuant/BTC/Exchange Flows/`, `CryptoQuant/BTC/Fund Data/`.
5. **On-chain (ETH).** Analogous ETH metrics from `CryptoQuant/ETH/`; plus ETH staking rate, total staked, LST/LRT TVL from `Artemis/Liquid Staking - LST TVL (USD).csv`, `Artemis/Liquid Restaking - LRT TVL (USD).csv`.
6. **Derivatives.** Funding rate, OI change, leverage ratio, taker CVD, DVOL change (post-2021), CME basis (BTC and ETH from 2021-02). Source: `CryptoQuant/BTC/Derivatives/`, `CryptoQuant/ETH/Derivatives/`, `Tradingview/Daily/` CME continuous.
7. **Sentiment.** Fear & Greed, USEPUINDXD, DVOL level.

**Frequency / sample.**
- Daily comparative sample: 2020-11-01 → 2026-04-17 (~1,350 trading days; split 800 pre-BTC-ETF / 550 post).
- BTC-only extension: 2018-01-01 → 2026-04-17 as robustness.
- ETH treatment window: 2024-07-23 as second treatment in staggered design.

**Baseline model family.**
- Block-wise OLS with HAC-Newey-West (5-lag). Compute full-model R² and each block's partial-R² (Shapley-Owen style, bootstrap 5,000 for CIs).
- Pre/post split at 2024-01-11 (BTC equations), 2024-07-23 (ETH equations). Difference-in-partial-R² with bootstrap CIs.
- Rolling 126-day block-R² dashboard.

**Structural-break family.**
- Chow test at pre-specified candidate dates (2023-10-16 ETF-speculation peak, 2024-01-11 launch, 2024-03 IBIT-inflow peak, 2024-07-23 ETH launch, 2024-04-19 halving).
- Bai-Perron with 0–5 endogenous breaks, BIC-selected.
- Quandt-Andrews sup-F with unknown break date.
- CUSUM-OLS on each factor-block coefficient.

**Robustness family.**
- Weekly-frequency replication.
- MIDAS with monthly CPI/UNRATE entering the daily regression.
- Block orthogonalization via within-block PCA (first-1, first-3 PCs).
- Horizon-heterogeneity: redo the partial-R² decomposition at 1-day, 5-day, 22-day horizons (tests H5).
- Placebo break dates (2023-07-01, 2022-11-09 FTX) — should not produce equivalent breaks.
- TVP-VAR(1) as a secondary robustness specification (small system: ΔBTC, ΔETH, flow, macro PC1, on-chain PC1, derivatives PC1).
- Sensitivity via Oster (2019) on any residually-identified claims.

**Acceptable supporting ML.** LASSO within-block for sparsity / redundancy check. Permutation importance on a non-linear booster as nonlinearity flag only.

**Charts / tables (headline).**
- **Table 1.** Block partial-R² pre vs. post (BTC equation, ETH equation) with bootstrap CIs and Δ-in-R² test p-values.
- **Table 2.** Bai-Perron endogenous break dates + confidence bands, BIC-selected # breaks.
- **Figure 1.** Stacked rolling 126-day block-R² (area chart) for BTC and ETH.
- **Figure 2.** Coefficient trajectories (κ_flow, κ_SPY, κ_DXY, κ_funding, κ_MVRV) over time with treatment markers.
- **Figure 3.** Horizon-heterogeneity Shapley decomposition (1d / 5d / 22d) for on-chain block.
- **Figure 4.** Placebo break-date null distribution vs. actual.

**Empirical workflow (week-by-week).**
1. Week 1: Data audit & panel construction. Verify every CSV path in `MASTER_DATA-6.md`. Stationarity tests (ADF/PP/KPSS) on every candidate series. Freeze block membership. Write `PROTOCOL.md` with H1–H5 and the full robustness list. Commit.
2. Week 2: Full-sample OLS baseline + pre/post split regressions. Compute block partial-R². Bootstrap CIs.
3. Week 3: Structural-break estimation (Chow, Bai-Perron, Quandt-Andrews). Rolling 126-day dashboard.
4. Week 4: ETH parallel. Staggered-treatment tables.
5. Week 5: Horizon-heterogeneity (tests H5). MIDAS. Weekly replication.
6. Week 6: Placebos + TVP-VAR robustness. Oster sensitivity.
7. Week 7: LASSO / permutation-importance diagnostic appendix.
8. Week 8–10: Writing + iterate. Produce 4 headline figures and 2 main tables.

**Contribution vs. 2025–2026 literature.**
- Extends [Tandfonline 2026 rolling-correlation decoupling](https://www.tandfonline.com/doi/full/10.1080/23322039.2026.2625541) with formal partial-R² block decomposition.
- Formalizes the 21Shares / VanEck "on-chain is weakening" practitioner claims.
- Staggered BTC/ETH design neutralizes halving confound — a defect in most 2024 event studies.
- First econometric use of BTC-DAT-inclusive flow block + CryptoQuant-native on-chain block in the same regression.

**Likely criticisms + defense.**
- "Post-ETF sample too short." → HAC, bootstrap, and the staggered ETH window give a second treatment with independent sample.
- "Halving and macro-cycle confound." → Placebo break dates at 2023-07 and 2022-11, plus ETH window at 2024-07 (no halving confound).
- "Mechanical correlation of MVRV-type on-chain with price." → Orthogonalize on-chain block via PCA; report Δ-in-R² on orthogonal block.
- "Multiple testing over break dates." → Bai-Perron's joint test; Bonferroni over Chow candidates.

**Feasibility 9 / Novelty 7 / Publication defensibility 9. Composite 8.4.** **PURSUE as flagship.**

**Suggested subagent.** `agent-project-1` or `cursor-agent-01`. Pre-load: Python (statsmodels, linearmodels, `ruptures` for Bai-Perron, `arch` for HAC).

---

### PROJECT 2 — Best Runner-Up

#### "Flow Impact, Properly Identified": ETF Flows, Cash-and-Carry, and BTC Price Transmission (2024–2026)

**One-line thesis.** The headline OLS estimate of BTC price elasticity to cumulative ETF flow (β ≈ 0.27, R² ≈ 0.69) overstates the causal contemporaneous impact because flows are endogenous to prices. Using (i) expected-vs-unexpected flow decomposition, (ii) issuer-idiosyncratic flow as an IV, and (iii) Jordà local projections, we identify a lower but still economically meaningful price impact that peaks at 3–7 trading-day horizons and transmits substantially through the CME cash-and-carry channel (basis compression + funding adjustment + OI expansion) rather than through direct spot absorption alone.

**Hypotheses (pre-registered).**
- **H1.** OLS contemporaneous β is biased upward relative to IV β.
- **H2.** Local-projection IRFs peak at horizon 3–7 days, not horizon 0.
- **H3.** A positive ETF-flow innovation compresses CME basis within 3 days and raises OI within 5 days, consistent with cash-and-carry scaling.
- **H4.** Price impact is larger in high-VIX and drawdown regimes (state-dependent transmission).
- **H5.** Coinbase Premium Δ is mechanically related to IBIT NAV-premium Δ and issuer flow Δ post-ETF (AP-arbitrage mechanism).

**Dependent variables.** BTC daily log return; Δ CME BTC basis (continuous front-month - spot); Δ OI (total, all exchanges); funding rate; Coinbase Premium Gap; 5-day RV.

**Factor blocks.**
- Primary: total BTC ETF net flow (Farside); issuer-level flows (IBIT, FBTC, ARKB, BITB, HODL, BTCW, EZBC, BTCO, BRRR, GBTC — from `Farside ETF Data/`).
- Expected flow via ARIMA(p,d,q), Kalman filter with AUM state.
- Unexpected flow = ARIMA residual.
- Issuer-idiosyncratic flow = residual of each issuer's flow on aggregate-ex-that-issuer (e.g., `FBTC_flow ~ flow_total_excl_FBTC`).
- Controls: SPY return, ΔDXY, ΔVIX, ΔHY-OAS, ΔFunding, ΔOI lagged (for RHS separation).
- Placebo outcomes: GLD daily return; pre-ETF (2021–2023) CME BTC OI-Δ as pre-ETF analog.

**Frequency / sample.**
- Daily, 2024-01-11 → 2026-04-17 (main).
- Pre-ETF placebo window: 2021-01-01 → 2023-12-31 (for falsification).
- ETH parallel: 2024-07-23 → 2026-04-17.

**Baseline model family.**
- OLS with HAC (benchmark).
- Jordà local projections horizon 0–20 on both total flow and unexpected flow.
- 2SLS IV using issuer-idiosyncratic flow as instrument for aggregate unexpected flow. Report first-stage F (target ≥ 10, ideally ≥ 20).

**Robustness family.**
- Alternative ARIMA orders (p,d,q ∈ {0–3}).
- Kalman / state-space first stage as alternative expected-flow model.
- Oster (2019) bounds on β under hypothetical unobserved confounding.
- Heterogeneity: VIX-tercile, drawdown-regime, funding-regime cuts.
- ETH replication as out-of-sample validation.
- Falsification: run the same IV design on GLD — should produce null.
- Falsification 2: pre-ETF CME OI-change IV on pre-ETF BTC price — should produce null.

**Mechanism section (cash-and-carry + Coinbase-Premium AP-arb audit, absorbing research_memo E15).**
- Regress Δ-CME-basis and Δ-OI on unexpected flow (horizons 0–10).
- Regress Δ-Coinbase-Premium on IBIT-NAV-premium Δ + issuer flow Δ (tests H5).
- Report FEVD from a VAR{flow_innovation, basis, OI, price, funding}.

**Acceptable supporting ML.** XGBoost as an alternative first-stage expected-flow model (report as diagnostic). LASSO for lag selection in the ARDL robustness.

**Charts / tables (headline).**
- **Table 1.** OLS vs. IV β at horizon 0, 3, 7, 14, with first-stage F and Oster bounds.
- **Table 2.** Heterogeneity across VIX / drawdown / funding regimes.
- **Figure 1.** Local-projection IRF of BTC return to unexpected flow, horizons 0–20, with 95% CI bands.
- **Figure 2.** Mechanism — IRFs of basis, OI, funding to the same shock.
- **Figure 3.** Falsification — GLD and pre-ETF placebo IRFs.
- **Figure 4.** Coinbase-Premium decomposition: share explained by IBIT-NAV-premium vs. issuer-flow vs. residual.

**Contribution vs. literature.**
- First IV-identified estimate of ETF flow price impact in crypto.
- First peer-reviewable mechanism audit of the CME cash-and-carry channel post-spot-ETF.
- Directly addresses the sloppy practitioner β ≈ 0.27 claim.

**Criticisms + defense.**
- "Exclusion restriction for issuer-idiosyncratic flow is not watertight." → Oster bounds + falsification on GLD + falsification on pre-ETF CME OI + heterogeneity pattern consistency.
- "Post-ETF sample too short." → Jordà LPs are robust at horizons up to ~n/10; 550 days supports horizons ≤ 20.
- "Reverse causality: flows follow prices." → That is the whole point of the expected-vs-unexpected decomposition; report reduced-form regressions too.

**Feasibility 9 / Novelty 8 / Publication defensibility 9. Composite 8.7.** **PURSUE as second paper.**

**Suggested subagent.** `agent-project-2`. Pre-load: Python with `linearmodels` for IV, `statsmodels.tsa` for ARIMA & LP, `arch` for HAC. Provide the flow CSVs up front.

---

### PROJECT 3 — Safe Parallel

#### "Shadow Dollars": Stablecoin Supply as a Crypto-Native Liquidity Channel Separate from ETF Flows

**One-line thesis.** Stablecoin supply / transaction / exchange-balance dynamics operate as a **crypto-native liquidity channel** whose transmission to BTC/ETH returns and volatility is structurally distinct from ETF-flow transmission: ETF flows lead BTC spot and CME basis; stablecoin supply leads DEX volume, altcoin TVL, and funding. The two channels are **complements** in risk-on regimes and **substitutes** during stress.

**Hypotheses (pre-registered).**
- **H1.** Stablecoin-block partial-R² for BTC/ETH returns is strictly positive and non-subsumed by ETF-flow block post-2024.
- **H2.** In a horse-race regression, SSR and aggregate stablecoin mcap Δ retain their coefficients when added to a full ETF-flow + macro specification.
- **H3.** A TVAR with VIX threshold identifies regime-dependent transmission: in low-VIX, stablecoins and ETF flows are complements; in high-VIX, they act as substitutes.
- **H4.** Stablecoin impact is larger for ETH than BTC in normal regimes (DeFi-collateral channel).
- **H5.** The liquidity-complement-vs-substitute pattern is also visible between stablecoin-supply Δ and macro-liquidity proxies (WALCL, RRP-drawdown).

**Dependent variables.** BTC / ETH daily return; RV5; DEX spot volume; funding rate (both assets); CME basis.

**Factor blocks.**
- **Stablecoin block.** USDT supply Δ, USDC supply Δ, aggregate stablecoin mcap Δ (DefiLlama), stablecoin transaction volume (Artemis), P2P volume, SSR (CryptoQuant), exchange-stablecoin ratio (CryptoQuant), stablecoin active-address count.
- **ETF-flow block.** Total BTC/ETH ETF flow, AUM Δ.
- **Macro liquidity.** WALCL, RRP, SOFR-IORB spread, NFCI.
- **Equity / rates controls.** SPY, ΔDGS10, ΔDXY, ΔVIX.

**Frequency / sample.**
- Daily, 2020-11-01 → 2026-04-17. Main regime-split at 2024-01-11 / 2024-07-23.
- Weekly aggregation as robustness.

**Baseline model family.**
- VAR with Cholesky ordering: {macro → stablecoin supply → ETF flow → crypto prices} (tests transmission). Compute IRFs and FEVD.
- Block-horse-race OLS: regress BTC return on {stablecoin-block, ETF-flow-block, macro, equity}; report whether stablecoin-block coefficients survive.
- Granger block-causality tests.

**Robustness family.**
- Threshold-VAR with VIX-threshold (high vs. low stress) — tests H3.
- Local projections to large stablecoin supply shocks (top 5% of absolute daily Δ).
- Sub-period split: 2020-11 → 2023-12 vs. 2024-01 → 2026-04.
- ETH parallel.
- Smooth-transition VAR as alternative non-linear spec.
- Tether/Circle issuance-announcement event study as supplementary identification.

**Acceptable supporting ML.** Sparse PCA within the stablecoin block.

**Charts / tables (headline).**
- **Table 1.** Horse-race coefficients (stablecoin-block vs. ETF-flow-block) pre vs. post.
- **Table 2.** Granger block-causality F-statistics across regimes.
- **Figure 1.** IRFs — BTC return and DEX volume response to stablecoin-supply shock vs. to ETF-flow shock.
- **Figure 2.** FEVD pies — share of BTC / ETH / DEX / funding variance attributed to stablecoin vs. ETF-flow shocks, pre vs. post.
- **Figure 3.** TVAR regime-dependent IRFs (high-VIX vs. low-VIX).

**Contribution vs. literature.** BIS ([BIS stablecoin liquidity 2025](https://www.bis.org/publ/work1270.pdf)), IMF 2026, ECB 2025 papers treat stablecoins at the macro level. This paper translates that macro-financial framing to crypto asset pricing with an unusually rich crypto-specific dataset. Disentangling stablecoin vs. ETF-flow channels is new.

**Criticisms + defense.**
- "Stablecoin supply is endogenous to crypto demand." → Use Tether/Circle issuance announcements as event-study anchors; exchange-stablecoin-balance-ratio as a less endogenous proxy.
- "SSR is just the inverse of price." → Report both SSR-based and raw-supply-based specs; the raw-supply spec does not mechanically depend on BTC price.
- "Supply Δ is a noisy proxy." → PCA across supply, tx volume, and active addresses as a compressed block.

**Feasibility 8 / Novelty 7 / Publication defensibility 8. Composite 7.7.** **PURSUE as safe parallel.**

**Suggested subagent.** `agent-project-3`. Pre-load: Python `statsmodels.tsa.vector_ar`, `tsDyn` equivalent for TVAR (or custom), `linearmodels`.

---

### PROJECT 4 — Event-Driven High-Clarity

#### "Anatomy of a Cascade": The October 10, 2025 Liquidation Event + Cross-Cascade Taxonomy (2020–2026)

**One-line thesis.** The Oct-10-2025 cascade ($19–31B liquidated, ~86% long-side) is the largest natural experiment in crypto leverage dynamics since March 2020. Comparing it with four prior cascades (May-2021, Nov-2022 FTX, Mar-2023, Aug-2024) via a pooled event-study + unsupervised clustering reveals **two distinct cascade archetypes** — leverage-unwind and macro-shock — with different pre-event warning signatures (funding, OI, basis/funding divergence, leverage ratio).

**Hypotheses (pre-registered).**
- **H1.** Funding rate + leverage ratio + OI + CME-basis / funding divergence in the 60 days pre-event are jointly significant predictors of cascade occurrence (logit).
- **H2.** Post-event reconvergence time (half-life of funding, basis, DVOL) differs significantly between leverage-unwind and macro-shock archetypes.
- **H3.** Oct-10-2025 loads predominantly on the leverage-unwind archetype (ex ante ELR > 0.30, funding > 0.02%/day, long-skew liquidations).
- **H4.** Pre-event basis-vs-funding divergence (research_memo E7) is a stronger leading indicator than funding alone.
- **H5.** BTC-vs-ETH asymmetry: ETH suffers larger pre/post volatility amplification than BTC in the leverage-unwind archetype.

**Dependent variables.** BTC / ETH daily return; RV5 in a ±30-day window; funding rate; ELR; OI; DVOL level; CME basis.

**Event set.**
| Date | Short name | Pre-identified archetype (hypothesis) |
|---|---|---|
| 2021-05-19 | May-21 China-FUD cascade | Leverage-unwind |
| 2022-11-09 | FTX collapse | Macro-shock (credit) |
| 2023-03-10 | SVB / USDC depeg | Macro-shock (banking) |
| 2024-08-05 | Yen-carry unwind | Macro-shock (vol) |
| 2025-10-10 | **Oct-10-2025** | **Leverage-unwind (flagship event)** |

**Factor blocks.**
- **Pre-event leverage.** Funding rate, ELR, OI total, OI-by-exchange share, taker CVD, exchange-stablecoin ratio, CME basis, DVOL level.
- **Macro.** ΔVIX, ΔHY-OAS, ΔDXY.
- **Event.** Liquidation $USD total, long-liq share, time-concentration index.
- **Post-event.** Same as pre-event, plus ETF flow (post-2024 only).

**Frequency / sample.**
- Daily. ±60 trading days pre-event and ±30 post-event as standard windows.
- Full comparative sample 2020-01 → 2026-04.

**Baseline model family.**
- Matched-window event study with control windows drawn from day-of-week × vol-regime × funding-regime strata.
- Pooled cross-cascade fixed-effects panel regression: `response_t = α_event + β · pre-event leverage + γ · macro + ε`.
- Logit of cascade-occurrence on 30-day lagged leverage-panel — tests H1 & H4.
- Hierarchical clustering on event-window feature vectors (pre-event 60d means of funding, ELR, OI, basis, VIX, DXY, HY-OAS + event magnitude + post-event reconvergence times). Bootstrap cluster-stability.

**Robustness family.**
- Alternative event-day definition (max-liquidation-day vs. first 10% drawdown day).
- Cross-exchange heterogeneity (Binance / Bybit / OKX funding).
- Pre-ETF vs. post-ETF cascade-behavior split.
- Isolation-forest anomaly detection as alternative archetype labeler.

**Acceptable supporting ML.** Isolation-forest for anomaly detection on the full factor panel as an "systemic-stress index" companion (research_memo E12 absorbed). Hierarchical clustering is part of the main spec.

**Charts / tables (headline).**
- **Table 1.** Cascade-event feature table (5 rows × ~12 features).
- **Table 2.** Logit pre-event warning model coefficients (tests H1, H4).
- **Figure 1.** Five-event overlay: funding / ELR / CME basis / DVOL in ±60/30 windows.
- **Figure 2.** Hierarchical-clustering dendrogram of cascade feature vectors.
- **Figure 3.** Post-event reconvergence half-life by archetype (bar chart).
- **Figure 4.** Oct-10-2025 deep dive: intraday cascade timeline overlaid with pre-event funding / ELR anomaly flags.

**Contribution vs. literature.** Most post-mortems (Amberdata, FTI, Galaxy, Coin Metrics) are descriptive and single-event. This is the first pooled-event panel econometric treatment with pre-registered cascade archetypes and a quantified warning-signal framework.

**Criticisms + defense.**
- "n = 5 events is small." → Pooled fixed-effects with event-specific controls; report cluster-stability bootstrap.
- "Archetype labels are subjective." → Clusters are unsupervised (hierarchical + isolation-forest) before archetype names are attached.
- "Event-date definition is ambiguous." → Robustness across three date definitions.

**Feasibility 9 / Novelty 8 / Publication defensibility 8. Composite 8.3.** **PURSUE — strong, self-contained.**

**Suggested subagent.** `agent-project-4`. Pre-load: Python `scipy.cluster`, `statsmodels`, `sklearn.ensemble.IsolationForest`.

---

### PROJECT 5 — High-Novelty Contrarian

#### "Premium Collapse": The Digital Asset Treasury Premium and the Asymmetric Beta of MicroStrategy (2020–2026)

**One-line thesis.** The DAT premium (mNAV) collapse from ~4× at the 2024 peak to ~1.16 by March 2026 is the cleanest natural experiment in crypto-equity structure in years. MSTR's equity-return loading on BTC is structurally **asymmetric**: BTC × leverage on the upside but BTC × leverage × mNAV-compression on the downside. The mNAV compression itself is explained by (i) industry-wide DAT dilution pace, (ii) BTC drawdown regime, and (iii) equity-market risk appetite — **not by BTC level alone** — and is best understood as a crowded-issuance premium unwind, not a re-pricing of BTC credit risk.

**Hypotheses (pre-registered).**
- **H1.** MSTR's BTC-β is regime-dependent; Markov 2-state β estimates are significantly larger (in absolute value) in BTC-drawdown regimes than in trend regimes.
- **H2.** MSTR daily returns decompose approximately as `β_BTC · ret_BTC + β_mNAV · Δ(mNAV) + β_eq · ret_SPY + ε`.
- **H3.** Δ(mNAV) is explained by industry-DAT-dilution pace + BTC-drawdown-depth + ΔVIX + ΔHY-OAS, and **not** significantly by BTC-level.
- **H4.** Bai-Perron on mNAV identifies a break date in 2024-Q4 or 2025-Q1.
- **H5.** Comparator equities (COIN, MARA, RIOT, CRCL) do **not** display the same asymmetric β → mNAV-channel signature; the signature is DAT-specific.

**Dependent variables.** MSTR daily return; mNAV level and Δ; MSTR-BTC β (rolling 63-day). Secondary: MSTR realized vol, drawdown.

**Factor blocks.**
- **DAT universe.** MSTR + all Artemis DAT names (if DAT-level granularity is confirmed in week 1 from `Artemis/BTC DATs - Bitcoin Count.csv` + `Artemis/BTC DATs- Fully Diluted EV NAV.csv` + `Artemis/Artemis - Digital Asset Treasuries Overview.csv`). **Go/no-go gate:** if only aggregate DAT series is available, scope tightens to MSTR vs. aggregate-DAT-industry.
- **BTC.** Daily return, drawdown-depth (from 252-day peak), 30-day RV.
- **Equity / risk.** SPY, VIX, HY-OAS, DXY.
- **ETF flow.** Total BTC ETF flow (Farside).
- **Comparators.** COIN, MARA, RIOT, CRCL from `Tradingview/`.

**Frequency / sample.**
- Daily, 2020-08-10 → 2026-04-17 (DAT count starts 2020-08-10).
- Core analysis window: 2022-01-01 → 2026-04-17.

**Baseline model family.**
- Rolling 63-day OLS of MSTR return on BTC return, SPY return, Δ(mNAV) with HAC.
- Markov 2-state regime-switching regression on BTC-drawdown as the state variable.
- Bai-Perron on mNAV level, 0–3 breaks.
- Shapley decomposition of MSTR-return variance across {BTC, Δmnav, SPY, idiosyncratic}.

**Robustness family.**
- Alternative window lengths (30d, 90d, 126d).
- Hamilton filter as alternative regime model.
- Instrumented regression: **industry-aggregate DAT-count Δ (excluding MSTR itself) as IV for MSTR-specific mNAV Δ** — identifies the "crowded-issuance premium unwind" mechanism.
- Placebo regressions on COIN / MARA / RIOT — should produce null on the mNAV channel (tests H5).
- Event study around top 10 MSTR equity-issuance announcements.

**Acceptable supporting ML.** SHAP on a boosted regression of Δ(mNAV) on all regressors as exploratory variable importance only.

**Charts / tables (headline).**
- **Table 1.** Markov regime-switching β(MSTR, BTC) in drawdown vs. trend regimes.
- **Table 2.** mNAV decomposition: industry-dilution + drawdown + risk-appetite — with and without BTC-level (tests H3).
- **Figure 1.** mNAV timeline for top-5 DATs with break markers.
- **Figure 2.** MSTR vs. BTC scatter color-coded by drawdown regime (tests H1 visually).
- **Figure 3.** Rolling β decomposition — stacked area of β_BTC / β_mNAV / β_eq / residual.
- **Figure 4.** Placebo — comparator equities (COIN/MARA/RIOT/CRCL) run through same decomposition, showing null.

**Contribution vs. literature.** No peer-reviewed econometric treatment of the DAT-premium collapse exists. This paper produces (a) the first asymmetric-β decomposition for MSTR, (b) the first industry-dilution IV for mNAV, and (c) the first placebo-tested DAT-specificity claim.

**Criticisms + defense.**
- "MSTR is n=1." → Artemis DAT panel gives multi-entity cross-section; if panel is truly unavailable, the paper tightens to MSTR vs. aggregate-DAT.
- "Reflexivity — MSTR dilution affects BTC price." → Industry-aggregate-dilution-excluding-MSTR as IV isolates the idiosyncratic MSTR mNAV channel.
- "MSTR has idiosyncratic accounting / rating / convert-debt events." → Event-time fixed effects; event-window robustness around top-10 issuance dates.

**Go/no-go gate (Week 1).** Open `Artemis/BTC DATs - Bitcoin Count.csv` and `Artemis/BTC DATs- Fully Diluted EV NAV.csv`. If they provide DAT-level time series (not just aggregate), PROCEED. If only aggregate, narrow scope to MSTR + aggregate-DAT-industry, acceptable but weaker.

**Feasibility 7 (conditional) / Novelty 9 / Publication defensibility 8. Composite 8.1.** **PURSUE — highest-novelty, but start with the Week-1 gate.**

**Suggested subagent.** `agent-project-5`. Pre-load: Python `statsmodels` (regime-switching), `linearmodels` (IV), `ruptures` (Bai-Perron).

---

## 9. Integration Map: How the Five Projects Share the Dataset

**Shared deliverable (Week 1, cross-project).** A canonical daily parquet file `panel_daily_2020-11_2026-04.parquet` with all variables listed across the five projects, plus `PANEL_DICTIONARY.md`. All five subagents read from this single file. Built once, shared across all agents to avoid 5× redundant data wrangling.

**Project-level cross-coverage:**
- **Project 1 → Project 2.** The Project-1 "flow block" coefficient magnitudes feed Project 2's motivation (quantifies the bias the naive OLS misses).
- **Project 2 → Project 1.** Project 2's Coinbase-Premium AP-arbitrage audit is a mechanism footnote in Project 1.
- **Project 3 → Project 1.** Project 3's stablecoin-block coefficients should replace / augment Project 1's stablecoin variables — tighter internal consistency.
- **Project 4 → Project 1.** Project 4's pre-event leverage-warning logit is a figure in Project 1's robustness section.
- **Project 5 → Project 1 & 2.** DAT-industry flows can be a small additional block in Project 1's "flow block" and a supplementary instrument in Project 2.

**Shared robustness battery** (already covered within the projects): Bai-Perron, HAC, bootstrap CIs, pre/post splits, placebo outcomes, weekly aggregation, ETH parallels.

---

## 10. What the Outputs Collectively Missed

Things no model handled well that should be considered:

1. **Weekend / holiday microstructure.** Crypto trades 7 days; ETF flows and CME (pre-May-2026) are 5 days. All five outputs either ignored this or treated it as a robustness check. It should be a **first-class design choice**: every pre/post-ETF comparison must control for weekend-straddled return distribution changes. Add an `is_weekend`, `is_cme_closed`, and `Monday_reopen` flag to the panel.

2. **Look-ahead contamination in flow data.** Farside daily BTC ETF flows are reported T+1 with lag. All five outputs assume contemporaneous timing. This is a real sample-alignment issue that will bias IRFs at horizon 0. **Fix:** lag flow by one trading day in all regressions; report T-0 results as benchmark only.

3. **Survivorship in DAT panel.** The Artemis DAT list is current; DATs that delisted or collapsed (e.g., 2022 miners that accumulated BTC and then bankrupted) are not in the panel. Project 5 needs a survivorship-free construction or an explicit caveat.

4. **Miner / validator structural heterogeneity** is under-discussed. research_memo mentions it (M10, E6) but even there it is weak. Post-halving, miner selling is now a tiny fraction of daily volume; this fact is under-used in the flagship's mechanism for why on-chain factors lose explanatory share.

5. **Uneven sample starts within the "on-chain" block.** Several CryptoQuant ETH series start 2020-11; others start later. None of the outputs systematically audit each factor's available start date against the regression sample. This will bite — do it in Week 1.

6. **Multiple-hypothesis testing correction.** Four of five outputs (Beyond-Correlation excluded) ignore MHT correction over break dates + block coefficients + horizons. Use Bonferroni across horizon × block, or Romano-Wolf for the structural-break battery.

7. **No model flagged the DVOL data gap cleanly for the options-skew idea.** research_memo did flag it, but the options "equity-ification" headline claim (widely cited by NYDIG/XBTO) cannot be tested without 25-Δ skew + term-structure data, which is not in the inventory. This is a confirmed reject.

8. **No model used the SOL ETF (2025-10-31) as a third staggered treatment.** Too short to anchor a paper, but as an *overlay* in Project 1's staggered-treatment design, it gives a third treatment date for visual validation of the factor-reallocation pattern.

9. **No model handled calendar effects formally** (month-end ETF flow seasonality, CME roll dates, US employment-report days). For IRF-based work (Projects 2, 3), calendar dummies should be pre-specified.

10. **No model treated CPI / FOMC / NFP release days as separate macro-shock events.** For Project 3's stablecoin-vs-ETF-horse-race, release-day conditional regressions would be a clean heterogeneity cut.

---

## 11. Practical Next Step (Immediately After This Memo)

**Do now (Day 1–3):**
1. Spawn a **Master Data subagent** to produce `panel_daily_2020-11_2026-04.parquet` + `PANEL_DICTIONARY.md` from the CSV paths in `MASTER_DATA-6.md`. Run ADF/PP/KPSS on every series and embed results in the dictionary.
2. Run the **Project-5 Week-1 gate** (DAT-level panel availability check in Artemis). Result determines Project-5 scope.
3. Freeze the **block definitions and H1–H5 for Project 1** in `projects/P1_PROTOCOL.md` with a git commit hash **before** running any regression. Same for Projects 2–5.

**Do in parallel (Day 3–14):**
- Spawn five subagents, one per project, all reading from the shared panel parquet.
- Each subagent must produce a Week-1 deliverable: preliminary headline table + one figure. If Project-1 rolling block-R² is weak/indistinct, pivot emphasis to Project 2 as flagship.

**Postpone:**
- TVP-VAR, MIDAS, XGBoost, SHAP, wavelet coherence, connectedness network plots. These are Week 6+ robustness.
- Any intraday / hourly analysis — confirm the inventory first, and only then.
- SOL-specific analysis (too short). Include as visual overlay only.

**Cut:**
- Options-skew / "equity-ification" paper (M9). Cannot be done with current data.
- RWA → beta-compression paper (M11). Too indirect.
- Methodology-heavy unified-connectedness paper (M12). Reviewer bait without a sharp question.
- News-sentiment, geopolitical-event, CBDC-competition ideas from Beyond-Correlation (#6, #8, #10, #12, #14, #15). All weaker than the five projects above.
- Pure DAT Bitcoin-count time-series paper in isolation. Too thin without the MSTR decomposition frame.
- Any "return prediction" or "trading strategy" framing. All outputs agree on this — keep it that way.

**Decision memo status:** ready for execution. Hand this document, `MASTER_DATA-6.md`, and the five project briefs above to parallel subagents. Expect partial results within 1 week and full Project 1 headline figure set within 3 weeks.

---

*End of synthesis.*
