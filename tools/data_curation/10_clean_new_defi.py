"""Step 10: Clean the newly-added files under Data/DefiLlama/ChainMetrics/ and Data/DefiLlama/RWA/.

Combines:
1. **SHA-256 dedupe** across all of `Data/DefiLlama/` (excluding `_raw_parts/`).
   Byte-identical duplicates are quarantined under `_raw_parts/duplicates/`.

2. **Hard-coded duplicate groups** where files are NOT byte-identical but are
   clearly the same underlying series with different export options (user re-
   downloaded with different checkboxes). The canonical winner is chosen by
   column count (more = more complete) with a size tie-breaker. Losers go to
   `_raw_parts/duplicates/`.

3. **Rename map** for cryptic or broken filenames (`[object Object]`, `platfrom`
   typo, export-date suffix), producing canonical `snake_case__daily.csv` names.

Idempotent: re-runs are no-ops after the first successful pass.
"""
from __future__ import annotations

import shutil
import sys
from collections import defaultdict
from pathlib import Path

import pandas as pd

sys.path.insert(0, str(Path(__file__).resolve().parent))
from _common import DATA_DIR, log, rel_to_data, sha256_of_file  # noqa: E402

DEFI_ROOT = DATA_DIR / "DefiLlama"
DUP_ARCHIVE = DEFI_ROOT / "_raw_parts" / "duplicates"


# -----------------------------------------------------------------------------
# Near-duplicate groups that are NOT byte-identical.
# We pick the winner by (1) most columns, (2) largest size.
# -----------------------------------------------------------------------------
NEAR_DUP_GROUPS: list[list[Path]] = [
    [
        DEFI_ROOT / "ChainMetrics" / "all_metrics_2026-04-17.csv",
        DEFI_ROOT / "ChainMetrics" / "all_metrics_2026-04-17 (1) volume.csv",
    ],
    [
        DEFI_ROOT / "ChainMetrics" / "ethereum_metrics_2026-04-17 (1).csv",
        DEFI_ROOT / "ChainMetrics" / "ethereum_metrics_2026-04-17 Fees and revenue.csv",
        DEFI_ROOT / "ChainMetrics" / "ethereum_metrics_2026-04-17 volume.csv",
    ],
    [
        DEFI_ROOT / "RWA" / "rwa-time-series-chart-active-mcap-all-2026-04-17.csv",
        DEFI_ROOT / "RWA" / "rwa-time-series-chart-active-mcap-all-2026-04-14.csv",
    ],
    [
        DEFI_ROOT / "RWA" / "rwa-time-series-chart-onchain-mcap-all-2026-04-17.csv",
        DEFI_ROOT / "RWA" / "rwa-time-series-chart-onchain-mcap-all-2026-04-14.csv",
    ],
]

# -----------------------------------------------------------------------------
# Rename map applied AFTER dedupe. Keys are basenames; values are final
# basenames. Subfolder is preserved.
# -----------------------------------------------------------------------------
RENAME_MAP: dict[str, str] = {
    # ChainMetrics
    "all_metrics_2026-04-17.csv":                 "all_chains_metrics__daily.csv",
    "ethereum_metrics_2026-04-17 (1).csv":        "ethereum_metrics__daily.csv",
    "ethereum_metrics_2026-04-17 volume.csv":     "ethereum_metrics__daily.csv",
    "ethereum_metrics_2026-04-17 Fees and revenue.csv":
                                                  "ethereum_metrics__daily.csv",
    "solana_metrics_2026-04-17.csv":              "solana_metrics__daily.csv",
    "chain-revenue-chart_combined.[object Object]_2026-04-17.csv":
                                                  "chain_revenue_combined__daily.csv",
    "chains-dominance-2026-04-17.csv":            "chain_tvl_dominance__daily.csv",
    "all dex metrics.csv":                        "all_dex_metrics__daily.csv",
    "all-chains-perp-volume-by-protocol-bar-absolute-stacked-daily-2026-04-17.csv":
                                                  "all_chains_perp_volume_by_protocol__daily.csv",
    # RWA
    "rwa-time-series-chart-active-mcap-all-2026-04-17.csv":
                                                  "rwa_active_mcap_all__daily.csv",
    "rwa-time-series-chart-onchain-mcap-all-2026-04-17.csv":
                                                  "rwa_onchain_mcap_all__daily.csv",
    "rwa-time-series-chart-onchain-mcap-all-2026-04-17 platfrom breakdown.csv":
                                                  "rwa_onchain_mcap_by_platform__daily.csv",
    "rwa-time-series-chart-defi-active-tvl-all-2026-04-14.csv":
                                                  "rwa_defi_active_tvl_all__daily.csv",
    "rwa-category-chart_combined_2026-04-17.csv": "rwa_mcap_by_category__daily.csv",
}


def _score_file(p: Path) -> tuple[int, int]:
    """Score for near-dup selection: (col_count, size_bytes). Higher wins."""
    try:
        df = pd.read_csv(p, nrows=1)
        return (len(df.columns), p.stat().st_size)
    except Exception:
        return (0, p.stat().st_size if p.exists() else 0)


def _quarantine(p: Path) -> Path:
    DUP_ARCHIVE.mkdir(parents=True, exist_ok=True)
    dest = DUP_ARCHIVE / p.name
    counter = 1
    while dest.exists():
        dest = DUP_ARCHIVE / f"{p.stem}__{counter}{p.suffix}"
        counter += 1
    shutil.move(str(p), str(dest))
    return dest


def _sha_dedupe(files: list[Path]) -> list[str]:
    """Archive byte-identical duplicates, keep the first one."""
    lines: list[str] = []
    by_hash: dict[str, list[Path]] = defaultdict(list)
    for p in files:
        if not p.is_file():
            continue
        by_hash[sha256_of_file(p)].append(p)
    for digest, group in by_hash.items():
        if len(group) < 2:
            continue
        # Prefer the one WITHOUT `(1)` / `(2)` in the name.
        group_sorted = sorted(group, key=lambda x: ("(1)" in x.name or "(2)" in x.name, len(x.name)))
        keeper = group_sorted[0]
        lines.append(f"- byte-identical group `{digest[:12]}`: kept `{rel_to_data(keeper)}`.")
        for loser in group_sorted[1:]:
            dest = _quarantine(loser)
            lines.append(f"  - archived `{rel_to_data(loser)}` -> `{rel_to_data(dest)}`.")
    return lines


def _near_dup_resolve() -> list[str]:
    lines: list[str] = []
    for group in NEAR_DUP_GROUPS:
        present = [p for p in group if p.is_file()]
        if len(present) < 2:
            continue
        scored = sorted(present, key=_score_file, reverse=True)
        winner = scored[0]
        lines.append(
            f"- near-dup group: winner `{rel_to_data(winner)}` "
            f"(cols={_score_file(winner)[0]}, size={winner.stat().st_size:,})"
        )
        for loser in scored[1:]:
            dest = _quarantine(loser)
            lines.append(
                f"  - archived `{rel_to_data(loser)}` "
                f"(cols={_score_file(Path(dest))[0] if dest.exists() else '?'}) -> `{rel_to_data(dest)}`."
            )
    return lines


def _apply_renames() -> list[str]:
    """Rename files by EXACT basename match.

    We avoid `rglob(src_name)` because basenames with `[` / `]` are interpreted
    as glob character classes. Instead we walk every csv under DEFI_ROOT and
    match by basename equality.
    """
    lines: list[str] = []
    all_csvs = [
        p for p in DEFI_ROOT.rglob("*.csv")
        if "_raw_parts" not in str(p)
    ]
    by_name: dict[str, list[Path]] = defaultdict(list)
    for p in all_csvs:
        by_name[p.name].append(p)

    for src_name, dst_name in RENAME_MAP.items():
        matches = by_name.get(src_name, [])
        for src in matches:
            dst = src.parent / dst_name
            if dst.is_file():
                if src.name != dst.name and src.is_file():
                    _quarantine(src)
                    lines.append(f"- target `{rel_to_data(dst)}` already existed; archived stray `{src.name}`.")
                continue
            src.rename(dst)
            lines.append(f"- renamed `{rel_to_data(src)}` -> `{rel_to_data(dst)}`.")
    return lines


def main() -> None:
    if not DEFI_ROOT.is_dir():
        print(f"DefiLlama dir not found: {DEFI_ROOT}")
        return

    all_lines: list[str] = []

    # 1. Near-dup groups first (so SHA pass sees only survivors).
    nd_lines = _near_dup_resolve()
    if nd_lines:
        all_lines.append("### Near-duplicate resolution")
        all_lines.extend(nd_lines)

    # 2. Global SHA-256 dedupe over whole DefiLlama/ (excluding _raw_parts).
    csvs = [
        p for p in DEFI_ROOT.rglob("*.csv")
        if "_raw_parts" not in str(p)
    ]
    sha_lines = _sha_dedupe(csvs)
    if sha_lines:
        all_lines.append("")
        all_lines.append("### SHA-256 byte-identical dedupe")
        all_lines.extend(sha_lines)

    # 3. Renames.
    rn_lines = _apply_renames()
    if rn_lines:
        all_lines.append("")
        all_lines.append("### Renames")
        all_lines.extend(rn_lines)

    if not all_lines:
        all_lines.append("No changes (all new DefiLlama files already canonical).")

    log("Step 10 — clean new DefiLlama files", all_lines)
    print(f"Step 10 done: {len(all_lines)} log lines.")


if __name__ == "__main__":
    main()
