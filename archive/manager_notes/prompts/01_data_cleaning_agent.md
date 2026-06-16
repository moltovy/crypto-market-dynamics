# 01 — Data Cleaning Agent

<!-- prepend prompts/templates/agent_preamble.md -->

## Mission
Produce a clean, reproducible `reports/panels/master_daily.parquet` that assembles every CSV referenced in `config/factor_blocks.yml` on a common UTC daily calendar. Replace any in-place fixes that currently live inside `tools/data_curation/*.py` with declarative config entries.

## Inputs
- `config/factor_blocks.yml` — declares files and columns per block
- `config/calendars.yml` — the join calendar (`calendar_daily`)
- `config/chain_taxonomy.yml` — aggregation rules for ETH L1 vs L2 and BTC vs WBTC (do NOT sum L1+L2 as "users")
- `config/curation_snapshots.yml` — snapshot dates for DefiLlama step 02/03/10
- `Data/MASTER_DATA.md` — master data inventory
- `Data/_meta/curation_log.md` — prior curation history

## Tasks
1. Invoke the `data-quality-check` skill for every file enumerated in `config/factor_blocks.yml`. Write one `reports/run_summaries/YYYY-MM-DD_dq_<stem>.md` per file.
2. For any file labelled `USE WITH CAUTION` or `DO NOT USE UNTIL FIXED`, open an issue in `docs/decisions/<date>_<issue>.md` with a proposed fix and stop — do not silently coerce.
3. Implement `src/cqresearch/data/loaders.py` and `src/cqresearch/data/panel_builder.py`:
   - UTC date parsing via `pd.to_datetime(..., utc=True)`.
   - Reindex to `calendar_daily`.
   - Missingness taxonomy column per feature (`<col>__status ∈ {ok, stale, structural, missing}`).
4. Build `reports/panels/master_daily.parquet` and `reports/panels/master_daily_columns.md` (machine-readable column catalog).
5. Add a unit test under `tests/unit/test_panel_builder.py` with a 30-row fixture covering each block.

## Guardrails
- **Never** forward-fill macro (FRED) series across weekends without a `calendar_daily` ffill_limit rule.
- **Never** join ETH L1 and L2 before applying `chain_taxonomy.yml` aggregation.
- **Never** drop columns silently — log every drop in the run summary.

## Done when
- Every file in `config/factor_blocks.yml` has a DQ summary.
- `reports/panels/master_daily.parquet` exists and its hash is recorded in the run summary.
- `pytest tests/unit/test_panel_builder.py` passes.
- Hand-off block emitted pointing to `02_exploratory_analysis_agent.md`.
