"""Step 03: Merge DefiLlama multi-part exports into canonical CSVs.

Two groups, per plan:
1. stablecoin-mcap-chart_combined_2026-04-17*.csv  (base + part 1..4 + (1) part 5..7)
   -> Data/Defi/stablecoin_mcap_by_defillama_id__daily.csv
   Parts have DIFFERENT stablecoin-id columns for the SAME dates.
   We outer-join on date. Columns are numeric DefiLlama IDs; we also emit an
   id-to-name lookup by joining against Data/Defi/stablecoins.csv.
2. cex-inflows-chart_combined_2026-04-17 part 1..3.csv
   -> Data/Defi/cex_net_inflows_by_exchange__daily.csv
   Parts have DIFFERENT exchange-slug columns for the SAME dates.

Parts are archived to Data/Defi/_raw_parts/stablecoin_mcap/ and
Data/Defi/_raw_parts/cex_inflows/ respectively.
"""
from __future__ import annotations

import json
import shutil
import sys
from pathlib import Path

import pandas as pd

sys.path.insert(0, str(Path(__file__).resolve().parent))
from _common import DATA_DIR, log, rel_to_data  # noqa: E402

DEFI_DIR = DATA_DIR / "Defi"
ARCHIVE_ROOT = DEFI_DIR / "_raw_parts"


def _read_part(path: Path) -> pd.DataFrame:
    df = pd.read_csv(path)
    if df.columns[0].lower() != "date":
        df = df.rename(columns={df.columns[0]: "date"})
    df["date"] = pd.to_datetime(df["date"], utc=True, errors="coerce").dt.strftime(
        "%Y-%m-%d"
    )
    df = df.dropna(subset=["date"]).drop_duplicates(subset=["date"])
    return df


def _merge_parts(paths: list[Path]) -> tuple[pd.DataFrame, list[str]]:
    """Outer-join on date. Later parts DON'T overwrite earlier parts unless the
    earlier part had a missing value.

    Returns (merged, report_lines).
    """
    lines: list[str] = []
    merged: pd.DataFrame | None = None
    for p in paths:
        df = _read_part(p)
        n_cols = len(df.columns) - 1
        lines.append(
            f"  - `{rel_to_data(p)}` -> {len(df):>5} rows x {n_cols:>3} data columns, "
            f"{df['date'].min()} .. {df['date'].max()}"
        )
        if merged is None:
            merged = df
            continue
        overlap = [c for c in df.columns if c != "date" and c in merged.columns]
        if overlap:
            lines.append(f"    overlap columns (will coalesce): {overlap[:5]}{'...' if len(overlap) > 5 else ''}")
        merged = pd.merge(merged, df, on="date", how="outer", suffixes=("", "__dup"))
        for c in list(merged.columns):
            if c.endswith("__dup"):
                base = c[:-5]
                # Prefer non-null of original; fall back to duplicate.
                merged[base] = merged[base].combine_first(merged[c])
                merged = merged.drop(columns=[c])
    assert merged is not None
    merged = merged.sort_values("date").reset_index(drop=True)
    return merged, lines


def _archive_parts(paths: list[Path], subdir: str) -> list[str]:
    dest_dir = ARCHIVE_ROOT / subdir
    dest_dir.mkdir(parents=True, exist_ok=True)
    out: list[str] = []
    for p in paths:
        dest = dest_dir / p.name
        if dest.exists():
            dest.unlink()
        shutil.move(str(p), str(dest))
        out.append(f"  - archived `{rel_to_data(p)}` -> `{rel_to_data(dest)}`")
    return out


def merge_stablecoin_mcap() -> list[str]:
    pattern_files = sorted(DEFI_DIR.glob("stablecoin-mcap-chart_combined_2026-04-17*.csv"))
    if not pattern_files:
        return ["- stablecoin-mcap parts: none found."]
    lines = ["### stablecoin-mcap merge", "", "Parts scanned:"]
    merged, part_lines = _merge_parts(pattern_files)
    lines.extend(part_lines)

    out_path = DEFI_DIR / "stablecoin_mcap_by_defillama_id__daily.csv"
    merged.to_csv(out_path, index=False)
    lines.append("")
    lines.append(
        f"Merged output: `{rel_to_data(out_path)}` ({len(merged):,} rows x "
        f"{len(merged.columns) - 1:,} id columns; {merged['date'].min()} .. {merged['date'].max()})."
    )

    # Build ID -> name lookup using stablecoins.csv.
    id_lookup_path = DEFI_DIR / "stablecoin_mcap_id_to_name.csv"
    stable_meta = DEFI_DIR / "stablecoins.csv"
    id_cols = [c for c in merged.columns if c != "date"]
    if stable_meta.exists():
        try:
            meta = pd.read_csv(stable_meta)
            # DefiLlama /stablecoins endpoint has no explicit id column exported.
            # The stablecoin id system is positional in most UI exports; we map by
            # row order fallback AND by matching numeric ids if present.
            lookup = pd.DataFrame({"defillama_id": id_cols})
            if "id" in meta.columns:
                lookup = lookup.merge(
                    meta[["id", "name", "symbol", "pegType"]].rename(columns={"id": "defillama_id"}),
                    on="defillama_id",
                    how="left",
                )
            else:
                lookup["name"] = None
                lookup["symbol"] = None
                lookup["pegType"] = None
            lookup.to_csv(id_lookup_path, index=False)
            unresolved = lookup[lookup["name"].isna()]
            lines.append(
                f"ID-to-name lookup written: `{rel_to_data(id_lookup_path)}` "
                f"({len(lookup)} ids; {len(unresolved)} unresolved)."
            )
        except Exception as e:  # pragma: no cover
            lines.append(f"ID-to-name lookup FAILED: {e!r}")
    else:
        lines.append(f"`{rel_to_data(stable_meta)}` not found; skipped id-to-name lookup.")

    lines.append("")
    lines.append("Archiving parts:")
    lines.extend(_archive_parts(pattern_files, "stablecoin_mcap"))
    return lines


def merge_cex_inflows() -> list[str]:
    pattern_files = sorted(DEFI_DIR.glob("cex-inflows-chart_combined_2026-04-17*.csv"))
    if not pattern_files:
        return ["- cex-inflows parts: none found."]
    lines = ["### cex-inflows merge", "", "Parts scanned:"]
    merged, part_lines = _merge_parts(pattern_files)
    lines.extend(part_lines)

    out_path = DEFI_DIR / "cex_net_inflows_by_exchange__daily.csv"
    merged.to_csv(out_path, index=False)
    lines.append("")
    lines.append(
        f"Merged output: `{rel_to_data(out_path)}` ({len(merged):,} rows x "
        f"{len(merged.columns) - 1:,} exchange columns; {merged['date'].min()} .. {merged['date'].max()})."
    )
    lines.append("")
    lines.append("Archiving parts:")
    lines.extend(_archive_parts(pattern_files, "cex_inflows"))
    return lines


def main() -> None:
    lines = []
    lines.extend(merge_stablecoin_mcap())
    lines.append("")
    lines.extend(merge_cex_inflows())
    log("Step 03 — merge Defi multi-part exports", lines)
    print("Step 03 done.")


if __name__ == "__main__":
    main()
