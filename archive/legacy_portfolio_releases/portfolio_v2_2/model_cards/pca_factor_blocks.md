# Model Card - PCA Factor Blocks

## Purpose

Compress related factor blocks into a small number of standardized components.

## Inputs

Frozen feature panel columns grouped into macro, TradFi, liquidity, BTC-native, and ETF-flow blocks.

## Sample

Full frozen daily panel; blocks with fewer than two usable variables are skipped.

## Method

Standardize each block, fit sklearn PCA independently, and retain up to two components.

## Output files

`pca_block_loadings.csv`, `pca_explained_variance.csv`, `F70`, `F71`.

## Interpretation

Components summarize co-movement inside feature blocks and support visual diagnostics.

## Risks / limitations

PCA signs are arbitrary; components are statistical summaries, not structural factors.

## Upgrade path

Add out-of-sample stability checks and component sign anchoring.
