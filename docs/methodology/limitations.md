# Methodology Limitations

The project is intentionally reduced-form. It is built to make factor exposure,
market plumbing, regime, and robustness diagnostics inspectable, not to identify
structural shocks.

Daily frequency limits sequencing. ETF-flow, stablecoin, and native-factor
variables can move simultaneously with returns. Native valuation-state variables
such as MVRV can mechanically co-move with price. VAR/FEVD outputs are
ordering-sensitive and should be read as connectedness diagnostics.
