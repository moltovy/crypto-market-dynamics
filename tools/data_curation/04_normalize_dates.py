"""Step 04: Normalize the date column across every time-series CSV under Data/.

Universal contract after this script runs:
- First column is `date` (ISO `YYYY-MM-DD`, UTC calendar).
- Rows sorted ascending on `date`, deduplicated on `date` (for wide panels).
- **No `timestamp_utc` column anywhere** — all data is collapsed to daily granularity.
- UTF-8, LF line endings, no BOM.
- All other columns are preserved verbatim.

Per-source rules:
- CryptoQuant (Data/CryptoQuant/**):   `Datetime` -> `date` (drop any `timestamp_utc`).
- Artemis (Data/Artemis/*.csv):        quoted `"DateTime"` -> `date`.
- Farside (Data/Farside ETF Data/**):  `Date` -> `date`.
- FRED (Data/FRED/*.csv):              `date` already normalized by fetcher — idempotent touch.
- AlternativeMe (Data/AlternativeMe/*.csv):  `date` already normalized by fetcher — idempotent touch.
- DefiLlama website exports (Data/DefiLlama/{Stablecoins,ETFs,RWA,ChainMetrics,CEX,DATs}/):
    * `date` stays as-is.
    * `day` (etf-history) -> `date`.
    * `Date` + `Timestamp` (rwa-time-series-chart-*) -> drop `Timestamp`, `Date` -> `date`.
- DefiLlama generated TVL panels (Data/DefiLlama/TVL/**):   `Date` -> `date`.
- Tradingview (Data/Tradingview/{Daily,Weekly}/*): `time` (Unix sec) -> `date` (drop any `timestamp_utc`).
- Snapshot files (no date column, e.g. stablecoins.csv, dat-institutions.csv,
  tvl_chains_current.csv, tvl_protocols_current.csv): LEFT UNTOUCHED.
"""
from __future__ import annotations

import io
import sys
from pathlib import Path

import pandas as pd

sys.path.insert(0, str(Path(__file__).resolve().parent))
from _common import DATA_DIR, log, rel_to_data  # noqa: E402


# Files that are snapshots / entity lists with no date axis — skip normalization.
SNAPSHOT_FILES = {
    "DefiLlama/Stablecoins/stablecoins.csv",
    "DefiLlama/Stablecoins/stablecoins-chains.csv",
    "DefiLlama/Stablecoins/stablecoin_mcap_id_to_name.csv",
    "DefiLlama/DATs/dat-institutions.csv",
    "DefiLlama/ETFs/etf-overview.csv",
    "DefiLlama/TVL/Snapshot/tvl_chains_current.csv",
    "DefiLlama/TVL/Snapshot/tvl_protocols_current.csv",
    "Artemis/Artemis - Digital Asset Treasuries Overview.csv",
}


def _find_col(df: "pd.DataFrame", candidates: tuple[str, ...]) -> str | None:
    lower_map = {c.lower(): c for c in df.columns}
    for cand in candidates:
        if cand.lower() in lower_map:
            return lower_map[cand.lower()]
    return None


def _write_csv(df: pd.DataFrame, path: Path) -> None:
    """Write UTF-8, LF line endings, no BOM."""
    buf = io.StringIO()
    df.to_csv(buf, index=False, lineterminator="\n")
    path.write_bytes(buf.getvalue().encode("utf-8"))


def _to_iso_date(series: pd.Series) -> pd.Series:
    dt = pd.to_datetime(series, utc=True, errors="coerce")
    return dt.dt.strftime("%Y-%m-%d")


def _normalize_cryptoquant(path: Path) -> tuple[bool, str]:
    df = pd.read_csv(path)
    cols = list(df.columns)
    # Idempotent path: already has `date`, maybe also leftover `timestamp_utc`.
    if "date" in cols:
        if "timestamp_utc" in cols:
            df = df.drop(columns=["timestamp_utc"])
        df["date"] = _to_iso_date(df["date"])
        df = df.dropna(subset=["date"]).sort_values("date").drop_duplicates(subset=["date"])
        other = [c for c in df.columns if c != "date"]
        df = df[["date"] + other]
        _write_csv(df, path)
        return True, "CryptoQuant: idempotent normalize"
    col = _find_col(df, ("Datetime", "datetime"))
    if col is None:
        return False, f"no `Datetime` column, skipped"
    df["date"] = _to_iso_date(df[col])
    df = df.drop(columns=[col])
    df = df.dropna(subset=["date"]).sort_values("date").drop_duplicates(subset=["date"])
    other = [c for c in df.columns if c != "date"]
    df = df[["date"] + other]
    _write_csv(df, path)
    return True, f"CryptoQuant: {len(df):,} rows, {df['date'].min()}..{df['date'].max()}"


def _normalize_artemis(path: Path) -> tuple[bool, str]:
    df = pd.read_csv(path)
    first = df.columns[0]
    if first.lower() not in ("datetime", "date"):
        return False, f"first column is `{first}`, skipped"
    df = df.rename(columns={first: "date"})
    df["date"] = _to_iso_date(df["date"])
    df = df.dropna(subset=["date"]).sort_values("date").drop_duplicates(subset=["date"])
    _write_csv(df, path)
    return True, f"Artemis: {len(df):,} rows, {df['date'].min()}..{df['date'].max()}"


def _normalize_farside(path: Path) -> tuple[bool, str]:
    df = pd.read_csv(path)
    first = df.columns[0]
    if first.lower() != "date":
        return False, f"first column is `{first}`, skipped"
    df = df.rename(columns={first: "date"})
    df["date"] = _to_iso_date(df["date"])
    df = df.dropna(subset=["date"]).sort_values("date").drop_duplicates(subset=["date"])
    _write_csv(df, path)
    return True, f"Farside: {len(df):,} rows, {df['date'].min()}..{df['date'].max()}"


def _normalize_defi_generic(path: Path) -> tuple[bool, str]:
    df = pd.read_csv(path)
    cols = list(df.columns)
    long_format = False
    if "Timestamp" in cols and "Date" in cols:
        df = df.drop(columns=["Timestamp"]).rename(columns={"Date": "date"})
    else:
        col = _find_col(df, ("date", "Date", "day", "Day", "DateTime", "datetime"))
        if col is None:
            return False, f"no recognized date column, skipped"
        if col != "date":
            df = df.rename(columns={col: "date"})
        # If date is NOT the first column, this is a long-format file
        # (e.g. etf-history.csv: gecko_id,day,total_flow_usd) — preserve row shape.
        if cols[0] != col and cols[0].lower() != col.lower():
            long_format = True
    df["date"] = _to_iso_date(df["date"])
    df = df.dropna(subset=["date"]).sort_values("date")
    if not long_format:
        df = df.drop_duplicates(subset=["date"])
    # Put date first
    other = [c for c in df.columns if c != "date"]
    df = df[["date"] + other]
    _write_csv(df, path)
    return True, f"Defi: {len(df):,} rows, {df['date'].min()}..{df['date'].max()}"


def _normalize_defillama(path: Path) -> tuple[bool, str]:
    df = pd.read_csv(path)
    first = df.columns[0]
    if first.lower() != "date":
        return False, f"first column is `{first}`, skipped"
    if first != "date":
        df = df.rename(columns={first: "date"})
    df["date"] = _to_iso_date(df["date"])
    df = df.dropna(subset=["date"]).sort_values("date")
    # Long-format files may have duplicate dates across chains — do NOT dedupe.
    _write_csv(df, path)
    return True, f"DefiLlama: {len(df):,} rows, {df['date'].min()}..{df['date'].max()}"


def _normalize_tradingview(path: Path) -> tuple[bool, str]:
    df = pd.read_csv(path)
    cols = list(df.columns)
    # Idempotent: drop `timestamp_utc` if present, normalize `date`.
    if "date" in cols:
        if "timestamp_utc" in cols:
            df = df.drop(columns=["timestamp_utc"])
        df["date"] = _to_iso_date(df["date"])
        df = df.dropna(subset=["date"]).sort_values("date").drop_duplicates(subset=["date"])
        other = [c for c in df.columns if c != "date"]
        df = df[["date"] + other]
        _write_csv(df, path)
        return True, "TradingView: idempotent normalize"
    if "time" not in cols:
        return False, f"no `time` column, skipped"
    ts = pd.to_datetime(df["time"], unit="s", utc=True, errors="coerce")
    df["date"] = ts.dt.strftime("%Y-%m-%d")
    df = df.drop(columns=["time"])
    df = df.dropna(subset=["date"]).sort_values("date").drop_duplicates(subset=["date"])
    other = [c for c in df.columns if c != "date"]
    df = df[["date"] + other]
    _write_csv(df, path)
    return True, f"TradingView: {len(df):,} rows, {df['date'].min()}..{df['date'].max()}"


def _normalize_simple(path: Path) -> tuple[bool, str]:
    """FRED / AlternativeMe / any source whose first column is already `date`."""
    df = pd.read_csv(path)
    first = df.columns[0]
    if first.lower() != "date":
        return False, f"first column is `{first}`, skipped"
    if first != "date":
        df = df.rename(columns={first: "date"})
    df["date"] = _to_iso_date(df["date"])
    df = df.dropna(subset=["date"]).sort_values("date").drop_duplicates(subset=["date"])
    _write_csv(df, path)
    return True, f"simple: {len(df):,} rows, {df['date'].min()}..{df['date'].max()}"


def classify(path: Path) -> str:
    rel = rel_to_data(path)
    if rel in SNAPSHOT_FILES:
        return "snapshot"
    if rel.startswith("CryptoQuant/") and rel.endswith(".csv"):
        return "cryptoquant"
    if rel.startswith("Artemis/") and rel.endswith(".csv"):
        return "artemis"
    if rel.startswith("Farside ETF Data/") and rel.endswith(".csv"):
        return "farside"
    if rel.startswith("DefiLlama/") and rel.endswith(".csv"):
        # Exclude raw-parts archives from normalization (preserve originals).
        if rel.startswith("DefiLlama/_raw_parts/"):
            return "snapshot"
        # TVL panels (generated by harvest_defillama_simple.py) vs website-export subfolders.
        if rel.startswith("DefiLlama/TVL/"):
            return "defillama"
        return "defi"
    if rel.startswith("Tradingview/") and rel.endswith(".csv"):
        # Skip quarantined files.
        if "_quarantine/" in rel:
            return "snapshot"
        return "tradingview"
    if rel.startswith("FRED/") and rel.endswith(".csv"):
        # `fred_series_metadata.csv` and `fred_daily_panel.csv` both pass — their first col is `date` or `series_id`.
        # Only normalize time-series-style files.
        if rel.endswith("_metadata.csv"):
            return "snapshot"
        return "simple"
    if rel.startswith("AlternativeMe/") and rel.endswith(".csv"):
        return "simple"
    return "skip"


NORMALIZERS = {
    "cryptoquant": _normalize_cryptoquant,
    "artemis": _normalize_artemis,
    "farside": _normalize_farside,
    "defi": _normalize_defi_generic,
    "defillama": _normalize_defillama,
    "tradingview": _normalize_tradingview,
    "simple": _normalize_simple,
}


def main() -> None:
    counts: dict[str, int] = {k: 0 for k in list(NORMALIZERS.keys()) + ["skip", "snapshot", "fail"]}
    failures: list[str] = []
    dropped_ts = 0  # count of CSVs where we removed a stray `timestamp_utc` column

    for path in sorted(DATA_DIR.rglob("*.csv")):
        kind = classify(path)
        if kind in ("skip", "snapshot"):
            counts[kind] += 1
            continue
        fn = NORMALIZERS[kind]
        try:
            ok, msg = fn(path)
            if ok:
                counts[kind] += 1
            else:
                counts["fail"] += 1
                failures.append(f"- `{rel_to_data(path)}` ({kind}): {msg}")
        except Exception as e:
            counts["fail"] += 1
            failures.append(f"- `{rel_to_data(path)}` ({kind}): EXCEPTION {type(e).__name__}: {e}")

    # Belt-and-suspenders sweep: drop any lingering `timestamp_utc` column from EVERY csv under Data/.
    # The per-source normalizers above already handle this, but this catches snapshots or odd files.
    for path in sorted(DATA_DIR.rglob("*.csv")):
        rel = rel_to_data(path)
        if "_quarantine/" in rel or "_raw_parts/" in rel:
            continue
        try:
            df = pd.read_csv(path, nrows=1)
        except Exception:
            continue
        if "timestamp_utc" not in df.columns:
            continue
        try:
            df_full = pd.read_csv(path).drop(columns=["timestamp_utc"])
            _write_csv(df_full, path)
            dropped_ts += 1
        except Exception as e:
            failures.append(f"- `{rel}` (sweep): could not drop timestamp_utc: {type(e).__name__}: {e}")

    lines = [
        "Per-source counts:",
        *[f"- **{k}**: {v}" for k, v in counts.items() if v],
        f"- **timestamp_utc columns dropped in sweep**: {dropped_ts}",
    ]
    if failures:
        lines.append("")
        lines.append("**Failures / skipped non-snapshot files:**")
        lines.extend(failures)
    log("Step 04 — normalize dates", lines)
    print("Step 04 done.", counts)
    if failures:
        print(f"  {len(failures)} failures (see curation_log.md)")


if __name__ == "__main__":
    main()
