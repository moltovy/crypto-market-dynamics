"""Optional free-data source scaffolding.

These helpers build public-source URLs and normalize sample payloads. They do
not fetch data and are intentionally kept outside the core portfolio pipelines.
"""
from cqresearch.optional_data.binance_public import (
    build_klines_url,
    klines_url,
    normalize_klines,
    normalize_klines_response,
)
from cqresearch.optional_data.coingecko_free import (
    build_market_chart_url,
    coin_market_chart_url,
    normalize_market_chart,
    normalize_market_chart_response,
)
from cqresearch.optional_data.defillama_free import (
    build_tvl_url,
    defillama_chains_url,
    defillama_protocol_tvl_url,
    normalize_chain_tvl_response,
    normalize_defillama_chains,
    normalize_defillama_protocol_tvl,
    normalize_stablecoin_response,
)
from cqresearch.optional_data.fred_free import (
    build_series_observations_url,
    fred_observations_url,
    normalize_fred_observations,
)
from cqresearch.optional_data.registry import optional_source_registry

__all__ = [
    "build_klines_url",
    "build_market_chart_url",
    "build_series_observations_url",
    "build_tvl_url",
    "coin_market_chart_url",
    "defillama_chains_url",
    "defillama_protocol_tvl_url",
    "fred_observations_url",
    "klines_url",
    "normalize_chain_tvl_response",
    "normalize_defillama_chains",
    "normalize_defillama_protocol_tvl",
    "normalize_fred_observations",
    "normalize_klines",
    "normalize_klines_response",
    "normalize_market_chart",
    "normalize_market_chart_response",
    "normalize_stablecoin_response",
    "optional_source_registry",
]
