# Results at a Glance

| Diagnostic | Value | Source |
|---|---:|---|
| BTC full-model R² | 0.921 | T03 |
| BTC R² without MVRV | 0.146 | T03 |
| BTC MVRV ΔR² (block removal) | 0.775 | T03 |
| BTC MVRV-only standalone R² | 0.912 | T07 |
| BTC native-ex-MVRV standalone R² | 0.0037 | T07 |
| BTC–MVRV correlation | 0.955 | T07 |
| ETF-flow lag 0 HAC t-stat | 10.22 | T04 |
| BTC Chow test p-value (ETF date) | 0.6236 | T08 |
| Mean VAR connectedness index | 36.9% | T09 |

The strongest empirical result is that BTC daily-return models are extremely
sensitive to MVRV-style valuation state. In the current daily linear setup,
`btc_mvrv_d1` has correlation ≈ 0.955 with `btc_ret`, and removing
MVRV from the full model drops R² from 0.921 to 0.146.
ETF-flow intensity shows strong same-day association (lag 0 t = 10.2),
but daily timing prevents causal interpretation. Non-MVRV native variables, macro,
TradFi, and liquidity blocks each contribute ΔR² < 0.01 in the full model.

We report both full and ex-MVRV models because MVRV is a valuation-state
variable highly correlated with BTC returns — not a clean exogenous factor.
