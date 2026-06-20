# Crypto Market Dynamics - maintained build targets

.PHONY: help setup install inventory features analysis figures outputs check-public-surface test typecheck lint verify format clean

help:
	@echo "Targets:"
	@echo "  setup                - install dependencies with uv"
	@echo "  inventory            - rebuild data inventory and source coverage"
	@echo "  features             - rebuild canonical feature stores"
	@echo "  analysis             - rebuild semantic tables, reports, and model cards"
	@echo "  figures              - rebuild the nine public figures"
	@echo "  outputs              - run the complete canonical offline build"
	@echo "  check-public-surface - validate README/output/public-surface guardrails"
	@echo "  test                 - run pytest"
	@echo "  typecheck            - run mypy"
	@echo "  lint                 - run Ruff on maintained source/script/test trees"
	@echo "  verify               - run the final local release gate"
	@echo "  clean                - remove local caches and build artifacts"

setup:
	uv sync --all-extras

install: setup

inventory:
	uv run python scripts/build_data_inventory.py

features:
	uv run python scripts/build_feature_store.py

analysis:
	uv run python scripts/build_analysis_outputs.py

figures:
	uv run python scripts/build_public_figures.py

outputs:
	uv run python scripts/run_all.py

check-public-surface:
	uv run python scripts/check_public_surface.py

test:
	uv run pytest

typecheck:
	uv run mypy src/cqresearch

lint:
	uv run ruff check src/cqresearch scripts tests

format:
	uv run ruff format src/cqresearch scripts tests

verify: setup lint typecheck test outputs check-public-surface

clean:
	uv run python -c "import shutil; [shutil.rmtree(p, ignore_errors=True) for p in ['.pytest_cache', '.ruff_cache', '.mypy_cache', 'build', 'dist']]"
