"""Fetch FRED macro / rates / liquidity / sentiment series into Data/FRED/.

Reads FRED_API_KEY from the project .env (via python-dotenv) or the process env.

For each series in SERIES we:
1. Hit /fred/series/observations?series_id=... to pull the full history.
2. Hit /fred/series?series_id=...      to pull metadata (title, units, frequency, last_updated).
3. Write Data/FRED/<series_id>__<freq>.csv with columns [date, value].
4. FRED's '.' missing sentinel is converted to NaN (empty cell in the CSV).

At the end, we also build a combined wide panel of the DAILY series on a
business-day calendar (outer-join on date) -> Data/FRED/fred_macro_panel__daily.csv,
and regenerate Data/FRED/README.md with the full series list + last-updated stamps.

Usage:
    python tools/data_collection/fetch_fred.py

Re-run periodically; the script is idempotent (fully overwrites per-series CSVs).
"""
from __future__ import annotations

import io
import json
import os
import sys
import time
from datetime import datetime, timezone
from pathlib import Path

import pandas as pd
import requests
from dotenv import load_dotenv

ROOT = Path(__file__).resolve().parents[2]
DATA_FRED = ROOT / "Data" / "FRED"
API_ROOT = "https://api.stlouisfed.org/fred"

# -----------------------------------------------------------------------------
# Series list (19 series: your 9 + 10 extras chosen for a quant BTC/ETH panel).
# key      = FRED series id
# freq     = our file-naming tag (daily / weekly / monthly) — NOT the FRED native
#            frequency, which we pull from the API into the README.
# category = used in the README grouping.
# -----------------------------------------------------------------------------
SERIES: list[dict] = [
    # ---- Rates / curve ----
    {"id": "DGS10",        "freq": "daily",   "cat": "rates_curve",
     "note": "10-Year Treasury constant maturity, nominal."},
    {"id": "DGS2",         "freq": "daily",   "cat": "rates_curve",
     "note": "2-Year Treasury constant maturity, nominal."},
    {"id": "DGS30",        "freq": "daily",   "cat": "rates_curve",
     "note": "30-Year Treasury constant maturity, nominal."},
    {"id": "DFII10",       "freq": "daily",   "cat": "rates_curve",
     "note": "10-Year TIPS real yield (inflation-indexed)."},
    {"id": "T10Y2Y",       "freq": "daily",   "cat": "rates_curve",
     "note": "10-Year minus 2-Year Treasury spread (yield curve)."},
    {"id": "SOFR",         "freq": "daily",   "cat": "rates_curve",
     "note": "Secured Overnight Financing Rate."},
    {"id": "DFF",          "freq": "daily",   "cat": "rates_curve",
     "note": "Effective Federal Funds Rate (daily)."},
    # ---- Credit / risk / volatility ----
    {"id": "BAMLH0A0HYM2", "freq": "daily",   "cat": "credit_risk",
     "note": "ICE BofA US High Yield Option-Adjusted Spread."},
    {"id": "VIXCLS",       "freq": "daily",   "cat": "credit_risk",
     "note": "CBOE Volatility Index (VIX) close."},
    {"id": "NFCI",         "freq": "weekly",  "cat": "credit_risk",
     "note": "Chicago Fed National Financial Conditions Index (weekly)."},
    {"id": "ANFCI",        "freq": "weekly",  "cat": "credit_risk",
     "note": "Chicago Fed Adjusted National Financial Conditions Index."},
    {"id": "STLFSI4",      "freq": "weekly",  "cat": "credit_risk",
     "note": "St. Louis Fed Financial Stress Index (4th version, weekly)."},
    # ---- Fed balance sheet / liquidity ----
    {"id": "WALCL",        "freq": "weekly",  "cat": "fed_liquidity",
     "note": "Fed balance sheet total assets (H.4.1, weekly Wed)."},
    {"id": "RRPONTSYD",    "freq": "daily",   "cat": "fed_liquidity",
     "note": "Overnight Reverse Repurchase Agreements (ON RRP, daily)."},
    # ---- FX / commodities ----
    {"id": "DTWEXBGS",     "freq": "daily",   "cat": "fx_commodities",
     "note": "Nominal Broad US Dollar Index (daily)."},
    {"id": "DCOILWTICO",   "freq": "daily",   "cat": "fx_commodities",
     "note": "WTI spot crude oil (USD/bbl)."},
    # ---- Macro ----
    {"id": "CPIAUCSL",     "freq": "monthly", "cat": "macro",
     "note": "CPI All Urban Consumers, SA (monthly, index)."},
    {"id": "UNRATE",       "freq": "monthly", "cat": "macro",
     "note": "Civilian unemployment rate (monthly, %)."},
    {"id": "USEPUINDXD",   "freq": "daily",   "cat": "macro",
     "note": "Economic Policy Uncertainty Index (daily)."},
]


def _load_api_key() -> str:
    load_dotenv(ROOT / ".env")
    key = os.environ.get("FRED_API_KEY", "").strip()
    if not key:
        print(
            "ERROR: FRED_API_KEY is not set.\n"
            f"  Add it to {ROOT / '.env'} like:\n"
            "      FRED_API_KEY=your_fred_api_key_here\n"
            "  or export it in your shell, then re-run this script.",
            file=sys.stderr,
        )
        sys.exit(2)
    return key


def _get(session: requests.Session, path: str, params: dict) -> dict:
    params = dict(params)
    params["file_type"] = "json"
    url = f"{API_ROOT}/{path}"
    for attempt in range(5):
        try:
            r = session.get(url, params=params, timeout=30)
            if r.status_code == 200:
                return r.json()
            # FRED returns 429 Too Many Requests — back off.
            if r.status_code == 429:
                time.sleep(2 * (attempt + 1))
                continue
            # 400 with bad series id, surface clearly.
            raise RuntimeError(f"FRED {path} {params.get('series_id')} -> HTTP {r.status_code}: {r.text[:200]}")
        except requests.RequestException as e:
            if attempt == 4:
                raise
            time.sleep(1 + attempt)
    raise RuntimeError("unreachable")


def _fetch_series(session: requests.Session, api_key: str, sid: str) -> pd.DataFrame:
    data = _get(session, "series/observations",
                {"series_id": sid, "api_key": api_key, "observation_start": "1900-01-01"})
    obs = data.get("observations", [])
    if not obs:
        return pd.DataFrame(columns=["date", "value"])
    df = pd.DataFrame(obs)[["date", "value"]]
    # FRED uses '.' for missing. Convert to NaN.
    df["value"] = pd.to_numeric(df["value"].replace(".", pd.NA), errors="coerce")
    df["date"] = pd.to_datetime(df["date"], errors="coerce").dt.strftime("%Y-%m-%d")
    df = df.dropna(subset=["date"]).sort_values("date").drop_duplicates(subset=["date"])
    return df[["date", "value"]].reset_index(drop=True)


def _fetch_meta(session: requests.Session, api_key: str, sid: str) -> dict:
    data = _get(session, "series", {"series_id": sid, "api_key": api_key})
    series = data.get("seriess", [{}])[0]
    return {
        "id": sid,
        "title": series.get("title", ""),
        "units": series.get("units_short", series.get("units", "")),
        "frequency": series.get("frequency", ""),
        "seasonal_adjustment": series.get("seasonal_adjustment_short", ""),
        "observation_start": series.get("observation_start", ""),
        "observation_end": series.get("observation_end", ""),
        "last_updated": series.get("last_updated", ""),
        "notes": (series.get("notes") or "").strip().replace("\n", " ")[:500],
    }


def _write_csv(df: pd.DataFrame, path: Path) -> None:
    buf = io.StringIO()
    df.to_csv(buf, index=False, lineterminator="\n")
    path.write_bytes(buf.getvalue().encode("utf-8"))


def _build_readme(results: list[dict], panel_rows: int, panel_start: str, panel_end: str) -> str:
    now = datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M:%SZ")
    lines = [
        "# FRED",
        "",
        "**Source**: Federal Reserve Economic Data — https://fred.stlouisfed.org/  ",
        "**API**: https://api.stlouisfed.org/fred/  ",
        "**Fetcher**: `tools/data_collection/fetch_fred.py` (re-runnable)  ",
        "",
        "US macro, rates, liquidity, FX, commodities, and risk-sentiment series used as "
        "exogenous / macro controls in the BTC vs. ETH factor-evolution analysis.",
        "",
        "## Date convention",
        "",
        "Every file's first column is `date` (ISO `YYYY-MM-DD`, FRED's publication calendar, ",
        "ascending). Value column is `value` as a float; FRED's `.` missing sentinel is kept as an empty cell.",
        "",
        "## Units and frequency",
        "",
        "`frequency` below is FRED's native frequency (what they publish); the filename `__daily/__weekly/__monthly` ",
        "suffix is our convenience tag.",
        "",
        "| Series | Title | Units | FRED freq | Obs. range | Last updated | Rows | File |",
        "| --- | --- | --- | --- | --- | --- | ---: | --- |",
    ]
    for r in results:
        m = r["meta"]
        lines.append(
            f"| `{m['id']}` | {m['title']} | {m['units']} | {m['frequency']} | "
            f"{m['observation_start']} .. {m['observation_end']} | {m['last_updated']} | "
            f"{r['rows']:,} | `{r['file']}` |"
        )
    lines += [
        "",
        "## Category grouping (for factor-block mapping)",
        "",
        "| Category | Series |",
        "| --- | --- |",
    ]
    by_cat: dict[str, list[str]] = {}
    for r in results:
        by_cat.setdefault(r["cat"], []).append(r["meta"]["id"])
    cat_names = {
        "rates_curve": "Rates & yield curve",
        "credit_risk": "Credit spreads / financial conditions / vol",
        "fed_liquidity": "Fed balance sheet / liquidity",
        "fx_commodities": "FX & commodities",
        "macro": "Macro (inflation, labor, policy uncertainty)",
    }
    for cat, ids in by_cat.items():
        lines.append(f"| {cat_names.get(cat, cat)} | {', '.join(f'`{x}`' for x in ids)} |")
    lines += [
        "",
        "## Combined daily panel",
        "",
        f"`fred_macro_panel__daily.csv` — outer-joined wide panel of all DAILY series on a business-day ",
        f"calendar from `{panel_start}` to `{panel_end}` ({panel_rows:,} rows, forward-filling is left to the consumer).",
        "",
        "## Sample rows",
        "",
    ]
    for r in results[:3]:
        lines.append(f"**`{r['file']}`**")
        lines.append("")
        lines.append("```csv")
        lines.append(r["sample"])
        lines.append("```")
        lines.append("")
    lines.append("---")
    lines.append(f"_Auto-generated on {now} by `tools/data_collection/fetch_fred.py`._")
    return "\n".join(lines) + "\n"


def main() -> None:
    api_key = _load_api_key()
    DATA_FRED.mkdir(parents=True, exist_ok=True)
    session = requests.Session()

    results: list[dict] = []
    meta_rows: list[dict] = []
    daily_frames: list[pd.DataFrame] = []
    for spec in SERIES:
        sid = spec["id"]
        freq_tag = spec["freq"]
        print(f"  fetching {sid} ({freq_tag}) ...")
        try:
            df = _fetch_series(session, api_key, sid)
            meta = _fetch_meta(session, api_key, sid)
        except Exception as e:
            print(f"    ! failed: {e}", file=sys.stderr)
            continue
        fname = f"{sid}__{freq_tag}.csv"
        out = DATA_FRED / fname
        _write_csv(df, out)
        sample = df.head(2).to_csv(index=False, lineterminator="\n").strip()
        results.append({
            "cat": spec["cat"],
            "file": fname,
            "rows": len(df),
            "meta": meta,
            "sample": sample,
        })
        meta_rows.append({**meta, "category": spec["cat"], "freq_tag": freq_tag, "file": fname,
                          "project_note": spec["note"]})
        if freq_tag == "daily":
            renamed = df.rename(columns={"value": sid})
            daily_frames.append(renamed)

    # Metadata sidecar (so downstream scripts / README authors never have to re-hit FRED).
    with (DATA_FRED / "fred_series_metadata.csv").open("w", encoding="utf-8", newline="") as f:
        df_meta = pd.DataFrame(meta_rows)
        if not df_meta.empty:
            df_meta.to_csv(f, index=False, lineterminator="\n")

    # Combined wide daily panel on business-day calendar.
    panel_rows = 0
    panel_start = panel_end = "—"
    if daily_frames:
        panel = daily_frames[0]
        for nxt in daily_frames[1:]:
            panel = panel.merge(nxt, on="date", how="outer")
        panel = panel.sort_values("date")
        # Reindex onto business-day calendar between min and max observed dates.
        if not panel.empty:
            dmin = pd.to_datetime(panel["date"]).min()
            dmax = pd.to_datetime(panel["date"]).max()
            bdays = pd.bdate_range(dmin, dmax).strftime("%Y-%m-%d")
            panel = panel.set_index("date").reindex(bdays).rename_axis("date").reset_index()
            panel_rows = len(panel)
            panel_start = panel["date"].iloc[0]
            panel_end = panel["date"].iloc[-1]
        _write_csv(panel, DATA_FRED / "fred_macro_panel__daily.csv")

    (DATA_FRED / "README.md").write_text(
        _build_readme(results, panel_rows, panel_start, panel_end), encoding="utf-8"
    )

    # Dump a compact status json for downstream scripts.
    status = {
        "fetched_at_utc": datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"),
        "series_count": len(results),
        "panel_rows": panel_rows,
    }
    (DATA_FRED / "_fetch_status.json").write_text(json.dumps(status, indent=2), encoding="utf-8")
    print(f"FRED done: {len(results)} series, panel rows = {panel_rows}.")


if __name__ == "__main__":
    main()
