"""Step 05: Rename the 12 cryptic TradingView exports to descriptive names.

Mapping per plan. Idempotent: if the target name already exists, do nothing.
"""
from __future__ import annotations

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from _common import DATA_DIR, log, rel_to_data  # noqa: E402


TV_DIR = DATA_DIR / "Tradingview"

# source_name -> new_name
RENAMES = {
    "BATS_ETHA_INDEX_ETHUSD, 1D_2f598.csv":       "tradingview__ETHA_ETF_over_SPOT_ETH__daily.csv",
    "BATS_IBIT_INDEX_BTCUSD, 1D_82cbc.csv":       "tradingview__IBIT_ETF_over_SPOT_BTC__daily.csv",
    "CME_DL_BTC1!, 1D_f2832.csv":                 "tradingview__CME_BTC_front_month_futures__daily.csv",
    "CME_DL_BTC1!-INDEX_BTCUSD, 1D_bab18.csv":    "tradingview__CME_BTC_futures_minus_SPOT_BTC_basis__daily.csv",
    "CME_DL_BTC1!_INDEX_BTCUSD, 1D_35ff1.csv":    "tradingview__CME_BTC_futures_over_SPOT_BTC_ratio__daily.csv",
    "CME_DL_ETH1!, 1D_d7e37.csv":                 "tradingview__CME_ETH_front_month_futures__daily.csv",
    "CME_DL_ETH1!-INDEX_ETHUSD, 1D_94468.csv":    "tradingview__CME_ETH_futures_minus_SPOT_ETH_basis__daily.csv",
    "CME_DL_ETH1!_INDEX_ETHUSD, 1D_26513.csv":    "tradingview__CME_ETH_futures_over_SPOT_ETH_ratio__daily.csv",
    "CME_DL_MBT1!, 1D_98b41.csv":                 "tradingview__CME_Micro_Bitcoin_futures__daily.csv",
    "CME_DL_MET1!, 1D_85ee4.csv":                 "tradingview__CME_Micro_Ether_futures__daily.csv",
    "CME_DL_SOL1!, 1D_e1c21.csv":                 "tradingview__CME_Solana_futures__daily.csv",
    "DERIBIT_DVOL, 1D_75dd9.csv":                 "tradingview__Deribit_BTC_volatility_index_DVOL__daily.csv",
}


def main() -> None:
    lines: list[str] = []
    renamed = 0
    skipped = 0
    for old, new in RENAMES.items():
        src = TV_DIR / old
        dst = TV_DIR / new
        if not src.exists() and dst.exists():
            lines.append(f"- already renamed: `{rel_to_data(dst)}`")
            skipped += 1
            continue
        if not src.exists():
            lines.append(f"- MISSING source: `Tradingview/{old}`")
            continue
        if dst.exists():
            lines.append(f"- SKIP (dst exists): `Tradingview/{old}` -> `Tradingview/{new}`")
            continue
        src.rename(dst)
        renamed += 1
        lines.append(f"- `Tradingview/{old}` -> `Tradingview/{new}`")

    log("Step 05 — rename TradingView", lines)
    print(f"Step 05 done: {renamed} renamed, {skipped} already renamed.")


if __name__ == "__main__":
    main()
