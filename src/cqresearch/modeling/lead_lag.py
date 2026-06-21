"""Lead-lag regressions and flow-bucket summaries.

Lag convention used throughout:

``lag < 0`` means the flow/proxy series is shifted earlier and therefore leads
the target return. In implementation terms, the regressor is ``x.shift(-lag)``.
For example, lag ``-1`` regresses today's return on yesterday's flow.
"""

from __future__ import annotations

import numpy as np
import pandas as pd

from cqresearch.modeling.ols import fit_ols

LAG_CONVENTION = (
    "lag < 0 means x is shifted earlier and leads the target; lag -1 uses x[t-1] to explain y[t]"
)


def make_lagged_frame(
    y: pd.Series,
    x: pd.Series,
    lags: range,
    controls: pd.DataFrame | None = None,
) -> pd.DataFrame:
    """Build one aligned frame with lagged ``x`` columns and optional controls."""

    y_name = y.name or "target"
    x_name = x.name or "x"
    data: dict[str, pd.Series] = {y_name: y}
    for lag in lags:
        data[f"{x_name}_lag_{lag}"] = x.shift(-lag)
    out = pd.DataFrame(data)
    if controls is not None and not controls.empty:
        out = pd.concat([out, controls], axis=1)
    return out


def _asset_from_name(name: str | None) -> str:
    if not name:
        return "unknown"
    return name.split("_")[0]


def lead_lag_regression_grid(
    y: pd.Series,
    x: pd.Series,
    controls: pd.DataFrame | None,
    lags: range = range(-5, 6),
    hac_lags: int = 5,
) -> pd.DataFrame:
    """Fit ``y`` on each lagged ``x`` plus controls and return one row per lag."""

    rows: list[dict[str, object]] = []
    control_cols = list(controls.columns) if controls is not None else []
    frame = make_lagged_frame(y, x, lags, controls=controls)
    y_name = y.name or "target"
    x_name = x.name or "x"
    asset = _asset_from_name(y.name)

    for lag in lags:
        lag_col = f"{x_name}_lag_{lag}"
        regressors = [lag_col, *control_cols]
        df = frame[[y_name, *regressors]].dropna()
        if len(df) < max(30, len(regressors) + 5):
            rows.append(
                {
                    "asset": asset,
                    "target": y_name,
                    "x": x_name,
                    "lag": int(lag),
                    "coefficient": np.nan,
                    "hac_se": np.nan,
                    "t": np.nan,
                    "p": np.nan,
                    "n": len(df),
                    "r2": np.nan,
                    "controls": ";".join(control_cols),
                    "lag_convention": LAG_CONVENTION,
                    "note": "insufficient_sample",
                }
            )
            continue

        res = fit_ols(
            df[y_name],
            df[regressors],
            hac_lags=hac_lags,
            label=f"{x_name}_lag_{lag}",
        )
        rows.append(
            {
                "asset": asset,
                "target": y_name,
                "x": x_name,
                "lag": int(lag),
                "coefficient": float(res.params[lag_col]),
                "hac_se": float(res.hac_se[lag_col]),
                "t": float(res.tvals[lag_col]),
                "p": float(res.pvals[lag_col]),
                "n": int(res.nobs),
                "r2": float(res.r2),
                "controls": ";".join(control_cols),
                "lag_convention": LAG_CONVENTION,
                "note": "ok",
            }
        )
    return pd.DataFrame(rows)


def _forward_return(ret: pd.Series, horizon: int) -> pd.Series:
    if horizon <= 0:
        return ret
    return sum(ret.shift(-i) for i in range(horizon + 1))


def flow_quintile_summary(
    ret: pd.Series,
    flow_intensity: pd.Series,
    horizons: tuple[int, ...] = (0, 1, 3, 5),
) -> pd.DataFrame:
    """Summarize forward returns by flow-intensity quintile."""

    flow_name = flow_intensity.name or "flow_intensity"
    base = pd.DataFrame({"flow": flow_intensity}).dropna()
    if len(base) < 30 or base["flow"].nunique() < 5:
        return pd.DataFrame(
            columns=[
                "quintile",
                "horizon",
                "n",
                "mean_return",
                "median_return",
                "mean_flow_intensity",
                "flow_col",
                "lag_convention",
            ]
        )

    base["quintile"] = pd.qcut(base["flow"], 5, labels=False, duplicates="drop") + 1
    rows: list[dict[str, object]] = []
    for horizon in horizons:
        fwd = _forward_return(ret, horizon).rename("forward_return")
        df = pd.concat([base, fwd], axis=1).dropna()
        for quintile, group in df.groupby("quintile", observed=True):
            rows.append(
                {
                    "quintile": int(quintile),
                    "horizon": int(horizon),
                    "n": len(group),
                    "mean_return": float(group["forward_return"].mean()),
                    "median_return": float(group["forward_return"].median()),
                    "mean_flow_intensity": float(group["flow"].mean()),
                    "flow_col": flow_name,
                    "lag_convention": LAG_CONVENTION,
                }
            )
    return pd.DataFrame(rows)


def top_flow_days(
    panel_or_feat: pd.DataFrame, flow_col: str, ret_col: str, n: int = 10
) -> pd.DataFrame:
    """Return the largest absolute-flow days with same-day target returns."""

    cols = [flow_col, ret_col]
    missing = [col for col in cols if col not in panel_or_feat.columns]
    if missing:
        return pd.DataFrame(columns=["date", flow_col, ret_col, "abs_flow_intensity", "note"])
    df = panel_or_feat[cols].dropna().copy()
    df["abs_flow_intensity"] = df[flow_col].abs()
    df = df.sort_values("abs_flow_intensity", ascending=False).head(n)
    df = df.reset_index(names="date")
    df["rank_by_abs_flow"] = range(1, len(df) + 1)
    df["note"] = "largest absolute same-day flow intensity; descriptive only"
    return df


__all__ = [
    "LAG_CONVENTION",
    "flow_quintile_summary",
    "lead_lag_regression_grid",
    "make_lagged_frame",
    "top_flow_days",
]
