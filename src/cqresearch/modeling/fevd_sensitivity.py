"""FEVD order-sensitivity diagnostics."""
from __future__ import annotations

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
        ok.groupby(["from", "to"], dropna=False)["share"]
        .agg(["min", "max", "mean"])
        .reset_index()
    )
    summary["range"] = summary["max"] - summary["min"]
    return summary.sort_values("range", ascending=False)


__all__ = ["run_fevd_order_sensitivity", "summarize_fevd_sensitivity"]
