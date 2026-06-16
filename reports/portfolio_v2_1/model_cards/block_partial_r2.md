# Model Card - Block Partial R^2

## Purpose

Measure factor-block contribution by comparing full and reduced models.

## Inputs

BTC/ETH returns and standardized feature blocks.

## Sample

Full, pre/post BTC ETF, and post ETH ETF where available.

## Method

Full-vs-reduced block partial R^2: `(RSS_reduced - RSS_full) / TSS`.

## Output files

`block_partial_r2_btc.csv`, `block_partial_r2_eth.csv`, rolling block tables.

## Interpretation

Contribution conditional on the specified full model; not Shapley/Owen.

## Risks / limitations

Correlated blocks can shift contribution between blocks.

## Upgrade path

Add Shapley/Owen only as a tested appendix and compare labels carefully.
