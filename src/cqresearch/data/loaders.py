"""Typed CSV loaders — one per data source family.

Conventions every loader enforces:

* Output is indexed by a UTC-normalized daily ``DatetimeIndex`` named ``date``.
* Numeric columns are ``float64``. Non-positive prices / negative volumes are
  treated as missing (data-quality rule — never convert to zero).
* Duplicates on the date index are collapsed to the *last* row (latest vintage).
* Loaders never forward-fill; that decision is made by
  :func:`cqresearch.data.calendars.align_to_master` given the series' kind.
"""
from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Iterable

import numpy as np
import pandas as pd

from config.paths import DATA_DIR
from cqresearch.data.calendars import to_daily_utc


@dataclass(frozen=True)
class LoadResult:
    name: str
    path: Path
    df: pd.DataFrame
    first: pd.Timestamp
    last: pd.Timestamp
    n_rows: int
    n_missing_rows: int  # rows where *all* numeric values are NaN

    def summary(self) -> dict:
        return {
            "name": self.name,
            "path": str(self.path.relative_to(DATA_DIR.parent)),
            "first": self.first.date().isoformat(),
            "last": self.last.date().isoformat(),
            "n_rows": self.n_rows,
            "n_missing_rows": self.n_missing_rows,
            "n_cols": int(self.df.shape[1]),
        }


def _canonical(df: pd.DataFrame, date_col: str) -> pd.DataFrame:
    df = df.copy()
    df[date_col] = to_daily_utc(df[date_col])
    df = df.dropna(subset=[date_col]).set_index(date_col)
    df.index.name = "date"
    df = df[~df.index.duplicated(keep="last")].sort_index()
    return df


def _finalize(df: pd.DataFrame, name: str, path: Path) -> LoadResult:
    num = df.select_dtypes("number")
    all_nan = num.isna().all(axis=1) if num.shape[1] else pd.Series(False, index=df.index)
    return LoadResult(
        name=name,
        path=path,
        df=df,
        first=df.index.min(),
        last=df.index.max(),
        n_rows=len(df),
        n_missing_rows=int(all_nan.sum()),
    )


# ---------------------------------------------------------------------------
# Price / market data  (CryptoQuant exports)
# ---------------------------------------------------------------------------
def load_btc_price() -> LoadResult:
    path = DATA_DIR / "CryptoQuant/BTC/Market Data/Bitcoin Price & Volume - Spot, All Exchanges, BTC-USD - Day.csv"
    df = pd.read_csv(path)
    df = _canonical(df, "date")
    df = df.rename(columns={c: f"btc_{c.lower()}" for c in df.columns})
    # Treat non-positive prices as missing (source has pre-2010 placeholder zeros)
    for c in ["btc_open", "btc_high", "btc_low", "btc_close"]:
        if c in df.columns:
            df[c] = df[c].where(df[c] > 0, np.nan)
    return _finalize(df, "btc_price", path)


def load_eth_price() -> LoadResult:
    path = DATA_DIR / "CryptoQuant/ETH/Market Data/Ethereum Price & Volume - Spot, All Exchanges, ETH-USD - Day.csv"
    df = pd.read_csv(path)
    df = _canonical(df, "date")
    df = df.rename(columns={c: f"eth_{c.lower()}" for c in df.columns})
    for c in ["eth_open", "eth_high", "eth_low", "eth_close"]:
        if c in df.columns:
            df[c] = df[c].where(df[c] > 0, np.nan)
    return _finalize(df, "eth_price", path)


def load_btc_mcap() -> LoadResult:
    """USD market capitalization (full dollars, not millions)."""

    path = DATA_DIR / "CryptoQuant/BTC/Market Data/Bitcoin Market Cap - Day.csv"
    df = pd.read_csv(path)
    df = _canonical(df, "date")
    df = df.rename(columns={"Market Cap": "btc_mcap_usd"})
    df["btc_mcap_usd"] = pd.to_numeric(df["btc_mcap_usd"], errors="coerce")
    df["btc_mcap_usd"] = df["btc_mcap_usd"].where(df["btc_mcap_usd"] > 0, np.nan)
    return _finalize(df[["btc_mcap_usd"]], "btc_mcap", path)


def load_eth_mcap() -> LoadResult:
    path = DATA_DIR / "CryptoQuant/ETH/Market Data/Ethereum Market Cap - Day.csv"
    df = pd.read_csv(path)
    df = _canonical(df, "date")
    df = df.rename(columns={"Market Cap": "eth_mcap_usd"})
    df["eth_mcap_usd"] = pd.to_numeric(df["eth_mcap_usd"], errors="coerce")
    df["eth_mcap_usd"] = df["eth_mcap_usd"].where(df["eth_mcap_usd"] > 0, np.nan)
    return _finalize(df[["eth_mcap_usd"]], "eth_mcap", path)


def load_btc_exchange_netflow() -> LoadResult:
    path = (
        DATA_DIR
        / "CryptoQuant/BTC/Exchange Flows/Bitcoin Exchange Netflow (Total) - All Exchanges - Day.csv"
    )
    df = pd.read_csv(path)
    df = _canonical(df, "date")
    df = df.rename(columns={"Exchange Netflow (Total)": "btc_exchange_netflow"})
    df["btc_exchange_netflow"] = pd.to_numeric(df["btc_exchange_netflow"], errors="coerce")
    return _finalize(df[["btc_exchange_netflow"]], "btc_exchange_netflow", path)


def load_btc_miner_to_exchange() -> LoadResult:
    path = (
        DATA_DIR
        / "CryptoQuant/BTC/Miner Flows/Bitcoin Miner to Exchange Flow (Total) - All Miners, All Exchanges - Day.csv"
    )
    df = pd.read_csv(path)
    df = _canonical(df, "date")
    df = df.rename(
        columns={"Miner to Exchange Flow (Total)": "btc_miner_to_exchange_flow"}
    )
    df["btc_miner_to_exchange_flow"] = pd.to_numeric(df["btc_miner_to_exchange_flow"], errors="coerce")
    return _finalize(df[["btc_miner_to_exchange_flow"]], "btc_miner_to_exchange", path)


def load_btc_mvrv() -> LoadResult:
    path = DATA_DIR / "CryptoQuant/BTC/Market Indicator/Bitcoin MVRV Ratio - Day.csv"
    df = pd.read_csv(path)
    df = _canonical(df, "date")
    df = df.rename(columns={"MVRV Ratio": "btc_mvrv"})
    df["btc_mvrv"] = pd.to_numeric(df["btc_mvrv"], errors="coerce")
    return _finalize(df[["btc_mvrv"]], "btc_mvrv", path)


# ---------------------------------------------------------------------------
# Macro (FRED panel)
# ---------------------------------------------------------------------------
def load_fred() -> LoadResult:
    path = DATA_DIR / "FRED/fred_macro_panel__daily.csv"
    df = pd.read_csv(path)
    df = _canonical(df, "date")
    return _finalize(df, "fred_macro", path)


# ---------------------------------------------------------------------------
# Tradingview daily OHLC family  (equities, DXY, DVOL, CME basis, etc.)
# ---------------------------------------------------------------------------
TV_DIR = DATA_DIR / "Tradingview" / "Daily"


def load_tv_close(name: str, prefix: str) -> LoadResult:
    """Load a Tradingview daily CSV and keep only the close as ``{prefix}_close``.

    Parameters
    ----------
    name
        Filename under ``Data/Tradingview/Daily``.
    prefix
        Column prefix (e.g. ``spy``, ``dxy_tv``, ``dvol_btc``).
    """

    path = TV_DIR / name
    df = pd.read_csv(path)
    df = _canonical(df, "date")
    close_col = next((c for c in df.columns if c.lower() == "close"), None)
    if close_col is None:
        raise KeyError(f"No close column in {path}")
    out = df[[close_col]].rename(columns={close_col: f"{prefix}_close"})
    out[f"{prefix}_close"] = pd.to_numeric(out[f"{prefix}_close"], errors="coerce")
    out[f"{prefix}_close"] = out[f"{prefix}_close"].where(out[f"{prefix}_close"] > 0, np.nan)
    return _finalize(out, prefix, path)


# ---------------------------------------------------------------------------
# Farside ETF flows
# ---------------------------------------------------------------------------
def load_farside(asset: str) -> LoadResult:
    """Load Farside daily ETF flows for ``asset`` in {"btc", "eth"}.

    Numbers are USD millions. NaN values in business days are genuine 'no
    report' and are left as-is (the calendar aligner treats them as 0 only on
    weekends/holidays, per the `flow` semantics)."""

    file = {
        "btc": "farside_btc_etf_flows__daily.csv",
        "eth": "farside_eth_etf_flows__daily.csv",
    }[asset.lower()]
    path = DATA_DIR / "Farside ETF Data" / file
    df = pd.read_csv(path)
    df = _canonical(df, "date")
    # Coerce numeric; strings like "-" should have been cleaned upstream.
    for c in df.columns:
        df[c] = pd.to_numeric(df[c], errors="coerce")
    df = df.rename(columns={c: f"{asset}_etf_{c.lower()}" for c in df.columns})
    return _finalize(df, f"farside_{asset}_etf", path)


# ---------------------------------------------------------------------------
# DeFi / stablecoins
# ---------------------------------------------------------------------------
def load_tvl_all() -> LoadResult:
    path = DATA_DIR / "DefiLlama/TVL/Daily/tvl_all_chains_daily.csv"
    df = pd.read_csv(path)
    df = _canonical(df, "date")
    df = df.rename(columns={"TVL": "defi_tvl_usd"})
    df["defi_tvl_usd"] = pd.to_numeric(df["defi_tvl_usd"], errors="coerce")
    df["defi_tvl_usd"] = df["defi_tvl_usd"].where(df["defi_tvl_usd"] > 0, np.nan)
    return _finalize(df, "tvl_all", path)


def load_stablecoin_total() -> LoadResult:
    """Sum of *all* per-id market caps → total stablecoin USD float.

    Each column is a DefiLlama stablecoin id. Missing = not yet launched; we
    treat NaN as 0 when summing so the total reflects the cross-section at
    each date."""

    path = DATA_DIR / "DefiLlama/Stablecoins/stablecoin_mcap_by_defillama_id__daily.csv"
    df = pd.read_csv(path)
    df = _canonical(df, "date")
    totals = df.fillna(0).sum(axis=1).rename("stables_total_usd")
    # If before any stablecoin existed the row would still be 0 — keep it.
    out = totals.to_frame()
    return _finalize(out, "stablecoin_total", path)


# ---------------------------------------------------------------------------
# Sentiment
# ---------------------------------------------------------------------------
def load_fear_greed() -> LoadResult:
    path = DATA_DIR / "AlternativeMe/fear_greed_index__daily.csv"
    df = pd.read_csv(path)
    df = _canonical(df, "date")
    df = df.rename(columns={"fng_value": "fng_value"})
    df["fng_value"] = pd.to_numeric(df["fng_value"], errors="coerce")
    return _finalize(df[["fng_value"]], "fear_greed", path)


# ---------------------------------------------------------------------------
# Convenience
# ---------------------------------------------------------------------------
def load_all() -> dict[str, LoadResult]:
    return {
        "btc_price": load_btc_price(),
        "eth_price": load_eth_price(),
        "btc_mcap": load_btc_mcap(),
        "eth_mcap": load_eth_mcap(),
        "btc_exchange_netflow": load_btc_exchange_netflow(),
        "btc_miner_to_exchange": load_btc_miner_to_exchange(),
        "btc_mvrv": load_btc_mvrv(),
        "fred_macro": load_fred(),
        "spy": load_tv_close("SPY_sp500_etf__daily.csv", "spy"),
        "qqq": load_tv_close("QQQ_nasdaq100_etf__daily.csv", "qqq"),
        "gld": load_tv_close("GLD_gold_etf__daily.csv", "gld"),
        "xlk": load_tv_close("XLK_tech_sector_etf__daily.csv", "xlk"),
        "dxy_tv": load_tv_close("DXY_us_dollar_index__daily.csv", "dxy_tv"),
        "dvol_btc": load_tv_close("Deribit_BTC_volatility_index_DVOL__daily.csv", "dvol_btc"),
        "cme_btc_basis": load_tv_close(
            "CME_BTC_futures_minus_SPOT_BTC_basis__daily.csv", "cme_btc_basis"
        ),
        "cme_eth_basis": load_tv_close(
            "CME_ETH_futures_minus_SPOT_ETH_basis__daily.csv", "cme_eth_basis"
        ),
        "farside_btc_etf": load_farside("btc"),
        "farside_eth_etf": load_farside("eth"),
        "tvl_all": load_tvl_all(),
        "stablecoin_total": load_stablecoin_total(),
        "fear_greed": load_fear_greed(),
    }


__all__ = [
    "LoadResult",
    "load_btc_price",
    "load_eth_price",
    "load_btc_mcap",
    "load_eth_mcap",
    "load_btc_exchange_netflow",
    "load_btc_miner_to_exchange",
    "load_btc_mvrv",
    "load_fred",
    "load_tv_close",
    "load_farside",
    "load_tvl_all",
    "load_stablecoin_total",
    "load_fear_greed",
    "load_all",
]
