#!/usr/bin/env python3
"""
Organize CryptoQuant CSV exports into category subfolders and write *_Metrics.txt inventories.
"""
from __future__ import annotations

import csv
import hashlib
import re
import shutil
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import Callable, Iterable

# BUG-FIX (2026-04-18): previously parents[1] resolved to tools/, which made
# CRYPTOQUANT = tools/CryptoQuant and silently operated on the wrong path.
# Resolve against the project root and Data/ via config/paths.py.
import sys as _sys
_proot = Path(__file__).resolve().parents[2]
if str(_proot) not in _sys.path:
    _sys.path.insert(0, str(_proot))
try:
    from config.paths import DATA_DIR, PROJECT_ROOT as ROOT
except Exception:
    ROOT = _proot
    DATA_DIR = ROOT / "Data"
CRYPTOQUANT = DATA_DIR / "CryptoQuant"


# Nav order per asset (CryptoQuant Summary pages)
CATEGORY_ORDER: dict[str, list[str]] = {
    "BTC": [
        "Exchange Flows",
        "Flow Indicator",
        "Market Indicator",
        "Network Indicator",
        "Miner Flows",
        "Derivatives",
        "Fund Data",
        "Market Data",
        "Addresses",
        "Fees And Revenue",
        "Network Stats",
        "Supply",
        "Transactions",
        "Inter Entity Flows",
    ],
    "ETH": [
        "Exchange Flows",
        "Flow Indicator",
        "Market Indicator",
        "Derivatives",
        "Fund Data",
        "Market Data",
        "ETH 2.0",
        "Addresses",
        "Fees And Revenue",
        "Network Stats",
        "Supply",
        "Transactions",
    ],
    "USDC": [
        "Exchange Flows",
        "Flow Indicator",
        "Market Data",
        "Addresses",
        "Supply",
        "Transactions",
    ],
    "USDT_ETH": [
        "Exchange Flows",
        "Flow Indicator",
        "Market Data",
        "Addresses",
        "Supply",
        "Transactions",
    ],
    "USDT_TRX": [
        "Exchange Flows",
        "Flow Indicator",
        "Market Data",
        "Addresses",
        "Supply",
        "Transactions",
    ],
    "WBTC": [
        "Addresses",
        "Supply",
        "Transactions",
    ],
}

METRICS_FILENAMES = {
    "BTC": "BTC_Metrics.txt",
    "ETH": "ETH_Metrics.txt",
    "USDC": "USDC_Metrics.txt",
    "USDT_ETH": "USDT_ETH_Metrics.txt",
    "USDT_TRX": "USDT_TRX_Metrics.txt",
    "WBTC": "WBTC_Metrics.txt",
}

ASSET_DIRS: dict[str, Path] = {
    "BTC": CRYPTOQUANT / "BTC",
    "ETH": CRYPTOQUANT / "ETH",
    "USDC": CRYPTOQUANT / "USDC",
    "USDT_ETH": CRYPTOQUANT / "USDT ETH",
    "USDT_TRX": CRYPTOQUANT / "USDT (TRX)",
    "WBTC": CRYPTOQUANT / "WBTC",
}


def _norm(name: str) -> str:
    return name.casefold()


def _strip_day_suffix(filename: str) -> str:
    base = filename
    if base.lower().endswith(".csv"):
        base = base[:-4]
    base = re.sub(r"\s*-\s*Day\s*(\(\d+\))?\s*$", "", base, flags=re.I)
    return base.strip()


def classify_btc(filename: str) -> str:
    n = _norm(filename)
    # Inter-entity (before generic Miner / Exchange)
    if "exchange to exchange" in n:
        return "Inter Entity Flows"
    if "miner to miner" in n:
        return "Inter Entity Flows"
    if "miner to exchange" in n or "exchange to miner" in n:
        return "Miner Flows"
    if "miners' position index" in n or "miner reserve" in n or "miner netflow" in n:
        return "Miner Flows"
    if " miner " in n or n.startswith("bitcoin miner") or "bitcoin miner " in n:
        return "Miner Flows"
    # Flow indicators (before generic exchange)
    if "exchange inflow - spent output" in n:
        return "Exchange Flows"
    if "exchange inflow cdd" in n:
        return "Flow Indicator"
    if "fund flow ratio" in n:
        return "Flow Indicator"
    if "whale ratio" in n:
        return "Flow Indicator"
    if "exchange stablecoins ratio" in n:
        return "Flow Indicator"
    if "stablecoin supply ratio" in n or "(ssr)" in n:
        return "Flow Indicator"
    if "exchange supply ratio" in n:
        return "Flow Indicator"
    # Derivatives
    if "open interest" in n or "funding rates" in n or "liquidations" in n:
        return "Derivatives"
    if "estimated leverage" in n:
        return "Derivatives"
    if "futures taker cvd" in n:
        return "Derivatives"
    # Fund data
    if "fund holdings" in n or "fund volume" in n or "fund market premium" in n or "fund price" in n:
        return "Fund Data"
    if "coinbase premium" in n or "korea premium" in n:
        return "Fund Data"
    # Fees
    if "fees" in n or "block rewards" in n:
        return "Fees And Revenue"
    # Market data (caps, price, volume, taker spot, trading volume, geographical)
    if "market cap" in n or "realized cap" in n or "thermo cap" in n or "delta cap" in n or "average cap" in n:
        return "Market Data"
    if "price & volume" in n or "trading volume" in n:
        return "Market Data"
    if "taker buy" in n or "taker sell" in n or "taker buy sell ratio" in n:
        return "Market Data"
    if "geographical supply" in n:
        return "Market Data"
    if "exchange supply" in n and "ratio" not in n:
        return "Market Data"
    # Spot taker CVD = market indicator on CQ
    if "spot taker cvd" in n:
        return "Market Indicator"
    # Market indicators (valuation / behavior)
    if any(
        x in n
        for x in (
            "mvrv",
            "sopr",
            "nvt",
            "nvm",
            "binary cdd",
            "adjusted sopr",
            "nupl",
            "net unrealized",
            "puell",
            "stock-to-flow",
            "realized price",
            "spent output",
            "mean coin age",
            "sum coin age",
            "mean coin dollar age",
            "sum coin dollar age",
            "supply in profit",
            "supply in loss",
            "average dormancy",
            "supply adjusted dormancy",
            "supply-adjusted cdd",
            "average supply-adjusted cdd",
            "long term holder",
            "short term holder",
            "long-term holder",
            "short-term holder",
        )
    ):
        return "Market Indicator"
    # Network indicator: base CDD, UTXO distribution (not simple count)
    if "coin days destroyed (cdd)" in n and "exchange" not in n:
        return "Network Indicator"
    if "utxo age bands" in n or "utxo value bands" in n:
        return "Network Indicator"
    if "utxo count - age" in n or "utxo count - value" in n:
        return "Network Indicator"
    if "utxos in profit" in n or "utxos in loss" in n:
        return "Network Indicator"
    if "spent output age bands" in n or "spent output value bands" in n:
        return "Market Indicator"
    # Network stats
    if any(
        x in n
        for x in (
            "hashrate",
            "difficulty",
            "block interval",
            "block size",
            "blocks mined",
            "velocity",
        )
    ):
        return "Network Stats"
    if re.search(r"utxo count\s*-\s*day", n) or n.endswith("utxo count - day.csv"):
        return "Network Stats"
    if "bitcoin utxo count - day" in n:
        return "Network Stats"
    # Simple UTXO count file
    if "utxo count" in n and "age" not in n and "value" not in n and "bands" not in n:
        return "Network Stats"
    # Supply
    if "total supply" in n or "new supply" in n:
        return "Supply"
    # Addresses
    if "active addresses" in n or "active sending" in n or "active receiving" in n:
        return "Addresses"
    # Transactions
    if "tokens transferred" in n or "transaction count" in n:
        return "Transactions"
    # Exchange flows (catch-all)
    if "exchange" in n:
        return "Exchange Flows"
    return "_Needs_Review"


def classify_eth(filename: str) -> str:
    n = _norm(filename)
    # ETH 2.0 / staking
    if any(
        x in n
        for x in (
            "eth 2.0",
            "staking",
            "cumulative txs to eth 2.0",
            "phase 0",
            "total value staked",
            "new depositors",
            "unique depositors",
            "number of eth 2.0 deposits",
        )
    ):
        return "ETH 2.0"
    # Derivatives
    if "open interest" in n or "funding rates" in n or "liquidations" in n or "estimated leverage" in n:
        return "Derivatives"
    if "futures taker cvd" in n:
        return "Derivatives"
    # Fund data
    if "fund holdings" in n or "fund volume" in n or "fund market premium" in n or "fund price" in n:
        return "Fund Data"
    if "coinbase premium" in n or "korea premium" in n:
        return "Fund Data"
    # Fees
    if "fees" in n:
        return "Fees And Revenue"
    # Market data
    if "market cap" in n or "price & volume" in n:
        return "Market Data"
    if "taker buy" in n or "taker sell" in n or "taker buy sell ratio" in n:
        return "Market Data"
    # Flow indicator
    if "exchange supply ratio" in n:
        return "Flow Indicator"
    # Network stats (chain / contracts aggregate)
    if any(x in n for x in ("number of contracts", "new contracts", "destroyed contracts")):
        return "Network Stats"
    # Addresses
    if "active addresses" in n or "active sending" in n or "active receiving" in n:
        return "Addresses"
    # Transactions (transfers, txs, contract calls)
    if any(
        x in n
        for x in (
            "tokens transferred",
            "transaction count",
            "transactions between",
            "transfers between",
            "transfer count",
            "contract calls",
            "transfers by",
        )
    ):
        return "Transactions"
    # Exchange flows
    if "exchange" in n:
        return "Exchange Flows"
    return "_Needs_Review"


def classify_erc20_stable(filename: str) -> str:
    """USDC / USDT ETH / USDT TRX — ERC20/TRC20 stablecoin nav."""
    n = _norm(filename)
    if "market cap" in n:
        return "Market Data"
    if "exchange supply ratio" in n:
        return "Flow Indicator"
    if "active addresses" in n or "active sending" in n or "active receiving" in n:
        return "Addresses"
    if "total supply" in n or "issued supply" in n or "minted supply" in n or "burned supply" in n:
        return "Supply"
    if any(
        x in n
        for x in (
            "tokens transferred",
            "transfer event count",
            "transaction count",
        )
    ):
        return "Transactions"
    if "exchange" in n:
        return "Exchange Flows"
    return "_Needs_Review"


def classify_wbtc(filename: str) -> str:
    n = _norm(filename)
    if "active addresses" in n or "active sending" in n or "active receiving" in n:
        return "Addresses"
    if "total supply" in n or "velocity" in n:
        return "Supply"
    if "tokens transferred" in n or "transaction count" in n or "transfer count" in n:
        return "Transactions"
    return "_Needs_Review"


def get_classifier(asset_key: str) -> Callable[[str], str]:
    if asset_key == "BTC":
        return classify_btc
    if asset_key == "ETH":
        return classify_eth
    if asset_key in ("USDC", "USDT_ETH", "USDT_TRX"):
        return classify_erc20_stable
    if asset_key == "WBTC":
        return classify_wbtc
    raise ValueError(asset_key)


def allowed_categories(asset_key: str) -> set[str]:
    return set(CATEGORY_ORDER[asset_key]) | {"_Needs_Review"}


def coerce_category(asset_key: str, raw: str) -> str:
    allowed = allowed_categories(asset_key)
    if raw in allowed:
        return raw
    # Map disallowed to closest bucket for this asset family
    if asset_key in ("USDC", "USDT_ETH", "USDT_TRX"):
        if raw == "Network Indicator":
            return "Flow Indicator"
        if raw in ("Miner Flows", "Inter Entity Flows"):
            return "Exchange Flows"
    if asset_key == "WBTC":
        if raw in ("Market Data", "Network Stats"):
            return "Transactions"
    if asset_key == "ETH" and raw == "Network Indicator":
        return "Market Indicator"
    if raw not in allowed and raw != "_Needs_Review":
        return "_Needs_Review"
    return raw


def metric_display_name(asset_key: str, filename: str) -> str:
    stem = _strip_day_suffix(filename)
    prefixes = (
        "Bitcoin ",
        "Ethereum ",
        "USD Coin(ERC20) ",
        "Tether USD(ERC20) ",
        "Tether USD(TRC20) ",
        "Wrapped BTC ",
    )
    for p in prefixes:
        if stem.startswith(p):
            stem = stem[len(p) :]
            break
    return stem.strip()


def read_datetime_bounds(path: Path) -> tuple[str | None, str | None]:
    """Min/max UTC date (YYYY-MM-DD) from Datetime column."""
    min_dt: datetime | None = None
    max_dt: datetime | None = None
    try:
        with path.open("r", encoding="utf-8-sig", newline="") as f:
            reader = csv.reader(f)
            header = next(reader, None)
            if not header:
                return None, None
            try:
                idx = next(i for i, h in enumerate(header) if h.strip().lower() == "datetime")
            except StopIteration:
                idx = 0
            for row in reader:
                if not row or idx >= len(row):
                    continue
                s = row[idx].strip()
                if not s:
                    continue
                try:
                    if s.endswith("Z"):
                        dt = datetime.fromisoformat(s.replace("Z", "+00:00"))
                    else:
                        dt = datetime.fromisoformat(s)
                    if dt.tzinfo is None:
                        dt = dt.replace(tzinfo=timezone.utc)
                    else:
                        dt = dt.astimezone(timezone.utc)
                except ValueError:
                    continue
                if min_dt is None or dt < min_dt:
                    min_dt = dt
                if max_dt is None or dt > max_dt:
                    max_dt = dt
    except OSError:
        return None, None
    if min_dt is None or max_dt is None:
        return None, None
    return min_dt.strftime("%Y-%m-%d"), max_dt.strftime("%Y-%m-%d")


def file_sha256(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as f:
        for chunk in iter(lambda: f.read(1 << 20), b""):
            h.update(chunk)
    return h.hexdigest()


def dedupe_trx_inflow_duplicates(folder: Path) -> list[str]:
    """Remove TRC20 duplicate Inflow (Total) if identical to base file."""
    logs: list[str] = []
    a = folder / "Tether USD(TRC20) Exchange Inflow (Total) - All Exchanges - Day.csv"
    b = folder / "Tether USD(TRC20) Exchange Inflow (Total) - All Exchanges - Day (1).csv"
    if not a.is_file() or not b.is_file():
        return logs
    if file_sha256(a) == file_sha256(b):
        b.unlink()
        logs.append(f"Removed duplicate (identical): {b.name}")
    else:
        logs.append(f"WARNING: duplicates differ, keeping both: {a.name} vs {b.name}")
    return logs


def sort_key_category(asset_key: str, category: str) -> tuple[int, str]:
    order = CATEGORY_ORDER.get(asset_key, [])
    try:
        idx = order.index(category)
    except ValueError:
        idx = 999
    return (idx, category)


@dataclass
class MetricRow:
    display: str
    category: str
    start: str | None
    end: str | None
    relpath: str


def collect_csv_paths(asset_dir: Path) -> list[Path]:
    """All CSVs under asset_dir except metrics txt."""
    out: list[Path] = []
    for p in asset_dir.rglob("*.csv"):
        if p.name in set(METRICS_FILENAMES.values()):
            continue
        out.append(p)
    return sorted(out, key=lambda x: str(x).lower())


def move_files_to_categories(asset_key: str, asset_dir: Path, classifier: Callable[[str], str]) -> list[str]:
    logs: list[str] = []
    allowed = allowed_categories(asset_key) - {"_Needs_Review"}
    for path in list(asset_dir.glob("*.csv")):
        if path.name in METRICS_FILENAMES.values():
            continue
        cat = coerce_category(asset_key, classifier(path.name))
        if cat not in allowed and cat != "_Needs_Review":
            cat = "_Needs_Review"
        dest_dir = asset_dir / cat
        dest_dir.mkdir(parents=True, exist_ok=True)
        dest = dest_dir / path.name
        if dest.resolve() == path.resolve():
            continue
        if dest.exists():
            logs.append(f"SKIP exists: {dest}")
            continue
        shutil.move(str(path), str(dest))
        logs.append(f"MOVED {path.name} -> {cat}/")
    return logs


def write_metrics_file(asset_key: str, asset_dir: Path) -> None:
    order = CATEGORY_ORDER[asset_key]
    metrics_name = METRICS_FILENAMES[asset_key]
    rows: list[MetricRow] = []
    for path in collect_csv_paths(asset_dir):
        rel = str(path.relative_to(asset_dir)).replace("\\", "/")
        cat = path.parent.name
        display = metric_display_name(asset_key, path.name)
        start, end = read_datetime_bounds(path)
        rows.append(
            MetricRow(
                display=display,
                category=cat,
                start=start,
                end=end,
                relpath=rel,
            )
        )

    def sort_key(m: MetricRow) -> tuple[int, str]:
        sk = sort_key_category(asset_key, m.category)
        return (sk[0], m.display.lower())

    rows.sort(key=sort_key)

    out_path = asset_dir / metrics_name
    lines: list[str] = []
    for m in rows:
        sd = m.start or "?"
        ed = m.end or "?"
        lines.append(
            f"{m.display}    Category: {m.category}    [Start Date: {sd} End Date: {ed}]"
        )
    out_path.write_text("\n".join(lines) + ("\n" if lines else ""), encoding="utf-8")


def regenerate_all_metrics() -> None:
    for asset_key, asset_dir in ASSET_DIRS.items():
        if asset_dir.is_dir():
            write_metrics_file(asset_key, asset_dir)


def main() -> None:
    all_logs: list[str] = []
    # Pre-dedupe USDT TRX at root before moves
    trx = ASSET_DIRS["USDT_TRX"]
    if trx.is_dir():
        all_logs.extend(dedupe_trx_inflow_duplicates(trx))
        # Also under Exchange Flows if re-run
        sub = trx / "Exchange Flows"
        if sub.is_dir():
            all_logs.extend(dedupe_trx_inflow_duplicates(sub))

    # Dedupe BTC Exchange Inflow CDD duplicate if present
    btc = ASSET_DIRS["BTC"]
    if btc.is_dir():
        a = btc / "Bitcoin Exchange Inflow CDD - All Exchanges - Day.csv"
        b = btc / "Bitcoin Exchange Inflow CDD - All Exchanges - Day (1).csv"
        if a.is_file() and b.is_file():
            if file_sha256(a) == file_sha256(b):
                b.unlink()
                all_logs.append(f"Removed duplicate (identical): {b.name}")
            else:
                all_logs.append(f"WARNING: BTC CDD duplicates differ, keeping both")

    for asset_key, asset_dir in ASSET_DIRS.items():
        if not asset_dir.is_dir():
            all_logs.append(f"Missing dir: {asset_dir}")
            continue
        clf = get_classifier(asset_key)
        all_logs.append(f"=== {asset_key} ===")
        all_logs.extend(move_files_to_categories(asset_key, asset_dir, clf))
        write_metrics_file(asset_key, asset_dir)

    print("\n".join(all_logs))


if __name__ == "__main__":
    import sys

    if len(sys.argv) > 1 and sys.argv[1] == "--metrics-only":
        regenerate_all_metrics()
    else:
        main()
