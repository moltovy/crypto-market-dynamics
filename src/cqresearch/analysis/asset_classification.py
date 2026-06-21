"""Internal asset classification rules for market-structure universes."""

from __future__ import annotations

from pathlib import Path

import pandas as pd
import yaml


def load_classification_overrides(path: Path) -> dict[str, set[str]]:
    """Load symbol override sets from YAML."""

    if not path.exists():
        return {}
    raw = yaml.safe_load(path.read_text(encoding="utf-8")) or {}
    return {str(key): {str(item).upper() for item in values or []} for key, values in raw.items()}


def classify_asset(symbol: str, overrides: dict[str, set[str]] | None = None) -> str:
    """Classify an asset symbol using explicit overrides and conservative suffix rules."""

    token = symbol.upper().strip()
    rules = overrides or {}
    for class_name, values in rules.items():
        if token in values:
            return class_name
    if token.startswith("W") and len(token) > 3:
        return "wrapped_assets"
    if token.endswith("USD") or token.endswith("USDT") or token.endswith("USDC"):
        return "stablecoins"
    return "risk_assets"


def classify_symbol_frame(
    frame: pd.DataFrame, overrides: dict[str, set[str]] | None = None
) -> pd.DataFrame:
    """Add base-asset class labels to a symbol table."""

    out = frame.copy()
    if "base_asset" not in out and "symbol" in out:
        out["base_asset"] = (
            out["symbol"].astype(str).str.extract(r"^([A-Z0-9]+?)(?:USDT|USDC|FDUSD|BUSD)$")[0]
        )
    out["asset_class"] = (
        out["base_asset"].fillna("").map(lambda value: classify_asset(str(value), overrides))
    )
    return out


def classification_summary(frame: pd.DataFrame) -> pd.DataFrame:
    """Return counts by classification."""

    if "asset_class" not in frame:
        return pd.DataFrame(columns=["asset_class", "asset_count"])
    return (
        frame.groupby("asset_class", dropna=False)
        .size()
        .rename("asset_count")
        .reset_index()
        .sort_values(["asset_count", "asset_class"], ascending=[False, True])
    )
