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
        "executive_summary.md": """
# Executive Summary

Crypto Market Factor Lab is a reproducible Python analytics system for BTC/ETH
factor regimes, ETF-flow market plumbing, stablecoin liquidity, cross-asset
connectedness, and crypto-native market structure.

The canonical public artifact packet lives under `outputs/`. It uses a frozen
daily panel from 2020-01-01 through 2026-04-11 with 2,293 rows and 63 columns.
The frozen-data design keeps the project reproducible and avoids paid or live
data dependencies for public review.

## Headline Results

- BTC model fit is heavily influenced by native valuation and flow-state
  variables, especially MVRV-style valuation state. MVRV is separated from
  non-MVRV native variables because it can mechanically co-move with returns.
- ETF-flow intensity has strong same-day association with BTC and ETH returns,
  but daily data cannot identify causal flow impact. The evidence is framed as
  market-plumbing and lead-lag diagnostics.
- Rolling correlations show time-varying integration between BTC, ETH, TradFi,
  rates, and volatility variables.
- Stablecoin supply and DeFi TVL are useful liquidity context, not identified
  liquidity shocks.
- Structural-break diagnostics are Chow tests and single-break sup-F sweeps,
  not full multiple-break Bai-Perron estimation.
- Advanced diagnostics include PCA compression, exact block Shapley R2,
  exploratory CUSUM, FEVD-order sensitivity, rolling connectedness, and a BTC
  robustness grid.
""",
        "technical_report.md": """
# Technical Report

## Data Contract

The project uses a frozen 2020-01-01 to 2026-04-11 daily panel with 2,293 rows
and 63 columns. Inputs combine curated crypto, macro, ETF-flow, stablecoin,
DeFi, sentiment, and on-chain sources. Raw files under `Data/` are not modified
by the canonical export pipeline.

## Feature Engineering

Price-like series are transformed into log returns. Rates, spreads, sentiment,
and native levels use first differences. ETF-flow intensity is daily USD ETF
flow divided by prior-day USD market capitalization. Realized volatility uses a
30-day annualized rolling standard deviation of crypto returns.

## Models And Diagnostics

- HAC OLS for reduced-form factor exposure.
- Full-vs-reduced block partial R2 for block attribution.
- ETF and stablecoin lead-lag regressions with explicit lag convention.
- Rolling cross-asset correlations and pre/post event deltas.
- Stablecoin supply, DeFi TVL, and realized-volatility diagnostics.
- BTC-native factor registry and ablations with MVRV separated.
- Chow tests and single-break sup-F scans for structural-break diagnostics.
- VAR/FEVD connectedness and event-study CAR summaries.
- Advanced diagnostics: PCA blocks, exact block Shapley R2, exploratory CUSUM,
  FEVD-order sensitivity, rolling connectedness, and BTC robustness grid.

## Interpretation

All outputs are reduced-form diagnostics. The project uses language such as
association, exposure, market plumbing, contribution, sensitivity, and regime
diagnostics. It does not claim ETF flows caused BTC or ETH returns.
""",
        "methodology.md": """
# Methodology

## Feature Construction

The panel standardizes heterogeneous daily data into returns, differences,
intensity ratios, rolling volatility, and event-aligned variables. ETF-flow
intensity is scaled by prior-day USD market capitalization to make flow
magnitudes comparable through time.

## Factor Exposure

Static models use HAC OLS to estimate reduced-form associations between BTC/ETH
returns and factor families. Results are not structural shocks or causal
effects.

## Attribution

Canonical block attribution is full-vs-reduced block partial R2. It measures the
loss in explanatory power when a block is removed from the full model. Advanced
attribution includes exact block Shapley R2 over the chosen block design.

## Lead-Lag

Lead-lag tables use the convention `lag < 0` means the explanatory series is
shifted earlier and leads the target return. Daily sequencing remains
simultaneity-prone.

## Regimes And Connectedness

Rolling correlations, Chow tests, single-break sup-F scans, VAR/FEVD tables,
and event studies are descriptive regime and connectedness diagnostics.
""",
        "data_atlas.md": """
# Data Atlas

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
under `Data/`.
""",
        "limitations.md": """
# Limitations

- Daily data cannot identify intraday market mechanisms or order flow.
- ETF-flow, stablecoin, and native-factor results are reduced-form diagnostics,
  not causal identification.
- Stablecoin supply and TVL are liquidity proxies, not proven liquidity shocks.
- Structural-break diagnostics use Chow tests and single-break sup-F sweeps,
  not full Bai-Perron multiple-break estimation.
- Block partial R2 and exact Shapley R2 depend on block definitions and the
  selected feature set.
- Frozen data supports reproducibility but is not a live market monitor.
- Broad repository linting still includes legacy files; maintained public
  surfaces use focused Ruff, mypy, and pytest checks.
""",
        "reorganization_summary.md": """
# Reorganization Summary

## What Changed

The repository was consolidated from a release-history layout into one clean
public project:

- `outputs/` is the canonical public artifact packet.
- `docs/` contains concise methodology, architecture, data, and decision docs.
- `archive/` retains internal manager notes, historical release packets, old
  drafts, career-oriented material, and release-process documents.
- `reports/` keeps compatibility generated tables, figures, and panel metadata
  used by legacy scripts.

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
- Structural-break diagnostics remain Chow plus single-break sup-F, not full
  Bai-Perron.
- Advanced attribution is labeled separately from block partial R2.
""",
    }


def outputs_readme() -> str:
    return """
# Canonical Outputs

`outputs/` is the canonical public artifact packet for Crypto Market Factor
Lab. Historical release packets and internal planning material live under
`archive/`.

## Reports

- `report/executive_summary.md`
- `report/technical_report.md`
- `report/methodology.md`
- `report/data_atlas.md`
- `report/limitations.md`
- `report/reorganization_summary.md`

## Figures

- `figures/F01_data_coverage.png`
- `figures/F02_btc_block_attribution.png`
- `figures/F03_btc_etf_lead_lag.png`
- `figures/F04_btc_rolling_correlations.png`
- `figures/F05_stablecoin_supply_tvl.png`
- `figures/F06_btc_native_dashboard.png`
- `figures/F07_connectedness.png`
- `figures/F08_robustness_grid.png`

## Tables

- `tables/T01_source_inventory.csv`
- `tables/T02_panel_coverage.csv`
- `tables/T03_block_attribution.csv`
- `tables/T04_etf_lead_lag.csv`
- `tables/T05_correlation_regime.csv`
- `tables/T06_stablecoin_liquidity.csv`
- `tables/T07_native_factor_ablation.csv`
- `tables/T08_structural_breaks.csv`
- `tables/T09_connectedness.csv`
- `tables/T10_robustness.csv`

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


def export_figures(v21: Path, v22: Path) -> list[dict[str, str]]:
    mappings = [
        (v21 / "figures" / "F62_baseline_data_coverage.png", "F01_data_coverage.png"),
        (v21 / "figures" / "F10_btc_block_partial_r2_heatmap.png", "F02_btc_block_attribution.png"),
        (v21 / "figures" / "F22_btc_etf_lead_lag_heatmap.png", "F03_btc_etf_lead_lag.png"),
        (v21 / "figures" / "F30_btc_rolling_correlations_180d.png", "F04_btc_rolling_correlations.png"),
        (v21 / "figures" / "F40_stablecoin_supply_and_tvl.png", "F05_stablecoin_supply_tvl.png"),
        (v21 / "figures" / "F50_btc_native_zscore_dashboard.png", "F06_btc_native_dashboard.png"),
        (v22 / "figures" / "F77_rolling_connectedness.png", "F07_connectedness.png"),
        (v22 / "figures" / "F78_robustness_grid_heatmap.png", "F08_robustness_grid.png"),
    ]
    return [copy_file(src, OUTPUTS / "figures" / dst) for src, dst in mappings]


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
        copy_file(v22 / "tables" / "robustness_grid.csv", OUTPUTS / "tables" / "T10_robustness.csv"),
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
    readme = """
# Data Catalog

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
    v21 = find_packet("portfolio_v2_1")
    v22 = find_packet("portfolio_v2_2")

    for subdir in ["report", "figures", "tables", "model_cards"]:
        (OUTPUTS / subdir).mkdir(parents=True, exist_ok=True)

    reports = export_reports()
    figures = export_figures(v21, v22)
    tables = export_tables(v21, v22)
    model_cards = export_model_cards(v21, v22)
    data_catalog = export_data_catalog()
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
