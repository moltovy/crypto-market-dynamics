"""FEVD order-sensitivity diagnostics."""

from __future__ import annotations

from typing import Any

import pandas as pd

from cqresearch.modeling.var_fevd import fit_var_fevd


def run_fevd_order_sensitivity(
    df: pd.DataFrame,
    orderings: dict[str, list[str]],
    horizon: int = 10,
    maxlags: int = 10,
) -> pd.DataFrame:
    """Run FEVD for each variable ordering and return a long table."""

    rows: list[dict[str, object]] = []
    for ordering_name, cols in orderings.items():
        cols_here = [col for col in cols if col in df.columns]
        if len(cols_here) < 3:
            rows.append({"ordering": ordering_name, "error": "fewer_than_3_available_columns"})
            continue
        try:
            fevd = fit_var_fevd(df[cols_here].dropna(), horizon=horizon, maxlags=maxlags)
            for from_col, row in fevd.table.iterrows():
                for to_col, share in row.items():
                    rows.append(
                        {
                            "ordering": ordering_name,
                            "from": from_col,
                            "to": to_col,
                            "share": float(share),
                            "lag_order": fevd.lag_order,
                            "n": fevd.n,
                            "horizon": horizon,
                            "error": "",
                        }
                    )
        except Exception as exc:
            rows.append({"ordering": ordering_name, "error": str(exc)})
    return pd.DataFrame(rows)


def summarize_fevd_sensitivity(results: pd.DataFrame) -> pd.DataFrame:
    """Summarize min/max/range of FEVD shares across orderings."""

    if results.empty or "share" not in results.columns:
        return pd.DataFrame()
    if "error" in results.columns:
        ok = results[results["error"].fillna("") == ""].copy()
    else:
        ok = results.copy()
    if ok.empty:
        return pd.DataFrame()
    summary = (
        ok.groupby(["from", "to"], dropna=False)["share"].agg(["min", "max", "mean"]).reset_index()
    )
    summary["range"] = summary["max"] - summary["min"]
    return summary.sort_values("range", ascending=False)


def plot_order_sensitivity(summary: pd.DataFrame, ax: Any | None = None) -> Any:
    """Plot the largest FEVD share ranges and return the matplotlib axis."""

    import matplotlib.pyplot as plt

    axis = ax if ax is not None else plt.subplots(figsize=(8, 4))[1]
    if summary.empty:
        axis.text(0.5, 0.5, "No FEVD sensitivity rows", ha="center", va="center")
        axis.set_axis_off()
        return axis
    top = summary.head(12).copy()
    top["pair"] = top["from"].astype(str) + " -> " + top["to"].astype(str)
    axis.barh(top["pair"], top["range"])
    axis.invert_yaxis()
    axis.set_xlabel("Range in FEVD share")
    axis.set_title("FEVD Order Sensitivity")
    return axis


__all__ = ["plot_order_sensitivity", "run_fevd_order_sensitivity", "summarize_fevd_sensitivity"]
