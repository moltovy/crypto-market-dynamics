"""Institutional visual design tokens for public research artifacts."""

from __future__ import annotations

from dataclasses import dataclass
from datetime import date

COLORS: dict[str, str] = {
    "bg": "#080B12",
    "surface": "#0F172A",
    "surface2": "#111827",
    "grid": "#243044",
    "axis": "#334155",
    "text": "#E5E7EB",
    "muted": "#94A3B8",
    "faint": "#64748B",
    "btc": "#F7931A",
    "eth": "#627EEA",
    "macro": "#60A5FA",
    "institutional": "#2DD4BF",
    "liquidity": "#22C55E",
    "stablecoin": "#10B981",
    "native": "#A78BFA",
    "risk": "#EF4444",
    "gold": "#FBBF24",
    "neutral": "#94A3B8",
    "positive": "#22C55E",
    "negative": "#EF4444",
    "white": "#FFFFFF",
}

FACTOR_COLORS: dict[str, str] = {
    "BTC ETF Flow": COLORS["institutional"],
    "ETH ETF Flow": COLORS["institutional"],
    "BTC MVRV": COLORS["native"],
    "ETH MVRV": COLORS["native"],
    "BTC Native ex MVRV": "#C084FC",
    "Native": COLORS["native"],
    "Macro": COLORS["macro"],
    "TradFi": COLORS["gold"],
    "Liquidity": COLORS["liquidity"],
    "Sentiment": COLORS["neutral"],
    "Risk": COLORS["risk"],
}

EVENTS: tuple[tuple[date, str, str], ...] = (
    (date(2022, 11, 8), "FTX", COLORS["risk"]),
    (date(2023, 3, 10), "SVB", COLORS["gold"]),
    (date(2024, 1, 11), "BTC ETF", COLORS["institutional"]),
    (date(2024, 4, 20), "Halving", COLORS["native"]),
    (date(2024, 7, 23), "ETH ETF", COLORS["eth"]),
)

FONT_FAMILY: list[str] = ["Inter", "Segoe UI", "DejaVu Sans", "Arial", "sans-serif"]
MONO_FONT_FAMILY: list[str] = ["Consolas", "DejaVu Sans Mono", "monospace"]

EXPORT_DPI = 160
SVG_DPI = 160
HERO_SIZE = (10.0, 5.625)
DETAIL_SIZE = (10.0, 6.4)
CONTACT_SHEET_SIZE = (16.0, 10.5)

HEADER_Y = 0.935
SUBTITLE_Y = 0.885
FOOTER_Y = 0.035

GRID_ALPHA = 0.45
LINE_WIDTH = 1.8
THIN_LINE = 0.9
MARKER_SIZE = 28
PANEL_RADIUS = 0.018


@dataclass(frozen=True)
class FigureMeta:
    """Metadata attached to a generated public figure."""

    filename: str
    title: str
    source_table: str
    model_card: str
    method: str


FIGURE_SET: tuple[FigureMeta, ...] = (
    FigureMeta(
        "F00_project_summary_card.png",
        "Crypto Market Factor Lab summary",
        "outputs/tables/T02_panel_coverage.csv",
        "outputs/model_cards/factor_exposure.md",
        "public artifact overview",
    ),
    FigureMeta(
        "F01_data_coverage.png",
        "Frozen BTC/ETH multi-source panel",
        "outputs/tables/T01_source_inventory.csv",
        "outputs/model_cards/factor_exposure.md",
        "source inventory coverage",
    ),
    FigureMeta(
        "F02_btc_block_attribution.png",
        "BTC factor attribution",
        "outputs/tables/T03_block_attribution.csv",
        "outputs/model_cards/block_attribution.md",
        "full-vs-reduced block partial R2",
    ),
    FigureMeta(
        "F03_btc_etf_lead_lag.png",
        "BTC ETF-flow lead-lag",
        "outputs/tables/T04_etf_lead_lag.csv",
        "outputs/model_cards/etf_flow_lead_lag.md",
        "HAC lead-lag association grid",
    ),
    FigureMeta(
        "F04_btc_rolling_correlations.png",
        "Cross-asset co-movement",
        "outputs/tables/T05_correlation_regime.csv",
        "outputs/model_cards/rolling_correlations.md",
        "180-day rolling correlations",
    ),
    FigureMeta(
        "F05_stablecoin_supply_tvl.png",
        "Stablecoin and DeFi liquidity context",
        "outputs/tables/T06_stablecoin_liquidity.csv",
        "outputs/model_cards/stablecoin_liquidity.md",
        "liquidity proxy diagnostics",
    ),
    FigureMeta(
        "F06_btc_native_dashboard.png",
        "BTC-native factor dashboard",
        "outputs/tables/T07_native_factor_ablation.csv",
        "outputs/model_cards/btc_native_factors.md",
        "native-factor ablation and correlation",
    ),
    FigureMeta(
        "F07_connectedness.png",
        "BTC/ETH/TradFi connectedness",
        "outputs/tables/T09_connectedness.csv",
        "outputs/model_cards/connectedness.md",
        "VAR/FEVD and rolling connectedness",
    ),
    FigureMeta(
        "F08_robustness_grid.png",
        "BTC robustness grid",
        "outputs/tables/T10_robustness.csv",
        "outputs/model_cards/robustness.md",
        "window/HAC/winsorization sensitivity",
    ),
    FigureMeta(
        "F09_key_results_cards.png",
        "Key results cards",
        "outputs/tables/key_results.md",
        "outputs/model_cards/factor_exposure.md",
        "summary research cards",
    ),
    FigureMeta(
        "T00_key_results_table.png",
        "Key results table card",
        "outputs/tables/key_results.md",
        "outputs/model_cards/factor_exposure.md",
        "styled public table",
    ),
)


def factor_color(name: str) -> str:
    """Return a stable color for a factor or block label."""

    return FACTOR_COLORS.get(name, COLORS["neutral"])
