"""Optional free-data source scaffolding.

These helpers build public-source URLs and normalize sample payloads. They do
not fetch data and are intentionally kept outside the core portfolio pipelines.
"""
from cqresearch.optional_data.binance_public import klines_url, normalize_klines
from cqresearch.optional_data.coingecko_free import (
    coin_market_chart_url,
    normalize_market_chart,
)
from cqresearch.optional_data.defillama_free import (
    defillama_chains_url,
    defillama_protocol_tvl_url,
    normalize_defillama_chains,
    normalize_defillama_protocol_tvl,
)
from cqresearch.optional_data.fred_free import fred_observations_url, normalize_fred_observations
from cqresearch.optional_data.registry import optional_source_registry

__all__ = [
    "coin_market_chart_url",
    "defillama_chains_url",
    "defillama_protocol_tvl_url",
    "fred_observations_url",
    "klines_url",
    "normalize_defillama_chains",
    "normalize_defillama_protocol_tvl",
    "normalize_fred_observations",
    "normalize_klines",
    "normalize_market_chart",
    "optional_source_registry",
]
