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
        figure_id="cross_asset_dependence_regimes",
        filename="research/01_cross_asset_dependence_regimes/figures/01_cross_asset_clustered_correlation.png",
        research_question="How broad is realized crypto and macro dependence across matched assets?",
        source_tables="research/01_cross_asset_dependence_regimes/tables/pearson_correlation_matrix.csv; research/01_cross_asset_dependence_regimes/tables/pca_variance_share.csv",
        caveat="Current-cohort selected-major daily data is survivorship-biased.",
        readme_section="selected-analytical-results",
    ),
    PublicFigure(
        figure_id="tradfi_exposure_shift",
        filename="research/02_macro_tradfi_integration/figures/02_tradfi_exposure_shift.png",
        research_question="How did equity co-movement change across periods?",
        source_tables="research/02_macro_tradfi_integration/tables/block_delta_r2.csv; research/02_macro_tradfi_integration/tables/rolling_tradfi_exposures.csv",
        caveat="Period comparison, not ETF-effect identification.",
        readme_section="selected-analytical-results",
    ),
    PublicFigure(
        figure_id="leverage_tail_stress",
        filename="research/03_derivatives_leverage_liquidations/figures/03_leverage_tail_stress.png",
        research_question="Where do lagged leverage states show up in tail stress?",
        source_tables="research/03_derivatives_leverage_liquidations/tables/leverage_tail_risk_summary.csv; research/03_derivatives_leverage_liquidations/tables/tail_risk_models.csv",
        caveat="Stress-state diagnostics do not establish liquidation-caused returns.",
        readme_section="selected-analytical-results",
    ),
    PublicFigure(
        figure_id="etf_lag_response",
        filename="research/04_etf_institutional_flows/figures/04_etf_lag_response.png",
        research_question="How do ETF flow-return associations vary over lags 0-5?",
        source_tables="research/04_etf_institutional_flows/tables/etf_lag_response.csv; research/04_etf_institutional_flows/tables/etf_pre_inception_plot_audit.csv",
        caveat="ETF flows are timing-sensitive market plumbing, not causal price impact.",
        readme_section="selected-analytical-results",
    ),
    PublicFigure(
        figure_id="relative_asset_factor_structure",
        filename="research/08_relative_asset_risk_factor_structure/figures/08_common_idiosyncratic_risk_decomposition.png",
        research_question="How much selected-major risk is common crypto factor versus idiosyncratic?",
        source_tables="research/08_relative_asset_risk_factor_structure/tables/relative_factor_decomposition.csv; research/08_relative_asset_risk_factor_structure/tables/downside_expected_shortfall.csv",
        caveat="Matched-window, current-cohort risk diagnostics are not investability claims.",
        readme_section="selected-analytical-results",
    ),
)

GALLERY_FIGURES: tuple[str, ...] = (
    "research/06_onchain_valuation_holder_behavior/figures/measurement_mvrv_mechanics.png",
    "research/09_event_stress_cross_module_synthesis/figures/appendix_event_response_matrix.png",
)

PUBLIC_TABLES: frozenset[str] = frozenset(
    {
        "research/00_data_measurement_foundation/tables/provider_inventory.csv",
        "research/00_data_measurement_foundation/tables/feature_usage_matrix.csv",
        "research/01_cross_asset_dependence_regimes/tables/pearson_correlation_matrix.csv",
        "research/02_macro_tradfi_integration/tables/block_delta_r2.csv",
        "research/03_derivatives_leverage_liquidations/tables/leverage_tail_risk_summary.csv",
        "research/04_etf_institutional_flows/tables/etf_lag_response.csv",
        "research/05_stablecoin_defi_liquidity/tables/valuation_contamination_audit.csv",
        "research/06_onchain_valuation_holder_behavior/tables/mvrv_mechanical_link_audit.csv",
        "research/08_relative_asset_risk_factor_structure/tables/relative_factor_decomposition.csv",
        "research/09_event_stress_cross_module_synthesis/tables/evidence_ledger.csv",
    }
)


def public_figure_paths() -> list[str]:
    return [figure.filename for figure in PUBLIC_FIGURES]


def public_table_names() -> set[str]:
    return set(PUBLIC_TABLES)
