"""Export the canonical public artifact packet under outputs/.

This script does not run new analysis and does not touch raw Data/. It copies
the strongest tracked artifacts from the maintained release packets into a
single public layout, then writes clean reports, model cards, and a manifest.
"""

from __future__ import annotations

import csv
import json
import shutil
import subprocess
from datetime import UTC, datetime
from pathlib import Path

from scripts.make_hero_figures import render_all_figures

ROOT = Path(__file__).resolve().parents[1]
OUTPUTS = ROOT / "outputs"
PANEL_META = {"start": "2020-01-01", "end": "2026-04-11", "n_rows": 2293, "n_cols": 63}


def find_packet(name: str) -> Path:
    candidates = [
        ROOT / "reports" / name,
        ROOT / "archive" / "legacy_portfolio_releases" / name,
    ]
    for candidate in candidates:
        if candidate.exists():
            return candidate
    raise FileNotFoundError(f"Could not find source packet {name!r}")


def rel(path: Path) -> str:
    if any(part.startswith("portfolio_v2") for part in path.parts):
        return f"archived_release_artifact/{path.parent.name}/{path.name}"
    return path.relative_to(ROOT).as_posix()


def copy_file(src: Path, dst: Path) -> dict[str, str]:
    if not src.exists():
        raise FileNotFoundError(src)
    dst.parent.mkdir(parents=True, exist_ok=True)
    shutil.copy2(src, dst)
    return {"source": rel(src), "output": rel(dst)}


def combine_csv(sources: list[Path], dst: Path) -> dict[str, object]:
    dst.parent.mkdir(parents=True, exist_ok=True)
    rows_written = 0
    header: list[str] | None = None
    with dst.open("w", newline="", encoding="utf-8") as out_f:
        writer = csv.writer(out_f)
        for src in sources:
            if not src.exists():
                raise FileNotFoundError(src)
            with src.open(newline="", encoding="utf-8") as in_f:
                reader = csv.reader(in_f)
                src_header = next(reader)
                if header is None:
                    header = src_header
                    writer.writerow(header)
                elif src_header != header:
                    raise ValueError(f"Cannot combine mismatched CSV headers: {src}")
                for row in reader:
                    writer.writerow(row)
                    rows_written += 1
    return {"sources": [rel(src) for src in sources], "output": rel(dst), "rows": rows_written}


def write_csv(path: Path, header: list[str], rows: list[list[object]]) -> dict[str, object]:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)
        writer.writerow(header)
        writer.writerows(rows)
    return {"source": "generated from frozen panel metadata", "output": rel(path), "rows": len(rows)}


def sanitize_card(text: str) -> str:
    replacements = {
        "Portfolio v2.1": "Crypto Market Factor Lab",
        "Portfolio v2.2": "Crypto Market Factor Lab",
        "baseline v2 bundle": "baseline bundle",
        "Baseline v2": "Baseline",
        "portfolio v2.1": "canonical public output",
        "portfolio v2.2": "advanced diagnostics",
        "v2.1": "canonical",
        "v2.2": "advanced diagnostics",
        "reports/portfolio_v2_1": "outputs",
        "reports/portfolio_v2_2": "outputs",
        "reports\\portfolio_v2_1": "outputs",
        "reports\\portfolio_v2_2": "outputs",
        "resume": "project",
        "Resume": "Project",
        "interview": "review",
        "Interview": "Review",
        "recruiter": "reviewer",
        "Recruiter": "Reviewer",
        "LinkedIn": "public",
    }
    for old, new in replacements.items():
        text = text.replace(old, new)
    return text


def write_text(path: Path, text: str) -> dict[str, str]:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text.strip() + "\n", encoding="utf-8")
    return {"source": "generated canonical narrative", "output": rel(path)}


def git_commit() -> str:
    try:
        return subprocess.check_output(
            ["git", "rev-parse", "--short", "HEAD"], cwd=ROOT, text=True
        ).strip()
    except Exception:
        return "unknown"


def report_texts() -> dict[str, str]:
    return {
        "executive_summary.md": """# Executive Summary

The Crypto Market Factor Lab evaluates the factors explaining BTC and ETH returns using a frozen daily panel from 2020-01-01 through 2026-04-11 (2,293 observations, 63 features). The primary objective is to separate structural price co-movements (valuation state) from exogenous risk factors (macro, liquidity, TradFi) and market-plumbing elements (ETF flows).

## Core Findings

1. **MVRV Dominance & Valuation-State Sensitivity**
   - The full BTC model achieves an $R^2 \\approx 0.921$, but removing the BTC MVRV block collapses the reduced model's fit to $R^2 \\approx 0.146$.
   - The block partial $R^2$ ($\\Delta R^2$) for MVRV is $0.775$. Standalone, an MVRV-only model yields $R^2 \\approx 0.912$. This indicates that the high model fit is not a broad factor structure but is almost entirely driven by the first-differenced MVRV valuation-state variable, which has a $0.955$ daily correlation with BTC returns.

2. **Native ex-MVRV Features**
   - Daily crypto-native flow and structure variables—such as CME futures basis (`cme_btc_basis_close_d1`), exchange netflow (`btc_exchange_netflow_d1`), and miner-to-exchange flows (`btc_miner_to_exchange_flow_d1`)—exhibit near-zero contemporaneous correlation with BTC returns.
   - Standardized OLS coefficients and standalone regressions yield $R^2 \\approx 0.0037$ for these variables. This confirms that daily native flows (excluding MVRV) do not explain daily returns in a linear same-day specification.

3. **ETF Flow Plumbing & Timing**
   - ETF-flow intensity is strongly associated with same-day returns ($t\\text{-stat} \\approx 10.22$, standalone $R^2 \\approx 0.271$). However, negative lags (excluding lag -1) are weak, and lag +1 is also strong, highlighting that this association represents contemporaneous market-plumbing co-movement rather than predictive ex-ante causality.

4. **Regime and Temporal Stability**
   - MVRV dominance persists across regimes but exhibits temporal shifts. In the post-ETF era (2024–2026), MVRV's standalone explanatory power is still dominant but declines slightly as TradFi integration and ETF flow associations grow.
   - Realized volatility regimes (high vs. low vol quartiles) show that macro and TradFi risk exposures are regime-dependent, with stronger TradFi betas observed during low-volatility regimes.

5. **Analytical Infrastructure & Same-Support Comparisons**
   - In previous iterations, model comparisons were biased by varying sample sizes (differing $n$). The new implementation introduces same-support ablation tables ($T19$ and $T20$), ensuring all model combinations are estimated on identical observation samples to guarantee apples-to-apples comparisons.""",
        "technical_report.md": """# Technical Report

## Data Pipeline and Sample Support
The data foundation is a frozen daily panel spanning 2020-01-01 to 2026-04-11 ($n = 2,293$). The database combines Artemis, CryptoQuant, DefiLlama, FRED, and TradingView series.
To address sample-composition bias (differing $n$ across models due to feature missingness), the analysis implements a Same-Support constraint. Standalone, full, and ablated models are evaluated on a common support ($n = 1,940$ for BTC, $n = 794$ for ETH) to ensure valid statistical comparisons.

## Model Formulation
Linear modeling uses Ordinary Least Squares (OLS) with Heteroskedasticity and Autocorrelation Consistent (HAC) standard errors (Newey-West with automatic lag selection) to handle serial correlation and heteroskedasticity.

### 1. Static Exposure Model
$$r_t = \\alpha + \\sum_j \\beta_j F_{j, t} + \\epsilon_t$$
where $r_t$ represents the asset return, and $F_{j, t}$ are stationary factor differences (log returns for prices, first differences for rates/spreads/levels, and scaled ratios for flows).

### 2. Full vs. Reduced Block Attribution
Block partial $R^2$ is defined as:
$$\\text{Partial } R^2_{\\text{Block}} = R^2_{\\text{Full}} - R^2_{\\text{Reduced (ex-Block)}}$$
which measures the incremental contribution of a group of variables conditional on all other features being present.

### 3. Ex-MVRV Benchmark
To evaluate macro, TradFi, and liquidity factors without the dominance of the near-price MVRV state variable, we run an Ex-MVRV factor model:
$$r_t = \\alpha + \\sum_{k \\neq \\text{MVRV}} \\beta_k F_{k, t} + \\epsilon_t$$

## Key Diagnostic Outputs

### 1. Feature Strength Tables (T14 - T17)
These tables report individual feature statistics including Pearson correlation, absolute correlation rank, standardized multivariate OLS coefficients ($\\beta$), HAC $t$-stats, $p$-values, and drop-one $\\Delta R^2$.

### 2. Same-Support Ablation (T19 - T20)
Provides sequential and block-based R² ladders, illustrating model performance from intercept-only up to the full factor stack.

### 3. Regime Sensitivity (T25)
Decomposes the explanatory power of MVRV vs. ex-MVRV models across different regimes:
- Pre-ETF ($n = 1,471$) vs. Post-ETF ($n = 822$)
- Yearly sub-samples (2020 through 2026 YTD)
- Realized Volatility Quartiles (High vs. Low Volatility)

## Results and Interpretation
- **MVRV Dominance**: In the full sample, MVRV-only yields $R^2 \\approx 0.912$, and its block partial $R^2$ is $0.775$. Its explanatory dominance remains high but shifts down in 2025-2026, indicating changing market structure.
- **Ex-MVRV Performance**: Without MVRV, the combined macro, TradFi, liquidity, and sentiment blocks explain only $\\approx 14.6\\%$ of daily BTC return variance. TradFi and ETF flow intensity are the primary contributors in this subset.
- **Daily Plumbing vs. Prediction**: ETF flows exhibit a contemporaneous association ($t = 10.22$), but lead-lag diagnostic regressions indicate that lagged flows have minimal predictive power, consistent with daily plumbing and inventory adjustment rather than lead-lag signaling.""",
        "methodology.md": """# Methodology

## 1. Feature Construction & Stationarity
To avoid spurious regressions, all non-stationary series are transformed:
- **Price series** (BTC, ETH, SPY, QQQ, GLD): Log differences ($r_t = \\ln(P_t) - \\ln(P_{t-1})$).
- **Yields, Spreads, Sentiment, and On-chain Levels** (DGS10, DGS2, VIX, MVRV, Exchange Netflow, Miner-to-Exchange flow): First differences ($\\Delta X_t = X_t - X_{t-1}$).
- **ETF-Flow Intensity**: Scaled as daily net USD flow divided by prior-day total asset market capitalization. This normalizes flow magnitudes relative to the growing scale of the market.

## 2. Regime Definitions (`src/cqresearch/analysis/regimes.py`)
To analyze structural shifts through time and conditions, we define the following boolean masks over the dataset:
- **Temporal Regimes**:
  - `full`: 2020-01-01 to 2026-04-11
  - `pre_btc_etf`: dates before 2024-01-11
  - `post_btc_etf`: dates on or after 2024-01-11
  - `post_eth_etf`: dates on or after 2024-07-23
  - `year_2020` through `year_2026_ytd`
- **Volatility Regimes**:
  - `high_vol`: Days in the top quartile of rolling 30-day annualized realized volatility.
  - `low_vol`: Days in the bottom quartile of rolling 30-day annualized realized volatility.

## 3. Statistical Diagnostic Framework
- **HAC OLS Regressions**: OLS models are estimated using Newey-West standard errors. This corrects for autocorrelation and heteroskedasticity in daily financial time series.
- **Univariate vs. Multivariate Feature Strength**:
  - *Univariate*: Static correlation and standalone single-variable regressions.
  - *Multivariate*: Standardized betas (coefficients estimated after standardizing variables to unit variance, allowing direct magnitude comparison) and drop-one $\\Delta R^2$.
- **Same-Support Ablation Constraint**:
  - When comparing models (e.g., full model vs. ex-MVRV model vs. native-only model), any rows containing missing data in any feature of the *full model* are dropped across *all* compared models. This forces estimation on an identical sample $S$, ensuring differences in $R^2$ reflect feature information, not sample composition.

## 4. Connectedness and Spillovers
Cross-asset connectedness uses a Vector Autoregressive (VAR) model framework. The system estimates daily Forecast Error Variance Decompositions (FEVD) to compute the Directional Connectedness Index (DCI) and Net Spillover effects among core market segments.""",
        "data_atlas.md": """# Data Atlas

| Source | Role |
|---|---|
| CryptoQuant | BTC/ETH native, on-chain, market-structure indicators |
| Farside ETF Data | BTC and ETH ETF flows |
| DefiLlama | TVL, stablecoin, and DeFi liquidity context |
| FRED | Macro, rates, dollar, and volatility variables |
| TradingView | Cross-asset market data |
| Artemis | ETF, DeFi, and chain context |
| AlternativeMe | Fear and Greed sentiment |

Panel range: 2020-01-01 through 2026-04-11.

Panel shape: 2,293 daily rows and 63 columns.

The clean public catalog is in `data/catalog/`. The frozen source files remain
under `Data/`.""",
        "limitations.md": """# Limitations & Methodological Caveats

## 1. Contemporaneous vs. Predictive (Lagged) Models
The baseline static OLS and block-attribution models are contemporaneous exposure diagnostics. They measure co-movement, not predictive power. While useful for risk decomposition and hedging analysis, they cannot be used directly for forecasting. Lagged predictive diagnostic models (where features are lagged by one day) show significantly lower explanatory power, demonstrating that the contemporaneous relationships are driven by same-day market-clearing mechanisms.

## 2. MVRV Interpretation Risks
MVRV (Market Value to Realized Value) is a ratio constructed as:
$$\\text{MVRV} = \\frac{\\text{Market Capitalization}}{\\text{Realized Capitalization}}$$
Since the numerator is current market price times supply, the first difference of MVRV ($\\Delta \\text{MVRV}_t$) is highly correlated with price returns ($r_t$) by construction ($r \\approx 0.955$).
- **Risk**: Treating MVRV as a standard independent factor (like interest rates or GDP growth) is invalid. It is a valuation-state proxy.
- **Mitigation**: The project explicitly separates MVRV from other native variables and presents an independent "Ex-MVRV" model family to evaluate macro and liquidity factors cleanly.

## 3. ETF-Flow Causal Interpretation
ETF-flow intensity shows a high same-day association with BTC returns. Daily data cannot identify the direction of causality. ETF flows could be driving price appreciation, or momentum/intraday price action could be driving ETF subscriptions (feedback loop). 
- **Risk**: Interpreting OLS coefficients as causal impact (e.g., "an inflow of $\\$100\\text{M}$ causes a $1\\%$ rise") is statistically incorrect. It represents market-plumbing co-movement.
- **Mitigation**: Lead-lag regressions demonstrate that lag +1 (returns leading ETF flows) is statistically significant, supporting the feedback loop hypothesis.

## 4. Liquidity Proxies vs. Shocks
Stablecoin supply changes and DeFi TVL growth are slow-moving liquidity indicators. In a daily regression framework, they behave as lagging context rather than contemporaneous or leading price drivers.

## 5. Structural Breaks and sweeps
Chow tests and sup-F sweeps sweep for a single structural break. They do not estimate multi-break Bai-Perron models.

## 6. Data Replicability Constraint
The project relies on a frozen database (2020-01-01 to 2026-04-11). It is not a live trading dashboard and does not capture structural changes occurring after April 2026.""",
        "reorganization_summary.md": """# Reorganization Summary

## What Changed

The repository was consolidated from a release-history layout into one clean public project:

- `outputs/` is the canonical public artifact packet.
- `docs/` contains concise methodology, architecture, data, and decision docs.
- `archive/` retains internal manager notes, historical release packets, old drafts, and release-process documents.
- `reports/` keeps compatibility generated tables, figures, and panel metadata used by legacy scripts.

## Public Structure

```text
README.md
Data/
docs/
outputs/
scripts/
src/cqresearch/
tests/
archive/
```

## Guardrails

- Raw `Data/` files are not modified by the canonical export path.
- ETF-flow outputs remain reduced-form diagnostics, not causal claims.
- Stablecoin and TVL outputs remain liquidity proxies.
- Structural-break diagnostics remain Chow plus single-break sup-F, not full Bai-Perron.
- Advanced attribution is labeled separately from block partial R2.
- The new Feature Strength & Regime Analysis tables (T11-T27) and figures (F01-F08) are fully integrated into the public analytical surface.""",
    }


def outputs_readme() -> str:
    return """# Canonical Outputs

`outputs/` is the canonical public artifact packet for Crypto Market Factor Lab. Historical release packets and internal planning material live under `archive/`.

## Reports

- `report/executive_summary.md`
- `report/technical_report.md`
- `report/methodology.md`
- `report/data_atlas.md`
- `report/limitations.md`
- `report/reorganization_summary.md`

## Figures

- `figures/F01_mvrv_sensitivity_by_regime_v2.png`
- `figures/F02_same_support_ablation.png`
- `figures/F03_btc_ex_mvrv_strength.png`
- `figures/F04_etf_flow_lead_lag.png`
- `figures/F05_core_correlation_matrix.png`
- `figures/F06_rolling_correlations.png`
- `figures/F07_feature_strength_heatmap.png`
- `figures/F08_connectedness_robustness.png`
- `figures/gallery/G01_native_state_detail.png`
- `figures/gallery/G02_liquidity_context.png`

## Tables

- `tables/README.md`
- `tables/T01_source_inventory.csv`
- `tables/T02_panel_coverage.csv`
- `tables/T03_block_attribution.csv`
- `tables/T03_rolling_block_partial_r2_btc_180d.csv`
- `tables/T04_etf_lead_lag.csv`
- `tables/T05_correlation_regime.csv`
- `tables/T05_rolling_correlations.csv`
- `tables/T06_stablecoin_liquidity.csv`
- `tables/T07_native_factor_ablation.csv`
- `tables/T07_native_factor_registry.csv`
- `tables/T07_btc_native_correlations.csv`
- `tables/T08_structural_breaks.csv`
- `tables/T09_connectedness.csv`
- `tables/T09_rolling_connectedness.csv`
- `tables/T10_robustness.csv`
- `tables/T11_results_at_a_glance.md`
- `tables/T12_regime_definitions.csv`
- `tables/T13_factor_dictionary.md`
- `tables/T13_factor_dictionary.csv`
- `tables/T14_feature_strength_btc_full.csv`
- `tables/T15_feature_strength_btc_ex_mvrv.csv`
- `tables/T16_feature_strength_eth.csv`
- `tables/T17_feature_strength_by_regime.csv`
- `tables/T18_block_strength_by_regime.csv`
- `tables/T19_same_support_ablation_btc.csv`
- `tables/T20_same_support_ablation_eth.csv`
- `tables/T21_top_correlations_btc.csv`
- `tables/T22_top_correlations_eth.csv`
- `tables/T23_core_correlation_matrix.csv`
- `tables/T24_pre_post_correlation_delta.csv`
- `tables/T25_mvrv_sensitivity_by_regime.csv`
- `tables/T26_etf_era_feature_strength.csv`
- `tables/T27_rolling_feature_rank_stability.csv`

## Dashboard

- `dashboard/index.html`

## Reproduce

```powershell
uv sync --all-extras
uv run pytest
uv run mypy src/cqresearch
uv run python scripts/run_all.py
```
"""


def export_reports() -> list[dict[str, str]]:
    outputs = []
    for filename, text in report_texts().items():
        outputs.append(write_text(OUTPUTS / "report" / filename, text))
    outputs.append(write_text(OUTPUTS / "README.md", outputs_readme()))
    return outputs


def export_figures() -> list[dict[str, str]]:
    rendered = render_all_figures()
    figure_paths = [
        path
        for path in rendered
        if path.is_relative_to(OUTPUTS / "figures") and path.suffix.lower() in {".png", ".svg"}
    ]
    return [
        {
            "source": "generated from canonical output tables and archived supplemental tables",
            "output": rel(path),
        }
        for path in sorted(figure_paths)
    ]


def export_tables(v21: Path, v22: Path) -> list[dict[str, object]]:
    tables = [
        copy_file(ROOT / "Data" / "MASTER_DATA.csv", OUTPUTS / "tables" / "T01_source_inventory.csv"),
        write_csv(
            OUTPUTS / "tables" / "T02_panel_coverage.csv",
            ["start", "end", "n_rows", "n_cols", "frequency", "data_policy"],
            [[PANEL_META["start"], PANEL_META["end"], PANEL_META["n_rows"], PANEL_META["n_cols"], "daily", "frozen"]],
        ),
        combine_csv(
            [
                v21 / "tables" / "block_partial_r2_btc.csv",
                v21 / "tables" / "block_partial_r2_eth.csv",
            ],
            OUTPUTS / "tables" / "T03_block_attribution.csv",
        ),
        combine_csv(
            [v21 / "tables" / "etf_lead_lag_btc.csv", v21 / "tables" / "etf_lead_lag_eth.csv"],
            OUTPUTS / "tables" / "T04_etf_lead_lag.csv",
        ),
        combine_csv(
            [
                v21 / "tables" / "correlation_delta_pre_post_btc_etf.csv",
                v21 / "tables" / "correlation_delta_pre_post_eth_etf.csv",
            ],
            OUTPUTS / "tables" / "T05_correlation_regime.csv",
        ),
        copy_file(
            v21 / "tables" / "stablecoin_liquidity_features.csv",
            OUTPUTS / "tables" / "T06_stablecoin_liquidity.csv",
        ),
        copy_file(
            v21 / "tables" / "btc_native_ablation.csv",
            OUTPUTS / "tables" / "T07_native_factor_ablation.csv",
        ),
        copy_file(
            v21 / "tables" / "baseline_structural_breaks_summary.csv",
            OUTPUTS / "tables" / "T08_structural_breaks.csv",
        ),
        copy_file(
            v21 / "tables" / "baseline_fevd_10d_compact.csv",
            OUTPUTS / "tables" / "T09_connectedness.csv",
        ),
        copy_file(
            v21 / "tables" / "rolling_block_partial_r2_btc_180d.csv",
            OUTPUTS / "tables" / "T03_rolling_block_partial_r2_btc_180d.csv",
        ),
        copy_file(
            v21 / "tables" / "rolling_correlations.csv",
            OUTPUTS / "tables" / "T05_rolling_correlations.csv",
        ),
        copy_file(
            v21 / "tables" / "native_factor_registry.csv",
            OUTPUTS / "tables" / "T07_native_factor_registry.csv",
        ),
        copy_file(
            v21 / "tables" / "btc_native_correlations.csv",
            OUTPUTS / "tables" / "T07_btc_native_correlations.csv",
        ),
        copy_file(
            v22 / "tables" / "rolling_connectedness.csv",
            OUTPUTS / "tables" / "T09_rolling_connectedness.csv",
        ),
        copy_file(v22 / "tables" / "robustness_grid.csv", OUTPUTS / "tables" / "T10_robustness.csv"),
        
        # New Feature Strength and Regime Analysis Tables
        {"source": "generated by scripts/06_feature_strength.py", "output": "outputs/tables/T11_results_at_a_glance.md"},
        {"source": "generated by scripts/06_feature_strength.py", "output": "outputs/tables/T12_regime_definitions.csv"},
        {"source": "generated by scripts/06_feature_strength.py", "output": "outputs/tables/T13_factor_dictionary.md"},
        {"source": "generated by scripts/06_feature_strength.py", "output": "outputs/tables/T13_factor_dictionary.csv"},
        {"source": "generated by scripts/06_feature_strength.py", "output": "outputs/tables/T14_feature_strength_btc_full.csv"},
        {"source": "generated by scripts/06_feature_strength.py", "output": "outputs/tables/T15_feature_strength_btc_ex_mvrv.csv"},
        {"source": "generated by scripts/06_feature_strength.py", "output": "outputs/tables/T16_feature_strength_eth.csv"},
        {"source": "generated by scripts/06_feature_strength.py", "output": "outputs/tables/T17_feature_strength_by_regime.csv"},
        {"source": "generated by scripts/06_feature_strength.py", "output": "outputs/tables/T18_block_strength_by_regime.csv"},
        {"source": "generated by scripts/06_feature_strength.py", "output": "outputs/tables/T19_same_support_ablation_btc.csv"},
        {"source": "generated by scripts/06_feature_strength.py", "output": "outputs/tables/T20_same_support_ablation_eth.csv"},
        {"source": "generated by scripts/06_feature_strength.py", "output": "outputs/tables/T21_top_correlations_btc.csv"},
        {"source": "generated by scripts/06_feature_strength.py", "output": "outputs/tables/T22_top_correlations_eth.csv"},
        {"source": "generated by scripts/06_feature_strength.py", "output": "outputs/tables/T23_core_correlation_matrix.csv"},
        {"source": "generated by scripts/06_feature_strength.py", "output": "outputs/tables/T24_pre_post_correlation_delta.csv"},
        {"source": "generated by scripts/06_feature_strength.py", "output": "outputs/tables/T25_mvrv_sensitivity_by_regime.csv"},
        {"source": "generated by scripts/06_feature_strength.py", "output": "outputs/tables/T26_etf_era_feature_strength.csv"},
        {"source": "generated by scripts/06_feature_strength.py", "output": "outputs/tables/T27_rolling_feature_rank_stability.csv"},
    ]
    return tables


def export_model_cards(v21: Path, v22: Path) -> list[dict[str, str]]:
    mappings = [
        (v21 / "model_cards" / "static_ols.md", "factor_exposure.md"),
        (v21 / "model_cards" / "block_partial_r2.md", "block_attribution.md"),
        (v21 / "model_cards" / "etf_flow_lead_lag.md", "etf_flow_lead_lag.md"),
        (v21 / "model_cards" / "rolling_correlations.md", "rolling_correlations.md"),
        (v21 / "model_cards" / "stablecoin_liquidity.md", "stablecoin_liquidity.md"),
        (v21 / "model_cards" / "btc_native_factor_lab.md", "btc_native_factors.md"),
        (v21 / "model_cards" / "structural_breaks.md", "structural_breaks.md"),
        (v21 / "model_cards" / "var_fevd.md", "connectedness.md"),
        (v22 / "model_cards" / "shapley_r2.md", "advanced_attribution.md"),
        (v22 / "model_cards" / "robustness_grid.md", "robustness.md"),
    ]
    outputs = []
    for src, dst in mappings:
        if not src.exists():
            raise FileNotFoundError(src)
        text = sanitize_card(src.read_text(encoding="utf-8"))
        out = OUTPUTS / "model_cards" / dst
        out.parent.mkdir(parents=True, exist_ok=True)
        out.write_text(text.strip() + "\n", encoding="utf-8")
        outputs.append({"source": rel(src), "output": rel(out)})
    return outputs


def export_data_catalog() -> list[dict[str, str]]:
    catalog = ROOT / "docs" / "data" / "catalog"
    outputs = [
        copy_file(ROOT / "Data" / "MASTER_DATA.md", catalog / "MASTER_DATA.md"),
        copy_file(ROOT / "Data" / "MASTER_DATA.csv", catalog / "MASTER_DATA.csv"),
        copy_file(ROOT / "Data" / "_meta" / "curation_log.md", catalog / "curation_log.md"),
    ]
    readme = """# Data Catalog

This folder is the clean public entry point for the frozen data inventory. Raw
and curated source files remain under the historical `Data/` tree for backward
compatibility with existing scripts.

The canonical public output packet is `outputs/`.
"""
    outputs.append(write_text(ROOT / "docs" / "data" / "README.md", readme))
    return outputs


def write_manifest(
    figures: list[dict[str, str]],
    tables: list[dict[str, object]],
    reports: list[dict[str, str]],
    model_cards: list[dict[str, str]],
    data_catalog: list[dict[str, str]],
) -> None:
    manifest = {
        "generated_at_utc": datetime.now(UTC).isoformat(),
        "git_commit": git_commit(),
        "artifact_root": "outputs",
        "figure_bundle": {
            "style": "institutional_dark_research_cards",
            "generated_from": "canonical output tables plus archived supplemental tables",
            "export_formats": ["png", "svg"],
            "dashboard": "outputs/dashboard/index.html",
        },
        "panel": PANEL_META,
        "commands_to_reproduce": [
            "uv sync --all-extras",
            "uv run pytest",
            "uv run mypy src/cqresearch",
            "uv run python scripts/run_all.py",
        ],
        "figures": figures,
        "tables": tables,
        "reports": reports,
        "model_cards": model_cards,
        "dashboard": [
            {"source": "generated static dashboard", "output": "outputs/dashboard/index.html"}
        ],
        "data_catalog": data_catalog,
        "guardrails": [
            "Data/ is not modified by the canonical export pipeline.",
            "ETF-flow diagnostics are reduced-form association, not causal identification.",
            "Stablecoin and TVL features are liquidity proxies, not identified shocks.",
            "Structural-break diagnostics are Chow plus single-break sup-F, not full Bai-Perron.",
            "Block attribution is full-vs-reduced partial R2; exact Shapley R2 is labeled advanced diagnostics.",
            "Historical release packets and manager notes are archived outside the public surface.",
        ],
    }
    (OUTPUTS / "manifest.json").write_text(json.dumps(manifest, indent=2) + "\n", encoding="utf-8")


def main() -> int:
    # First regenerate new tables to ensure all new outputs exist before drawing and exporting
    print("Regenerating feature strength and regime tables...")
    subprocess.run(["uv", "run", "python", "scripts/06_feature_strength.py"], check=True)

    v21 = find_packet("portfolio_v2_1")
    v22 = find_packet("portfolio_v2_2")

    for subdir in ["report", "figures", "tables", "model_cards"]:
        (OUTPUTS / subdir).mkdir(parents=True, exist_ok=True)

    reports = export_reports()
    tables = export_tables(v21, v22)
    model_cards = export_model_cards(v21, v22)
    data_catalog = export_data_catalog()
    figures = export_figures()
    reports.extend(
        [
            {"source": "generated visual QA narrative", "output": "outputs/report/visual_audit.md"},
            {"source": "generated visual QA narrative", "output": "outputs/report/visual_quality_check.md"},
        ]
    )
    tables.extend(
        [
            {"source": "generated key-results presentation table", "output": "outputs/tables/README.md"},
        ]
    )
    write_manifest(figures, tables, reports, model_cards, data_catalog)

    print("[ok] canonical outputs exported")
    print(f"[ok] reports: {len(reports)}")
    print(f"[ok] figures: {len(figures)}")
    print(f"[ok] tables: {len(tables)}")
    print(f"[ok] model cards: {len(model_cards)}")
    print("[ok] manifest: outputs/manifest.json")
    return 0



if __name__ == "__main__":
    raise SystemExit(main())
