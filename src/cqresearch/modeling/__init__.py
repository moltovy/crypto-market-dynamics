"""cqresearch.modeling - econometric primitives.

Implemented modules:
    - ols.py               : static OLS with HAC standard errors
    - rolling.py           : rolling OLS with drop-one marginal R^2
    - partial_r2.py        : full-vs-reduced block partial R^2
    - ablation.py          : nested BTC/ETH ablation tables
    - lead_lag.py          : lead-lag regressions and flow quintiles
    - structural_breaks.py : Chow tests and single-break sup-F sweeps
    - var_fevd.py          : compact VAR with FEVD connectedness
    - event_study.py       : CARs around pre-registered dates in config/events.yml
    - pca_blocks.py        : block-level PCA factors for diagnostics
    - shapley_r2.py        : exact static and stepped rolling block Shapley R^2
    - cusum.py             : exploratory standardized residual CUSUM diagnostics
    - fevd_sensitivity.py  : FEVD ordering sensitivity tables
    - rolling_connectedness.py : stepped rolling VAR/FEVD connectedness
    - robustness_grid.py   : compact HAC/window/winsor/calendar robustness grid
"""
