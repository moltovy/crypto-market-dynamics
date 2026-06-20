"""Shared pytest fixtures.

Keeps tests side-effect-free and fast. Fixtures here must NOT touch local
provider-data folders such as ``data_local/`` or legacy ``Data/``.
"""
from __future__ import annotations

from pathlib import Path

import pytest


@pytest.fixture(scope="session")
def project_root() -> Path:
    from config.paths import PROJECT_ROOT
    return PROJECT_ROOT


@pytest.fixture(scope="session")
def fixtures_dir() -> Path:
    return Path(__file__).resolve().parent.parent / "fixtures"


@pytest.fixture(scope="session")
def tiny_prices_csv(fixtures_dir: Path) -> Path:
    return fixtures_dir / "tiny_prices.csv"


@pytest.fixture(scope="session")
def tiny_macro_csv(fixtures_dir: Path) -> Path:
    return fixtures_dir / "tiny_macro.csv"
