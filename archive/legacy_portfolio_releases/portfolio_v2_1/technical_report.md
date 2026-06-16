# Portfolio v2.1 Technical Report

## Scope

Portfolio v2.1 extends the stable v2 packet with additional reduced-form
analytics. The goal is public-readiness for quant finance, crypto research, and
data-engineering review. It is not a causal identification design.

## Data

The frozen panel spans 2020-01-01 through 2026-04-11 with
2,293 rows and 63 columns. The selected
baseline source table bundle is `reports\tables\2026-06-16`;
the selected source figure bundle is `reports\figures\2026-06-16`.

## Feature Engineering

Price-like series are transformed into log returns. Rates, spreads, sentiment,
and native levels use first differences. ETF-flow intensity is daily USD ETF
flow divided by prior-day USD market capitalization. Realized volatility uses a
30-day rolling annualized standard deviation of log returns.

## Factor Attribution

BTC block partial R^2:

| asset   | sample       | block              |   partial_r2 |   full_r2 |   reduced_r2 |    n |   n_vars | variables                                                                    | method                                       |
|:--------|:-------------|:-------------------|-------------:|----------:|-------------:|-----:|---------:|:-----------------------------------------------------------------------------|:---------------------------------------------|
| btc     | full         | Macro              |       0.0001 |    0.9207 |       0.9206 | 1940 |        5 | DGS10_d1;DGS2_d1;VIXCLS_d1;DTWEXBGS_d1;DFF_d1                                | full_vs_reduced_block_partial_r2_not_shapley |
| btc     | full         | TradFi             |       0.0023 |    0.9207 |       0.9185 | 1940 |        3 | spy_ret;qqq_ret;gld_ret                                                      | full_vs_reduced_block_partial_r2_not_shapley |
| btc     | full         | Liquidity          |       0.0009 |    0.9207 |       0.9198 | 1940 |        2 | defi_tvl_usd_ret;stables_total_usd_ret                                       | full_vs_reduced_block_partial_r2_not_shapley |
| btc     | full         | Sentiment          |       0      |    0.9207 |       0.9207 | 1940 |        1 | fng_value_d1                                                                 | full_vs_reduced_block_partial_r2_not_shapley |
| btc     | full         | BTC Native ex MVRV |       0.0002 |    0.9207 |       0.9206 | 1940 |        3 | cme_btc_basis_close_d1;btc_exchange_netflow_d1;btc_miner_to_exchange_flow_d1 | full_vs_reduced_block_partial_r2_not_shapley |
| btc     | full         | BTC MVRV           |       0.7748 |    0.9207 |       0.146  | 1940 |        1 | btc_mvrv_d1                                                                  | full_vs_reduced_block_partial_r2_not_shapley |
| btc     | pre_btc_etf  | Macro              |       0.0002 |    0.9044 |       0.9042 | 1210 |        5 | DGS10_d1;DGS2_d1;VIXCLS_d1;DTWEXBGS_d1;DFF_d1                                | full_vs_reduced_block_partial_r2_not_shapley |
| btc     | pre_btc_etf  | TradFi             |       0.0036 |    0.9044 |       0.9008 | 1210 |        3 | spy_ret;qqq_ret;gld_ret                                                      | full_vs_reduced_block_partial_r2_not_shapley |
| btc     | pre_btc_etf  | Liquidity          |       0.0011 |    0.9044 |       0.9033 | 1210 |        2 | defi_tvl_usd_ret;stables_total_usd_ret                                       | full_vs_reduced_block_partial_r2_not_shapley |
| btc     | pre_btc_etf  | Sentiment          |       0.0001 |    0.9044 |       0.9043 | 1210 |        1 | fng_value_d1                                                                 | full_vs_reduced_block_partial_r2_not_shapley |
| btc     | pre_btc_etf  | BTC Native ex MVRV |       0.0004 |    0.9044 |       0.9039 | 1210 |        3 | cme_btc_basis_close_d1;btc_exchange_netflow_d1;btc_miner_to_exchange_flow_d1 | full_vs_reduced_block_partial_r2_not_shapley |
| btc     | pre_btc_etf  | BTC MVRV           |       0.7589 |    0.9044 |       0.1455 | 1210 |        1 | btc_mvrv_d1                                                                  | full_vs_reduced_block_partial_r2_not_shapley |
| btc     | post_btc_etf | Macro              |       0.0008 |    0.9728 |       0.972  |  729 |        5 | DGS10_d1;DGS2_d1;VIXCLS_d1;DTWEXBGS_d1;DFF_d1                                | full_vs_reduced_block_partial_r2_not_shapley |
| btc     | post_btc_etf | TradFi             |       0.0004 |    0.9728 |       0.9724 |  729 |        3 | spy_ret;qqq_ret;gld_ret                                                      | full_vs_reduced_block_partial_r2_not_shapley |
| btc     | post_btc_etf | Liquidity          |       0.0005 |    0.9728 |       0.9723 |  729 |        2 | defi_tvl_usd_ret;stables_total_usd_ret                                       | full_vs_reduced_block_partial_r2_not_shapley |
| btc     | post_btc_etf | Sentiment          |       0      |    0.9728 |       0.9728 |  729 |        1 | fng_value_d1                                                                 | full_vs_reduced_block_partial_r2_not_shapley |
| btc     | post_btc_etf | BTC Native ex MVRV |       0.0003 |    0.9728 |       0.9725 |  729 |        3 | cme_btc_basis_close_d1;btc_exchange_netflow_d1;btc_miner_to_exchange_flow_d1 | full_vs_reduced_block_partial_r2_not_shapley |
| btc     | post_btc_etf | BTC MVRV           |       0.6866 |    0.9728 |       0.2862 |  729 |        1 | btc_mvrv_d1                                                                  | full_vs_reduced_block_partial_r2_not_shapley |
| btc     | post_btc_etf | BTC ETF Flow       |       0.002  |    0.9728 |       0.9708 |  729 |        1 | btc_etf_intensity                                                            | full_vs_reduced_block_partial_r2_not_shapley |

ETH block partial R^2:

| asset   | sample       | block        |   partial_r2 |   full_r2 |   reduced_r2 |    n |   n_vars | variables                                     | method                                       |
|:--------|:-------------|:-------------|-------------:|----------:|-------------:|-----:|---------:|:----------------------------------------------|:---------------------------------------------|
| eth     | full         | Macro        |       0.0136 |    0.1785 |       0.1649 | 1559 |        5 | DGS10_d1;DGS2_d1;VIXCLS_d1;DTWEXBGS_d1;DFF_d1 | full_vs_reduced_block_partial_r2_not_shapley |
| eth     | full         | TradFi       |       0.0317 |    0.1785 |       0.1469 | 1559 |        3 | spy_ret;qqq_ret;gld_ret                       | full_vs_reduced_block_partial_r2_not_shapley |
| eth     | full         | Liquidity    |       0.0072 |    0.1785 |       0.1713 | 1559 |        2 | defi_tvl_usd_ret;stables_total_usd_ret        | full_vs_reduced_block_partial_r2_not_shapley |
| eth     | full         | Sentiment    |       0.0042 |    0.1785 |       0.1743 | 1559 |        1 | fng_value_d1                                  | full_vs_reduced_block_partial_r2_not_shapley |
| eth     | full         | ETH Native   |       0.0008 |    0.1785 |       0.1777 | 1559 |        1 | cme_eth_basis_close_d1                        | full_vs_reduced_block_partial_r2_not_shapley |
| eth     | pre_btc_etf  | Macro        |       0.0176 |    0.191  |       0.1734 |  841 |        5 | DGS10_d1;DGS2_d1;VIXCLS_d1;DTWEXBGS_d1;DFF_d1 | full_vs_reduced_block_partial_r2_not_shapley |
| eth     | pre_btc_etf  | TradFi       |       0.0352 |    0.191  |       0.1558 |  841 |        3 | spy_ret;qqq_ret;gld_ret                       | full_vs_reduced_block_partial_r2_not_shapley |
| eth     | pre_btc_etf  | Liquidity    |       0.019  |    0.191  |       0.172  |  841 |        2 | defi_tvl_usd_ret;stables_total_usd_ret        | full_vs_reduced_block_partial_r2_not_shapley |
| eth     | pre_btc_etf  | Sentiment    |       0.0087 |    0.191  |       0.1824 |  841 |        1 | fng_value_d1                                  | full_vs_reduced_block_partial_r2_not_shapley |
| eth     | pre_btc_etf  | ETH Native   |       0.0011 |    0.191  |       0.1899 |  841 |        1 | cme_eth_basis_close_d1                        | full_vs_reduced_block_partial_r2_not_shapley |
| eth     | post_btc_etf | Macro        |       0.0051 |    0.2456 |       0.2405 |  548 |        5 | DGS10_d1;DGS2_d1;VIXCLS_d1;DTWEXBGS_d1;DFF_d1 | full_vs_reduced_block_partial_r2_not_shapley |
| eth     | post_btc_etf | TradFi       |       0.034  |    0.2456 |       0.2116 |  548 |        3 | spy_ret;qqq_ret;gld_ret                       | full_vs_reduced_block_partial_r2_not_shapley |
| eth     | post_btc_etf | Liquidity    |       0.0014 |    0.2456 |       0.2441 |  548 |        2 | defi_tvl_usd_ret;stables_total_usd_ret        | full_vs_reduced_block_partial_r2_not_shapley |
| eth     | post_btc_etf | Sentiment    |       0.0009 |    0.2456 |       0.2446 |  548 |        1 | fng_value_d1                                  | full_vs_reduced_block_partial_r2_not_shapley |
| eth     | post_btc_etf | ETH Native   |       0.0001 |    0.2456 |       0.2454 |  548 |        1 | cme_eth_basis_close_d1                        | full_vs_reduced_block_partial_r2_not_shapley |
| eth     | post_btc_etf | ETH ETF Flow |       0.0313 |    0.2456 |       0.2142 |  548 |        1 | eth_etf_intensity                             | full_vs_reduced_block_partial_r2_not_shapley |
| eth     | post_eth_etf | Macro        |       0.0051 |    0.2456 |       0.2405 |  548 |        5 | DGS10_d1;DGS2_d1;VIXCLS_d1;DTWEXBGS_d1;DFF_d1 | full_vs_reduced_block_partial_r2_not_shapley |
| eth     | post_eth_etf | TradFi       |       0.034  |    0.2456 |       0.2116 |  548 |        3 | spy_ret;qqq_ret;gld_ret                       | full_vs_reduced_block_partial_r2_not_shapley |
| eth     | post_eth_etf | Liquidity    |       0.0014 |    0.2456 |       0.2441 |  548 |        2 | defi_tvl_usd_ret;stables_total_usd_ret        | full_vs_reduced_block_partial_r2_not_shapley |
| eth     | post_eth_etf | Sentiment    |       0.0009 |    0.2456 |       0.2446 |  548 |        1 | fng_value_d1                                  | full_vs_reduced_block_partial_r2_not_shapley |
| eth     | post_eth_etf | ETH Native   |       0.0001 |    0.2456 |       0.2454 |  548 |        1 | cme_eth_basis_close_d1                        | full_vs_reduced_block_partial_r2_not_shapley |
| eth     | post_eth_etf | ETH ETF Flow |       0.0313 |    0.2456 |       0.2142 |  548 |        1 | eth_etf_intensity                             | full_vs_reduced_block_partial_r2_not_shapley |

The block statistic is full-vs-reduced partial R^2. It is not Shapley/Owen and
not the older rolling drop-one marginal R^2.

## ETF-Flow Intensity

Lag convention: lag < 0 means x is shifted earlier and leads the target; lag -1 uses x[t-1] to explain y[t].

BTC ETF lead-lag return rows:

| asset   | target   | x                 |   lag |   coefficient |   hac_se |       t |      p |   n |     r2 | controls                                | lag_convention                                                                              | note   |
|:--------|:---------|:------------------|------:|--------------:|---------:|--------:|-------:|----:|-------:|:----------------------------------------|:--------------------------------------------------------------------------------------------|:-------|
| btc     | btc_ret  | btc_etf_intensity |    -5 |        4.7948 |   4.8333 |  0.992  | 0.3212 | 817 | 0.1525 | spy_ret;VIXCLS_d1;DGS10_d1;btc_ret_lag1 | lag < 0 means x is shifted earlier and leads the target; lag -1 uses x[t-1] to explain y[t] | ok     |
| btc     | btc_ret  | btc_etf_intensity |    -4 |        4.3445 |   5.883  |  0.7385 | 0.4602 | 818 | 0.1523 | spy_ret;VIXCLS_d1;DGS10_d1;btc_ret_lag1 | lag < 0 means x is shifted earlier and leads the target; lag -1 uses x[t-1] to explain y[t] | ok     |
| btc     | btc_ret  | btc_etf_intensity |    -3 |       -1.5393 |   4.5111 | -0.3412 | 0.7329 | 819 | 0.1513 | spy_ret;VIXCLS_d1;DGS10_d1;btc_ret_lag1 | lag < 0 means x is shifted earlier and leads the target; lag -1 uses x[t-1] to explain y[t] | ok     |
| btc     | btc_ret  | btc_etf_intensity |    -2 |        2.3949 |   4.5406 |  0.5274 | 0.5979 | 820 | 0.1514 | spy_ret;VIXCLS_d1;DGS10_d1;btc_ret_lag1 | lag < 0 means x is shifted earlier and leads the target; lag -1 uses x[t-1] to explain y[t] | ok     |
| btc     | btc_ret  | btc_etf_intensity |    -1 |       10.7159 |   5.7289 |  1.8705 | 0.0614 | 821 | 0.1539 | spy_ret;VIXCLS_d1;DGS10_d1;btc_ret_lag1 | lag < 0 means x is shifted earlier and leads the target; lag -1 uses x[t-1] to explain y[t] | ok     |
| btc     | btc_ret  | btc_etf_intensity |     0 |       56.869  |   5.5621 | 10.2243 | 0      | 820 | 0.2709 | spy_ret;VIXCLS_d1;DGS10_d1;btc_ret_lag1 | lag < 0 means x is shifted earlier and leads the target; lag -1 uses x[t-1] to explain y[t] | ok     |
| btc     | btc_ret  | btc_etf_intensity |     1 |       47.4068 |   4.3119 | 10.9945 | 0      | 819 | 0.2469 | spy_ret;VIXCLS_d1;DGS10_d1;btc_ret_lag1 | lag < 0 means x is shifted earlier and leads the target; lag -1 uses x[t-1] to explain y[t] | ok     |
| btc     | btc_ret  | btc_etf_intensity |     2 |       23.3018 |   4.0832 |  5.7067 | 0      | 818 | 0.1736 | spy_ret;VIXCLS_d1;DGS10_d1;btc_ret_lag1 | lag < 0 means x is shifted earlier and leads the target; lag -1 uses x[t-1] to explain y[t] | ok     |
| btc     | btc_ret  | btc_etf_intensity |     3 |       15.0955 |   3.8137 |  3.9582 | 0.0001 | 817 | 0.1628 | spy_ret;VIXCLS_d1;DGS10_d1;btc_ret_lag1 | lag < 0 means x is shifted earlier and leads the target; lag -1 uses x[t-1] to explain y[t] | ok     |
| btc     | btc_ret  | btc_etf_intensity |     4 |        9.3992 |   4.4842 |  2.0961 | 0.0361 | 816 | 0.1577 | spy_ret;VIXCLS_d1;DGS10_d1;btc_ret_lag1 | lag < 0 means x is shifted earlier and leads the target; lag -1 uses x[t-1] to explain y[t] | ok     |
| btc     | btc_ret  | btc_etf_intensity |     5 |        2.9538 |   4.9293 |  0.5992 | 0.549  | 815 | 0.1542 | spy_ret;VIXCLS_d1;DGS10_d1;btc_ret_lag1 | lag < 0 means x is shifted earlier and leads the target; lag -1 uses x[t-1] to explain y[t] | ok     |

ETH ETF lead-lag return rows:

| asset   | target   | x                 |   lag |   coefficient |   hac_se |       t |      p |   n |     r2 | controls                                | lag_convention                                                                              | note   |
|:--------|:---------|:------------------|------:|--------------:|---------:|--------:|-------:|----:|-------:|:----------------------------------------|:--------------------------------------------------------------------------------------------|:-------|
| eth     | eth_ret  | eth_etf_intensity |    -5 |        5.0376 |   4.6397 |  1.0858 | 0.2776 | 623 | 0.214  | spy_ret;VIXCLS_d1;DGS10_d1;eth_ret_lag1 | lag < 0 means x is shifted earlier and leads the target; lag -1 uses x[t-1] to explain y[t] | ok     |
| eth     | eth_ret  | eth_etf_intensity |    -4 |        3.0761 |   4.1581 |  0.7398 | 0.4594 | 624 | 0.2131 | spy_ret;VIXCLS_d1;DGS10_d1;eth_ret_lag1 | lag < 0 means x is shifted earlier and leads the target; lag -1 uses x[t-1] to explain y[t] | ok     |
| eth     | eth_ret  | eth_etf_intensity |    -3 |       -4.9649 |   4.1659 | -1.1918 | 0.2333 | 625 | 0.2149 | spy_ret;VIXCLS_d1;DGS10_d1;eth_ret_lag1 | lag < 0 means x is shifted earlier and leads the target; lag -1 uses x[t-1] to explain y[t] | ok     |
| eth     | eth_ret  | eth_etf_intensity |    -2 |       -0.9054 |   4.9993 | -0.1811 | 0.8563 | 626 | 0.214  | spy_ret;VIXCLS_d1;DGS10_d1;eth_ret_lag1 | lag < 0 means x is shifted earlier and leads the target; lag -1 uses x[t-1] to explain y[t] | ok     |
| eth     | eth_ret  | eth_etf_intensity |    -1 |        9.9507 |   5.0851 |  1.9568 | 0.0504 | 627 | 0.2207 | spy_ret;VIXCLS_d1;DGS10_d1;eth_ret_lag1 | lag < 0 means x is shifted earlier and leads the target; lag -1 uses x[t-1] to explain y[t] | ok     |
| eth     | eth_ret  | eth_etf_intensity |     0 |       25.2171 |   5.3903 |  4.6782 | 0      | 626 | 0.2477 | spy_ret;VIXCLS_d1;DGS10_d1;eth_ret_lag1 | lag < 0 means x is shifted earlier and leads the target; lag -1 uses x[t-1] to explain y[t] | ok     |
| eth     | eth_ret  | eth_etf_intensity |     1 |       28.9026 |   5.0747 |  5.6955 | 0      | 625 | 0.2612 | spy_ret;VIXCLS_d1;DGS10_d1;eth_ret_lag1 | lag < 0 means x is shifted earlier and leads the target; lag -1 uses x[t-1] to explain y[t] | ok     |
| eth     | eth_ret  | eth_etf_intensity |     2 |       15.5156 |   5.1212 |  3.0297 | 0.0024 | 624 | 0.2295 | spy_ret;VIXCLS_d1;DGS10_d1;eth_ret_lag1 | lag < 0 means x is shifted earlier and leads the target; lag -1 uses x[t-1] to explain y[t] | ok     |
| eth     | eth_ret  | eth_etf_intensity |     3 |        8.0553 |   4.0387 |  1.9946 | 0.0461 | 623 | 0.2261 | spy_ret;VIXCLS_d1;DGS10_d1;eth_ret_lag1 | lag < 0 means x is shifted earlier and leads the target; lag -1 uses x[t-1] to explain y[t] | ok     |
| eth     | eth_ret  | eth_etf_intensity |     4 |       15.5998 |   3.998  |  3.9019 | 0.0001 | 622 | 0.2375 | spy_ret;VIXCLS_d1;DGS10_d1;eth_ret_lag1 | lag < 0 means x is shifted earlier and leads the target; lag -1 uses x[t-1] to explain y[t] | ok     |
| eth     | eth_ret  | eth_etf_intensity |     5 |       10.6812 |   4.7056 |  2.2699 | 0.0232 | 621 | 0.2306 | spy_ret;VIXCLS_d1;DGS10_d1;eth_ret_lag1 | lag < 0 means x is shifted earlier and leads the target; lag -1 uses x[t-1] to explain y[t] | ok     |

ETF-flow intensity is contemporaneous/lag association. It should be discussed as
market plumbing and simultaneity-sensitive evidence, not causal impact.

## Rolling Correlations And Regimes

The v2.1 dashboard writes rolling 60/180/365-day correlations and pre/post ETF
delta tables. Event markers include FTX, SVB, BTC ETF, BTC halving, and ETH ETF
dates. These are descriptive co-movement diagnostics.

## Stablecoin Liquidity

Stablecoin supply growth and TVL growth are liquidity proxies. BTC stablecoin
lead-lag rows:

| asset   | target   | x                     |   lag |   coefficient |   hac_se |      t |      p |    n |     r2 | controls                                | lag_convention                                                                              | note   |
|:--------|:---------|:----------------------|------:|--------------:|---------:|-------:|-------:|-----:|-------:|:----------------------------------------|:--------------------------------------------------------------------------------------------|:-------|
| btc     | btc_ret  | stables_total_usd_ret |    -5 |        0.0643 |   0.1365 | 0.4712 | 0.6375 | 2287 | 0.1261 | spy_ret;VIXCLS_d1;DGS10_d1;btc_ret_lag1 | lag < 0 means x is shifted earlier and leads the target; lag -1 uses x[t-1] to explain y[t] | ok     |
| btc     | btc_ret  | stables_total_usd_ret |    -4 |        0.1747 |   0.1585 | 1.1023 | 0.2703 | 2288 | 0.1267 | spy_ret;VIXCLS_d1;DGS10_d1;btc_ret_lag1 | lag < 0 means x is shifted earlier and leads the target; lag -1 uses x[t-1] to explain y[t] | ok     |
| btc     | btc_ret  | stables_total_usd_ret |    -3 |        0.0023 |   0.1617 | 0.0143 | 0.9886 | 2289 | 0.1259 | spy_ret;VIXCLS_d1;DGS10_d1;btc_ret_lag1 | lag < 0 means x is shifted earlier and leads the target; lag -1 uses x[t-1] to explain y[t] | ok     |
| btc     | btc_ret  | stables_total_usd_ret |    -2 |        0.0318 |   0.1504 | 0.2116 | 0.8324 | 2290 | 0.126  | spy_ret;VIXCLS_d1;DGS10_d1;btc_ret_lag1 | lag < 0 means x is shifted earlier and leads the target; lag -1 uses x[t-1] to explain y[t] | ok     |
| btc     | btc_ret  | stables_total_usd_ret |    -1 |        0.156  |   0.14   | 1.1146 | 0.265  | 2291 | 0.1259 | spy_ret;VIXCLS_d1;DGS10_d1;btc_ret_lag1 | lag < 0 means x is shifted earlier and leads the target; lag -1 uses x[t-1] to explain y[t] | ok     |
| btc     | btc_ret  | stables_total_usd_ret |     0 |        0.1325 |   0.1734 | 0.7644 | 0.4446 | 2291 | 0.1258 | spy_ret;VIXCLS_d1;DGS10_d1;btc_ret_lag1 | lag < 0 means x is shifted earlier and leads the target; lag -1 uses x[t-1] to explain y[t] | ok     |
| btc     | btc_ret  | stables_total_usd_ret |     1 |        0.7594 |   0.1715 | 4.4291 | 0      | 2290 | 0.1399 | spy_ret;VIXCLS_d1;DGS10_d1;btc_ret_lag1 | lag < 0 means x is shifted earlier and leads the target; lag -1 uses x[t-1] to explain y[t] | ok     |
| btc     | btc_ret  | stables_total_usd_ret |     2 |        0.5906 |   0.1403 | 4.2082 | 0      | 2289 | 0.1342 | spy_ret;VIXCLS_d1;DGS10_d1;btc_ret_lag1 | lag < 0 means x is shifted earlier and leads the target; lag -1 uses x[t-1] to explain y[t] | ok     |
| btc     | btc_ret  | stables_total_usd_ret |     3 |        0.3541 |   0.1365 | 2.594  | 0.0095 | 2288 | 0.1285 | spy_ret;VIXCLS_d1;DGS10_d1;btc_ret_lag1 | lag < 0 means x is shifted earlier and leads the target; lag -1 uses x[t-1] to explain y[t] | ok     |
| btc     | btc_ret  | stables_total_usd_ret |     4 |        0.1974 |   0.1435 | 1.3748 | 0.1692 | 2287 | 0.1272 | spy_ret;VIXCLS_d1;DGS10_d1;btc_ret_lag1 | lag < 0 means x is shifted earlier and leads the target; lag -1 uses x[t-1] to explain y[t] | ok     |
| btc     | btc_ret  | stables_total_usd_ret |     5 |        0.1199 |   0.1608 | 0.746  | 0.4557 | 2286 | 0.1269 | spy_ret;VIXCLS_d1;DGS10_d1;btc_ret_lag1 | lag < 0 means x is shifted earlier and leads the target; lag -1 uses x[t-1] to explain y[t] | ok     |

Stablecoin results are funding-context diagnostics and should not be described
as proven causal drivers.

## BTC-Native Factor Lab

Native registry:

| group                  | feature                       | available   |   non_missing | interpretation                                                    | portfolio_note                                       |
|:-----------------------|:------------------------------|:------------|--------------:|:------------------------------------------------------------------|:-----------------------------------------------------|
| market_structure_basis | cme_btc_basis_close_d1        | True        |          1942 | BTC futures basis or market-structure state.                      | Reduced-form input; not a standalone trading signal. |
| exchange_flow          | btc_exchange_netflow_d1       | True        |          2292 | Exchange netflow proxy; descriptive flow state.                   | Reduced-form input; not a standalone trading signal. |
| miner_flow             | btc_miner_to_exchange_flow_d1 | True        |          2292 | Miner-to-exchange flow proxy; descriptive supply pressure state.  | Reduced-form input; not a standalone trading signal. |
| valuation_state        | btc_mvrv_d1                   | True        |          2292 | MVRV valuation-state change; can mechanically co-move with price. | Reduced-form input; not a standalone trading signal. |

MVRV is explicitly separated from non-MVRV native variables because valuation
state can mechanically co-move with BTC returns.

## Structural-Break Diagnostics

The baseline packet remains the source for structural-break diagnostics:
`baseline_structural_breaks_summary.csv`. The current implementation is Chow
tests plus a single-break sup-F sweep, not full Bai-Perron.

## VAR/FEVD Connectedness

The baseline compact FEVD table is copied as `baseline_fevd_10d_compact.csv`.
It is a connectedness diagnostic under the stated VAR ordering, not a structural
shock-identification model.

## Event Studies

The baseline event-study table is copied as `baseline_event_studies.csv`.
Event-window CARs are reduced-form associations and remain confounded by
overlapping market news.

## Limitations

- Daily ETF-flow data is simultaneity-prone.
- Full-vs-reduced block partial R^2 can be unstable with correlated blocks.
- Rolling correlations and pre/post deltas describe co-movement, not causes.
- Stablecoin supply is a proxy, not a directly identified liquidity shock.
- Native factors, especially MVRV, can be mechanically linked to price.

## Reproducibility

```powershell
uv run pytest
uv run mypy src/cqresearch
uv run python scripts/run_portfolio_v2_1_pipeline.py
uv run ruff check scripts/run_portfolio_v2_1_pipeline.py src/cqresearch/modeling/partial_r2.py src/cqresearch/modeling/lead_lag.py src/cqresearch/modeling/ablation.py src/cqresearch/analysis/portfolio_v2_1.py tests/unit/test_partial_r2.py tests/unit/test_lead_lag.py tests/unit/test_ablation.py tests/unit/test_portfolio_v2_1_pipeline.py
```
