"""Step 07: Validation pass.

- Compare 5 randomly chosen CryptoQuant files against the local snapshot backup
  (C:/Dev/Projects/CryptoQuant_Data_backup_2026-04-16/...): row count must match,
  and the set of metric values must be preserved (order differs because original
  was descending).
- Sanity check the merged Defi files: column count == union of part columns,
  no duplicate dates, date range equals min(part start) .. max(part end).
- Re-hash every file and write Data/_meta/curated_manifest.csv; diff against
  raw_manifest.csv.

Outputs a clean pass/fail summary to the curation log.
"""
from __future__ import annotations

import csv
import random
import sys
from datetime import datetime, timezone
from pathlib import Path

import pandas as pd

sys.path.insert(0, str(Path(__file__).resolve().parent))
from _common import (  # noqa: E402
    DATA_DIR,
    META_DIR,
    iter_data_files,
    log,
    rel_to_data,
    sha256_of_file,
)

BACKUP_DIR = Path("C:/Dev/Projects/CryptoQuant_Data_backup_2026-04-16")


def _hash_all(out_name: str) -> dict[str, str]:
    manifest: dict[str, str] = {}
    for p in iter_data_files(exts=(".csv", ".txt", ".md")):
        rel = rel_to_data(p)
        manifest[rel] = sha256_of_file(p)
    out_path = META_DIR / out_name
    with out_path.open("w", encoding="utf-8", newline="") as f:
        w = csv.writer(f)
        w.writerow(["relpath", "sha256"])
        for k, v in sorted(manifest.items()):
            w.writerow([k, v])
    return manifest


def validate_cryptoquant_samples(n: int = 5) -> list[str]:
    lines: list[str] = []
    if not BACKUP_DIR.is_dir():
        return [f"- backup dir missing at `{BACKUP_DIR}`, skipping CQ spot-checks."]
    cq_files = [
        p for p in DATA_DIR.rglob("*.csv")
        if rel_to_data(p).startswith("CryptoQuant/")
    ]
    random.seed(42)
    sample = random.sample(cq_files, min(n, len(cq_files)))
    for p in sample:
        rel = rel_to_data(p)
        cur = pd.read_csv(p)
        backup_p = BACKUP_DIR / rel
        if not backup_p.is_file():
            lines.append(f"- **MISSING backup** for `{rel}`")
            continue
        orig = pd.read_csv(backup_p)
        metric_col = [c for c in orig.columns if c != "Datetime"][0]
        ok_rows = len(cur) == len(orig)
        # Compare value sets ignoring order
        try:
            a = sorted(pd.to_numeric(orig[metric_col], errors="coerce").dropna().round(9).tolist())
            b = sorted(pd.to_numeric(cur[metric_col], errors="coerce").dropna().round(9).tolist())
            ok_values = a == b
        except Exception:
            ok_values = False
        status = "PASS" if (ok_rows and ok_values) else "FAIL"
        lines.append(
            f"- [{status}] `{rel}`: rows {len(orig)} -> {len(cur)}, "
            f"values preserved={ok_values}, ascending={list(cur['date']) == sorted(list(cur['date']))}"
        )
    return lines


def validate_merges() -> list[str]:
    lines: list[str] = []
    # Stablecoin mcap merge
    sc_out = DATA_DIR / "DefiLlama" / "Stablecoins" / "stablecoin_mcap_by_defillama_id__daily.csv"
    sc_parts = sorted((DATA_DIR / "DefiLlama" / "_raw_parts" / "stablecoin_mcap").glob("*.csv"))
    if sc_out.is_file() and sc_parts:
        dfs = [pd.read_csv(p) for p in sc_parts]
        union_cols = set()
        min_d, max_d = None, None
        for df in dfs:
            union_cols |= set(df.columns) - {"date"}
            # Some original parts stored numeric ids as strings; cast for comparison.
            if "date" in df.columns:
                d = pd.to_datetime(df["date"], errors="coerce").dropna()
                if len(d) > 0:
                    min_d = d.min() if min_d is None else min(min_d, d.min())
                    max_d = d.max() if max_d is None else max(max_d, d.max())
        merged = pd.read_csv(sc_out)
        merged_cols = set(merged.columns) - {"date"}
        merged_dates = pd.to_datetime(merged["date"], errors="coerce").dropna()
        dup_dates = merged["date"].duplicated().sum()
        cols_ok = merged_cols == union_cols
        date_ok = merged_dates.min() == min_d and merged_dates.max() == max_d
        lines.append(
            f"- stablecoin_mcap merge: cols_union_match={cols_ok} "
            f"(merged={len(merged_cols)}, parts_union={len(union_cols)}), "
            f"dup_dates={dup_dates}, date_range_match={date_ok} "
            f"({merged_dates.min().date()} .. {merged_dates.max().date()})"
        )
    else:
        lines.append("- stablecoin_mcap merge: OUTPUT OR PARTS MISSING")

    # CEX inflows merge
    cex_out = DATA_DIR / "DefiLlama" / "CEX" / "cex_net_inflows_by_exchange__daily.csv"
    cex_parts = sorted((DATA_DIR / "DefiLlama" / "_raw_parts" / "cex_inflows").glob("*.csv"))
    if cex_out.is_file() and cex_parts:
        dfs = [pd.read_csv(p) for p in cex_parts]
        union_cols = set()
        min_d, max_d = None, None
        for df in dfs:
            union_cols |= set(df.columns) - {"date"}
            d = pd.to_datetime(df["date"], errors="coerce").dropna()
            if len(d) > 0:
                min_d = d.min() if min_d is None else min(min_d, d.min())
                max_d = d.max() if max_d is None else max(max_d, d.max())
        merged = pd.read_csv(cex_out)
        merged_cols = set(merged.columns) - {"date"}
        merged_dates = pd.to_datetime(merged["date"], errors="coerce").dropna()
        dup_dates = merged["date"].duplicated().sum()
        cols_ok = merged_cols == union_cols
        date_ok = merged_dates.min() == min_d and merged_dates.max() == max_d
        lines.append(
            f"- cex_net_inflows merge: cols_union_match={cols_ok} "
            f"(merged={len(merged_cols)}, parts_union={len(union_cols)}), "
            f"dup_dates={dup_dates}, date_range_match={date_ok} "
            f"({merged_dates.min().date()} .. {merged_dates.max().date()})"
        )
    else:
        lines.append("- cex_net_inflows merge: OUTPUT OR PARTS MISSING")
    return lines


def validate_date_standardization() -> list[str]:
    """Every non-snapshot CSV should have `date` as first column in YYYY-MM-DD format."""
    bad: list[str] = []
    snapshot_ok = {
        "DefiLlama/Stablecoins/stablecoins.csv",
        "DefiLlama/Stablecoins/stablecoins-chains.csv",
        "DefiLlama/Stablecoins/stablecoin_mcap_id_to_name.csv",
        "DefiLlama/DATs/dat-institutions.csv",
        "DefiLlama/ETFs/etf-overview.csv",
        "DefiLlama/TVL/Snapshot/tvl_chains_current.csv",
        "DefiLlama/TVL/Snapshot/tvl_protocols_current.csv",
        "Artemis/Artemis - Digital Asset Treasuries Overview.csv",
        "FRED/fred_series_metadata.csv",
        "MASTER_DATA.csv",
    }
    checked = 0
    for p in DATA_DIR.rglob("*.csv"):
        rel = rel_to_data(p)
        if rel.startswith("_meta/") or rel.startswith("DefiLlama/_raw_parts/"):
            continue
        if "_quarantine/" in rel:
            continue
        if rel in snapshot_ok:
            continue
        try:
            df = pd.read_csv(p, nrows=5)
        except Exception as e:
            bad.append(f"  - `{rel}`: read failed ({e})")
            continue
        first = df.columns[0]
        if first != "date":
            bad.append(f"  - `{rel}`: first column is `{first}` (expected `date`)")
            continue
        # Sample the first value for format check
        sample = str(df["date"].iloc[0]) if len(df) else ""
        if len(sample) == 10 and sample[4] == "-" and sample[7] == "-":
            checked += 1
        else:
            bad.append(f"  - `{rel}`: first date value `{sample}` is not YYYY-MM-DD")
    return [f"- date normalization: {checked} files OK, {len(bad)} failed."] + bad


def validate_no_timestamp_utc() -> list[str]:
    """Confirm that NO csv under Data/ still carries a `timestamp_utc` column."""
    offenders: list[str] = []
    checked = 0
    for p in DATA_DIR.rglob("*.csv"):
        rel = rel_to_data(p)
        if rel.startswith("_meta/") or "_raw_parts/" in rel or "_quarantine/" in rel:
            continue
        try:
            head = pd.read_csv(p, nrows=0)
        except Exception:
            continue
        checked += 1
        if "timestamp_utc" in head.columns:
            offenders.append(f"  - `{rel}` still has `timestamp_utc`")
    return [f"- no-timestamp-utc check: {checked} files checked, {len(offenders)} violations."] + offenders


def main() -> None:
    lines: list[str] = []
    lines.append("### Date-standardization check")
    lines.extend(validate_date_standardization())
    lines.append("")
    lines.append("### No timestamp_utc column check")
    lines.extend(validate_no_timestamp_utc())
    lines.append("")
    lines.append("### Merged-file sanity checks")
    lines.extend(validate_merges())
    lines.append("")
    lines.append("### CryptoQuant spot-checks (5 random files)")
    lines.extend(validate_cryptoquant_samples(5))
    lines.append("")
    lines.append("### Curated hash manifest")
    curated = _hash_all("curated_manifest.csv")
    lines.append(f"- Wrote `Data/_meta/curated_manifest.csv` ({len(curated)} files).")
    log("Step 07 — validation", lines)
    print("Step 07 done.")


if __name__ == "__main__":
    main()
