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
        filename="research/02_macro_cross_asset_exposure/figures/01_tradfi_exposure_shift.png",
        research_question="How did equity co-movement change across periods?",
        source_tables="research/02_macro_cross_asset_exposure/tables/block_delta_r2.csv",
        caveat="Pre-specified pre-BTC-ETF versus BTC-ETF-era comparison; not an ETF-effect estimate.",
        readme_section="figure-set",
    ),
    PublicFigure(
        figure_id="etf_market_plumbing",
        filename="research/04_etf_institutional_plumbing/figures/02_etf_market_plumbing.png",
        research_question="How do ETF flow measures line up with same-day and lagged returns?",
        source_tables="research/04_etf_institutional_plumbing/tables/etf_absorption_metrics.csv; research/04_etf_institutional_plumbing/tables/etf_flow_associations.csv",
        caveat="ETF flow intensity is a market-plumbing association, not causal price impact.",
        readme_section="figure-set",
    ),
    PublicFigure(
        figure_id="leverage_tail_stress",
        filename="research/03_derivatives_leverage_liquidations/figures/03_leverage_tail_stress.png",
        research_question="Where do lagged leverage states show up in tail stress?",
        source_tables="research/03_derivatives_leverage_liquidations/tables/leverage_tail_risk_summary.csv; research/03_derivatives_leverage_liquidations/tables/tail_risk_models.csv",
        caveat="Lagged leverage states are stress diagnostics; same-day liquidation signatures are appendix context.",
        readme_section="figure-set",
    ),
    PublicFigure(
        figure_id="market_concentration_state",
        filename="research/09_market_concentration_state/figures/market_concentration_state.png",
        research_question="How did point-in-time concentration and rank persistence evolve?",
        source_tables="research/09_market_concentration_state/tables/pit_market_structure_summary.csv",
        caveat="Monthly PIT snapshots support concentration and turnover state analysis, not daily performance.",
        readme_section="figure-set",
    ),
    PublicFigure(
        figure_id="selected_major_asset_risk",
        filename="research/08_relative_major_asset_risk/figures/05_selected_major_asset_risk.png",
        research_question="How do selected majors compare on volatility and drawdown?",
        source_tables="research/08_relative_major_asset_risk/tables/selected_major_risk_metrics.csv",
        caveat="Coverage-aware risk map; HYPE is explicitly short-history.",
        readme_section="figure-set",
    ),
)

GALLERY_FIGURES: tuple[str, ...] = (
    "research/06_onchain_valuation_holder_state/figures/measurement_mvrv_mechanics.png",
    "research/10_event_sensitivity/figures/appendix_event_response_matrix.png",
)

PUBLIC_TABLES: frozenset[str] = frozenset(
    {
        "research/00_data_foundation/tables/provider_inventory.csv",
        "research/00_data_foundation/tables/feature_usage_matrix.csv",
        "research/02_macro_cross_asset_exposure/tables/block_delta_r2.csv",
        "research/02_macro_cross_asset_exposure/tables/frequency_robustness.csv",
        "research/03_derivatives_leverage_liquidations/tables/leverage_tail_risk_summary.csv",
        "research/04_etf_institutional_plumbing/tables/etf_flow_associations.csv",
        "research/05_stablecoin_defi_liquidity/tables/valuation_contamination_audit.csv",
        "research/06_onchain_valuation_holder_state/tables/mvrv_mechanical_link_audit.csv",
        "research/08_relative_major_asset_risk/tables/selected_major_risk_metrics.csv",
        "research/09_market_concentration_state/tables/pit_market_structure_summary.csv",
        "research/11_cross_module_synthesis/tables/evidence_ledger.csv",
    }
)


def public_figure_paths() -> list[str]:
    return [figure.filename for figure in PUBLIC_FIGURES]


def public_table_names() -> set[str]:
    return set(PUBLIC_TABLES)
