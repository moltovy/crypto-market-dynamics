# Research Memo: Publishable Crypto/Finance Papers Feasible from Current Data

**Prepared:** 2026-04-17
**Scope:** Evaluation of MASTER_DATA.txt (484+ CSV feed inventory across AlternativeMe, Artemis, CryptoQuant, DefiLlama, FRED, Farside, TradingView) and identification of quantitatively defensible research programs.
**Methodological posture:** Explanatory, structural, and connectedness-oriented. ML is optional and secondary. No return-prediction, no trading-strategy framing, no causal overclaim.

---

## 1. Data and Project Summary

The inventory is unusually well-suited to a **factor-evolution, market-structure, and cross-asset connectedness** research agenda centered on BTC and ETH, with SOL as a secondary asset where samples permit.

**Asset coverage.** Spot and futures prices (CryptoQuant, TradingView), CME front-month and continuous futures with basis/ratio to spot for BTC (from 2017-12) and ETH (from 2021-02), Micro BTC/ETH, and CME SOL from 2025-03-16. IBIT and ETHA premium-to-spot series are available daily. DVOL (Deribit implied vol index) from 2021-03-24.

**Institutional and flow layer.** Daily BTC/ETH/SOL spot-ETF flows (Farside), Artemis ETF AUM series (BTC from 2024-01-11, ETH from 2024-07-23, SOL from 2025-10-31), DAT counts and NAV (BTC DATs from 2020-08-10), and equity-market proxies for crypto exposure (MSTR, COIN, MARA, RIOT, CRCL).

**On-chain and derivatives layer.** CryptoQuant provides 345 files: realized-price and cost-basis bands (MVRV, SOPR, NUPL, Puell, NVT, aSOPR), miner flows, exchange inflows/outflows, Coinbase Premium, Korea Premium, funding rates, open interest, leverage ratio, liquidations, taker CVD, and stablecoin flows (USDT/USDC/WBTC). ETH on-chain from 2020-11.

**DeFi layer.** DefiLlama TVL panel (440 chain columns), stablecoin market-cap panel (201 tokens), LST/LRT, RWA, perps OI, DEX volume, CEX net flows.

**Macro layer.** FRED daily/weekly: DFF, DGS2/DGS10/DGS30, T10Y2Y, DFII10, SOFR, RRP, WALCL, VIX, NFCI, ANFCI, STLFSI4, DXY broad, WTI, HY OAS; monthly CPI and UNRATE. Plus daily USEPUINDXD (EPU).

**Sentiment/attention.** Fear & Greed (daily, 2018-02-01 onward).

**Binding sample constraints.**
- Post-ETF BTC era = 2024-01-11 to present ≈ 27 months.
- Post-ETF ETH era = 2024-07-23 to present ≈ 21 months.
- Post-ETF SOL era = 2025-10-31 to present ≈ 5.5 months — too short to anchor a standalone paper; SOL should only enter as a robustness or comparative arm.
- DVOL from 2021-03-24 constrains any paper that needs implied vol to post-2021.
- Core econometric work is most defensible at **daily** frequency; mixed-frequency (daily/weekly/monthly) is required when CPI or UNRATE enter.

The inventory does *not* support credible identification of causal effects, microstructure at sub-second resolution, or token-level alpha research at scale. It *does* support strong work in (a) **factor structure and regime change**, (b) **connectedness/spillover**, (c) **event-study and structural-break**, (d) **market-microstructure at daily/intraday-aggregate resolution**, and (e) **institutional-flow vs. on-chain substitution**.

This is the lane to stay in.

---

## 2. Recent Research Themes (Nov 2025 – Apr 2026)

Six themes dominate the recent credible literature and practitioner research. Each is directly addressable with this data.

**Theme A — Post-ETF institutionalization and cross-asset decoupling.** A 2026 study published in *Cogent Economics & Finance* documents a sharp break in rolling BTC–altcoin correlations after the January-2024 ETF launch, arguing BTC has partially decoupled from the crypto complex and re-coupled to macro/equity beta ([Tandfonline 2026](https://www.tandfonline.com/doi/full/10.1080/23322039.2026.2625541)). Practitioner research (NYDIG, Galaxy, VanEck) reports BTC–Nasdaq 60-day correlation near 0.72 in early 2026 and BTC realized volatility compressing to ~43% in 2025 from ~52% in 2024 ([NYDIG 2026 themes](https://nydig.com/research)).

**Theme B — ETF flow elasticity and price impact.** Practitioner regressions of cumulative net ETF flow on BTC price report β ≈ 0.27 with R² ≈ 0.69 over Jan-2024 to Feb-2026; IBIT held ~777k BTC and total US BTC spot-ETF AUM reached ~$128B by mid-March 2026 ([blockeden summary](https://blockeden.xyz/blog/2026/03/bitcoin-etf-flows)). This work is largely descriptive and would benefit from proper econometric treatment (endogeneity, price-impact decomposition, heterogeneity across issuers).

**Theme C — Digital Asset Treasuries (DATs) and the MSTR premium collapse.** mNAV on the largest DATs compressed from ~4× at the 2024 peak to ~1.16 by March 2026; MSTR fell ~50% in 2025 and ~66% from peak while BTC was roughly flat, consistent with an "asymmetric double-negative" payoff on BTC drawdowns ([NYDIG DAT research](https://nydig.com/research), [Galaxy December 2025](https://www.galaxy.com/insights/research)). The collapse of the DAT premium is one of the most important structural events of 2025–2026 and is under-studied econometrically.

**Theme D — Volatility compression, smile formation, and the equity-ification of BTC options.** NYDIG and XBTO argue BTC options now display equity-like put-skew as systematic call-selling strategies (covered-call ETFs) suppress upside vol, while crash risk is priced more like equities than in the 2017–2022 era ([XBTO commentary](https://xbto.com/insights)).

**Theme E — Overnight / 24-7 timing anomalies and geographic price discovery.** An SSRN working paper documents that BTC overnight returns (relative to US equity hours) dominate intraday returns post-2021 ([SSRN 5021138](https://papers.ssrn.com/sol3/papers.cfm?abstract_id=5021138)). A "BTC AfterDark" ETF concept was filed in December 2025, and CME moved toward 24/7 trading in early 2026. VanEck argues Asian trading hours now lead BTC price discovery ([VanEck 2026](https://www.vaneck.com/us/en/blogs/digital-assets/)).

**Theme F — Stablecoins, liquidity plumbing, and connectedness.** 2025 stablecoin transaction volumes exceeded Visa (~$33T). A 2025 *AgBioForum* paper applies Diebold–Yilmaz connectedness to stablecoin returns/volatility ([AgBioForum 2025](https://agbioforum.org/)), and multiple 2025 papers extend the framework via wavelet coherence to crypto sectors ([Tandfonline 2025](https://www.tandfonline.com/journals/rquf20)). The Stablecoin Supply Ratio (SSR) and stablecoin-exchange flows have become standard "dry powder" proxies but their information content vs. ETF flows has not been cleanly separated.

**Secondary themes.**
- *Economic Policy Uncertainty and crypto.* EFMA 2025 and *JIFMIM* 2025 papers link EPU shocks to BTC return synchronicity and attention ([EFMA 2025 program](https://efmaefm.org/)).
- *Leverage cascades.* The October-10-2025 liquidation event ($19–31B across exchanges; ~86% long-side per Amberdata) is a natural event-study anchor ([Amberdata 2025](https://blog.amberdata.io/)), with FTI Consulting, Galaxy, and Coin Metrics all publishing post-mortems.
- *The "four-year cycle" thesis failing.* Post-halving 2024 proved atypical; practitioners increasingly argue institutional flows dwarf miner issuance effects.
- *Declining information content of on-chain alone.* 21Shares (Nov 2025) and VanEck (Oct 2025) both argue on-chain signals are weaker than liquidity/leverage for high-frequency dynamics, but remain useful for slow-moving cost-basis and cycle-state variables.

These themes converge on a single empirical question: **how has the factor structure of crypto risk and return changed in the institutional era, and which of the traditional on-chain and derivatives factors still carry independent information once ETF flows, macro liquidity, and equity-market betas are controlled for?** That question is the spine of this memo.

---

## 3. Main Paper Ideas (Candidate Set)

Twelve candidates below. Each is scored on **Feasibility (data/timeline fit for an MSc-level team), Novelty vs. 2025–2026 literature, and Publication Defensibility (ability to withstand a skeptical referee report at a Q2-level finance/econ journal)**. Scores are blunt; a 6 is not a pass.

---

### M1. The ETF Break: Structural Change in the BTC Factor Model Around January 2024

- **Thesis:** The cross-sectional factor structure pricing BTC (and secondarily ETH) underwent a one-time structural break around the January-2024 spot-ETF launch, with equity-beta, rates, and ETF-flow factors gaining explanatory power at the direct expense of on-chain and crypto-native factors.
- **Central research question:** Which factor blocks *lose* explanatory power for BTC/ETH daily returns after ETF launch, and is the break statistically distinct from a slow-moving drift?
- **Why 2026:** Two-plus years of post-ETF data now exist — barely enough for credible sub-sample estimation. This window closes as the post-ETF era becomes the norm.
- **Why feasible:** Everything needed is in the inventory: ETF flows (Farside), macro (FRED), equity indices (TradingView), on-chain (CryptoQuant), derivatives (CryptoQuant + TradingView).
- **DVs:** Daily log returns of BTC, ETH (spot) and CME continuous futures log returns; weekly realized volatility (RV5/RV22) as secondary DV.
- **Factor blocks:**
  1. *Macro*: ΔDGS10, ΔDFII10, ΔDXY, ΔWTI, ΔVIX, ΔHY OAS, NFCI, ANFCI.
  2. *Equity*: SPY, QQQ, SMH, XLK, IWM, ARKK excess returns.
  3. *Crypto-native / on-chain*: MVRV-Z, SOPR, NUPL, exchange netflow, miner outflow, Puell, NVT, Coinbase Premium, Korea Premium, Fear&Greed.
  4. *Derivatives*: funding rate, OI change, leverage ratio, taker CVD, DVOL change (post-2021), CME basis.
  5. *Flow / institutional*: daily net ETF flow (BTC, ETH), ETF AUM change, DAT holdings change, IBIT/ETHA premium-to-spot, SSR.
- **Frequency:** Daily. Weekly robustness.
- **Sample:** 2021-03-24 → 2026-04-17 (DVOL-constrained). Pre/post split at 2024-01-11 (BTC); 2024-07-23 (ETH).
- **Econometric framework:**
  - Baseline: block-wise OLS with HAC errors; partial-R² decomposition by block per sub-sample; incremental R² from adding each block.
  - Structural break: Chow test at candidate dates (2023-10 preliminary ETF approval speculation, 2024-01-11 launch, 2024-03 IBIT inflow peak); Bai-Perron for endogenous break detection; CUSUM-OLS.
  - Quandt-Andrews sup-F for unknown break date as defensive robustness.
  - Rolling 126-day block-R² to visualize factor dominance over time.
- **Supporting ML (optional):** LASSO within each block to prune redundant on-chain indicators; random-forest permutation importance as a *diagnostic* for nonlinearity, not prediction. Must not be headlined.
- **Charts/tables:**
  - Table 1: Block-wise partial-R² pre vs. post, with bootstrap CIs.
  - Table 2: Bai-Perron break dates and confidence bands.
  - Figure 1: Stacked rolling R² by block (area chart).
  - Figure 2: Coefficient trajectories for key factors (ETF flow, SPY, DXY, funding, MVRV).
- **Likely criticism:** (i) Post-ETF sample is short (~550 daily obs); (ii) ETF flows and returns are mechanically correlated; (iii) multiple testing across break dates.
- **Defense:** (i) HAC + bootstrap; (ii) decompose flow into expected vs. innovation component using AR model on flows, use innovation in regression, and run IV using ETF issuer cross-section as a partial supply shifter; (iii) Bonferroni or Bai-Perron's joint test.
- **Feasibility 9 / Novelty 7 / Publication defensibility 8. Recommendation: PURSUE.**

---

### M2. Connectedness and Directional Spillovers Between Crypto, ETF Flows, Macro, and Equity Blocks (Diebold-Yilmaz 2012 + Frequency-Domain)

- **Thesis:** In the institutional era, the direction and magnitude of volatility/return spillovers among crypto, ETF flows, macro-liquidity, and equity sectors has shifted; crypto is now a net receiver of equity and liquidity shocks, reversing the 2021–2022 pattern.
- **Central research question:** Who transmits and who absorbs shocks across BTC, ETH, SPY/QQQ, DXY, VIX, HY OAS, ETF flows, and stablecoin supply changes, and does this change by frequency band?
- **Why 2026:** Diebold-Yilmaz applications to crypto are common; frequency-domain decomposition (Baruník-Křehlík 2018) on a post-ETF system including ETF flows as a network node is not.
- **Why feasible:** Panel is small (≤15 nodes), VAR of order 2–5 is tractable on ~1500 daily obs (2020-11 onward where all nodes exist).
- **DVs:** Daily log returns and realized volatility for each node.
- **Factor blocks / nodes:** BTC, ETH, SPY, QQQ, XLK, DXY, VIX, DGS10, HY OAS, BTC ETF flow, ETH ETF flow, USDT supply Δ, USDC supply Δ, CME BTC basis, DVOL.
- **Frequency:** Daily.
- **Sample:** 2020-11-01 → 2026-04-17. Rolling 200-day windows.
- **Econometric framework:**
  - Baseline: VAR(p) with SIC-selected p; Diebold-Yilmaz (2012) generalized FEVD connectedness; 200-day rolling total, directional-to, directional-from, and net connectedness.
  - Frequency-domain: Baruník-Křehlík short (1–5 days), medium (5–22), long (22+) band decomposition.
  - Pre/post ETF comparison with permutation tests on connectedness statistics.
  - Granger-causality block tests as supporting evidence.
- **Supporting ML:** None required. Could use LASSO-VAR for high-dimensional robustness if node count expands beyond 20.
- **Charts/tables:** Network plot pre vs. post; time-varying total connectedness; directional spillover heatmap by frequency band.
- **Criticism:** (i) DY connectedness is widely applied — marginal novelty needs sharpening; (ii) VAR misspecification in presence of structural breaks.
- **Defense:** (i) Frequency-band decomposition with ETF flows as explicit node is novel; (ii) Bai-Perron on total connectedness and subsample re-estimation.
- **Feasibility 9 / Novelty 6 / Publication defensibility 8. Recommendation: PURSUE (narrow to ETF-flows-as-node angle).**

---

### M3. The DAT Premium Collapse: What Explains the Asymmetric Double-Negative Payoff of MSTR to BTC

- **Thesis:** MSTR's price response to BTC is structurally asymmetric post-2024 — it behaves like BTC × leverage on the upside but like BTC × leverage × mNAV-compression on the downside — and the mNAV compression itself is explained by dilution pace, BTC drawdown regime, and equity-market risk appetite, not by BTC level alone.
- **Central research question:** What drives the cross-section and time-series of the DAT premium (mNAV), and can the asymmetric MSTR-β to BTC be decomposed into a BTC-beta component and a premium-compression component?
- **Why 2026:** The mNAV collapse from ~4× to ~1.16 is the cleanest natural experiment in crypto-equity structure in years and is under-studied econometrically.
- **Why feasible:** DAT count and NAV from Artemis (BTC DATs 2020-08-10 onward); MSTR daily price from 2010; BTC spot and CME basis; equity market regressors. COIN, MARA, RIOT as comparator equities.
- **DVs:** MSTR daily return; mNAV level and Δ; MSTR-BTC β (rolling); 1[MSTR_return < X·BTC_return] indicator (asymmetry).
- **Factor blocks:** BTC return, BTC drawdown-regime indicator (from peak), SPY return, DXY, HY OAS, DAT dilution rate (implied from count Δ), ETF flow, VIX, MSTR-specific equity-issuance news proxy (from TradingView volume spikes + external filings if available).
- **Frequency:** Daily.
- **Sample:** 2020-08-10 → 2026-04-17.
- **Econometric framework:**
  - Decomposition: Return(MSTR) = α + β_BTC·Return(BTC) + β_prem·Δ(mNAV) + β_SPY·Return(SPY) + … with rolling 63-day windows.
  - Regime-switching (Markov 2-state on BTC drawdown) for the asymmetric β.
  - Bai-Perron on mNAV level.
  - Instrumented regression: use aggregate DAT-count Δ across the full DAT universe (excluding MSTR) as a quasi-exogenous "industry dilution supply" shock affecting MSTR-specific mNAV.
- **Supporting ML:** Random-forest SHAP on mNAV Δ as exploratory diagnostic only.
- **Charts/tables:** mNAV timeline with break markers; asymmetric scatter MSTR vs. BTC color-coded by drawdown regime; rolling β decomposition stacked area.
- **Criticism:** (i) MSTR is n=1 — thin cross-section; (ii) Reflexivity between BTC and DAT dilution.
- **Defense:** (i) Extend to multi-DAT panel using Artemis DAT names (if available in CSVs — needs verification from the DAT Bitcoin Count file at row-level; see feasibility note); (ii) IV via industry-aggregate dilution.
- **Feasibility 7 / Novelty 9 / Publication defensibility 8. Recommendation: PURSUE.**

---

### M4. Price Discovery Across Venues in the 24-7 Era: CME Futures, Spot ETFs, Spot BTC, and Asian vs. US Sessions

- **Thesis:** Price discovery for BTC has shifted from spot-venues dominant (2020–2023) to a tri-polar system (spot, CME futures, spot ETF proxies via IBIT premium) with distinct regional leaders in Asian vs. US sessions.
- **Central research question:** What share of permanent price innovation is attributable to CME futures, spot BTC, and IBIT/ETHA, and how does that share differ across 24-hour sub-periods?
- **Why 2026:** CME moved toward 24/7 trading in 2026; "AfterDark" ETF filings reflect explicit recognition of overnight price formation. Also tests the VanEck claim that Asian hours lead.
- **Why feasible:** TradingView provides CME front-month BTC/ETH (with basis to spot) and IBIT/ETHA premium to spot. Spot BTC/ETH from CryptoQuant. Intraday hourly feeds are ambiguous from the inventory (MASTER_DATA.txt lists daily TradingView CSVs — intraday availability needs verification). If only daily, collapse sessions to close-to-close, Asia-close-to-US-close, US-close-to-Asia-close spans and use that tri-partition.
- **DVs:** Hasbrouck (1995) information share; Gonzalo-Granger (1995) common-factor weights; Putniņš (2013) modified info-share.
- **Factor blocks:** Co-integrated system {log spot, log CME front-month, log IBIT × NAV reconstructed}, with ETH analog.
- **Frequency:** Ideally 5-minute or 15-minute; **if only daily is available, the paper becomes a session-level price-discovery paper, which is still publishable but less impactful.**
- **Sample:** 2024-01-11 → 2026-04-17 (post-ETF).
- **Econometric framework:**
  - VECM → Hasbrouck IS, Gonzalo-Granger CS. Bootstrapped CIs.
  - Rolling 60-day windows to track drift in IS.
  - Session-split comparisons: pre-2026 (CME closed overnight/weekends) vs. post-2026 (24/7 CME).
- **Supporting ML:** None.
- **Charts/tables:** IS over time; session-split bar charts; pre/post 24-7 IS shift.
- **Criticism:** (i) Data-frequency concern — hourly is vastly preferred; (ii) IBIT premium may reflect APs' creation/redemption rather than fundamental discovery.
- **Defense:** (i) Confirm feed granularity at kickoff; (ii) decompose IBIT premium into NAV-deviation (AP arbitrage) and sentiment components and use only sentiment component.
- **Feasibility 6 (conditional on intraday granularity) / Novelty 7 / Publication defensibility 7. Recommendation: NARROW — confirm intraday granularity first; otherwise drop to session-level.**

---

### M5. ETF Flow Price Impact with Proper Endogeneity: A Supply-Shifter Identification

- **Thesis:** The headline β ≈ 0.27, R² ≈ 0.69 from practitioner regressions of BTC price on cumulative ETF flow is econometrically misleading; once expected flow is extracted and cross-issuer heterogeneity is used as an instrument, contemporaneous price impact is lower and flow innovations explain 20–35% of post-ETF return variance via a proper impulse-response.
- **Central research question:** What is the causal price impact of unexpected ETF flow on BTC returns, after addressing simultaneity?
- **Why 2026:** Practitioner regressions are widely cited; academic literature has not caught up. Institutional publication target.
- **Why feasible:** Farside provides issuer-level ETF flows; Artemis AUM confirms levels. BTC spot in CryptoQuant.
- **DVs:** BTC daily return; BTC intraday close-to-close.
- **Factor blocks:** Net ETF flow (expected vs. innovation from ARIMA); equity market return; DXY; VIX; cross-issuer flow shares; macro controls.
- **Frequency:** Daily.
- **Sample:** 2024-01-11 → 2026-04-17.
- **Econometric framework:**
  - Decompose flow into expected and unexpected (ARIMA residual; also Kalman filter with ETF-AUM state).
  - Local projections (Jordà 2005) of BTC return on unexpected ETF flow, horizons 0–20 days, with controls.
  - IV design: idiosyncratic issuer-level flow (e.g., FBTC flow purged of its common component with IBIT) as instrument for aggregate flow — argues that FBTC-specific demand is not mechanically BTC-price-driven except via aggregate flow.
  - Heterogeneity across volatility regimes (VIX-based), drawdown regimes.
- **Supporting ML:** None required.
- **Charts/tables:** Flow-decomposition series; IRF with CI bands; coefficient table comparing OLS, IV, local-projections.
- **Criticism:** (i) Instrument exclusion restriction is not watertight; (ii) Post-ETF sample is short.
- **Defense:** (i) Falsification tests (issuer flow shouldn't predict macro variables, pre-registration of exclusion reasoning); (ii) Newey-West, bootstrap.
- **Feasibility 9 / Novelty 8 / Publication defensibility 9. Recommendation: PURSUE.**

---

### M6. The Information Content of On-Chain Factors Conditional on ETF and Derivatives Information

- **Thesis:** Popular on-chain indicators (MVRV, SOPR, NUPL, Puell, NVT, exchange netflow) lose most of their incremental explanatory power for daily BTC/ETH returns and realized volatility once ETF flow, derivatives positioning, and macro-liquidity factors are controlled for, but retain power at *weekly and cycle-state* horizons.
- **Central research question:** Which on-chain variables carry independent information across horizons (1d / 1w / 1m), and does that set shrink post-ETF?
- **Why 2026:** 21Shares and VanEck both claim on-chain is "weakening"; the hypothesis has not been tested systematically in the published literature.
- **Why feasible:** CryptoQuant panel is the paper's core.
- **DVs:** BTC/ETH return; RV5/RV22; realized semivariance.
- **Factor blocks:** On-chain (12–15 indicators); derivatives (5); flow (3); macro (8); equity (4).
- **Frequency:** Daily, weekly, monthly triple-horizon.
- **Sample:** 2020-11 → 2026-04-17. Pre/post 2024-01-11 split.
- **Econometric framework:**
  - Hierarchical variance decomposition: block-wise Shapley-R² (Grömping).
  - MIDAS or Mixed-Data-Sampling for mixed-horizon robustness.
  - Pre/post ETF comparison with difference-in-R² bootstrap.
  - Partial-correlation network of on-chain vs. other blocks, pre vs. post.
- **Supporting ML:** Elastic-net for variable selection within on-chain block; permutation importance.
- **Charts/tables:** Shapley-R² decomposition bars across horizons; heatmap of on-chain coefficient significance pre/post.
- **Criticism:** (i) On-chain metrics are mechanically correlated with each other and with price; (ii) MVRV-type variables are functions of price, raising tautology concerns.
- **Defense:** (i) Orthogonalize on-chain block via PCA first; (ii) pre-difference or use unexpected component (residual from AR model on indicator levels).
- **Feasibility 9 / Novelty 7 / Publication defensibility 8. Recommendation: PURSUE.**

---

### M7. Stablecoin Supply Dynamics and the Transmission of Liquidity to Crypto Asset Prices

- **Thesis:** Stablecoin net supply changes (USDT + USDC) act as a crypto-native liquidity shock with transmission patterns that differ systematically from ETF flows — stablecoin supply leads DEX/CEX order book depth and alt-coin TVL, while ETF flow leads BTC/ETH spot.
- **Central research question:** Do stablecoin issuance/redemption and ETF flows carry distinct information for different crypto assets and segments (BTC, ETH, stablecoin-denominated DEX TVL)?
- **Why 2026:** $33T stablecoin throughput in 2025; SSR has become a cited metric but not rigorously differentiated from ETF flow.
- **Why feasible:** DefiLlama stablecoin panel (201 tokens); CryptoQuant USDT/USDC on-chain; Farside ETF flows.
- **DVs:** BTC return, ETH return, DEX volume, stablecoin-denominated TVL, CEX net inflow.
- **Factor blocks:** USDT supply Δ, USDC supply Δ, aggregate stablecoin mcap Δ, ETF flow, macro liquidity (WALCL, SOFR-IORB spread, RRP), equity return.
- **Frequency:** Daily.
- **Sample:** 2020-11 → 2026-04-17.
- **Econometric framework:**
  - VAR with Cholesky ordering: macro → stablecoin supply → ETF flow → crypto prices.
  - IRFs and FEVDs.
  - Granger block-causality.
  - Horse-race regression (SSR vs. ETF-flow coefficient stability).
- **Supporting ML:** None.
- **Charts/tables:** IRFs across DVs; FEVD pie charts; coefficient stability across sub-periods.
- **Criticism:** (i) Stablecoin issuance is endogenous to crypto demand; (ii) Supply Δ is a noisy proxy for liquidity.
- **Defense:** (i) Use Tether/Circle issuance announcements as event-study anchors; (ii) cross-check with exchange stablecoin balances.
- **Feasibility 8 / Novelty 7 / Publication defensibility 7. Recommendation: PURSUE.**

---

### M8. Event Study: The October 10, 2025 Liquidation Cascade as a Natural Experiment for Leverage-Induced Price Discovery

- **Thesis:** The Oct-10-2025 cascade ($19–31B liquidated, ~86% long) produced a sharp, temporary dislocation in funding rates, basis, and implied vol surface that reveals the state-dependent relationship between leverage build-up, funding-rate signals, and realized crash risk.
- **Central research question:** How do funding rates, OI, leverage ratio, and DVOL skew behave in the 60 days before and 30 days after a large liquidation cascade, and how does this pattern compare to prior cascades (May-2021, Nov-2022 FTX, Aug-2024)?
- **Why 2026:** Oct-10-2025 is a clean, large, well-documented event with multiple post-mortems.
- **Why feasible:** CryptoQuant funding, OI, leverage ratio, liquidations; DVOL skew if available at surface granularity (if only DVOL level is in inventory, the skew arm becomes infeasible — flag).
- **DVs:** BTC return, realized vol, funding rate, OI, DVOL, basis.
- **Factor blocks:** Pre-event leverage buildup indicators; macro controls; equity returns.
- **Frequency:** Daily with high-frequency robustness if hourly feeds exist.
- **Sample:** 2020-01-01 → 2026-04-17 with event windows.
- **Econometric framework:**
  - Event-study with matched control windows (same day-of-week, same vol regime, same funding regime).
  - Abnormal return/abnormal vol computation.
  - Comparative event-study across five cascades.
  - Pre-event logit (cascade indicator) on funding/OI to test whether funding-rate warnings were visible ex-ante.
- **Supporting ML:** Isolation-forest for anomaly detection pre-event as diagnostic.
- **Charts/tables:** Overlay of event-windows across cascades; pre-event warning-signal dashboard; post-event reconvergence curves.
- **Criticism:** (i) Small-n of cascades; (ii) Event-date is ambiguous (cascade lasted hours).
- **Defense:** (i) Pool across cascades and use fixed-effects; (ii) define event day as day of max single-day liquidation.
- **Feasibility 9 / Novelty 7 / Publication defensibility 8. Recommendation: PURSUE.**

---

### M9. The Equity-ification of BTC Options: Skew, Term Structure, and Call-Selling Supply

- **Thesis:** BTC's implied-volatility surface has shifted from symmetric/call-skewed in 2021–2022 to put-skewed and term-structure-flat post-2024, and this shift is explained by institutional call-selling supply (covered-call ETFs, DAT yield strategies) and correlates with ETF AUM, not with realized-vol regime alone.
- **Central research question:** What explains the emergence of equity-like put skew in BTC options?
- **Why 2026:** NYDIG/XBTO narrative is strong; academic test is missing.
- **Why feasible:** DVOL from 2021-03-24. **But DVOL is a level, not a surface — this paper requires surface data (25-delta skew, term structure) that the inventory does not appear to include.** If only DVOL level is available, the paper must be reframed as "DVOL level and structure" and loses ~50% of its bite. Flag as a major data-gap risk.
- **DVs:** DVOL level; realized-implied vol gap; realized semivariance ratio (as proxy for ex-post skew).
- **Factor blocks:** ETF AUM, DAT holdings Δ, equity VIX, BTC realized vol, funding rate, taker CVD.
- **Frequency:** Daily.
- **Sample:** 2021-03-24 → 2026-04-17.
- **Econometric framework:**
  - Baseline: HAR-RV with institutional-supply covariates.
  - Structural break tests on DVOL level and realized-implied spread.
  - If skew/term-structure data can be sourced separately (Deribit public API), add panel regressions of skew on supply proxies.
- **Supporting ML:** None.
- **Charts/tables:** DVOL level vs. ETF AUM overlay; break tests; HAR augmented with supply covariates.
- **Criticism:** (i) Without full surface, skew claim is unsupported; (ii) Supply-side proxies are coarse.
- **Defense:** (i) Reframe around DVOL level unless supplementary data can be added; (ii) use realized-semivariance ratio as model-free skew proxy.
- **Feasibility 5 (conditional — drops to 3 if surface unavailable) / Novelty 8 / Publication defensibility 6. Recommendation: NARROW — only pursue if surface data can be added outside this inventory; else REJECT as headline paper.**

---

### M10. Macro-Factor Betas of BTC and ETH: From 2017 to 2026 — A Rolling Exposure Study

- **Thesis:** BTC and ETH betas to rates (DGS2, DGS10, DFII10), USD (DXY), credit (HY OAS), and liquidity (WALCL, NFCI) evolve in regime-dependent ways, with a distinct post-2022-Q4 "rates-sensitive" regime and post-2024-Q1 "equity-sensitive" regime; ETH lags BTC in regime transitions by 1–3 months.
- **Central research question:** What is the time-varying macro-factor exposure of BTC and ETH across the last decade and how do the betas transition across clearly identifiable macro regimes?
- **Why 2026:** A decade-long macro-beta study including the post-ETF and high-real-rate period is overdue.
- **Why feasible:** FRED panel is complete; BTC from 2017, ETH from 2020-11; DXY and HY OAS from TradingView/FRED.
- **DVs:** BTC/ETH daily return; weekly return.
- **Factor blocks:** ΔDGS2, ΔDGS10, ΔDFII10, ΔDXY, ΔHY OAS, ΔWALCL, ΔNFCI, ΔVIX.
- **Frequency:** Daily and weekly.
- **Sample:** 2017-01-01 (BTC) / 2020-11-01 (ETH) → 2026-04-17.
- **Econometric framework:**
  - Rolling 126-day OLS with HAC; state-space/Kalman filter for time-varying betas.
  - Markov regime-switching on beta vector (2 or 3 states).
  - Bai-Perron on each beta.
  - ETH-lag hypothesis: Granger causality of BTC-beta changes on ETH-beta changes.
- **Supporting ML:** K-means clustering on macro-variable-path for regime identification as exploratory cross-check of Markov states.
- **Charts/tables:** Time-varying beta dashboards; regime-probability plots; regime-conditional beta table.
- **Criticism:** (i) Decade-long study is not new per se; (ii) beta instability may reflect misspecification.
- **Defense:** (i) Emphasize post-ETF regime as novel; (ii) report multiple specifications with robustness to frequency and window.
- **Feasibility 10 / Novelty 5 / Publication defensibility 7. Recommendation: PURSUE as baseline/foundational — publishable in mid-tier outlet, strong MSc thesis core.**

---

### M11. Economic Policy Uncertainty, Crypto Volatility, and the Attention Channel

- **Thesis:** EPU shocks transmit to crypto volatility both directly (risk-off) and indirectly through attention/sentiment; the attention channel has weakened post-ETF as a professional investor base partially replaces retail attention.
- **Central research question:** Does the EPU-to-crypto-volatility relationship run through attention/sentiment (Fear & Greed) and has that channel weakened post-ETF?
- **Why 2026:** EFMA 2025 and JIFMIM 2025 have brought the topic forward, but attention-channel decomposition post-ETF is novel.
- **Why feasible:** FRED USEPUINDXD daily; Fear & Greed daily from 2018.
- **DVs:** BTC/ETH realized volatility; realized-implied gap.
- **Factor blocks:** ΔEPU, Fear & Greed, macro (rates, DXY, VIX), ETF flow.
- **Frequency:** Daily.
- **Sample:** 2018-02 → 2026-04-17.
- **Econometric framework:**
  - Mediation analysis (Baron-Kenny with bootstrap CI) or structural VAR with EPU → F&G → vol ordering.
  - Pre/post ETF split.
  - Local projections of EPU shocks on vol with and without F&G as control.
- **Supporting ML:** None.
- **Charts/tables:** Mediation diagram with coefficients; IRF under two orderings; subsample stability table.
- **Criticism:** (i) F&G is itself influenced by price — reverse causality; (ii) EPU is a generic US-based index.
- **Defense:** (i) Use EPU innovations and pre-whitened F&G; (ii) robustness to country-EPU if feasible outside inventory.
- **Feasibility 8 / Novelty 6 / Publication defensibility 7. Recommendation: NARROW — strong secondary paper, not a flagship.**

---

### M12. Coinbase Premium, Korea Premium, and the Geography of Crypto Demand in the ETF Era

- **Thesis:** The Coinbase Premium (US demand proxy) and Korea Premium (Korean retail proxy) behave as partially substitutable geographic demand factors, and the post-ETF era has seen Coinbase Premium shift from being primarily driven by US spot-retail to being driven by ETF authorized-participant arbitrage, while Korea Premium retains retail-sentiment character.
- **Central research question:** Has the information content and driver set of Coinbase Premium structurally changed post-ETF, while Korea Premium has not?
- **Why 2026:** The geographic-premium literature is narrow; isolating an AP-arbitrage mechanism in Coinbase Premium is novel.
- **Why feasible:** CryptoQuant supplies both.
- **DVs:** Coinbase Premium level/Δ; Korea Premium level/Δ; BTC return.
- **Factor blocks:** ETF flow, IBIT NAV deviation, USD/KRW rate if available outside inventory, retail-attention proxies (F&G).
- **Frequency:** Daily.
- **Sample:** 2019 or earliest available → 2026-04-17.
- **Econometric framework:**
  - Pre/post ETF structural break on Coinbase Premium process (AR, vol, persistence).
  - Regression of Coinbase Premium on ETF flow innovations + controls; parallel on Korea Premium (expect null).
  - DY connectedness between the two premia + BTC + ETF flow.
- **Supporting ML:** None.
- **Charts/tables:** Break statistics; premium decomposition; connectedness diagram.
- **Criticism:** (i) Premia are noisy; (ii) USD/KRW FX needed for Korea Premium interpretation.
- **Defense:** (i) Use 7-day smoothed premia; (ii) add USD/KRW from outside inventory if required.
- **Feasibility 7 / Novelty 7 / Publication defensibility 7. Recommendation: PURSUE as secondary/side-paper or experimental pilot.**

---

## 4. Ranking of All Main Ideas (12 candidates)

Composite score = 0.4·Publication-defensibility + 0.3·Novelty + 0.3·Feasibility.

| Rank | ID | Title (short) | Feas. | Nov. | Pub. | Composite | Recommendation |
|---|---|---|---|---|---|---|---|
| 1 | M5 | ETF flow price impact with endogeneity | 9 | 8 | 9 | **8.7** | PURSUE |
| 2 | M1 | ETF structural break in factor model | 9 | 7 | 8 | **8.0** | PURSUE |
| 3 | M3 | DAT/MSTR asymmetric premium collapse | 7 | 9 | 8 | **7.9** | PURSUE |
| 4 | M6 | On-chain info content conditional on ETF | 9 | 7 | 8 | **8.0** | PURSUE |
| 5 | M8 | Oct-10-2025 liquidation event study | 9 | 7 | 8 | **8.0** | PURSUE |
| 6 | M2 | DY connectedness w/ ETF-flow node | 9 | 6 | 8 | **7.7** | PURSUE (narrow) |
| 7 | M10 | Macro-beta regime study (decade) | 10 | 5 | 7 | **7.3** | PURSUE as foundational |
| 8 | M7 | Stablecoin vs. ETF liquidity horse-race | 8 | 7 | 7 | **7.3** | PURSUE |
| 9 | M12 | Coinbase/Korea premium geography | 7 | 7 | 7 | **7.0** | PURSUE as side-paper |
| 10 | M11 | EPU / attention channel | 8 | 6 | 7 | **7.0** | NARROW — secondary |
| 11 | M4 | Price-discovery across venues & sessions | 6 | 7 | 7 | **6.7** | NARROW — data-granularity risk |
| 12 | M9 | Options equity-ification / skew | 5 | 8 | 6 | **6.3** | REJECT as headline |

(Tie-breaking favored publication defensibility.)

---

## 5. Top 5 Main Ideas — Deeper Treatment

### #1 — M5: ETF Flow Price Impact with Proper Endogeneity

- **Why it made top 5:** Directly addresses an empirically important, widely cited but econometrically sloppy claim. The identification story (issuer-level idiosyncratic flow as instrument, expected-vs-unexpected decomposition, local projections) is publishable in mainstream empirical finance outlets, not just crypto journals.
- **Why it beats lower-ranked:** M10 is foundational but incremental; M2 is methodologically familiar; M9 has a data gap. M5 combines a clean identification narrative with a canonical dataset and a real policy/practitioner question.
- **Implementation risk:** The IV exclusion restriction is the single biggest risk. Mitigation: pre-register the instrument logic, report reduced-form and over-identification-style diagnostics, run sensitivity analyses as in Oster (2019).
- **MVP:** OLS and Jordà local projections on aggregate flow, 24-month window, with macro controls.
- **Stronger version:** IV with issuer-idiosyncratic flow; heterogeneity across volatility and drawdown regimes; ETH parallel; realized-vol DV as a second outcome.

### #2 — M1: Structural Break in the BTC Factor Model

- **Why it made top 5:** Combines a clean, narratively powerful event (ETF launch) with a methodologically conservative toolkit (Bai-Perron, partial-R² decomposition, Shapley-like block contributions) and produces a result that is central to the 2025–2026 practitioner discourse.
- **Why it beats lower-ranked:** M10 answers "how do betas evolve" descriptively; M1 answers "what changed" with formal breaks. M2 is a methodology-first paper; M1 is a question-first paper.
- **Implementation risk:** Short post-ETF sample weakens break-test power; multiple-testing across candidate break dates.
- **MVP:** Pre/post split at 2024-01-11, block-R² decomposition, Chow.
- **Stronger version:** Bai-Perron with unknown break date, rolling Shapley-R² decomposition, parallel ETH analysis, sensitivity to sample length.

### #3 — M6: On-Chain Information Content Conditional on ETF and Derivatives

- **Why it made top 5:** Directly tests a popular 2025 claim (21Shares/VanEck). The result is informative whatever the sign — either on-chain factors survive as incremental information (surprising to practitioners) or they do not (validates the consensus rigorously for the first time).
- **Why it beats lower-ranked:** Clean identification, horizons naturally separated, and the on-chain block is the deepest in this inventory — so this paper uses the dataset's unique strength.
- **Implementation risk:** Mechanical dependence of MVRV-type metrics on price; requires careful orthogonalization.
- **MVP:** Daily-horizon block-wise R² pre/post with 5–8 on-chain indicators orthogonalized via PCA.
- **Stronger version:** Triple-horizon MIDAS; Shapley decomposition across horizons; ETH parallel; robustness using innovations rather than levels.

### #4 — M3: DAT / MSTR Premium Collapse

- **Why it made top 5:** Highest novelty in the candidate set. The mNAV collapse is a first-order event in 2025–2026 crypto-equity structure and is under-studied. MSTR-as-BTC-proxy is a canonical topic in practitioner finance.
- **Why it beats lower-ranked:** M12, M11, M9 all have narrow or conditional feasibility; M3's n=1 MSTR concern is mitigable via the DAT universe and via regime-switching design.
- **Implementation risk:** DAT cross-section may be too thin; reflexivity between MSTR dilution and BTC price.
- **MVP:** Rolling β(MSTR, BTC) decomposition with mNAV as conditioning variable; Bai-Perron on mNAV.
- **Stronger version:** Multi-DAT panel; regime-switching β; industry-dilution IV; event study on key issuance announcements.

### #5 — M8: October 10, 2025 Liquidation Cascade Event Study

- **Why it made top 5:** Event-study papers are publication-friendly and the Oct-10-2025 event is large, well-documented, and recent. Comparative event study across five cascades strengthens identification.
- **Why it beats lower-ranked:** M2 is methodology-heavy; M7 depends on stablecoin-flow endogeneity assumptions; M8 has a clean identification strategy built into the event structure.
- **Implementation risk:** Small-n of cascades; event-window definition.
- **MVP:** Single-event study of Oct-10-2025 with matched control windows.
- **Stronger version:** Five-cascade panel; pre-event leverage-warning logit; post-event vol-surface reconvergence; cross-exchange heterogeneity.

---

## 6. Top 3 Final Proposals (Journal-Submission Quality)

### Proposal A — "What the ETF Bought and What It Broke": Structural Change in the Factor Pricing of Bitcoin (M1)

- **Abstract.** We estimate block-wise factor models for daily Bitcoin and Ether returns over 2020–2026 and test for a structural break around the January-2024 launch of US spot Bitcoin ETFs. Using Bai-Perron endogenous break estimation, partial-R² decomposition, and rolling Shapley-block contributions, we show that equity-market, rates, and institutional-flow factors gained substantial explanatory power after January 2024, while several canonical on-chain factors (MVRV, SOPR, NUPL, Puell) lost incremental explanatory power net of controls. We document that the break is localized in time and not attributable to a slow drift. Results are robust across frequencies, factor orthogonalizations, and subsample designs. The findings provide the first formal econometric characterization of crypto factor-structure change in the institutional era.
- **Hypotheses:**
  - H1: Equity-block partial-R² for BTC/ETH returns rises after 2024-01-11.
  - H2: On-chain-block partial-R² for BTC returns declines after 2024-01-11 conditional on flow and derivatives blocks.
  - H3: Flow-block partial-R² is zero pre-ETF (by construction) and strictly positive post-ETF.
  - H4: The Bai-Perron endogenous break date falls within a narrow window of 2024-01-11.
- **Data blocks:** macro (FRED), equity (TradingView), flow (Farside/Artemis), on-chain (CryptoQuant), derivatives (CryptoQuant + TradingView DVOL), sentiment (F&G).
- **Sample design:** Daily, 2020-11-01 → 2026-04-17. ETH from 2020-11. Pre-sample N ≈ 800d; post-sample N ≈ 550d.
- **Baseline model family:** OLS with HAC (Newey-West, 5 lags); Chow; Bai-Perron; partial-R² (Shapley-Owen).
- **Robustness model family:** Quandt-Andrews; CUSUM-OLS; subsample bootstrap; factor orthogonalization via PCA within blocks; rolling 126d block-R²; weekly-frequency replication; MIDAS with monthly macro.
- **Acceptable ML:** LASSO within on-chain block for sparsity and redundancy checks (reported as a diagnostic, not a main specification); permutation importance for nonlinearity flags.
- **Empirical workflow:**
  1. Construct master daily panel, align by trading date, handle weekends via Monday-closing convention; confirm all series have been stationarity-tested (ADF/PP/KPSS) and differenced as needed.
  2. Estimate full-sample block-wise OLS; compute block partial-R² and full-model R².
  3. Split sample at 2024-01-11; re-estimate; compute block partial-R² pre and post; bootstrap 5,000-replication CIs on the difference.
  4. Run Bai-Perron with 0–5 breaks; report BIC-selected count and dates.
  5. Compute rolling 126-day block-R², plot.
  6. Robustness battery; write-up; pre-register pre-specified hypotheses with protocol archived.
- **Contribution vs. literature:** Extends the rolling-correlation decoupling work of Tandfonline 2026 with formal break estimation and block-by-block partial-R² rather than correlation; formalizes the 21Shares/VanEck on-chain-weakening claim.
- **Key differentiators:** (i) Block-wise partial-R² with explicit variance decomposition rather than correlation-only; (ii) inclusion of ETF-flow-as-factor as a separate block; (iii) formal endogenous-break estimation rather than assumed break date; (iv) transparent, non-ML headline methodology.
- **Feasibility for MSc team:** Strong. Core software: Python (statsmodels, linearmodels) or R (strucchange, urca, vars). Estimated ~10–14 weeks for MVP, 18–22 for strong version.

### Proposal B — "Flow Impact, Properly Identified": The Price Effect of ETF Flows on Bitcoin (M5)

- **Abstract.** We identify the price impact of US spot-Bitcoin-ETF flows on BTC returns over 2024–2026 using (a) an expected-vs-unexpected flow decomposition via an ARIMA forecasting model and (b) an instrumental-variables design that uses idiosyncratic issuer-level flow — the component of issuer-level flow orthogonal to aggregate flow — as a supply-side instrument for aggregate flow. Local projections provide horizon-specific impulse responses. We find contemporaneous price impact meaningfully below the naive OLS slope reported in practitioner studies, substantial peak response at horizons of 3–7 trading days, and heterogeneity across volatility and drawdown regimes. Falsification tests using pre-ETF equivalents of the instruments and placebo outcomes (e.g., gold) do not produce comparable responses, supporting the identification assumption.
- **Hypotheses:**
  - H1: OLS estimates of contemporaneous BTC-price elasticity to cumulative ETF flow overstate the causal effect.
  - H2: Local-projection IRFs peak at 3–7 days post-flow, not at 0.
  - H3: Price impact is larger during high-VIX and drawdown regimes.
- **Data blocks:** Flow (Farside by issuer), BTC price and returns, macro controls, equity controls, placebo outcomes (GLD), pre-ETF equivalent (CME futures open interest change).
- **Sample design:** Daily, 2024-01-11 → 2026-04-17; pre-ETF falsification window 2021-01 → 2023-12.
- **Baseline model family:** OLS with HAC; Jordà local projections; 2SLS IV.
- **Robustness model family:** Kalman filter for expected-flow state; Oster (2019) sensitivity; alternative ARIMA orders; issuer-level cross-validation; Newey-West lag selection; heterogeneity cuts by VIX, funding rate, drawdown regime.
- **Acceptable ML:** None required. XGBoost model of expected flow as alternative first stage (diagnostic only).
- **Empirical workflow:**
  1. Build issuer-level flow panel (Farside).
  2. Fit ARIMA(p,d,q) on aggregate flow; store innovations.
  3. Build issuer-idiosyncratic flow: residuals from regressing each issuer's flow on aggregate (excluding that issuer).
  4. OLS baselines of BTC return on total flow and flow innovations.
  5. Local projections with horizons 0–20.
  6. 2SLS IV using issuer-idiosyncratic flow; report first-stage F.
  7. Falsification with GLD and with pre-ETF CME OI-change analogue.
  8. Heterogeneity and sensitivity battery.
- **Contribution vs. literature:** First peer-reviewable econometric identification of ETF-flow price impact in crypto. Existing practitioner work is correlational.
- **Key differentiators:** (i) Explicit expected-vs-unexpected decomposition; (ii) issuer-level IV; (iii) Jordà LP rather than static regression; (iv) falsification tests.
- **Feasibility for MSc team:** Strong. Estimated ~10–12 weeks for MVP, 16–20 for strong version.

### Proposal C — "Premium Collapse": The Digital Asset Treasury Premium and the Asymmetric Beta of MicroStrategy (M3)

- **Abstract.** We document and decompose the compression of the Digital Asset Treasury (DAT) premium from ~4× mNAV at the 2024 peak to ~1.16 by March 2026 and its implications for MicroStrategy's equity-return dynamics. Using a multi-DAT panel (where feasible from Artemis) and a regime-switching model of MSTR-to-BTC beta, we show that MSTR's return loading on BTC is strongly asymmetric — BTC × leverage on the upside but BTC × leverage × mNAV-compression on the downside — and we provide an instrumented decomposition of the mNAV compression using cross-DAT dilution-supply shocks. We argue the collapse is consistent with a classic premium-unwind under crowded-issuance dynamics rather than with a re-pricing of BTC credit risk.
- **Hypotheses:**
  - H1: The MSTR-BTC β is regime-dependent, with significantly larger downside β during BTC-drawdown regimes.
  - H2: mNAV Δ is explained by DAT-industry dilution pace, BTC drawdown-regime, and equity-market risk appetite.
  - H3: MSTR returns decompose approximately as β_BTC·ret_BTC + β_mNAV·Δ(mNAV) + β_eq·ret_SPY.
- **Data blocks:** DAT holdings and mNAV (Artemis), MSTR and comparator stocks (TradingView), BTC price/drawdown, macro/equity controls.
- **Sample design:** Daily, 2020-08-10 → 2026-04-17. Core analysis window 2022-01-01 → 2026-04-17.
- **Baseline model family:** Rolling 63-day OLS with HAC; Markov regime-switching; Bai-Perron on mNAV.
- **Robustness model family:** Alternative window lengths; Hamilton filter for regime; placebo (COIN, MARA, RIOT) cross-sections; IV using cross-DAT dilution as instrument for MSTR-specific mNAV.
- **Acceptable ML:** SHAP on mNAV Δ for exploratory variable importance.
- **Empirical workflow:**
  1. Extract DAT Bitcoin Count and NAV from Artemis, confirm DAT-level granularity (if only BTC-DAT-aggregate is available, scope tightens to MSTR vs. aggregate-DAT-industry).
  2. Build mNAV timeline; event-annotate major issuance/crowding dates.
  3. Regress MSTR return on BTC return and mNAV Δ; decompose via Shapley.
  4. Fit 2-state Markov regime model on BTC drawdown; estimate regime-dependent β.
  5. Bai-Perron on mNAV level.
  6. IV with industry dilution.
  7. Robustness and comparator equities.
- **Contribution vs. literature:** First econometric treatment of the DAT-premium collapse; novel asymmetric-β decomposition.
- **Key differentiators:** (i) Regime-switching β with explicit mNAV-compression channel; (ii) industry-dilution IV; (iii) panel extension using full DAT universe.
- **Feasibility for MSc team:** Moderate-strong. Data-granularity risk (DAT-level panel in Artemis) must be verified in week 1. Estimated 12–16 weeks MVP, 20–26 weeks for strong version.

---

## 7. Best Overall Main Project

**Winner: Proposal A (M1) — "What the ETF Bought and What It Broke": Structural Change in the Factor Pricing of Bitcoin.**

**Why it wins.**
1. **Directly uses the dataset's best angle.** The inventory's unique strength is the simultaneous availability of ETF flow, on-chain, derivatives, macro, and equity factors at daily frequency across the break. No competing proposal leverages more of the inventory.
2. **Question-first, not method-first.** The central question — what changed when the ETF launched — is clearly important in 2026, clearly unresolved in the academic literature, and clearly answerable with the data in hand.
3. **Methodologically conservative.** Partial-R² decomposition, Bai-Perron, block regressions, rolling windows — nothing exotic, no ML dependence, everything replicable by a careful referee.
4. **Low data-risk.** Every required series is already in the inventory. No conditional feasibility.
5. **Narrative power.** The paper can be written so that non-specialists understand the claim in two sentences, which is a significant advantage in publication and practitioner reception.

**Why the others are weaker.**
- *Proposal B (M5)* is econometrically sharper but narrower in scope and depends critically on an IV exclusion restriction that reviewers will contest. It is a strong second paper, but defending the instrument absorbs more of the paper's real estate than is ideal for a flagship.
- *Proposal C (M3)* has the highest novelty but also the highest data-granularity risk (DAT panel availability in Artemis), the thinnest cross-section (MSTR is the dominant observation), and the weakest external validity — the result describes a specific corner of the crypto-equity market, not the crypto factor structure per se.

**Immediate next steps (week 1–2):**
1. **Data audit.** Open each CSV listed under Artemis, FRED, Farside, CryptoQuant, TradingView that corresponds to the 40–50 variables named in Proposal A. Confirm non-missingness, frequency, date ranges. Produce a data-readiness memo.
2. **Stationarity and alignment.** Run ADF/PP/KPSS on each candidate DV and regressor. Decide differencing convention. Produce an aligned daily panel as a parquet.
3. **Block definition freeze.** Commit to block membership before running any regressions. Pre-register hypotheses H1–H4 in an internal protocol document dated before any econometric work.
4. **Baseline estimation.** Run full-sample and pre/post OLS; produce block partial-R² table and rolling-R² plot.
5. **Break estimation.** Run Bai-Perron with 0–5 breaks, BIC-selected; Chow at candidate dates.
6. **Freeze robustness battery before seeing results.** Specify the exact robustness checks that will be run regardless of outcome.

---

## 8. Experimental / Adjacent Ideas (Explanatory Framing)

These are exploratory, complementary, or methodologically adventurous ideas. They are not return-prediction or strategy projects. They are either narrower in scope, more speculative, or primarily diagnostic/descriptive.

### E1. PCA of the Full On-Chain Factor Zoo Across Regimes
- **Thesis:** The 15–30 popular on-chain indicators reduce to 3–5 principal components whose loadings are regime-dependent; the regime structure itself is informative.
- **DVs/targets:** None — the paper is about the structure of the on-chain factor space.
- **Framework:** PCA on rolling 126-day windows; compare loadings across regimes identified externally (bull/bear/consolidation via Markov on BTC return).
- **Criticism:** PCA instability; arbitrary rotation choices. **Defense:** Procrustes alignment across windows.
- **Feasibility 10 / Novelty 5 / Publication defensibility 6. PURSUE as companion to M6.**

### E2. Wavelet Coherence Between BTC/ETH and Macro/Equity Blocks
- **Thesis:** The BTC–macro and BTC–equity relationships operate at different frequency bands; the wavelet-coherence band structure is itself diagnostic.
- **Framework:** Continuous wavelet coherence; cross-wavelet phase.
- **Feasibility 9 / Novelty 5 / Publication defensibility 6. PURSUE as robustness to M10.**

### E3. Network Topology of the Stablecoin Complex
- **Thesis:** USDT, USDC, DAI, USDe and minor stablecoins form a substitution network whose topology has changed post-Terra-collapse and post-2024 USDC banking-risk events.
- **Framework:** Minimum-spanning tree on stablecoin-return correlations; partial-correlation networks; community detection.
- **Feasibility 8 / Novelty 6 / Publication defensibility 6. PURSUE.**

### E4. Regime Identification via HMM on BTC Return, Vol, and Flow Tuple
- **Thesis:** A 3-state HMM over the joint (return, realized-vol, ETF-flow) space identifies regimes that are interpretable (e.g., risk-on-with-flow, drift, stress) and have differential macro-beta.
- **Framework:** HMM; then regime-conditional regressions.
- **Feasibility 9 / Novelty 5 / Publication defensibility 6. PURSUE as diagnostic companion.**

### E5. Fear & Greed Index — Decomposition and Redundancy Audit
- **Thesis:** F&G is a composite index; its components differ in information content, and the aggregate is dominated by momentum/volatility components that are redundant with price-based factors.
- **Framework:** If component-level F&G is sourceable (the inventory lists only aggregate — flag as potential data gap); LASSO/PCA; redundancy analysis.
- **Feasibility 5 (conditional on component availability) / Novelty 5 / Publication defensibility 5. NARROW / POSSIBLE BLOG-POST.**

### E6. Miner-Flow Exhaustion: Post-Halving Structural Analysis
- **Thesis:** The 2024 halving shrank miner selling pressure to a level where miner-flow-based indicators (Puell, Miner-Netflow, Thermocap) have mechanically lost most of their pre-2024 signal strength.
- **Framework:** Comparative pre/post-halving miner-flow magnitudes and their regression loadings on BTC returns.
- **Feasibility 10 / Novelty 6 / Publication defensibility 6. PURSUE as a 4–6 week side paper.**

### E7. Cross-Correlation Asymmetry Between CME Basis and Funding Rate
- **Thesis:** CME basis and perps funding rate are both positive-carry signals; their *divergence* (not either alone) identifies institutional-vs-retail leverage regimes.
- **Framework:** Spread regression; lead-lag analysis (Hayashi-Yoshida, or standard daily cross-correlogram); structural break.
- **Feasibility 9 / Novelty 7 / Publication defensibility 7. PURSUE.**

### E8. A Taxonomy of Liquidation Cascades (2020–2026) via Clustering
- **Thesis:** Five identifiable cascades (May-2021, Nov-2022, Mar-2023, Aug-2024, Oct-2025) cluster into two types — leverage-unwind and macro-shock — with distinct pre-event and post-event signatures.
- **Framework:** Hierarchical clustering on event-window feature vectors; narrative mapping; comparative event windows.
- **Feasibility 9 / Novelty 7 / Publication defensibility 7. PURSUE — strong companion to M8.**

### E9. TVL Network: DeFi Chain-Level Connectedness and the "L2 Era"
- **Thesis:** Ethereum L2 proliferation (Arbitrum, Optimism, Base, Scroll, etc.) changes chain-level TVL connectedness post-2023; TVL now redistributes across chains in ways that are masked by aggregate TVL.
- **Framework:** Diebold-Yilmaz on chain-level TVL Δ; before/after L2 event dates.
- **Feasibility 8 / Novelty 6 / Publication defensibility 6. PURSUE.**

### E10. Korea Premium as a Pure Retail-Sentiment Benchmark
- **Thesis:** Korea Premium, after FX and capital-control adjustments, has retained its retail-sentiment information content over 2017–2026 while US-centric premia (Coinbase) have not.
- **Framework:** Time-varying VAR; comparative persistence, half-life, and response to attention shocks.
- **Feasibility 6 (USD/KRW FX required from outside inventory) / Novelty 6 / Publication defensibility 6. NARROW.**

### E11. Fear & Greed Level as Cross-Sectional Sorting Variable Across Crypto Betas
- **Thesis:** F&G regime does not predict returns, but it organizes the cross-section of factor sensitivities — macro-β, equity-β, funding-β all vary with F&G level.
- **Framework:** Cross-sectional regression of rolling-β on F&G quantile.
- **Feasibility 10 / Novelty 5 / Publication defensibility 5. WEAK — keep as blog / working-paper side analysis.**

### E12. Anomaly Detection on the Full Factor Panel as a Systemic-Stress Diagnostic
- **Thesis:** A multivariate anomaly detector (Isolation Forest, Mahalanobis) on the factor panel flags the same historical stress dates (FTX, Terra, SVB, Oct-2025) and provides a transparent systemic-stress index for crypto.
- **Framework:** Rolling anomaly scoring; date-matching against narrative stress events.
- **Feasibility 9 / Novelty 5 / Publication defensibility 5. PURSUE as diagnostic.**

### E13. FRED-Liquidity Shocks and Stablecoin Supply: Substitute or Complement?
- **Thesis:** Stablecoin supply Δ and macro-liquidity indicators (WALCL, RRP-drawdown, SOFR spreads) are complementary during risk-on and substitutes during stress.
- **Framework:** Threshold-VAR or smooth-transition VAR with a VIX or NFCI threshold.
- **Feasibility 8 / Novelty 7 / Publication defensibility 7. PURSUE — strong companion to M7.**

### E14. Identifying Regime Transitions via Spectral Decomposition of Rolling Correlation Matrices
- **Thesis:** The top eigenvalue of rolling BTC-factor correlation matrices tracks "single-factor dominance" and spikes near stress events; its dynamics identify regime shifts.
- **Framework:** Rolling spectral analysis; comparison to MS-model transitions.
- **Feasibility 9 / Novelty 6 / Publication defensibility 6. PURSUE as methodological companion.**

### E15. A Granular Audit of the Coinbase Premium in the AP-Arbitrage Era
- **Thesis:** Daily-resolution Coinbase Premium Δ is almost fully explained post-ETF by IBIT NAV-deviation Δ and issuer-flow Δ, consistent with AP arbitrage dominating retail demand at that venue.
- **Framework:** High-frequency regression of Coinbase Premium on AP-arb proxies.
- **Feasibility 7 / Novelty 7 / Publication defensibility 7. PURSUE — lead-in to M12.**

---

## 9. Ranking of Experimental Ideas

| Rank | ID | Short title | Feas. | Nov. | Pub. | Composite |
|---|---|---|---|---|---|---|
| 1 | E8 | Liquidation-cascade taxonomy | 9 | 7 | 7 | **7.6** |
| 2 | E7 | Basis vs. funding divergence | 9 | 7 | 7 | **7.6** |
| 3 | E13 | Liquidity vs. stablecoin substitution | 8 | 7 | 7 | **7.3** |
| 4 | E15 | Coinbase Premium AP-arbitrage audit | 7 | 7 | 7 | **7.0** |
| 5 | E3 | Stablecoin network topology | 8 | 6 | 6 | **6.6** |
| 6 | E6 | Miner-flow exhaustion | 10 | 6 | 6 | **7.2** |
| 7 | E9 | L2-era TVL connectedness | 8 | 6 | 6 | **6.6** |
| 8 | E14 | Spectral regime detection | 9 | 6 | 6 | **6.9** |
| 9 | E2 | Wavelet coherence | 9 | 5 | 6 | **6.6** |
| 10 | E1 | On-chain PCA zoo | 10 | 5 | 6 | **6.9** |
| 11 | E4 | HMM on (return, vol, flow) | 9 | 5 | 6 | **6.6** |
| 12 | E12 | Anomaly-detection stress index | 9 | 5 | 5 | **6.2** |
| 13 | E10 | Korea Premium retail benchmark | 6 | 6 | 6 | **6.0** |
| 14 | E5 | F&G decomposition | 5 | 5 | 5 | **5.0** |
| 15 | E11 | F&G as cross-sectional sorter | 10 | 5 | 5 | **6.5** |

(Composite as above.)

---

## 10. Top 5 Experimental Ideas

### ★ E8 — Liquidation-Cascade Taxonomy
- **Why it matters:** Gives M8 a natural generalization. Produces a practitioner-relevant typology with implications for systemic-risk monitoring.
- **Risk:** Small-n; cluster stability.
- **MVP:** Five events, feature vectors, hierarchical clustering.
- **Stronger version:** Bootstrap-stabilized clustering; narrative validation; out-of-sample application to any new cascade.

### ★ E7 — Basis vs. Funding Divergence
- **Why it matters:** The CME-basis / perp-funding spread is a natural institutional-vs-retail leverage wedge; its structural breaks are interpretable.
- **Risk:** Time-series alignment across CME and CryptoQuant.
- **MVP:** Daily spread series; break tests; event overlay.
- **Stronger version:** Two-regime VAR with spread-threshold; cross-exchange decomposition of funding (Binance, Bybit, OKX if data available).

### ★ E13 — FRED-Liquidity vs. Stablecoin Supply: Substitute or Complement
- **Why it matters:** Direct test of the "stablecoin as crypto-native Fed balance sheet" narrative. Clean econometric design.
- **Risk:** Threshold identification.
- **MVP:** TVAR with VIX threshold on BTC return, stablecoin-supply Δ, WALCL Δ.
- **Stronger version:** Smooth-transition VAR; FEVDs by regime; ETH parallel.

### ★ E15 — Coinbase Premium AP-Arbitrage Audit
- **Why it matters:** Sharpens the mechanism story for M12. Uses the IBIT premium-to-spot series, which is relatively unexploited in the literature.
- **Risk:** Post-ETF sample only.
- **MVP:** OLS of Coinbase Premium Δ on IBIT premium Δ and issuer flow Δ.
- **Stronger version:** High-frequency regression if intraday IBIT data is available; pre/post ETF split.

### ★ E3 — Stablecoin Network Topology
- **Why it matters:** Generates a clean, visualizable structural map of the stablecoin complex; publishable as a mapping/descriptive paper with stress-period overlays.
- **Risk:** Network-stability specification choices.
- **MVP:** Minimum-spanning-tree on daily returns of top-10 stablecoins; pre/post major events.
- **Stronger version:** Community detection; spillover variants.

---

## 11. Experimental ↔ Main Integration Recommendations

Three experimental ideas should be *folded into* the Main top-3 rather than published separately. Two should sit as companion papers. The rest should remain standalone or sidelined.

**Fold into M1 (Proposal A):**
- **E1 (On-chain PCA zoo)** — becomes the factor-orthogonalization step within the on-chain block. Gives Proposal A a transparent way to handle mechanical on-chain correlation without exotic ML.
- **E14 (Spectral rolling-correlation regimes)** — becomes the regime-visualization companion to Proposal A's structural-break analysis. The top-eigenvalue plot is a compelling figure for the paper.

**Fold into M5 (Proposal B):**
- **E15 (Coinbase Premium AP-arb audit)** — becomes a mechanism/auxiliary-evidence section for Proposal B. If ETF flows are driving BTC prices via AP arbitrage, the Coinbase Premium should reflect that mechanically, and E15 quantifies it. This strengthens Proposal B's identification story.

**Fold into M8 / M3 (Proposals C and the liquidation event study as a secondary paper):**
- **E8 (Liquidation taxonomy)** — effectively *is* the stronger version of M8. Recommend merging: the event-study-plus-taxonomy is a single paper.
- **E7 (Basis vs. funding divergence)** — functions as pre-event warning-signal analysis inside M8. Absorbed into M8's pre-event logit.

**Keep as companion papers (separate publication):**
- **E13 (Liquidity vs. stablecoin substitution)** — methodologically different (TVAR) enough to warrant separate publication; companions M7 but stands on its own.
- **E6 (Miner-flow exhaustion)** — short, focused, and publishable on its own; a natural 6–8 week side paper for a second team member.

**Keep as exploratory or internal:**
- **E2, E4, E9, E11, E12** — useful diagnostics and internal robustness work, not headline papers. They strengthen the main projects without themselves being publication targets.

**Sideline:**
- **E5 (F&G component decomposition)** — requires component-level data the inventory doesn't appear to contain; reframe as a blog post only if that data can be added.
- **E10 (Korea Premium retail benchmark)** — requires USD/KRW FX; narrower than M12. Reject unless scope is expanded with external data.

**Net recommendation on portfolio shape:** Pursue Proposal A as flagship, Proposal B as second paper, the merged M8+E8 event-study paper as third publication target, and M3/Proposal C as higher-risk/higher-novelty fourth project contingent on DAT-level data being present in Artemis. E13 and E6 are appropriate side papers for an MSc or junior-PhD cohort. All other experimental ideas should enter as figures, tables, or robustness checks inside the main papers.

---

*End of memo.*
