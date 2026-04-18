# Quantitative Methods and Analysis Menu

## Central Question
How did the relative importance of macro / cross-asset, institutional, crypto-liquidity, and native on-chain / ecosystem factors change for BTC and ETH over time?

## Main Dependent Variables
- daily log returns
- weekly log returns
- realized volatility
- absolute returns
- downside volatility / drawdowns

## Core Quantitative / Statistical Methods

### 1. Descriptive and Regime Mapping
Purpose:
- identify broad changes before formal modeling

Methods:
- rolling correlations
- rolling betas
- z-score panels
- correlation heatmaps
- regime-by-period descriptive tables

### 2. Static Multi-Factor Regression
Purpose:
- estimate average factor exposures

Methods:
- OLS
- HAC / Newey-West robust errors
- subperiod regressions

Core equation:
Y_t^(a) = alpha + beta_M M_t + beta_I I_t^(a) + beta_L L_t + beta_N N_t^(a) + epsilon_t

Outputs:
- coefficients
- t-stats
- adjusted R^2
- subperiod differences

### 3. Rolling OLS / Time-Varying Coefficients
Purpose:
- quantify evolving factor exposures

Methods:
- rolling 60-day regressions
- rolling 90-day regressions
- rolling 120-day regressions

Outputs:
- rolling coefficients
- rolling t-stats
- rolling adjusted R^2

### 4. Block-Level Partial R^2 Decomposition
Purpose:
- measure explanatory share of each factor family

Method:
- compare full model vs model excluding one factor block
- compute incremental / partial R^2 by rolling window

This is likely the main figure of the paper.

### 5. Structural Break Analysis
Purpose:
- test whether relationships changed statistically

Methods:
- Chow test
- Bai-Perron multiple structural breaks
- CUSUM / recursive stability tests

### 6. Dynamic System Models
Purpose:
- study interaction and shock transmission

Methods:
- VAR
- Granger causality
- FEVD
- impulse responses
- VECM only if cointegration is credible

### 7. Event Studies
Purpose:
- isolate changes around important dates

Use around:
- BTC ETF launch / approval
- ETH ETF launch
- halving
- major macro / crypto stress windows

Outcomes:
- abnormal returns
- abnormal volatility
- pre/post coefficient changes
- pre/post correlation changes

### 8. Volatility Analysis
Purpose:
- study whether regime change affected volatility generation, not just returns

Methods:
- regressions on realized volatility
- regressions on |returns|
- downside volatility analysis
- optional GARCH-type robustness

### 9. PCA / Sparse PCA
Purpose:
- reduce dimensionality and multicollinearity inside factor blocks

Use within:
- macro block
- crypto-liquidity block
- BTC-native block
- ETH-native block

### 10. Connectedness / Spillover Analysis
Purpose:
- quantify transmission across crypto and traditional assets

Methods:
- Diebold-Yilmaz connectedness
- spillover tables / networks

### 11. Regime Classification / Clustering
Purpose:
- identify periods with different market-driver structures

Methods:
- clustering on rolling betas / correlations
- unsupervised regime classification
- optional Markov switching if justified

## ML / Big-Data Analytics Role (Support Only)
Use ML for:
- variable screening
- nonlinear relationship discovery
- clustering
- dimensionality reduction
- variable-importance diagnostics

Acceptable tools:
- lasso / elastic net
- random forest / boosting for contemporaneous variable importance
- SHAP only as interpretability support
- clustering methods
- PCA / sparse PCA

Not acceptable as main contribution:
- predictive return paper
- trading alpha claims
- black-box forecasting as headline result

## Clean Empirical Workflow
1. build factor library
2. group variables into factor blocks
3. run descriptive + rolling-correlation analysis
4. run structural break tests
5. run static regressions
6. run rolling regressions + rolling partial R^2
7. run small VAR / FEVD / Granger systems
8. run daily / weekly / monthly robustness
9. run ML-style support analyses only after baseline econometrics
