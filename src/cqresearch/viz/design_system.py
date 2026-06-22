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
        "01_cross_asset_clustered_correlation.png",
        "Cross-Asset Dependence",
        "research/01_cross_asset_dependence_regimes/tables/pearson_correlation_matrix.csv",
        "research/01_cross_asset_dependence_regimes/methodology.md",
        "clustered daily return correlation",
    ),
    FigureMeta(
        "02_tradfi_exposure_shift.png",
        "TradFi Exposure Shift",
        "research/02_macro_tradfi_integration/tables/block_delta_r2.csv",
        "research/02_macro_tradfi_integration/methodology.md",
        "same-support period exposure comparison",
    ),
    FigureMeta(
        "03_leverage_tail_stress.png",
        "Leverage and Tail Stress",
        "research/03_derivatives_leverage_liquidations/tables/leverage_tail_risk_summary.csv",
        "research/03_derivatives_leverage_liquidations/methodology.md",
        "state-conditioned downside-return summary",
    ),
    FigureMeta(
        "04_etf_lag_response.png",
        "ETF Lag Response",
        "research/04_etf_institutional_flows/tables/etf_lag_response.csv",
        "research/04_etf_institutional_flows/methodology.md",
        "lagged market-plumbing association with bootstrap intervals",
    ),
    FigureMeta(
        "08_common_idiosyncratic_risk_decomposition.png",
        "Common and Idiosyncratic Risk",
        "research/08_relative_asset_risk_factor_structure/tables/common_idiosyncratic_risk_decomposition.csv",
        "research/08_relative_asset_risk_factor_structure/methodology.md",
        "PCA common-factor variance decomposition",
    ),
)


def factor_color(name: str) -> str:
    """Return a stable color for a factor or block label."""

    return FACTOR_COLORS.get(name, COLORS["neutral"])
