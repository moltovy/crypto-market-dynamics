# Executive Summary

The Crypto Market Factor Lab evaluates the factors explaining BTC and ETH returns using a frozen daily panel from 2020-01-01 through 2026-04-11 (2,293 observations, 63 features). The primary objective is to separate structural price co-movements (valuation state) from exogenous risk factors (macro, liquidity, TradFi) and market-plumbing elements (ETF flows).

## Core Findings

1. **MVRV Dominance & Valuation-State Sensitivity**
   - The full BTC model achieves an $R^2 \approx 0.921$, but removing the BTC MVRV block collapses the reduced model's fit to $R^2 \approx 0.146$.
   - The block partial $R^2$ ($\Delta R^2$) for MVRV is $0.775$. Standalone, an MVRV-only model yields $R^2 \approx 0.912$. This indicates that the high model fit is not a broad factor structure but is almost entirely driven by the first-differenced MVRV valuation-state variable, which has a $0.955$ daily correlation with BTC returns.

2. **Native ex-MVRV Features**
   - Daily crypto-native flow and structure variables—such as CME futures basis (`cme_btc_basis_close_d1`), exchange netflow (`btc_exchange_netflow_d1`), and miner-to-exchange flows (`btc_miner_to_exchange_flow_d1`)—exhibit near-zero contemporaneous correlation with BTC returns.
   - Standardized OLS coefficients and standalone regressions yield $R^2 \approx 0.0037$ for these variables. This confirms that daily native flows (excluding MVRV) do not explain daily returns in a linear same-day specification.

3. **ETF Flow Plumbing & Timing**
   - ETF-flow intensity is strongly associated with same-day returns ($t\text{-stat} \approx 10.22$, standalone $R^2 \approx 0.271$). However, negative lags (excluding lag -1) are weak, and lag +1 is also strong, highlighting that this association represents contemporaneous market-plumbing co-movement rather than predictive ex-ante causality.

4. **Regime and Temporal Stability**
   - MVRV dominance persists across regimes but exhibits temporal shifts. In the post-ETF era (2024–2026), MVRV's standalone explanatory power is still dominant but declines slightly as TradFi integration and ETF flow associations grow.
   - Realized volatility regimes (high vs. low vol quartiles) show that macro and TradFi risk exposures are regime-dependent, with stronger TradFi betas observed during low-volatility regimes.

5. **Analytical Infrastructure & Same-Support Comparisons**
   - In previous iterations, model comparisons were biased by varying sample sizes (differing $n$). The new implementation introduces same-support ablation tables ($T19$ and $T20$), ensuring all model combinations are estimated on identical observation samples to guarantee apples-to-apples comparisons.
