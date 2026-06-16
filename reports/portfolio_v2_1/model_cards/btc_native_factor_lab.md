# Model Card - BTC-Native Factor Lab

## Purpose

Separate BTC-native valuation state from flow/market-structure variables.

## Inputs

BTC basis, exchange netflow, miner-to-exchange flow, and MVRV changes.

## Sample

Full native-variable support from the frozen panel.

## Method

Registry, z-score dashboard, native ablation, and correlations.

## Output files

`native_factor_registry.csv`, `btc_native_ablation.csv`, `btc_native_correlations.csv`.

## Interpretation

Research lens for BTC-native state; not a standalone trade signal.

## Risks / limitations

MVRV can mechanically co-move with price and dominate fit.

## Upgrade path

Add more native variables only with cached, documented source support.
