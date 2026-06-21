"""Canonical module registry for the public research surface."""

from __future__ import annotations

from dataclasses import dataclass

ALLOWED_USAGE_STATUSES: frozenset[str] = frozenset(
    {
        "primary_analysis",
        "robustness_or_sensitivity",
        "diagnostic_only",
        "excluded_insufficient_coverage",
        "excluded_definition_or_unit_ambiguity",
        "excluded_duplicate_or_redundant",
        "excluded_licensing_or_release_risk",
    }
)


@dataclass(frozen=True)
class ResearchModule:
    module_id: str
    title: str
    research_question: str


MODULES: tuple[ResearchModule, ...] = (
    ResearchModule(
        "00_data_foundation",
        "Data Foundation",
        "What data, units, timing, coverage, identity, and release-risk constraints govern every later result?",
    ),
    ResearchModule(
        "01_returns_risk_regimes",
        "Returns, Risk, and Regimes",
        "How do BTC and ETH return distributions, volatility, drawdown, and tail behavior vary across transparent regimes?",
    ),
    ResearchModule(
        "02_macro_cross_asset_exposure",
        "Macro and Cross-Asset Exposure",
        "How does crypto co-movement with equities, volatility, rates, dollar, and gold vary by asset, calendar, and period?",
    ),
    ResearchModule(
        "03_derivatives_leverage_liquidations",
        "Derivatives, Leverage, and Liquidations",
        "Where do leverage, funding, open-interest scaling, and liquidation stress appear in volatility and tail outcomes?",
    ),
    ResearchModule(
        "04_etf_institutional_plumbing",
        "ETF and Institutional Plumbing",
        "How do ETF flow intensity and absorption measures line up with contemporaneous and lagged crypto outcomes?",
    ),
    ResearchModule(
        "05_stablecoin_defi_liquidity",
        "Stablecoin and DeFi Liquidity State",
        "What do stablecoin supply and DeFi TVL proxies say about liquidity-state associations after unit and valuation audits?",
    ),
    ResearchModule(
        "06_onchain_valuation_holder_state",
        "On-Chain Valuation and Holder State",
        "Which on-chain valuation and holder-state measures are diagnostics versus admissible lagged state variables?",
    ),
    ResearchModule(
        "07_chain_fundamentals",
        "Chain Fundamentals",
        "Which chain-level activity measures have enough coverage and definition clarity for descriptive panel analysis?",
    ),
    ResearchModule(
        "08_relative_major_asset_risk",
        "Relative Major-Asset Risk",
        "How do selected major crypto assets compare on matched-window risk, downside, drawdown, and beta measures?",
    ),
    ResearchModule(
        "09_market_concentration_state",
        "Market Concentration State",
        "How do monthly point-in-time concentration, turnover, and rank-persistence states relate to market-structure conditions?",
    ),
    ResearchModule(
        "10_event_sensitivity",
        "Event Sensitivity",
        "How do registered event windows compare with empirical placebo windows under fixed window conventions?",
    ),
    ResearchModule(
        "11_cross_module_synthesis",
        "Cross-Module Synthesis",
        "Which findings remain strongest after comparing outcome, coverage, timing, uncertainty, and measurement-risk evidence?",
    ),
)


def module_ids() -> list[str]:
    return [module.module_id for module in MODULES]


def module_by_id(module_id: str) -> ResearchModule:
    for module in MODULES:
        if module.module_id == module_id:
            return module
    raise KeyError(f"Unknown research module: {module_id}")
