# BTC Attribution Note

## Methodology

The block attribution diagnostics (`T03_block_attribution.csv` and the corresponding figure) use a nested OLS framework with Newey-West HAC standard errors. The baseline model explains BTC returns using a hierarchical sequence of feature blocks: Macro, TradFi, Liquidity, ETF-Flow, and Native Valuation (MVRV).

To isolate the explanatory power of each block, we calculate the full-vs-reduced partial R². This is done by comparing the R² of the full model against a reduced model that excludes the block in question.

## Interpretation Guardrails

- **Descriptive, Not Causal:** The partial R² values measure contemporaneous association and model sensitivity. They do not represent causal attribution.
- **Order Dependence:** The reported values are full-vs-reduced partial R² drops. They are distinct from exact Shapley R² values, which average over all possible inclusion sequences.
- **ETF Flow Intensity:** The model shows a strong contemporaneous correlation between ETF flow intensity and BTC returns. Due to the daily resolution of the data, this association is a reflection of market state and flow environment, not necessarily a predictive causal mechanism.
- **MVRV Valuation State:** Native valuation metrics like MVRV capture a large portion of the model fit. However, since MVRV is structurally linked to price levels, its high partial R² should be interpreted as a mechanical regime marker rather than an exogenous driver.
