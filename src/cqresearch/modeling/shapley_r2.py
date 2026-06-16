"""Exact block Shapley R^2 attribution."""
from __future__ import annotations

from itertools import combinations
from math import factorial

import numpy as np
import pandas as pd


def _r2_on_frame(frame: pd.DataFrame, y_col: str, cols: list[str]) -> float:
    y = frame[y_col].to_numpy(dtype=float)
    tss = float(((y - y.mean()) ** 2).sum())
    if tss <= 0:
        return float("nan")
    if not cols:
        return 0.0
    x = frame[cols].to_numpy(dtype=float)
    design = np.column_stack([np.ones(len(frame)), x])
    beta, *_ = np.linalg.lstsq(design, y, rcond=None)
    resid = y - design @ beta
    return float(1.0 - float(resid @ resid) / tss)


def _block_cols(blocks: dict[str, list[str]], selected_blocks: list[str]) -> list[str]:
    return list(dict.fromkeys(col for block in selected_blocks for col in blocks[block]))


def r2_for_selected_blocks(
    y: pd.Series,
    x: pd.DataFrame,
    blocks: dict[str, list[str]],
    selected_blocks: list[str],
) -> float:
    """Return in-sample R^2 for selected blocks on the common full-block sample."""

    available = {
        block: [col for col in cols if col in x.columns]
        for block, cols in blocks.items()
    }
    all_cols = list(dict.fromkeys(col for cols in available.values() for col in cols))
    frame = pd.concat([y.rename("__y__"), x[all_cols]], axis=1).dropna()
    cols = _block_cols(available, selected_blocks)
    return _r2_on_frame(frame, "__y__", cols)


def exact_block_shapley_r2(
    y: pd.Series, x: pd.DataFrame, blocks: dict[str, list[str]]
) -> pd.DataFrame:
    """Compute exact block Shapley R^2 over all block coalitions."""

    available = {
        block: [col for col in cols if col in x.columns]
        for block, cols in blocks.items()
    }
    available = {block: cols for block, cols in available.items() if cols}
    block_names = list(available)
    all_cols = list(dict.fromkeys(col for cols in available.values() for col in cols))
    frame = pd.concat([y.rename("__y__"), x[all_cols]], axis=1).dropna()
    m = len(block_names)
    if m == 0 or frame.empty:
        return pd.DataFrame()

    cache: dict[tuple[str, ...], float] = {}

    def r2_subset(subset: tuple[str, ...]) -> float:
        key = tuple(sorted(subset))
        if key not in cache:
            cache[key] = _r2_on_frame(frame, "__y__", _block_cols(available, list(key)))
        return cache[key]

    rows: list[dict[str, object]] = []
    for block in block_names:
        contribution = 0.0
        others = [candidate for candidate in block_names if candidate != block]
        for k in range(len(others) + 1):
            weight = factorial(k) * factorial(m - k - 1) / factorial(m)
            for subset in combinations(others, k):
                with_block = tuple(sorted((*subset, block)))
                contribution += weight * (r2_subset(with_block) - r2_subset(tuple(subset)))
        rows.append(
            {
                "block": block,
                "shapley_r2": float(contribution),
                "full_r2": float(r2_subset(tuple(block_names))),
                "n": len(frame),
                "n_blocks": m,
                "variables": ";".join(available[block]),
                "method": "exact_block_shapley_r2",
            }
        )
    return pd.DataFrame(rows)


def validate_shapley_sum(shapley_df: pd.DataFrame, full_r2: float, tol: float = 1e-8) -> bool:
    """Return True when Shapley contributions sum to full R^2 within tolerance."""

    if shapley_df.empty:
        return False
    return bool(abs(float(shapley_df["shapley_r2"].sum()) - full_r2) <= tol)


def rolling_block_shapley_r2(
    y: pd.Series,
    x: pd.DataFrame,
    blocks: dict[str, list[str]],
    window: int = 180,
    step: int = 30,
    min_periods: int = 150,
) -> pd.DataFrame:
    """Rolling exact block Shapley R^2 using stepped windows for tractability."""

    cols = list(dict.fromkeys(col for values in blocks.values() for col in values if col in x.columns))
    frame = pd.concat([y.rename("__y__"), x[cols]], axis=1).dropna()
    rows: list[pd.DataFrame] = []
    for end in range(window - 1, len(frame), step):
        chunk = frame.iloc[end - window + 1 : end + 1]
        if len(chunk) < min_periods:
            continue
        out = exact_block_shapley_r2(chunk["__y__"], chunk[cols], blocks)
        if out.empty:
            continue
        out.insert(0, "date", frame.index[end])
        out.insert(1, "window", window)
        out.insert(2, "step", step)
        rows.append(out)
    return pd.concat(rows, ignore_index=True) if rows else pd.DataFrame()


__all__ = [
    "exact_block_shapley_r2",
    "r2_for_selected_blocks",
    "rolling_block_shapley_r2",
    "validate_shapley_sum",
]
