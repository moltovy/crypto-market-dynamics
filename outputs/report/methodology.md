# Methodology

## 1. Feature Construction & Stationarity
To avoid spurious regressions, all non-stationary series are transformed:
- **Price series** (BTC, ETH, SPY, QQQ, GLD): Log differences ($r_t = \ln(P_t) - \ln(P_{t-1})$).
- **Yields, Spreads, Sentiment, and On-chain Levels** (DGS10, DGS2, VIX, MVRV, Exchange Netflow, Miner-to-Exchange flow): First differences ($\Delta X_t = X_t - X_{t-1}$).
- **ETF-Flow Intensity**: Scaled as daily net USD flow divided by prior-day total asset market capitalization. This normalizes flow magnitudes relative to the growing scale of the market.

## 2. Regime Definitions (`src/cqresearch/analysis/regimes.py`)
To analyze structural shifts through time and conditions, we define the following boolean masks over the dataset:
- **Temporal Regimes**:
  - `full`: 2020-01-01 to 2026-04-11
  - `pre_btc_etf`: dates before 2024-01-11
  - `post_btc_etf`: dates on or after 2024-01-11
  - `post_eth_etf`: dates on or after 2024-07-23
  - `year_2020` through `year_2026_ytd`
- **Volatility Regimes**:
  - `high_vol`: Days in the top quartile of rolling 30-day annualized realized volatility.
  - `low_vol`: Days in the bottom quartile of rolling 30-day annualized realized volatility.

## 3. Statistical Diagnostic Framework
- **HAC OLS Regressions**: OLS models are estimated using Newey-West standard errors. This corrects for autocorrelation and heteroskedasticity in daily financial time series.
- **Univariate vs. Multivariate Feature Strength**:
  - *Univariate*: Static correlation and standalone single-variable regressions.
  - *Multivariate*: Standardized betas (coefficients estimated after standardizing variables to unit variance, allowing direct magnitude comparison) and drop-one $\Delta R^2$.
- **Same-Support Ablation Constraint**:
  - When comparing models (e.g., full model vs. ex-MVRV model vs. native-only model), any rows containing missing data in any feature of the *full model* are dropped across *all* compared models. This forces estimation on an identical sample $S$, ensuring differences in $R^2$ reflect feature information, not sample composition.

## 4. Connectedness and Spillovers
Cross-asset connectedness uses a Vector Autoregressive (VAR) model framework. The system estimates daily Forecast Error Variance Decompositions (FEVD) to compute the Directional Connectedness Index (DCI) and Net Spillover effects among core market segments.
