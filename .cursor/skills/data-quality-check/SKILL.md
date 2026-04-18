---
name: data-quality-check
description: Run a standard data-quality profile on any CSV in Data/. Reports row count, date range, duplicates, missingness, stale blocks, unit sanity checks, and a Top-N preview. Use whenever touching a new dataset, before any join, or before citing a file in a claim.
---

# data-quality-check

## When to invoke
- Before writing any analysis that depends on a `Data/...` CSV.
- Before citing a file in a markdown claim.
- Whenever `Data/MASTER_DATA.md` mentions a dataset you haven't personally profiled this session.

## Inputs
- A CSV file path under `Data/`.
- (optional) Expected date-column name, expected calendar key from `config/calendars.yml`, expected value-column name.

## Steps
1. **Load without inference.** Use `pd.read_csv(path, dtype=str)` first. Never trust inferred dtypes.
2. **Parse the date column** with `pd.to_datetime(..., utc=True, errors='coerce')`. Report how many rows failed to parse.
3. **Report shape.** `(rows, cols)`, column names, first/last date, date frequency inferred via `pd.infer_freq`.
4. **Duplicate scan.** Count duplicates by `date`. Count duplicates by all columns. Flag if > 0.
5. **Missingness.** Per-column null rate. Split into: *structural* (pre-launch), *stale* (final N rows same value), *random*.
6. **Unit sanity.** Ranges per numeric column (min, p1, median, p99, max). Flag values outside plausible ranges (e.g. negative prices, >100% percentages stored as 500).
7. **Calendar alignment.** Reindex to the configured calendar and report gaps.
8. **Preview.** First 3 and last 3 rows.
9. **Write summary.** Emit `reports/run_summaries/<YYYY-MM-DD>_dq_<file-stem>.md`.

## Output contract
A markdown block with:
- File path (absolute).
- Shape, date range, inferred frequency.
- Duplicate count, missingness per column, stale-tail length.
- Unit-sanity flags (each with a single-line explanation).
- Three lines: "SAFE TO USE / USE WITH CAUTION / DO NOT USE UNTIL FIXED".
- Confidence label.

## Failure modes to look for
- Column renamed between CryptoQuant API dumps (look for `value` vs `close`).
- Silent timezone change (UTC+0 vs America/New_York).
- BTC + WBTC merged as `btc_total_exchange_balance` — always check the `chain_taxonomy.yml` aggregation rule.
- ETH L1 + L2 summed (forbidden by `config/chain_taxonomy.yml`).

## Reference
- `config/calendars.yml`, `config/chain_taxonomy.yml`, `config/factor_blocks.yml`
- `Data/MASTER_DATA.md`, `Data/_meta/curation_log.md`
