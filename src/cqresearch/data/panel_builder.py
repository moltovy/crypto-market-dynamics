"""Assemble the master daily panel.

All sources are reindexed onto the crypto-7 calendar
(:data:`cqresearch.data.calendars.DEFAULT_START` .. ``DEFAULT_END``) using the
right semantics (*stock* / *flow* / *rate*). The result is a dense DataFrame
with a ``DatetimeIndex`` named ``date`` and columns grouped by block.

This module is **deterministic**: every transformation is a pure function of
the CSVs on disk. No hidden state, no random sampling.
"""
from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path

import numpy as np
import pandas as pd

from cqresearch.data import loaders
from cqresearch.data.calendars import (
    DEFAULT_END,
    DEFAULT_START,
    align_to_master,
    crypto_index,
)


@dataclass
class PanelBuildReport:
    master_start: pd.Timestamp
    master_end: pd.Timestamp
    n_rows: int
    coverage_by_col: pd.DataFrame  # col, first, last, missing_pct


# --- kind assignments per variable ------------------------------------------
# 'stock' forward-fills weekends; 'flow' zero-fills weekends; 'rate' ffills.
KINDS: dict[str, str] = {
    # Prices (stock levels — carry across the weekend for equities/FX)
    "btc_close": "stock",
    "eth_close": "stock",
    "spy_close": "stock",
    "qqq_close": "stock",
    "gld_close": "stock",
    "xlk_close": "stock",
    "dxy_tv_close": "stock",
    "dvol_btc_close": "rate",       # implied-vol level
    "cme_btc_basis_close": "rate",  # basis spread
    "cme_eth_basis_close": "rate",
    # Volumes (flow)
    "btc_volume": "flow",
    "eth_volume": "flow",
    # Macro (rate)
    "DGS10": "rate", "DGS2": "rate", "DGS30": "rate", "DFII10": "rate",
    "T10Y2Y": "rate", "SOFR": "rate", "DFF": "rate",
    "BAMLH0A0HYM2": "rate", "VIXCLS": "rate", "RRPONTSYD": "rate",
    "DTWEXBGS": "rate", "DCOILWTICO": "stock", "USEPUINDXD": "rate",
    # DeFi (stock)
    "defi_tvl_usd": "stock",
    "stables_total_usd": "stock",
    # Sentiment (stock — the survey result persists across the day)
    "fng_value": "stock",
}

# ETF columns follow a naming convention we expand programmatically.
def _etf_flow_kind(col: str) -> str:
    return "flow"  # all Farside ETF columns are flows


def build_master_panel(
    start: pd.Timestamp | str = DEFAULT_START,
    end: pd.Timestamp | str = DEFAULT_END,
) -> tuple[pd.DataFrame, PanelBuildReport]:
    """Return ``(panel, report)`` where ``panel`` is the dense master frame."""

    master_idx = crypto_index(start, end)
    all_sources = loaders.load_all()

    aligned: dict[str, pd.Series] = {}

    def _add(col: str, series: pd.Series, kind: str) -> None:
        aligned[col] = align_to_master(series, kind=kind, master_index=master_idx)

    # Prices
    p = all_sources["btc_price"].df
    for c in ["btc_open", "btc_high", "btc_low", "btc_close", "btc_volume"]:
        if c in p.columns:
            _add(c, p[c], KINDS.get(c, "stock"))

    e = all_sources["eth_price"].df
    for c in ["eth_open", "eth_high", "eth_low", "eth_close", "eth_volume"]:
        if c in e.columns:
            _add(c, e[c], KINDS.get(c, "stock"))

    # Tradingview closes
    for key in ["spy", "qqq", "gld", "xlk", "dxy_tv", "dvol_btc", "cme_btc_basis", "cme_eth_basis"]:
        df = all_sources[key].df
        col = f"{key}_close"
        _add(col, df[col], KINDS.get(col, "stock"))

    # FRED
    fred = all_sources["fred_macro"].df
    for c in fred.columns:
        _add(c, fred[c], KINDS.get(c, "rate"))

    # DeFi stocks
    for key, col in [("tvl_all", "defi_tvl_usd"), ("stablecoin_total", "stables_total_usd")]:
        _add(col, all_sources[key].df[col], "stock")

    # Sentiment
    _add("fng_value", all_sources["fear_greed"].df["fng_value"], "stock")

    # ETF flows (wide): each column is one issuer; also includes "Total".
    for asset in ("btc", "eth"):
        etf = all_sources[f"farside_{asset}_etf"].df
        for c in etf.columns:
            _add(c, etf[c], _etf_flow_kind(c))

    panel = pd.DataFrame(aligned)
    panel.index.name = "date"

    # Coverage report
    rep_rows = []
    for c in panel.columns:
        s = panel[c]
        first = s.first_valid_index()
        last = s.last_valid_index()
        miss = float(s.isna().mean() * 100) if first is not None else 100.0
        rep_rows.append({
            "column": c,
            "first": first.date().isoformat() if first is not None else "",
            "last": last.date().isoformat() if last is not None else "",
            "missing_pct": round(miss, 2),
        })
    coverage = pd.DataFrame(rep_rows).sort_values("column").reset_index(drop=True)

    report = PanelBuildReport(
        master_start=master_idx.min(),
        master_end=master_idx.max(),
        n_rows=len(master_idx),
        coverage_by_col=coverage,
    )
    return panel, report


def write_panel(
    panel: pd.DataFrame,
    report: PanelBuildReport,
    out_dir: Path,
) -> tuple[Path, Path, Path]:
    out_dir.mkdir(parents=True, exist_ok=True)
    parquet = out_dir / "master_daily.parquet"
    panel.to_parquet(parquet)
    coverage = out_dir / "master_daily_coverage.csv"
    report.coverage_by_col.to_csv(coverage, index=False)
    meta = out_dir / "master_daily_meta.json"
    import json
    meta.write_text(
        json.dumps(
            {
                "start": report.master_start.date().isoformat(),
                "end": report.master_end.date().isoformat(),
                "n_rows": report.n_rows,
                "n_cols": int(panel.shape[1]),
                "columns": list(panel.columns),
            },
            indent=2,
        ),
        encoding="utf-8",
    )
    return parquet, coverage, meta


__all__ = ["build_master_panel", "write_panel", "PanelBuildReport"]
