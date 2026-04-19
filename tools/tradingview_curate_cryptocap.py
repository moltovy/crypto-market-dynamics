"""
One-off helper: convert TradingView CRYPTOCAP root exports (time = unix sec) to
Daily/Weekly CSVs with date column and standard Tradingview column layout.
"""
from __future__ import annotations

import csv
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1] / "Data" / "Tradingview"

# Must match existing Tradingview files (split matches csv.reader on disk).
STANDARD_COLUMNS = [
    "date",
    "open",
    "high",
    "low",
    "close",
    "Volume",
    "Open Interest",
    "Open Interest (Open)",
    "Open Interest (High",
    "Open Interest (Low)",
    "Open Interest (Close)",
]


def unix_to_date_str(ts: str) -> str:
    sec = int(float(ts.strip()))
    dt = datetime.fromtimestamp(sec, tz=timezone.utc)
    return dt.strftime("%Y-%m-%d")


def convert_ohlc_time_csv(src: Path, dest: Path) -> int:
    with src.open(newline="", encoding="utf-8") as f:
        reader = csv.reader(f)
        header = next(reader)
        if header[0].strip().lower() != "time":
            raise ValueError(f"{src}: expected first column 'time', got {header[0]!r}")
        idx = {name.strip().lower(): i for i, name in enumerate(header)}
        for col in ("open", "high", "low", "close"):
            if col not in idx:
                raise ValueError(f"{src}: missing column {col!r}")

        rows: list[tuple[str, str, str, str, str]] = []
        for row in reader:
            if not row or not row[0].strip():
                continue
            d = unix_to_date_str(row[0])
            o = row[idx["open"]]
            h = row[idx["high"]]
            lo = row[idx["low"]]
            c = row[idx["close"]]
            rows.append((d, o, h, lo, c))

    dest.parent.mkdir(parents=True, exist_ok=True)
    with dest.open("w", newline="", encoding="utf-8") as f:
        w = csv.writer(f)
        w.writerow(STANDARD_COLUMNS)
        for d, o, h, lo, c in rows:
            w.writerow([d, o, h, lo, c, "", "", "", "", ""])

    return len(rows)


def main() -> None:
    jobs = [
        (
            ROOT / "CRYPTOCAP_BTC.D, 1D_6cbb5.csv",
            ROOT / "Daily" / "CRYPTOCAP_BTC_dominance__daily.csv",
        ),
        (
            ROOT / "CRYPTOCAP_ETH.D, 1D_16c8e.csv",
            ROOT / "Daily" / "CRYPTOCAP_ETH_dominance__daily.csv",
        ),
        (
            ROOT / "CRYPTOCAP_TOTAL3, 1D_fb655.csv",
            ROOT / "Daily" / "CRYPTOCAP_TOTAL3__daily.csv",
        ),
        (
            ROOT / "CRYPTOCAP_BTC.D, 1W_bf0e1.csv",
            ROOT / "Weekly" / "CRYPTOCAP_BTC_dominance__weekly.csv",
        ),
        (
            ROOT / "CRYPTOCAP_ETH.D, 1W_73ab7.csv",
            ROOT / "Weekly" / "CRYPTOCAP_ETH_dominance__weekly.csv",
        ),
        (
            ROOT / "CRYPTOCAP_TOTAL3, 1W_72843.csv",
            ROOT / "Weekly" / "CRYPTOCAP_TOTAL3__weekly.csv",
        ),
    ]
    for src, dest in jobs:
        if not src.exists():
            raise FileNotFoundError(src)
        n = convert_ohlc_time_csv(src, dest)
        print(f"Wrote {n} rows -> {dest.relative_to(ROOT)}")


if __name__ == "__main__":
    main()
