"""One-shot inventory of the CSVs the panel will consume.

Writes a markdown run summary so downstream agents know exactly which files
were inspected, their shapes, date ranges, and columns.
"""
from __future__ import annotations

import json
from datetime import datetime
from pathlib import Path

import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
DATA = ROOT / "Data"
OUT = ROOT / "reports" / "run_summaries" / "01_inspect_core_files.md"

TARGETS: dict[str, str] = {
    # Prices (dependent variables)
    "btc_price": "CryptoQuant/BTC/Market Data/Bitcoin Price & Volume - Spot, All Exchanges, BTC-USD - Day.csv",
    "eth_price": "CryptoQuant/ETH/Market Data/Ethereum Price & Volume - Spot, All Exchanges, ETH-USD - Day.csv",

    # Macro block
    "fred_macro": "FRED/fred_macro_panel__daily.csv",

    # TradFi comparables
    "spy": "Tradingview/Daily/SPY_sp500_etf__daily.csv",
    "qqq": "Tradingview/Daily/QQQ_nasdaq100_etf__daily.csv",
    "gld": "Tradingview/Daily/GLD_gold_etf__daily.csv",
    "dxy_tv": "Tradingview/Daily/DXY_us_dollar_index__daily.csv",
    "dvol_btc": "Tradingview/Daily/Deribit_BTC_volatility_index_DVOL__daily.csv",
    "cme_btc_basis": "Tradingview/Daily/CME_BTC_futures_minus_SPOT_BTC_basis__daily.csv",
    "cme_eth_basis": "Tradingview/Daily/CME_ETH_futures_minus_SPOT_ETH_basis__daily.csv",

    # Institutional flows
    "farside_btc_etf": "Farside ETF Data/farside_btc_etf_flows__daily.csv",
    "farside_eth_etf": "Farside ETF Data/farside_eth_etf_flows__daily.csv",

    # Liquidity / DeFi
    "tvl_all": "DefiLlama/TVL/Daily/tvl_all_chains_daily.csv",
    "stablecoin_mcap": "DefiLlama/Stablecoins/stablecoin_mcap_by_defillama_id__daily.csv",

    # Fear & Greed sentiment
    "fear_greed": "AlternativeMe/fear_greed_index__daily.csv",
}


def profile(path: Path) -> dict:
    df = pd.read_csv(path)
    # Locate date column
    date_col = None
    for c in df.columns:
        if c.lower() in {"date", "datetime", "day", "timestamp"}:
            date_col = c
            break
    info: dict = {
        "rows": int(df.shape[0]),
        "cols": int(df.shape[1]),
        "columns": [str(c) for c in df.columns],
        "date_col": date_col,
    }
    if date_col is not None:
        try:
            d = pd.to_datetime(df[date_col], errors="coerce")
            info["first_date"] = str(d.min().date()) if d.notna().any() else None
            info["last_date"] = str(d.max().date()) if d.notna().any() else None
            info["n_valid_dates"] = int(d.notna().sum())
        except Exception as exc:  # pragma: no cover - defensive
            info["date_parse_error"] = str(exc)
    num = df.select_dtypes("number")
    if len(num.columns):
        info["numeric_cols"] = list(num.columns)
        info["missing_pct_top"] = {
            c: round(float(num[c].isna().mean() * 100), 2)
            for c in num.columns[:10]
        }
    return info


def main() -> None:
    OUT.parent.mkdir(parents=True, exist_ok=True)
    out: dict[str, dict] = {}
    missing: list[str] = []
    for key, rel in TARGETS.items():
        p = DATA / rel
        if not p.exists():
            missing.append(f"{key} -> {rel}")
            continue
        try:
            out[key] = {"path": rel, **profile(p)}
        except Exception as exc:
            out[key] = {"path": rel, "error": str(exc)}

    lines: list[str] = []
    lines.append(f"# Core file inspection — {datetime.utcnow().strftime('%Y-%m-%d %H:%M UTC')}\n")
    lines.append("Scope: files the master panel consumes for the v0.1 analyses.\n")
    if missing:
        lines.append("## Missing files\n")
        for m in missing:
            lines.append(f"- {m}")
        lines.append("")

    lines.append("## Profile summary\n")
    lines.append("| key | path | rows | cols | first | last | date_col |")
    lines.append("| --- | --- | ---: | ---: | --- | --- | --- |")
    for k, info in out.items():
        lines.append(
            f"| `{k}` | `Data/{info['path']}` | {info.get('rows','?')} | {info.get('cols','?')} | "
            f"{info.get('first_date','')} | {info.get('last_date','')} | {info.get('date_col','')} |"
        )

    lines.append("\n## Columns per file\n")
    for k, info in out.items():
        lines.append(f"### `{k}` — `Data/{info['path']}`")
        lines.append("")
        cols = info.get("columns", [])
        lines.append("Columns: " + ", ".join(f"`{c}`" for c in cols))
        if "missing_pct_top" in info:
            lines.append("")
            lines.append("Missing % (first 10 numeric cols):")
            for c, pct in info["missing_pct_top"].items():
                lines.append(f"- `{c}`: {pct}%")
        lines.append("")

    OUT.write_text("\n".join(lines), encoding="utf-8")
    print(f"wrote {OUT}")
    # Also dump JSON next to the markdown for machine consumption
    (OUT.with_suffix(".json")).write_text(json.dumps(out, indent=2), encoding="utf-8")


if __name__ == "__main__":
    main()
