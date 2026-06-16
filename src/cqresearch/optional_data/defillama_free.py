"""DefiLlama public endpoint URL builders and payload normalizers."""
from __future__ import annotations

from typing import Any
from urllib.parse import quote

import pandas as pd

BASE_URL = "https://api.llama.fi"


def defillama_chains_url() -> str:
    """Return the public DefiLlama chains endpoint."""

    return f"{BASE_URL}/v2/chains"


def defillama_protocol_tvl_url(protocol_slug: str) -> str:
    """Return the public protocol TVL endpoint for a DefiLlama slug."""

    return f"{BASE_URL}/protocol/{quote(protocol_slug.strip())}"


def build_tvl_url(protocol_slug: str) -> str:
    """Compatibility alias for the optional-data sprint spec."""

    return defillama_protocol_tvl_url(protocol_slug)


def normalize_defillama_chains(payload: list[dict[str, Any]]) -> pd.DataFrame:
    """Normalize a DefiLlama chains response to a compact table."""

    rows = []
    for item in payload:
        rows.append(
            {
                "source": "defillama",
                "chain": item.get("name") or item.get("chain"),
                "tvl_usd": pd.to_numeric(item.get("tvl"), errors="coerce"),
                "token_symbol": item.get("tokenSymbol"),
            }
        )
    return pd.DataFrame(rows)


def normalize_defillama_protocol_tvl(payload: dict[str, Any]) -> pd.DataFrame:
    """Normalize a DefiLlama protocol payload's TVL time series."""

    protocol = str(payload.get("slug") or payload.get("name") or "")
    rows = []
    for item in payload.get("tvl", []):
        rows.append(
            {
                "source": "defillama",
                "protocol": protocol,
                "date": pd.to_datetime(item.get("date"), unit="s", utc=True).date(),
                "tvl_usd": pd.to_numeric(item.get("totalLiquidityUSD"), errors="coerce"),
            }
        )
    return pd.DataFrame(rows)


def normalize_chain_tvl_response(payload: list[dict[str, Any]]) -> pd.DataFrame:
    """Compatibility alias for chain-level TVL payload normalization."""

    return normalize_defillama_chains(payload)


def normalize_stablecoin_response(payload: dict[str, Any]) -> pd.DataFrame:
    """Normalize a compact DefiLlama stablecoin payload shape.

    DefiLlama stablecoin endpoint shapes vary by route. This helper accepts the
    common ``peggedAssets`` list and returns a source-tagged supply table.
    """

    rows = []
    for item in payload.get("peggedAssets", []):
        rows.append(
            {
                "source": "defillama",
                "stablecoin": item.get("name") or item.get("symbol"),
                "symbol": item.get("symbol"),
                "circulating_usd": pd.to_numeric(item.get("circulating", {}).get("peggedUSD"), errors="coerce"),
            }
        )
    return pd.DataFrame(rows)


__all__ = [
    "build_tvl_url",
    "defillama_chains_url",
    "defillama_protocol_tvl_url",
    "normalize_chain_tvl_response",
    "normalize_defillama_chains",
    "normalize_defillama_protocol_tvl",
    "normalize_stablecoin_response",
]
