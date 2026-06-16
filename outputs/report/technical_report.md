# Technical Report

## Data Pipeline and Sample Support
The data foundation is a frozen daily panel spanning 2020-01-01 to 2026-04-11 ($n = 2,293$). The database combines Artemis, CryptoQuant, DefiLlama, FRED, and TradingView series.
To address sample-composition bias (differing $n$ across models due to feature missingness), the analysis implements a Same-Support constraint. Standalone, full, and ablated models are evaluated on a common support ($n = 1,940$ for BTC, $n = 794$ for ETH) to ensure valid statistical comparisons.

## Model Formulation
Linear modeling uses Ordinary Least Squares (OLS) with Heteroskedasticity and Autocorrelation Consistent (HAC) standard errors (Newey-West with automatic lag selection) to handle serial correlation and heteroskedasticity.

### 1. Static Exposure Model
$$r_t = \alpha + \sum_j \beta_j F_{j, t} + \epsilon_t$$
where $r_t$ represents the asset return, and $F_{j, t}$ are stationary factor differences (log returns for prices, first differences for rates/spreads/levels, and scaled ratios for flows).

### 2. Full vs. Reduced Block Attribution
Block partial $R^2$ is defined as:
$$\text{Partial } R^2_{\text{Block}} = R^2_{\text{Full}} - R^2_{\text{Reduced (ex-Block)}}$$
which measures the incremental contribution of a group of variables conditional on all other features being present.

### 3. Ex-MVRV Benchmark
To evaluate macro, TradFi, and liquidity factors without the dominance of the near-price MVRV state variable, we run an Ex-MVRV factor model:
$$r_t = \alpha + \sum_{k \neq \text{MVRV}} \beta_k F_{k, t} + \epsilon_t$$

## Key Diagnostic Outputs

### 1. Feature Strength Tables (T14 - T17)
These tables report individual feature statistics including Pearson correlation, absolute correlation rank, standardized multivariate OLS coefficients ($\beta$), HAC $t$-stats, $p$-values, and drop-one $\Delta R^2$.

### 2. Same-Support Ablation (T19 - T20)
Provides sequential and block-based R² ladders, illustrating model performance from intercept-only up to the full factor stack.

### 3. Regime Sensitivity (T25)
Decomposes the explanatory power of MVRV vs. ex-MVRV models across different regimes:
- Pre-ETF ($n = 1,471$) vs. Post-ETF ($n = 822$)
- Yearly sub-samples (2020 through 2026 YTD)
- Realized Volatility Quartiles (High vs. Low Volatility)

## Results and Interpretation
- **MVRV Dominance**: In the full sample, MVRV-only yields $R^2 \approx 0.912$, and its block partial $R^2$ is $0.775$. Its explanatory dominance remains high but shifts down in 2025-2026, indicating changing market structure.
- **Ex-MVRV Performance**: Without MVRV, the combined macro, TradFi, liquidity, and sentiment blocks explain only $\approx 14.6\%$ of daily BTC return variance. TradFi and ETF flow intensity are the primary contributors in this subset.
- **Daily Plumbing vs. Prediction**: ETF flows exhibit a contemporaneous association ($t = 10.22$), but lead-lag diagnostic regressions indicate that lagged flows have minimal predictive power, consistent with daily plumbing and inventory adjustment rather than lead-lag signaling.
