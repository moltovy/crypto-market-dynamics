# Attribution Methods

## Block Partial R2

The canonical block attribution table uses full-vs-reduced block partial R2.
For each factor block, the diagnostic compares the full model with a reduced
model that removes that block.

This is not sequential R2 and not Shapley/Owen attribution.

## Exact Block Shapley R2

Advanced attribution enumerates block coalitions and allocates full-model R2
across blocks. The result is predictive attribution over the selected block
design, not causal contribution.

## Interpretation

Attribution results can be unstable when blocks are correlated. The outputs are
best read as model-sensitivity diagnostics.
