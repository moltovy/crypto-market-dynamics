from __future__ import annotations

from pathlib import Path

import pandas as pd
import pytest

from cqresearch.analysis.market_universe import (
    MONTHLY_UNIVERSE_CACHE,
    MONTHLY_UNIVERSE_CURATED,
    UniverseValidationError,
    build_market_structure_daily_context,
    classify_market_universe,
    clean_risk_top100,
    cycle_phase_market_structure,
    ingest_defillama_monthly_universe,
    market_structure_composition,
    market_structure_composition_shift,
    market_structure_modeling_summary,
    market_structure_monthly_features,
    market_structure_return_regimes,
    market_structure_turnover_by_phase,
    normalize_defillama_monthly_universe,
    rank_turnover,
)


def _raw_universe() -> pd.DataFrame:
    rows = []
    specs = [
        (
            "2024-01-31",
            [
                ("BTC", "Bitcoin", 1000, 1),
                ("ETH", "Ethereum", 900, 2),
                ("USDT", "Tether", 800, 3),
                ("WBTC", "Wrapped BTC", 700, 4),
                ("STETH", "Lido Staked ETH", 600, 5),
                ("PAXG", "Pax Gold", 500, 6),
                ("DOGE", "Dogecoin", 400, 7),
                ("SOL", "Solana", 300, 8),
            ],
        ),
        (
            "2024-02-16",
            [
                ("BTC", "Bitcoin", 1100, 1),
                ("ETH", "Ethereum", 950, 2),
                ("USDC", "USD Coin", 850, 3),
                ("CBBTC", "Coinbase Wrapped BTC", 750, 4),
                ("WSTETH", "Wrapped stETH", 650, 5),
                ("XAUT", "Tether Gold", 550, 6),
                ("ADA", "Cardano", 450, 7),
                ("DOGE", "Dogecoin", 350, 8),
            ],
        ),
    ]
    for date, assets in specs:
        for symbol, name, market_cap, rank in assets:
            rows.append(
                {
                    "date": date,
                    "ticker": symbol,
                    "name": name,
                    "price": market_cap / 100,
                    "marketCap": market_cap,
                    "rank": rank,
                }
            )
    return pd.DataFrame(rows)


def _normalized() -> pd.DataFrame:
    return normalize_defillama_monthly_universe(
        _raw_universe(),
        expected_snapshots=2,
        rows_per_snapshot=8,
        partial_month_date="2024-02-16",
    )


def test_missing_monthly_universe_cache_skips_without_writing(tmp_path: Path) -> None:
    out_path, skipped = ingest_defillama_monthly_universe(tmp_path)

    assert out_path is None
    assert skipped
    assert not (tmp_path / MONTHLY_UNIVERSE_CURATED).exists()


def test_valid_monthly_universe_ingests_and_marks_partial_month(tmp_path: Path) -> None:
    source = tmp_path / MONTHLY_UNIVERSE_CACHE
    source.parent.mkdir(parents=True)
    _raw_universe().to_csv(source, index=False)

    out_path, skipped = ingest_defillama_monthly_universe(
        tmp_path,
        expected_snapshots=2,
        rows_per_snapshot=8,
        partial_month_date="2024-02-16",
    )
    written = pd.read_csv(out_path)

    assert skipped == []
    assert out_path == tmp_path / MONTHLY_UNIVERSE_CURATED
    assert len(written) == 16
    assert written["rank_full_market"].max() == 8
    assert written.loc[written["snapshot_date"] == "2024-02-16", "is_partial_month"].all()


def test_monthly_universe_validation_failures_are_loud() -> None:
    raw = _raw_universe()
    with pytest.raises(UniverseValidationError, match="Expected 9 rows"):
        normalize_defillama_monthly_universe(
            raw,
            expected_snapshots=2,
            rows_per_snapshot=9,
            partial_month_date="2024-02-16",
        )

    bad_missing_eth = raw[raw["ticker"] != "ETH"]
    with pytest.raises(UniverseValidationError, match="BTC/ETH missing"):
        normalize_defillama_monthly_universe(
            bad_missing_eth,
            expected_snapshots=2,
            rows_per_snapshot=7,
            partial_month_date="2024-02-16",
        )

    bad_market_cap = raw.copy()
    bad_market_cap.loc[0, "marketCap"] = 0
    with pytest.raises(UniverseValidationError, match="market_cap_usd"):
        normalize_defillama_monthly_universe(
            bad_market_cap,
            expected_snapshots=2,
            rows_per_snapshot=8,
            partial_month_date="2024-02-16",
        )

    bad_rank = raw.copy()
    bad_rank.loc[0, "rank"] = 2
    with pytest.raises(UniverseValidationError, match="rank_full_market"):
        normalize_defillama_monthly_universe(
            bad_rank,
            expected_snapshots=2,
            rows_per_snapshot=8,
            partial_month_date="2024-02-16",
        )


def test_clean_risk_universe_excludes_productized_and_stable_assets() -> None:
    overrides = {
        "stablecoins": {"USDT", "USDC"},
        "wrapped_assets": {"WBTC", "CBBTC"},
        "lst_restaking": {"STETH", "WSTETH"},
        "tokenized_commodities": {"PAXG", "XAUT"},
        "base_assets": {"BTC", "ETH", "SOL", "ADA"},
    }
    classified = classify_market_universe(_normalized(), overrides)
    clean = clean_risk_top100(classified)

    assert {"USDT", "USDC", "WBTC", "CBBTC", "STETH", "WSTETH", "PAXG", "XAUT"}.isdisjoint(
        set(clean["symbol"])
    )
    assert {"BTC", "ETH", "DOGE"}.issubset(set(clean["symbol"]))


def test_composition_turnover_and_cycle_phase_builders() -> None:
    overrides = {
        "stablecoins": {"USDT", "USDC"},
        "wrapped_assets": {"WBTC", "CBBTC"},
        "lst_restaking": {"STETH", "WSTETH"},
        "tokenized_commodities": {"PAXG", "XAUT"},
        "base_assets": {"BTC", "ETH", "SOL", "ADA"},
    }
    classified = classify_market_universe(_normalized(), overrides)
    composition = market_structure_composition(classified)
    turnover = rank_turnover(classified)
    cycle = cycle_phase_market_structure(composition)

    assert {"full_top100", "ex_stable_top100", "clean_risk_top100"}.issubset(
        set(composition["universe_type"])
    )
    latest_turnover = turnover[
        (turnover["month"] == "2024-02") & (turnover["universe_type"] == "clean_risk_top100")
    ].iloc[0]
    assert latest_turnover["entrants"] == 1
    assert latest_turnover["exits"] == 1
    assert not cycle.empty


def test_monthly_features_daily_context_and_regime_diagnostics() -> None:
    overrides = {
        "stablecoins": {"USDT", "USDC"},
        "wrapped_assets": {"WBTC", "CBBTC"},
        "lst_restaking": {"STETH", "WSTETH"},
        "tokenized_commodities": {"PAXG", "XAUT"},
        "base_assets": {"BTC", "ETH", "SOL", "ADA"},
    }
    classified = classify_market_universe(_normalized(), overrides)
    composition = market_structure_composition(classified)
    turnover = rank_turnover(classified)
    monthly = market_structure_monthly_features(classified, composition, turnover)

    assert len(monthly) == 2
    assert monthly["btc_eth_share_full_top100"].between(0, 1).all()
    assert monthly["clean_risk_entrants"].iloc[-1] == 1

    dates = pd.date_range("2024-01-01", "2024-03-15", freq="D")
    daily = pd.DataFrame(
        {
            "date": dates,
            "btc_close": [100 + idx for idx in range(len(dates))],
            "eth_close": [50 + idx * 0.5 for idx in range(len(dates))],
        }
    )
    context = build_market_structure_daily_context(daily, monthly)
    assert not context.empty
    assert context["market_structure_snapshot_date"].min() == pd.Timestamp("2024-01-31")
    assert context["btc_return_1d"].notna().any()

    synthetic_context = context.copy()
    synthetic_context["top10_share_full_top100"] = [
        0.40 + idx / 1000 for idx in range(len(synthetic_context))
    ]
    synthetic_context["clean_risk_share_full_top100"] = [
        0.30 + idx / 1200 for idx in range(len(synthetic_context))
    ]
    regimes = market_structure_return_regimes(synthetic_context)
    shift = market_structure_composition_shift(monthly)
    turnover_phase = market_structure_turnover_by_phase(monthly)
    summary = market_structure_modeling_summary(monthly, context, regimes, shift, turnover_phase)

    assert {"BTC", "ETH"}.issubset(set(regimes["asset"]))
    assert {"low", "mid", "high"}.issubset(set(regimes["bucket"]))
    assert not shift.empty
    assert not turnover_phase.empty
    assert "descriptive regime analysis" in summary
