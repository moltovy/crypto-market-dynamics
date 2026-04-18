# tools/

Operational scripts for **data collection** and **data curation**.

Run them via `run_pipeline.py` at the repo root, not individually, unless debugging. The orchestrator enforces the correct execution order (which is not the same as the filename-numeric order — see §"Execution order" below).

All scripts import paths from `config/paths.py`. Snapshot-specific dates (e.g. DefiLlama monthly dumps) come from `config/curation_snapshots.yml`. **Never** hardcode a date in a new script; add a key to `curation_snapshots.yml` instead.

---

## Layout

```
tools/
├── data_collection/          # Fetchers (pull external data into Data/)
│   ├── fetch_fred.py                 # Requires FRED_API_KEY
│   ├── fetch_fear_greed.py
│   ├── fetch_farside_etf_csv.py      # BUG-FIXED 2026-04-18 — now writes to Data/
│   ├── harvest_defillama.py          # Default --spec lives under archive/
│   └── organize_cryptoquant_metrics.py  # BUG-FIXED 2026-04-18 — parents[2]
└── data_curation/            # One-shot + repeatable transforms of Data/
    ├── _common.py                    # shared helpers, imports config/paths.py
    ├── 01_snapshot_raw_hashes.py
    ├── 02_dedupe_defi.py             # snapshot dates in curation_snapshots.yml
    ├── 03_merge_defi_parts.py
    ├── 04_normalize_dates.py
    ├── 05_rename_tradingview.py
    ├── 06_build_inventory.py         # FINAL step — writes Data/MASTER_DATA.md
    ├── 07_validate.py                # backup_dir in curation_snapshots.yml
    ├── 08_consolidate_defi.py
    ├── 09_reorg_tradingview.py
    ├── 10_clean_new_defi.py
    └── 11_flatten_farside.py
```

---

## Execution order (authoritative)

```
ingest  ->  fetch_fred
            fetch_fear_greed
            fetch_farside_etf_csv
            harvest_defillama
curate  ->  01 -> 02 -> 03 -> 04 -> 05 -> 08 -> 09 -> 10 -> 11 -> 06 -> 07
```

Why is 06 second-to-last and 07 last? Because 06 (build inventory) and 07 (validate) must see every other curation step's output.

---

## Quick commands

```powershell
# Full pipeline (ingest + curate)
python run_pipeline.py

# Curation only
python run_pipeline.py --only curate

# From a specific step
python run_pipeline.py --from-step curate.10_clean_new_defi

# Dry-run (print plan, don't execute)
python run_pipeline.py --dry-run
```

---

## Adding a new snapshot

When a new DefiLlama dump arrives (e.g. 2026-07-01):

1. Drop the raw CSVs in `Data/DefiLlama/_raw_parts/<category>/`.
2. Add the date to `config/curation_snapshots.yml`:
   ```yaml
   dedupe_defi:
     target_dates:
       - 2026-04-17
       - 2026-04-14
       - 2026-07-01   # NEW
   ```
3. Run `python run_pipeline.py --from-step curate.02_dedupe_defi`.

Do NOT edit scripts for snapshot changes.
