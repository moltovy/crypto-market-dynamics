# Limitations & Methodological Caveats

## 1. Contemporaneous vs. Predictive (Lagged) Models
The baseline static OLS and block-attribution models are contemporaneous exposure diagnostics. They measure co-movement, not predictive power. While useful for risk decomposition and hedging analysis, they cannot be used directly for forecasting. Lagged predictive diagnostic models (where features are lagged by one day) show significantly lower explanatory power, demonstrating that the contemporaneous relationships are driven by same-day market-clearing mechanisms.

## 2. MVRV Interpretation Risks
MVRV (Market Value to Realized Value) is a ratio constructed as:
$$\text{MVRV} = \frac{\text{Market Capitalization}}{\text{Realized Capitalization}}$$
Since the numerator is current market price times supply, the first difference of MVRV ($\Delta \text{MVRV}_t$) is highly correlated with price returns ($r_t$) by construction ($r \approx 0.955$).
- **Risk**: Treating MVRV as a standard independent factor (like interest rates or GDP growth) is invalid. It is a valuation-state proxy.
- **Mitigation**: The project explicitly separates MVRV from other native variables and presents an independent "Ex-MVRV" model family to evaluate macro and liquidity factors cleanly.

## 3. ETF-Flow Causal Interpretation
ETF-flow intensity shows a high same-day association with BTC returns. Daily data cannot identify the direction of causality. ETF flows could be driving price appreciation, or momentum/intraday price action could be driving ETF subscriptions (feedback loop). 
- **Risk**: Interpreting OLS coefficients as causal impact (e.g., "an inflow of $\$100\text{M}$ causes a $1\%$ rise") is statistically incorrect. It represents market-plumbing co-movement.
- **Mitigation**: Lead-lag regressions demonstrate that lag +1 (returns leading ETF flows) is statistically significant, supporting the feedback loop hypothesis.

## 4. Liquidity Proxies vs. Shocks
Stablecoin supply changes and DeFi TVL growth are slow-moving liquidity indicators. In a daily regression framework, they behave as lagging context rather than contemporaneous or leading price drivers.

## 5. Structural Breaks and sweeps
Chow tests and sup-F sweeps sweep for a single structural break. They do not estimate multi-break Bai-Perron models.

## 6. Data Replicability Constraint
The project relies on a frozen database (2020-01-01 to 2026-04-11). It is not a live trading dashboard and does not capture structural changes occurring after April 2026.
