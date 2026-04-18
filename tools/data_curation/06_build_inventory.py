"""Step 06: Generate per-folder README.md files, Data/MASTER_DATA.md, Data/MASTER_DATA.txt, Data/MASTER_DATA.csv.

For every CSV under Data/, compute:
- Date range (from `date` column where present).
- Row count, column list.
- Frequency guess (daily / weekly / monthly / snapshot / intraday).
- Missing-day count (only for daily calendar-day files).
- SHA-256 (12-char prefix).
- Two sample rows.

Group by folder and write:
- `<folder>/README.md` — rich, for humans.
- `Data/MASTER_DATA.md`   — single-file overview across all sources.
- `Data/MASTER_DATA.txt`  — same inventory as `.md` plus an LLM-oriented preamble (UTF-8 plain text; best for Perplexity / chat uploads).
- `Data/MASTER_DATA.csv`  — machine-readable master index.
"""
from __future__ import annotations

import csv
import sys
from collections import defaultdict
from datetime import datetime, timedelta, timezone
from pathlib import Path

import pandas as pd

sys.path.insert(0, str(Path(__file__).resolve().parent))

# Preamble for MASTER_DATA.txt — optimized for LLM attachments (plain text, no PDF/DOCX parsing).
_LLM_TXT_PREAMBLE = """\
================================================================================
MASTER DATA INVENTORY — context for research LLMs (e.g. Perplexity Pro)
================================================================================
What this is
  Single canonical index of every CSV under Data/ for a crypto quant research
  project: BTC/ETH factor evolution, macro, on-chain, DeFi, ETFs, sentiment.

Recommended use
  • Upload this file as a document in Perplexity (Pro) or similar deep-research chats.
  • Use the same content as MASTER_DATA.md; tables use Markdown pipe syntax.
  • For exact column lists and SHA-256 hashes, also attach Data/MASTER_DATA.csv.

Why .txt (not PDF/DOC)
  Plain UTF-8 text avoids PDF text-extraction errors and Word metadata noise; models
  parse Markdown-style tables reliably.

Data conventions (all time-series CSVs)
  • First column: date — ISO YYYY-MM-DD, ascending.
  • No separate timestamp_utc column.

--------------------------------------------------------------------------------
Inventory body (matches MASTER_DATA.md; regenerated together)
--------------------------------------------------------------------------------

"""
from _common import DATA_DIR, log, rel_to_data, sha256_of_file  # noqa: E402


# =============================================================================
# Source descriptors — human context that can't be inferred from the CSVs alone.
# =============================================================================

SOURCE_DOCS: dict[str, dict] = {
    "Artemis": {
        "url": "https://app.artemis.xyz/",
        "summary": (
            "Cross-chain analytics platform. Exports here are manually downloaded "
            "dashboards covering ETF AUM, perpetuals, DEX activity, lending, "
            "stablecoins, and RWAs."
        ),
        "date_convention": (
            "Each file originally had a quoted `\"DateTime\"` column as "
            "`YYYY-MM-DD 00:00:00`. After curation it is `date` (ISO `YYYY-MM-DD`, UTC, ascending)."
        ),
        "units": "Mixed — USD for AUM / mcap / volumes / TVL, count for addresses, see per-file headers.",
        "licensing": "Artemis Terms of Use; for internal research use.",
        "frequency_hint": "Mostly daily, some monthly aggregates (ETF flows).",
    },
    "CryptoQuant": {
        "url": "https://cryptoquant.com/",
        "summary": (
            "On-chain, derivatives, exchange-flow, and market-indicator data for BTC, ETH, "
            "USDC, USDT (ERC20 / TRC20), and WBTC. Source files are per-metric daily CSVs "
            "exported from the CryptoQuant web UI."
        ),
        "date_convention": (
            "Original column was `Datetime` (ISO `YYYY-MM-DDThh:mm:ssZ`, descending). "
            "After curation each file has `date` (ISO `YYYY-MM-DD`, ascending) as its first column; "
            "the original timestamp column has been dropped (everything is daily granularity)."
        ),
        "units": "Varies per metric; see the existing `<ASSET>_Metrics.txt` inventories.",
        "licensing": "CryptoQuant Terms of Service; for internal research use.",
        "frequency_hint": "All daily.",
        "note": (
            "Derivatives metrics are aggregated across 'All Exchanges, All Symbol'. "
            "Whether CME BTC / ETH futures are included is NOT exposed in the export. "
            "For explicit CME coverage, see `Data/Tradingview/` CME files."
        ),
    },
    "DefiLlama": {
        "url": "https://defillama.com/ + https://api.llama.fi/ (programmatic via harvest_defillama_simple.py)",
        "summary": (
            "All DefiLlama data — programmatic TVL panels plus manual website exports. "
            "Organised into topical subfolders: "
            "`TVL/` (all-chain / per-chain TVL daily and weekly panels), "
            "`Stablecoins/` (market cap time-series + entity lists), "
            "`ETFs/` (flow history + overview snapshot), "
            "`RWA/` (real-world-asset market-cap and TVL by category), "
            "`ChainMetrics/` (chain-level all-in-one dashboards: fees, revenue, volumes, TVL), "
            "`CEX/` (centralized-exchange net inflows by exchange), "
            "`DATs/` (public-company digital-asset-treasuries snapshot)."
        ),
        "date_convention": (
            "Originally mixed (`date`, `Date`, `day`, `Timestamp+Date`). After curation every "
            "time-series file has `date` (ISO `YYYY-MM-DD`, UTC) as its first column. "
            "Snapshot entity lists (`Stablecoins/stablecoins.csv`, `DATs/dat-institutions.csv`, "
            "`ETFs/etf-overview.csv`, `TVL/Snapshot/*`) have no date column."
        ),
        "units": "USD for all flow / mcap / TVL / fees / revenue / volume figures unless stated.",
        "licensing": "DefiLlama data is free and public; attribution is appreciated.",
        "frequency_hint": "Daily for time-series; `TVL/` also has Weekly aggregates; Snapshots are point-in-time.",
        "note": (
            "Multi-part website exports (stablecoin-mcap parts 1..7, cex-inflows parts 1..3) "
            "were merged via outer join on `date`. Originals are archived under `_raw_parts/`. "
            "`TVL/` is the only subfolder managed by `harvest_defillama_simple.py`; the others "
            "are manual UI exports."
        ),
    },
    "Farside ETF Data": {
        "url": "https://farside.co.uk/bitcoin-etf-flow-all-data/ (+ /ethereum/, /sol/)",
        "summary": (
            "Daily US$m net flows for US spot BTC, ETH, and SOL ETFs. "
            "See `Farside_ETF_Data_Summary.txt` for ticker list per asset."
        ),
        "date_convention": (
            "Originally `Date` (`YYYY-MM-DD`, trading-day cadence). After curation the column "
            "is lowercase `date`."
        ),
        "units": "US$m (millions of USD). Empty cells mean 'no flow / not applicable'; "
                 "outflows are negative numbers.",
        "licensing": "Farside publishes daily; treat attribution per their terms.",
        "frequency_hint": "Trading-day daily (NYSE calendar; weekends and holidays absent).",
    },
    "Tradingview": {
        "url": "https://www.tradingview.com/",
        "summary": (
            "Manual chart-to-CSV exports from TradingView. Organised into two subfolders: "
            "`Daily/` (1D bars — CME BTC/ETH/Micro BTC/Micro ETH/SOL futures, CME basis and "
            "ratio series, spot-proxy ETFs, miner/crypto stocks, Deribit DVOL, IBIT/ETHA ETF "
            "premiums, DXY) and `Weekly/` (1W continuous contracts, index ETFs, commodities)."
        ),
        "date_convention": (
            "Originally `time` as Unix epoch seconds. After curation each file has `date` "
            "(ISO `YYYY-MM-DD`, ascending) as its first column — no `timestamp_utc`."
        ),
        "units": "OHLC in instrument quote currency; Volume in contracts / shares; Open Interest in contracts.",
        "licensing": "TradingView chart data is for research use only; redistribution restricted.",
        "frequency_hint": "Daily bars under `Daily/`, weekly bars under `Weekly/`.",
        "note": (
            "These files explicitly cover CME BTC/ETH futures, which CryptoQuant aggregates away. "
            "DXY files were deduplicated by keeping the longest-history version."
        ),
    },
    "FRED": {
        "url": "https://fred.stlouisfed.org/",
        "summary": (
            "Macro / rates / liquidity / sentiment series pulled from the St Louis Fed "
            "`fred/series/observations` endpoint. Each series has its own 2-column CSV "
            "(`date,value`) plus one combined wide panel (`fred_macro_panel__daily.csv`) and "
            "a metadata table (`fred_series_metadata.csv`)."
        ),
        "date_convention": (
            "`date` is ISO `YYYY-MM-DD` ascending. Missing observations (FRED `.` sentinel) "
            "are written as empty cells."
        ),
        "units": "Per-series — see `fred_series_metadata.csv` (column `units`).",
        "licensing": "FRED data is public-domain / Federal Reserve Bank of St. Louis.",
        "frequency_hint": "Mix of daily, weekly, and monthly; the combined panel is daily-aligned.",
        "note": (
            "Re-runnable via `python tools/data_collection/fetch_fred.py` "
            "(requires `FRED_API_KEY` in `.env`)."
        ),
    },
    "AlternativeMe": {
        "url": "https://alternative.me/crypto/fear-and-greed-index/",
        "summary": (
            "Crypto Fear & Greed Index — a daily 0–100 composite sentiment score blending "
            "volatility, momentum, social media, surveys, BTC dominance, and search trends. "
            "Useful as a broad, exogenous sentiment control."
        ),
        "date_convention": "`date` is ISO `YYYY-MM-DD` ascending, one row per calendar day.",
        "units": "`fng_value` is 0–100 integer. `fng_classification` is the bucket label "
                 "(`Extreme Fear`, `Fear`, `Neutral`, `Greed`, `Extreme Greed`).",
        "licensing": "Alternative.me; free with attribution.",
        "frequency_hint": "Daily, calendar-day cadence (no gaps).",
    },
}

# File-name keywords -> inferred topic label (used to produce a short Topic column).
TOPIC_HINTS: list[tuple[str, str]] = [
    # FRED series — prefix with series id for instant recognition.
    ("DGS10", "FRED: 10Y Treasury yield"),
    ("DGS2", "FRED: 2Y Treasury yield"),
    ("DGS30", "FRED: 30Y Treasury yield"),
    ("DFII10", "FRED: 10Y TIPS (real yield)"),
    ("T10Y2Y", "FRED: 10Y-2Y term spread"),
    ("SOFR", "FRED: SOFR overnight rate"),
    ("DFF", "FRED: Fed Funds Effective Rate"),
    ("BAMLH0A0HYM2", "FRED: High-yield OAS spread"),
    ("VIXCLS", "FRED: VIX"),
    ("NFCI", "FRED: Chicago Fed NFCI"),
    ("ANFCI", "FRED: Adjusted NFCI"),
    ("STLFSI4", "FRED: St Louis Financial Stress Index"),
    ("WALCL", "FRED: Fed balance sheet total assets"),
    ("RRPONTSYD", "FRED: Reverse-repo facility"),
    ("DTWEXBGS", "FRED: Broad USD trade-weighted index"),
    ("DCOILWTICO", "FRED: WTI crude oil"),
    ("CPIAUCSL", "FRED: CPI headline"),
    ("UNRATE", "FRED: Unemployment rate"),
    ("USEPUINDXD", "FRED: Economic Policy Uncertainty"),
    ("fred_macro_panel", "FRED: combined daily panel"),
    ("fred_series_metadata", "FRED: series metadata"),
    ("fear_greed_index", "Crypto Fear & Greed index"),
    ("Open Interest", "Open interest"),
    ("Funding Rates", "Funding rates"),
    ("Liquidations", "Liquidations"),
    ("Leverage Ratio", "Estimated leverage ratio"),
    ("Taker CVD", "Taker CVD"),
    ("Coinbase Premium", "Coinbase premium"),
    ("Korea Premium", "Korea premium"),
    ("Fund Holdings", "Fund holdings"),
    ("Fund Price", "Fund price"),
    ("Fund Volume", "Fund volume"),
    ("Fund Market Premium", "Fund market premium"),
    ("MVRV", "MVRV ratio"),
    ("SOPR", "SOPR"),
    ("NVT", "NVT"),
    ("NUPL", "NUPL"),
    ("Puell Multiple", "Puell multiple"),
    ("Realized Cap", "Realized cap"),
    ("Realized Price", "Realized price"),
    ("Market Cap", "Market cap"),
    ("Thermo Cap", "Thermo cap"),
    ("Exchange Reserve", "Exchange reserve"),
    ("Exchange Netflow", "Exchange netflow"),
    ("Exchange Inflow", "Exchange inflow"),
    ("Exchange Outflow", "Exchange outflow"),
    ("Miner Netflow", "Miner netflow"),
    ("Miner Reserve", "Miner reserve"),
    ("Hashrate", "Hashrate"),
    ("Difficulty", "Difficulty"),
    ("Active Addresses", "Active addresses"),
    ("UTXO", "UTXO metrics"),
    ("Taker Buy", "Taker buy volume"),
    ("Taker Sell", "Taker sell volume"),
    ("Price & Volume", "Price & volume"),
    ("Fees", "Fees"),
    ("Stablecoin", "Stablecoin"),
    ("ETF", "ETF"),
    ("CME_BTC", "CME BTC futures"),
    ("CME_ETH", "CME ETH futures"),
    ("Micro_Bitcoin", "CME Micro BTC futures"),
    ("Micro_Ether", "CME Micro ETH futures"),
    ("SOL", "Solana"),
    ("DVOL", "Deribit volatility index"),
    ("IBIT", "BlackRock IBIT ETF"),
    ("ETHA", "BlackRock ETHA ETF"),
    ("TVL", "TVL"),
    ("dat-", "Public-company digital-asset treasuries"),
    ("rwa-", "Real-world assets (RWA)"),
    ("cex_net_inflows", "CEX net inflows"),
    ("stablecoin_mcap", "Stablecoin market cap"),
]


def infer_topic(name: str) -> str:
    low = name.lower()
    for kw, topic in TOPIC_HINTS:
        if kw.lower() in low:
            return topic
    stem = Path(name).stem
    return stem


def guess_frequency(dates: pd.Series) -> str:
    if dates.empty:
        return "snapshot"
    unique = pd.to_datetime(dates.drop_duplicates().sort_values())
    if len(unique) < 2:
        return "snapshot"
    deltas = unique.diff().dropna().dt.days
    if deltas.empty:
        return "intraday"
    med = int(deltas.median())
    if med <= 1:
        return "daily"
    if med in range(6, 9):
        return "weekly"
    if med in range(25, 35):
        return "monthly"
    return f"~{med}d"


def count_missing_days(dates: pd.Series) -> int | None:
    """Missing calendar days between min and max date. None if not daily / single-date."""
    if dates.empty:
        return None
    d = pd.to_datetime(dates.drop_duplicates().sort_values())
    if len(d) < 2:
        return None
    deltas = d.diff().dropna().dt.days
    # Only compute for daily files.
    if int(deltas.median()) > 2:
        return None
    expected = int((d.max() - d.min()).days) + 1
    missing = expected - len(d)
    return max(0, missing)


def sample_rows_text(df: pd.DataFrame, n: int = 2) -> str:
    cols = list(df.columns)
    sub = df.head(n)
    # Truncate wide rows for legibility in markdown code blocks.
    max_cols = 10
    if len(cols) > max_cols:
        cols = cols[:max_cols]
        sub = sub.iloc[:, :max_cols]
        header = ",".join(cols) + ",... (+{} more)".format(len(df.columns) - max_cols)
    else:
        header = ",".join(cols)
    rows = [header]
    for _, r in sub.iterrows():
        vals = []
        for c in cols:
            v = r[c]
            if pd.isna(v):
                vals.append("")
            else:
                s = str(v)
                if len(s) > 40:
                    s = s[:37] + "..."
                vals.append(s)
        rows.append(",".join(vals))
    return "\n".join(rows)


def summarize_file(path: Path) -> dict:
    """Read a CSV (lightly) and produce a dict of summary fields."""
    info: dict = {
        "relpath": rel_to_data(path),
        "size_bytes": path.stat().st_size,
        "sha256_12": sha256_of_file(path)[:12],
        "topic": infer_topic(path.name),
    }
    try:
        df = pd.read_csv(path, nrows=200000)  # ample for our files
    except Exception as e:
        info["error"] = f"read failed: {e}"
        return info
    info["row_count"] = len(df)
    info["col_count"] = len(df.columns)
    info["columns"] = list(df.columns)
    if "date" in df.columns:
        d = pd.to_datetime(df["date"], errors="coerce").dropna()
        if len(d) > 0:
            info["start"] = d.min().strftime("%Y-%m-%d")
            info["end"] = d.max().strftime("%Y-%m-%d")
            info["frequency"] = guess_frequency(df["date"])
            info["missing_days"] = count_missing_days(df["date"])
        else:
            info["frequency"] = "snapshot"
    else:
        info["frequency"] = "snapshot"
    info["sample"] = sample_rows_text(df, n=2)
    return info


# =============================================================================
# README generation
# =============================================================================

def _folder_source(rel: str) -> str:
    return rel.split("/", 1)[0]


def _build_folder_readme(folder_rel: str, files: list[dict]) -> str:
    source = _folder_source(folder_rel)
    doc = SOURCE_DOCS.get(source, {})
    sub = folder_rel[len(source):].lstrip("/")
    title = f"{source}" + (f" / {sub}" if sub else "")

    lines: list[str] = [f"# {title}", ""]
    if doc:
        lines.append(f"**Source**: {doc.get('url', '')}")
        lines.append("")
        lines.append(doc.get("summary", ""))
        lines.append("")
        lines.append(f"**Date convention**: {doc.get('date_convention', '')}")
        lines.append("")
        lines.append(f"**Units**: {doc.get('units', '')}")
        lines.append("")
        if doc.get("note"):
            lines.append(f"> Note: {doc['note']}")
            lines.append("")
        lines.append(f"**Frequency hint**: {doc.get('frequency_hint', '')}")
        lines.append("")
        lines.append(f"**Licensing**: {doc.get('licensing', '')}")
        lines.append("")

    lines.append(f"## Files ({len(files)})")
    lines.append("")
    lines.append("| File | Topic | Date range | Rows | Freq | Missing days | Cols | SHA |")
    lines.append("| --- | --- | --- | ---: | --- | ---: | ---: | --- |")
    for f in sorted(files, key=lambda x: x["relpath"].lower()):
        name = f["relpath"].rsplit("/", 1)[-1]
        topic = f.get("topic", "")
        if "start" in f and "end" in f:
            drange = f"{f['start']} .. {f['end']}"
        else:
            drange = "—"
        rows = f.get("row_count", "—")
        freq = f.get("frequency", "—")
        miss = f.get("missing_days")
        miss_s = "—" if miss is None else str(miss)
        cols_n = f.get("col_count", "—")
        sha = f.get("sha256_12", "")
        lines.append(
            f"| `{name}` | {topic} | {drange} | {rows:,} | {freq} | {miss_s} | {cols_n} | `{sha}` |"
            if isinstance(rows, int)
            else f"| `{name}` | {topic} | {drange} | {rows} | {freq} | {miss_s} | {cols_n} | `{sha}` |"
        )
    lines.append("")

    # Sample rows block (first 6 files to keep readme readable)
    lines.append("## Sample rows (first 2 rows per file — truncated to 10 columns)")
    lines.append("")
    for f in sorted(files, key=lambda x: x["relpath"].lower())[:12]:
        name = f["relpath"].rsplit("/", 1)[-1]
        lines.append(f"**`{name}`**")
        lines.append("")
        lines.append("```csv")
        lines.append(f.get("sample", ""))
        lines.append("```")
        lines.append("")
    if len(files) > 12:
        lines.append(
            f"_({len(files) - 12} more files in this folder — see the table above or the master inventory.)_"
        )
        lines.append("")

    lines.append("---")
    lines.append(
        f"_Auto-generated on {datetime.now(timezone.utc).strftime('%Y-%m-%d')} by "
        f"`tools/data_curation/06_build_inventory.py`. Regenerate after any data refresh._"
    )
    return "\n".join(lines) + "\n"


def _build_master_md(by_source: dict, all_summaries: list[dict]) -> str:
    lines: list[str] = [
        "# Master Data Inventory",
        "",
        "This file is the single-page index of every CSV under `Data/`. "
        "It is intended for two audiences:",
        "",
        "1. **Teammates** — to know what data exists, what dates it covers, and where to find it.",
        "2. **Downstream AI / scripts** — paired with `MASTER_DATA.csv`, this is a machine-readable inventory.",
        "",
        "Mission context (from `Manager_Outline.md`): comparative BTC/ETH factor-evolution research "
        "around post-ETF institutionalization, using macro, institutional, crypto-liquidity, and on-chain factor blocks.",
        "",
        "All time-series CSVs have been normalized to:",
        "",
        "- `date` as the first column (ISO `YYYY-MM-DD`, UTC calendar, ascending).",
        "- **No `timestamp_utc` column** — everything is collapsed to daily granularity.",
        "- Deduplicated on `date` for wide (one-row-per-day) panels; long-format files may keep duplicate dates by design.",
        "- UTF-8, LF line endings, no BOM.",
        "",
        "## Sources",
        "",
        "| Source | Files | Rows total | Date span | Primary kind |",
        "| --- | ---: | ---: | --- | --- |",
    ]
    for src, entries in sorted(by_source.items()):
        rows_total = sum(e.get("row_count", 0) for e in entries if isinstance(e.get("row_count"), int))
        starts = [e["start"] for e in entries if "start" in e]
        ends = [e["end"] for e in entries if "end" in e]
        span = f"{min(starts)} .. {max(ends)}" if starts and ends else "—"
        freqs = [e.get("frequency", "") for e in entries]
        kind_primary = max(set(freqs), key=freqs.count) if freqs else "—"
        lines.append(
            f"| `{src}/` | {len(entries)} | {rows_total:,} | {span} | {kind_primary} |"
        )
    lines.append("")

    # Factor-block mapping cheat sheet (from Manager_Outline.md)
    lines.extend([
        "## Factor-block mapping (for quick teammate orientation)",
        "",
        "| Factor block | Primary sources |",
        "| --- | --- |",
        "| Macro / rates / liquidity | `FRED/` (rates curve, VIX, financial-conditions indices, Fed balance sheet, RRP, DXY, WTI), `Tradingview/Daily/DXY`, `Tradingview/Weekly/SPY/QQQ/IWM/GLD/XAUUSD` |",
        "| Sentiment | `AlternativeMe/fear_greed_index__daily.csv`, `FRED/USEPUINDXD`, `Tradingview/.../DVOL` |",
        "| Institutional (ETF / DAT) | `Farside ETF Data/`, `Artemis/` ETF AUMs, `DefiLlama/ETFs/`, `DefiLlama/DATs/` |",
        "| Crypto-liquidity | `DefiLlama/TVL/`, `DefiLlama/Stablecoins/`, `DefiLlama/CEX/`, `DefiLlama/ChainMetrics/`, Artemis chain/DEX/lending metrics |",
        "| BTC-native | `CryptoQuant/BTC/` (all subfolders), `Tradingview/Daily/` and `Tradingview/Weekly/` CME BTC futures |",
        "| ETH-native | `CryptoQuant/ETH/` (all subfolders), `Tradingview/` CME ETH futures, Artemis chain metrics |",
        "",
    ])

    # Per-source full file listings.
    lines.append("## Full file index")
    lines.append("")
    for src, entries in sorted(by_source.items()):
        doc = SOURCE_DOCS.get(src, {})
        lines.append(f"### {src}")
        lines.append("")
        if doc:
            lines.append(doc.get("summary", ""))
            lines.append("")
        lines.append("| Relative path | Topic | Date range | Rows | Freq | Missing days | Cols |")
        lines.append("| --- | --- | --- | ---: | --- | ---: | ---: |")
        for e in sorted(entries, key=lambda x: x["relpath"].lower()):
            drange = f"{e['start']} .. {e['end']}" if "start" in e and "end" in e else "—"
            rows = e.get("row_count", "—")
            miss = e.get("missing_days")
            miss_s = "—" if miss is None else str(miss)
            lines.append(
                f"| `{e['relpath']}` | {e.get('topic','')} | {drange} | "
                f"{rows:,} | {e.get('frequency','—')} | {miss_s} | {e.get('col_count','—')} |"
                if isinstance(rows, int)
                else f"| `{e['relpath']}` | {e.get('topic','')} | {drange} | "
                     f"{rows} | {e.get('frequency','—')} | {miss_s} | {e.get('col_count','—')} |"
            )
        lines.append("")

    # One-sample-row-per-file appendix is too long (450+ files); reference the CSV.
    lines.append("## Machine-readable version")
    lines.append("")
    lines.append(
        "The same information (plus column lists and SHA-256) is in "
        "`Data/MASTER_DATA.csv` for programmatic consumption."
    )
    lines.append("")
    lines.append(
        "For **LLM / chat attachments** (e.g. Perplexity Pro deep research), prefer "
        "`Data/MASTER_DATA.txt`: same inventory as this file, UTF-8 plain text with a "
        "short usage preamble — avoids PDF/DOCX extraction issues."
    )
    lines.append("")
    lines.append(
        f"_Auto-generated on {datetime.now(timezone.utc).strftime('%Y-%m-%d')} by "
        f"`tools/data_curation/06_build_inventory.py`._"
    )
    return "\n".join(lines) + "\n"


def _build_master_txt(master_md: str) -> str:
    """Same body as MASTER_DATA.md with a plain-text preamble for LLM uploads."""
    return _LLM_TXT_PREAMBLE + master_md


def main() -> None:
    # 1. Collect all CSVs (skip hidden / meta / archive / quarantine)
    all_csvs: list[Path] = []
    for p in sorted(DATA_DIR.rglob("*.csv")):
        rel = rel_to_data(p)
        if rel.startswith("_meta/") or rel.startswith("_quarantine/"):
            continue
        if "_raw_parts/" in rel:
            continue
        # Skip self-generated inventory file at Data/ root; it is not a data source.
        if rel in ("MASTER_DATA.csv",):
            continue
        all_csvs.append(p)

    # 2. Summarize each
    summaries: list[dict] = []
    for i, p in enumerate(all_csvs, 1):
        if i % 50 == 0:
            print(f"  [{i}/{len(all_csvs)}] ...")
        summaries.append(summarize_file(p))

    # 3. Group by directory (for per-folder README) and by source (for master)
    by_dir: dict[str, list[dict]] = defaultdict(list)
    by_source: dict[str, list[dict]] = defaultdict(list)
    for s in summaries:
        folder_rel = s["relpath"].rsplit("/", 1)[0] if "/" in s["relpath"] else ""
        by_dir[folder_rel].append(s)
        by_source[_folder_source(s["relpath"])].append(s)

    # 4. Write per-folder READMEs (skip Data/ root — the master files live there instead).
    readmes_written = 0
    for folder_rel, files in by_dir.items():
        if folder_rel == "":
            continue
        # Skip archive folders — they have raw parts, not canonical files.
        if "/_raw_parts" in ("/" + folder_rel):
            continue
        folder_path = DATA_DIR / folder_rel if folder_rel else DATA_DIR
        if not folder_path.is_dir():
            continue
        text = _build_folder_readme(folder_rel, files)
        (folder_path / "README.md").write_text(text, encoding="utf-8")
        readmes_written += 1

    # Remove any stale Data/README.md from a previous run.
    stale = DATA_DIR / "README.md"
    if stale.is_file():
        stale.unlink()

    # A lightweight README for each _raw_parts archive folder.
    for src in by_source:
        archive = DATA_DIR / src / "_raw_parts"
        if archive.is_dir():
            note = (
                f"# {src} / _raw_parts\n\n"
                "This folder preserves the **original multi-part downloads** that were merged "
                "into canonical CSVs in the parent folder. Keep them as an audit trail; do not "
                "use them directly for analysis (use the merged canonical files instead).\n\n"
                "See `../README.md` for the merged files.\n"
            )
            (archive / "README.md").write_text(note, encoding="utf-8")
            readmes_written += 1

    # 5. Write master markdown + LLM-friendly plain-text copy
    master_md = _build_master_md(by_source, summaries)
    (DATA_DIR / "MASTER_DATA.md").write_text(master_md, encoding="utf-8")
    (DATA_DIR / "MASTER_DATA.txt").write_text(_build_master_txt(master_md), encoding="utf-8")

    # 6. Write master CSV
    csv_path = DATA_DIR / "MASTER_DATA.csv"
    fieldnames = [
        "source",
        "relpath",
        "topic",
        "start_date",
        "end_date",
        "row_count",
        "col_count",
        "frequency",
        "missing_days",
        "size_bytes",
        "sha256_12",
        "columns",
    ]
    with csv_path.open("w", encoding="utf-8", newline="") as f:
        w = csv.DictWriter(f, fieldnames=fieldnames)
        w.writeheader()
        for s in sorted(summaries, key=lambda x: x["relpath"].lower()):
            w.writerow({
                "source": _folder_source(s["relpath"]),
                "relpath": s["relpath"],
                "topic": s.get("topic", ""),
                "start_date": s.get("start", ""),
                "end_date": s.get("end", ""),
                "row_count": s.get("row_count", ""),
                "col_count": s.get("col_count", ""),
                "frequency": s.get("frequency", ""),
                "missing_days": s.get("missing_days") if s.get("missing_days") is not None else "",
                "size_bytes": s.get("size_bytes", ""),
                "sha256_12": s.get("sha256_12", ""),
                "columns": "|".join(s.get("columns", [])),
            })

    log(
        "Step 06 — build inventory",
        [
            f"Summarized {len(summaries)} CSV files.",
            f"Wrote {readmes_written} per-folder README.md files.",
            "Wrote `Data/MASTER_DATA.md`.",
            "Wrote `Data/MASTER_DATA.txt`.",
            "Wrote `Data/MASTER_DATA.csv`.",
        ],
    )
    print(f"Step 06 done: {len(summaries)} files, {readmes_written} READMEs.")


if __name__ == "__main__":
    main()
