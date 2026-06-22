"""Canonical module registry for the public research surface."""

from __future__ import annotations

from dataclasses import dataclass

ALLOWED_USAGE_STATUSES: frozenset[str] = frozenset(
    {
        "primary_analysis",
        "robustness_or_sensitivity",
        "diagnostic_only",
        "excluded_insufficient_coverage",
        "excluded_ambiguous_definition_or_unit",
        "excluded_duplicate",
        "excluded_release_risk",
    }
)


@dataclass(frozen=True)
class ResearchModule:
    module_id: str
    title: str
    research_question: str


MODULES: tuple[ResearchModule, ...] = (
    ResearchModule(
        "00_data_measurement_foundation",
        "Data and Measurement Foundation",
        "What data, assets, units, timing, coverage, identity, and release-risk constraints govern later empirical claims?",
    ),
    ResearchModule(
        "01_cross_asset_dependence_regimes",
        "Cross-Asset Dependence and Regimes",
        "How do crypto and TradFi return dependence, common-factor share, lower-tail co-exceedance, and regimes vary across matched samples?",
    ),
    ResearchModule(
        "02_macro_tradfi_integration",
        "Macro and TradFi Integration",
        "How do crypto exposures to equities, volatility, rates, the dollar, gold, and credit vary across calendars and periods?",
    ),
    ResearchModule(
        "03_derivatives_leverage_liquidations",
        "Derivatives, Leverage, and Liquidations",
        "Where do leverage, funding, open-interest scaling, and liquidation stress appear in volatility and tail outcomes?",
    ),
    ResearchModule(
        "04_etf_institutional_flows",
        "ETF and Institutional Flows",
        "How do ETF flow intensity, timing, lag response, and shock/placebo diagnostics line up with crypto outcomes?",
    ),
    ResearchModule(
        "05_stablecoin_defi_liquidity",
        "Stablecoin and DeFi Liquidity State",
        "What do stablecoin supply and DeFi TVL proxies say about liquidity-state associations after unit and valuation audits?",
    ),
    ResearchModule(
        "06_onchain_valuation_holder_behavior",
        "On-Chain Valuation and Holder Behavior",
        "Which on-chain valuation and holder-state measures are diagnostics versus admissible lagged state variables?",
    ),
    ResearchModule(
        "07_chain_fundamentals_sector_dynamics",
        "Chain Fundamentals and Sector Dynamics",
        "Which chain-level activity, sector, and point-in-time state measures have enough coverage and definition clarity for descriptive panel analysis?",
    ),
    ResearchModule(
        "08_relative_asset_risk_factor_structure",
        "Relative Asset Risk and Factor Structure",
        "How do selected crypto assets compare on matched-window risk, downside beta, expected shortfall, and common-versus-idiosyncratic factor structure?",
    ),
    ResearchModule(
        "09_event_stress_cross_module_synthesis",
        "Event Stress and Cross-Module Synthesis",
        "Which event-window, stress-state, and cross-module findings remain strongest after comparing sample, method, uncertainty, measurement risk, and limitations?",
    ),
)


def module_ids() -> list[str]:
    return [module.module_id for module in MODULES]


def module_by_id(module_id: str) -> ResearchModule:
    for module in MODULES:
        if module.module_id == module_id:
            return module
    raise KeyError(f"Unknown research module: {module_id}")
