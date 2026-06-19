from __future__ import annotations

from cqresearch.data.market_structure_cache import CacheLayout
from cqresearch.data.market_structure_clients import fetch_json_spec
from cqresearch.data.market_structure_endpoints import EndpointSpec


def test_fetch_json_spec_dry_run_does_not_require_network(tmp_path) -> None:
    layout = CacheLayout(tmp_path / "cache")
    spec = EndpointSpec("binance", "spot_exchange_info", "https://api.binance.com/api/v3/exchangeInfo")

    result = fetch_json_spec(spec, layout, dry_run=True)

    assert result.status == "dry_run"
    assert "api.binance.com" in result.safe_url


def test_fetch_json_spec_skips_missing_required_key(tmp_path, monkeypatch) -> None:
    monkeypatch.delenv("CMC_API_KEY", raising=False)
    layout = CacheLayout(tmp_path / "cache")
    spec = EndpointSpec(
        "coinmarketcap",
        "fear_greed_historical",
        "https://pro-api.coinmarketcap.com/v3/fear-and-greed/historical",
        requires_key_env="CMC_API_KEY",
    )

    result = fetch_json_spec(spec, layout)

    assert result.status == "skipped_missing_key"
    assert "CMC_API_KEY" in result.message
