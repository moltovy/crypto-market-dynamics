# Model Card - Stablecoin Liquidity

## Purpose

Use stablecoin growth and TVL growth as liquidity/funding proxies.

## Inputs

Stablecoin supply, DeFi TVL, BTC/ETH returns, realized volatility.

## Sample

Full frozen panel with 30-day realized-volatility support.

## Method

Z-score composite, lead-lag OLS, and quintile summaries.

## Output files

`stablecoin_liquidity_features.csv`, stablecoin lead-lag/quintile tables.

## Interpretation

Liquidity context, not a proven causal funding channel.

## Risks / limitations

Proxy measurement error and confounding by broad risk appetite.

## Upgrade path

Add source-specific stablecoin flows and local projections if justified.
