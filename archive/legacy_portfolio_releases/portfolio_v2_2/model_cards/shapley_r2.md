# Model Card - Exact Block Shapley R2

## Purpose

Allocate model R2 across factor blocks using exact coalition enumeration.

## Inputs

BTC/ETH returns and standardized non-ETF factor blocks.

## Sample

Static full sample plus stepped 180-day rolling windows.

## Method

Enumerate all block subsets and average marginal R2 contributions by Shapley weights.

## Output files

`shapley_r2_btc.csv`, `shapley_r2_eth.csv`, `rolling_shapley_r2_*`, `F72`, `F73`.

## Interpretation

Shows which specified blocks receive more predictive attribution in the selected design.

## Risks / limitations

Shapley attribution depends on block definitions and the linear model design; it is not causal proof.

## Upgrade path

Add Owen grouping for nested block hierarchies if future specs require it.
