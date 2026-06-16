"""CoinGecko free endpoint URL builders and payload normalizers."""
from __future__ import annotations

from typing import Any
from urllib.parse import urlencode

import pandas as pd

BASE_URL = "https://api.coingecko.com/api/v3"


def coin_market_chart_url(
    coin_id: str,
    *,
    vs_currency: str = "usd",
    days: str = "max",
    interval: str = "daily",
) -> str:
    """Return a CoinGecko market-chart URL."""

    query = urlencode({"vs_currency": vs_currency, "days": days, "interval": interval})
    return f"{BASE_URL}/coins/{coin_id.strip()}/market_chart?{query}"


def build_market_chart_url(
    coin_id: str,
    *,
    vs_currency: str = "usd",
    days: str = "max",
    interval: str = "daily",
) -> str:
    """Compatibility alias for the optional-data sprint spec."""

    return coin_market_chart_url(
        coin_id,
        vs_currency=vs_currency,
        days=days,
        interval=interval,
    )


def _series_frame(values: list[list[float]], column: str) -> pd.DataFrame:
    frame = pd.DataFrame(values, columns=["timestamp_ms", column])
    frame["date"] = pd.to_datetime(frame["timestamp_ms"], unit="ms", utc=True).dt.date
    return frame[["date", column]]


def normalize_market_chart(payload: dict[str, Any], coin_id: str) -> pd.DataFrame:
    """Normalize a CoinGecko market-chart response."""

    prices = _series_frame(payload.get("prices", []), "price_usd")
    market_caps = _series_frame(payload.get("market_caps", []), "market_cap_usd")
    volumes = _series_frame(payload.get("total_volumes", []), "volume_usd")
    out = prices.merge(market_caps, on="date", how="outer").merge(volumes, on="date", how="outer")
    out.insert(0, "source", "coingecko")
    out.insert(1, "coin_id", coin_id)
    return out.sort_values("date").reset_index(drop=True)


def normalize_market_chart_response(payload: dict[str, Any], coin_id: str) -> pd.DataFrame:
    """Compatibility alias for market-chart normalization."""

    return normalize_market_chart(payload, coin_id)


__all__ = [
    "build_market_chart_url",
    "coin_market_chart_url",
    "normalize_market_chart",
    "normalize_market_chart_response",
]
