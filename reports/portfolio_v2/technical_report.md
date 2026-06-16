# Technical Report - Portfolio v2

## Scope

Crypto Market Factor Lab estimates reduced-form BTC/ETH factor diagnostics on a
frozen daily panel. The analysis is useful for regime description, factor
exposure comparison, ETF-flow market-plumbing discussion, and reproducible
research engineering. It is not a causal identification design.

## Static Factor Exposure

| Asset | Full R^2 | Pre-ETF R^2 | Post-ETF R^2 |
|---|---:|---:|---:|
| BTC | 0.921 | 0.904 | 0.971 |
| ETH | 0.179 | 0.173 | 0.214 |

## Block R^2 Snapshot

| period   | asset   |   R2_Macro |   N_Macro |   R2_Institutional |   N_Institutional |   R2_Liquidity |   N_Liquidity |   R2_Sentiment |   N_Sentiment |   R2_Native_btc |   N_Native_btc |   R2_Native_eth |   N_Native_eth |
|:---------|:--------|-----------:|----------:|-------------------:|------------------:|---------------:|--------------:|---------------:|--------------:|----------------:|---------------:|----------------:|---------------:|
| full     | btc     |     0.1144 |      2287 |             0.1218 |              2291 |         0.0008 |          2292 |         0.0015 |          2292 |          0.9156 |           1942 |        nan      |            nan |
| pre_etf  | btc     |     0.1131 |      1465 |             0.1175 |              1469 |         0.002  |          1470 |         0.0037 |          1470 |          0.8972 |           1212 |        nan      |            nan |
| post_etf | btc     |     0.1262 |       822 |             0.1412 |               822 |         0.0005 |           822 |         0      |           822 |          0.9687 |            730 |        nan      |            nan |
| full     | eth     |     0.1262 |      2287 |             0.129  |              2291 |         0.0036 |          2292 |         0.0001 |          2292 |        nan      |            nan |          0.002  |           1559 |
| pre_etf  | eth     |     0.1168 |      1465 |             0.1169 |              1469 |         0.0048 |          1470 |         0.0017 |          1470 |        nan      |            nan |          0.0037 |            841 |
| post_etf | eth     |     0.1547 |       822 |             0.1768 |               822 |         0.002  |           822 |         0.0017 |           822 |        nan      |            nan |          0.0005 |            718 |

Interpretation: BTC fit is dominated by BTC-native valuation/flow variables in
this specification. ETH is less well explained by the current ETH-native block,
so the portfolio should present ETH as a comparison asset rather than forcing
symmetry.

## ETF-Flow Intensity

ETF-flow intensity is computed as daily ETF flow divided by prior-day USD market
cap. The BTC post-launch regression reports beta=46.13,
HAC t=8.67, p=<0.001, R^2=0.237,
and N=821. This is same-day association and should be described as
market-plumbing evidence, not a causal effect.

## Structural-Break Diagnostics

| asset   | chow_breakpoint   |   chow_f |    chow_p |   sup_f | sup_f_argmax_date   |   sup_f_placebo_p |   null_mean |   null_95th |    n |   k |
|:--------|:------------------|---------:|----------:|--------:|:--------------------|------------------:|------------:|------------:|-----:|----:|
| btc     | 2024-01-11        |  0.79225 | 0.623582  | 3.84497 | 2021-01-04          |        0.01       |     1.81781 |     2.673   | 2287 |   9 |
| eth     | 2024-07-23        |  2.12027 | 0.0249229 | 4.1144  | 2021-05-12          |        0.00333333 |     1.85449 |     2.85758 | 2287 |   9 |

The implemented structural-break diagnostics are Chow tests and a single-break
sup-F sweep. They should not be labeled full Bai-Perron multi-break tests.

## VAR/FEVD Connectedness

Compact VAR metadata:

```json
{
  "label": "compact_4var",
  "lag_order": 1,
  "n": 2291,
  "horizon": 10,
  "dy_total_connectedness_pct": 35.27,
  "columns": [
    "btc_ret",
    "eth_ret",
    "spy_ret",
    "VIXCLS_d1"
  ],
  "cholesky_note": "FEVD uses statsmodels VAR with Cholesky ordering = column order listed in 'columns'."
}
```

Compact 10-day FEVD table:

| to        |   btc_ret |    eth_ret |     spy_ret |   VIXCLS_d1 |
|:----------|----------:|-----------:|------------:|------------:|
| btc_ret   |  0.995895 | 0.00267443 | 0.00100342  | 0.000427576 |
| eth_ret   |  0.670279 | 0.329181   | 0.000213418 | 0.000326149 |
| spy_ret   |  0.110839 | 0.0164735  | 0.872641    | 4.60893e-05 |
| VIXCLS_d1 |  0.105907 | 0.0175715  | 0.485218    | 0.391304    |

The FEVD table is best framed as connectedness diagnostics under the specified
VAR ordering, not a structural spillover model.

## ETF Event Studies

| window   |        car |    t_stat |   n_days |       alpha |    beta |   sigma_e |   placebo_p_m5_p5 | placebo_benchmark_window   | asset   | event                            | event_date   |
|:---------|-----------:|----------:|---------:|------------:|--------:|----------:|------------------:|:---------------------------|:--------|:---------------------------------|:-------------|
| [-1,+1]  | -0.0821718 | -2.30503  |        3 | 0.00159715  | 0.38309 | 0.0205819 |          0.613065 | [-5,+5]                    | btc     | BTC spot ETF launch (2024-01-11) | 2024-01-11   |
| [-5,+5]  | -0.0469101 | -0.687204 |       11 | 0.00159715  | 0.38309 | 0.0205819 |          0.613065 | [-5,+5]                    | btc     | BTC spot ETF launch (2024-01-11) | 2024-01-11   |
| [+0,+5]  | -0.0867417 | -1.72055  |        6 | 0.00159715  | 0.38309 | 0.0205819 |          0.613065 | [-5,+5]                    | btc     | BTC spot ETF launch (2024-01-11) | 2024-01-11   |
| [+0,+30] | -0.0452555 | -0.394916 |       31 | 0.00159715  | 0.38309 | 0.0205819 |          0.613065 | [-5,+5]                    | btc     | BTC spot ETF launch (2024-01-11) | 2024-01-11   |
| [-1,+1]  | -0.0428157 | -0.827407 |        3 | 1.42422e-05 | 1.09093 | 0.0298761 |          0.924623 | [-5,+5]                    | eth     | ETH spot ETF launch (2024-07-23) | 2024-07-23   |
| [-5,+5]  | -0.010646  | -0.10744  |       11 | 1.42422e-05 | 1.09093 | 0.0298761 |          0.924623 | [-5,+5]                    | eth     | ETH spot ETF launch (2024-07-23) | 2024-07-23   |
| [+0,+5]  | -0.0304923 | -0.416669 |        6 | 1.42422e-05 | 1.09093 | 0.0298761 |          0.924623 | [-5,+5]                    | eth     | ETH spot ETF launch (2024-07-23) | 2024-07-23   |
| [+0,+30] | -0.293198  | -1.76261  |       31 | 1.42422e-05 | 1.09093 | 0.0298761 |          0.924623 | [-5,+5]                    | eth     | ETH spot ETF launch (2024-07-23) | 2024-07-23   |

## Reproducibility

Run order:

```powershell
uv sync --all-extras
uv run pytest
uv run python scripts/run_portfolio_pipeline.py
```
