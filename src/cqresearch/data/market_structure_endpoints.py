"""Endpoint registry for the market-structure extension."""

from __future__ import annotations

import os
from dataclasses import dataclass, field
from typing import Any
from urllib.parse import urlencode

from cqresearch.data.market_structure_cache import redact_url


@dataclass(frozen=True)
class EndpointSpec:
    """A requestable endpoint plus public metadata."""

    source: str
    dataset: str
    url: str
    method: str = "GET"
    params: dict[str, Any] = field(default_factory=dict)
    headers: dict[str, str] = field(default_factory=dict)
    requires_key_env: str | None = None
    tier: str = "free"
    frequency: str = "snapshot"
    notes: str = ""

    @property
    def has_required_key(self) -> bool:
        return self.requires_key_env is None or bool(os.getenv(self.requires_key_env))

    @property
    def safe_url(self) -> str:
        if not self.params:
            return redact_url(self.url)
        separator = "&" if "?" in self.url else "?"
        return redact_url(f"{self.url}{separator}{urlencode(self.params)}")

    def resolved_headers(self) -> dict[str, str]:
        headers = dict(self.headers)
        if self.requires_key_env == "CMC_API_KEY":
            headers["X-CMC_PRO_API_KEY"] = os.getenv("CMC_API_KEY", "")
        return headers


def defillama_specs(use_pro: bool | None = None) -> list[EndpointSpec]:
    """Return DefiLlama free endpoints plus Pro specs when requested."""

    specs = [
        EndpointSpec("defillama", "chains_current", "https://api.llama.fi/v2/chains", frequency="snapshot"),
        EndpointSpec(
            "defillama",
            "stablecoins_current",
            "https://stablecoins.llama.fi/stablecoins",
            frequency="snapshot",
        ),
        EndpointSpec(
            "defillama",
            "stablecoins_history",
            "https://stablecoins.llama.fi/stablecoincharts/all",
            frequency="daily",
        ),
        EndpointSpec("defillama", "dex_overview", "https://api.llama.fi/overview/dexs", frequency="daily"),
        EndpointSpec("defillama", "fees_overview", "https://api.llama.fi/overview/fees", frequency="daily"),
        EndpointSpec(
            "defillama",
            "open_interest_overview",
            "https://api.llama.fi/overview/open-interest",
            frequency="daily",
        ),
    ]
    if use_pro is None:
        use_pro = os.getenv("DEFILLAMA_USE_PRO", "").lower() in {"1", "true", "yes", "y"}
    if use_pro:
        key = os.getenv("DEFILLAMA_API_KEY", "{DEFILLAMA_API_KEY}")
        pro_base = f"https://pro-api.llama.fi/{key}"
        specs.extend(
            [
                EndpointSpec(
                    "defillama",
                    "etf_history",
                    f"{pro_base}/etfs",
                    requires_key_env="DEFILLAMA_API_KEY",
                    tier="pro",
                    frequency="daily",
                    notes="Optional Pro endpoint; skipped when plan/key access is unavailable.",
                ),
                EndpointSpec(
                    "defillama",
                    "bridges",
                    f"{pro_base}/bridges",
                    requires_key_env="DEFILLAMA_API_KEY",
                    tier="pro",
                    frequency="daily",
                ),
                EndpointSpec(
                    "defillama",
                    "rwa",
                    f"{pro_base}/rwa",
                    requires_key_env="DEFILLAMA_API_KEY",
                    tier="pro",
                    frequency="daily",
                ),
                EndpointSpec(
                    "defillama",
                    "dat",
                    f"{pro_base}/dat",
                    requires_key_env="DEFILLAMA_API_KEY",
                    tier="pro",
                    frequency="snapshot",
                ),
                EndpointSpec(
                    "defillama",
                    "historical_token_liquidity",
                    f"{pro_base}/historicalLiquidity",
                    requires_key_env="DEFILLAMA_API_KEY",
                    tier="pro",
                    frequency="daily",
                ),
            ]
        )
    return specs


def binance_specs(core_symbols: list[str] | None = None) -> list[EndpointSpec]:
    """Return Binance public endpoint specs for spot and USD-M futures."""

    symbols = core_symbols or ["BTCUSDT", "ETHUSDT"]
    specs: list[EndpointSpec] = [
        EndpointSpec("binance", "spot_exchange_info", "https://api.binance.com/api/v3/exchangeInfo"),
        EndpointSpec("binance", "spot_24h_tickers", "https://api.binance.com/api/v3/ticker/24hr"),
        EndpointSpec("binance", "spot_book_tickers", "https://api.binance.com/api/v3/ticker/bookTicker"),
        EndpointSpec("binance", "usd_m_futures_exchange_info", "https://fapi.binance.com/fapi/v1/exchangeInfo"),
    ]
    for symbol in symbols:
        specs.append(
            EndpointSpec(
                "binance",
                f"spot_daily_klines_{symbol}",
                "https://api.binance.com/api/v3/klines",
                params={"symbol": symbol, "interval": "1d", "limit": 1000},
                frequency="daily",
            )
        )
        specs.append(
            EndpointSpec(
                "binance",
                f"usd_m_funding_rate_{symbol}",
                "https://fapi.binance.com/fapi/v1/fundingRate",
                params={"symbol": symbol, "limit": 1000},
                frequency="8h",
            )
        )
        for endpoint, dataset in [
            ("klines", "usd_m_futures_klines"),
            ("markPriceKlines", "usd_m_mark_price_klines"),
            ("indexPriceKlines", "usd_m_index_price_klines"),
            ("premiumIndexKlines", "usd_m_premium_index_klines"),
        ]:
            specs.append(
                EndpointSpec(
                    "binance",
                    f"{dataset}_{symbol}",
                    f"https://fapi.binance.com/fapi/v1/{endpoint}",
                    params={"symbol": symbol, "interval": "1d", "limit": 1000},
                    frequency="daily",
                )
            )
        specs.append(
            EndpointSpec(
                "binance",
                f"usd_m_continuous_contract_klines_{symbol}",
                "https://fapi.binance.com/fapi/v1/continuousKlines",
                params={"pair": symbol, "contractType": "PERPETUAL", "interval": "1d", "limit": 1000},
                frequency="daily",
            )
        )
    return specs


def cmc_specs() -> list[EndpointSpec]:
    """Return CoinMarketCap Fear & Greed specs."""

    return [
        EndpointSpec(
            "coinmarketcap",
            "fear_greed_historical",
            "https://pro-api.coinmarketcap.com/v3/fear-and-greed/historical",
            params={"start": 1, "limit": 500},
            headers={"Accept": "application/json"},
            requires_key_env="CMC_API_KEY",
            tier="basic_plus",
            frequency="daily",
            notes="Requires X-CMC_PRO_API_KEY; skipped without CMC_API_KEY.",
        )
    ]


def all_endpoint_specs() -> list[EndpointSpec]:
    """Return every endpoint registered for the extension."""

    return [*defillama_specs(), *binance_specs(), *cmc_specs()]


def endpoint_audit_rows(specs: list[EndpointSpec] | None = None) -> list[dict[str, Any]]:
    """Return public-safe endpoint registry rows."""

    rows = []
    for spec in specs or all_endpoint_specs():
        rows.append(
            {
                "source": spec.source,
                "dataset": spec.dataset,
                "tier": spec.tier,
                "frequency": spec.frequency,
                "requires_key_env": spec.requires_key_env or "",
                "key_available": spec.has_required_key,
                "safe_url": spec.safe_url,
                "notes": spec.notes,
            }
        )
    return rows
