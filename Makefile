# CryptoQuant Research — Makefile
# Usage: `make <target>`. On Windows, invoke via `make` if GNU Make is installed
# (e.g. `choco install make`), or run the equivalent commands directly.

.PHONY: help setup ingest curate inventory validate pipeline test lint format figures paper clean

help:
	@echo "Targets:"
	@echo "  setup      - create uv venv and install deps (dev extras)"
	@echo "  ingest     - run data collection (FRED, Fear-Greed, Farside, DefiLlama)"
	@echo "  curate     - run curation pipeline (tools/data_curation/*)"
	@echo "  inventory  - rebuild Data/MASTER_DATA.{md,txt,csv}"
	@echo "  validate   - run tools/data_curation/07_validate.py"
	@echo "  pipeline   - run run_pipeline.py end-to-end"
	@echo "  test       - run pytest"
	@echo "  lint       - run ruff check + mypy"
	@echo "  format     - run ruff format"
	@echo "  figures    - rebuild reports/figures/ from cached panels"
	@echo "  paper      - build reports/drafts/paper_v1.md from sections/"
	@echo "  clean      - remove caches and build artifacts"

setup:
	uv sync --all-extras

ingest:
	python tools/data_collection/fetch_fred.py
	python tools/data_collection/fetch_fear_greed.py
	python tools/data_collection/fetch_farside_etf_csv.py
	python tools/data_collection/harvest_defillama.py

curate:
	python run_pipeline.py --from-step 01 --to-step 11

inventory:
	python tools/data_curation/06_build_inventory.py

validate:
	python tools/data_curation/07_validate.py

pipeline:
	python run_pipeline.py

test:
	pytest

lint:
	ruff check .
	mypy src/cqresearch

format:
	ruff format .

figures:
	python scripts/30_descriptives.py
	python scripts/50_rolling_and_partial_r2.py
	python scripts/70_var_fevd.py

paper:
	python scripts/99_export_paper_artifacts.py

clean:
	python -c "import shutil, pathlib; [shutil.rmtree(p, ignore_errors=True) for p in ['.pytest_cache', '.ruff_cache', '.mypy_cache', 'build', 'dist']]"
