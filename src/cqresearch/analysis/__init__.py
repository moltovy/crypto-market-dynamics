"""cqresearch.analysis - orchestrators that glue features and models into outputs.

Current top-level orchestration lives in ``scripts/``:
    - 01_build_master_panel.py     : frozen daily panel build
    - 02_run_analyses.py           : OLS, rolling drop-one R^2, breaks, VAR/FEVD, events
    - 03_make_figures.py           : publication and portfolio figures
    - run_portfolio_pipeline.py    : portfolio_v2 artifact assembly
    - run_portfolio_v2_1_pipeline.py : enhanced portfolio_v2_1 analytics packet
"""
