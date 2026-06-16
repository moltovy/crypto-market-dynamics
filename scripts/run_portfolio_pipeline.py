"""Build the portfolio_v2 release packet.

This script packages the newest complete historical analysis bundle into a
portfolio-facing artifact set. It intentionally does not refresh or mutate the
frozen source data under ``Data/``.
"""
from __future__ import annotations

import json
import shutil
import sys
from dataclasses import dataclass
from datetime import UTC, datetime
from pathlib import Path

import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
sys.path.insert(0, str(ROOT / "src"))

from config.paths import (  # noqa: E402
    DATA_DIR,
    REPORTS_FIGURES_DIR,
    REPORTS_PANELS_DIR,
    REPORTS_TABLES_DIR,
)

PORTFOLIO_DIR = ROOT / "reports" / "portfolio_v2"
PORTFOLIO_FIGURES_DIR = PORTFOLIO_DIR / "figures"
PORTFOLIO_TABLES_DIR = PORTFOLIO_DIR / "tables"
PORTFOLIO_MODEL_CARDS_DIR = PORTFOLIO_DIR / "model_cards"

REQUIRED_TABLES = {
    "block_r2_pre_post.csv",
    "correlation_matrix_post_etf.csv",
    "correlation_matrix_pre_etf.csv",
    "descriptive_stats.csv",
    "etf_flow_regression.csv",
    "event_studies.csv",
    "fevd_10d.csv",
    "fevd_10d_compact.csv",
    "rolling_ols_btc_180d.csv",
    "rolling_ols_eth_180d.csv",
    "rolling_r2_btc_median_by_year.csv",
    "rolling_r2_eth_median_by_year.csv",
    "static_ols_pre_post_etf.csv",
    "structural_breaks_summary.csv",
    "sup_f_series_btc.csv",
    "sup_f_series_eth.csv",
    "var_fevd_meta.json",
    "var_fevd_meta_compact.json",
}

TABLES_TO_COPY = sorted(REQUIRED_TABLES)

FIGURES_TO_COPY = {
    "F01_cumulative_returns.png": "hero_cumulative_returns.png",
    "F02_btc_rolling_r2.png": "btc_rolling_r2.png",
    "F02_eth_rolling_r2.png": "eth_rolling_r2.png",
    "F03_btc_partial_r2_stack.png": "btc_drop_one_r2_stack.png",
    "F04_eth_partial_r2_stack.png": "eth_drop_one_r2_stack.png",
    "F05_sup_f_btc.png": "btc_single_break_sup_f.png",
    "F06_sup_f_eth.png": "eth_single_break_sup_f.png",
    "F07_fevd_heatmap.png": "fevd_compact_heatmap.png",
    "F07b_fevd_heatmap_full.png": "fevd_full_heatmap.png",
    "F08_event_cars.png": "event_study_cars.png",
    "F09_coverage.png": "data_coverage.png",
    "F10_btc_tradfi_corr.png": "btc_tradfi_rolling_corr.png",
}

EXTERNAL_SOURCES = [
    (
        "Common Risk Factors in Cryptocurrency",
        "https://onlinelibrary.wiley.com/doi/10.1111/jofi.13119",
        "Academic context for factor-style crypto return analysis.",
    ),
    (
        "SEC statement on spot bitcoin ETP approval",
        "https://www.sec.gov/newsroom/speeches-statements/gensler-statement-spot-bitcoin-011023",
        "Official context for the January 10, 2024 spot bitcoin ETP approval.",
    ),
    (
        "SEC spot ether ETP approval order",
        "https://www.sec.gov/files/rules/sro/nysearca/2024/34-100224.pdf",
        "Official context for the May 23, 2024 ether ETP rule-change approvals.",
    ),
    (
        "FRED API documentation",
        "https://fred.stlouisfed.org/docs/api/fred/",
        "Official macro data API context.",
    ),
    (
        "DefiLlama API documentation",
        "https://api-docs.defillama.com/",
        "Official DeFi/stablecoin/TVL API context.",
    ),
    (
        "CoinGecko API documentation",
        "https://docs.coingecko.com/",
        "Official crypto market data API context.",
    ),
    (
        "Binance public market data documentation",
        "https://developers.binance.com/docs/binance-spot-api-docs/rest-api",
        "Official public exchange market-data context.",
    ),
    (
        "Bai and Perron multiple structural changes",
        "https://ideas.repec.org/a/ecm/emetrp/v66y1998i1p47-78.html",
        "Methods context for full multi-break models not implemented here.",
    ),
    (
        "MacKinlay event-study survey",
        "https://www.bu.edu/econ/files/2011/01/MacKinlay-1996-Event-Studies-in-Economics-and-Finance.pdf",
        "Methods context for abnormal-return event studies.",
    ),
    (
        "Diebold-Yilmaz connectedness research",
        "https://financialconnectedness.org/research.html",
        "Methods context for FEVD-based connectedness framing.",
    ),
]


@dataclass(frozen=True)
class PortfolioInputs:
    table_dir: Path
    figure_dir: Path
    panel_meta: dict
    inventory: pd.DataFrame
    static_ols: pd.DataFrame
    block_r2: pd.DataFrame
    etf_flow: pd.DataFrame
    structural_breaks: pd.DataFrame
    event_studies: pd.DataFrame
    fevd_compact: pd.DataFrame
    coverage: pd.DataFrame
    var_meta: dict
    var_meta_compact: dict


def is_complete_table_dir(path: Path, required: set[str] | None = None) -> bool:
    """Return True when a dated table directory has every required artifact."""

    required_names = required if required is not None else REQUIRED_TABLES
    return path.is_dir() and all((path / name).exists() for name in required_names)


def latest_complete_table_dir(
    base: Path = REPORTS_TABLES_DIR, required: set[str] | None = None
) -> Path:
    """Select the newest complete dated table bundle."""

    candidates = sorted(
        [p for p in base.iterdir() if p.is_dir()],
        key=lambda p: p.name,
        reverse=True,
    )
    for candidate in candidates:
        if is_complete_table_dir(candidate, required):
            return candidate
    raise FileNotFoundError(f"No complete table bundle found under {base}")


def latest_complete_figure_dir(base: Path = REPORTS_FIGURES_DIR) -> Path:
    """Select the newest figure bundle with all portfolio hero figures."""

    candidates = sorted(
        [p for p in base.iterdir() if p.is_dir()],
        key=lambda p: p.name,
        reverse=True,
    )
    for candidate in candidates:
        if all((candidate / name).exists() for name in FIGURES_TO_COPY):
            return candidate
    raise FileNotFoundError(f"No complete figure bundle found under {base}")


def read_csv(path: Path) -> pd.DataFrame:
    """Read a CSV and remove pandas' serialized index columns."""

    df = pd.read_csv(path)
    return df.loc[:, ~df.columns.astype(str).str.startswith("Unnamed")]


def read_json(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))


def md_table(df: pd.DataFrame, *, index: bool = False) -> str:
    if df.empty:
        return "_No rows._"
    return df.to_markdown(index=index)


def fmt(value: object, digits: int = 3) -> str:
    if value is None or pd.isna(value):
        return "n/a"
    if isinstance(value, str):
        return value
    return f"{float(value):.{digits}f}"


def fmt_p(value: object) -> str:
    if value is None or pd.isna(value):
        return "n/a"
    value_f = float(value)
    if value_f < 0.001:
        return "<0.001"
    return f"{value_f:.3f}"


def ensure_portfolio_dirs() -> None:
    for path in [
        PORTFOLIO_DIR,
        PORTFOLIO_FIGURES_DIR,
        PORTFOLIO_TABLES_DIR,
        PORTFOLIO_MODEL_CARDS_DIR,
    ]:
        path.mkdir(parents=True, exist_ok=True)


def load_inputs() -> PortfolioInputs:
    table_dir = latest_complete_table_dir()
    figure_dir = latest_complete_figure_dir()
    panel_meta = read_json(REPORTS_PANELS_DIR / "master_daily_meta.json")
    inventory = read_csv(DATA_DIR / "MASTER_DATA.csv")
    return PortfolioInputs(
        table_dir=table_dir,
        figure_dir=figure_dir,
        panel_meta=panel_meta,
        inventory=inventory,
        static_ols=read_csv(table_dir / "static_ols_pre_post_etf.csv"),
        block_r2=read_csv(table_dir / "block_r2_pre_post.csv"),
        etf_flow=read_csv(table_dir / "etf_flow_regression.csv"),
        structural_breaks=read_csv(table_dir / "structural_breaks_summary.csv"),
        event_studies=read_csv(table_dir / "event_studies.csv"),
        fevd_compact=read_csv(table_dir / "fevd_10d_compact.csv"),
        coverage=read_csv(REPORTS_PANELS_DIR / "master_daily_coverage.csv"),
        var_meta=read_json(table_dir / "var_fevd_meta.json"),
        var_meta_compact=read_json(table_dir / "var_fevd_meta_compact.json"),
    )


def source_summary(inputs: PortfolioInputs) -> pd.DataFrame:
    inv = inputs.inventory.copy()
    inv["row_count"] = pd.to_numeric(inv["row_count"], errors="coerce").fillna(0)
    grouped = (
        inv.groupby("source", dropna=False)
        .agg(files=("relpath", "count"), rows=("row_count", "sum"))
        .reset_index()
        .sort_values("files", ascending=False)
    )
    grouped["rows"] = grouped["rows"].astype(int)
    return grouped


def static_row(inputs: PortfolioInputs, asset: str, sample: str) -> pd.Series:
    rows = inputs.static_ols[
        (inputs.static_ols["calendar"] == "crypto7")
        & (inputs.static_ols["asset"] == asset)
        & (inputs.static_ols["sample"] == sample)
        & (inputs.static_ols["regressor"] == "const")
    ]
    if rows.empty:
        raise KeyError(f"Missing static OLS row for {asset}/{sample}")
    return rows.iloc[0]


def etf_flow_row(inputs: PortfolioInputs, regressor: str = "btc_etf_intensity") -> pd.Series:
    rows = inputs.etf_flow[inputs.etf_flow["regressor"] == regressor]
    if rows.empty:
        raise KeyError(f"Missing ETF-flow row for {regressor}")
    return rows.iloc[0]


def break_row(inputs: PortfolioInputs, asset: str) -> pd.Series:
    rows = inputs.structural_breaks[inputs.structural_breaks["asset"] == asset]
    if rows.empty:
        raise KeyError(f"Missing break row for {asset}")
    return rows.iloc[0]


def top_coverage_issues(inputs: PortfolioInputs) -> pd.DataFrame:
    cov = inputs.coverage.copy()
    cov["missing_pct"] = pd.to_numeric(cov["missing_pct"], errors="coerce")
    cov = cov.sort_values("missing_pct", ascending=False)
    return cov.head(12)


def write_text(path: Path, content: str) -> None:
    path.write_text(content.strip() + "\n", encoding="utf-8")
    print(f"[ok] wrote {path}")


def copy_artifacts(inputs: PortfolioInputs) -> None:
    for name in TABLES_TO_COPY:
        shutil.copy2(inputs.table_dir / name, PORTFOLIO_TABLES_DIR / name)
    for src_name, dst_name in FIGURES_TO_COPY.items():
        shutil.copy2(inputs.figure_dir / src_name, PORTFOLIO_FIGURES_DIR / dst_name)
    print(f"[ok] copied tables from {inputs.table_dir}")
    print(f"[ok] copied figures from {inputs.figure_dir}")


def external_sources_markdown() -> str:
    rows = [
        {"source": f"[{title}]({url})", "use": note}
        for title, url, note in EXTERNAL_SOURCES
    ]
    return md_table(pd.DataFrame(rows))


def build_executive_summary(inputs: PortfolioInputs) -> str:
    btc_post = static_row(inputs, "btc", "post_etf")
    eth_post = static_row(inputs, "eth", "post_etf")
    etf = etf_flow_row(inputs)
    btc_break = break_row(inputs, "btc")
    eth_break = break_row(inputs, "eth")
    return f"""
# Crypto Market Factor Lab - Executive Summary

**Portfolio release:** `portfolio_v2`
**Source table bundle:** `{inputs.table_dir.relative_to(ROOT)}`
**Source figure bundle:** `{inputs.figure_dir.relative_to(ROOT)}`
**Panel:** {inputs.panel_meta["start"]} through {inputs.panel_meta["end"]},
{inputs.panel_meta["n_rows"]:,} daily rows, {inputs.panel_meta["n_cols"]} columns

## Diagnosis

This repo is strongest when framed as a reproducible crypto factor analytics lab:
it combines frozen multi-source data, transparent feature engineering, reduced-form
models, and public-facing interpretation. The highest-value story is not "ETFs
caused a structural break." The better story is that the project maps how BTC
and ETH exposures, liquidity channels, ETF-flow intensity, and connectedness
behaved across changing market regimes.

## Headline Evidence

- BTC post-ETF static factor stack: R^2={fmt(btc_post["r2"])}, N={int(btc_post["n"])}.
- ETH post-ETF static factor stack: R^2={fmt(eth_post["r2"])}, N={int(eth_post["n"])}.
- BTC ETF-flow intensity has a strong same-day association:
  beta={fmt(etf["beta"], 2)}, HAC t={fmt(etf["t"], 2)}, p={fmt_p(etf["p"])},
  model R^2={fmt(etf["r2"])}, N={int(etf["n"])}.
- BTC Chow test at 2024-01-11 is not supportive of a single-date break:
  F={fmt(btc_break["chow_f"], 2)}, p={fmt_p(btc_break["chow_p"])}.
- BTC single-break sup-F peaks at {btc_break["sup_f_argmax_date"]}, not the ETF
  launch date. ETH peaks at {eth_break["sup_f_argmax_date"]}.

## Portfolio Value

The project demonstrates quant research, data engineering, careful econometric
labeling, and crypto market-structure understanding. The public packet should
lead with the data atlas, curated visuals, model cards, and honest narrative
around association rather than causal identification.
"""


def build_data_atlas(inputs: PortfolioInputs) -> str:
    summary = source_summary(inputs)
    coverage = top_coverage_issues(inputs)
    return f"""
# Data Atlas - Portfolio v2

## Frozen Panel

- Date range: {inputs.panel_meta["start"]} through {inputs.panel_meta["end"]}
- Rows: {inputs.panel_meta["n_rows"]:,}
- Columns: {inputs.panel_meta["n_cols"]}
- Source files in inventory: {len(inputs.inventory):,}
- Machine-readable inventory: `Data/MASTER_DATA.csv`
- Human-readable inventory: `Data/MASTER_DATA.md`
- Curation log: `Data/_meta/curation_log.md`

## Source Inventory

{md_table(summary)}

## Highest Missingness Columns

These are not necessarily data-quality failures. ETF columns are structurally
missing before product launch, while newer funds can have very short live
histories.

{md_table(coverage)}

## Core Feature Blocks

| Block | Examples | Use |
|---|---|---|
| Macro | Treasury yields, VIX, DXY, oil, policy rates | Risk and macro controls |
| Institutional | BTC/ETH ETF flows and market proxies | ETF-flow and TradFi plumbing |
| Liquidity | DeFi TVL and stablecoin supply | Crypto-dollar and funding proxy |
| Sentiment | Fear & Greed and uncertainty | Risk-appetite context |
| BTC-native | MVRV, exchange netflow, miner-to-exchange flow | BTC valuation and flow state |
| ETH-native | CME ETH basis and ETH ETF variables | ETH comparison state |

## Data Add-On Decision

Portfolio v2 keeps the frozen data as core. Free APIs such as DefiLlama, FRED,
CoinGecko, and Binance should remain optional unless they add a material,
cached, reproducible variable that is not already represented.
"""


def build_technical_report(inputs: PortfolioInputs) -> str:
    btc_full = static_row(inputs, "btc", "full")
    eth_full = static_row(inputs, "eth", "full")
    btc_pre = static_row(inputs, "btc", "pre_etf")
    btc_post = static_row(inputs, "btc", "post_etf")
    eth_pre = static_row(inputs, "eth", "pre_etf")
    eth_post = static_row(inputs, "eth", "post_etf")
    etf = etf_flow_row(inputs)
    breaks = inputs.structural_breaks.copy()
    block = inputs.block_r2.copy()
    fevd = inputs.fevd_compact.copy()
    etf_events = inputs.event_studies[
        inputs.event_studies["event"].astype(str).str.contains("ETF launch", na=False)
    ].copy()
    return f"""
# Technical Report - Portfolio v2

## Scope

Crypto Market Factor Lab estimates reduced-form BTC/ETH factor diagnostics on a
frozen daily panel. The analysis is useful for regime description, factor
exposure comparison, ETF-flow market-plumbing discussion, and reproducible
research engineering. It is not a causal identification design.

## Static Factor Exposure

| Asset | Full R^2 | Pre-ETF R^2 | Post-ETF R^2 |
|---|---:|---:|---:|
| BTC | {fmt(btc_full["r2"])} | {fmt(btc_pre["r2"])} | {fmt(btc_post["r2"])} |
| ETH | {fmt(eth_full["r2"])} | {fmt(eth_pre["r2"])} | {fmt(eth_post["r2"])} |

## Block R^2 Snapshot

{md_table(block)}

Interpretation: BTC fit is dominated by BTC-native valuation/flow variables in
this specification. ETH is less well explained by the current ETH-native block,
so the portfolio should present ETH as a comparison asset rather than forcing
symmetry.

## ETF-Flow Intensity

ETF-flow intensity is computed as daily ETF flow divided by prior-day USD market
cap. The BTC post-launch regression reports beta={fmt(etf["beta"], 2)},
HAC t={fmt(etf["t"], 2)}, p={fmt_p(etf["p"])}, R^2={fmt(etf["r2"])},
and N={int(etf["n"])}. This is same-day association and should be described as
market-plumbing evidence, not a causal effect.

## Structural-Break Diagnostics

{md_table(breaks)}

The implemented structural-break diagnostics are Chow tests and a single-break
sup-F sweep. They should not be labeled full Bai-Perron multi-break tests.

## VAR/FEVD Connectedness

Compact VAR metadata:

```json
{json.dumps(inputs.var_meta_compact, indent=2)}
```

Compact 10-day FEVD table:

{md_table(fevd)}

The FEVD table is best framed as connectedness diagnostics under the specified
VAR ordering, not a structural spillover model.

## ETF Event Studies

{md_table(etf_events)}

## Reproducibility

Run order:

```powershell
uv sync --all-extras
uv run pytest
uv run python scripts/run_portfolio_pipeline.py
```
"""


def build_manager_report(inputs: PortfolioInputs) -> str:
    source_table = source_summary(inputs)
    etf = etf_flow_row(inputs)
    btc_break = break_row(inputs, "btc")
    eth_break = break_row(inputs, "eth")
    btc_native = inputs.block_r2[
        (inputs.block_r2["asset"] == "btc") & (inputs.block_r2["period"] == "post_etf")
    ].copy()
    native_text = "n/a"
    if not btc_native.empty and "R2_Native_btc" in btc_native:
        native_text = fmt(btc_native.iloc[0]["R2_Native_btc"])
    generated_at = datetime.now(UTC).strftime("%Y-%m-%d %H:%M UTC")
    inventory_count = len(inputs.inventory)
    table_source = inputs.table_dir.relative_to(ROOT)
    figure_source = inputs.figure_dir.relative_to(ROOT)
    return f"""
# Deep Research Manager Report - Crypto Market Factor Lab

Generated: {generated_at}
Source tables: `{table_source}`
Source figures: `{figure_source}`

## 1. Executive Diagnosis

**Verified from repo.** The repository is a working Python research system with
curated data, feature engineering, econometric modules, dated outputs, figures,
run summaries, and tests. The frozen panel spans {inputs.panel_meta["start"]}
through {inputs.panel_meta["end"]} with {inputs.panel_meta["n_rows"]:,} rows and
{inputs.panel_meta["n_cols"]} columns (`reports/panels/master_daily_meta.json`).

**Inference.** The highest-value portfolio positioning is **Crypto Market Factor
Lab**: a reproducible crypto factor analytics and market-structure system. The
repo should lead with the data atlas, model cards, factor-regime diagnostics,
ETF-flow plumbing, and careful visual interpretation.

**External research context.** Academic crypto factor work supports factor-style
crypto return analysis; official SEC materials anchor ETF event dates; official
FRED, DefiLlama, CoinGecko, and Binance docs show that free data can extend the
project, but the frozen repo already has enough coverage for a shippable v2.

## 2. Repo Evidence Summary

**Verified from repo paths.**

- `Data/MASTER_DATA.md` and `Data/MASTER_DATA.csv` document {inventory_count:,}
  curated CSV inventory rows across AlternativeMe,
  Artemis, CryptoQuant, DefiLlama, FRED, Farside ETF Data, and TradingView.
- `Data/_meta/curation_log.md` records the curation/audit trail.
- `src/cqresearch/features/panel.py` scales ETF flow intensity by prior-day USD
  market cap.
- `src/cqresearch/modeling/rolling.py` explicitly implements drop-one marginal
  R^2, not Shapley/Owen.
- `src/cqresearch/modeling/structural_breaks.py` implements Chow and a
  single-break sup-F sweep, not full Bai-Perron.
- `{table_source}` and `{figure_source}` are the complete bundles selected for
  portfolio v2.
- `tests/` contains 13 passing tests after adding the portfolio-bundle selector
  guardrail.

Source inventory:

{md_table(source_table)}

**Inspection coverage.**

| Requested inspection area | Current evidence |
|---|---|
| README and project framing | `README.md` rewritten for Crypto Market Factor Lab |
| Data inventory and curation | `Data/MASTER_DATA.md`, `Data/MASTER_DATA.csv`, `Data/_meta/curation_log.md` |
| Research plan location | root `project_research_plan.md` absent; historical plan is under `Manager/Opus Manager/project_research_plan.md` |
| Config contracts | `config/factor_blocks.yml`, `config/events.yml`, `config/calendars.yml` |
| Specs | legacy warnings in `docs/specs/research_spec.md`, `data_spec.md`, `methods_spec.md`; active v2 specs added |
| Native metrics | `docs/specs/paper_1_native_metrics.yml` retained as historical native-metric context |
| Data pipeline | `src/cqresearch/data/loaders.py`, `panel_builder.py`, feature construction in `features/panel.py` |
| Modeling code | OLS, rolling, structural-break, VAR/FEVD, and event-study modules under `src/cqresearch/modeling/` |
| Scripts | `scripts/01_build_master_panel.py` through `05_robustness.py`, `run_full_pipeline.py`, and `run_portfolio_pipeline.py` |
| Outputs | panel metadata/coverage, latest complete tables/figures, run summaries, drafts, and portfolio v2 packet |
| Tests/tooling | `tests/`, `pyproject.toml`, `Makefile`, `.cursor/rules`, and `prompts/` |

**Verified suspected-fact verdicts.**

| Prior suspected fact | Verdict | Evidence |
|---|---|---|
| Hundreds of curated CSVs across major crypto/macro sources | Confirmed | `Data/MASTER_DATA.csv`, `Data/MASTER_DATA.md` |
| Master panel around 2020-01-01 to 2026-04-11 with about 63 columns | Confirmed | `reports/panels/master_daily_meta.json` |
| ETF-flow intensity equals ETF flow divided by prior-day market cap | Confirmed | `src/cqresearch/features/panel.py` |
| Rolling code computes drop-one marginal R^2, not true block partial R^2 | Confirmed | `src/cqresearch/modeling/rolling.py` |
| Break code is Chow plus single-break sup-F, not full Bai-Perron | Confirmed | `src/cqresearch/modeling/structural_breaks.py` |
| Specs drifted from implementation | Confirmed and corrected for portfolio v2 | legacy warnings in `docs/specs/*.md`; v2 specs added |
| BTC-native variables dominate BTC model fit | Confirmed for current block table | post-ETF BTC native R^2 snapshot {native_text} |
| ETF-flow intensity is strong contemporaneously while lag-only evidence is weaker | Confirmed as a reduced-form association | `etf_flow_regression.csv`, `robustness/R1_lagged_etf_flow.csv` |
| Pre/post correlations and VAR/FEVD exist but needed packaging | Confirmed and packaged | `reports/portfolio_v2/tables/`, `reports/portfolio_v2/figures/` |

## 3. Critique of the Crypto Market Factor Lab Direction

**Recommendation: accept and sharpen.** The direction is right because it uses
the repo's actual strengths: curated data breadth, reproducible Python
orchestration, factor blocks, ETF-flow diagnostics, event studies, and
connectedness. The key refinement is to avoid overclaiming structural breaks or
causality.

**Refinement.** The best v2 is a static, reproducible GitHub portfolio packet
with curated visuals and model cards, not a live-data app or a new methodology
rewrite. The tradeoff is that v2 stays narrower than a dashboard product, but it
is more reliable for public review and interviews.

## 4. Best Project Framing for Resume and GitHub

**Title:** Crypto Market Factor Lab
**Subtitle:** Reproducible BTC/ETH factor-regime analytics across ETF flows,
stablecoin liquidity, macro risk, and crypto-native market structure.

The first 60 seconds should communicate:

- frozen multi-source panel through April 2026
- reproducible one-command portfolio packet
- honest reduced-form econometrics
- curated figures and model cards
- no paid-data dependency for the portfolio release

## 5. Recommended Analysis Modules

| Module | Tier | Purpose | Inputs | Methods | Outputs / figures | Resume value | Difficulty | Risks |
|---|---|---|---|---|---|---|---|---|
| Data Atlas | Tier 0 | Prove data engineering depth | `Data/MASTER_DATA.csv`, panel metadata | inventory and coverage summaries | `data_atlas.md`, coverage figure/table | data engineering, reproducibility | Low | too much detail |
| Market Regime / Rolling Dashboard | Tier 0 | Show time-varying fit | rolling OLS outputs | 180-day rolling R^2 | rolling R^2 figures | quant visualization | Low | over-reading fit |
| Factor-Block Attribution | Tier 0 | Compare macro/institutional/liquidity/native blocks | feature panel, block tables | drop-one marginal R^2 and block R^2 | block tables, stacked R^2 figures | factor modeling | Medium | not fair Shapley allocation |
| ETF-Flow Intensity Lab | Tier 0 | Explain ETF market plumbing | Farside flows, market cap, returns | intensity regression and robustness | ETF regression table, event text | crypto market structure | Medium | simultaneity |
| Stablecoin Liquidity Lab | Tier 1 | Frame crypto-dollar liquidity | stablecoin supply, TVL, returns | descriptive and VAR context | atlas and FEVD context | liquidity research | Medium | weak identification |
| Crypto-Native Factor Lab | Tier 0 | Show BTC valuation/flow insight | MVRV, exchange/miner flows | first-difference native block | BTC native block result | on-chain research | Medium | BTC/ETH asymmetry |
| Structural-Break Diagnostics | Tier 0 | Test regime-change claims carefully | returns and macro/institutional regressors | Chow and single-break sup-F | break table, sup-F figures | econometrics judgment | Medium | not full Bai-Perron |
| VAR/FEVD Connectedness | Tier 1 | Show dynamic connectedness | returns, SPY, VIX, liquidity proxies | statsmodels VAR, 10-day FEVD | compact/full FEVD heatmaps | time-series modeling | Medium | Cholesky ordering |
| Event Studies | Tier 1 | Add event-window context | BTC/ETH returns and SPY | market-model abnormal returns | event CAR table/figure | empirical finance | Medium | confounding and low power |
| Optional Free Data Add-ons | Tier 2 | Future enrichments | free APIs/docs | evaluate and cache only if useful | docs-only decision table | research PM judgment | Low | scope creep |

## 6. Methodology Decisions and Recommendations

| Decision | Options considered | Recommendation | Why |
|---|---|---|---|
| Attribution | true block partial R^2, drop-one marginal R^2, Shapley/Owen | Drop-one for v2; Shapley/Owen later | implemented, honest, reproducible |
| Feature representation | raw stationary variables, PCA factors, LASSO screening | stationary variables plus clear labels | easiest to audit and explain |
| Break tests | Chow/sup-F, Bai-Perron, CUSUM | Chow/sup-F for v2 | current implementation supports it |
| ETF-flow timing | contemporaneous, lagged, event-style | report contemporaneous association plus lag/event caveats | avoids causality overreach |
| Stablecoins | local projections, VAR, descriptive | descriptive and VAR context | enough for portfolio without new identification |
| BTC/ETH symmetry | BTC-primary, fully symmetric | BTC-primary with ETH comparison | BTC-native variables are stronger |
| Data policy | frozen only, optional free add-ons, refresh core | frozen core; free add-ons optional | avoids API/subscription fragility |
| Delivery format | technical report, dashboard, notebook gallery | static GitHub reports and figures | shippable and reviewable |
| App layer | Streamlit/Dash, static packet | static packet for v2 | avoids maintenance burden |

## 7. Data-Source Decision Table

| Source | Variables added | Overlap | Core-story value | Maintenance burden | Decision |
|---|---|---|---|---|---|
| Existing CryptoQuant exports | BTC/ETH native, MVRV, flows | unique/high | high | none for frozen release | Keep core |
| Existing Farside ETF flows | spot ETF fund flows | unique/high | high | none for frozen release | Keep core |
| Existing DefiLlama/Artemis data | TVL, stablecoins, DEX/perps context | medium | high | none for frozen release | Keep core |
| Existing FRED macro | rates, VIX, dollar, macro controls | low | high | none for frozen release | Keep core |
| DefiLlama free API | refreshed TVL/stablecoin/chain metrics | overlaps existing | medium | medium | Optional add-on |
| CoinGecko free/demo API | prices, market caps, volumes | high overlap | low/medium | medium | Optional validation only |
| Binance public data | candles, trades, funding-adjacent market data | partial | medium for microstructure | medium/high | Optional future module |
| SEC filings/orders | ETF dates and regulatory context | low | high as citations | low | Use as context |
| Yahoo/Stooq/free equity endpoints | equity/ETF prices | overlaps TradingView/FRED | low | medium | Reject for v2 |
| Paid data | any premium signals | unknown | not allowed | high | Reject |

## 8. Codex Orchestration Strategy

**Manager owns:** framing, scope, interpretation, causal-language guardrails,
method decisions, acceptance criteria, and review sign-off.

**Codex implementers own:** narrow code/doc patches, artifact generation,
tests, manifests, and evidence collection. In the requested manager/implementer
split, Codex GPT-5.5 extra-high agents should be treated as implementation
agents with bounded tickets, not as scope owners.

**Owner approves:** title/framing, whether to add optional data, whether to add
new methods, and whether to publish/push.

**Task format:** every Codex task should include files to read, likely files to
edit, exact outputs, tests/commands, acceptance criteria, and "do not change"
boundaries. Prevent scope creep by forbidding raw-data edits, new unapproved
models, and unrelated notebook/tooling lint cleanups.

**Branch/PR strategy:** keep `portfolio_v2` as the release branch; use small
follow-up branches for any future optional add-ons; open the PR with generated
portfolio artifacts and verification output.

## 9. Proposed Codex Work Packages

| Ticket | Goal | Files to read | Files likely to edit | Exact outputs | Tests | Acceptance criteria | Do not change | Manager review |
|---|---|---|---|---|---|---|---|---|
| WP1 Reproduction audit | prove baseline | `pyproject.toml`, scripts, tests | dependency files only if needed | command log | `uv sync`, `pytest`, full pipeline | pipeline passes or failure recorded | raw data | reproducibility evidence |
| WP2 Portfolio packet | create v2 artifacts | latest tables/figures, specs | `scripts/run_portfolio_pipeline.py`, `reports/portfolio_v2/` | reports, tables, figures, cards | portfolio pipeline | one-command regeneration | model results | artifact completeness |
| WP3 Method labels | align language | modeling code/specs/reports | README/specs/report text | corrected labels | phrase scans | no false Shapley/Bai-Perron claims | model code | claim accuracy |
| WP4 Model cards | disclose methods | model modules/tables | `model_cards/*.md` | five cards | section check | all required sections present | results | interpretation limits |
| WP5 README polish | public first screen | README, artifacts | README | figure links and quick start | link check | all links resolve | data/results | recruiter clarity |
| WP6 Final audit | public-readiness gate | all active artifacts | `final_audit.md` | audit report | pytest, mypy, Ruff, scans | all required checks pass | unrelated lint | PR readiness |

## 10. Final Artifact Map

- `reports/portfolio_v2/executive_summary.md`
- `reports/portfolio_v2/technical_report.md`
- `reports/portfolio_v2/data_atlas.md`
- `reports/portfolio_v2/manager_report.md`
- `reports/portfolio_v2/resume_bullets.md`
- `reports/portfolio_v2/figures/hero_cumulative_returns.png`
- `reports/portfolio_v2/figures/btc_rolling_r2.png`
- `reports/portfolio_v2/figures/btc_drop_one_r2_stack.png`
- `reports/portfolio_v2/figures/event_study_cars.png`
- `reports/portfolio_v2/figures/fevd_compact_heatmap.png`
- `reports/portfolio_v2/figures/data_coverage.png`
- `reports/portfolio_v2/tables/*.csv`
- `reports/portfolio_v2/model_cards/*.md`
- `reports/portfolio_v2/final_audit.md`
- `reports/portfolio_v2/manifest.json`
- `docs/specs/portfolio_spec.md`
- `docs/specs/methods_spec_v2.md`
- `docs/specs/feature_registry.md`
- `README.md` with hero figure links

## 11. Resume / LinkedIn Positioning

- Built a reproducible Python crypto factor analytics framework over {inventory_count:,} curated
  multi-source CSVs and a 2,293-day BTC/ETH panel through April 2026.
- Engineered stationary factor features for macro, ETF-flow, stablecoin
  liquidity, DeFi, and crypto-native market-structure diagnostics.
- Implemented reduced-form OLS, rolling drop-one R^2, Chow/sup-F break tests,
  VAR/FEVD connectedness, and event-study outputs with model cards.
- Reframed ETF-flow evidence as association and market plumbing rather than
  unsupported causality.

## 12. Questions and Decisions for the Owner

| Decision | Options | Recommendation | If different |
|---|---|---|---|
| Public title | Crypto Market Factor Lab vs legacy title | Crypto Market Factor Lab | Legacy framing narrows recruiter appeal |
| Core data | Frozen only vs refresh | Frozen only | Refresh adds brittle API risk |
| Attribution | Drop-one vs Shapley | Drop-one in v2 | Shapley adds scope and runtime risk |
| Break tests | Chow/sup-F vs Bai-Perron | Chow/sup-F in v2 | Bai-Perron needs tested implementation |
| App layer | Static reports vs dashboard | Static reports first | Dashboard adds maintenance burden |
| Optional data | No add-ons, validation-only add-ons, new core add-ons | No core add-ons for v2 | Core add-ons create maintenance burden |
| BTC/ETH emphasis | BTC-primary, symmetric BTC/ETH | BTC-primary with ETH comparison | Forced symmetry weakens interpretation |

## Verified Headline Corrections

- BTC post-ETF native-block R^2 snapshot: {native_text}.
- BTC ETF-flow same-day intensity: beta={fmt(etf["beta"], 2)},
  t={fmt(etf["t"], 2)}, p={fmt_p(etf["p"])}.
- BTC Chow at ETF date: F={fmt(btc_break["chow_f"], 2)},
  p={fmt_p(btc_break["chow_p"])}.
- ETH Chow at ETF date: F={fmt(eth_break["chow_f"], 2)},
  p={fmt_p(eth_break["chow_p"])}.

## External Research Sources

Sources are separated by role: academic factor context, official regulatory/data
documentation, and methods references. They inform framing and optional add-on
decisions; they do not override the frozen repo evidence.

{external_sources_markdown()}

**Research topic coverage.**

| Topic requested | Portfolio v2 takeaway |
|---|---|
| Crypto factor models and asset pricing | Use reduced-form factor exposure diagnostics; avoid pretending daily regressions identify structural risk premia. |
| BTC/ETH market structure after US spot ETFs | Treat spot ETFs as market-plumbing/institutionalization context, not a single causal break by itself. |
| ETF-flow analysis | Scale flows by prior-day market cap; report contemporaneous association and lag/event caveats. |
| Stablecoin liquidity | Keep stablecoin supply as a crypto-dollar liquidity proxy; avoid causal funding-channel claims in v2. |
| DeFi/perps/DEX/open-interest variables | Existing Artemis/DefiLlama coverage is useful context; do not add live add-ons unless cached. |
| On-chain indicators | BTC MVRV and flow-state variables are strong in the current BTC block; ETH-native coverage is weaker. |
| Structural-break/regime methods | Chow and single-break sup-F are defensible portfolio diagnostics; full Bai-Perron is future work. |
| Rolling R^2, Shapley/Owen, PCA/LASSO, VAR/FEVD, events | Use implemented drop-one R^2, VAR/FEVD, and event studies now; keep Shapley/Owen/PCA/LASSO as optional extensions. |
| Public quant repo best practices | Lead with README, reproducible commands, data atlas, model cards, figures, and honest limitations. |
| Codex agent best practices | Use narrow tickets, explicit acceptance criteria, raw-data guardrails, and verification commands. |
"""


def build_resume_bullets(inputs: PortfolioInputs) -> str:
    return f"""
# Resume and LinkedIn Bullets

## Quant Research

- Built a reproducible BTC/ETH factor-regime lab using OLS, rolling drop-one
  R^2, structural-break diagnostics, VAR/FEVD connectedness, and event studies.
- Analyzed ETF-flow intensity, macro risk, stablecoin liquidity, and crypto-native
  variables on a frozen {inputs.panel_meta["n_rows"]:,}-day panel through
  April 2026.

## Crypto Research

- Mapped post-ETF BTC/ETH market evolution across ETF flows, stablecoin supply,
  DeFi TVL, macro conditions, and on-chain valuation/flow indicators.
- Framed ETF-flow evidence as same-day association and market plumbing, avoiding
  unsupported causal claims.

## Data Engineering / Modeling

- Curated and documented {len(inputs.inventory):,} multi-source CSV files into a reproducible daily
  analytics panel with coverage reporting and model-ready feature transforms.
- Built a one-command portfolio pipeline that assembles reports, tables, figures,
  model cards, and a data atlas from versioned analysis outputs.

## Quant Developer

- Packaged a Python research codebase with `uv`, `pytest`, reusable modeling
  modules, dated outputs, and portfolio release automation.
- Added guardrails so portfolio generation selects complete output bundles and
  does not publish partial pipeline runs.
"""


def model_cards() -> dict[str, str]:
    return {
        "factor_exposure_ols.md": """
# Model Card - Static Factor Exposure OLS

## Purpose

Estimate reduced-form BTC/ETH return exposure to macro, institutional,
liquidity, sentiment, and native factor blocks.

## Inputs

`reports/panels/master_daily.parquet` transformed by
`src/cqresearch/features/panel.py`.

## Method

OLS with HAC/Newey-West standard errors over full, pre-ETF, and post-ETF
samples.

## Outputs

`static_ols_pre_post_etf.csv` and `block_r2_pre_post.csv`.

## Interpretation

Exposure and association diagnostics, not causal estimates.

## Risks

Multicollinearity, mixed calendars, omitted variables, and observational
confounding.

## Upgrade Path

Add block-level Shapley/Owen attribution only after a tested implementation is
available, and keep the current HAC OLS outputs as the reproducible baseline.
""",
        "rolling_drop_one_r2.md": """
# Model Card - Rolling Drop-One Marginal R^2

## Purpose

Track time variation in model fit and approximate factor-block contribution.

## Inputs

Stationary feature panel and 180-day rolling windows.

## Method

Fit rolling OLS, then drop one regressor at a time and measure the increase in
RSS relative to TSS.

## Outputs

`rolling_ols_btc_180d.csv`, `rolling_ols_eth_180d.csv`, and stacked figures.

## Interpretation

Drop-one marginal R^2 is conditional on the full model and correlated
regressors. It is not Shapley/Owen fair attribution.

## Risks

Correlated features can make marginal attribution unstable.

## Upgrade Path

Add Shapley/Owen attribution as an appendix and compare it against the current
drop-one marginal R^2 outputs before promoting any new attribution language.
""",
        "structural_breaks.md": """
# Model Card - Structural-Break Diagnostics

## Purpose

Test whether ETF launch dates align with detectable coefficient instability and
scan for single unknown break dates.

## Inputs

BTC/ETH returns and selected macro/institutional regressors.

## Method

Chow tests at pre-registered ETF dates plus single-break sup-F sweeps with
placebo inference.

## Outputs

`structural_breaks_summary.csv`, `sup_f_series_btc.csv`, and
`sup_f_series_eth.csv`.

## Interpretation

Regime diagnostic only. Current implementation is not Bai-Perron multi-break.

## Risks

Low power around noisy events, multiple testing, and model-dependence.

## Upgrade Path

Add a full Bai-Perron multi-break estimator only with tested assumptions,
simulation checks, and clear separation from the current Chow/sup-F diagnostics.
""",
        "var_fevd_connectedness.md": """
# Model Card - VAR/FEVD Connectedness

## Purpose

Summarize dynamic connectedness between BTC, ETH, equities, volatility, and
liquidity proxies.

## Inputs

Stationary feature columns selected by `scripts/02_run_analyses.py`.

## Method

statsmodels VAR with BIC lag selection and 10-day FEVD.

## Outputs

`fevd_10d_compact.csv`, `fevd_10d.csv`, and FEVD heatmaps.

## Interpretation

Connectedness diagnostics under the declared variable ordering.

## Risks

Ordering sensitivity, non-structural shocks, and unstable small systems.

## Upgrade Path

Add generalized FEVD or ordering-sensitivity tables before making stronger
connectedness claims.
""",
        "event_studies.md": """
# Model Card - Event Studies

## Purpose

Compare abnormal BTC/ETH returns around ETF launches and selected market events.

## Inputs

Daily log returns for BTC/ETH and SPY market-model benchmark.

## Method

Market-model abnormal returns over event windows with placebo p-values.

## Outputs

`event_studies.csv` and `event_study_cars.png`.

## Interpretation

Event-window association. Not causal proof of event impact.

## Risks

Confounding news, overlapping shocks, crypto 24/7 calendar differences, and
limited sample size.

## Upgrade Path

Add alternative market benchmarks and wider placebo batteries before using event
windows as stronger evidence.
""",
    }


def write_model_cards() -> None:
    for name, body in model_cards().items():
        write_text(PORTFOLIO_MODEL_CARDS_DIR / name, body)


def write_reports(inputs: PortfolioInputs) -> None:
    write_text(PORTFOLIO_DIR / "executive_summary.md", build_executive_summary(inputs))
    write_text(PORTFOLIO_DIR / "technical_report.md", build_technical_report(inputs))
    write_text(PORTFOLIO_DIR / "data_atlas.md", build_data_atlas(inputs))
    write_text(PORTFOLIO_DIR / "manager_report.md", build_manager_report(inputs))
    write_text(PORTFOLIO_DIR / "resume_bullets.md", build_resume_bullets(inputs))
    write_model_cards()


def write_manifest(inputs: PortfolioInputs) -> None:
    commands_run = [
        "uv sync --all-extras",
        "uv run pytest",
        "uv run mypy src/cqresearch",
        "uv run python scripts/run_full_pipeline.py",
        "uv run python scripts/run_portfolio_pipeline.py",
        (
            "uv run ruff check scripts/run_portfolio_pipeline.py "
            "tests/unit/test_portfolio_pipeline.py "
            "src/cqresearch/analysis/__init__.py "
            "src/cqresearch/modeling/__init__.py "
            "src/cqresearch/data/panel_builder.py"
        ),
    ]
    manifest = {
        "generated_at_utc": datetime.now(UTC).isoformat(),
        "table_source": str(inputs.table_dir.relative_to(ROOT)),
        "table_source_date": inputs.table_dir.name,
        "figure_source": str(inputs.figure_dir.relative_to(ROOT)),
        "figure_source_date": inputs.figure_dir.name,
        "portfolio_dir": str(PORTFOLIO_DIR.relative_to(ROOT)),
        "commands_run": commands_run,
        "panel": {
            "start": inputs.panel_meta["start"],
            "end": inputs.panel_meta["end"],
            "n_rows": inputs.panel_meta["n_rows"],
            "n_cols": inputs.panel_meta["n_cols"],
        },
        "copied_tables": TABLES_TO_COPY,
        "copied_figures": list(FIGURES_TO_COPY.values()),
    }
    path = PORTFOLIO_DIR / "manifest.json"
    path.write_text(json.dumps(manifest, indent=2), encoding="utf-8")
    print(f"[ok] wrote {path}")


def run() -> PortfolioInputs:
    ensure_portfolio_dirs()
    inputs = load_inputs()
    copy_artifacts(inputs)
    write_reports(inputs)
    write_manifest(inputs)
    return inputs


def main() -> int:
    try:
        inputs = run()
    except Exception as exc:
        print(f"[FAIL] portfolio pipeline: {exc}")
        return 1

    print("[ok] portfolio_v2 complete")
    print(f"[ok] table source: {inputs.table_dir}")
    print(f"[ok] figure source: {inputs.figure_dir}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
