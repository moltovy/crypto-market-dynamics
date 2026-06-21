# Attribution Methods

## Drop-Block Delta R-Squared

The canonical block table reports `R2_full - R2_reduced` as `drop_block_delta_r2`.
This is a same-support model-sensitivity diagnostic. It is not labeled
conventional partial R-squared.

## Conventional Partial R-Squared

For readers who need the conventional formula, the separate
`research/02_macro_cross_asset_exposure/tables/conventional_partial_r2.csv` table reports
`(SSE_reduced - SSE_full) / SSE_reduced`.

## Interpretation

Attribution diagnostics can be unstable when feature blocks are correlated. Read
contemporaneous TradFi models as co-movement/integration evidence and lagged
state models as lagged-state associations, not causal contribution or forecast
importance.
