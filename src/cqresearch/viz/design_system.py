"""Institutional visual design tokens for public research artifacts."""

from __future__ import annotations

from dataclasses import dataclass
from datetime import date

COLORS: dict[str, str] = {
    "bg": "#FAFAF7",
    "surface": "#FFFFFF",
    "surface2": "#F3F4F6",
    "grid": "#D9DEE7",
    "axis": "#E5E7EB",
    "text": "#111827",
    "muted": "#6B7280",
    "faint": "#9CA3AF",
    "btc": "#F7931A",
    "eth": "#627EEA",
    "macro": "#2563EB",
    "institutional": "#0F766E",
    "liquidity": "#16A34A",
    "stablecoin": "#059669",
    "native": "#7C3AED",
    "risk": "#DC2626",
    "gold": "#D97706",
    "neutral": "#6B7280",
    "positive": "#16A34A",
    "negative": "#DC2626",
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

TEXT_DENSITY = "minimal"


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
        "F01_mvrv_sensitivity_by_regime_v2.png",
        "MVRV Sensitivity by Regime",
        "outputs/tables/T25_mvrv_sensitivity_by_regime.csv",
        "outputs/model_cards/factor_exposure.md",
        "same-support regime sensitivity",
    ),
    FigureMeta(
        "F02_same_support_ablation.png",
        "Same-Support BTC Ablation",
        "outputs/tables/T19_same_support_ablation_btc.csv",
        "outputs/model_cards/block_attribution.md",
        "same-support nested model ablation",
    ),
    FigureMeta(
        "F03_btc_ex_mvrv_strength.png",
        "BTC Feature Strength ex-MVRV",
        "outputs/tables/T15_feature_strength_btc_ex_mvrv.csv",
        "outputs/model_cards/btc_native_factors.md",
        "feature strength without valuation-state proxy",
    ),
    FigureMeta(
        "F04_etf_flow_lead_lag.png",
        "ETF Flow Lead-Lag",
        "outputs/tables/T04_etf_lead_lag.csv",
        "outputs/model_cards/etf_flow_lead_lag.md",
        "HAC lead-lag association grid",
    ),
    FigureMeta(
        "F05_core_correlation_matrix.png",
        "Core Correlation Matrix",
        "outputs/tables/T23_core_correlation_matrix.csv",
        "outputs/model_cards/factor_exposure.md",
        "pairwise core feature correlations",
    ),
    FigureMeta(
        "F07_feature_strength_heatmap.png",
        "Feature Strength by Regime",
        "outputs/tables/T17_feature_strength_by_regime.csv",
        "outputs/model_cards/factor_exposure.md",
        "regime-stratified HAC t-stat heatmap",
    ),
)


def factor_color(name: str) -> str:
    """Return a stable color for a factor or block label."""

    return FACTOR_COLORS.get(name, COLORS["neutral"])
