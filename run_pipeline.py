"""Top-level pipeline orchestrator.

Runs the ingestion + curation scripts in the correct EXECUTION order. Note that
the *filename* number does NOT always equal the *execution* order: some curation
scripts were added later (08, 09, 10, 11) and must slot in before the final
inventory (06) and validation (07).

Execution order (updated 2026-04-18):
    ingest:  tools/data_collection/fetch_fred.py
             tools/data_collection/fetch_fear_greed.py
             tools/data_collection/fetch_farside_etf_csv.py
             tools/data_collection/harvest_defillama.py
    curate:  01_snapshot_raw_hashes.py
             02_dedupe_defi.py
             03_merge_defi_parts.py
             04_normalize_dates.py
             05_rename_tradingview.py
             08_consolidate_defi.py
             09_reorg_tradingview.py
             10_clean_new_defi.py
             11_flatten_farside.py
             06_build_inventory.py
             07_validate.py

Use ``--dry-run`` to print the plan without invoking scripts.
Use ``--from-step N`` / ``--to-step N`` to restrict to a slice.
"""

from __future__ import annotations

import argparse
import subprocess
import sys
from pathlib import Path

from config.paths import PROJECT_ROOT

INGEST_STEPS: list[tuple[str, Path]] = [
    ("ingest.fred",          PROJECT_ROOT / "tools" / "data_collection" / "fetch_fred.py"),
    ("ingest.fear_greed",    PROJECT_ROOT / "tools" / "data_collection" / "fetch_fear_greed.py"),
    ("ingest.farside_etf",   PROJECT_ROOT / "tools" / "data_collection" / "fetch_farside_etf_csv.py"),
    ("ingest.defillama",     PROJECT_ROOT / "tools" / "data_collection" / "harvest_defillama.py"),
]

CURATE_STEPS: list[tuple[str, Path]] = [
    ("curate.01_snapshot",            PROJECT_ROOT / "tools" / "data_curation" / "01_snapshot_raw_hashes.py"),
    ("curate.02_dedupe_defi",         PROJECT_ROOT / "tools" / "data_curation" / "02_dedupe_defi.py"),
    ("curate.03_merge_defi",          PROJECT_ROOT / "tools" / "data_curation" / "03_merge_defi_parts.py"),
    ("curate.04_normalize_dates",     PROJECT_ROOT / "tools" / "data_curation" / "04_normalize_dates.py"),
    ("curate.05_rename_tv",           PROJECT_ROOT / "tools" / "data_curation" / "05_rename_tradingview.py"),
    ("curate.08_consolidate_defi",    PROJECT_ROOT / "tools" / "data_curation" / "08_consolidate_defi.py"),
    ("curate.09_reorg_tv",            PROJECT_ROOT / "tools" / "data_curation" / "09_reorg_tradingview.py"),
    ("curate.10_clean_new_defi",      PROJECT_ROOT / "tools" / "data_curation" / "10_clean_new_defi.py"),
    ("curate.11_flatten_farside",     PROJECT_ROOT / "tools" / "data_curation" / "11_flatten_farside.py"),
    ("curate.06_inventory",           PROJECT_ROOT / "tools" / "data_curation" / "06_build_inventory.py"),
    ("curate.07_validate",            PROJECT_ROOT / "tools" / "data_curation" / "07_validate.py"),
]

ALL_STEPS = INGEST_STEPS + CURATE_STEPS


def step_index(step_name: str) -> int:
    for i, (name, _) in enumerate(ALL_STEPS):
        if name == step_name or name.endswith("." + step_name):
            return i
    raise SystemExit(f"Unknown step: {step_name}")


def main() -> int:
    parser = argparse.ArgumentParser(description="CryptoQuant pipeline orchestrator")
    parser.add_argument("--dry-run", action="store_true", help="Print plan without executing")
    parser.add_argument("--from-step", default=None, help="First step name (e.g. 'curate.04_normalize_dates' or '04_normalize_dates')")
    parser.add_argument("--to-step", default=None, help="Last step name (inclusive)")
    parser.add_argument("--only", default=None, help="Run a single stage: 'ingest' or 'curate'")
    args = parser.parse_args()

    steps = ALL_STEPS
    if args.only == "ingest":
        steps = INGEST_STEPS
    elif args.only == "curate":
        steps = CURATE_STEPS

    start = step_index(args.from_step) if args.from_step else 0
    end = step_index(args.to_step) + 1 if args.to_step else len(steps)
    selected = steps[start:end]

    print(f"[pipeline] {'DRY-RUN' if args.dry_run else 'EXECUTING'} {len(selected)} step(s):")
    for name, path in selected:
        exists = "OK" if path.exists() else "MISSING"
        print(f"  [{exists}] {name}  ->  {path.relative_to(PROJECT_ROOT)}")

    if args.dry_run:
        return 0

    for name, path in selected:
        if not path.exists():
            print(f"[pipeline] SKIP {name} (script not found: {path})")
            continue
        print(f"\n[pipeline] --- RUN {name} ---")
        rc = subprocess.call([sys.executable, str(path)])
        if rc != 0:
            print(f"[pipeline] FAILED {name} (exit {rc}). Stopping.")
            return rc

    print("\n[pipeline] Done.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
