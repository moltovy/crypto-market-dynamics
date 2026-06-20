# MVRV Mechanics Model Card

Purpose: audit whether same-day MVRV changes mechanically overlap BTC returns and summarize lagged MVRV state outcomes.

Outcome and features: BTC log return, `d_log_mvrv`, `d_log_market_cap`, `d_log_realized_cap`, and `identity_residual` over the same daily interval.

Principal finding: corr(BTC return, d-log MVRV)=0.9966; R2=0.9932; median abs residual / median abs BTC return=1.14e-07.

Estimator and uncertainty: HAC same-day diagnostic plus identity residual quantiles. This is a measurement audit, not a predictive model.

Prohibited claims: MVRV is the strongest independent factor; same-day MVRV predicts BTC returns.
