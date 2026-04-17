"""Fetch the Alternative.me Crypto Fear & Greed Index into Data/AlternativeMe/.

The upstream endpoint returns pseudo-JSON that embeds a raw CSV between
`"data": [` and `],` markers (the CSV is NOT a JSON string — it's inlined
with literal newlines, so the blob isn't parseable as JSON):

    {
        "name": "Fear and Greed Index",
        "data": [
    fng_value,fng_classification,date
    04-17-2026,21,Extreme Fear
    ...
        ],
        "metadata": {"error": null}
    }

Also: the CSV header row is MISLABELED. Header reads
`fng_value,fng_classification,date` but the columns are actually in the order
`date (MM-DD-YYYY), fng_value (int), fng_classification (label)`. We override
the bogus header with our own column names.

Steps:
1. GET with limit=0 (full history) and date_format=us (MM-DD-YYYY).
2. Slice the text between `"data": [` and `],` to get the raw CSV body.
3. Drop the mislabeled header row and parse with explicit column names.
4. Convert `date` to ISO YYYY-MM-DD, dedupe/sort, write
   Data/AlternativeMe/fear_greed_index__daily.csv + README.md.
"""
from __future__ import annotations

import io
import re
import sys
from datetime import datetime, timezone
from pathlib import Path

import pandas as pd
import requests

ROOT = Path(__file__).resolve().parents[2]
OUT_DIR = ROOT / "Data" / "AlternativeMe"
URL = "https://api.alternative.me/fng/?limit=0&format=csv&date_format=us"


_DATA_BLOCK = re.compile(r'"data"\s*:\s*\[(.*?)\]\s*,\s*"metadata"', re.DOTALL)


def _extract_inner_csv(raw_text: str) -> str:
    """Slice out the raw CSV that lives between `"data": [` and `], "metadata"`.

    The upstream response is pseudo-JSON: the CSV is inlined with literal
    newlines and is NOT a JSON string, so `json.loads` fails. We fall back to
    regex slicing which is robust against this.
    """
    m = _DATA_BLOCK.search(raw_text)
    if not m:
        # Last-ditch: maybe they fixed the format and sent real JSON or raw CSV.
        if raw_text.lstrip().lower().startswith("fng_value") or "Extreme Fear" in raw_text:
            return raw_text
        raise ValueError("Could not find CSV data block in Alternative.me response.")
    return m.group(1).strip()


def _normalize(csv_text: str) -> pd.DataFrame:
    """Parse raw CSV. Header row is mislabeled; override with actual column order."""
    # Strip the bogus header line if present.
    lines = [ln for ln in csv_text.splitlines() if ln.strip()]
    if lines and lines[0].lower().startswith("fng_value"):
        lines = lines[1:]
    clean_csv = "\n".join(lines)
    df = pd.read_csv(
        io.StringIO(clean_csv),
        header=None,
        names=["date", "fng_value", "fng_classification"],
        dtype=str,
    )
    df["date"] = pd.to_datetime(df["date"], format="%m-%d-%Y", errors="coerce")
    df = df.dropna(subset=["date"]).copy()
    df["date"] = df["date"].dt.strftime("%Y-%m-%d")
    df["fng_value"] = pd.to_numeric(df["fng_value"], errors="coerce").astype("Int64")
    df["fng_classification"] = df["fng_classification"].astype(str).str.strip()
    df = (
        df[["date", "fng_value", "fng_classification"]]
        .drop_duplicates(subset=["date"])
        .sort_values("date")
        .reset_index(drop=True)
    )
    return df


def _write_csv(df: pd.DataFrame, path: Path) -> None:
    buf = io.StringIO()
    df.to_csv(buf, index=False, lineterminator="\n")
    path.write_bytes(buf.getvalue().encode("utf-8"))


def _build_readme(df: pd.DataFrame) -> str:
    now = datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M:%SZ")
    sample = df.head(2).to_csv(index=False, lineterminator="\n").strip()
    start = df["date"].iloc[0] if len(df) else "—"
    end = df["date"].iloc[-1] if len(df) else "—"
    return (
        "# AlternativeMe — Crypto Fear & Greed Index\n"
        "\n"
        "**Source**: https://alternative.me/crypto/fear-and-greed-index/  \n"
        "**API**: " + URL + "  \n"
        "**Fetcher**: `tools/data_collection/fetch_fear_greed.py` (re-runnable)\n"
        "\n"
        "A daily 0–100 composite sentiment index for crypto (mostly BTC-weighted). "
        "Blends price volatility, market momentum, social media, surveys, BTC dominance, and search trends. "
        "Useful as a broad, exogenous sentiment control separate from on-chain / positioning data.\n"
        "\n"
        "## Date convention\n"
        "\n"
        "First column is `date` (ISO `YYYY-MM-DD`, ascending, one row per calendar day). "
        "Values are 0–100 (higher = more greed, lower = more fear).\n"
        "\n"
        "## Files\n"
        "\n"
        f"| File | Date range | Rows | Columns |\n"
        f"| --- | --- | ---: | --- |\n"
        f"| `fear_greed_index__daily.csv` | {start} .. {end} | {len(df):,} | `date,fng_value,fng_classification` |\n"
        "\n"
        "## Classification buckets\n"
        "\n"
        "`fng_classification` is Alternative.me's human label for the `fng_value` bucket:\n"
        "\n"
        "- `Extreme Fear` (0–24)\n"
        "- `Fear` (25–49)\n"
        "- `Neutral` (~50)\n"
        "- `Greed` (51–74)\n"
        "- `Extreme Greed` (75–100)\n"
        "\n"
        "## Sample rows\n"
        "\n"
        "```csv\n"
        f"{sample}\n"
        "```\n"
        "\n"
        "---\n"
        f"_Auto-generated on {now} by `tools/data_collection/fetch_fear_greed.py`._\n"
    )


def main() -> None:
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    print(f"  GET {URL}")
    r = requests.get(URL, timeout=60)
    r.raise_for_status()
    csv_text = _extract_inner_csv(r.text)
    df = _normalize(csv_text)
    out = OUT_DIR / "fear_greed_index__daily.csv"
    _write_csv(df, out)
    (OUT_DIR / "README.md").write_text(_build_readme(df), encoding="utf-8")
    print(f"AlternativeMe done: {len(df):,} rows ({df['date'].iloc[0]} .. {df['date'].iloc[-1]}).")


if __name__ == "__main__":
    main()
