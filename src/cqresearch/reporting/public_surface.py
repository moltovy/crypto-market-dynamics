"""Single source of truth for maintained public artifacts."""

from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class PublicFigure:
    figure_id: str
    filename: str
    research_question: str
    source_tables: str
    caveat: str
    readme_section: str


PUBLIC_FIGURES: tuple[PublicFigure, ...] = (
    PublicFigure(
        figure_id="tradfi_exposure_shift",
        filename="01_tradfi_exposure_shift.png",
        research_question="How did equity co-movement change across periods?",
        source_tables="outputs/tables/block_delta_r2.csv",
        caveat="Pre-specified pre-BTC-ETF versus BTC-ETF-era comparison; not an ETF-effect estimate.",
        readme_section="macro-integration-and-institutional-access",
    ),
    PublicFigure(
        figure_id="etf_market_plumbing",
        filename="02_etf_market_plumbing.png",
        research_question="How do ETF flow measures line up with same-day and lagged returns?",
        source_tables="outputs/tables/etf_absorption_metrics.csv; outputs/tables/etf_flow_associations.csv",
        caveat="ETF flow intensity is a market-plumbing association, not causal price impact.",
        readme_section="macro-integration-and-institutional-access",
    ),
    PublicFigure(
        figure_id="leverage_tail_stress",
        filename="03_leverage_tail_stress.png",
        research_question="Where do lagged leverage states show up in tail stress?",
        source_tables="outputs/tables/leverage_tail_risk_summary.csv; outputs/tables/tail_risk_models.csv",
        caveat="Lagged leverage states are stress diagnostics; same-day liquidation signatures are appendix context.",
        readme_section="leverage-and-liquidity-state",
    ),
    PublicFigure(
        figure_id="point_in_time_market_structure",
        filename="04_point_in_time_market_structure.png",
        research_question="How did point-in-time composition and concentration evolve?",
        source_tables="outputs/tables/pit_composition.csv; outputs/tables/pit_concentration.csv",
        caveat="Monthly PIT snapshots support structure and concentration, not daily performance.",
        readme_section="market-structure-and-selected-major-risk",
    ),
    PublicFigure(
        figure_id="selected_major_asset_risk",
        filename="05_selected_major_asset_risk.png",
        research_question="How do selected majors compare on volatility and drawdown?",
        source_tables="outputs/tables/selected_major_risk_metrics.csv",
        caveat="Coverage-aware risk map; HYPE is explicitly short-history.",
        readme_section="market-structure-and-selected-major-risk",
    ),
)

GALLERY_FIGURES: tuple[str, ...] = (
    "measurement_mvrv_mechanics.png",
    "appendix_event_response_matrix.png",
)

PUBLIC_TABLES: frozenset[str] = frozenset(
    {
        "tables/data_source_coverage.csv",
        "tables/provider_data_disposition.csv",
        "tables/valuation_contamination_audit.csv",
        "tables/feature_registry.csv",
        "tables/mvrv_mechanical_link_audit.csv",
        "tables/btc_ex_mvrv_feature_strength.csv",
        "tables/eth_feature_strength.csv",
        "tables/rolling_tradfi_exposures.csv",
        "tables/rolling_exposure_summary.csv",
        "tables/leverage_tail_risk_summary.csv",
        "tables/etf_market_plumbing_summary.csv",
        "tables/stablecoin_defi_liquidity_summary.csv",
        "tables/selected_major_risk_metrics.csv",
        "tables/selected_major_comparable_window_metrics.csv",
        "tables/pit_market_structure_summary.csv",
        "tables/event_response_matrix.csv",
        "tables/local_window_correlation_distribution.csv",
        "tables/robustness_summary.csv",
        "tables/evidence_ledger.csv",
        "tables/evidence_map.md",
        "tables/claim_inventory.csv",
    }
)


def public_figure_paths() -> list[str]:
    return [f"outputs/figures/public/{figure.filename}" for figure in PUBLIC_FIGURES]


def public_table_names() -> set[str]:
    return set(PUBLIC_TABLES)
