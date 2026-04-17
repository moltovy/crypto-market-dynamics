"""Step 09: Reorganize Data/Tradingview/.

- Renames every TradingView CSV to our convention `<TICKER>_<desc>__<freq>.csv`.
- Splits files into `Daily/` and `Weekly/` subfolders.
- Dedupes the two pairs of TVC_DXY exports (keeps the better one, moves the
  duplicate to `Data/_quarantine/tradingview_duplicates/`).
- For files that still have the raw TradingView `time` (Unix seconds) column,
  parses it to ISO `date` and drops `time`.
- Drops the `timestamp_utc` column introduced by earlier curation passes
  (per the "no timestamps in curated files" rule).
- Preserves all OHLC / volume / indicator columns verbatim.

Idempotent: running the script a second time is a no-op.
"""
from __future__ import annotations

import io
import shutil
import sys
from pathlib import Path

import pandas as pd

sys.path.insert(0, str(Path(__file__).resolve().parent))
from _common import DATA_DIR, log, rel_to_data, sha256_of_file  # noqa: E402

TV_DIR = DATA_DIR / "Tradingview"
DAILY_DIR = TV_DIR / "Daily"
WEEKLY_DIR = TV_DIR / "Weekly"
QUARANTINE_DIR = DATA_DIR / "_quarantine" / "tradingview_duplicates"


# -----------------------------------------------------------------------------
# Rename map.
# Keys are CURRENT file basenames (may be in Tradingview/ root OR already in
# Daily/ or Weekly/ from a previous run). Values are the target basename
# (without subfolder — the freq suffix determines that).
# -----------------------------------------------------------------------------
RENAME_MAP: dict[str, str] = {
    # --- Existing curated files (drop the `tradingview__` prefix) ---
    "tradingview__CME_BTC_front_month_futures__daily.csv":
        "CME_BTC_front_month_futures__daily.csv",
    "tradingview__CME_BTC_futures_minus_SPOT_BTC_basis__daily.csv":
        "CME_BTC_futures_minus_SPOT_BTC_basis__daily.csv",
    "tradingview__CME_BTC_futures_over_SPOT_BTC_ratio__daily.csv":
        "CME_BTC_futures_over_SPOT_BTC_ratio__daily.csv",
    "tradingview__CME_ETH_front_month_futures__daily.csv":
        "CME_ETH_front_month_futures__daily.csv",
    "tradingview__CME_ETH_futures_minus_SPOT_ETH_basis__daily.csv":
        "CME_ETH_futures_minus_SPOT_ETH_basis__daily.csv",
    "tradingview__CME_ETH_futures_over_SPOT_ETH_ratio__daily.csv":
        "CME_ETH_futures_over_SPOT_ETH_ratio__daily.csv",
    "tradingview__CME_Micro_Bitcoin_futures__daily.csv":
        "CME_Micro_Bitcoin_futures__daily.csv",
    "tradingview__CME_Micro_Ether_futures__daily.csv":
        "CME_Micro_Ether_futures__daily.csv",
    "tradingview__CME_Solana_futures__daily.csv":
        "CME_Solana_futures__daily.csv",
    "tradingview__Deribit_BTC_volatility_index_DVOL__daily.csv":
        "Deribit_BTC_volatility_index_DVOL__daily.csv",
    "tradingview__ETHA_ETF_over_SPOT_ETH__daily.csv":
        "ETHA_ETF_over_SPOT_ETH__daily.csv",
    "tradingview__IBIT_ETF_over_SPOT_BTC__daily.csv":
        "IBIT_ETF_over_SPOT_BTC__daily.csv",
    # --- New CME weekly continuous futures ---
    "CME_DL_BTC1!, 1W_6395d.csv":  "CME_BTC1_continuous_futures__weekly.csv",
    "CME_DL_ETH1!, 1W_69670.csv":  "CME_ETH1_continuous_futures__weekly.csv",
    "CME_DL_MBT1!, 1W_22da0.csv":  "CME_Micro_Bitcoin_MBT1_continuous__weekly.csv",
    "CME_DL_MET1!, 1W_566c8.csv":  "CME_Micro_Ether_MET1_continuous__weekly.csv",
    # --- BATS daily (stocks + ETFs) ---
    "BATS_ARKK, 1D_5ac9c.csv": "ARKK_innovation_etf__daily.csv",
    "BATS_COIN, 1D_4dc12.csv": "COIN_coinbase_stock__daily.csv",
    "BATS_CRCL, 1D_dfc61.csv": "CRCL_circle_stock__daily.csv",
    "BATS_GLD, 1D_424f4.csv":  "GLD_gold_etf__daily.csv",
    "BATS_IWM, 1D_7b248.csv":  "IWM_russell2000_etf__daily.csv",
    "BATS_MARA, 1D_404d6.csv": "MARA_marathon_miner_stock__daily.csv",
    "BATS_MSTR, 1D_c7fbe.csv": "MSTR_microstrategy_stock__daily.csv",
    "BATS_QQQ, 1D_8372e.csv":  "QQQ_nasdaq100_etf__daily.csv",
    "BATS_RIOT, 1D_bf328.csv": "RIOT_riot_miner_stock__daily.csv",
    "BATS_SMH, 1D_7eb28.csv":  "SMH_vaneck_semiconductor_etf__daily.csv",
    "BATS_SOXX, 1D_9233e.csv": "SOXX_ishares_semiconductor_etf__daily.csv",
    "BATS_SPY, 1D_b62b8.csv":  "SPY_sp500_etf__daily.csv",
    "BATS_XLK, 1D_7d51a.csv":  "XLK_tech_sector_etf__daily.csv",
    # --- BATS weekly ---
    "BATS_COIN, 1W_b988a.csv": "COIN_coinbase_stock__weekly.csv",
    "BATS_MSTR, 1W_34c00.csv": "MSTR_microstrategy_stock__weekly.csv",
    "BATS_QQQ, 1W_06346.csv":  "QQQ_nasdaq100_etf__weekly.csv",
    "BATS_RIOT, 1W_ecfda.csv": "RIOT_riot_miner_stock__weekly.csv",
    "BATS_SPY, 1W_08055.csv":  "SPY_sp500_etf__weekly.csv",
    # --- OANDA gold spot ---
    "OANDA_XAUUSD, 1D_5955d.csv": "XAUUSD_gold_spot__daily.csv",
    "OANDA_XAUUSD, 1W_e338a.csv": "XAUUSD_gold_spot__weekly.csv",
}

# TVC_DXY has duplicate exports we must dedupe by content / date range.
DXY_DAILY_CANDIDATES = ["TVC_DXY, 1D_4f17d.csv", "TVC_DXY, 1D_b5047.csv"]
DXY_WEEKLY_CANDIDATES = ["TVC_DXY, 1W_5f115.csv", "TVC_DXY, 1W_def5e.csv"]
DXY_DAILY_TARGET = "DXY_us_dollar_index__daily.csv"
DXY_WEEKLY_TARGET = "DXY_us_dollar_index__weekly.csv"


def _target_dir(dst_name: str) -> Path:
    if dst_name.endswith("__weekly.csv"):
        return WEEKLY_DIR
    return DAILY_DIR


def _locate_source(name: str) -> Path | None:
    """The rename map key may already have been moved on a previous run."""
    for candidate in (TV_DIR / name, DAILY_DIR / name, WEEKLY_DIR / name):
        if candidate.is_file():
            return candidate
    return None


def _write_csv(df: pd.DataFrame, path: Path) -> None:
    buf = io.StringIO()
    df.to_csv(buf, index=False, lineterminator="\n")
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_bytes(buf.getvalue().encode("utf-8"))


def _normalize_tv_df(df: pd.DataFrame) -> pd.DataFrame:
    """Unified normalization:

    - If `time` exists (fresh TradingView export), convert Unix-seconds -> ISO date.
    - If `date` + `timestamp_utc` already exist (earlier curated), drop timestamp_utc.
    - If only `date` exists, coerce to ISO.
    - Drop duplicate dates, sort ascending, put `date` first.
    """
    cols = list(df.columns)
    if "time" in cols:
        ts = pd.to_datetime(df["time"], unit="s", utc=True, errors="coerce")
        df = df.drop(columns=["time"])
        df["date"] = ts.dt.strftime("%Y-%m-%d")
    elif "date" in cols:
        df["date"] = pd.to_datetime(df["date"], utc=True, errors="coerce").dt.strftime("%Y-%m-%d")
    else:
        raise ValueError(f"Neither `time` nor `date` column present. Columns: {cols}")
    if "timestamp_utc" in df.columns:
        df = df.drop(columns=["timestamp_utc"])
    df = df.dropna(subset=["date"]).drop_duplicates(subset=["date"]).sort_values("date")
    other = [c for c in df.columns if c != "date"]
    return df[["date"] + other].reset_index(drop=True)


def _process_file(src: Path, dst: Path) -> str:
    df = pd.read_csv(src)
    df = _normalize_tv_df(df)
    _write_csv(df, dst)
    if src.resolve() != dst.resolve():
        src.unlink()
    return f"`{rel_to_data(src)}` -> `{rel_to_data(dst)}` ({len(df):,} rows)"


def _dedupe_pair(candidates: list[str], target_basename: str) -> list[str]:
    """Decide the winner between two candidate files and quarantine the other."""
    lines: list[str] = []
    present = [(TV_DIR / c) for c in candidates if (TV_DIR / c).is_file()]
    # Also consider a previous winner already living at the target.
    target_dir = _target_dir(target_basename)
    existing_target = target_dir / target_basename
    if existing_target.is_file():
        # Target already exists from a previous run; make sure all stragglers are quarantined.
        for p in present:
            _quarantine(p)
            lines.append(f"already have `{rel_to_data(existing_target)}`, quarantined stray `{rel_to_data(p)}`")
        return lines
    if not present:
        return [f"no candidates found for `{target_basename}`"]
    if len(present) == 1:
        # Single candidate, just rename it.
        dst = target_dir / target_basename
        lines.append(_process_file(present[0], dst))
        return lines

    # Choose the winner.
    hashes = {p: sha256_of_file(p) for p in present}
    unique_hashes = set(hashes.values())
    if len(unique_hashes) == 1:
        # Byte-identical duplicates — keep the first one.
        winner = present[0]
        losers = present[1:]
        lines.append(f"byte-identical duplicates: {', '.join(p.name for p in present)}")
    else:
        # Pick the one with the longer date span.
        metrics: list[tuple[Path, int, int]] = []
        for p in present:
            try:
                df = pd.read_csv(p, usecols=["time"]) if "time" in pd.read_csv(p, nrows=1).columns else pd.read_csv(p, usecols=["date"])
                if "time" in df.columns:
                    ts = pd.to_datetime(df["time"], unit="s", utc=True, errors="coerce").dropna()
                else:
                    ts = pd.to_datetime(df["date"], utc=True, errors="coerce").dropna()
                span = int((ts.max() - ts.min()).days) if len(ts) else 0
                metrics.append((p, len(ts), span))
            except Exception:
                metrics.append((p, 0, 0))
        metrics.sort(key=lambda x: (x[1], x[2], x[0].stat().st_size), reverse=True)
        winner = metrics[0][0]
        losers = [m[0] for m in metrics[1:]]
        lines.append(
            "differing bytes; picked widest date span: "
            + ", ".join(f"{p.name} rows={r} span_d={s}" for p, r, s in metrics)
        )
    dst = target_dir / target_basename
    lines.append(_process_file(winner, dst))
    for loser in losers:
        _quarantine(loser)
        lines.append(f"quarantined duplicate `{rel_to_data(loser)}`")
    return lines


def _quarantine(p: Path) -> None:
    QUARANTINE_DIR.mkdir(parents=True, exist_ok=True)
    dest = QUARANTINE_DIR / p.name
    counter = 1
    while dest.exists():
        dest = QUARANTINE_DIR / f"{p.stem}__{counter}{p.suffix}"
        counter += 1
    shutil.move(str(p), str(dest))


def main() -> None:
    TV_DIR.mkdir(parents=True, exist_ok=True)
    DAILY_DIR.mkdir(parents=True, exist_ok=True)
    WEEKLY_DIR.mkdir(parents=True, exist_ok=True)

    lines: list[str] = []
    moved = 0
    skipped = 0

    # 1. Straight renames.
    for src_name, dst_name in sorted(RENAME_MAP.items()):
        src = _locate_source(src_name)
        if src is None:
            # Maybe already at destination.
            dst_path = _target_dir(dst_name) / dst_name
            if dst_path.is_file():
                skipped += 1
                continue
            lines.append(f"  MISSING: `{src_name}` — not at root, not at target.")
            continue
        dst = _target_dir(dst_name) / dst_name
        try:
            lines.append(_process_file(src, dst))
            moved += 1
        except Exception as e:
            lines.append(f"  ERROR on `{src_name}`: {type(e).__name__}: {e}")

    # 2. DXY dedupe pairs.
    lines.append("")
    lines.append("**TVC_DXY daily pair**")
    for ln in _dedupe_pair(DXY_DAILY_CANDIDATES, DXY_DAILY_TARGET):
        lines.append(f"  - {ln}")
    lines.append("")
    lines.append("**TVC_DXY weekly pair**")
    for ln in _dedupe_pair(DXY_WEEKLY_CANDIDATES, DXY_WEEKLY_TARGET):
        lines.append(f"  - {ln}")

    # 3. Sanity: no stray CSVs left at TV_DIR root.
    strays = [p for p in TV_DIR.glob("*.csv") if p.is_file()]
    if strays:
        lines.append("")
        lines.append("**Unhandled files still at `Tradingview/` root (action needed):**")
        for p in strays:
            lines.append(f"  - `{rel_to_data(p)}` ({p.stat().st_size:,} bytes)")

    log("Step 09 — reorganize Tradingview", lines)
    print(f"Step 09 done: {moved} moved/renamed, {skipped} already in place, {len(strays)} strays.")


if __name__ == "__main__":
    main()
