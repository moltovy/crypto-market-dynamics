**Research memo: what you can actually publish with the data already in hand**

The short version of my judgment is this: your best paper is **not** an ETF paper, **not** an on-chain-only paper, and **not** a giant kitchen-sink “what moves crypto” omnibus. The strongest path is a **modular, time-varying factor-block paper** on BTC and ETH that asks whether the post-ETF regime changed the **incremental explanatory power** of macro, institutional, crypto-liquidity, and native on-chain/ecosystem blocks. That is the cleanest way to use what you actually have, and it matches the project brief rather than drifting into a weaker adjacent story.   

## 1) What the actual project/data situation is

You do not have a hypothetical dataset. You already have a serious daily research inventory: normalized daily UTC panels across CryptoQuant, Artemis, DefiLlama, FRED, Farside ETF data, TradingView, and Alternative.me, with especially strong BTC depth, usable ETH depth from 2020 onward, ETF/DAT/wrapper layers from 2024 onward, and macro/liquidity overlays that make a real explanatory design possible. The strength is **complementarity**, not just size. The main weakness is **uneven start dates**, which means a single universal full-sample panel would be bad design; this has to be modular by sample window and question.    

The file inventory implies three natural modules. First, a **BTC-heavy long window** built mainly from CryptoQuant BTC + macro + market-structure controls. Second, a **BTC/ETH comparative core** starting around 2021, when ETH derivatives and on-chain comparables are usable. Third, a **post-institutionalization regime module** starting 2024-01-11 for spot BTC ETF flow/AUM analysis and 2024-07-23 for spot ETH ETF analysis. Any design that ignores those window asymmetries is methodologically weaker than it looks.   

Data-source credibility is good enough for a publishable MSc paper if you are disciplined. Artemis positions itself as institutional-grade metrics across crypto, stablecoins, and equities; DefiLlama clearly distinguishes its free and pro APIs and documents methodology; CryptoQuant provides explicit definitions for open interest, funding, leverage, reserve, inflow, outflow, and netflow; Dune is useful as a targeted augmentation layer, but it is **not needed** for the core paper and would probably distract you if introduced too early. ([Artemis Terminal][1])

Three ideas I would eliminate immediately: a pure ETF event paper, a broad ML prediction paper, and a pure DAT paper. The first is too crowded and too short-sample; the second violates your own brief and would be easy to criticize; the third is interesting but still too structurally noisy and thin as a standalone main thesis.  

## 2) Most relevant recent research themes, Nov 2025 to Apr 17, 2026

**A. Institutionalization is no longer a side note; it is market structure.** CME announced 24/7 crypto futures and options trading starting May 29, 2026, and CME’s Q1 2026 crypto update reported average daily open interest of 313.9K contracts, up 25% year over year. At the same time, SEC exchange-rule activity around options on spot crypto ETFs broadened the wrapper layer around BTC and ETH. Methodologically, this pushes the literature toward **lead-lag**, **basis**, **wrapper-premium**, **flow transmission**, and **calendar-friction** designs rather than simple event studies. ([CME Group][2])

**B. Stablecoins have moved from “crypto plumbing” to macro-financial relevance.** BIS, IMF, ECB, and the Fed are now treating stablecoins as channels that matter for FX markets, short-end Treasury pricing, bank funding, and monetary transmission. BIS documents spillovers from stablecoin-based FX into traditional FX; another BIS paper links stablecoin inflows to lower T-bill yields using local projections and IV; IMF’s 2026 paper develops stablecoin shock measures with heteroskedastic identification; ECB studies deposit substitution and monetary-policy transmission; the Fed’s April 2026 note puts aggregate stablecoin market cap at $317 billion as of April 6, 2026. This is a major clue: a serious crypto paper in 2026 can no longer treat stablecoins as a minor control variable. ([Bank for International Settlements][3])

**C. The frontier is hybrid on-/off-chain explanatory modeling, not pure on-chain storytelling.** Recent work explicitly asks how on-chain and off-chain demand/supply drivers jointly explain Bitcoin, while other 2026 work revisits hidden-factor structures in crypto pricing. The implication for your project is straightforward: the best contribution is not “one magic factor,” but **block-level competition** among macro, institutional, liquidity, and native variables. ([arXiv][4])

**D. Cross-chain substitution and negative spillovers are becoming serious research themes.** A 2026 arXiv paper on cross-chain negative spillovers argues that surges on one chain can coincide with declines on others, especially around attention shocks, which is a useful warning against assuming “more crypto activity” is one-dimensional. For you, that mainly matters as a reason to avoid simplistic chain-activity aggregates and to treat ETH’s ecosystem variables differently from BTC’s native metrics. ([arXiv][5])

**E. Derivatives stress is being reframed as a structural transmission mechanism, not just a trading metric.** Recent work on exogenous stress and runs on perpetual futures, combined with official metric definitions around funding, estimated leverage ratio, open interest, and exchange flows, supports a cleaner explanatory paper on how leveraged positioning amplifies spot stress episodes. That is a good secondary track, but it is more likely a strong subpaper than the single best flagship paper. ([SSRN][6])

**F. Public-market wrappers and treasury vehicles are now a real transmission layer.** The growth of ETF wrappers, listed crypto proxies, and digital-asset treasury vehicles is now large enough that it can plausibly affect the information path into crypto markets. Practitioner research is ahead of academia here, which means novelty is available, but reviewer skepticism will also be high. That makes wrappers a very good paper or appendix topic if kept tightly empirical and market-structure focused. ([DeFi Llama][7])

## 3) MAIN paper ideas that are realistically executable now

### M1. **From Crypto-Native to Hybrid Macro–Institutional: Time-Varying Factor Blocks in BTC and ETH**

**Thesis:** BTC and ETH did not simply “financialize”; the post-ETF regime changed the *relative explanatory power* of macro, institutional, crypto-liquidity, and native blocks, with BTC likely shifting faster than ETH.
**RQ:** How did block-level explanatory importance change over time, and where do structural breaks actually occur?
**Why 2026:** This is the cleanest response to ETF institutionalization without reducing the paper to ETFs.
**Why feasible:** The inventory already contains all four blocks at daily frequency: FRED/TradingView macro, Farside/Artemis/TradingView/CQ institutional proxies, DefiLlama/Artemis/CQ liquidity variables, and rich BTC/ETH native metrics.    
**DVs:** BTC and ETH daily log returns; 7-day and 30-day realized volatility; BTC-ETH relative return as a secondary DV.
**Factor blocks:** Macro/rates/liquidity; institutional flows/wrappers; crypto-liquidity/stablecoin/DEX/CEX; native BTC/ETH on-chain and derivatives.
**Freq/sample:** Daily; main comparison 2021-01 to 2026-04; BTC extension 2018-01 to 2026-04; institutional submodule from 2024-01 and 2024-07 for ETH ETF effects.
**Framework:** Block compression, rolling OLS, rolling partial (R^2), SUR for BTC/ETH, Bai-Perron/Chow/CUSUM breaks, local projections for selected shocks.
**Support ML:** Sparse PCA or elastic-net screening within blocks only.
**Main exhibits:** Stacked rolling partial-(R^2) charts; break-date timeline; block heatmaps; pre/post ETF coefficient tables.
**Likely criticisms:** Too many variables; data mining; endogeneity; BTC/ETH asymmetry.
**Defense:** Pre-specify block hierarchy; use slim baseline block representatives; claim explanatory dominance, not causality; keep modular windows.
**Scores:** Feasibility 9 | Novelty 7 | Publication defensibility 9
**Recommendation:** **Pursue**

### M2. **Did BTC Financialize Faster Than ETH?**

**Thesis:** BTC and ETH have not converged into one institutional asset class; BTC likely became more wrapper/macro-sensitive, while ETH retained stronger ecosystem dependence.
**RQ:** Is there a measurable post-2024 divergence in factor sensitivity between BTC and ETH?
**Why 2026:** Cleaner than a giant BTC/ETH comparison and directly tied to the post-ETF regime.
**Why feasible:** ETH has sufficient derivatives and native data from 2020 onward, plus ETF flows from July 2024 onward.  
**DVs:** BTC and ETH daily returns, 30-day volatility, ETH/BTC relative performance.
**Factor blocks:** Same four blocks as M1, but only with the top 2–4 representatives per block.
**Freq/sample:** Daily, 2021-01 to 2026-04; ETF subperiod 2024-07 onward.
**Framework:** SUR/system regressions, interaction terms by asset and regime, rolling betas, incremental (R^2).
**Support ML:** None beyond variable screening.
**Main exhibits:** Differential rolling betas; BTC-minus-ETH block importance chart; regime-interaction tables.
**Likely criticisms:** Too close to M1; contribution may feel incremental.
**Defense:** Make it the narrow version if the professor wants a crisper thesis.
**Scores:** Feasibility 9 | Novelty 6 | Publication defensibility 8
**Recommendation:** **Narrow**

### M3. **Who Leads Now? Listed Wrappers, CME Basis, ETF Flows, and Daily Price Transmission**

**Thesis:** In the institutional regime, price transmission increasingly runs through ETF flows, wrapper premia, and regulated-futures basis rather than purely native spot/on-chain channels.
**RQ:** Do ETF flows, CME basis, and wrapper dislocations now explain same-day/next-day BTC and ETH moves better than before?
**Why 2026:** This sits exactly at the intersection of spot ETFs, CME expansion, and 24/7-vs-business-hours frictions. ([CME Group][2])
**Why feasible:** You already have Farside flows, Artemis AUM, IBIT/ETHA-over-spot series, CME BTC/ETH basis/ratio series, and Coinbase premium/fund metrics.   
**DVs:** BTC/ETH daily returns; Monday reopen effects; wrapper premium changes.
**Factor blocks:** ETF net flows/AUM, wrapper-over-spot ratios, CME basis/ratio, Coinbase premium, fund holdings.
**Freq/sample:** Daily; BTC 2024-01-11 to 2026-04; ETH 2024-07-23 to 2026-04.
**Framework:** Business-day aligned distributed lags, VAR/Granger, FEVD, event studies around extreme flow days, Friday–Monday subsamples.
**Support ML:** None needed.
**Main exhibits:** Flow-event cumulative-return charts; CME-basis lead-lag tables; weekend/friction comparison charts.
**Likely criticisms:** Daily data are too coarse for “price discovery.”
**Defense:** Do **not** call it intraday price discovery; call it **daily transmission and timing frictions**.
**Scores:** Feasibility 8 | Novelty 8 | Publication defensibility 8
**Recommendation:** **Pursue**

### M4. **Stablecoin Plumbing and the Price of Crypto Risk**

**Thesis:** Stablecoin supply, transaction volume, and exchange-available dollar liquidity have become a first-order explanatory state variable for BTC and ETH.
**RQ:** When does the stablecoin block add explanatory power beyond macro and native crypto variables?
**Why 2026:** Stablecoins are now macro-financially relevant, not just DeFi mechanics. ([Bank for International Settlements][3])
**Why feasible:** Your inventory is unusually strong here: DefiLlama stablecoins/CEX, Artemis stablecoin supply/tx/P2P/regional series, and CryptoQuant stablecoin ratios.  
**DVs:** BTC/ETH returns, volatility, funding, basis.
**Factor blocks:** Stablecoin total supply, by chain/token, tx volume, active addresses, P2P volume, CQ SSR/exchange stablecoin ratio, CEX net inflows.
**Freq/sample:** Daily main sample from 2022-11 to 2026-04; monthly regional appendix.
**Framework:** Rolling OLS, partial (R^2), block orthogonalization, local projections to large stablecoin-flow shocks.
**Support ML:** Sparse PCA inside the stablecoin block.
**Main exhibits:** Stablecoin block partial-(R^2) over time; large-supply-shock impulse charts; block-subsumption tables.
**Likely criticisms:** High endogeneity; same-cycle variable.
**Defense:** Keep the claims explanatory and state-dependent, not causal.
**Scores:** Feasibility 8 | Novelty 8 | Publication defensibility 8
**Recommendation:** **Pursue**

### M5. **Perpetual Leverage, Exchange Flows, and the Anatomy of Crypto Stress**

**Thesis:** The key mechanism in major BTC/ETH drawdowns is not “sentiment” in the abstract but the interaction between leverage, forced liquidations, and exchange-available supply.
**RQ:** How do leverage and exchange-flow variables explain stress episodes before and after ETF institutionalization?
**Why 2026:** Strong because official/academic attention is shifting toward structural derivatives stress. ([SSRN][6])
**Why feasible:** CryptoQuant depth is excellent for BTC and good for ETH on funding, OI, ELR, liquidations, taker flow, reserve, and netflow. 
**DVs:** Drawdown severity, volatility spikes, same-day/next-day return reversals.
**Factor blocks:** Funding, ELR, OI, liquidations, taker CVD, reserve/netflow, CEX inflows, ETF controls.
**Freq/sample:** Daily, 2019-03 to 2026-04.
**Framework:** Stress-event studies, local projections, clustered regime maps, downside-state regressions.
**Support ML:** HDBSCAN or k-means for stress-state clustering only.
**Main exhibits:** Stress-episode anatomy charts; leverage-state maps; LP responses to leverage shocks.
**Likely criticisms:** Could look like a risk dashboard rather than a paper.
**Defense:** Anchor it to the change in post-2024 institutional regime.
**Scores:** Feasibility 9 | Novelty 6 | Publication defensibility 8
**Recommendation:** **Pursue**

### M6. **Macro Uncertainty vs Crypto Internals: Competing Explanatory Regimes**

**Thesis:** BTC and ETH alternate between macro-dominant and crypto-internal regimes, and those regimes are measurable rather than narrative.
**RQ:** When do VIX/EPU/rates/DXY dominate, and when do native metrics dominate?
**Why 2026:** Good topic, but easier to oversell than to prove.
**Why feasible:** You already have EPU, VIX, yields, DXY, oil, Fed balance sheet, plus native blocks. 
**DVs:** Returns and volatility.
**Factor blocks:** Uncertainty block vs native/on-chain vs liquidity block.
**Freq/sample:** Daily, 2020-01 to 2026-04.
**Framework:** Interaction regressions, unsupervised regime clustering, break tests, robustness by weekly aggregation.
**Support ML:** Regime clustering only.
**Main exhibits:** Regime timeline; block dominance heatmap; conditional coefficient tables.
**Likely criticisms:** Regime labels can become subjective.
**Defense:** Use unsupervised regimes and pre-defined stress windows separately.
**Scores:** Feasibility 7 | Novelty 7 | Publication defensibility 7
**Recommendation:** **Narrow**

### M7. **Public-Market Crypto Wrappers and DATs as a New Transmission Layer**

**Thesis:** Listed proxies and treasury vehicles are not just “levered beta”; they may now be part of the transmission channel from institutional sentiment into native crypto.
**RQ:** Do MSTR/COIN/miners/DAT metrics co-move with BTC/ETH in ways not captured by spot and ETF data alone?
**Why 2026:** Interesting and timely, but still noisy.
**Why feasible:** TradingView has MSTR, COIN, MARA, RIOT; Artemis/DefiLlama have DAT count/EV-NAV/treasury data.  
**DVs:** BTC/ETH returns; wrapper premium/discount proxies; BTC-adjacent equity returns.
**Factor blocks:** BTC/ETH spot, ETF flows, DAT count/EV-NAV, listed-wrapper returns, volatility.
**Freq/sample:** Daily, mostly 2024-01 to 2026-04.
**Framework:** Panel/event designs, distributed lags, relative-valuation charts.
**Support ML:** None.
**Main exhibits:** Wrapper-vs-native beta tables; premium-dislocation episodes; DAT event windows.
**Likely criticisms:** Corporate idiosyncrasy overwhelms crypto signal.
**Defense:** Keep this as a transmission-layer paper, not a corporate-finance paper.
**Scores:** Feasibility 7 | Novelty 8 | Publication defensibility 6
**Recommendation:** **Narrow**

### M8. **ETH After the ETF: Internal Ecosystem Forces vs Institutional Flows**

**Thesis:** ETH remains the better asset for testing whether crypto-native structure still matters after institutionalization.
**RQ:** Did ETF access reduce, or merely coexist with, ETH staking/LST/LRT/DeFi explanatory power?
**Why 2026:** Good niche paper, especially if the professor wants something less BTC-crowded.
**Why feasible:** ETH staking rate, ETH 2.0 flows, Ethereum native metrics, LST/LRT TVL, ETF data are already present.  
**DVs:** ETH returns, volatility, ETH/BTC relative returns, ETH basis/funding.
**Factor blocks:** ETF flows, CME ETH basis, staking rate, ETH 2.0 flows, LST/LRT TVL, Ethereum chain metrics, macro controls.
**Freq/sample:** Daily, 2021-01 to 2026-04.
**Framework:** Rolling regressions, partial (R^2), structural breaks, relative-value specifications.
**Support ML:** Sparse PCA in ETH-native block.
**Main exhibits:** ETH block competition charts; pre/post July 2024 splits.
**Likely criticisms:** Too niche; short common window.
**Defense:** Reframe with ETH/BTC relative performance.
**Scores:** Feasibility 8 | Novelty 7 | Publication defensibility 7
**Recommendation:** **Narrow**

### M9. **Cross-Chain Liquidity Rotation and ETH/BTC Relative Performance**

**Thesis:** Some ETH underperformance/overperformance may reflect capital rotation across chains rather than broad crypto sentiment.
**RQ:** Do cross-chain TVL, DEX activity, stablecoin share, and perp activity help explain ETH/BTC moves?
**Why 2026:** Timely, but easy to let it drift into an alt-L1 paper.
**Why feasible:** DefiLlama and Artemis chain-level metrics are there.  
**DVs:** ETH/BTC relative return; ETH relative volatility.
**Factor blocks:** Ethereum vs other-chain TVL/volume/stablecoin share/perp volume/revenue metrics.
**Freq/sample:** Daily, 2021-01 to 2026-04.
**Framework:** Relative-value regressions, spillover analysis, connectedness measures.
**Support ML:** Dimensionality reduction across chain panels.
**Main exhibits:** Chain-rotation heatmaps; ETH/BTC relative-performance decomposition.
**Likely criticisms:** Mission drift away from BTC/ETH core question.
**Defense:** Force every result through the ETH/BTC relative lens.
**Scores:** Feasibility 7 | Novelty 8 | Publication defensibility 6
**Recommendation:** **Narrow**

### M10. **Supply Pressure in Two Different Architectures: BTC Miners vs ETH Validators/Stakers**

**Thesis:** BTC and ETH face structurally different supply-pressure channels, and those differences may matter more in an institutional regime.
**RQ:** Are miner/validator-related variables still relevant once ETFs and macro controls enter?
**Why 2026:** Potentially elegant, but asymmetry is hard to operationalize cleanly.
**Why feasible:** BTC miner flows are rich; ETH staking proxies exist. 
**DVs:** BTC/ETH returns and volatility.
**Factor blocks:** BTC miner netflow/reserve/MPI vs ETH staking-rate/ETH2 flows/LST/LRT activity, with common macro/institutional controls.
**Freq/sample:** Daily, 2021-01 to 2026-04.
**Framework:** Separate asset regressions plus differential-response comparison.
**Support ML:** None needed.
**Main exhibits:** Supply-pressure coefficient comparison chart.
**Likely criticisms:** Miner and validator variables are not conceptually equivalent.
**Defense:** Present it explicitly as an architectural comparison, not a symmetric horse race.
**Scores:** Feasibility 7 | Novelty 6 | Publication defensibility 6
**Recommendation:** **Narrow**

### M11. **Tokenized RWAs and Crypto Beta Compression**

**Thesis:** Growth in tokenized RWAs may coincide with lower “pure crypto” beta and more finance-like behavior in majors.
**RQ:** Does RWA growth map to BTC/ETH volatility compression or correlation shifts?
**Why 2026:** Conceptually interesting, empirically weak.
**Why feasible:** Artemis and DefiLlama both track RWA market-cap series.  
**DVs:** BTC/ETH volatility and cross-asset correlations.
**Factor blocks:** RWA market cap, tokenized-asset TVL, macro controls.
**Freq/sample:** Daily, 2023-01 to 2026-04.
**Framework:** Rolling correlation, break tests, parsimonious regressions.
**Support ML:** None.
**Main exhibits:** RWA growth vs crypto-volatility panels.
**Likely criticisms:** Indirect channel, weak identification, likely spurious.
**Defense:** There is no strong defense beyond calling it exploratory.
**Scores:** Feasibility 6 | Novelty 7 | Publication defensibility 4
**Recommendation:** **Reject**

### M12. **A Unified Connectedness Map Across Macro, ETFs, Stablecoins, Derivatives, and On-Chain Blocks**

**Thesis:** The main result is the evolving network of spillovers, not individual coefficients.
**RQ:** How does cross-block connectedness change across regimes?
**Why 2026:** Stylish, but dangerously close to complexity for its own sake.
**Why feasible:** The data breadth is sufficient, but variable choice becomes the whole paper. 
**DVs:** System-wide spillover measures rather than a single asset DV.
**Factor blocks:** One representative portfolio per block.
**Freq/sample:** Daily, 2021-01 to 2026-04.
**Framework:** TVP-VAR / Diebold-Yilmaz connectedness / FEVD.
**Support ML:** Block compression only.
**Main exhibits:** Spillover network graphs and connectedness timeline.
**Likely criticisms:** Arbitrary variable selection, fragile results, too “dashboard-like.”
**Defense:** Severe parsimony. Even then, I would still worry.
**Scores:** Feasibility 6 | Novelty 7 | Publication defensibility 6
**Recommendation:** **Reject**

## 4) Ranking the MAIN ideas, strongest to weakest

1. **M1** — best balance of fit, feasibility, and publishability.
2. **M3** — strongest distinct alternative; very 2026-relevant and differentiated.
3. **M4** — best bridge from crypto-native liquidity into macro-finance.
4. **M5** — clean mechanics and strong data, but slightly more crowded.
5. **M2** — good narrow variant of M1, but partly redundant.
6. **M6** — interesting, but regime labeling can get mushy.
7. **M8** — strong ETH-specific backup.
8. **M7** — good appendix/support paper, weaker as flagship.
9. **M9** — potentially novel, but mission drift risk is high.
10. **M10** — elegant idea, but conceptual asymmetry hurts.
11. **M12** — methodological overreach risk.
12. **M11** — too indirect to recommend.

## 5) Top 5 MAIN ideas: why they made the cut

### 1. M1

It made the top 5 because it is the only idea that fully uses the brief *and* the inventory without collapsing into either ETF myopia or crypto-native nostalgia. It beats lower-ranked ideas because it can absorb them as robustness layers rather than competing with them. Main risks: variable overload, factor proliferation, reviewer concern about ex post model selection. Minimum viable version: four pre-specified blocks, two DVs, daily 2021–2026, rolling partial (R^2), break tests. Stronger version: add ETH/BTC relative-performance equations and local projections around identified flow/liquidity shocks.

### 2. M3

It made the top 5 because it is the cleanest **distinct** story from M1 and is unusually relevant given ETF options expansion and CME’s move toward 24/7 crypto derivatives. It beats lower ideas because it has a crisper market-structure contribution and a more visible 2026 hook than broad regime papers. Main risks: daily data cannot support aggressive “price discovery” claims. Minimum viable version: ETF flows, CME basis, IBIT/ETHA premiums, BTC/ETH returns. Stronger version: business-day vs weekend/friday–Monday asymmetry layer.

### 3. M4

It made the top 5 because stablecoins are now one of the strongest bridges between crypto and traditional finance. It beats lower ideas because the data block is already unusually rich and the recent literature is moving toward exactly this macro-financial interpretation. Main risks: endogeneity and causal overreach. Minimum viable version: stablecoin block incremental explanatory power for BTC/ETH returns/vol. Stronger version: interaction with leverage states and ETF regime splits.

### 4. M5

It made the top 5 because the data quality is high and the mechanism is intuitive: leverage plus exchange supply plus liquidations. It beats lower ideas because the paper can be tightly executed and visually compelling. Main risks: it may read like a monitoring paper rather than an academic paper unless anchored to regime change. Minimum viable version: event-study anatomy of large drawdowns. Stronger version: add post-ETF comparison and BTC/ETH asymmetry.

### 5. M2

It made the top 5 because it is the most viable “narrowed M1” if your professor wants a simpler thesis. It beats lower-ranked ideas because it stays close to the core research question and avoids ancillary detours. Main risks: redundancy with M1 and possible under-contribution. Minimum viable version: differential rolling betas and partial (R^2). Stronger version: full system regressions with explicit post-ETF interactions.

## 6) Final top 3 MAIN proposals

### Final Proposal A

**Title:** **From Crypto-Native to Hybrid Macro–Institutional: Time-Varying Factor Blocks in BTC and ETH, 2021–2026**

**Abstract-style summary:**
This paper studies whether BTC and ETH experienced a structural change in what explains their market behavior after spot-ETF institutionalization. Rather than asking whether one variable “causes” crypto returns, it estimates how the incremental explanatory power of four pre-specified factor blocks—macro/cross-asset, institutional/wrapper, crypto-liquidity, and native on-chain/ecosystem—evolved through time. The paper treats BTC as the primary asset and ETH as the structured comparison. The contribution is a disciplined, transparent decomposition of changing market structure rather than a predictive or alpha-oriented exercise. Relative to recent work on hidden factors and on-/off-chain drivers, this would be broader, more comparative, and better aligned with the actual post-2024 institutional regime. ([arXiv][4])

**Hypotheses:**
H1: The institutional block gained incremental explanatory power after spot BTC ETF approval, especially for BTC.
H2: ETH remained more sensitive than BTC to crypto-native and ecosystem variables after July 2024.
H3: Structural breaks occur near, but not necessarily exactly on, ETF launch dates.

**Data blocks required:**
Macro/FRED/TradingView; institutional flows/AUM/premiums/basis/fund proxies; stablecoin/CEX/DEX/lending/liquidity variables; BTC and ETH native CryptoQuant/Artemis metrics.   

**Recommended sample design:**
Main daily comparative sample 2021-01 to 2026-04; BTC-only extension 2018-01 onward; institutional submodule beginning 2024-01-11 for BTC and 2024-07-23 for ETH.

**Baseline model family:**
Block-compressed rolling OLS with rolling partial (R^2), asset-specific regressions, and BTC-vs-ETH comparison.

**Robustness family:**
Bai-Perron/Chow/CUSUM breaks, SUR, weekly/monthly aggregation, alternative block representatives, local projections around large institutional/liquidity shocks.

**Acceptable support ML:**
Sparse PCA / elastic-net screening within blocks only.

**Empirical workflow:**
Build slim baseline panel → winsorize/standardize → create block representatives → estimate static baseline → roll windows → compute incremental (R^2) → run break tests → compare BTC vs ETH → produce robustness tables.

**Contribution vs recent literature:**
Recent work is either too single-channel, too cross-sectional, or too detached from the wrapper/institutional layer. Your data let you test whether market structure itself changed, not merely whether one driver matters. ([arXiv][4])

**What makes it stand out:**
Block competition, time variation, modular sample design, and a serious BTC/ETH comparison.

**Why realistic for a small MSc team:**
Technically demanding but conceptually controlled. Coding agents can automate panel building, diagnostics, and chart generation; the intellectual task remains manageable.

---

### Final Proposal B

**Title:** **Who Leads When Markets Close? ETF Flows, CME Basis, and Daily Transmission Between Listed Wrappers and Native Crypto**

**Abstract-style summary:**
This paper examines whether the post-ETF regime changed the daily transmission of information between listed crypto wrappers and native crypto markets. Using ETF net flows, ETF-over-spot premia, CME futures basis and ratio series, and related institutional proxies, it studies whether BTC and ETH are increasingly responding through wrapper-layer variables rather than through purely native market signals. The paper is explicitly framed as a daily market-structure and timing-friction study, not an intraday price-discovery study. Its edge comes from combining ETF flows, wrapper premia, and regulated-futures structure in a period when CME is moving crypto derivatives toward 24/7 trading. ([CME Group][2])

**Hypotheses:**
H1: Extreme ETF flow days are associated with larger same-day/next-day BTC and ETH responses in the institutional regime.
H2: CME basis and wrapper premium dislocations contain information about subsequent native-crypto moves.
H3: Business-hour constraints create distinctive Friday–Monday transmission patterns.

**Data blocks required:**
Farside ETF flows, Artemis ETF AUM, IBIT/ETHA-over-spot, CME BTC/ETH basis and ratio series, Coinbase premium and fund data, BTC/ETH spot returns.   

**Recommended sample design:**
BTC: 2024-01-11 to 2026-04; ETH: 2024-07-23 to 2026-04; business-day alignment plus explicit weekend flags.

**Baseline model family:**
Distributed lags and small VARs.

**Robustness family:**
Event studies on top decile flow days, Friday–Monday split, weekly aggregation, alternative premium definitions.

**Acceptable support ML:**
None.

**Empirical workflow:**
Align calendars → construct wrapper and basis dislocation measures → estimate distributed-lag models → event windows → regime splits → weekend-friction appendix.

**Contribution vs recent literature:**
Most literature still treats institutionalization as approval events or broad “financialization.” This design studies the operational wrapper layer itself. ([CME Group][2])

**What makes it stand out:**
Very 2026-specific, visually intuitive, and genuinely tied to changing market plumbing.

**Why realistic for a small MSc team:**
Shorter sample, fewer variables, cleaner story. The constraint is interpretation, not engineering.

---

### Final Proposal C

**Title:** **Stablecoin Plumbing and the Price of Crypto Risk: Dollar-Liquidity Transmission to BTC and ETH**

**Abstract-style summary:**
This paper studies whether stablecoin variables have become a first-order explanatory block for BTC and ETH. It does not claim that stablecoins “cause” prices in a strict causal sense; instead, it asks whether dollar-like liquidity inside crypto markets adds incremental explanatory power beyond macro controls and native crypto metrics. The contribution would be to translate the new macro-financial stablecoin literature into a concrete asset-pricing and market-structure setting using a richer crypto-specific dataset than most macro papers possess. ([Bank for International Settlements][3])

**Hypotheses:**
H1: Stablecoin block explanatory power rises materially after 2022 and remains important after ETF institutionalization.
H2: Stablecoin variables matter more for ETH than BTC in normal regimes, but matter for both in stress regimes.
H3: Stablecoin measures partially subsume traditional crypto-liquidity proxies during stress.

**Data blocks required:**
DefiLlama stablecoin/CEX/chain metrics; Artemis stablecoin supply/volume/P2P/regional metrics; CryptoQuant SSR/exchange stablecoin ratio; BTC/ETH returns, funding, basis, macro controls.  

**Recommended sample design:**
Daily 2022-11 to 2026-04 main sample; monthly regional appendix.

**Baseline model family:**
Rolling OLS with block-level incremental explanatory power.

**Robustness family:**
Local projections to large supply/tx shocks, orthogonalized stablecoin block, weekly aggregation, post-ETF splits.

**Acceptable support ML:**
Sparse PCA inside the stablecoin block only.

**Empirical workflow:**
Build stablecoin block → orthogonalize against broad crypto market level → estimate baseline and regime-split models → test stress interactions → compare BTC vs ETH.

**Contribution vs recent literature:**
BIS/IMF/ECB/Fed establish that stablecoins matter for macro-financial channels; your paper would show how that plumbing maps into major-asset pricing dynamics. ([Bank for International Settlements][3])

**What makes it stand out:**
It is one of the few ideas that really bridges TradFi and crypto-native metrics without resorting to hype.

**Why realistic for a small MSc team:**
The data are already in hand; the main challenge is disciplined interpretation.

## 7) Best overall MAIN project

### Winner: **Final Proposal A — the time-varying factor-block paper**

**Why it wins:**
It best matches the brief, uses the inventory most efficiently, survives skeptical reviewer questions better than the alternatives, and gives you the most room to be both conventional and interesting. It is broad enough to matter, but narrow enough if you enforce block discipline. It also naturally nests many of the other ideas as robustness or appendix layers rather than forcing you to choose between them.

**Why Proposal B is weaker:**
It is excellent, but the sample is shorter, daily data limit the strength of “leadership” claims, and it is more vulnerable to the critique that you are studying wrappers rather than crypto itself.

**Why Proposal C is weaker:**
It is intellectually strong, but reviewers will press hard on endogeneity and reverse causality. You can still write a very good paper, but it requires more defensive framing.

**Immediate next steps if you commit to Proposal A:**
Build one slim master panel with four pre-specified blocks, not dozens of ad hoc variables. Freeze a baseline sample plan before looking at results. Start with 2 DVs only: daily return and 30-day realized volatility. Limit the baseline to 3–5 representatives per block, then add block-compression later. Produce, in week one, five charts only: BTC rolling block partial (R^2), ETH rolling block partial (R^2), BTC-vs-ETH block difference, structural break dates, and missingness/start-date map. If those charts are weak, stop early and pivot to Proposal B.

---

# Experimental / adjacent project track

## 8) Experimental ideas

### E1. **Weekend Information Absorption Between 24/7 Crypto and Weekday Wrappers**

Thesis: crypto may absorb macro/policy information before ETFs and listed proxies reopen. Exploratory question: do Friday–Monday patterns reveal asymmetric information processing? Interesting because it directly studies the 24/7 vs weekday split. Executable with current daily data, though stronger with later intraday augmentation. Methods: weekday/weekend event panels, reopen-gap decomposition, distributed lags. Risk: daily data may be too blunt. **Status:** actively explore.

### E2. **The May 29, 2026 CME 24/7 Shift as a Natural Experiment**

Thesis: regulated derivatives moving closer to crypto’s clock may change basis behavior and weekend frictions. Question: does CME 24/7 reduce wrapper/native timing asymmetry? Interesting and clean, but **not yet main-paper ready** because the event is future-facing relative to your local sample. Methods: pre/post structural comparison once enough post-event data exist. Risk: unavailable sample length right now. **Status:** backup/appendix idea. ([CME Group][2])

### E3. **Policy and Politics as Competing Explanatory Regimes**

Thesis: during some intervals, policy uncertainty dominates classical macro and crypto internals. Question: when does EPU beat rates, DXY, and native metrics? Interesting because it captures the “modern status quo” concern in your brief. Executable with EPU now; stronger with curated event coding. Methods: regime interactions and event-state analysis. Risk: event selection subjectivity. **Status:** backup/appendix idea.

### E4. **DAT mNAV Dislocations as an Institutional Sentiment Proxy**

Thesis: DAT discounts/premia may reveal institutional demand pressure not fully visible in ETF flows. Question: do mNAV dislocations help explain BTC/ETH moves or wrapper repricing? Interesting because it is a new public-market bridge. Executable with Artemis/DefiLlama DAT data and listed proxies. Methods: distributed lags, event studies, co-movement analysis. Risk: corporate idiosyncrasy. **Status:** actively explore.

### E5. **ETH Staking/LST/LRT Crowding as a Hidden ETH Factor**

Thesis: ETF access did not eliminate ETH’s internal structure; staking and restaking may still shape ETH pricing and basis. Question: when do staking-system variables dominate ETF flow variables? Interesting because ETH is where crypto-native structure still plausibly matters most. Executable now. Methods: rolling regressions and block comparisons. Risk: overfitting a niche sub-ecosystem. **Status:** actively explore.

### E6. **CEX-to-DEX Liquidity Migration as a Regime Variable**

Thesis: part of crypto market evolution is not price level but *where* liquidity lives. Question: does the relative share of CEX vs DEX activity change ETH/BTC sensitivity to other factors? Interesting and plausibly publishable as an appendix. Executable with current data. Methods: ratio-state variables, break tests, interaction regressions. Risk: measurement mismatch across venues. **Status:** backup/appendix idea.

### E7. **Cross-Chain Substitution Shocks and ETH/BTC Relative Performance**

Thesis: activity booms on other chains can pull capital away from Ethereum rather than lifting all crypto equally. Question: does chain rotation explain ETH/BTC moves better than broad crypto sentiment? Interesting and aligned with newer spillover work. Executable with current data. Methods: relative-performance regressions, spillover models. Risk: mission drift. **Status:** backup/appendix idea. ([arXiv][5])

### E8. **Stablecoin Regional Activity and Geopolitical Dollar Demand**

Thesis: stablecoin usage outside core U.S. venues may matter for crypto pricing and dollar demand. Question: do regional stablecoin transaction shifts line up with BTC/ETH sensitivity changes? Interesting, but your regional Artemis series are monthly, which weakens the core design. Methods: mixed-frequency or monthly appendices. Risk: interpretation too macro-speculative. **Status:** reject as main, maybe tiny appendix.

### E9. **DeFi Exploit Episodes and System-Wide Liquidity Withdrawal**

Thesis: large exploit events may behave like localized financial accidents that trigger broader crypto-liquidity contractions. Question: do exploits propagate through BTC/ETH via liquidity channels? Interesting, but you would need additional event/hack data beyond the current core inventory. Methods: event study + liquidity response. Risk: data assembly burden. **Status:** backup only.

### E10. **Public Crypto Equities as Levered Volatility Wrappers**

Thesis: MSTR/COIN/miners may serve as publicly listed volatility wrappers rather than simple beta proxies. Question: when do these equities overreact relative to underlying crypto moves? Interesting and visually compelling. Executable now. Methods: conditional beta, convexity-type response analysis, event windows. Risk: equity-specific confounds. **Status:** backup/appendix idea.

### E11. **RWA Growth and Major-Crypto Volatility Compression**

Thesis: as tokenized real-world assets scale, major crypto may look more like finance infrastructure and less like pure speculative beta. Interesting, but the current evidence base is too indirect. Methods: rolling correlation and volatility regressions. Risk: weak mechanism. **Status:** reject.

### E12. **Narrative-Attention Indices as a Support Layer, Not a Main Thesis**

Thesis: narrative shocks matter, but they should support rather than replace structural factor analysis. Question: can external text/news/social attention variables improve regime labeling? Interesting, but requires additional data engineering. Methods: LLM classification or search-trend proxies. Risk: huge scope creep. **Status:** backup only.

## 9) Ranking the EXPERIMENTAL ideas

1. **E1**
2. **E4**
3. **E5**
4. **E6**
5. **E10**
6. **E2**
7. **E7**
8. **E3**
9. **E9**
10. **E12**
11. **E8**
12. **E11**

## 10) Top 5 experimental ideas and whether they should modify the MAIN top 3

**E1 should be merged into Proposal B.** It is not strong enough as a standalone main paper with current daily data, but it materially improves the wrapper/native transmission paper.

**E4 should support Proposals A and B.** DAT dislocations are best treated as an institutional-sentiment proxy or appendix transmission layer, not as the whole thesis.

**E5 should be merged into Proposal A as the ETH-native sub-block.** This is exactly the kind of disciplined niche variable family that makes the main factor-block paper better.

**E6 should support Proposal A or M5.** CEX-to-DEX migration is a good regime interaction variable, especially for ETH and stress periods.

**E10 should support Proposal B.** Public crypto equities are a useful wrapper appendix; they should not replace ETF/CME variables as the paper’s center of gravity.

## Final verdict

If I were directing this project, I would commit to **Proposal A immediately**, while building **Proposal B** in parallel as the fallback if the first-pass rolling block-(R^2) charts turn out to be weak or visually unconvincing. I would keep **Proposal C** as a serious secondary branch, but only if the stablecoin block shows clear incremental explanatory power very early in the exploratory pass.

That is the strongest, most defensible use of the data you already have.

[1]: https://app.artemis.xyz/docs/welcome/overview "https://app.artemis.xyz/docs/welcome/overview"
[2]: https://www.cmegroup.com/media-room/press-releases/2026/2/19/cme_group_to_launch247cryptocurrencyfuturesandoptionstradingonma.html "https://www.cmegroup.com/media-room/press-releases/2026/2/19/cme_group_to_launch247cryptocurrencyfuturesandoptionstradingonma.html"
[3]: https://www.bis.org/publ/work1340.pdf "https://www.bis.org/publ/work1340.pdf"
[4]: https://arxiv.org/pdf/2602.08429 "https://arxiv.org/pdf/2602.08429"
[5]: https://arxiv.org/abs/2602.23762 "https://arxiv.org/abs/2602.23762"
[6]: https://papers.ssrn.com/sol3/Delivery.cfm/6301038.pdf?abstractid=6301038&mirid=1 "https://papers.ssrn.com/sol3/Delivery.cfm/6301038.pdf?abstractid=6301038&mirid=1"
[7]: https://defillama.com/digital-asset-treasuries/ethereum "https://defillama.com/digital-asset-treasuries/ethereum"
