# Maintained Architecture

The maintained public build path is:

- `src/cqresearch/pipelines/final_research.py` for orchestration.
- `scripts/build_data_inventory.py` for source inventory.
- `scripts/build_feature_store.py` for deterministic panels.
- `scripts/build_analysis_outputs.py` for tables, reports, and model cards.
- `scripts/build_public_figures.py` for six README figures, one gallery appendix figure, and the QA contact sheet.
- `scripts/check_public_surface.py` for README/output guardrails.
- `scripts/run_all.py` for the complete offline build.

Legacy portfolio and versioned release workflows are not part of the maintained public surface.
