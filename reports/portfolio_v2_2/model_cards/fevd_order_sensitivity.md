# Model Card - FEVD Order Sensitivity

## Purpose

Measure how compact VAR FEVD shares change under alternative variable orderings.

## Inputs

BTC, ETH, SPY, and VIX-derived return/difference features.

## Sample

Full frozen sample after complete-case filtering.

## Method

Run 10-day VAR FEVD under crypto-first, TradFi-first, risk-first, and ETH-first orderings.

## Output files

`fevd_order_sensitivity.csv`, `fevd_order_sensitivity_summary.csv`, `F76`.

## Interpretation

Large ranges indicate relationships whose variance accounting depends on ordering choices.

## Risks / limitations

Reduced-form FEVD is ordering-sensitive and does not establish structural shocks.

## Upgrade path

Add generalized FEVD or sign-restricted structural VAR variants.
