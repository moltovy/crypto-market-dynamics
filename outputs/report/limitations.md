# Limitations

- Daily data cannot identify intraday market mechanisms or order flow.
- ETF-flow, stablecoin, and native-factor results are reduced-form diagnostics,
  not causal identification.
- Stablecoin supply and TVL are liquidity proxies, not proven liquidity shocks.
- Structural-break diagnostics use Chow tests and single-break sup-F sweeps,
  not full Bai-Perron multiple-break estimation.
- Block partial R2 and exact Shapley R2 depend on block definitions and the
  selected feature set.
- Frozen data supports reproducibility but is not a live market monitor.
- Broad repository linting still includes legacy files; maintained public
  surfaces use focused Ruff, mypy, and pytest checks.
