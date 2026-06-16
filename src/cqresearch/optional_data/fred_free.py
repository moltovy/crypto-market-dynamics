"""FRED URL builders and payload normalizers.

FRED data is free, but the official API typically requires a free API key. This
module only builds URLs and normalizes supplied payloads; it does not fetch.
"""
from __future__ import annotations

from typing import Any
from urllib.parse import urlencode

import pandas as pd

BASE_URL = "https://api.stlouisfed.org/fred"


def fred_observations_url(
    series_id: str,
    *,
    api_key: str | None = None,
    observation_start: str | None = None,
    observation_end: str | None = None,
) -> str:
    """Return a FRED observations URL."""

    query: dict[str, str] = {"series_id": series_id.strip(), "file_type": "json"}
    if api_key:
        query["api_key"] = api_key
    if observation_start:
        query["observation_start"] = observation_start
    if observation_end:
        query["observation_end"] = observation_end
    return f"{BASE_URL}/series/observations?{urlencode(query)}"


def normalize_fred_observations(payload: dict[str, Any], series_id: str) -> pd.DataFrame:
    """Normalize a FRED observations payload."""

    rows = []
    for item in payload.get("observations", []):
        value = item.get("value")
        rows.append(
            {
                "source": "fred",
                "series_id": series_id.strip(),
                "date": pd.to_datetime(item.get("date")).date(),
                "value": pd.to_numeric(None if value == "." else value, errors="coerce"),
            }
        )
    return pd.DataFrame(rows)


__all__ = ["fred_observations_url", "normalize_fred_observations"]
