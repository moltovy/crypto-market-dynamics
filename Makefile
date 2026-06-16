# Crypto Market Factor Lab - Makefile
# Usage: `make <target>`. On Windows, invoke via `make` if GNU Make is installed
# (for example, `choco install make`), or run the equivalent commands directly.

RUFF_PORTFOLIO_PATHS = \
	scripts/export_outputs.py \
	scripts/run_all.py \
	scripts/run_portfolio_pipeline.py \
	scripts/run_portfolio_v2_1_pipeline.py \
	scripts/run_portfolio_v2_2_pipeline.py \
	scripts/optional_data \
	src/cqresearch/analysis/native_factors.py \
	src/cqresearch/analysis/portfolio_v2_1.py \
	src/cqresearch/analysis/portfolio_v2_2.py \
	src/cqresearch/features/volatility.py \
	src/cqresearch/modeling/partial_r2.py \
	src/cqresearch/modeling/ablation.py \
	src/cqresearch/modeling/lead_lag.py \
	src/cqresearch/modeling/pca_blocks.py \
	src/cqresearch/modeling/shapley_r2.py \
	src/cqresearch/modeling/cusum.py \
	src/cqresearch/modeling/fevd_sensitivity.py \
	src/cqresearch/modeling/rolling_connectedness.py \
	src/cqresearch/modeling/robustness_grid.py \
	src/cqresearch/optional_data \
	tests/unit/test_partial_r2.py \
	tests/unit/test_lead_lag.py \
	tests/unit/test_ablation.py \
	tests/unit/test_volatility.py \
	tests/unit/test_pca_blocks.py \
	tests/unit/test_shapley_r2.py \
	tests/unit/test_cusum.py \
	tests/unit/test_fevd_sensitivity.py \
	tests/unit/test_rolling_connectedness.py \
	tests/unit/test_robustness_grid.py \
	tests/unit/test_portfolio_v2_1_pipeline.py \
	tests/unit/test_portfolio_v2_2_pipeline.py \
	tests/unit/test_optional_data_sources.py

.PHONY: help install setup ingest curate inventory validate pipeline test typecheck lint format figures outputs portfolio portfolio-v2 portfolio-v2-1 portfolio-v2-2 optional-data verify clean

help:
	@echo "Targets:"
	@echo "  setup          - create uv venv and install deps (dev extras)"
	@echo "  install        - alias for setup"
	@echo "  ingest         - run legacy data collection scripts"
	@echo "  curate         - run the full frozen-panel pipeline"
	@echo "  inventory      - rebuild Data/MASTER_DATA.{md,txt,csv}"
	@echo "  validate       - run config/data unit checks"
	@echo "  pipeline       - run scripts/run_full_pipeline.py"
	@echo "  test           - run pytest"
	@echo "  typecheck      - run mypy"
	@echo "  lint           - run focused Ruff + mypy"
	@echo "  format         - run ruff format on source/script/test trees"
	@echo "  figures        - rebuild cached figure outputs"
	@echo "  outputs        - export canonical public artifact packet"
	@echo "  portfolio-v2   - legacy: build baseline portfolio packet"
	@echo "  portfolio-v2-1 - legacy: build enhanced portfolio packet"
	@echo "  portfolio-v2-2 - legacy: build advanced diagnostics packet"
	@echo "  optional-data  - verify optional free-data scaffolding"
	@echo "  verify         - run public-readiness verification targets"
	@echo "  clean          - remove caches and build artifacts"

setup:
	uv sync --all-extras

install: setup

ingest:
	uv run python tools/data_collection/fetch_fred.py
	uv run python tools/data_collection/fetch_fear_greed.py
	uv run python tools/data_collection/fetch_farside_etf_csv.py
	uv run python tools/data_collection/harvest_defillama.py

curate:
	uv run python scripts/run_full_pipeline.py

inventory:
	uv run python tools/data_curation/06_build_inventory.py

validate:
	uv run pytest tests/unit/test_config_yamls.py tests/unit/test_fixtures.py

pipeline:
	uv run python scripts/run_full_pipeline.py

test:
	uv run pytest

typecheck:
	uv run mypy src/cqresearch

lint:
	uv run ruff check $(RUFF_PORTFOLIO_PATHS)
	uv run mypy src/cqresearch

format:
	uv run ruff format src scripts tests

figures:
	uv run python scripts/03_make_figures.py

outputs:
	uv run python scripts/run_all.py

portfolio: outputs

portfolio-v2:
	uv run python scripts/run_portfolio_pipeline.py

portfolio-v2-1:
	uv run python scripts/run_portfolio_v2_1_pipeline.py

portfolio-v2-2:
	uv run python scripts/run_portfolio_v2_2_pipeline.py

optional-data:
	uv run pytest tests/unit/test_optional_data_sources.py
	uv run ruff check src/cqresearch/optional_data scripts/optional_data tests/unit/test_optional_data_sources.py

verify: test lint outputs optional-data
	git status --short -- Data

clean:
	uv run python -c "import shutil; [shutil.rmtree(p, ignore_errors=True) for p in ['.pytest_cache', '.ruff_cache', '.mypy_cache', 'build', 'dist']]"
