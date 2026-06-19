from __future__ import annotations

from io import StringIO
from pathlib import Path

import pandas as pd
import pytest

from cqresearch.analysis.constituent_rotation import (
    DAILY_CONSTITUENT_CACHE,
    DAILY_CONSTITUENT_CURATED,
    SAMPLE_NOTE,
    ConstituentValidationError,
    build_constituent_rotation_tables,
    ingest_defillama_daily_constituents,
    load_daily_constituents,
    normalize_defillama_daily_constituents,
    read_defillama_daily_constituent_raw,
)


def _daily_raw(days: int = 220) -> pd.DataFrame:
    rows = []
    symbols = [
        ("BTC", "bitcoin", 1, 42000.0, 800_000_000_000.0),
        ("ETH", "ethereum", 2, 2300.0, 280_000_000_000.0),
        ("SOL", "solana", 3, 90.0, 40_000_000_000.0),
        ("DOGE", "dogecoin", 4, 0.08, 12_000_000_000.0),
    ]
    for day_idx, date_value in enumerate(pd.date_range("2024-01-01", periods=days, freq="D")):
        for symbol, token_id, rank, base_price, base_mcap in symbols:
            drift = 1 + day_idx * (0.0015 if symbol in {"SOL", "DOGE"} else 0.001)
            close = base_price * drift
            rows.append(
                {
                    "date": date_value.date().isoformat(),
                    "rank": rank,
                    "symbol": symbol,
                    "coingecko_id": token_id,
                    "open": close * 0.99,
                    "high": close * 1.02,
                    "low": close * 0.98,
                    "close": close,
                    "volume": 1_000_000 * rank,
                    "mcap": base_mcap * drift,
                }
            )
    return pd.DataFrame(rows)


def _write_config(root: Path) -> None:
    (root / "config").mkdir(parents=True, exist_ok=True)
    (root / "config" / "asset_classification_overrides.yml").write_text(
        "base_assets: [BTC, ETH, SOL, DOGE]\n",
        encoding="utf-8",
    )
    (root / "config" / "events.yml").write_text(
        """
primary_breaks:
  - id: test_event
    date: 2024-04-15
    description: Test event.
secondary_candidates: []
""".lstrip(),
        encoding="utf-8",
    )


def test_missing_daily_constituent_cache_skips_without_writing(tmp_path: Path) -> None:
    out_path, skipped = ingest_defillama_daily_constituents(tmp_path)

    assert out_path is None
    assert skipped
    assert not (tmp_path / DAILY_CONSTITUENT_CURATED).exists()


def test_daily_constituent_reader_skips_metadata_row(tmp_path: Path) -> None:
    source = tmp_path / DAILY_CONSTITUENT_CACHE
    source.parent.mkdir(parents=True)
    payload = _daily_raw(days=2).to_csv(index=False)
    source.write_text("## DefiLlama export metadata\n" + payload, encoding="utf-8")

    raw = read_defillama_daily_constituent_raw(source)

    assert list(raw.columns[:4]) == ["date", "rank", "symbol", "coingecko_id"]
    assert len(raw) == 8


def test_valid_daily_constituents_ingest_and_build_rotation_tables(tmp_path: Path) -> None:
    _write_config(tmp_path)
    source = tmp_path / DAILY_CONSTITUENT_CACHE
    source.parent.mkdir(parents=True)
    source.write_text(
        "## DefiLlama export metadata\n" + _daily_raw().to_csv(index=False), encoding="utf-8"
    )

    out_path, skipped = ingest_defillama_daily_constituents(tmp_path)
    daily = load_daily_constituents(tmp_path)
    tables = build_constituent_rotation_tables(
        daily, events_path=tmp_path / "config" / "events.yml"
    )

    assert skipped == []
    assert out_path == tmp_path / DAILY_CONSTITUENT_CURATED
    assert len(daily) == 880
    assert daily["method_note"].eq(SAMPLE_NOTE).all()
    assert not tables["breadth"].empty
    assert not tables["indexes"].empty
    assert not tables["dispersion"].empty
    assert not tables["beta"].empty
    assert not tables["events"].empty
    assert tables["gap"].loc[0, "status"] == "available"
    assert tables["gap"].loc[0, "row_count"] == 880
    assert "top50_ex_btc_eth" in set(tables["indexes"]["universe"])


def test_daily_constituent_validation_failures_are_loud() -> None:
    raw = _daily_raw(days=2)
    with pytest.raises(ConstituentValidationError, match="Missing daily constituent"):
        normalize_defillama_daily_constituents(raw.drop(columns=["mcap"]))

    bad_close = raw.copy()
    bad_close.loc[0, "close"] = 0
    with pytest.raises(ConstituentValidationError, match="positive"):
        normalize_defillama_daily_constituents(bad_close)

    missing_mcap = raw.copy()
    missing_mcap.loc[0, "mcap"] = 0
    normalized = normalize_defillama_daily_constituents(missing_mcap)
    assert normalized.loc[0, "market_cap_missing_or_nonpositive"]
    assert pd.isna(normalized.loc[0, "market_cap_usd"])

    duplicated = pd.concat([raw, raw.head(1)], ignore_index=True)
    with pytest.raises(ConstituentValidationError, match="duplicate"):
        normalize_defillama_daily_constituents(duplicated)


def test_daily_constituent_normalizer_accepts_file_like_raw_payload() -> None:
    raw = pd.read_csv(StringIO(_daily_raw(days=1).to_csv(index=False)))
    normalized = normalize_defillama_daily_constituents(raw)

    assert normalized["source"].eq("defillama_current_top50_exploratory_daily_ohlcv").all()
    assert normalized["universe_label"].eq("current_top50_exploratory_current_cohort").all()
