# Research Framework and Candidate Pathways

## Core Framework
Organize the project around factor blocks rather than isolated narratives.

### Factor Blocks
1. Macro / cross-asset block
2. Institutional block
3. Crypto-liquidity block
4. BTC-native block
5. ETH-native block

## General Model Form
For asset a in {BTC, ETH}:

Y_t^(a) = alpha + beta_M M_t + beta_I I_t^(a) + beta_L L_t + beta_N N_t^(a) + epsilon_t

Where:
- M_t = macro / cross-asset factors
- I_t^(a) = institutional factors for that asset
- L_t = crypto-liquidity factors
- N_t^(a) = native on-chain / ecosystem factors for that asset

Y_t^(a) can be:
- daily log return
- weekly log return
- realized volatility
- absolute return
- downside volatility / drawdown measure

## Cleanest Main Direction
Time-varying factor-evolution study for BTC and ETH.

Main question:
Which factor blocks matter most in each period, and how did that change after institutionalization / ETF-era adoption?

## Strong Candidate Pathways

### Pathway A: Factor-Evolution / Structural Change (Preferred)
Main tools:
- static OLS with HAC errors
- rolling OLS
- rolling partial R^2
- structural break tests

Why strong:
- interpretable
- publishable
- directly aligned with finance / econometrics expectations
- handles broad factor libraries cleanly

### Pathway B: BTC vs ETH Comparative Driver Structure
Main tools:
- same factor-block setup for BTC and ETH separately
- compare coefficient paths, break dates, and explanatory shares

Why strong:
- clearer than trying to include too many altcoins
- lets BTC and ETH play different economic roles

### Pathway C: Dynamic Interaction / Shock Transmission
Main tools:
- VAR
- Granger causality
- FEVD
- impulse responses
- connectedness / spillovers

Why strong:
- good secondary pillar
- useful for studying ETF / stablecoin / macro shock propagation

### Pathway D: Regime Mapping / Big-Data Analytics Layer
Main tools:
- PCA / sparse PCA
- clustering of periods
- regime classification
- nonlinear variable importance diagnostics

Why strong:
- allows high-dimensional exploration without making prediction claims
- good supporting section and model-selection aid

## Things to Avoid as Main Paper Angles
- pure predictive ML
- trading strategy framing
- huge altcoin panels without clean economic structure
- forcing every available metric into one regression
- pure ETF flow paper with no broader factor architecture

## Recommended Scope Logic
- Main asset: BTC
- Comparison / robustness asset: ETH
- Daily data main panel
- Weekly / monthly robustness
- Long-history reduced BTC model as context
- Shorter specialized subpanels for variables with later start dates
