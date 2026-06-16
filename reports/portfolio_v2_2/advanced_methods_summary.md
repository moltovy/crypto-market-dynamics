# Portfolio v2.2 Advanced Methods Summary

## PCA Blocks

PCA is fitted independently within multi-variable factor blocks after
standardization. Single-variable blocks are skipped because PCA would only
rename the original series. PCA factors are diagnostics for compression and
visualization, not economic latent variables by themselves.

## Exact Block Shapley R2

The static Shapley implementation enumerates every block coalition and allocates
full-model R2 across blocks. Rolling Shapley uses 180-day windows, `step=30`,
and `min_periods=150` to keep runtime bounded.

BTC static full-model R2: `0.921`.

## CUSUM

CUSUM uses standardized full-sample OLS residuals and a visual 5% reference
boundary. It is labeled exploratory because the current implementation is not a
full multi-break estimator.

## FEVD Sensitivity

FEVD is recomputed under compact variable orderings: `crypto_first`,
`tradfi_first`, `risk_first`, and `eth_first`. The sensitivity table reports the
range of 10-day FEVD shares across successful orderings.

Top sensitivity rows:

| from      | to        |         min |      max |    range |
|:----------|:----------|------------:|---------:|---------:|
| eth_ret   | eth_ret   | 0.322027    | 0.999437 | 0.67741  |
| eth_ret   | btc_ret   | 2.38355e-05 | 0.670279 | 0.670256 |
| btc_ret   | eth_ret   | 0.00232214  | 0.671711 | 0.669389 |
| btc_ret   | btc_ret   | 0.326858    | 0.995895 | 0.669036 |
| VIXCLS_d1 | VIXCLS_d1 | 0.391304    | 0.994306 | 0.603003 |
| VIXCLS_d1 | spy_ret   | 0.00455986  | 0.600601 | 0.596041 |
| spy_ret   | VIXCLS_d1 | 4.60893e-05 | 0.594891 | 0.594845 |
| spy_ret   | spy_ret   | 0.401778    | 0.996463 | 0.594685 |

## Robustness Grid

The BTC-focused grid varies trailing window, HAC lag length, winsorization,
MVRV inclusion, and calendar support.

Successful grid rows: `108` of `108`.
