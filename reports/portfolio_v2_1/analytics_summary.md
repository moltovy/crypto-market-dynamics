# Portfolio v2.1 Analytics Summary

## Factor Attribution

Block partial R^2 is computed as full-vs-reduced block partial R^2:
`(RSS_reduced - RSS_full) / TSS`. This is not drop-one marginal R^2,
Shapley/Owen attribution, or sequential R^2.

BTC fit is heavily influenced by BTC-native valuation and flow-state variables.
MVRV is separated from non-MVRV native variables because valuation-state inputs
can mechanically co-move with returns. ETH remains a comparison asset because
the available ETH-native block is thinner.

## ETF-Flow Market Plumbing

ETF-flow lead-lag tables use this convention: lag < 0 means x is shifted earlier and leads the target; lag -1 uses x[t-1] to explain y[t]. Same-day and
lagged rows are reduced-form market-plumbing checks. They do not establish that
ETF flows caused BTC/ETH returns, especially because daily flow and return data
are vulnerable to simultaneity and omitted news shocks.

## Rolling Correlation Regimes

The largest BTC ETF pre/post correlation deltas are:

| pair                  | lhs     | rhs        |   corr_pre |   corr_post |     delta |
|:----------------------|:--------|:-----------|-----------:|------------:|----------:|
| gld_ret vs dxy_tv_ret | gld_ret | dxy_tv_ret | -0.176743  |  -0.0572457 | 0.119497  |
| spy_ret vs dxy_tv_ret | spy_ret | dxy_tv_ret | -0.172153  |  -0.0583458 | 0.113807  |
| eth_ret vs spy_ret    | eth_ret | spy_ret    |  0.316449  |   0.416723  | 0.100274  |
| qqq_ret vs dxy_tv_ret | qqq_ret | dxy_tv_ret | -0.146486  |  -0.0535013 | 0.0929845 |
| btc_ret vs dxy_tv_ret | btc_ret | dxy_tv_ret | -0.0771997 |   0.0138037 | 0.0910035 |

The largest ETH ETF pre/post correlation deltas are:

| pair                 | lhs     | rhs       |   corr_pre |   corr_post |     delta |
|:---------------------|:--------|:----------|-----------:|------------:|----------:|
| eth_ret vs spy_ret   | eth_ret | spy_ret   |   0.308676 |    0.460479 |  0.151804 |
| eth_ret vs qqq_ret   | eth_ret | qqq_ret   |   0.318522 |    0.461608 |  0.143086 |
| btc_ret vs spy_ret   | btc_ret | spy_ret   |   0.305144 |    0.430377 |  0.125233 |
| qqq_ret vs VIXCLS_d1 | qqq_ret | VIXCLS_d1 |  -0.697234 |   -0.815661 | -0.118426 |
| spy_ret vs VIXCLS_d1 | spy_ret | VIXCLS_d1 |  -0.751655 |   -0.856253 | -0.104598 |

Rolling correlations are descriptive integration diagnostics. They can show
co-movement regimes but not the cause of those regimes.

## Stablecoin Liquidity

Stablecoin supply growth and DeFi TVL growth are used as liquidity/funding
proxies. The v2.1 outputs add realized-volatility features and compare returns
and volatility across stablecoin-growth lags and quintiles. Weak or mixed
lead-lag rows should be read as liquidity context, not as a funding-channel
claim.

## BTC-Native Lab

Native ablation snapshot:

| model_id          |          r2 |   delta_r2_vs_prev |    n |
|:------------------|------------:|-------------------:|-----:|
| N0_intercept      | 1.11022e-16 |       nan          | 2292 |
| N1_native_ex_mvrv | 0.00370189  |         0.00370189 | 1942 |
| N2_mvrv_only      | 0.912229    |         0.908527   | 2292 |
| N3_all_native     | 0.915594    |         0.00336563 | 1942 |

MVRV is useful because it summarizes valuation state, but it can dominate fit
for mechanical reasons. The native lab is a research lens, not a trade-signal
claim.
