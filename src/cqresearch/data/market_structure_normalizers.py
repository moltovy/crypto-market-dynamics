"""Payload normalizers for curated market-structure CSVs."""

from __future__ import annotations

from typing import Any

import pandas as pd


def normalize_binance_exchange_info(payload: dict[str, Any]) -> pd.DataFrame:
    """Normalize Binance exchangeInfo payloads to one row per symbol."""

    rows = []
    for item in payload.get("symbols", []):
        rows.append(
            {
                "source": "binance",
                "symbol": item.get("symbol"),
                "status": item.get("status"),
                "base_asset": item.get("baseAsset"),
                "quote_asset": item.get("quoteAsset"),
                "is_spot_trading_allowed": item.get("isSpotTradingAllowed"),
                "is_margin_trading_allowed": item.get("isMarginTradingAllowed"),
                "contract_type": item.get("contractType", ""),
            }
        )
    return pd.DataFrame(rows)


def normalize_binance_klines(payload: list[list[Any]], symbol: str, interval: str = "1d") -> pd.DataFrame:
    """Normalize Binance kline arrays."""

    cols = [
        "open_time_ms",
        "open",
        "high",
        "low",
        "close",
        "volume",
        "close_time_ms",
        "quote_asset_volume",
        "trade_count",
        "taker_buy_base_volume",
        "taker_buy_quote_volume",
        "ignore",
    ]
    if not payload:
        return pd.DataFrame(columns=["source", "symbol", "interval", *cols[:-1], "date", "close_time"])
    frame = pd.DataFrame(payload, columns=cols)
    for col in cols[:-1]:
        frame[col] = pd.to_numeric(frame[col], errors="coerce")
    frame.insert(0, "source", "binance")
    frame.insert(1, "symbol", symbol.upper())
    frame.insert(2, "interval", interval)
    frame["date"] = pd.to_datetime(frame["open_time_ms"], unit="ms", utc=True).dt.date
    frame["close_time"] = pd.to_datetime(frame["close_time_ms"], unit="ms", utc=True)
    return frame.drop(columns=["ignore"])


def normalize_binance_24h_tickers(payload: list[dict[str, Any]]) -> pd.DataFrame:
    """Normalize Binance 24h ticker snapshots."""

    frame = pd.DataFrame(payload)
    if frame.empty:
        return frame
    frame.insert(0, "source", "binance")
    numeric_cols = [
        "priceChange",
        "priceChangePercent",
        "weightedAvgPrice",
        "lastPrice",
        "volume",
        "quoteVolume",
        "count",
    ]
    for col in numeric_cols:
        if col in frame:
            frame[col] = pd.to_numeric(frame[col], errors="coerce")
    return frame


def normalize_binance_funding_rates(payload: list[dict[str, Any]]) -> pd.DataFrame:
    """Normalize USD-M funding-rate history."""

    frame = pd.DataFrame(payload)
    if frame.empty:
        return pd.DataFrame(columns=["source", "symbol", "funding_time", "funding_rate", "mark_price"])
    frame.insert(0, "source", "binance")
    frame["funding_time"] = pd.to_datetime(frame["fundingTime"], unit="ms", utc=True)
    frame["funding_rate"] = pd.to_numeric(frame["fundingRate"], errors="coerce")
    frame["mark_price"] = pd.to_numeric(frame.get("markPrice"), errors="coerce")
    return frame.drop(columns=[col for col in ["fundingTime", "fundingRate", "markPrice"] if col in frame])


def normalize_defillama_chains(payload: list[dict[str, Any]]) -> pd.DataFrame:
    """Normalize DefiLlama chain TVL snapshot rows."""

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


def normalize_defillama_stablecoins(payload: dict[str, Any]) -> pd.DataFrame:
    """Normalize DefiLlama stablecoin snapshot payload."""

    rows = []
    for item in payload.get("peggedAssets", []):
        circulating = item.get("circulating") or {}
        rows.append(
            {
                "source": "defillama",
                "defillama_id": item.get("id"),
                "name": item.get("name"),
                "symbol": item.get("symbol"),
                "peg_type": item.get("pegType"),
                "circulating_usd": pd.to_numeric(circulating.get("peggedUSD"), errors="coerce"),
            }
        )
    return pd.DataFrame(rows)


def normalize_defillama_overview(payload: dict[str, Any], dataset: str) -> pd.DataFrame:
    """Normalize DefiLlama overview chart payloads when present."""

    rows = []
    for key in ("totalDataChart", "totalDataChartBreakdown", "data"):
        values = payload.get(key)
        if not isinstance(values, list):
            continue
        for item in values:
            if isinstance(item, list) and len(item) >= 2:
                rows.append({"source": "defillama", "dataset": dataset, "date": pd.to_datetime(item[0], unit="s", utc=True).date(), "value": item[1]})
            elif isinstance(item, dict):
                row = {"source": "defillama", "dataset": dataset, **item}
                rows.append(row)
        if rows:
            break
    return pd.DataFrame(rows)


def normalize_cmc_fear_greed(payload: dict[str, Any]) -> pd.DataFrame:
    """Normalize CMC Fear & Greed historical response."""

    rows = []
    for item in payload.get("data", []):
        rows.append(
            {
                "source": "coinmarketcap",
                "date": pd.to_datetime(item.get("timestamp"), utc=True).date(),
                "fng_value": pd.to_numeric(item.get("value"), errors="coerce"),
                "fng_classification": item.get("value_classification"),
            }
        )
    return pd.DataFrame(rows)


def normalize_alternative_me_fear_greed(frame: pd.DataFrame) -> pd.DataFrame:
    """Normalize tracked AlternativeMe Fear & Greed data to the comparison schema."""

    out = frame.copy()
    out.insert(0, "source", "alternative_me")
    out["date"] = pd.to_datetime(out["date"], errors="coerce").dt.date
    out["fng_value"] = pd.to_numeric(out["fng_value"], errors="coerce")
    return out[["source", "date", "fng_value", "fng_classification"]]
