#!/usr/bin/env python3
"""Download Farside Investors ETF flow tables and write CSVs."""
from __future__ import annotations

import csv
import re
from datetime import datetime
from pathlib import Path
from urllib.request import Request, urlopen

from bs4 import BeautifulSoup

UA = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
DATE_RE = re.compile(r"^\d{1,2}\s+\w+\s+\d{4}$")


def fetch_html(url: str) -> str:
    req = Request(url, headers={"User-Agent": UA})
    with urlopen(req, timeout=120) as resp:
        return resp.read().decode("utf-8", "replace")


def parse_flow_cell(raw: str) -> str:
    """Return CSV-safe string; empty for '-'; numeric string for numbers (negatives without parens)."""
    s = raw.strip()
    if not s or s == "-":
        return ""
    s = s.replace("*", "").replace(",", "")
    m = re.fullmatch(r"\((.+)\)", s)
    if m:
        inner = m.group(1).strip()
        return f"-{inner}" if inner else ""
    return s


def parse_btc(soup: BeautifulSoup) -> tuple[list[str], list[list[str]]]:
    table = soup.find_all("table")[1]
    rows = table.find_all("tr", recursive=True)
    headers: list[str] | None = None
    for tr in rows:
        cells = tr.find_all(["th", "td"], recursive=False)
        vals = [c.get_text(strip=True) for c in cells]
        if vals and vals[0] == "Date":
            headers = vals
            break
    if not headers:
        raise ValueError("BTC: missing header row")

    data: list[list[str]] = []
    for tr in rows:
        tds = tr.find_all("td", recursive=False)
        if not tds:
            continue
        first = tds[0].get_text(strip=True)
        if not DATE_RE.match(first):
            continue
        line = [first] + [parse_flow_cell(c.get_text(strip=True)) for c in tds[1:]]
        data.append(line)
    return headers, data


def parse_eth(soup: BeautifulSoup) -> tuple[list[str], list[list[str]]]:
    table = soup.find_all("table")[1]
    rows = table.find_all("tr", recursive=True)
    # Row 1: tickers; first cell empty, last may be empty (Total from row 0)
    tickers: list[str] | None = None
    for tr in rows:
        cells = tr.find_all(["th", "td"], recursive=False)
        vals = [c.get_text(strip=True) for c in cells]
        if len(vals) > 2 and vals[1] == "ETHA":
            tickers = vals[1:]
            break
    if not tickers:
        raise ValueError("ETH: missing ticker row")

    headers = ["Date"] + [t if t else "Total" for t in tickers]

    data: list[list[str]] = []
    for tr in rows:
        tds = tr.find_all("td", recursive=False)
        if not tds:
            continue
        first = tds[0].get_text(strip=True)
        if not DATE_RE.match(first):
            continue
        line = [first] + [parse_flow_cell(c.get_text(strip=True)) for c in tds[1:]]
        data.append(line)
    return headers, data


def to_iso_date(dmy: str) -> str:
    dt = datetime.strptime(dmy, "%d %b %Y")
    return dt.strftime("%Y-%m-%d")


def write_csv(path: Path, headers: list[str], data: list[list[str]]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8", newline="") as f:
        w = csv.writer(f)
        w.writerow(headers)
        for row in data:
            w.writerow([to_iso_date(row[0])] + row[1:])


def main() -> None:
    root = Path(__file__).resolve().parents[1]
    out_btc = root / "Farside ETF Data" / "BTC" / "bitcoin_etf_flow_all_data.csv"
    out_eth = root / "Farside ETF Data" / "ETH" / "ethereum_etf_flow_all_data.csv"

    url_btc = "https://farside.co.uk/bitcoin-etf-flow-all-data/"
    url_eth = "https://farside.co.uk/ethereum-etf-flow-all-data/"

    h_btc, d_btc = parse_btc(BeautifulSoup(fetch_html(url_btc), "html.parser"))
    h_eth, d_eth = parse_eth(BeautifulSoup(fetch_html(url_eth), "html.parser"))

    write_csv(out_btc, h_btc, d_btc)
    write_csv(out_eth, h_eth, d_eth)

    print(f"Wrote {out_btc} ({len(d_btc)} rows)")
    print(f"Wrote {out_eth} ({len(d_eth)} rows)")


if __name__ == "__main__":
    main()
