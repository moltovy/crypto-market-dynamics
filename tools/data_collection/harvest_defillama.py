#!/usr/bin/env python3
"""Research-focused DefiLlama CSV harvester.

Creates clean daily and weekly CSV panels for crypto research. The CSV files do
not include API plumbing columns; they are intended for statistical analysis.
"""
from __future__ import annotations

import argparse
import csv
import json
import os
import random
import re
import shutil
import tempfile
import time
from concurrent.futures import ThreadPoolExecutor, as_completed
from datetime import datetime, timezone
from pathlib import Path
from typing import Any
from urllib.parse import quote

import pandas as pd
import requests


ROOT = Path(__file__).resolve().parent
TODAY = datetime.now(timezone.utc).strftime("%Y-%m-%d")
RETRY_STATUSES = {408, 425, 429, 500, 502, 503, 504}
FLOW_WORDS = ("fees", "revenue", "volume", "flows", "premium", "notional", "inflows", "outflows", "transactions")
DATE_COLUMNS = ["Date", "date", "timestamp", "time", "day"]


def parse_args() -> argparse.Namespace:
    p = argparse.ArgumentParser(description="Create DefiLlama research CSVs.")
    p.add_argument("--mode", choices=["full", "update"], default="full")
    # NOTE (2026-04-18): the OpenAPI spec was moved during the repo reorg from
    # the project root to archive/defillama_openapi_2026-04-14.json. Default is
    # kept in sync with config/curation_snapshots.yml -> harvester.default_spec_path.
    p.add_argument("--spec", default="archive/defillama_openapi_2026-04-14.json")
    p.add_argument("--out", default="Data/DefiLlama/TVL")
    p.add_argument("--overlap-days", type=int, default=7)
    p.add_argument("--max-workers", type=int, default=5)
    p.add_argument("--timeout", type=float, default=60.0)
    p.add_argument("--sleep", type=float, default=0.15)
    p.add_argument("--top-pools", type=int, default=750, help="Yield pool histories to pull by TVL; 0 means all pools.")
    p.add_argument("--top-protocols", type=int, default=0, help="Protocol TVL histories to pull by TVL; 0 means all protocols.")
    return p.parse_args()


def safe_name(value: Any, max_len: int = 120) -> str:
    s = str(value).strip().lower().replace("&", " and ")
    s = re.sub(r"[^a-z0-9_]+", "_", s)
    s = re.sub(r"_+", "_", s).strip("_")
    return (s or "unknown")[:max_len].strip("_") or "unknown"


def load_env_key() -> str | None:
    values: dict[str, str] = {}
    env_path = ROOT / ".env"
    if env_path.exists():
        for line in env_path.read_text(encoding="utf-8").splitlines():
            line = line.strip()
            if line and not line.startswith("#") and "=" in line:
                k, v = line.split("=", 1)
                values[k.strip()] = v.strip().strip('"').strip("'")
    return os.getenv("DEFILLAMA_API_KEY") or os.getenv("LLAMA_API_KEY") or values.get("DEFILLAMA_API_KEY") or values.get("LLAMA_API_KEY")


def load_spec(path: Path) -> list[dict[str, Any]]:
    spec = json.loads(path.read_text(encoding="utf-8"))
    default_servers = spec.get("servers") or [{"url": "https://api.llama.fi"}]
    endpoints = []
    for api_path, ops in (spec.get("paths") or {}).items():
        for method, op in ops.items():
            if method.lower() != "get":
                continue
            servers = op.get("servers") or default_servers
            params = []
            for raw in op.get("parameters") or []:
                schema = raw.get("schema") or {}
                params.append(
                    {
                        "name": raw.get("name"),
                        "in": raw.get("in"),
                        "enum": [str(x) for x in (schema.get("enum") or [])],
                        "description": raw.get("description") or "",
                    }
                )
            endpoints.append(
                {
                    "path": api_path,
                    "tag": (op.get("tags") or ["untagged"])[0],
                    "base_url": (servers[0].get("url") or "https://api.llama.fi").rstrip("/"),
                    "params": params,
                }
            )
    return endpoints


def ep(endpoints: list[dict[str, Any]], path: str, tag: str | None = None, base_contains: str | None = None) -> dict[str, Any] | None:
    matches = [x for x in endpoints if x["path"] == path]
    if tag:
        matches = [x for x in matches if x["tag"] == tag]
    if base_contains:
        matches = [x for x in matches if base_contains in x["base_url"]]
    return matches[0] if matches else None


def enum_values(endpoint: dict[str, Any] | None, param: str, default: list[str]) -> list[str]:
    if not endpoint:
        return default
    for p in endpoint.get("params", []):
        if p.get("name") == param and p.get("enum"):
            return p["enum"]
    return default


def dimension_data_types(endpoints: list[dict[str, Any]]) -> dict[str, list[str]]:
    endpoint = ep(endpoints, "/api/v2/metrics/{metric}", "Dimensions")
    desc = ""
    if endpoint:
        for p in endpoint.get("params", []):
            if p.get("name") == "dataType":
                desc = p.get("description") or ""
    parsed: dict[str, list[str]] = {}
    for metric, values_text in re.findall(r"\*\*([^*]+)\*\*:\s*([^\n]+)", desc):
        vals = []
        for raw in values_text.split(","):
            val = re.sub(r"\s*\([^)]*\)", "", raw.strip()).strip(".")
            if val:
                vals.append(val)
        if vals:
            parsed[metric.strip()] = vals
    return parsed or {
        "fees": ["dailyFees", "dailyRevenue", "dailySupplySideRevenue", "dailyHoldersRevenue", "dailyProtocolRevenue"],
        "dexs": ["dailyVolume", "dailyNotionalVolume"],
        "derivatives": ["dailyVolume", "dailyNotionalVolume"],
        "options": ["dailyNotionalVolume", "dailyPremiumVolume"],
        "aggregators": ["dailyVolume"],
        "bridge-aggregators": ["dailyBridgeVolume"],
        "open-interest": ["openInterestAtEnd", "shortOpenInterestAtEnd", "longOpenInterestAtEnd"],
        "normalized-volume": ["dailyNormalizedVolume", "dailyActiveLiquidity"],
    }


def make_url(endpoint: dict[str, Any], path_params: dict[str, Any], api_key: str | None) -> str | None:
    base = endpoint["base_url"]
    if "pro-api.llama.fi" in base:
        if not api_key:
            return None
        base = f"{base}/{quote(api_key, safe='')}"
    path = endpoint["path"]
    for k, v in path_params.items():
        path = path.replace("{" + k + "}", quote(str(v), safe=""))
    return f"{base}{path}"


def api_get(session: requests.Session, endpoint: dict[str, Any], path_params: dict[str, Any], query: dict[str, Any], api_key: str | None, args: argparse.Namespace) -> tuple[Any | None, str | None]:
    url = make_url(endpoint, path_params, api_key)
    if url is None:
        return None, "missing API key"
    params = {k: (str(v).lower() if isinstance(v, bool) else str(v)) for k, v in query.items() if v is not None}
    last_error = None
    for attempt in range(1, 6):
        try:
            time.sleep(args.sleep)
            r = session.get(url, params=params, timeout=args.timeout)
            if r.status_code in RETRY_STATUSES and attempt < 5:
                wait = retry_wait(r, attempt)
                time.sleep(wait)
                continue
            if not r.ok:
                text = (r.text or "").replace("\n", " ").replace("\r", " ").strip()
                return None, f"HTTP {r.status_code}: {text[:300]}"
            return r.json(), None
        except requests.RequestException as exc:
            last_error = str(exc)
            if attempt < 5:
                time.sleep(min(2 ** attempt, 30) + random.uniform(0.1, 1.0))
    return None, last_error or "request failed"


def retry_wait(r: requests.Response, attempt: int) -> float:
    ra = r.headers.get("Retry-After")
    if ra:
        try:
            return min(float(ra), 120.0)
        except ValueError:
            pass
    return (15 if r.status_code == 429 else min(2 ** attempt, 30)) + random.uniform(0.25, 1.5)


def to_date(value: Any) -> str | None:
    if value is None or value == "":
        return None
    if isinstance(value, str):
        s = value.strip()
        if re.match(r"^\d{4}-\d{2}-\d{2}", s):
            return s[:10]
        if re.match(r"^\d{1,2}/\d{1,2}/\d{2,4}$", s):
            try:
                return pd.to_datetime(s, utc=True).strftime("%Y-%m-%d")
            except Exception:
                return None
    try:
        ts = int(float(value))
        if ts > 10_000_000_000:
            ts //= 1000
        if 946684800 <= ts <= 4102444800:
            return datetime.fromtimestamp(ts, tz=timezone.utc).strftime("%Y-%m-%d")
    except Exception:
        return None
    return None


def normalize_rows(rows: list[dict[str, Any]]) -> list[dict[str, Any]]:
    out = []
    for row in rows:
        r = dict(row)
        date = r.get("Date")
        if date is None:
            for c in DATE_COLUMNS:
                if c in r:
                    date = r[c]
                    break
        nd = to_date(date)
        if nd:
            r["Date"] = nd
        for k in list(r.keys()):
            if k != "Date" and k.lower() in ("timestamp", "time", "day", "date"):
                r.pop(k, None)
        out.append(r)
    return out


def clean_numeric(df: pd.DataFrame, skip: set[str]) -> pd.DataFrame:
    for c in df.columns:
        if c not in skip:
            df[c] = pd.to_numeric(df[c], errors="ignore")
    return df


def write_csv(path: Path, rows: list[dict[str, Any]], mode: str, dataset_kind: str, key_cols: list[str] | None = None) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    rows = normalize_rows(rows)
    new = pd.DataFrame(rows)
    if new.empty:
        pd.DataFrame(columns=["Date"]).to_csv(path, index=False)
        return
    if mode == "update" and path.exists():
        try:
            old = pd.read_csv(path)
            new = pd.concat([old, new], ignore_index=True, sort=False)
        except Exception:
            pass
    key_cols = [c for c in (key_cols or []) if c in new.columns]
    if not key_cols:
        key_cols = dedupe_keys(new)
    if key_cols:
        new = new.drop_duplicates(subset=key_cols, keep="last")
    else:
        new = new.drop_duplicates(keep="last")
    if "Date" in new.columns:
        new["_sort_date"] = pd.to_datetime(new["Date"], errors="coerce")
        sort_cols = ["_sort_date"] + [c for c in key_cols if c != "Date"]
        new = new.sort_values(sort_cols, kind="stable").drop(columns=["_sort_date"])
    new = clean_numeric(new, {"Date", "Protocol", "Chain", "Stablecoin", "Pool", "Metric", "DataType", "Asset", "Ticker", "Symbol"})
    new.to_csv(path, index=False)


def dedupe_keys(df: pd.DataFrame) -> list[str]:
    if "Date" not in df.columns:
        return []
    dims = [c for c in ["Protocol", "Chain", "Stablecoin", "Pool", "Metric", "DataType", "Asset", "Ticker", "Symbol"] if c in df.columns]
    return ["Date"] + dims


def write_daily_weekly(
    daily_dir: Path,
    weekly_dir: Path,
    name: str,
    rows: list[dict[str, Any]],
    mode: str,
    dataset_kind: str,
    key_cols: list[str] | None = None,
    weekly_agg: str | None = None,
) -> tuple[Path, Path]:
    daily_path = daily_dir / f"{safe_name(name)}_daily.csv"
    weekly_path = weekly_dir / f"{safe_name(name)}_weekly.csv"
    if not rows:
        pd.DataFrame(columns=["Date"]).to_csv(daily_path, index=False)
        pd.DataFrame(columns=["Date"]).to_csv(weekly_path, index=False)
        return daily_path, weekly_path
    write_csv(daily_path, rows, mode, dataset_kind, key_cols)
    try:
        df = pd.read_csv(daily_path)
    except pd.errors.EmptyDataError:
        pd.DataFrame(columns=["Date"]).to_csv(weekly_path, index=False)
        return daily_path, weekly_path
    weekly = make_weekly(df, dataset_kind, weekly_agg)
    weekly.to_csv(weekly_path, index=False)
    return daily_path, weekly_path


def make_weekly(df: pd.DataFrame, dataset_kind: str, weekly_agg: str | None = None) -> pd.DataFrame:
    if df.empty or "Date" not in df.columns:
        return df
    out = df.copy()
    out["Date"] = pd.to_datetime(out["Date"], errors="coerce")
    out = out.dropna(subset=["Date"])
    if out.empty:
        return df
    out["Week"] = out["Date"].dt.to_period("W-SUN").dt.end_time.dt.strftime("%Y-%m-%d")
    dims = [c for c in ["Protocol", "Chain", "Stablecoin", "Pool", "Metric", "DataType", "Asset", "Ticker", "Symbol"] if c in out.columns]
    numeric = [c for c in out.columns if c not in dims + ["Date", "Week"]]
    for c in numeric:
        out[c] = pd.to_numeric(out[c], errors="coerce")
    agg_method = weekly_agg or ("sum" if dataset_kind == "flow" else "last")
    grouped = out.groupby(["Week"] + dims, dropna=False, as_index=False)
    if agg_method == "mean":
        weekly = grouped[numeric].mean()
    elif agg_method == "sum":
        weekly = grouped[numeric].sum(min_count=1)
    else:
        weekly = grouped[numeric].last()
    weekly = weekly.rename(columns={"Week": "Date"})
    return weekly


def pivot_wide(rows: list[dict[str, Any]], index_cols: list[str], column_col: str, value_col: str) -> list[dict[str, Any]]:
    if not rows:
        return []
    df = pd.DataFrame(normalize_rows(rows))
    if df.empty or column_col not in df.columns:
        return []
    if value_col not in df.columns:
        by_lower = {str(c).lower(): c for c in df.columns}
        value_col = by_lower.get(value_col.lower(), value_col)
    if value_col not in df.columns:
        return []
    wide = df.pivot_table(index=index_cols, columns=column_col, values=value_col, aggfunc="last").reset_index()
    wide.columns = [safe_name(c) if not isinstance(c, str) or c not in index_cols else c for c in wide.columns]
    return wide.to_dict("records")


def as_list(value: Any) -> list[Any]:
    if value is None:
        return []
    return value if isinstance(value, list) else [value]


def chart_rows(data: Any, value_name: str = "Value") -> list[dict[str, Any]]:
    rows = []
    for item in as_list(data):
        if isinstance(item, list) and len(item) >= 2:
            date = to_date(item[0])
            if date:
                rows.append({"Date": date, value_name: item[1]})
        elif isinstance(item, dict):
            date = to_date(item.get("date") or item.get("timestamp") or item.get("time"))
            if date:
                row = {"Date": date}
                matched_value_col = False
                for k, v in item.items():
                    if isinstance(v, (int, float, str)) and k not in ("date", "timestamp", "time"):
                        if str(k).lower() == value_name.lower():
                            row[value_name] = v
                            matched_value_col = True
                        else:
                            row[safe_name(k)] = v
                    elif isinstance(v, dict):
                        for kk, vv in v.items():
                            if isinstance(vv, (int, float, str)):
                                if str(kk).lower() == value_name.lower():
                                    row[value_name] = vv
                                    matched_value_col = True
                                else:
                                    row[safe_name(kk)] = vv
                if not matched_value_col and value_name not in row:
                    lower = value_name.lower()
                    if lower in row:
                        row[value_name] = row.pop(lower)
                rows.append(row)
    return rows


def breakdown_rows(data: Any, entity_col: str, value_col: str = "Value") -> list[dict[str, Any]]:
    rows: list[dict[str, Any]] = []
    for item in as_list(data):
        if isinstance(item, list) and len(item) >= 2:
            date = to_date(item[0])
            payload = item[1]
            if date and isinstance(payload, dict):
                for entity, value in payload.items():
                    rows.append({"Date": date, entity_col: str(entity), value_col: value})
        elif isinstance(item, dict):
            date = to_date(item.get("date") or item.get("timestamp") or item.get("time"))
            if not date:
                continue
            for k, v in item.items():
                if k in ("date", "timestamp", "time"):
                    continue
                if isinstance(v, (int, float, str)):
                    rows.append({"Date": date, entity_col: str(k), value_col: v})
                elif isinstance(v, dict):
                    for kk, vv in v.items():
                        if isinstance(vv, (int, float, str)):
                            rows.append({"Date": date, entity_col: str(kk), value_col: vv})
    return rows


def save_snapshot(snapshot_dir: Path, name: str, rows: list[dict[str, Any]], mode: str = "full") -> Path:
    path = snapshot_dir / f"{safe_name(name)}.csv"
    write_csv(path, rows, "full", "snapshot")
    return path


def rows_from_records(data: Any) -> list[dict[str, Any]]:
    rows = []
    for item in as_list(data):
        if isinstance(item, dict):
            row = {}
            for k, v in item.items():
                if isinstance(v, (int, float, str, bool)) or v is None:
                    row[safe_name(k)] = v
                else:
                    row[f"{safe_name(k)}_json"] = json.dumps(v, ensure_ascii=False, sort_keys=True, default=str)
            rows.append(row)
    return rows


def fetch_task(session: requests.Session, task: dict[str, Any], api_key: str | None, args: argparse.Namespace) -> dict[str, Any]:
    data, err = api_get(session, task["endpoint"], task.get("path_params", {}), task.get("query", {}), api_key, args)
    return {**task, "data": data, "error": err}


def parallel_fetch(tasks: list[dict[str, Any]], api_key: str | None, args: argparse.Namespace, label: str) -> tuple[list[dict[str, Any]], list[dict[str, Any]]]:
    results, failures = [], []
    if not tasks:
        return results, failures
    print(f"{label}: {len(tasks)} API calls")
    with ThreadPoolExecutor(max_workers=max(1, args.max_workers)) as ex:
        futures = []
        for task in tasks:
            session = requests.Session()
            session.headers.update({"Accept": "application/json", "User-Agent": "CryptoQuant-DefiLlama-Research/1.0"})
            futures.append(ex.submit(fetch_task, session, task, api_key, args))
        for i, fut in enumerate(as_completed(futures), start=1):
            res = fut.result()
            if res.get("error"):
                failures.append(res)
            else:
                results.append(res)
            if i == 1 or i % 25 == 0 or i == len(tasks):
                print(f"  {label}: {i}/{len(tasks)} complete, failures={len(failures)}")
    return results, failures


def fetch_one(session: requests.Session, endpoints: list[dict[str, Any]], path: str, tag: str, api_key: str | None, args: argparse.Namespace, path_params: dict[str, Any] | None = None, query: dict[str, Any] | None = None, base_contains: str | None = None) -> tuple[Any | None, str | None, dict[str, Any] | None]:
    endpoint = ep(endpoints, path, tag, base_contains)
    if not endpoint:
        return None, f"endpoint missing: {path}", None
    data, err = api_get(session, endpoint, path_params or {}, query or {}, api_key, args)
    return data, err, endpoint


def harvest_tvl(session: requests.Session, endpoints: list[dict[str, Any]], api_key: str | None, args: argparse.Namespace, dirs: dict[str, Path], failures: list[dict[str, Any]]) -> dict[str, Any]:
    print("Harvesting TVL")
    chains_data, err, _ = fetch_one(session, endpoints, "/v2/chains", "TVL", api_key, args)
    protocols_data, err2, _ = fetch_one(session, endpoints, "/protocols", "TVL", api_key, args)
    if err:
        failures.append({"name": "chains_snapshot", "error": err})
    if err2:
        failures.append({"name": "protocols_snapshot", "error": err2})
    chains = sorted([r for r in as_list(chains_data) if isinstance(r, dict)], key=lambda r: float(r.get("tvl") or 0), reverse=True)
    protocols = sorted([r for r in as_list(protocols_data) if isinstance(r, dict)], key=lambda r: float(r.get("tvl") or 0), reverse=True)
    save_snapshot(dirs["snapshot"], "tvl_chains_current", rows_from_records(chains))
    save_snapshot(dirs["snapshot"], "tvl_protocols_current", rows_from_records(protocols))

    all_chain_hist, err, _ = fetch_one(session, endpoints, "/v2/historicalChainTvl", "TVL", api_key, args)
    if err:
        failures.append({"name": "historical_chain_tvl_all_chains", "error": err})
    else:
        rows = chart_rows(all_chain_hist, "TVL")
        write_daily_weekly(dirs["daily"], dirs["weekly"], "tvl_all_chains", rows, args.mode, "stock", ["Date"])

    chain_tasks = []
    chain_ep = ep(endpoints, "/v2/historicalChainTvl/{chain}", "TVL")
    if chain_ep:
        for c in chains:
            name = c.get("name") or c.get("gecko_id")
            if name:
                chain_tasks.append({"name": str(name), "endpoint": chain_ep, "path_params": {"chain": name}, "query": {}})
    chain_results, chain_failures = parallel_fetch(chain_tasks, api_key, args, "TVL chain histories")
    failures.extend({"name": f"historical_chain_tvl_{x['name']}", "error": x["error"]} for x in chain_failures)
    rows = []
    for res in chain_results:
        for r in chart_rows(res["data"], "TVL"):
            r["Chain"] = res["name"]
            rows.append(r)
    write_daily_weekly(dirs["daily"], dirs["weekly"], "tvl_by_chain_long", rows, args.mode, "stock", ["Date", "Chain"])
    wide = pivot_wide(rows, ["Date"], "Chain", "TVL")
    write_daily_weekly(dirs["daily"], dirs["weekly"], "tvl_by_chain_wide", wide, args.mode, "stock", ["Date"])

    protocol_limit = None if args.top_protocols == 0 else args.top_protocols
    protocol_subset = protocols[:protocol_limit] if protocol_limit else protocols
    protocol_ep = ep(endpoints, "/protocol/{protocol}", "TVL")
    tasks = []
    if protocol_ep:
        for p in protocol_subset:
            slug = p.get("slug") or p.get("name")
            if slug:
                tasks.append({"name": str(slug), "endpoint": protocol_ep, "path_params": {"protocol": slug}, "query": {}})
    results, bad = parallel_fetch(tasks, api_key, args, "TVL protocol histories")
    failures.extend({"name": f"protocol_tvl_{x['name']}", "error": x["error"]} for x in bad)
    rows = []
    chain_rows = []
    for res in results:
        data = res["data"]
        protocol = data.get("name") or res["name"] if isinstance(data, dict) else res["name"]
        for r in chart_rows(data.get("tvl") if isinstance(data, dict) else [], "TVL"):
            r["Protocol"] = protocol
            rows.append(r)
        if isinstance(data, dict):
            for chain, vals in (data.get("chainTvls") or {}).items():
                if isinstance(vals, dict):
                    vals = vals.get("tvl") or vals.get("tokens") or []
                for r in chart_rows(vals, "TVL"):
                    r["Protocol"] = protocol
                    r["Chain"] = chain
                    chain_rows.append(r)
    write_daily_weekly(dirs["daily"], dirs["weekly"], "tvl_by_protocol_long", rows, args.mode, "stock", ["Date", "Protocol"])
    write_daily_weekly(dirs["daily"], dirs["weekly"], "tvl_by_protocol_chain_long", chain_rows, args.mode, "stock", ["Date", "Protocol", "Chain"])
    wide = pivot_wide(rows, ["Date"], "Protocol", "TVL")
    write_daily_weekly(dirs["daily"], dirs["weekly"], "tvl_by_protocol_wide", wide, args.mode, "stock", ["Date"])
    return {"chains": chains, "protocols": protocols}


def harvest_stablecoins(session: requests.Session, endpoints: list[dict[str, Any]], api_key: str | None, args: argparse.Namespace, dirs: dict[str, Path], chains: list[dict[str, Any]], failures: list[dict[str, Any]]) -> list[dict[str, Any]]:
    print("Harvesting stablecoins")
    data, err, _ = fetch_one(session, endpoints, "/stablecoins", "stablecoins", api_key, args, query={"includePrices": True})
    if err:
        failures.append({"name": "stablecoins_snapshot", "error": err})
        stablecoins = []
    else:
        stablecoins = sorted(as_list(data.get("peggedAssets") if isinstance(data, dict) else data), key=stablecoin_mcap, reverse=True)
        save_snapshot(dirs["snapshot"], "stablecoins_current", rows_from_records(stablecoins))

    total, err, _ = fetch_one(session, endpoints, "/stablecoincharts/all", "stablecoins", api_key, args)
    if err:
        failures.append({"name": "stablecoin_market_cap_total", "error": err})
    else:
        rows = normalize_stablecoin_chart(total, "MarketCap")
        write_daily_weekly(dirs["daily"], dirs["weekly"], "stablecoin_market_cap_total", rows, args.mode, "stock", ["Date"])

    prices, err, _ = fetch_one(session, endpoints, "/stablecoinprices", "stablecoins", api_key, args)
    if err:
        failures.append({"name": "stablecoin_prices", "error": err})
    else:
        rows = normalize_stablecoin_prices(prices)
        write_daily_weekly(dirs["daily"], dirs["weekly"], "stablecoin_prices_long", rows, args.mode, "stock", ["Date", "Stablecoin"])
        wide = pivot_wide(rows, ["Date"], "Stablecoin", "Price")
        write_daily_weekly(dirs["daily"], dirs["weekly"], "stablecoin_prices", wide, args.mode, "stock", ["Date"])

    chain_ep = ep(endpoints, "/stablecoincharts/{chain}", "stablecoins")
    tasks = []
    if chain_ep:
        for c in chains:
            name = c.get("name") or c.get("gecko_id")
            if name:
                tasks.append({"name": str(name), "endpoint": chain_ep, "path_params": {"chain": name}, "query": {}})
    results, bad = parallel_fetch(tasks, api_key, args, "Stablecoin chain market caps")
    failures.extend({"name": f"stablecoincharts_{x['name']}", "error": x["error"]} for x in bad)
    rows = []
    for res in results:
        for r in normalize_stablecoin_chart(res["data"], "MarketCap"):
            r["Chain"] = res["name"]
            rows.append(r)
    write_daily_weekly(dirs["daily"], dirs["weekly"], "stablecoin_market_cap_by_chain_long", rows, args.mode, "stock", ["Date", "Chain"])
    wide = pivot_wide(rows, ["Date"], "Chain", "MarketCap")
    write_daily_weekly(dirs["daily"], dirs["weekly"], "stablecoin_market_cap_by_chain_wide", wide, args.mode, "stock", ["Date"])

    stable_ep = ep(endpoints, "/stablecoin/{asset}", "stablecoins")
    tasks = []
    if stable_ep:
        for s in stablecoins:
            asset_id = s.get("id")
            symbol = s.get("symbol") or s.get("name") or asset_id
            if asset_id is not None:
                tasks.append({"name": str(symbol), "asset_id": asset_id, "endpoint": stable_ep, "path_params": {"asset": asset_id}, "query": {}})
    results, bad = parallel_fetch(tasks, api_key, args, "Stablecoin asset histories")
    failures.extend({"name": f"stablecoin_{x['name']}", "error": x["error"]} for x in bad)
    total_rows, chain_rows = [], []
    for res in results:
        symbol = res["name"]
        asset_id = res["asset_id"]
        data = res["data"] if isinstance(res["data"], dict) else {}
        name = data.get("symbol") or data.get("name") or symbol
        for r in normalize_stablecoin_chart(data.get("totalCirculating"), "Circulating"):
            r["Stablecoin"] = name
            r["AssetID"] = asset_id
            total_rows.append(r)
        for chain, vals in (data.get("chainCirculating") or {}).items():
            for r in normalize_stablecoin_chart(vals, "Circulating"):
                r["Stablecoin"] = name
                r["AssetID"] = asset_id
                r["Chain"] = chain
                chain_rows.append(r)
    write_daily_weekly(dirs["daily"], dirs["weekly"], "stablecoin_circulating_by_asset_long", total_rows, args.mode, "stock", ["Date", "Stablecoin"])
    write_daily_weekly(dirs["daily"], dirs["weekly"], "stablecoin_circulating_by_asset_chain_long", chain_rows, args.mode, "stock", ["Date", "Stablecoin", "Chain"])
    wide = pivot_wide(total_rows, ["Date"], "Stablecoin", "Circulating")
    write_daily_weekly(dirs["daily"], dirs["weekly"], "stablecoin_circulating_by_asset_wide", wide, args.mode, "stock", ["Date"])
    return stablecoins


def stablecoin_mcap(row: dict[str, Any]) -> float:
    circ = row.get("circulating")
    if isinstance(circ, dict):
        return float(circ.get("peggedUSD") or 0)
    return float(row.get("mcap") or row.get("peggedUSD") or 0)


def normalize_stablecoin_chart(data: Any, value_col: str) -> list[dict[str, Any]]:
    rows = []
    if isinstance(data, dict):
        data = data.get("data") or data.get("peggedUSD") or data.get("circulating") or data
    for item in as_list(data):
        if isinstance(item, dict):
            date = to_date(item.get("date") or item.get("timestamp"))
            value = None
            for candidate in [value_col, "peggedUSD", "totalCirculatingUSD", "totalCirculating", "circulating", "value"]:
                if candidate in item:
                    value = item[candidate]
                    break
            if value is None:
                for v in item.values():
                    if isinstance(v, dict) and "peggedUSD" in v:
                        value = v["peggedUSD"]
                        break
            if date and value is not None:
                rows.append({"Date": date, value_col: value})
        elif isinstance(item, list) and len(item) >= 2:
            date = to_date(item[0])
            value = item[1]
            if isinstance(value, dict):
                value = value.get("peggedUSD") or value.get("value")
            if date and value is not None:
                rows.append({"Date": date, value_col: value})
    return rows


def normalize_stablecoin_prices(data: Any) -> list[dict[str, Any]]:
    rows = []
    payload = data.get("peggedAssets") if isinstance(data, dict) and "peggedAssets" in data else data
    for item in as_list(payload):
        if isinstance(item, list) and len(item) >= 2:
            date = to_date(item[0])
            if date and isinstance(item[1], dict):
                for coin, price in item[1].items():
                    rows.append({"Date": date, "Stablecoin": str(coin), "Price": price})
        elif isinstance(item, dict):
            date = to_date(item.get("date") or item.get("timestamp"))
            if not date:
                continue
            for k, v in item.items():
                if k in ("date", "timestamp"):
                    continue
                if isinstance(v, (int, float, str)):
                    rows.append({"Date": date, "Stablecoin": str(k), "Price": v})
                elif isinstance(v, dict):
                    price = v.get("price") or v.get("peg") or v.get("value")
                    if price is not None:
                        rows.append({"Date": date, "Stablecoin": str(k), "Price": price})
    return rows


def harvest_coins(session: requests.Session, endpoints: list[dict[str, Any]], api_key: str | None, args: argparse.Namespace, dirs: dict[str, Path], stablecoins: list[dict[str, Any]], failures: list[dict[str, Any]]) -> None:
    print("Harvesting coins/prices")
    coin_ids = ["coingecko:bitcoin", "coingecko:ethereum"]
    for s in stablecoins:
        gecko = s.get("gecko_id") or s.get("geckoId")
        if gecko:
            coin_ids.append(f"coingecko:{gecko}")
    coin_ids = sorted(set(coin_ids))
    chart_ep = ep(endpoints, "/chart/{coins}", "coins", "coins.llama.fi")
    if not chart_ep:
        failures.append({"name": "coin_prices", "error": "chart endpoint missing"})
        return
    rows = []
    for chunk_i, chunk in enumerate(chunks(coin_ids, 25), start=1):
        data, err = api_get(session, chart_ep, {"coins": ",".join(chunk)}, {"start": 0, "period": "1d"}, api_key, args)
        if err:
            failures.append({"name": f"coin_prices_chunk_{chunk_i}", "error": err})
            continue
        rows.extend(normalize_coin_chart(data))
    write_daily_weekly(dirs["daily"], dirs["weekly"], "coin_prices_long", rows, args.mode, "stock", ["Date", "Asset"])
    wide = pivot_wide(rows, ["Date"], "Asset", "Price")
    write_daily_weekly(dirs["daily"], dirs["weekly"], "coin_prices_btc_eth_stablecoins", wide, args.mode, "stock", ["Date"])


def normalize_coin_chart(data: Any) -> list[dict[str, Any]]:
    rows = []
    if isinstance(data, dict) and "coins" in data:
        for asset, payload in (data.get("coins") or {}).items():
            prices = payload.get("prices") or payload.get("price") or payload.get("data") if isinstance(payload, dict) else payload
            for r in chart_rows(prices, "Price"):
                r["Asset"] = asset
                rows.append(r)
    elif isinstance(data, dict):
        for asset, payload in data.items():
            if isinstance(payload, dict):
                prices = payload.get("prices") or payload.get("data") or payload.get("price")
                for r in chart_rows(prices, "Price"):
                    r["Asset"] = asset
                    rows.append(r)
    return rows


def harvest_dimensions(session: requests.Session, endpoints: list[dict[str, Any]], api_key: str | None, args: argparse.Namespace, dirs: dict[str, Path], failures: list[dict[str, Any]]) -> None:
    print("Harvesting Dimensions / volumes / fees / revenue / perps")
    metric_types = dimension_data_types(endpoints)
    protocol_ep = ep(endpoints, "/api/v2/chart/{metric}/protocol-breakdown", "Dimensions")
    chain_ep = ep(endpoints, "/api/v2/chart/{metric}/chain-breakdown", "Dimensions")
    total_ep = ep(endpoints, "/api/v2/chart/{metric}", "Dimensions")
    for metric, data_types in metric_types.items():
        for dt in data_types:
            query = {"dataType": dt}
            kind = "flow" if any(x in dt.lower() or x in metric.lower() for x in FLOW_WORDS) else "stock"
            value_col = dt
            if total_ep:
                data, err = api_get(session, total_ep, {"metric": metric}, query, api_key, args)
                if err:
                    failures.append({"name": f"dimensions_{metric}_{dt}_total", "error": err})
                else:
                    rows = chart_rows(data, value_col)
                    for r in rows:
                        r["Metric"] = metric
                        r["DataType"] = dt
                    write_daily_weekly(dirs["daily"], dirs["weekly"], f"dimensions_{metric}_{dt}_total", rows, args.mode, kind, ["Date", "Metric", "DataType"])
            if protocol_ep:
                data, err = api_get(session, protocol_ep, {"metric": metric}, query, api_key, args)
                if err:
                    failures.append({"name": f"dimensions_{metric}_{dt}_protocol", "error": err})
                else:
                    rows = breakdown_rows(data, "Protocol", value_col)
                    for r in rows:
                        r["Metric"] = metric
                        r["DataType"] = dt
                    write_daily_weekly(dirs["daily"], dirs["weekly"], f"dimensions_{metric}_{dt}_by_protocol_long", rows, args.mode, kind, ["Date", "Protocol", "Metric", "DataType"])
                    wide = pivot_wide(rows, ["Date"], "Protocol", value_col)
                    write_daily_weekly(dirs["daily"], dirs["weekly"], f"dimensions_{metric}_{dt}_by_protocol_wide", wide, args.mode, kind, ["Date"])
            if chain_ep:
                data, err = api_get(session, chain_ep, {"metric": metric}, query, api_key, args)
                if err:
                    failures.append({"name": f"dimensions_{metric}_{dt}_chain", "error": err})
                else:
                    rows = breakdown_rows(data, "Chain", value_col)
                    for r in rows:
                        r["Metric"] = metric
                        r["DataType"] = dt
                    write_daily_weekly(dirs["daily"], dirs["weekly"], f"dimensions_{metric}_{dt}_by_chain_long", rows, args.mode, kind, ["Date", "Chain", "Metric", "DataType"])
                    wide = pivot_wide(rows, ["Date"], "Chain", value_col)
                    write_daily_weekly(dirs["daily"], dirs["weekly"], f"dimensions_{metric}_{dt}_by_chain_wide", wide, args.mode, kind, ["Date"])


def harvest_yields(session: requests.Session, endpoints: list[dict[str, Any]], api_key: str | None, args: argparse.Namespace, dirs: dict[str, Path], failures: list[dict[str, Any]]) -> None:
    print("Harvesting yields")
    pools, err, _ = fetch_one(session, endpoints, "/pools", "yields", api_key, args)
    if err:
        failures.append({"name": "yield_pools_snapshot", "error": err})
        return
    pool_rows = as_list(pools.get("data") if isinstance(pools, dict) else pools)
    pool_rows = sorted([r for r in pool_rows if isinstance(r, dict)], key=lambda r: float(r.get("tvlUsd") or 0), reverse=True)
    save_snapshot(dirs["snapshot"], "yield_pools_current", rows_from_records(pool_rows))
    selected = pool_rows if args.top_pools == 0 else pool_rows[: args.top_pools]
    chart_ep = ep(endpoints, "/chart/{pool}", "yields", "yields.llama.fi")
    if not chart_ep:
        failures.append({"name": "yield_chart", "error": "yield chart endpoint missing"})
        return
    tasks = []
    for row in selected:
        pool_id = row.get("pool")
        if pool_id:
            tasks.append({"name": str(pool_id), "project": row.get("project"), "chain": row.get("chain"), "symbol": row.get("symbol"), "endpoint": chart_ep, "path_params": {"pool": pool_id}, "query": {}})
    results, bad = parallel_fetch(tasks, api_key, args, "Yield pool histories")
    failures.extend({"name": f"yield_pool_{x['name']}", "error": x["error"]} for x in bad)
    rows = []
    for res in results:
        for r in normalize_yield_chart(res["data"]):
            r["Pool"] = res["name"]
            r["Protocol"] = res.get("project")
            r["Chain"] = res.get("chain")
            r["Symbol"] = res.get("symbol")
            rows.append(r)
    write_daily_weekly(dirs["daily"], dirs["weekly"], "yields_by_pool_long", rows, args.mode, "stock", ["Date", "Pool"], weekly_agg="mean")


def normalize_yield_chart(data: Any) -> list[dict[str, Any]]:
    payload = data.get("data") if isinstance(data, dict) and "data" in data else data
    rows = []
    for item in as_list(payload):
        if not isinstance(item, dict):
            continue
        date = to_date(item.get("timestamp") or item.get("date"))
        if not date:
            continue
        row = {"Date": date}
        for key in ["apy", "apyBase", "apyReward", "tvlUsd", "il7d", "apyBase7d"]:
            if key in item:
                row[safe_name(key)] = item[key]
        rows.append(row)
    return rows


def harvest_treasury_oracles_etfs(session: requests.Session, endpoints: list[dict[str, Any]], api_key: str | None, args: argparse.Namespace, dirs: dict[str, Path], failures: list[dict[str, Any]]) -> None:
    print("Harvesting treasury, oracles, ETFs")
    treasuries, err, _ = fetch_one(session, endpoints, "/api/treasuries", "main page", api_key, args)
    treasury_rows = []
    if err:
        failures.append({"name": "treasuries_snapshot", "error": err})
        treasury_protocols = []
    else:
        treasury_records = rows_from_records(as_list(treasuries))
        save_snapshot(dirs["snapshot"], "treasuries_current", treasury_records)
        treasury_protocols = discover_protocol_names(treasuries)
    chart_ep = ep(endpoints, "/api/v2/chart/treasury/protocol/{protocol}", "Treasury")
    if chart_ep:
        tasks = [{"name": p, "endpoint": chart_ep, "path_params": {"protocol": p}, "query": {"key": "all"}} for p in treasury_protocols]
        results, bad = parallel_fetch(tasks, api_key, args, "Treasury histories")
        failures.extend({"name": f"treasury_{x['name']}", "error": x["error"]} for x in bad)
        for res in results:
            for r in chart_rows(res["data"], "TreasuryValue"):
                r["Protocol"] = res["name"]
                treasury_rows.append(r)
    write_daily_weekly(dirs["daily"], dirs["weekly"], "treasury_by_protocol_long", treasury_rows, args.mode, "stock", ["Date", "Protocol"])
    wide = pivot_wide(treasury_rows, ["Date"], "Protocol", "TreasuryValue")
    write_daily_weekly(dirs["daily"], dirs["weekly"], "treasury_by_protocol_wide", wide, args.mode, "stock", ["Date"])

    oracle_total, err, _ = fetch_one(session, endpoints, "/api/v2/chart/oracle", "Oracles", api_key, args)
    if err:
        failures.append({"name": "oracles_total", "error": err})
    else:
        rows = chart_rows(oracle_total, "TVS")
        write_daily_weekly(dirs["daily"], dirs["weekly"], "oracles_total_tvs", rows, args.mode, "stock", ["Date"])
    for path, entity, name in [
        ("/api/v2/chart/oracle/protocol-breakdown", "Protocol", "oracles_tvs_by_protocol"),
        ("/api/v2/chart/oracle/chain-breakdown", "Chain", "oracles_tvs_by_chain"),
    ]:
        data, err, _ = fetch_one(session, endpoints, path, "Oracles", api_key, args)
        if err:
            failures.append({"name": name, "error": err})
            continue
        rows = breakdown_rows(data, entity, "TVS")
        write_daily_weekly(dirs["daily"], dirs["weekly"], f"{name}_long", rows, args.mode, "stock", ["Date", entity])
        wide = pivot_wide(rows, ["Date"], entity, "TVS")
        write_daily_weekly(dirs["daily"], dirs["weekly"], f"{name}_wide", wide, args.mode, "stock", ["Date"])

    etf_snapshot, err, _ = fetch_one(session, endpoints, "/etfs/snapshot", "ETFs", api_key, args)
    if err:
        failures.append({"name": "etfs_snapshot", "error": err})
    else:
        save_snapshot(dirs["snapshot"], "etfs_current", rows_from_records(as_list(etf_snapshot)))
    etf_flows, err, _ = fetch_one(session, endpoints, "/etfs/flows", "ETFs", api_key, args)
    if err:
        failures.append({"name": "etfs_flows", "error": err})
    else:
        rows = normalize_etf_flows(etf_flows)
        write_daily_weekly(dirs["daily"], dirs["weekly"], "etf_flows_long", rows, args.mode, "flow", ["Date", "Ticker"])
        wide = pivot_wide(rows, ["Date"], "Ticker", "Flow")
        write_daily_weekly(dirs["daily"], dirs["weekly"], "etf_flows_wide", wide, args.mode, "flow", ["Date"])


def discover_protocol_names(payload: Any) -> list[str]:
    vals = []
    for item in walk(payload):
        if isinstance(item, dict):
            vals.extend([item.get("slug"), item.get("module"), item.get("name"), item.get("protocol")])
    return unique(vals)


def walk(value: Any) -> list[Any]:
    out = [value]
    if isinstance(value, dict):
        for v in value.values():
            out.extend(walk(v))
    elif isinstance(value, list):
        for v in value:
            out.extend(walk(v))
    return out


def unique(values: list[Any]) -> list[str]:
    seen, out = set(), []
    for v in values:
        if v is None:
            continue
        s = str(v).strip()
        if s and s.lower() != "none" and s not in seen:
            seen.add(s)
            out.append(s)
    return out


def normalize_etf_flows(data: Any) -> list[dict[str, Any]]:
    rows = []
    payload = data.get("data") if isinstance(data, dict) and "data" in data else data
    for item in as_list(payload):
        if not isinstance(item, dict):
            continue
        date = to_date(item.get("date") or item.get("timestamp"))
        if not date:
            continue
        ticker = item.get("ticker") or item.get("symbol") or item.get("asset") or item.get("name")
        flow = item.get("flow") or item.get("flows") or item.get("netFlow") or item.get("value")
        if flow is not None:
            rows.append({"Date": date, "Ticker": ticker or "unknown", "Flow": flow})
        else:
            for k, v in item.items():
                if k not in ("date", "timestamp") and isinstance(v, (int, float)):
                    rows.append({"Date": date, "Ticker": k, "Flow": v})
    return rows


def chunks(values: list[str], n: int) -> list[list[str]]:
    return [values[i : i + n] for i in range(0, len(values), n)]


def clean_output(out_dir: Path) -> None:
    if out_dir.exists():
        for child in out_dir.iterdir():
            if child.is_dir():
                shutil.rmtree(child)
            else:
                child.unlink()
    out_dir.mkdir(parents=True, exist_ok=True)


def write_failures(out_dir: Path, failures: list[dict[str, Any]]) -> Path:
    path = out_dir / "Defillama_failed_endpoints.csv"
    with path.open("w", encoding="utf-8", newline="") as f:
        cols = ["name", "error"]
        w = csv.DictWriter(f, fieldnames=cols, extrasaction="ignore")
        w.writeheader()
        for row in failures:
            w.writerow(row)
    return path


def inventory(out_dir: Path, dirs: dict[str, Path], failures: list[dict[str, Any]]) -> Path:
    files = sorted([*dirs["daily"].glob("*.csv"), *dirs["weekly"].glob("*.csv"), *dirs["snapshot"].glob("*.csv")], key=lambda p: str(p).lower())
    lines = ["DefiLlama Research CSV Inventory", "=" * 32, ""]
    for path in files:
        try:
            df = pd.read_csv(path, nrows=10000)
            columns = list(df.columns)
            sample = "EMPTY FILE" if df.empty else json.dumps({k: (None if pd.isna(v) else v) for k, v in df.iloc[0].to_dict().items()}, ensure_ascii=False, default=str)
            start, end = infer_range(df)
            dtype = "snapshot" if start == "SNAPSHOT" else "historical"
        except Exception as exc:
            columns, sample, start, end, dtype = [], f"READ ERROR: {exc}", "SNAPSHOT", "SNAPSHOT", "snapshot"
        lines.extend(
            [
                f"File Name: {path.name}",
                f"Full Path: {path}",
                f"File Type: CSV",
                f"Dataset Type: {dtype}",
                f"Start Date: {start}",
                f"End Date: {end}",
                f"Columns: {', '.join(columns) if columns else 'NONE'}",
                f"Sample Row: {sample}",
                "",
            ]
        )
    if failures:
        lines.extend(["Failed / unavailable API calls", "-" * 30])
        for row in failures[:500]:
            lines.append(f"{row.get('name')}: {row.get('error')}")
        if len(failures) > 500:
            lines.append(f"... {len(failures) - 500} more failures in Defillama_failed_endpoints.csv")
        lines.append("")
    path = out_dir / "Defillama_data.txt"
    path.write_text("\n".join(lines), encoding="utf-8")
    return path


def infer_range(df: pd.DataFrame) -> tuple[str, str]:
    if "Date" not in df.columns or df.empty:
        return "SNAPSHOT", "SNAPSHOT"
    dates = pd.to_datetime(df["Date"], errors="coerce").dropna()
    if dates.empty:
        return "SNAPSHOT", "SNAPSHOT"
    return dates.min().strftime("%Y-%m-%d"), dates.max().strftime("%Y-%m-%d")


def main() -> None:
    args = parse_args()
    spec_path = Path(args.spec)
    if not spec_path.is_absolute():
        spec_path = ROOT / spec_path
    out_dir = Path(args.out)
    if not out_dir.is_absolute():
        out_dir = ROOT / out_dir

    if args.mode == "full":
        clean_output(out_dir)
    out_dir.mkdir(parents=True, exist_ok=True)
    dirs = {
        "daily": out_dir / "Daily",
        "weekly": out_dir / "Weekly",
        "snapshot": out_dir / "Snapshot",
    }
    for d in dirs.values():
        d.mkdir(parents=True, exist_ok=True)

    api_key = load_env_key()
    endpoints = load_spec(spec_path)
    session = requests.Session()
    session.headers.update({"Accept": "application/json", "User-Agent": "CryptoQuant-DefiLlama-Research/1.0"})
    failures: list[dict[str, Any]] = []

    print(f"DefiLlama research harvest started. Mode={args.mode}; API key present={bool(api_key)}")
    print(f"Output folder: {out_dir}")
    tvl_universe = harvest_tvl(session, endpoints, api_key, args, dirs, failures)
    stablecoins = harvest_stablecoins(session, endpoints, api_key, args, dirs, tvl_universe.get("chains", []), failures)
    harvest_coins(session, endpoints, api_key, args, dirs, stablecoins, failures)
    harvest_dimensions(session, endpoints, api_key, args, dirs, failures)
    harvest_yields(session, endpoints, api_key, args, dirs, failures)
    harvest_treasury_oracles_etfs(session, endpoints, api_key, args, dirs, failures)

    failure_path = write_failures(out_dir, failures)
    inventory_path = inventory(out_dir, dirs, failures)
    daily_count = len(list(dirs["daily"].glob("*.csv")))
    weekly_count = len(list(dirs["weekly"].glob("*.csv")))
    snapshot_count = len(list(dirs["snapshot"].glob("*.csv")))
    print("")
    print("DefiLlama research harvest complete")
    print(f"Daily CSV files: {daily_count}")
    print(f"Weekly CSV files: {weekly_count}")
    print(f"Snapshot CSV files: {snapshot_count}")
    print(f"Failures logged: {len(failures)} -> {failure_path}")
    print(f"Inventory: {inventory_path}")


if __name__ == "__main__":
    main()
