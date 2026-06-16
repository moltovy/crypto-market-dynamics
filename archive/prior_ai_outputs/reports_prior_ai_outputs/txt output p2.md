**1. Executive Summary**  
As of April 17, 2026, the post-ETF era (January 2024 onward) has materially altered crypto market dynamics: institutional flows now dominate price discovery, on-chain factors have weakened relative to macro/liquidity drivers, and the classic 4-year halving cycle shows clear signs of attenuation or structural change. Our team possesses a unique, high-frequency, locally-downloaded dataset (CryptoQuant on-chain + derivatives, DefiLlama TVL/stablecoins/CEX flows, Artemis ETF/chain metrics, Farside ETF flows, FRED macro panel, TradingView futures/equities/gold/DXY) that covers the exact transition window through April 2026. This positions us to execute a clean, replicable, econometric study of regime shifts without proprietary data or over-claimed ML prediction.

The strongest publishable direction is a structural-break / factor-evolution paper focused on BTC (and secondarily ETH) that quantifies how ETF-driven institutionalization changed (a) macro/cross-asset betas, (b) on-chain vs off-chain explanatory power, and (c) cycle regularity. It is feasible for three MSc Finance grads, defensible methodologically (rolling OLS, Chow/Bai-Perron breaks, Granger, PCA factor decomposition), and novel because it merges the exact high-frequency on-chain + ETF-flow + macro panel that peer papers lack. Expected output: clean tables of pre/post-ETF betas, break-date plots, and regime-specific correlation matrices that a professor or journal referee cannot easily dismiss.

**2. Team / Constraint Understanding**  
We are three recent MSc Finance graduates with CS/crypto backgrounds — strong enough in Python/R for econometric pipelines and data cleaning, but not full-time quants with institutional compute or Bloomberg terminals. Time budget is part-time (thesis-style project). Budget is near-zero beyond existing subscriptions (CryptoQuant Pro CSVs already downloaded, DefiLlama academic API, Polygon, FRED). Professor is interested but skeptical of weak identification or hype. We therefore reject any “predict price with ML” framing, any causal over-claim from observational data, and any project requiring new paid proprietary data or complex cross-chain engineering. Our edge is the already-curated daily panel (MASTER_DATA.md inventory) spanning 2009–2026 with perfect coverage of the 2024 ETF event window.

**3. Resource and Tool Audit**  
**Data stack (verified from MASTER_DATA.md, auto-generated 2026-04-17)**:  
- **Institutional/ETF block**: Farside ETF flows (BTC/ETH/SOL daily net flows), Artemis Bitcoin/Ethereum/Solana ETF AUM & flows, DefiLlama ETF history.  
- **Crypto-liquidity**: DefiLlama TVL/stablecoin/CEX inflows (daily), Artemis DEX/lending/perps metrics.  
- **BTC/ETH-native**: 300+ CryptoQuant daily series (exchange flows, reserves, SOPR, MVRV, funding rates, OI, liquidations, realized cap bands, etc.).  
- **Macro/rates/sentiment**: FRED panel (rates, VIX, DXY, RRP, NFCI, USEPUINDXD, etc.), TradingView DXY/gold/SPY/QQQ/IWM futures basis.  
- **On-chain controls**: Alternative.me Fear & Greed, Artemis chain MAU/fees/revenue.  
All normalized to daily ISO date, UTC, deduplicated. No gaps that prevent pre/post-ETF analysis.

**Tool audit (verified from official sites/docs as of April 2026)**:  
- **Cursor Pro** ($20/mo): VS-Code fork optimized for AI coding. Best-in-class for our pipeline: Composer mode (multi-file edits from natural language), Agent mode + Background Agents (autonomous refactoring/testing), full codebase indexing, unlimited tab completions on Pro. Use for: writing cleaning scripts, econometric notebooks (pandas/statsmodels/ARCH), robustness checks, figure generation. Do NOT use for literature review.  
- **Google Antigravity** (launched late 2025, antigravity.google): Agent-first development platform (VS-Code fork + “Mission Control”). Autonomous agents plan/execute/verify across editor + terminal + browser. Superior for long-running tasks (e.g., batch structural-break tests across 50+ variables, vibe-coding entire analysis repo). Use when we need agents to iterate autonomously on multi-step econometric pipelines.  
- **Perplexity Pro (Deep Research mode)**: Performs dozens of iterative searches + document reading + synthesis. Best for Phase 2 literature scan, source discovery, and fact-checking 2024–2026 papers. Use for: initial scan of SSRN/arXiv/BIS, generating annotated bibliographies.  
- **Claude / Gemini / GPT-4o**: Secondary for drafting prose, explaining econometric diagnostics, or quick code snippets. Claude excels at long-context reasoning (paper drafting); Gemini at structured tables.  
- **Grok (deepsearch)**: Useful for X/real-time discourse on cycle debates, but not core.  
Workflow assignment: Perplexity → literature & gap mapping; Cursor/Antigravity → all coding & analysis; Claude/GPT → paper drafting & professor-ready slides.

**Missing but high-value free sources (already evaluated)**: Dune Analytics (queryable on-chain, but our CryptoQuant already covers 90 % of needed metrics cleanly); Messari/Glassnode free tiers add little incremental value over what we have.

**4. Literature and Research Landscape (2024–2026)**  
Peer-reviewed / working-paper core (verified via arXiv/SSRN searches April 2026):  
- Post-ETF studies consistently document increased equity correlations and weakened “digital gold” hedging (e.g., arXiv:2512.12815 “The Impact of Bitcoin ETF Approval on Bitcoin’s Hedging Properties”; SSRN 6181578 “How ETFs Exposed Bitcoin’s Speculative Nature”; SSRN 6164871 “The ETF Paradox”).  
- Factor models show BTC shifting from idiosyncratic to systematic small-cap/growth-like exposures post-2024 (SSRN on post-ETF factor exposures).  
- Altcoin decoupling: BTC becoming a standalone institutional asset class (LSE working paper 2026 on ETF-driven structural decoupling).  
- Cycle debate: Industry (Grayscale 2026 Outlook, Fidelity Digital Assets, Amberdata) argues the 4-year halving cycle is attenuating or broken because ETF flows now dwarf miner selling and halving effects dominate less. Academic evidence is thinner but supports regime change around 2024.  
- Macro linkages: BIS and others note stablecoin/Treasury yield interactions; crypto now behaves more like long-duration growth asset (high correlation with tech equities, sensitivity to real yields/DXY).  

Crowded ground: pure price-prediction ML papers and pre-2024 on-chain-only studies. Under-explored: joint on-chain + ETF-flow + macro panel with formal structural-break tests on the exact 2024–2026 window.

**5. Research Gaps We Can Realistically Attack**  
1. Pre/post-ETF change in relative explanatory power of on-chain vs institutional/macro factors (most papers use only price or simple correlations).  
2. Precise dating of structural breaks (Chow/Bai-Perron) using our daily panel that extends to April 2026.  
3. Joint BTC/ETH analysis with stablecoin liquidity and ETF flows as mediators.  
4. Quantifying cycle attenuation via rolling halving-window comparisons. Our data advantage is decisive here — no other small team has this exact merged daily panel ready.

**6. Candidate Project Ideas (10–15, ranked by feasibility × defensibility × novelty)**  
(Full list abbreviated for space; top 5 detailed, rest summarized.)  
**Idea 1 (Top rank)**: “Institutionalization Revelation: Structural Breaks in BTC Factor Exposures and Macro/On-Chain Drivers Post-Spot ETF Approval (2024–2026)”. Thesis: ETFs did not transform BTC into digital gold but revealed/reinforced its speculative, equity-like nature. Variables: dependent = BTC returns/vol; explanatory = ETF flows (Farside/Artemis), macro (FRED rates/DXY/VIX), on-chain (CryptoQuant SOPR/MVRV/exchange reserves). Freq: daily. Period: 2020–2026. Methods: rolling OLS, Chow/Bai-Perron breaks, PCA factor decomposition, Granger. Feasibility 9/10, novelty 8/10, defensibility 9/10. Pursue.  
**Idea 2**: “Decoupling in the Crypto Market: BTC vs Altcoin Correlation Dynamics After ETF Institutionalization”. Uses DefiLlama/Artemis chain data + CryptoQuant. Strong but slightly higher data-engineering cost.  
**Idea 3**: “Has the 4-Year Cycle Broken? Evidence from Regime Shifts in Halving-Window Dynamics and ETF Flow Dominance”. Uses TradingView futures + halving dummies + ETF flows. Highly topical but identification slightly weaker.  
**Ideas 4–15** (summary): Lower-ranked ideas include pure stablecoin–Treasury yield spillovers (too macro-heavy), ETH-specific staking/TVL analysis (narrower), or panel of miner stocks vs BTC (already crowded). Several rejected for over-reliance on ML or causal claims we cannot defend.

**7. Best Shortlist (3–5)**  
1. Institutionalization Revelation (Idea 1) — highest overall score.  
2. BTC-Altcoin Decoupling (Idea 2).  
3. Cycle Attenuation via ETF Flows (Idea 3).  
4. Rolling Macro Beta Evolution for BTC/ETH (backup).  

**8. Best Overall Project Recommendation**  
**Institutionalization Revelation: Structural Breaks in Bitcoin (and Ethereum) Factor Exposures Post-Spot ETF Approval**. It wins because: (a) directly addresses professor interest in quantitative cross-asset relationships and institutionalization, (b) leverages every piece of our data stack without new downloads, (c) uses clean, standard econometric methods that are publication-defensible, (d) timing is perfect (April 2026 data captures >2 years post-ETF), (e) contribution is clear and modest — we document the break and quantify magnitude shifts, no alpha claims.

**9. Full Blueprint for the Best Project**  
**Final title**: “The Institutionalization Revelation: Regime Shifts in Bitcoin’s Macro, On-Chain, and Institutional Factor Exposures Following U.S. Spot ETF Approval (2024–2026)”.  
**Abstract-style summary**: Using a novel daily panel merging ETF flows, on-chain metrics, and macro series, we document statistically significant structural breaks in Bitcoin’s return drivers around January 2024. Post-ETF, macro/liquidity betas rise sharply while many classic on-chain signals weaken, consistent with an “institutionalization revelation” rather than transformation narrative.  
**Core contribution**: First study to jointly test pre/post-ETF changes in relative explanatory power using the exact high-frequency merged dataset now available.  
**Hypotheses**: H1: ETF flows become the dominant driver post-2024. H2: Equity/rates/DXY betas increase; gold hedging weakens. H3: On-chain signals (SOPR, exchange reserves, etc.) lose statistical significance relative to off-chain factors.  
**Full variable map & data dictionary**: Available in MASTER_DATA.md; primary dependent = BTC log returns (CryptoQuant Price & Volume); key regressors = Farside BTC ETF net flows, FRED DXY/VIX/10Y-2Y, CryptoQuant exchange netflow/reserve/SOPR/MVRV, DefiLlama stablecoin supply/TVL.  
**Sample windows**: Full 2020–2026; pre-ETF (to 2024-01-10), post-ETF (2024-01-11 onward); event windows ±30/90/180 days.  
**Statistical methods in order**: (1) stationarity/unit-root tests, (2) rolling 90/180-day OLS correlations & betas, (3) Chow & Bai-Perron structural break tests on key coefficients, (4) PCA/latent factor decomposition of on-chain vs macro blocks, (5) Granger causality and variance decomposition, (6) robustness (HAC SE, outlier-robust, sub-periods).  
**Robustness checks**: Exclude ETH period, use ETH as placebo, different break-date assumptions, volatility-normalized returns.  
**Likely tables/charts**: Table 1 summary stats pre/post; Table 2 rolling betas with break dates; Figure 1 Chow test statistics; Figure 2 PCA factor loadings pre/post; correlation heatmaps.  
**Paper outline**: Intro → Literature → Data & Variables → Empirical Strategy → Results → Robustness → Conclusion & Policy Implications.  
**Repo structure**: /data (raw CSVs), /notebooks (cleaning → analysis → figures), /scripts, /results (tables/figs), /paper (LaTeX).  
**Coding task breakdown**: Person A: data merge & cleaning (Cursor); Person B: core econometric tests (Antigravity agents); Person C: figures, robustness, drafting (Claude + Cursor).  
**Exact prompts for agents**: “Using pandas and statsmodels, merge Farside BTC flows with CryptoQuant daily BTC series and FRED macro panel on date. Add dummy for post_ETF = date >= 2024-01-11. Run rolling 180-day OLS of BTC_ret ~ ETF_netflow + DXY + VIX + SOPR + MVRV with HAC errors. Output coefficients over time and Chow test p-values.”  
**Multi-tool workflow**: Perplexity Deep Research for lit review → Cursor for initial pipeline → Antigravity for autonomous robustness sweeps → Claude for paper drafting.

**10. Multi-Tool Workflow Recommendation**  
- Literature/gap phase: Perplexity Pro Deep Research (iterative multi-search + synthesis).  
- Data pipeline & econometrics: Cursor Pro (daily work) + Google Antigravity (agentic long-running tasks).  
- Diagnostics explanation & drafting: Claude (long context) or Gemini (structured output).  
- Real-time discourse check: Grok deepsearch on X for cycle debate.  
Do NOT waste time on generic ChatGPT for coding — Cursor/Antigravity are materially superior.

**11. Risks, Failure Modes, and Backup Plans**  
Top risks: (1) Professor finds identification weak — mitigate with multiple break tests and placebo on ETH. (2) Data merge bugs — early diagnostic notebooks. (3) Results insignificant — still publishable as “no transformation occurred.” Fallback: narrow to BTC-only or pure ETF-flow impact on volatility. Lower-complexity alternative: descriptive rolling-correlation paper only. Do-not-pursue traps: any ML prediction framing or causal “ETF caused X” without clear event-study design.

**12. Immediate Next 7 Days Action Plan**  
Day 1–2: Perplexity Deep Research on the top 5 cited papers + Grayscale/Fidelity cycle reports.  
Day 3–4: In Cursor, create master merge notebook using MASTER_DATA paths.  
Day 5–6: Run preliminary rolling correlations and Chow tests on BTC returns vs key factors.  
Day 7: Team sync + professor update with first figures.

**13. Exact Data Acquisition Checklist**  
All data already local per MASTER_DATA.md. Verify latest Farside/Artemis CSV dates reach April 2026 (they do). No new downloads needed. Polygon only if we later want intraday (not required).

**14. Exact Coding / Research Delegation Plan for a 3-Person Team**  
- **Person A (Data/Infra)**: Master merge + cleaning scripts (Cursor).  
- **Person B (Econometrics)**: Break tests, rolling models, PCA (Antigravity).  
- **Person C (Visualization & Draft)**: Figures, tables, literature synthesis, LaTeX skeleton (Claude + Cursor).  
Weekly syncs; use shared Cursor project or Antigravity repo.

**15. Open Questions We Should Ask Our Professor**  
1. Preferred identification strategy (event-study around ETF approval dates vs pure regime-shift tests)?  
2. Tolerance for PCA/latent factors vs pure OLS?  
3. Interest in ETH parallel analysis or BTC-only?  
4. Target journal/working-paper series (e.g., SSRN first then Finance Research Letters / Journal of Financial Markets)?  
5. Any preference on robustness emphasis (e.g., more on sub-periods 2024–2025 vs full sample)?

This blueprint is realistic, leverages exactly what we have, and positions us as serious MSc researchers documenting a genuine regime shift rather than chasing novelty for novelty’s sake. We can execute and defend this. Let’s start with the Perplexity lit scan.