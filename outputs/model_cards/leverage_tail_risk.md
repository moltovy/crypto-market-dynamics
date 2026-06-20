# Leverage And Tail Risk Model Card

Purpose: evaluate leverage/funding/OI state and liquidation signatures as stress diagnostics.

Features and units: lagged OI/market-cap growth, funding z-score, leverage percentile, liquidation USD / lagged OI in percent, and liquidation USD / lagged market cap in basis points.

Principal finding: Q1 low tail-day rate=7.06% (n=453); Q3 tail-day rate=4.20% (n=452); Q5 high tail-day rate=7.73% (n=453); read as U-shaped state pattern.

Estimator: descriptive quintiles, lagged logit diagnostics, and top liquidation event response table.

Prohibited claims: liquidations initiated price moves.
