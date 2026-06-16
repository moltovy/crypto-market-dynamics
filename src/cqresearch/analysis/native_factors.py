"""BTC-native factor helpers for the portfolio v2.1 packet."""
from __future__ import annotations

import pandas as pd

from cqresearch.modeling.ablation import run_nested_ablation
from cqresearch.modeling.partial_r2 import safe_standardize

NATIVE_REGISTRY = {
    "market_structure_basis": {
        "columns": ["cme_btc_basis_close_d1"],
        "interpretation": "BTC futures basis or market-structure state.",
    },
    "exchange_flow": {
        "columns": ["btc_exchange_netflow_d1"],
        "interpretation": "Exchange netflow proxy; descriptive flow state.",
    },
    "miner_flow": {
        "columns": ["btc_miner_to_exchange_flow_d1"],
        "interpretation": "Miner-to-exchange flow proxy; descriptive supply pressure state.",
    },
    "valuation_state": {
        "columns": ["btc_mvrv_d1"],
        "interpretation": "MVRV valuation-state change; can mechanically co-move with price.",
    },
}


def native_factor_groups(feat: pd.DataFrame) -> dict[str, list[str]]:
    """Return native-factor groups using columns available in ``feat``."""

    groups = {
        name: [col for col in meta["columns"] if col in feat.columns]
        for name, meta in NATIVE_REGISTRY.items()
    }
    ex_mvrv = [
        col
        for key in ("market_structure_basis", "exchange_flow", "miner_flow")
        for col in groups.get(key, [])
    ]
    groups["native_ex_mvrv"] = ex_mvrv
    groups["mvrv"] = groups.get("valuation_state", [])
    groups["all_native"] = list(dict.fromkeys(ex_mvrv + groups["mvrv"]))
    return groups


def native_factor_registry(feat: pd.DataFrame) -> pd.DataFrame:
    """Return a public registry table for available BTC-native variables."""

    rows: list[dict[str, object]] = []
    for group, meta in NATIVE_REGISTRY.items():
        for col in meta["columns"]:
            rows.append(
                {
                    "group": group,
                    "feature": col,
                    "available": col in feat.columns,
                    "non_missing": int(feat[col].notna().sum()) if col in feat.columns else 0,
                    "interpretation": meta["interpretation"],
                    "portfolio_note": (
                        "Reduced-form input; not a standalone trading signal."
                    ),
                }
            )
    return pd.DataFrame(rows)


def native_factor_ablation(feat: pd.DataFrame, asset: str = "btc") -> pd.DataFrame:
    """Run a native-only ablation that separates MVRV from other native variables."""

    groups = native_factor_groups(feat)
    y = feat[f"{asset}_ret"].copy()
    y.attrs["sample"] = "full_native_support"
    specs = [
        ("N0_intercept", []),
        ("N1_native_ex_mvrv", groups["native_ex_mvrv"]),
        ("N2_mvrv_only", groups["mvrv"]),
        ("N3_all_native", groups["all_native"]),
    ]
    return run_nested_ablation(y, feat, specs)


def native_zscore_dashboard_data(feat: pd.DataFrame) -> pd.DataFrame:
    """Return z-scored BTC-native features for dashboard-style plotting."""

    cols = native_factor_groups(feat)["all_native"]
    if not cols:
        return pd.DataFrame(index=feat.index)
    out = safe_standardize(feat[cols])
    out.index.name = "date"
    return out


def native_factor_correlations(feat: pd.DataFrame, asset: str = "btc") -> pd.DataFrame:
    """Return correlations between native features and asset returns."""

    cols = native_factor_groups(feat)["all_native"]
    target = f"{asset}_ret"
    keep = [target, *cols]
    keep = [col for col in keep if col in feat.columns]
    if len(keep) < 2:
        return pd.DataFrame()
    return feat[keep].corr().round(4)


__all__ = [
    "native_factor_ablation",
    "native_factor_correlations",
    "native_factor_groups",
    "native_factor_registry",
    "native_zscore_dashboard_data",
]
