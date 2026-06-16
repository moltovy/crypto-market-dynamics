# Data, Calendar, and Metric Strategy v0

Date: 2026-04-18

Purpose: define the recommended data-design decisions for the four-paper program before code changes. This file does not change `Data/`, configs, or source code.

## Current Inventory Facts

Current `Data/MASTER_DATA.csv` count: 490 CSV files.

Source counts:

| Source | Files |
|---|---:|
| AlternativeMe | 1 |
| Artemis | 48 |
| CryptoQuant | 345 |
| DefiLlama | 28 |
| Farside ETF Data | 3 |
| FRED | 21 |
| Tradingview | 44 |

Frequency counts:

| Frequency | Files |
|---|---:|
| daily | 436 |
| weekly | 31 |
| monthly | 13 |
| snapshot | 9 |
| `~4d` | 1 |

Evidence: `Data/MASTER_DATA.csv`.

## Calendar Policy

Recommended default:

| Use case | Headline calendar | Robustness calendar | Rationale |
|---|---|---|---|
| Macro/ETF return regressions | Market day | Weekly and crypto-7 | Avoid artificial weekend zeros in TradFi variables. |
| ETF flow transmission | Market day | T+1 and weekly | ETF flows are trading-day native and reporting-time sensitive. |
| Stablecoin liquidity | Calendar day | Weekly | Stablecoin supply and crypto settlement operate 7 days. |
| DeFi/CEX and TVL | Calendar day | Weekly | DeFi is 7-day infrastructure; weekend activity is part of the object. |
| Lending/RWA | Weekly | Monthly if needed | Artemis lending is weekly and RWA histories may be sparse. |

Evidence: `config/calendars.yml`; `src/cqresearch/data/calendars.py`; `src/cqresearch/data/panel_builder.py`.

## Fill Policy

Recommended default:

- Returns: never forward-fill.
- Flows: never forward-fill as values; zero-fill only for confirmed non-events inside active observation windows.
- ETF flows: zero-fill only for confirmed non-trading days after fund listing, and run T+1 timing sensitivity.
- Levels: limited forward-fill allowed for TradFi levels and rates only if explicitly documented and bounded.
- Monthly releases: align to release date or month-end context; do not daily-fill into causal timing claims.
- Snapshots: exclude from time-series regressions.

Known conflict to resolve before code changes: `config/calendars.yml` and `src/cqresearch/data/calendars.py` do not yet behave as a single source of truth. Evidence: `config/calendars.yml`; `src/cqresearch/data/calendars.py`; `HANDOFF.md`.

## Source Precedence

| Concept | Primary source | Robustness source | Classification |
|---|---|---|---|
| BTC/ETH ETF flows | Farside | DefiLlama ETF history | Exact duplicate after unit conversion and asset filter. |
| ETF AUM | Artemis aggregate | Artemis issuer files | Related; level differences matter. |
| Stablecoin supply | DefiLlama daily aggregate | Artemis chain/token composition | Related but definitionally different. |
| TVL | DefiLlama all-chain | Artemis DEX TVL | Different concept unless restricted to DEX sector. |
| Dollar strength | FRED broad dollar index | TradingView DXY | Related but different definitions. |
| ETH market cap | CryptoQuant | Artemis | Near duplicate after unit alignment. |
| Open interest | CryptoQuant asset OI | Artemis platform OI | Not comparable without venue/instrument map. |
| Fees | CryptoQuant BTC/ETH where asset-specific | Artemis chain fees | Related but scope differs. |
| Active addresses | CryptoQuant BTC/ETH where asset-specific | Artemis chain activity | Not direct users; avoid summed-user claims. |
| Exchange flows | CryptoQuant asset exchange flows | DefiLlama CEX net inflows | Related but different concepts. |
| RWA | DefiLlama RWA | Artemis tokenized market cap | Metadata-sensitive. |
| DeFi lending | Artemis lending files | FRED rates and RWA controls | Proxy coverage, not direct yield panel. |

Evidence: `Data/MASTER_DATA.csv`; `Data/Farside ETF Data/`; `Data/DefiLlama/`; `Data/Artemis/`; `Data/FRED/`; `Data/Tradingview/`; `Data/CryptoQuant/`.

## Metric Dictionary Schema

Every candidate variable should be registered before entering a paper model.

Recommended fields:

- `metric_id`
- `paper_id`
- `concept_block`
- `source`
- `raw_path`
- `raw_column`
- `unit`
- `frequency`
- `timezone_or_calendar`
- `first_date`
- `last_date`
- `coverage_pct`
- `missing_policy`
- `fill_policy`
- `transform`
- `primary_or_robustness`
- `known_overlaps`
- `definition_notes`
- `release_lag_notes`
- `lookahead_risk`
- `approved_for_baseline`

## High-Dimensional Strategy

Recommended variable-selection order:

1. Economic block definition.
2. Source precedence.
3. Coverage and missingness screen.
4. Frequency compatibility screen.
5. Statistical screen within block.

Allowed statistical screens:

- PCA within a block.
- Clustering for redundancy detection.
- LASSO or elastic net only after pre-defining candidate block and outcome.
- Partial least squares only as robustness.
- Boosted-tree importance only as exploratory support.

Rejected:

- One universal daily panel for all 490 files.
- Unrestricted ML variable mining.
- Narrative selection after seeing significant results.
- Silent vendor substitution.

## Required Tests Before Production Panels

- Calendar-day vs market-day alignment tests.
- ETF flow unit conversion tests.
- Flow zero-fill and non-trading-day tests.
- FRED release-lag tests for monthly/weekly macro.
- Source-overlap tests for ETF flows, stablecoins, TVL, USD index, and ETH market cap.
- Metric dictionary completeness test for baseline variables.

Evidence: `tests/unit/`; `src/cqresearch/data/`; `scripts/02_run_analyses.py`.

