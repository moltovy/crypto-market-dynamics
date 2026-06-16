"""Optional data source decision registry."""
from __future__ import annotations

import pandas as pd


def optional_source_registry() -> pd.DataFrame:
    """Return source value, overlap, maintenance, and recommendation notes."""

    rows = [
        {
            "source": "DefiLlama",
            "value": "Cross-check DeFi TVL and chain-level liquidity coverage.",
            "overlap": "High with existing DefiLlama curated CSVs.",
            "auth_rate_limit": "No key for public endpoints; rate limits can change.",
            "maintenance": "Low",
            "recommendation": "Useful as an optional refresh or audit source, not core.",
        },
        {
            "source": "CoinGecko",
            "value": "Free market-cap, price, and volume history for crypto assets.",
            "overlap": "Medium; useful for benchmark expansion and sanity checks.",
            "auth_rate_limit": "Free tier has rate limits; paid plans exist but are not required here.",
            "maintenance": "Medium",
            "recommendation": "Optional benchmark extension only.",
        },
        {
            "source": "Binance public klines",
            "value": "Exchange-native OHLCV for liquid symbols.",
            "overlap": "Medium with TradingView price history.",
            "auth_rate_limit": "No key for spot klines; endpoint availability varies by jurisdiction.",
            "maintenance": "Medium",
            "recommendation": "Useful for reproducible microstructure appendices.",
        },
        {
            "source": "FRED",
            "value": "Macro rates, spreads, and risk proxies.",
            "overlap": "High with existing curated FRED inputs.",
            "auth_rate_limit": "Free API key normally required for official endpoint.",
            "maintenance": "Low",
            "recommendation": "Keep as optional refresh scaffolding; do not require for core releases.",
        },
        {
            "source": "SEC / public ETF filings",
            "value": "Primary-source dates and language for ETF approvals, listings, and fund documents.",
            "overlap": "Low with the numeric panel; useful for event-study documentation and date audits.",
            "auth_rate_limit": "No paid key required for public filings; automated access should respect SEC fair-access guidance.",
            "maintenance": "Low",
            "recommendation": "Optional documentation/audit source, not a numeric core data dependency.",
        },
    ]
    return pd.DataFrame(rows)


__all__ = ["optional_source_registry"]
