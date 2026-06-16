"""Portfolio v2.2 advanced quant diagnostics and artifact orchestration."""
from __future__ import annotations

import json
from dataclasses import dataclass
from datetime import UTC, datetime
from pathlib import Path
from typing import Any, SupportsFloat, cast

import matplotlib
import pandas as pd

matplotlib.use("Agg")
import matplotlib.pyplot as plt
from config.paths import DATA_DIR, PROJECT_ROOT

from cqresearch.analysis.portfolio_v2_1 import (
    ETH_ETF_DATE,
    fmt,
    git_commit_hash,
    load_panel_and_features,
    md_table,
)
from cqresearch.modeling.ablation import (
    BTC_MVRV,
    BTC_NATIVE_EX_MVRV,
    ETH_NATIVE,
    LIQUIDITY,
    MACRO,
    SENTIMENT,
    TRADFI,
)
from cqresearch.modeling.cusum import cusum_recursive_residuals, cusum_summary
from cqresearch.modeling.fevd_sensitivity import (
    run_fevd_order_sensitivity,
    summarize_fevd_sensitivity,
)
from cqresearch.modeling.ols import fit_ols
from cqresearch.modeling.partial_r2 import safe_standardize
from cqresearch.modeling.pca_blocks import make_pca_factor_panel, pca_block_summary
from cqresearch.modeling.robustness_grid import run_robustness_grid
from cqresearch.modeling.rolling_connectedness import rolling_fevd_connectedness
from cqresearch.modeling.shapley_r2 import exact_block_shapley_r2, rolling_block_shapley_r2
from cqresearch.viz.style import PALETTE, add_footer, setup

setup()

PORTFOLIO_DIR = PROJECT_ROOT / "reports" / "portfolio_v2_2"
TABLES_DIR = PORTFOLIO_DIR / "tables"
FIGURES_DIR = PORTFOLIO_DIR / "figures"
MODEL_CARDS_DIR = PORTFOLIO_DIR / "model_cards"
DIAGNOSTICS_DIR = PORTFOLIO_DIR / "diagnostics"

FOOTER = (
    "Crypto Market Factor Lab v2.2 - frozen panel, 2020-01-01..2026-04-11 - "
    "advanced diagnostics, not causal identification"
)

REQUIRED_MODEL_CARD_SECTIONS = [
    "Purpose",
    "Inputs",
    "Sample",
    "Method",
    "Output files",
    "Interpretation",
    "Risks / limitations",
    "Upgrade path",
]


@dataclass
class PortfolioV22Result:
    tables: list[Path]
    figures: list[Path]
    reports: list[Path]
    model_cards: list[Path]
    optional_failures: list[str]
    manifest_path: Path


def ensure_portfolio_dirs(base_dir: Path = PORTFOLIO_DIR) -> dict[str, Path]:
    """Create the v2.2 artifact tree and return its paths."""

    paths = {
        "base": base_dir,
        "tables": base_dir / "tables",
        "figures": base_dir / "figures",
        "model_cards": base_dir / "model_cards",
        "diagnostics": base_dir / "diagnostics",
    }
    for path in paths.values():
        path.mkdir(parents=True, exist_ok=True)
    return paths


def required_manifest_fields() -> list[str]:
    """Fields required in the v2.2 manifest."""

    return [
        "generated_at_utc",
        "git_commit",
        "panel",
        "commands_run",
        "tables_generated",
        "figures_generated",
        "reports_generated",
        "model_cards_generated",
        "method_notes",
    ]


def _write_text(path: Path, content: str) -> Path:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(content.strip() + "\n", encoding="utf-8")
    print(f"[ok] wrote {path}")
    return path


def _write_csv(df: pd.DataFrame, path: Path, *, index: bool = False) -> Path:
    path.parent.mkdir(parents=True, exist_ok=True)
    df.to_csv(path, index=index)
    print(f"[ok] wrote {path} rows={len(df)}")
    return path


def _save_figure(fig: plt.Figure, path: Path) -> Path:
    path.parent.mkdir(parents=True, exist_ok=True)
    try:
        fig.tight_layout(rect=(0, 0.045, 1, 1))
    except Exception as exc:
        print(f"[warn] tight_layout failed for {path.name}: {exc}")
    add_footer(fig, FOOTER)
    fig.savefig(path)
    plt.close(fig)
    print(f"[ok] wrote {path}")
    return path


def _active_blocks(
    feat: pd.DataFrame, blocks: dict[str, list[str]], *, min_non_missing: int = 30
) -> dict[str, list[str]]:
    active: dict[str, list[str]] = {}
    for block, cols in blocks.items():
        cols_here = [
            col for col in cols if col in feat.columns and feat[col].notna().sum() >= min_non_missing
        ]
        if cols_here:
            active[block] = cols_here
    return active


def shapley_blocks(asset: str) -> dict[str, list[str]]:
    """Return non-ETF block registry used for Shapley attribution."""

    blocks: dict[str, list[str]] = {
        "Macro": MACRO,
        "TradFi": TRADFI,
        "Liquidity": LIQUIDITY,
        "Sentiment": SENTIMENT,
    }
    if asset == "btc":
        blocks["BTC Native ex MVRV"] = BTC_NATIVE_EX_MVRV
        blocks["BTC MVRV"] = BTC_MVRV
    else:
        blocks["ETH Native"] = ETH_NATIVE
    return blocks


def pca_blocks() -> dict[str, list[str]]:
    """Return factor blocks eligible for PCA compression."""

    return {
        "Macro": MACRO,
        "TradFi": TRADFI,
        "Liquidity": LIQUIDITY,
        "BTC Native": BTC_NATIVE_EX_MVRV + BTC_MVRV,
        "ETF Flow": ["btc_etf_intensity", "eth_etf_intensity"],
    }


def _ols_frame(result: Any, *, asset: str) -> pd.DataFrame:
    out = result.to_frame().reset_index().rename(columns={"index": "term"})
    out.insert(0, "asset", asset)
    return out


def build_pca_tables(feat: pd.DataFrame) -> dict[str, pd.DataFrame]:
    blocks = _active_blocks(feat, pca_blocks(), min_non_missing=180)
    pca_panel, fitted = make_pca_factor_panel(feat, blocks, n_components=2)
    loadings, variance = pca_block_summary(fitted)
    summary = pca_panel.describe().T.reset_index().rename(columns={"index": "component"})

    ols_rows: list[pd.DataFrame] = []
    component_cols = [col for col in pca_panel.columns if pca_panel[col].notna().sum() >= 150]
    for asset in ("btc", "eth"):
        if component_cols:
            res = fit_ols(
                feat[f"{asset}_ret"],
                pca_panel[component_cols],
                hac_lags=10,
                label=f"{asset}_pca_blocks",
            )
            ols_rows.append(_ols_frame(res, asset=asset))
    pca_ols = pd.concat(ols_rows, ignore_index=True) if ols_rows else pd.DataFrame()
    return {
        "pca_block_loadings": loadings,
        "pca_explained_variance": variance,
        "pca_factor_panel_summary": summary,
        "pca_static_ols": pca_ols,
        "pca_factor_panel": pca_panel.reset_index(names="date"),
    }


def build_shapley_tables(feat: pd.DataFrame) -> dict[str, pd.DataFrame]:
    outputs: dict[str, pd.DataFrame] = {}
    for asset in ("btc", "eth"):
        blocks = _active_blocks(feat, shapley_blocks(asset), min_non_missing=150)
        cols = list(dict.fromkeys(col for values in blocks.values() for col in values))
        x = safe_standardize(feat[cols])
        static = exact_block_shapley_r2(feat[f"{asset}_ret"], x, blocks)
        if not static.empty:
            static.insert(0, "asset", asset)
        rolling = rolling_block_shapley_r2(
            feat[f"{asset}_ret"],
            x,
            blocks,
            window=180,
            step=30,
            min_periods=150,
        )
        if not rolling.empty:
            rolling.insert(0, "asset", asset)
        outputs[f"shapley_r2_{asset}"] = static
        outputs[f"rolling_shapley_r2_{asset}_180d"] = rolling
    return outputs


def build_cusum_tables(feat: pd.DataFrame) -> dict[str, pd.DataFrame]:
    rows: list[dict[str, object]] = []
    paths: list[pd.DataFrame] = []
    controls = [col for col in ["spy_ret", "VIXCLS_d1", "DGS10_d1", "stables_total_usd_ret"] if col in feat]
    for asset in ("btc", "eth"):
        summary = cusum_summary(feat[f"{asset}_ret"], feat[controls])
        summary["asset"] = asset
        summary["controls"] = ";".join(controls)
        rows.append(summary)
        path = cusum_recursive_residuals(feat[f"{asset}_ret"], feat[controls])
        if not path.empty:
            path.insert(0, "asset", asset)
            paths.append(path)
    return {
        "cusum_summary": pd.DataFrame(rows),
        "cusum_paths": pd.concat(paths, ignore_index=True) if paths else pd.DataFrame(),
    }


def compact_var_columns(feat: pd.DataFrame) -> list[str]:
    return [col for col in ["btc_ret", "eth_ret", "spy_ret", "VIXCLS_d1"] if col in feat.columns]


def build_fevd_tables(feat: pd.DataFrame) -> dict[str, pd.DataFrame]:
    orderings = {
        "crypto_first": ["btc_ret", "eth_ret", "spy_ret", "VIXCLS_d1"],
        "tradfi_first": ["spy_ret", "VIXCLS_d1", "btc_ret", "eth_ret"],
        "risk_first": ["VIXCLS_d1", "spy_ret", "btc_ret", "eth_ret"],
        "eth_first": ["eth_ret", "btc_ret", "spy_ret", "VIXCLS_d1"],
    }
    cols = compact_var_columns(feat)
    sensitivity = run_fevd_order_sensitivity(feat[cols], orderings, horizon=10, maxlags=5)
    summary = summarize_fevd_sensitivity(sensitivity)
    connectedness = rolling_fevd_connectedness(feat[cols], window=252, step=30, horizon=10)
    return {
        "fevd_order_sensitivity": sensitivity,
        "fevd_order_sensitivity_summary": summary,
        "rolling_connectedness": connectedness,
    }


def build_robustness_tables(feat: pd.DataFrame) -> dict[str, pd.DataFrame]:
    regressors = (
        MACRO
        + TRADFI
        + LIQUIDITY
        + SENTIMENT
        + BTC_NATIVE_EX_MVRV
        + BTC_MVRV
    )
    grid = run_robustness_grid(
        feat,
        "btc_ret",
        regressors,
        windows=(90, 180, 365),
        hac_lags=(5, 10, 20),
        winsorization=(None, 0.01, 0.05),
        include_mvrv=(True, False),
        calendars=("crypto7", "weekday"),
    )
    return {"robustness_grid": grid}


def generate_tables(feat: pd.DataFrame) -> dict[str, pd.DataFrame]:
    tables: dict[str, pd.DataFrame] = {}
    tables.update(build_pca_tables(feat))
    tables.update(build_shapley_tables(feat))
    tables.update(build_cusum_tables(feat))
    tables.update(build_fevd_tables(feat))
    tables.update(build_robustness_tables(feat))
    return tables


def write_tables(tables: dict[str, pd.DataFrame]) -> list[Path]:
    paths: list[Path] = []
    for name, df in tables.items():
        if name == "pca_factor_panel":
            continue
        paths.append(_write_csv(df, TABLES_DIR / f"{name}.csv"))
    return paths


def _figure_empty(ax: plt.Axes, message: str) -> None:
    ax.text(0.5, 0.5, message, ha="center", va="center", transform=ax.transAxes)
    ax.set_axis_off()


def plot_pca_variance(tables: dict[str, pd.DataFrame]) -> Path:
    df = tables["pca_explained_variance"]
    fig, ax = plt.subplots(figsize=(8, 4.5))
    if df.empty:
        _figure_empty(ax, "PCA skipped: not enough usable multi-variable blocks")
    else:
        labels = df["block"] + " PC" + df["component"].astype(str)
        ax.bar(labels, df["explained_variance_ratio"], color=PALETTE["macro"])
        ax.set_title("F70. PCA Explained Variance By Block")
        ax.set_ylabel("Explained variance ratio")
        ax.tick_params(axis="x", rotation=35)
    return _save_figure(fig, FIGURES_DIR / "F70_pca_explained_variance.png")


def plot_pca_factors(tables: dict[str, pd.DataFrame]) -> Path:
    panel = tables["pca_factor_panel"].copy()
    fig, ax = plt.subplots(figsize=(9, 4.5))
    if panel.empty:
        _figure_empty(ax, "No PCA factor panel was generated")
    else:
        panel["date"] = pd.to_datetime(panel["date"])
        cols = [col for col in panel.columns if col != "date"][:6]
        for col in cols:
            ax.plot(panel["date"], panel[col], linewidth=1.0, label=col)
        ax.axvline(ETH_ETF_DATE, color=PALETTE["event"], linewidth=0.8, alpha=0.5)
        ax.set_title("F71. PCA Factor Trajectories")
        ax.set_ylabel("Standardized component score")
        ax.legend(ncol=2)
    return _save_figure(fig, FIGURES_DIR / "F71_pca_factor_trajectories.png")


def plot_shapley_stack(tables: dict[str, pd.DataFrame], asset: str, figure_id: str) -> Path:
    df = tables[f"rolling_shapley_r2_{asset}_180d"].copy()
    fig, ax = plt.subplots(figsize=(9, 4.5))
    if df.empty:
        _figure_empty(ax, f"No rolling Shapley table for {asset.upper()}")
    else:
        df["date"] = pd.to_datetime(df["date"])
        pivot = df.pivot_table(index="date", columns="block", values="shapley_r2", aggfunc="sum")
        ax.stackplot(
            pivot.index,
            [pivot[col].fillna(0).to_numpy() for col in pivot.columns],
            labels=list(pivot.columns),
            alpha=0.85,
        )
        ax.set_title(f"{figure_id}. {asset.upper()} Rolling Exact Block Shapley R2")
        ax.set_ylabel("R2 contribution")
        ax.legend(loc="upper left", ncol=2)
    filename = f"{figure_id}_{asset}_shapley_r2_stack.png"
    return _save_figure(fig, FIGURES_DIR / filename)


def plot_cusum(tables: dict[str, pd.DataFrame], asset: str, figure_id: str) -> Path:
    paths = tables["cusum_paths"].copy()
    fig, ax = plt.subplots(figsize=(9, 4.5))
    sub = paths.loc[paths["asset"] == asset].copy() if not paths.empty else pd.DataFrame()
    if sub.empty:
        _figure_empty(ax, f"No CUSUM path for {asset.upper()}")
    else:
        sub["date"] = pd.to_datetime(sub["date"])
        ax.plot(sub["date"], sub["cusum"], color=PALETTE[asset], linewidth=1.2)
        ax.axhline(1.36, color=PALETTE["warn"], linestyle="--", linewidth=1)
        ax.axhline(-1.36, color=PALETTE["warn"], linestyle="--", linewidth=1)
        ax.set_title(f"{figure_id}. {asset.upper()} Exploratory Residual CUSUM")
        ax.set_ylabel("Standardized cumulative residual")
    filename = f"{figure_id}_{asset}_cusum.png"
    return _save_figure(fig, FIGURES_DIR / filename)


def plot_fevd_sensitivity(tables: dict[str, pd.DataFrame]) -> Path:
    df = tables["fevd_order_sensitivity_summary"].head(12).copy()
    fig, ax = plt.subplots(figsize=(9, 4.5))
    if df.empty:
        _figure_empty(ax, "No successful FEVD order sensitivity rows")
    else:
        df["pair"] = df["from"].astype(str) + " -> " + df["to"].astype(str)
        ax.barh(df["pair"], df["range"], color=PALETTE["institutional"])
        ax.invert_yaxis()
        ax.set_title("F76. FEVD Ordering Sensitivity")
        ax.set_xlabel("Range in 10-day FEVD share")
    return _save_figure(fig, FIGURES_DIR / "F76_fevd_order_sensitivity.png")


def plot_rolling_connectedness(tables: dict[str, pd.DataFrame]) -> Path:
    df = tables["rolling_connectedness"].copy()
    fig, ax = plt.subplots(figsize=(9, 4.5))
    ok = df.loc[df["error"].fillna("") == ""].copy() if not df.empty and "error" in df else df
    if ok.empty:
        _figure_empty(ax, "No successful rolling connectedness windows")
    else:
        ok["date"] = pd.to_datetime(ok["date"])
        ax.plot(ok["date"], ok["connectedness_pct"], color=PALETTE["crypto_native"], linewidth=1.4)
        ax.set_title("F77. Rolling VAR/FEVD Connectedness")
        ax.set_ylabel("Total connectedness index")
    return _save_figure(fig, FIGURES_DIR / "F77_rolling_connectedness.png")


def plot_robustness_heatmap(tables: dict[str, pd.DataFrame]) -> Path:
    df = tables["robustness_grid"].copy()
    fig, ax = plt.subplots(figsize=(8, 4.5))
    ok = df.loc[df["error"].fillna("") == ""].copy() if not df.empty and "error" in df else df
    if ok.empty:
        _figure_empty(ax, "No successful robustness-grid rows")
    else:
        ok = ok.loc[
            (ok["calendar"] == "crypto7")
            & (ok["include_mvrv"])
            & (ok["winsorization"].astype(str) == "0.01")
        ]
        heat = ok.pivot_table(index="window", columns="hac_lags", values="r2", aggfunc="mean")
        im = ax.imshow(heat.to_numpy(dtype=float), aspect="auto", cmap="viridis")
        ax.set_xticks(range(len(heat.columns)), labels=[str(col) for col in heat.columns])
        ax.set_yticks(range(len(heat.index)), labels=[str(idx) for idx in heat.index])
        ax.set_title("F78. BTC Robustness Grid R2")
        ax.set_xlabel("HAC lags")
        ax.set_ylabel("Trailing window")
        fig.colorbar(im, ax=ax, label="R2")
    return _save_figure(fig, FIGURES_DIR / "F78_robustness_grid_heatmap.png")


def generate_figures(tables: dict[str, pd.DataFrame]) -> list[Path]:
    return [
        plot_pca_variance(tables),
        plot_pca_factors(tables),
        plot_shapley_stack(tables, "btc", "F72"),
        plot_shapley_stack(tables, "eth", "F73"),
        plot_cusum(tables, "btc", "F74"),
        plot_cusum(tables, "eth", "F75"),
        plot_fevd_sensitivity(tables),
        plot_rolling_connectedness(tables),
        plot_robustness_heatmap(tables),
    ]


def _top_rows(df: pd.DataFrame, cols: list[str], n: int = 6) -> str:
    if df.empty:
        return "_No rows generated._"
    return md_table(df[cols].head(n))


def build_executive_summary(panel_meta: dict[str, Any], tables: dict[str, pd.DataFrame]) -> str:
    btc_shapley = tables["shapley_r2_btc"]
    eth_shapley = tables["shapley_r2_eth"]
    top_btc = (
        btc_shapley.sort_values("shapley_r2", ascending=False).head(3)
        if not btc_shapley.empty
        else pd.DataFrame()
    )
    top_eth = (
        eth_shapley.sort_values("shapley_r2", ascending=False).head(3)
        if not eth_shapley.empty
        else pd.DataFrame()
    )
    return f"""
# Portfolio v2.2 Executive Summary

Portfolio v2.2 is the advanced diagnostics extension for **Crypto Market Factor
Lab**. The main public portfolio release remains v2.1; v2.2 adds PCA factor
compression, exact block Shapley R2, exploratory CUSUM diagnostics, FEVD
ordering sensitivity, rolling connectedness, and a compact BTC robustness grid.

## Dataset

- Frozen panel: `{panel_meta["start"]}` to `{panel_meta["end"]}`
- Rows: `{panel_meta["n_rows"]}`
- Columns: `{panel_meta["n_cols"]}`
- Raw `Data/` files are not refreshed or modified.

## Read First

- `technical_report.md` documents methods and caveats.
- `advanced_methods_summary.md` gives an interview-ready explanation of each
  diagnostic.
- `manifest.json` records generated artifacts, commands, and method notes.
- Model cards in `model_cards/` state purpose, inputs, outputs, interpretation,
  risks, and upgrade paths.

## Static Exact Shapley R2 Leaders

BTC:

{_top_rows(top_btc, ["block", "shapley_r2", "full_r2", "n"])}

ETH:

{_top_rows(top_eth, ["block", "shapley_r2", "full_r2", "n"])}

## Guardrails

ETF-flow relationships are interpreted as reduced-form associations only. CUSUM
is an exploratory residual path diagnostic, not Bai-Perron. FEVD sensitivity is
ordering-sensitive VAR accounting, not structural identification.
"""


def build_advanced_methods_summary(tables: dict[str, pd.DataFrame]) -> str:
    shapley_btc = tables["shapley_r2_btc"]
    fevd_summary = tables["fevd_order_sensitivity_summary"]
    robustness = tables["robustness_grid"]
    ok_robustness = robustness.loc[robustness["error"].fillna("") == ""].copy()
    return f"""
# Portfolio v2.2 Advanced Methods Summary

## PCA Blocks

PCA is fitted independently within multi-variable factor blocks after
standardization. Single-variable blocks are skipped because PCA would only
rename the original series. PCA factors are diagnostics for compression and
visualization, not economic latent variables by themselves.

## Exact Block Shapley R2

The static Shapley implementation enumerates every block coalition and allocates
full-model R2 across blocks. Rolling Shapley uses 180-day windows, `step=30`,
and `min_periods=150` to keep runtime bounded.

BTC static full-model R2: `{fmt(shapley_btc["full_r2"].iloc[0] if not shapley_btc.empty else None)}`.

## CUSUM

CUSUM uses standardized full-sample OLS residuals and a visual 5% reference
boundary. It is labeled exploratory because the current implementation is not a
full multi-break estimator.

## FEVD Sensitivity

FEVD is recomputed under compact variable orderings: `crypto_first`,
`tradfi_first`, `risk_first`, and `eth_first`. The sensitivity table reports the
range of 10-day FEVD shares across successful orderings.

Top sensitivity rows:

{_top_rows(fevd_summary, ["from", "to", "min", "max", "range"], n=8)}

## Robustness Grid

The BTC-focused grid varies trailing window, HAC lag length, winsorization,
MVRV inclusion, and calendar support.

Successful grid rows: `{len(ok_robustness)}` of `{len(robustness)}`.
"""


def build_technical_report(panel_meta: dict[str, Any], tables: dict[str, pd.DataFrame]) -> str:
    pca_var = tables["pca_explained_variance"]
    cusum = tables["cusum_summary"]
    connectedness = tables["rolling_connectedness"]
    return f"""
# Portfolio v2.2 Technical Report

## Scope

This packet extends the v2.1 portfolio release with advanced diagnostics while
leaving v2 and v2.1 outputs intact. It is built from the frozen master panel
(`{panel_meta["start"]}` to `{panel_meta["end"]}`) and writes only to
`reports/portfolio_v2_2/`.

## Generated Tables

- PCA: `pca_block_loadings.csv`, `pca_explained_variance.csv`,
  `pca_factor_panel_summary.csv`, `pca_static_ols.csv`
- Shapley: `shapley_r2_btc.csv`, `shapley_r2_eth.csv`,
  `rolling_shapley_r2_btc_180d.csv`, `rolling_shapley_r2_eth_180d.csv`
- Regime/VAR: `cusum_summary.csv`, `fevd_order_sensitivity.csv`,
  `fevd_order_sensitivity_summary.csv`, `rolling_connectedness.csv`
- Robustness: `robustness_grid.csv`

## PCA Output Snapshot

{_top_rows(pca_var, ["block", "component", "explained_variance_ratio", "n_variables"], n=10)}

## CUSUM Summary

{md_table(cusum)}

## Rolling Connectedness Snapshot

{_top_rows(connectedness, ["date", "connectedness_pct", "lag_order", "n", "error"], n=8)}

## Interpretation Discipline

- Shapley R2 is a predictive attribution diagnostic over specified blocks; it
  does not prove economic causality.
- FEVD order sensitivity records how much VAR accounting depends on variable
  ordering.
- The CUSUM figures are residual diagnostics and are not labeled Bai-Perron.
- The robustness grid shows whether BTC model fit is stable across reasonable
  settings; unstable cells are evidence to discuss limitations, not to hide.
"""


def build_data_atlas(panel_meta: dict[str, Any], tables: dict[str, pd.DataFrame]) -> str:
    inventory = pd.read_csv(DATA_DIR / "MASTER_DATA.csv")
    source_summary = (
        inventory.assign(row_count=pd.to_numeric(inventory["row_count"], errors="coerce").fillna(0))
        .groupby("source", dropna=False)
        .agg(files=("relpath", "count"), rows=("row_count", "sum"))
        .reset_index()
        .sort_values("files", ascending=False)
    )
    source_summary["rows"] = source_summary["rows"].astype(int)
    table_coverage = pd.DataFrame(
        [
            {"table": name, "rows": len(df), "columns": len(df.columns)}
            for name, df in tables.items()
            if name != "pca_factor_panel"
        ]
    )
    return (
        "# Portfolio v2.2 Data Atlas\n\n"
        "This v2.2 atlas inherits the frozen v2.1 panel and adds advanced diagnostic "
        "table coverage. Raw `Data/` files are not modified.\n\n"
        f"- Date range: `{panel_meta['start']}` through `{panel_meta['end']}`\n"
        f"- Rows: `{panel_meta['n_rows']}`\n"
        f"- Columns: `{panel_meta['n_cols']}`\n"
        f"- Source inventory rows: `{len(inventory)}`\n\n"
        "## Source Inventory\n\n"
        + md_table(source_summary)
        + "\n\n"
        "## Advanced Table Coverage\n\n"
        + md_table(table_coverage)
        + "\n\n## Data Policy\n\n"
        "Portfolio v2.2 uses only the frozen committed panel and derived feature "
        "transforms. No raw `Data/` file is modified and no live or paid source is "
        "required for regeneration."
    )


def build_resume_bullets(panel_meta: dict[str, Any]) -> str:
    return f"""
# Portfolio v2.2 Resume Bullets

- Built an advanced crypto factor diagnostics extension over a frozen
  `{panel_meta["n_rows"]}`-row daily BTC/ETH panel, adding PCA block factors,
  exact block Shapley R2, rolling VAR/FEVD connectedness, CUSUM diagnostics, and
  a robustness grid without changing raw data.
- Implemented exact subset-enumerated block Shapley attribution and a bounded
  rolling version (`window=180`, `step=30`) to separate tested attribution from
  simpler drop-one partial R2 used in earlier release packets.
- Hardened interpretation language around ETF flows, PCA, FEVD, and CUSUM so the
  public portfolio reads as reduced-form analytics rather than causal claims.
"""


def model_card_texts() -> dict[str, str]:
    cards = {
        "pca_factor_blocks.md": (
            "PCA Factor Blocks",
            "Compress related factor blocks into a small number of standardized components.",
            "Frozen feature panel columns grouped into macro, TradFi, liquidity, BTC-native, and ETF-flow blocks.",
            "Full frozen daily panel; blocks with fewer than two usable variables are skipped.",
            "Standardize each block, fit sklearn PCA independently, and retain up to two components.",
            "`pca_block_loadings.csv`, `pca_explained_variance.csv`, `F70`, `F71`.",
            "Components summarize co-movement inside feature blocks and support visual diagnostics.",
            "PCA signs are arbitrary; components are statistical summaries, not structural factors.",
            "Add out-of-sample stability checks and component sign anchoring.",
        ),
        "shapley_r2.md": (
            "Exact Block Shapley R2",
            "Allocate model R2 across factor blocks using exact coalition enumeration.",
            "BTC/ETH returns and standardized non-ETF factor blocks.",
            "Static full sample plus stepped 180-day rolling windows.",
            "Enumerate all block subsets and average marginal R2 contributions by Shapley weights.",
            "`shapley_r2_btc.csv`, `shapley_r2_eth.csv`, `rolling_shapley_r2_*`, `F72`, `F73`.",
            "Shows which specified blocks receive more predictive attribution in the selected design.",
            "Shapley attribution depends on block definitions and the linear model design; it is not causal proof.",
            "Add Owen grouping for nested block hierarchies if future specs require it.",
        ),
        "cusum_diagnostics.md": (
            "CUSUM Diagnostics",
            "Flag periods where residual paths suggest possible parameter instability.",
            "BTC/ETH returns with compact macro/TradFi/liquidity controls.",
            "Full frozen sample with complete-case rows.",
            "Fit full-sample OLS, cumulate standardized residuals, and compare with a visual 5% boundary.",
            "`cusum_summary.csv`, `cusum_paths.csv`, `F74`, `F75`.",
            "Boundary crossings are prompts for regime discussion and further testing.",
            "This is exploratory standardized residual CUSUM, not full Bai-Perron multi-break estimation.",
            "Replace or augment with statsmodels recursive residual tests and selected break-date inference.",
        ),
        "fevd_order_sensitivity.md": (
            "FEVD Order Sensitivity",
            "Measure how compact VAR FEVD shares change under alternative variable orderings.",
            "BTC, ETH, SPY, and VIX-derived return/difference features.",
            "Full frozen sample after complete-case filtering.",
            "Run 10-day VAR FEVD under crypto-first, TradFi-first, risk-first, and ETH-first orderings.",
            "`fevd_order_sensitivity.csv`, `fevd_order_sensitivity_summary.csv`, `F76`.",
            "Large ranges indicate relationships whose variance accounting depends on ordering choices.",
            "Reduced-form FEVD is ordering-sensitive and does not establish structural shocks.",
            "Add generalized FEVD or sign-restricted structural VAR variants.",
        ),
        "rolling_connectedness.md": (
            "Rolling Connectedness",
            "Track time variation in compact VAR/FEVD total connectedness.",
            "BTC, ETH, SPY, and VIX-derived return/difference features.",
            "252-day windows stepped every 30 days.",
            "Fit compact VARs and compute Diebold-Yilmaz-style total connectedness from 10-day FEVD.",
            "`rolling_connectedness.csv`, `F77`.",
            "Highlights periods where cross-market variance accounting becomes more or less linked.",
            "Small VARs and BIC lag selection can be unstable in stressed windows.",
            "Add larger asset sets, generalized FEVD, and bootstrap intervals.",
        ),
        "robustness_grid.md": (
            "BTC Robustness Grid",
            "Test whether BTC factor fit is sensitive to common modeling choices.",
            "BTC returns and macro, TradFi, liquidity, sentiment, and BTC-native regressors.",
            "Trailing 90, 180, and 365 day windows with crypto-seven-day and weekday calendars.",
            "Run static HAC OLS across window, HAC lag, winsorization, MVRV, and calendar choices.",
            "`robustness_grid.csv`, `F78`.",
            "Stable R2 across cells supports model robustness; unstable cells clarify limitations.",
            "Grid search is diagnostic and in-sample; it is not model selection by itself.",
            "Add out-of-sample forecasts, purged cross-validation, and coefficient stability summaries.",
        ),
    }
    rendered: dict[str, str] = {}
    for filename, values in cards.items():
        title, purpose, inputs, sample, method, outputs, interpretation, risks, upgrade = values
        rendered[filename] = f"""
# Model Card - {title}

## Purpose

{purpose}

## Inputs

{inputs}

## Sample

{sample}

## Method

{method}

## Output files

{outputs}

## Interpretation

{interpretation}

## Risks / limitations

{risks}

## Upgrade path

{upgrade}
"""
    return rendered


def write_model_cards() -> list[Path]:
    return [_write_text(MODEL_CARDS_DIR / name, body) for name, body in model_card_texts().items()]


def write_reports(panel_meta: dict[str, Any], tables: dict[str, pd.DataFrame]) -> list[Path]:
    return [
        _write_text(PORTFOLIO_DIR / "executive_summary.md", build_executive_summary(panel_meta, tables)),
        _write_text(
            PORTFOLIO_DIR / "advanced_methods_summary.md",
            build_advanced_methods_summary(tables),
        ),
        _write_text(PORTFOLIO_DIR / "technical_report.md", build_technical_report(panel_meta, tables)),
        _write_text(PORTFOLIO_DIR / "data_atlas.md", build_data_atlas(panel_meta, tables)),
        _write_text(PORTFOLIO_DIR / "resume_bullets.md", build_resume_bullets(panel_meta)),
    ]


def write_optional_failures(failures: list[str]) -> Path:
    if failures:
        body = "# Optional Failures\n\n" + "\n".join(f"- {failure}" for failure in failures)
    else:
        body = "# Optional Failures\n\nNo optional v2.2 modules failed."
    return _write_text(DIAGNOSTICS_DIR / "optional_failures.md", body)


def write_verification_placeholder() -> Path:
    path = DIAGNOSTICS_DIR / "verification.md"
    if path.exists() and "## Command Results" in path.read_text(encoding="utf-8"):
        print(f"[ok] preserved {path}")
        return path
    body = """
# Portfolio v2.2 Verification

Generated by `scripts/run_portfolio_v2_2_pipeline.py`.

## Required Commands

- `uv run pytest`
- `uv run mypy src/cqresearch`
- `uv run python scripts/run_portfolio_v2_2_pipeline.py`
- `uv run ruff check scripts/run_portfolio_v2_2_pipeline.py src/cqresearch/modeling/pca_blocks.py src/cqresearch/modeling/shapley_r2.py src/cqresearch/modeling/cusum.py src/cqresearch/modeling/fevd_sensitivity.py src/cqresearch/modeling/rolling_connectedness.py src/cqresearch/modeling/robustness_grid.py src/cqresearch/analysis/portfolio_v2_2.py tests/unit/test_pca_blocks.py tests/unit/test_shapley_r2.py tests/unit/test_cusum.py tests/unit/test_fevd_sensitivity.py tests/unit/test_rolling_connectedness.py tests/unit/test_robustness_grid.py tests/unit/test_portfolio_v2_2_pipeline.py`

Status should be updated after verification.
"""
    return _write_text(path, body)


def build_manifest(
    panel_meta: dict[str, Any],
    tables: list[Path],
    figures: list[Path],
    reports: list[Path],
    model_cards: list[Path],
    optional_failures: list[str],
) -> dict[str, Any]:
    return {
        "generated_at_utc": datetime.now(UTC).isoformat(),
        "git_commit": git_commit_hash(),
        "portfolio_dir": str(PORTFOLIO_DIR.relative_to(PROJECT_ROOT)),
        "panel": {
            "start": panel_meta["start"],
            "end": panel_meta["end"],
            "n_rows": panel_meta["n_rows"],
            "n_cols": panel_meta["n_cols"],
        },
        "commands_run": [
            "uv run pytest",
            "uv run mypy src/cqresearch",
            "uv run python scripts/run_portfolio_v2_2_pipeline.py",
            (
                "uv run ruff check scripts/run_portfolio_v2_2_pipeline.py "
                "src/cqresearch/modeling/pca_blocks.py "
                "src/cqresearch/modeling/shapley_r2.py "
                "src/cqresearch/modeling/cusum.py "
                "src/cqresearch/modeling/fevd_sensitivity.py "
                "src/cqresearch/modeling/rolling_connectedness.py "
                "src/cqresearch/modeling/robustness_grid.py "
                "src/cqresearch/analysis/portfolio_v2_2.py "
                "tests/unit/test_pca_blocks.py "
                "tests/unit/test_shapley_r2.py "
                "tests/unit/test_cusum.py "
                "tests/unit/test_fevd_sensitivity.py "
                "tests/unit/test_rolling_connectedness.py "
                "tests/unit/test_robustness_grid.py "
                "tests/unit/test_portfolio_v2_2_pipeline.py"
            ),
        ],
        "tables_generated": [str(path.relative_to(PROJECT_ROOT)) for path in tables],
        "figures_generated": [str(path.relative_to(PROJECT_ROOT)) for path in figures],
        "reports_generated": [str(path.relative_to(PROJECT_ROOT)) for path in reports],
        "model_cards_generated": [str(path.relative_to(PROJECT_ROOT)) for path in model_cards],
        "optional_failures": optional_failures,
        "method_notes": {
            "pca": "block-level PCA after standardization; single-variable blocks skipped",
            "shapley_r2": "exact static block Shapley R2 plus stepped rolling windows",
            "cusum": "exploratory standardized residual CUSUM; not full Bai-Perron",
            "fevd": "compact VAR FEVD sensitivity; ordering-sensitive and reduced-form",
            "rolling_connectedness": "252-day windows, step=30, 10-day FEVD horizon",
            "robustness_grid": "BTC in-sample HAC OLS sensitivity grid",
            "etf_flows": "no causal ETF-flow claim is made",
        },
    }


def write_manifest(manifest: dict[str, Any]) -> Path:
    missing = [field for field in required_manifest_fields() if field not in manifest]
    if missing:
        raise ValueError(f"Manifest missing required fields: {missing}")
    path = PORTFOLIO_DIR / "manifest.json"
    path.write_text(json.dumps(manifest, indent=2), encoding="utf-8")
    print(f"[ok] wrote {path}")
    return path


def _coerce_float(value: object) -> str:
    if value is None or pd.isna(value):
        return "n/a"
    return f"{float(cast(SupportsFloat, value)):.3f}"


def run_portfolio_v2_2_pipeline() -> PortfolioV22Result:
    """Build the complete Portfolio v2.2 release packet."""

    ensure_portfolio_dirs()
    _panel, feat, panel_meta = load_panel_and_features()
    tables = generate_tables(feat)
    table_paths = write_tables(tables)
    figure_paths = generate_figures(tables)
    report_paths = write_reports(panel_meta, tables)
    model_card_paths = write_model_cards()
    optional_failures: list[str] = []
    report_paths.append(write_optional_failures(optional_failures))
    report_paths.append(write_verification_placeholder())
    manifest = build_manifest(
        panel_meta,
        table_paths,
        figure_paths,
        report_paths,
        model_card_paths,
        optional_failures,
    )
    manifest_path = write_manifest(manifest)
    print(
        "[ok] v2.2 summary: "
        f"BTC Shapley full R2={_coerce_float(tables['shapley_r2_btc']['full_r2'].iloc[0])}"
        if not tables["shapley_r2_btc"].empty
        else "[ok] v2.2 summary: BTC Shapley table empty"
    )
    return PortfolioV22Result(
        tables=table_paths,
        figures=figure_paths,
        reports=report_paths,
        model_cards=model_card_paths,
        optional_failures=optional_failures,
        manifest_path=manifest_path,
    )


__all__ = [
    "PORTFOLIO_DIR",
    "PortfolioV22Result",
    "build_manifest",
    "compact_var_columns",
    "ensure_portfolio_dirs",
    "generate_tables",
    "pca_blocks",
    "required_manifest_fields",
    "run_portfolio_v2_2_pipeline",
    "shapley_blocks",
]
