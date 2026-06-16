# CryptoQuant — Current architecture

Auto-generated inventory: paths, UTC creation times (filesystem `ctime` on Windows), and agent-oriented notes.

**Note:** `ctime` can change when files are copied or moved; treat as approximate lineage.

---

## 1. Tree overview

```
CryptoQuant/
|-- .cursor/          Cursor rules and skills
|-- .github/          CI
|-- .vscode/          Editor config
|-- archive/          Retired experiments
|-- config/           YAML policy (calendars, events, factors)
|-- Data/             Raw curated inputs
|-- docs/             Specs and context
|-- Manager/          Multi-agent and paper notes
|-- notebooks/        Jupyter exploration
|-- prompts/          Agent prompt copies
|-- references/       External methodology (see §3 — subtree omitted from §4)
|-- reports/          Generated tables, figures, drafts, panels
|-- scripts/          Pipeline scripts 01–05
|-- src/cqresearch/    Python package
|-- tests/             pytest
|-- tools/             Helpers
|-- pyproject.toml / uv.lock / README.md / …
```

### 1.1 Package and pipeline layout (logical)

```
src/cqresearch/
|-- data/          Loaders, calendars, panel_builder → master panel
|-- features/      Feature matrix from panel (returns, diffs, ETF intensity)
|-- modeling/      OLS, rolling, structural breaks, VAR/FEVD, event studies
|-- analysis/      Higher-level analysis helpers (if present)
|-- utils/         Shared helpers
|-- viz/           Plot helpers (if present)

scripts/
|-- 01_build_master_panel.py
|-- 02_run_analyses.py
|-- 03_make_figures.py
|-- 04_descriptives_and_summaries.py
|-- 05_robustness.py
```

Runtime/cache folders such as `__pycache__` appear in §4 but are not part of the logical design.

---

## 2. Folder guide (for other LLMs)

### `.cursor/`

Rules (`*.mdc`) and skills: enforce data integrity and repeatable workflows before changing claims or data.

### `.github/`

CI (e.g. pytest) on push/PR.

### `config/`

Calendars, events, factor blocks — prefer config over hardcoding.

### `Data/`

Source CSVs and `MASTER_DATA.md`; not regenerated reports.

### `docs/`

Specs, pre-registration YAML, context docs.

### `Manager/`

Workflows, backlogs, paper manager notes — planning, not empirical tables.

### `notebooks/`

Exploration; production code lives in `scripts/` and `src/cqresearch/`.

### `prompts/`

Agent constitution copies; align with root `AGENTS.md` if duplicated.

### `reports/`

Outputs: dated `tables/`, `figures/`, `drafts/`, `run_summaries/` — cite matching run dates.

### `scripts/`

Ordered pipeline to build panel and run analyses.

### `src/cqresearch/`

Loaders, features, modeling (OLS, VAR, breaks, events).

### `tests/`

Pytest; extend when changing contracts.

### `tools/`

Maintenance scripts.

### `archive/`

Old material; do not assume current.

### Root

`pyproject.toml`, `uv.lock`, `README.md`, `run_pipeline.py`, `.env.example`.

---

## 3. `references/` (summary only)

The full **`references/`** subtree is **omitted** from §4 (no per-file or per-subfolder rows). This directory holds **external bundles** useful for agent workflow — Cursor skills patterns, econometrics coursework mirrors, tips — **not** CryptoQuant empirical data. Use these materials for methodology inspiration, coding patterns, and documentation style; **do not** treat them as evidence for BTC/ETH results.

- **Total directories under `references/` (including nested):** 80
- **Total files under `references/`:** 211

- **Top-level bundles inside `references/` (folders):**
  - `awesome-cursor-skills-main/` — Vendored “awesome” Cursor skill templates and `resources/` recipes (testing, CI, rules, debugging). Helps agents borrow **workflow patterns**; unrelated to this repo’s Python research code.
  - `cursor-ai-tips-main/` — Cursor configuration/docs/tips (rules, weekly updates). Useful for **IDE and team conventions**, not for empirical crypto results.
  - `FinancialEconometrics-master/` — Julia notebooks, data, and PDFs for financial econometrics coursework. Useful for **econometric intuition** (e.g. breaks, VAR); code is **not** the `cqresearch` stack.

- **File extensions under `references/` (count):**
  - `md`: 122
  - `jl`: 33
  - `ipynb`: 28
  - `csv`: 9
  - `txt`: 9
  - `pdf`: 3
  - `json`: 2
  - `mdc`: 2
  - `gitattributes`: 1
  - `gitignore`: 1
  - `png`: 1

---

## 4. Full inventory (path + type + created UTC)

All repository paths except anything under `references/` other than the single top-level `references` directory row (see §3).

| Type | Path | Created (UTC) |
|------|------|----------------|
| dir | `.cursor` | 2026-04-18 21:54:56 UTC |
| dir | `.cursor/rules` | 2026-04-18 21:54:56 UTC |
| file | `.cursor/rules/data-integrity.mdc` | 2026-04-18 21:54:56 UTC |
| file | `.cursor/rules/defensive-commits.mdc` | 2026-04-18 21:54:56 UTC |
| file | `.cursor/rules/evidence-confidence.mdc` | 2026-04-18 21:54:56 UTC |
| file | `.cursor/rules/global-constitution.mdc` | 2026-04-18 21:54:56 UTC |
| file | `.cursor/rules/notebook-hygiene.mdc` | 2026-04-18 21:54:56 UTC |
| file | `.cursor/rules/spec-compliance.mdc` | 2026-04-18 21:54:56 UTC |
| dir | `.cursor/skills` | 2026-04-18 21:54:56 UTC |
| dir | `.cursor/skills/data-quality-check` | 2026-04-18 21:54:56 UTC |
| file | `.cursor/skills/data-quality-check/SKILL.md` | 2026-04-18 21:54:56 UTC |
| dir | `.cursor/skills/figure-template` | 2026-04-18 21:54:56 UTC |
| file | `.cursor/skills/figure-template/SKILL.md` | 2026-04-18 21:54:56 UTC |
| dir | `.cursor/skills/structural-break-runner` | 2026-04-18 21:54:56 UTC |
| file | `.cursor/skills/structural-break-runner/SKILL.md` | 2026-04-18 21:54:56 UTC |
| file | `.env` | 2026-04-14 22:22:34 UTC |
| file | `.env.example` | 2026-04-18 08:47:38 UTC |
| dir | `.github` | 2026-04-19 19:55:17 UTC |
| dir | `.github/workflows` | 2026-04-19 19:55:17 UTC |
| file | `.github/workflows/ci.yml` | 2026-04-19 19:55:17 UTC |
| file | `.gitignore` | 2026-04-12 06:39:49 UTC |
| file | `.pre-commit-config.yaml` | 2026-04-18 08:47:53 UTC |
| dir | `.pytest_cache` | 2026-04-18 09:03:32 UTC |
| file | `.pytest_cache/.gitignore` | 2026-04-18 09:03:32 UTC |
| file | `.pytest_cache/CACHEDIR.TAG` | 2026-04-18 09:03:32 UTC |
| file | `.pytest_cache/README.md` | 2026-04-18 09:03:32 UTC |
| dir | `.pytest_cache/v` | 2026-04-18 09:03:32 UTC |
| dir | `.pytest_cache/v/cache` | 2026-04-18 09:03:32 UTC |
| file | `.pytest_cache/v/cache/lastfailed` | 2026-04-18 09:03:32 UTC |
| file | `.pytest_cache/v/cache/nodeids` | 2026-04-18 09:03:51 UTC |
| dir | `.vscode` | 2026-04-18 21:53:15 UTC |
| file | `.vscode/settings.json` | 2026-04-18 21:53:15 UTC |
| dir | `archive` | 2026-04-18 08:46:04 UTC |
| file | `archive/.gitkeep` | 2026-04-18 08:46:12 UTC |
| file | `archive/current_status_analysis.md` | 2026-04-18 23:30:27 UTC |
| file | `archive/defillama_openapi_2026-04-14.json` | 2026-04-14 16:27:28 UTC |
| file | `archive/grok_convo_2026-04-16.txt` | 2026-04-16 01:59:54 UTC |
| dir | `config` | 2026-04-18 08:46:04 UTC |
| file | `config/__init__.py` | 2026-04-18 08:49:29 UTC |
| dir | `config/__pycache__` | 2026-04-18 09:02:09 UTC |
| file | `config/__pycache__/__init__.cpython-310.pyc` | 2026-04-19 01:01:12 UTC |
| file | `config/__pycache__/paths.cpython-310.pyc` | 2026-04-19 01:01:12 UTC |
| file | `config/calendars.yml` | 2026-04-18 08:49:41 UTC |
| file | `config/chain_taxonomy.yml` | 2026-04-18 08:49:51 UTC |
| file | `config/curation_snapshots.yml` | 2026-04-18 08:50:39 UTC |
| file | `config/events.yml` | 2026-04-18 08:50:28 UTC |
| file | `config/factor_blocks.yml` | 2026-04-18 08:50:12 UTC |
| file | `config/paths.py` | 2026-04-18 08:49:24 UTC |
| file | `Current_Architecture.md` | 2026-04-20 04:15:22 UTC |
| dir | `Data` | 2026-04-14 16:25:39 UTC |
| dir | `Data/_meta` | 2026-04-17 03:09:20 UTC |
| file | `Data/_meta/curated_manifest.csv` | 2026-04-17 03:19:05 UTC |
| file | `Data/_meta/curation_log.md` | 2026-04-17 03:09:47 UTC |
| file | `Data/_meta/raw_manifest.csv` | 2026-04-17 03:09:47 UTC |
| dir | `Data/AlternativeMe` | 2026-04-17 22:30:07 UTC |
| file | `Data/AlternativeMe/fear_greed_index__daily.csv` | 2026-04-17 22:30:07 UTC |
| file | `Data/AlternativeMe/README.md` | 2026-04-17 22:30:07 UTC |
| dir | `Data/Artemis` | 2026-04-16 02:17:39 UTC |
| file | `Data/Artemis/Adjusted Stablecoin Transactions by Region (Ethereum and Solana).csv` | 2026-04-16 02:45:54 UTC |
| file | `Data/Artemis/Artemis - Digital Asset Treasuries Overview.csv` | 2026-04-16 02:19:28 UTC |
| file | `Data/Artemis/Bitcoin ETFs AUM.csv` | 2026-04-16 02:27:15 UTC |
| file | `Data/Artemis/BTC DATs - Bitcoin Count.csv` | 2026-04-16 02:20:05 UTC |
| file | `Data/Artemis/BTC DATs- Fully Diluted EV NAV.csv` | 2026-04-16 02:20:30 UTC |
| file | `Data/Artemis/Centralized Exchanges - Open Interest.csv` | 2026-04-16 02:21:27 UTC |
| file | `Data/Artemis/Centralized Exchanges - Perpetuals Volume.csv` | 2026-04-16 02:21:17 UTC |
| file | `Data/Artemis/Centralized Exchanges - Spot Volume.csv` | 2026-04-16 02:21:23 UTC |
| file | `Data/Artemis/Chains - Chain MAU.csv` | 2026-04-16 02:47:37 UTC |
| file | `Data/Artemis/Chains - Daily Active Addresses (New Wallets).csv` | 2026-04-16 02:47:50 UTC |
| file | `Data/Artemis/Chains - Daily Active Addresses (Returning Wallets).csv` | 2026-04-16 02:47:58 UTC |
| file | `Data/Artemis/Chains - Fees.csv` | 2026-04-16 02:48:33 UTC |
| file | `Data/Artemis/Chains - Market Cap.csv` | 2026-04-16 02:48:38 UTC |
| file | `Data/Artemis/Chains - P2P Stablecoin Transaction Volume.csv` | 2026-04-16 02:48:10 UTC |
| file | `Data/Artemis/Chains - Revenue.csv` | 2026-04-16 02:48:29 UTC |
| file | `Data/Artemis/Chains - Stablecoin Supply.csv` | 2026-04-16 02:47:26 UTC |
| file | `Data/Artemis/Chains - Stablecoin Transaction Volume.csv` | 2026-04-16 02:48:17 UTC |
| file | `Data/Artemis/Crypto ETF AUM to Crypto Market Cap.csv` | 2026-04-16 02:27:07 UTC |
| file | `Data/Artemis/Crypto ETF Flows.csv` | 2026-04-16 02:27:09 UTC |
| file | `Data/Artemis/Crypto ETFs AUM.csv` | 2026-04-16 02:27:00 UTC |
| file | `Data/Artemis/DEX - Spot DEX Daily Active Users.csv` | 2026-04-16 02:23:26 UTC |
| file | `Data/Artemis/DEX - Spot Fees.csv` | 2026-04-16 02:23:22 UTC |
| file | `Data/Artemis/DEX - Spot Volume.csv` | 2026-04-16 02:23:12 UTC |
| file | `Data/Artemis/DEX - TVL.csv` | 2026-04-16 02:23:29 UTC |
| file | `Data/Artemis/Ethereum ETFs AUM.csv` | 2026-04-16 02:27:30 UTC |
| file | `Data/Artemis/Lending Borrows by Chain.csv` | 2026-04-16 02:26:13 UTC |
| file | `Data/Artemis/Lending Borrows by Protocol.csv` | 2026-04-16 02:25:53 UTC |
| file | `Data/Artemis/Lending Deposits by Chain.csv` | 2026-04-16 02:26:20 UTC |
| file | `Data/Artemis/Lending Deposits by Protocol.csv` | 2026-04-16 02:25:47 UTC |
| file | `Data/Artemis/Lending Interest Fees by Protocol.csv` | 2026-04-16 02:26:36 UTC |
| file | `Data/Artemis/Lending Protocol Revenue.csv` | 2026-04-16 02:25:24 UTC |
| file | `Data/Artemis/Liquid Restaking - LRT TVL (USD).csv` | 2026-04-16 02:44:31 UTC |
| file | `Data/Artemis/Liquid Staking - LST TVL (USD).csv` | 2026-04-16 02:44:20 UTC |
| file | `Data/Artemis/Monthly Bitcoin ETF flows.csv` | 2026-04-16 02:27:22 UTC |
| file | `Data/Artemis/Monthly Ethereum ETF flows.csv` | 2026-04-16 02:27:27 UTC |
| file | `Data/Artemis/Monthly Solana ETF flows.csv` | 2026-04-16 02:27:34 UTC |
| file | `Data/Artemis/Perpetuals Daily Active Users for Trading Platforms.csv` | 2026-04-16 02:18:00 UTC |
| file | `Data/Artemis/Perpetuals Open Interest for Trading Platforms.csv` | 2026-04-16 02:18:21 UTC |
| file | `Data/Artemis/Perpetuals Volume for Protocols.csv` | 2026-04-16 02:18:40 UTC |
| file | `Data/Artemis/Perpetuals Volume for Trading Platforms.csv` | 2026-04-16 02:17:45 UTC |
| file | `Data/Artemis/README.md` | 2026-04-17 03:17:34 UTC |
| file | `Data/Artemis/RWA - Tokenized Market Cap.csv` | 2026-04-16 02:43:57 UTC |
| file | `Data/Artemis/Solana ETFs AUM.csv` | 2026-04-16 02:27:36 UTC |
| file | `Data/Artemis/Stablecoin Active Addresses by Chain.csv` | 2026-04-16 02:45:37 UTC |
| file | `Data/Artemis/Stablecoin Active Addresses by Token.csv` | 2026-04-16 02:45:33 UTC |
| file | `Data/Artemis/Stablecoin Market Share by Token.csv` | 2026-04-16 02:45:41 UTC |
| file | `Data/Artemis/Stablecoin Supply by Chain.csv` | 2026-04-16 02:45:28 UTC |
| file | `Data/Artemis/Stablecoin Supply by Currency.csv` | 2026-04-16 02:46:01 UTC |
| file | `Data/Artemis/Stablecoin Supply by Token.csv` | 2026-04-16 02:45:20 UTC |
| dir | `Data/CryptoQuant` | 2026-04-12 05:50:00 UTC |
| dir | `Data/CryptoQuant/BTC` | 2026-04-12 05:50:00 UTC |
| dir | `Data/CryptoQuant/BTC/Addresses` | 2026-04-12 06:08:58 UTC |
| file | `Data/CryptoQuant/BTC/Addresses/Bitcoin Active Addresses - Day.csv` | 2026-04-12 05:50:00 UTC |
| file | `Data/CryptoQuant/BTC/Addresses/Bitcoin Active Receiving Addresses - Day.csv` | 2026-04-12 05:50:00 UTC |
| file | `Data/CryptoQuant/BTC/Addresses/Bitcoin Active Sending Addresses - Day.csv` | 2026-04-12 05:50:00 UTC |
| file | `Data/CryptoQuant/BTC/Addresses/README.md` | 2026-04-17 03:17:34 UTC |
| file | `Data/CryptoQuant/BTC/BTC_Metrics.txt` | 2026-04-12 06:08:59 UTC |
| dir | `Data/CryptoQuant/BTC/Derivatives` | 2026-04-12 06:08:58 UTC |
| file | `Data/CryptoQuant/BTC/Derivatives/Bitcoin Estimated Leverage Ratio - All Exchanges - Day.csv` | 2026-04-12 05:50:00 UTC |
| file | `Data/CryptoQuant/BTC/Derivatives/Bitcoin Funding Rates - All Exchanges - Day.csv` | 2026-04-12 05:50:00 UTC |
| file | `Data/CryptoQuant/BTC/Derivatives/Bitcoin Futures Taker CVD(Cumulative Volume Delta, 90-day) - Day.csv` | 2026-04-12 05:50:00 UTC |
| file | `Data/CryptoQuant/BTC/Derivatives/Bitcoin Long Liquidations - All Exchanges, All Symbol - Day.csv` | 2026-04-12 05:50:00 UTC |
| file | `Data/CryptoQuant/BTC/Derivatives/Bitcoin Long Liquidations USD - All Exchanges, All Symbol - Day.csv` | 2026-04-12 05:50:00 UTC |
| file | `Data/CryptoQuant/BTC/Derivatives/Bitcoin Open Interest - All Exchanges, All Symbol - Day.csv` | 2026-04-12 05:50:00 UTC |
| file | `Data/CryptoQuant/BTC/Derivatives/Bitcoin Short Liquidations - All Exchanges, All Symbol - Day.csv` | 2026-04-12 05:50:01 UTC |
| file | `Data/CryptoQuant/BTC/Derivatives/Bitcoin Short Liquidations USD - All Exchanges, All Symbol - Day.csv` | 2026-04-12 05:50:01 UTC |
| file | `Data/CryptoQuant/BTC/Derivatives/README.md` | 2026-04-17 03:17:34 UTC |
| dir | `Data/CryptoQuant/BTC/Exchange Flows` | 2026-04-12 06:08:58 UTC |
| file | `Data/CryptoQuant/BTC/Exchange Flows/Bitcoin Exchange Depositing Addresses - All Exchanges - Day.csv` | 2026-04-12 05:50:00 UTC |
| file | `Data/CryptoQuant/BTC/Exchange Flows/Bitcoin Exchange Depositing Transactions - All Exchanges - Day.csv` | 2026-04-12 05:50:00 UTC |
| file | `Data/CryptoQuant/BTC/Exchange Flows/Bitcoin Exchange In-House Flow (Mean) - All Exchanges - Day.csv` | 2026-04-12 05:50:00 UTC |
| file | `Data/CryptoQuant/BTC/Exchange Flows/Bitcoin Exchange In-House Flow (Total) - All Exchanges - Day.csv` | 2026-04-12 05:50:00 UTC |
| file | `Data/CryptoQuant/BTC/Exchange Flows/Bitcoin Exchange In-House Transactions - All Exchanges - Day.csv` | 2026-04-12 05:50:00 UTC |
| file | `Data/CryptoQuant/BTC/Exchange Flows/Bitcoin Exchange Inflow (Mean) - All Exchanges - Day.csv` | 2026-04-12 05:50:00 UTC |
| file | `Data/CryptoQuant/BTC/Exchange Flows/Bitcoin Exchange Inflow (Top10) - All Exchanges - Day.csv` | 2026-04-12 05:50:00 UTC |
| file | `Data/CryptoQuant/BTC/Exchange Flows/Bitcoin Exchange Inflow (Total) - All Exchanges - Day.csv` | 2026-04-12 05:50:00 UTC |
| file | `Data/CryptoQuant/BTC/Exchange Flows/Bitcoin Exchange Inflow - Spent Output Age Bands - All Exchanges - Day.csv` | 2026-04-12 05:50:00 UTC |
| file | `Data/CryptoQuant/BTC/Exchange Flows/Bitcoin Exchange Inflow - Spent Output Value Bands - All Exchanges - Day.csv` | 2026-04-12 05:50:00 UTC |
| file | `Data/CryptoQuant/BTC/Exchange Flows/Bitcoin Exchange Netflow (Total) - All Exchanges - Day.csv` | 2026-04-12 05:50:00 UTC |
| file | `Data/CryptoQuant/BTC/Exchange Flows/Bitcoin Exchange Outflow (Mean) - All Exchanges - Day.csv` | 2026-04-12 05:50:00 UTC |
| file | `Data/CryptoQuant/BTC/Exchange Flows/Bitcoin Exchange Outflow (Top10) - All Exchanges - Day.csv` | 2026-04-12 05:50:00 UTC |
| file | `Data/CryptoQuant/BTC/Exchange Flows/Bitcoin Exchange Outflow (Total) - All Exchanges - Day.csv` | 2026-04-12 05:50:00 UTC |
| file | `Data/CryptoQuant/BTC/Exchange Flows/Bitcoin Exchange Reserve - All Exchanges - Day.csv` | 2026-04-12 05:50:00 UTC |
| file | `Data/CryptoQuant/BTC/Exchange Flows/Bitcoin Exchange Reserve USD - All Exchanges - Day.csv` | 2026-04-12 05:50:00 UTC |
| file | `Data/CryptoQuant/BTC/Exchange Flows/Bitcoin Exchange Withdrawing Addresses - All Exchanges - Day.csv` | 2026-04-12 05:50:00 UTC |
| file | `Data/CryptoQuant/BTC/Exchange Flows/Bitcoin Exchange Withdrawing Transactions - All Exchanges - Day.csv` | 2026-04-12 05:50:00 UTC |
| file | `Data/CryptoQuant/BTC/Exchange Flows/README.md` | 2026-04-17 03:17:34 UTC |
| dir | `Data/CryptoQuant/BTC/Fees And Revenue` | 2026-04-12 06:08:58 UTC |
| file | `Data/CryptoQuant/BTC/Fees And Revenue/Bitcoin Block Rewards - Day.csv` | 2026-04-12 05:50:00 UTC |
| file | `Data/CryptoQuant/BTC/Fees And Revenue/Bitcoin Block Rewards USD - Day.csv` | 2026-04-12 05:50:00 UTC |
| file | `Data/CryptoQuant/BTC/Fees And Revenue/Bitcoin Fees (Total) - Day.csv` | 2026-04-12 05:50:00 UTC |
| file | `Data/CryptoQuant/BTC/Fees And Revenue/Bitcoin Fees per Block (Mean) - Day.csv` | 2026-04-12 05:50:00 UTC |
| file | `Data/CryptoQuant/BTC/Fees And Revenue/Bitcoin Fees per Block USD (Mean) - Day.csv` | 2026-04-12 05:50:00 UTC |
| file | `Data/CryptoQuant/BTC/Fees And Revenue/Bitcoin Fees per Transaction (Mean) - Day.csv` | 2026-04-12 05:50:00 UTC |
| file | `Data/CryptoQuant/BTC/Fees And Revenue/Bitcoin Fees per Transaction (Median) - Day.csv` | 2026-04-12 05:50:00 UTC |
| file | `Data/CryptoQuant/BTC/Fees And Revenue/Bitcoin Fees per Transaction USD (Mean) - Day.csv` | 2026-04-12 05:50:00 UTC |
| file | `Data/CryptoQuant/BTC/Fees And Revenue/Bitcoin Fees per Transaction USD (Median) - Day.csv` | 2026-04-12 05:50:00 UTC |
| file | `Data/CryptoQuant/BTC/Fees And Revenue/Bitcoin Fees to Reward Ratio - Day.csv` | 2026-04-12 05:50:00 UTC |
| file | `Data/CryptoQuant/BTC/Fees And Revenue/Bitcoin Fees USD (Total) - Day.csv` | 2026-04-12 05:50:00 UTC |
| file | `Data/CryptoQuant/BTC/Fees And Revenue/README.md` | 2026-04-17 03:17:34 UTC |
| dir | `Data/CryptoQuant/BTC/Flow Indicator` | 2026-04-12 06:08:58 UTC |
| file | `Data/CryptoQuant/BTC/Flow Indicator/Bitcoin Exchange Inflow CDD - All Exchanges - Day.csv` | 2026-04-12 05:50:00 UTC |
| file | `Data/CryptoQuant/BTC/Flow Indicator/Bitcoin Exchange Stablecoins Ratio - All Exchanges - Day.csv` | 2026-04-12 05:50:00 UTC |
| file | `Data/CryptoQuant/BTC/Flow Indicator/Bitcoin Exchange Stablecoins Ratio USD - All Exchanges - Day.csv` | 2026-04-12 05:50:00 UTC |
| file | `Data/CryptoQuant/BTC/Flow Indicator/Bitcoin Exchange Supply Ratio - All Exchanges - Day.csv` | 2026-04-12 05:50:00 UTC |
| file | `Data/CryptoQuant/BTC/Flow Indicator/Bitcoin Exchange Whale Ratio - All Exchanges - Day.csv` | 2026-04-12 05:50:00 UTC |
| file | `Data/CryptoQuant/BTC/Flow Indicator/Bitcoin Fund Flow Ratio - All Exchanges - Day.csv` | 2026-04-12 05:50:00 UTC |
| file | `Data/CryptoQuant/BTC/Flow Indicator/Bitcoin Stablecoin Supply Ratio (SSR) - Day.csv` | 2026-04-12 05:50:01 UTC |
| file | `Data/CryptoQuant/BTC/Flow Indicator/README.md` | 2026-04-17 03:17:34 UTC |
| dir | `Data/CryptoQuant/BTC/Fund Data` | 2026-04-12 06:08:58 UTC |
| file | `Data/CryptoQuant/BTC/Fund Data/Bitcoin Coinbase Premium Gap - Day.csv` | 2026-04-12 05:50:00 UTC |
| file | `Data/CryptoQuant/BTC/Fund Data/Bitcoin Coinbase Premium Index - Day.csv` | 2026-04-12 05:50:00 UTC |
| file | `Data/CryptoQuant/BTC/Fund Data/Bitcoin Fund Holdings - All Symbol - Day.csv` | 2026-04-12 05:50:00 UTC |
| file | `Data/CryptoQuant/BTC/Fund Data/Bitcoin Fund Market Premium - All Symbol - Day.csv` | 2026-04-12 05:50:00 UTC |
| file | `Data/CryptoQuant/BTC/Fund Data/Bitcoin Fund Price (USD) - GBTC - Day.csv` | 2026-04-12 05:50:00 UTC |
| file | `Data/CryptoQuant/BTC/Fund Data/Bitcoin Fund Volume - All Symbol - Day.csv` | 2026-04-12 05:50:00 UTC |
| file | `Data/CryptoQuant/BTC/Fund Data/Bitcoin Korea Premium Index - Day.csv` | 2026-04-12 05:50:00 UTC |
| file | `Data/CryptoQuant/BTC/Fund Data/README.md` | 2026-04-17 03:17:34 UTC |
| dir | `Data/CryptoQuant/BTC/Inter Entity Flows` | 2026-04-12 06:08:58 UTC |
| file | `Data/CryptoQuant/BTC/Inter Entity Flows/Bitcoin Exchange to Exchange Flow (Mean) - All Exchanges, Spot Exchanges - Day.csv` | 2026-04-12 05:50:00 UTC |
| file | `Data/CryptoQuant/BTC/Inter Entity Flows/Bitcoin Exchange to Exchange Flow (Total) - All Exchanges, Spot Exchanges - Day.csv` | 2026-04-12 05:50:00 UTC |
| file | `Data/CryptoQuant/BTC/Inter Entity Flows/Bitcoin Exchange to Exchange Transactions - All Exchanges, Spot Exchanges - Day.csv` | 2026-04-12 05:50:00 UTC |
| file | `Data/CryptoQuant/BTC/Inter Entity Flows/Bitcoin Miner to Miner Flow (Mean) - All Miners, 1THash - Day.csv` | 2026-04-12 05:50:00 UTC |
| file | `Data/CryptoQuant/BTC/Inter Entity Flows/Bitcoin Miner to Miner Flow (Total) - All Miners, 1THash - Day.csv` | 2026-04-12 05:50:00 UTC |
| file | `Data/CryptoQuant/BTC/Inter Entity Flows/Bitcoin Miner to Miner Transactions - All Miners, 1THash - Day.csv` | 2026-04-12 05:50:00 UTC |
| file | `Data/CryptoQuant/BTC/Inter Entity Flows/README.md` | 2026-04-17 03:17:34 UTC |
| dir | `Data/CryptoQuant/BTC/Market Data` | 2026-04-12 06:08:58 UTC |
| file | `Data/CryptoQuant/BTC/Market Data/Bitcoin Average Cap - Day.csv` | 2026-04-12 05:50:00 UTC |
| file | `Data/CryptoQuant/BTC/Market Data/Bitcoin Delta Cap - Day.csv` | 2026-04-12 05:50:00 UTC |
| file | `Data/CryptoQuant/BTC/Market Data/Bitcoin Exchange Supply - Day.csv` | 2026-04-12 05:50:00 UTC |
| file | `Data/CryptoQuant/BTC/Market Data/Bitcoin Geographical Supply Distribution by Entities - Day.csv` | 2026-04-12 05:50:00 UTC |
| file | `Data/CryptoQuant/BTC/Market Data/Bitcoin Market Cap - Day.csv` | 2026-04-12 05:50:00 UTC |
| file | `Data/CryptoQuant/BTC/Market Data/Bitcoin Price & Volume - Spot, All Exchanges, BTC-USD - Day.csv` | 2026-04-12 05:50:00 UTC |
| file | `Data/CryptoQuant/BTC/Market Data/Bitcoin Price & Volume KRW - Spot - Day.csv` | 2026-04-12 05:50:00 UTC |
| file | `Data/CryptoQuant/BTC/Market Data/Bitcoin Realized Cap - Day.csv` | 2026-04-12 05:50:00 UTC |
| file | `Data/CryptoQuant/BTC/Market Data/Bitcoin Realized Cap - UTXO Age Bands (%) - Day.csv` | 2026-04-12 05:50:00 UTC |
| file | `Data/CryptoQuant/BTC/Market Data/Bitcoin Realized Cap - UTXO Age Bands USD - Day.csv` | 2026-04-12 05:50:00 UTC |
| file | `Data/CryptoQuant/BTC/Market Data/Bitcoin Realized Cap - UTXO Value Bands (%) - Day.csv` | 2026-04-12 05:50:00 UTC |
| file | `Data/CryptoQuant/BTC/Market Data/Bitcoin Realized Cap - UTXO Value Bands USD - Day.csv` | 2026-04-12 05:50:00 UTC |
| file | `Data/CryptoQuant/BTC/Market Data/Bitcoin Taker Buy Ratio - All Exchanges - Day.csv` | 2026-04-12 05:50:01 UTC |
| file | `Data/CryptoQuant/BTC/Market Data/Bitcoin Taker Buy Sell Ratio - All Exchanges - Day.csv` | 2026-04-12 05:50:01 UTC |
| file | `Data/CryptoQuant/BTC/Market Data/Bitcoin Taker Buy Volume - All Exchanges - Day.csv` | 2026-04-12 05:50:01 UTC |
| file | `Data/CryptoQuant/BTC/Market Data/Bitcoin Taker Sell Ratio - All Exchanges - Day.csv` | 2026-04-12 05:50:01 UTC |
| file | `Data/CryptoQuant/BTC/Market Data/Bitcoin Taker Sell Volume - All Exchanges - Day.csv` | 2026-04-12 05:50:01 UTC |
| file | `Data/CryptoQuant/BTC/Market Data/Bitcoin Thermo Cap - Day.csv` | 2026-04-12 05:50:01 UTC |
| file | `Data/CryptoQuant/BTC/Market Data/Bitcoin Trading Volume (KYC VS. Non-KYC) - Day.csv` | 2026-04-12 05:50:01 UTC |
| file | `Data/CryptoQuant/BTC/Market Data/Bitcoin Trading Volume (Spot VS. Derivative) - Day.csv` | 2026-04-12 05:50:01 UTC |
| file | `Data/CryptoQuant/BTC/Market Data/README.md` | 2026-04-17 03:17:34 UTC |
| dir | `Data/CryptoQuant/BTC/Market Indicator` | 2026-04-12 06:08:58 UTC |
| file | `Data/CryptoQuant/BTC/Market Indicator/Bitcoin Adjusted SOPR (aSOPR) - Day.csv` | 2026-04-12 05:50:00 UTC |
| file | `Data/CryptoQuant/BTC/Market Indicator/Bitcoin Average Dormancy - Day.csv` | 2026-04-12 05:50:00 UTC |
| file | `Data/CryptoQuant/BTC/Market Indicator/Bitcoin Average Supply-Adjusted CDD - Day.csv` | 2026-04-12 05:50:00 UTC |
| file | `Data/CryptoQuant/BTC/Market Indicator/Bitcoin Binary CDD - Day.csv` | 2026-04-12 05:50:00 UTC |
| file | `Data/CryptoQuant/BTC/Market Indicator/Bitcoin Long Term Holder SOPR - Day.csv` | 2026-04-12 05:50:00 UTC |
| file | `Data/CryptoQuant/BTC/Market Indicator/Bitcoin Mean Coin Age - Day.csv` | 2026-04-12 05:50:00 UTC |
| file | `Data/CryptoQuant/BTC/Market Indicator/Bitcoin Mean Coin Dollar Age - Day.csv` | 2026-04-12 05:50:00 UTC |
| file | `Data/CryptoQuant/BTC/Market Indicator/Bitcoin MVRV Ratio - Day.csv` | 2026-04-12 05:50:00 UTC |
| file | `Data/CryptoQuant/BTC/Market Indicator/Bitcoin Net Unrealized Loss (NUL) - Day.csv` | 2026-04-12 05:50:00 UTC |
| file | `Data/CryptoQuant/BTC/Market Indicator/Bitcoin Net Unrealized Profit (NUP) - Day.csv` | 2026-04-12 05:50:00 UTC |
| file | `Data/CryptoQuant/BTC/Market Indicator/Bitcoin Net Unrealized Profit_Loss (NUPL) - Day.csv` | 2026-04-12 05:50:00 UTC |
| file | `Data/CryptoQuant/BTC/Market Indicator/Bitcoin NVM Ratio - Day.csv` | 2026-04-12 05:50:00 UTC |
| file | `Data/CryptoQuant/BTC/Market Indicator/Bitcoin NVT Golden Cross - Day.csv` | 2026-04-12 05:50:00 UTC |
| file | `Data/CryptoQuant/BTC/Market Indicator/Bitcoin NVT Ratio - Day.csv` | 2026-04-12 05:50:00 UTC |
| file | `Data/CryptoQuant/BTC/Market Indicator/Bitcoin Puell Multiple - Day.csv` | 2026-04-12 05:50:00 UTC |
| file | `Data/CryptoQuant/BTC/Market Indicator/Bitcoin Realized Price - Day.csv` | 2026-04-12 05:50:00 UTC |
| file | `Data/CryptoQuant/BTC/Market Indicator/Bitcoin Realized Price - UTXO Age Bands - Day.csv` | 2026-04-12 05:50:01 UTC |
| file | `Data/CryptoQuant/BTC/Market Indicator/Bitcoin Short Term Holder SOPR - Day.csv` | 2026-04-12 05:50:01 UTC |
| file | `Data/CryptoQuant/BTC/Market Indicator/Bitcoin SOPR Ratio (LTH-SOPR_STH-SOPR) - Day.csv` | 2026-04-12 05:50:01 UTC |
| file | `Data/CryptoQuant/BTC/Market Indicator/Bitcoin Spent Output Age Bands (%) - Day.csv` | 2026-04-12 05:50:01 UTC |
| file | `Data/CryptoQuant/BTC/Market Indicator/Bitcoin Spent Output Age Bands - Day.csv` | 2026-04-12 05:50:01 UTC |
| file | `Data/CryptoQuant/BTC/Market Indicator/Bitcoin Spent Output Age Bands USD - Day.csv` | 2026-04-12 05:50:01 UTC |
| file | `Data/CryptoQuant/BTC/Market Indicator/Bitcoin Spent Output Profit Ratio (SOPR) - Day.csv` | 2026-04-12 05:50:01 UTC |
| file | `Data/CryptoQuant/BTC/Market Indicator/Bitcoin Spent Output Value Bands (%) - Day.csv` | 2026-04-12 05:50:01 UTC |
| file | `Data/CryptoQuant/BTC/Market Indicator/Bitcoin Spent Output Value Bands - Day.csv` | 2026-04-12 05:50:01 UTC |
| file | `Data/CryptoQuant/BTC/Market Indicator/Bitcoin Spent Output Value Bands USD - Day.csv` | 2026-04-12 05:50:01 UTC |
| file | `Data/CryptoQuant/BTC/Market Indicator/Bitcoin Spot Taker CVD(Cumulative Volume Delta, 90-day) - Day.csv` | 2026-04-12 05:50:01 UTC |
| file | `Data/CryptoQuant/BTC/Market Indicator/Bitcoin Stock-to-Flow Ratio - Day.csv` | 2026-04-12 05:50:01 UTC |
| file | `Data/CryptoQuant/BTC/Market Indicator/Bitcoin Stock-to-Flow Reversion - Day.csv` | 2026-04-12 05:50:01 UTC |
| file | `Data/CryptoQuant/BTC/Market Indicator/Bitcoin Sum Coin Age - Day.csv` | 2026-04-12 05:50:01 UTC |
| file | `Data/CryptoQuant/BTC/Market Indicator/Bitcoin Sum Coin Age Distribution (%) - Day.csv` | 2026-04-12 05:50:01 UTC |
| file | `Data/CryptoQuant/BTC/Market Indicator/Bitcoin Sum Coin Age Distribution - Day.csv` | 2026-04-12 05:50:01 UTC |
| file | `Data/CryptoQuant/BTC/Market Indicator/Bitcoin Sum Coin Dollar Age - Day.csv` | 2026-04-12 05:50:01 UTC |
| file | `Data/CryptoQuant/BTC/Market Indicator/Bitcoin Supply Adjusted Dormancy - Day.csv` | 2026-04-12 05:50:01 UTC |
| file | `Data/CryptoQuant/BTC/Market Indicator/Bitcoin Supply in Loss (%) - Day.csv` | 2026-04-12 05:50:01 UTC |
| file | `Data/CryptoQuant/BTC/Market Indicator/Bitcoin Supply in Loss - Day.csv` | 2026-04-12 05:50:01 UTC |
| file | `Data/CryptoQuant/BTC/Market Indicator/Bitcoin Supply in Profit (%) - Day.csv` | 2026-04-12 05:50:01 UTC |
| file | `Data/CryptoQuant/BTC/Market Indicator/Bitcoin Supply in Profit - Day.csv` | 2026-04-12 05:50:01 UTC |
| file | `Data/CryptoQuant/BTC/Market Indicator/Bitcoin Supply-Adjusted CDD - Day.csv` | 2026-04-12 05:50:01 UTC |
| file | `Data/CryptoQuant/BTC/Market Indicator/README.md` | 2026-04-17 03:17:34 UTC |
| dir | `Data/CryptoQuant/BTC/Miner Flows` | 2026-04-12 06:08:58 UTC |
| file | `Data/CryptoQuant/BTC/Miner Flows/Bitcoin Exchange to Miner Flow (Mean) - All Exchanges, All Miners - Day.csv` | 2026-04-12 05:50:00 UTC |
| file | `Data/CryptoQuant/BTC/Miner Flows/Bitcoin Exchange to Miner Flow (Total) - All Exchanges, All Miners - Day.csv` | 2026-04-12 05:50:00 UTC |
| file | `Data/CryptoQuant/BTC/Miner Flows/Bitcoin Exchange to Miner Transactions - All Exchanges, All Miners - Day.csv` | 2026-04-12 05:50:00 UTC |
| file | `Data/CryptoQuant/BTC/Miner Flows/Bitcoin Miner Depositing Addresses - All Miners - Day.csv` | 2026-04-12 05:50:00 UTC |
| file | `Data/CryptoQuant/BTC/Miner Flows/Bitcoin Miner Depositing Transactions - All Miners - Day.csv` | 2026-04-12 05:50:00 UTC |
| file | `Data/CryptoQuant/BTC/Miner Flows/Bitcoin Miner In-House Flow (Mean) - All Miners - Day.csv` | 2026-04-12 05:50:00 UTC |
| file | `Data/CryptoQuant/BTC/Miner Flows/Bitcoin Miner In-House Flow (Total) - All Miners - Day.csv` | 2026-04-12 05:50:00 UTC |
| file | `Data/CryptoQuant/BTC/Miner Flows/Bitcoin Miner In-House Transactions - All Miners - Day.csv` | 2026-04-12 05:50:00 UTC |
| file | `Data/CryptoQuant/BTC/Miner Flows/Bitcoin Miner Inflow (Mean) - All Miners - Day.csv` | 2026-04-12 05:50:00 UTC |
| file | `Data/CryptoQuant/BTC/Miner Flows/Bitcoin Miner Inflow (Top10) - All Miners - Day.csv` | 2026-04-12 05:50:00 UTC |
| file | `Data/CryptoQuant/BTC/Miner Flows/Bitcoin Miner Inflow (Total) - All Miners - Day.csv` | 2026-04-12 05:50:00 UTC |
| file | `Data/CryptoQuant/BTC/Miner Flows/Bitcoin Miner Netflow Total - All Miners - Day.csv` | 2026-04-12 05:50:00 UTC |
| file | `Data/CryptoQuant/BTC/Miner Flows/Bitcoin Miner Outflow (Mean) - All Miners - Day.csv` | 2026-04-12 05:50:00 UTC |
| file | `Data/CryptoQuant/BTC/Miner Flows/Bitcoin Miner Outflow (Top10) - All Miners - Day.csv` | 2026-04-12 05:50:00 UTC |
| file | `Data/CryptoQuant/BTC/Miner Flows/Bitcoin Miner Outflow (Total) - All Miners - Day.csv` | 2026-04-12 05:50:00 UTC |
| file | `Data/CryptoQuant/BTC/Miner Flows/Bitcoin Miner Reserve - All Miners - Day.csv` | 2026-04-12 05:50:00 UTC |
| file | `Data/CryptoQuant/BTC/Miner Flows/Bitcoin Miner Reserve USD - All Miners - Day.csv` | 2026-04-12 05:50:00 UTC |
| file | `Data/CryptoQuant/BTC/Miner Flows/Bitcoin Miner Supply Ratio - All Miners - Day.csv` | 2026-04-12 05:50:00 UTC |
| file | `Data/CryptoQuant/BTC/Miner Flows/Bitcoin Miner to Exchange Flow (Mean) - All Miners, All Exchanges - Day.csv` | 2026-04-12 05:50:00 UTC |
| file | `Data/CryptoQuant/BTC/Miner Flows/Bitcoin Miner to Exchange Flow (Total) - All Miners, All Exchanges - Day.csv` | 2026-04-12 05:50:00 UTC |
| file | `Data/CryptoQuant/BTC/Miner Flows/Bitcoin Miner to Exchange Transactions - All Miners, All Exchanges - Day.csv` | 2026-04-12 05:50:00 UTC |
| file | `Data/CryptoQuant/BTC/Miner Flows/Bitcoin Miner Withdrawing Addresses - All Miners - Day.csv` | 2026-04-12 05:50:00 UTC |
| file | `Data/CryptoQuant/BTC/Miner Flows/Bitcoin Miner Withdrawing Transactions - All Miners - Day.csv` | 2026-04-12 05:50:00 UTC |
| file | `Data/CryptoQuant/BTC/Miner Flows/Bitcoin Miners' Position Index (MPI) - Day.csv` | 2026-04-12 05:50:00 UTC |
| file | `Data/CryptoQuant/BTC/Miner Flows/README.md` | 2026-04-17 03:17:34 UTC |
| dir | `Data/CryptoQuant/BTC/Network Indicator` | 2026-04-12 06:08:58 UTC |
| file | `Data/CryptoQuant/BTC/Network Indicator/Bitcoin Coin Days Destroyed (CDD) - Day.csv` | 2026-04-12 05:50:00 UTC |
| file | `Data/CryptoQuant/BTC/Network Indicator/Bitcoin UTXO Age Bands (%) - Day.csv` | 2026-04-12 05:50:01 UTC |
| file | `Data/CryptoQuant/BTC/Network Indicator/Bitcoin UTXO Age Bands - Day.csv` | 2026-04-12 05:50:01 UTC |
| file | `Data/CryptoQuant/BTC/Network Indicator/Bitcoin UTXO Age Bands USD - Day.csv` | 2026-04-12 05:50:01 UTC |
| file | `Data/CryptoQuant/BTC/Network Indicator/Bitcoin UTXO Count - Age Bands (%) - Day.csv` | 2026-04-12 05:50:01 UTC |
| file | `Data/CryptoQuant/BTC/Network Indicator/Bitcoin UTXO Count - Age Bands - Day.csv` | 2026-04-12 05:50:01 UTC |
| file | `Data/CryptoQuant/BTC/Network Indicator/Bitcoin UTXO Count - Value Bands (%) - Day.csv` | 2026-04-12 05:50:01 UTC |
| file | `Data/CryptoQuant/BTC/Network Indicator/Bitcoin UTXO Count - Value Bands - Day.csv` | 2026-04-12 05:50:01 UTC |
| file | `Data/CryptoQuant/BTC/Network Indicator/Bitcoin UTXO Value Bands (%) - Day.csv` | 2026-04-12 05:50:01 UTC |
| file | `Data/CryptoQuant/BTC/Network Indicator/Bitcoin UTXO Value Bands - Day.csv` | 2026-04-12 05:50:01 UTC |
| file | `Data/CryptoQuant/BTC/Network Indicator/Bitcoin UTXOs in Loss (%) - Day.csv` | 2026-04-12 05:50:01 UTC |
| file | `Data/CryptoQuant/BTC/Network Indicator/Bitcoin UTXOs in Loss - Day.csv` | 2026-04-12 05:50:01 UTC |
| file | `Data/CryptoQuant/BTC/Network Indicator/Bitcoin UTXOs in Profit (%) - Day.csv` | 2026-04-12 05:50:01 UTC |
| file | `Data/CryptoQuant/BTC/Network Indicator/Bitcoin UTXOs in Profit - Day.csv` | 2026-04-12 05:50:01 UTC |
| file | `Data/CryptoQuant/BTC/Network Indicator/README.md` | 2026-04-17 03:17:34 UTC |
| dir | `Data/CryptoQuant/BTC/Network Stats` | 2026-04-12 06:08:58 UTC |
| file | `Data/CryptoQuant/BTC/Network Stats/Bitcoin Block Interval (Mean) - Day.csv` | 2026-04-12 05:50:00 UTC |
| file | `Data/CryptoQuant/BTC/Network Stats/Bitcoin Block Size (Mean) - Day.csv` | 2026-04-12 05:50:00 UTC |
| file | `Data/CryptoQuant/BTC/Network Stats/Bitcoin Blocks Mined - Day.csv` | 2026-04-12 05:50:00 UTC |
| file | `Data/CryptoQuant/BTC/Network Stats/Bitcoin Difficulty - Day.csv` | 2026-04-12 05:50:00 UTC |
| file | `Data/CryptoQuant/BTC/Network Stats/Bitcoin Hashrate - Day.csv` | 2026-04-12 05:50:00 UTC |
| file | `Data/CryptoQuant/BTC/Network Stats/Bitcoin UTXO Count - Day.csv` | 2026-04-12 05:50:01 UTC |
| file | `Data/CryptoQuant/BTC/Network Stats/Bitcoin Velocity - Day.csv` | 2026-04-12 05:50:01 UTC |
| file | `Data/CryptoQuant/BTC/Network Stats/README.md` | 2026-04-17 03:17:34 UTC |
| dir | `Data/CryptoQuant/BTC/Supply` | 2026-04-12 06:08:58 UTC |
| file | `Data/CryptoQuant/BTC/Supply/Bitcoin New Supply - Day.csv` | 2026-04-12 05:50:00 UTC |
| file | `Data/CryptoQuant/BTC/Supply/Bitcoin Total Supply - Day.csv` | 2026-04-12 05:50:01 UTC |
| file | `Data/CryptoQuant/BTC/Supply/README.md` | 2026-04-17 03:17:34 UTC |
| dir | `Data/CryptoQuant/BTC/Transactions` | 2026-04-12 06:08:58 UTC |
| file | `Data/CryptoQuant/BTC/Transactions/Bitcoin Tokens Transferred (Mean) - Day.csv` | 2026-04-12 05:50:01 UTC |
| file | `Data/CryptoQuant/BTC/Transactions/Bitcoin Tokens Transferred (Median) - Day.csv` | 2026-04-12 05:50:01 UTC |
| file | `Data/CryptoQuant/BTC/Transactions/Bitcoin Tokens Transferred (Total) - Day.csv` | 2026-04-12 05:50:01 UTC |
| file | `Data/CryptoQuant/BTC/Transactions/Bitcoin Transaction Count (Mean) - Day.csv` | 2026-04-12 05:50:01 UTC |
| file | `Data/CryptoQuant/BTC/Transactions/Bitcoin Transaction Count (Total) - Day.csv` | 2026-04-12 05:50:01 UTC |
| file | `Data/CryptoQuant/BTC/Transactions/README.md` | 2026-04-17 03:17:34 UTC |
| dir | `Data/CryptoQuant/ETH` | 2026-04-12 05:50:01 UTC |
| dir | `Data/CryptoQuant/ETH/Addresses` | 2026-04-12 06:08:59 UTC |
| file | `Data/CryptoQuant/ETH/Addresses/Ethereum Active Addresses - Day.csv` | 2026-04-12 05:50:01 UTC |
| file | `Data/CryptoQuant/ETH/Addresses/Ethereum Active Addresses - Internal, External, EOA - Day.csv` | 2026-04-12 05:50:01 UTC |
| file | `Data/CryptoQuant/ETH/Addresses/Ethereum Active Receiving Addresses - Day.csv` | 2026-04-12 05:50:01 UTC |
| file | `Data/CryptoQuant/ETH/Addresses/Ethereum Active Receiving Addresses - Internal, External, EOA - Day.csv` | 2026-04-12 05:50:01 UTC |
| file | `Data/CryptoQuant/ETH/Addresses/Ethereum Active Sending Addresses - Day.csv` | 2026-04-12 05:50:01 UTC |
| file | `Data/CryptoQuant/ETH/Addresses/Ethereum Active Sending Addresses - Internal, External, EOA - Day.csv` | 2026-04-12 05:50:01 UTC |
| file | `Data/CryptoQuant/ETH/Addresses/README.md` | 2026-04-17 03:17:34 UTC |
| dir | `Data/CryptoQuant/ETH/Derivatives` | 2026-04-12 06:08:59 UTC |
| file | `Data/CryptoQuant/ETH/Derivatives/Ethereum Estimated Leverage Ratio - All Exchanges - Day.csv` | 2026-04-12 05:50:01 UTC |
| file | `Data/CryptoQuant/ETH/Derivatives/Ethereum Funding Rates - All Exchanges - Day.csv` | 2026-04-12 05:50:01 UTC |
| file | `Data/CryptoQuant/ETH/Derivatives/Ethereum Futures Taker CVD(Cumulative Volume Delta, 90-day) - Day.csv` | 2026-04-12 05:50:01 UTC |
| file | `Data/CryptoQuant/ETH/Derivatives/Ethereum Long Liquidations - All Exchanges, All Symbol - Day.csv` | 2026-04-12 05:50:01 UTC |
| file | `Data/CryptoQuant/ETH/Derivatives/Ethereum Long Liquidations USD - All Exchanges, All Symbol - Day.csv` | 2026-04-12 05:50:01 UTC |
| file | `Data/CryptoQuant/ETH/Derivatives/Ethereum Open Interest - All Exchanges, All Symbol - Day.csv` | 2026-04-12 05:50:01 UTC |
| file | `Data/CryptoQuant/ETH/Derivatives/Ethereum Short Liquidations - All Exchanges, All Symbol - Day.csv` | 2026-04-12 05:50:01 UTC |
| file | `Data/CryptoQuant/ETH/Derivatives/Ethereum Short Liquidations USD - All Exchanges, All Symbol - Day.csv` | 2026-04-12 05:50:02 UTC |
| file | `Data/CryptoQuant/ETH/Derivatives/README.md` | 2026-04-17 03:17:34 UTC |
| dir | `Data/CryptoQuant/ETH/ETH 2.0` | 2026-04-12 06:08:59 UTC |
| file | `Data/CryptoQuant/ETH/ETH 2.0/Ethereum Cumulative TXs to ETH 2.0 Contract - Day.csv` | 2026-04-12 05:50:01 UTC |
| file | `Data/CryptoQuant/ETH/ETH 2.0/Ethereum ETH 2.0 Staking Rate (%) - Day.csv` | 2026-04-12 05:50:01 UTC |
| file | `Data/CryptoQuant/ETH/ETH 2.0/Ethereum New Depositors - Day.csv` | 2026-04-12 05:50:01 UTC |
| file | `Data/CryptoQuant/ETH/ETH 2.0/Ethereum Number of ETH 2.0 Deposits - Day.csv` | 2026-04-12 05:50:01 UTC |
| file | `Data/CryptoQuant/ETH/ETH 2.0/Ethereum Number of Unique Depositors - Day.csv` | 2026-04-12 05:50:01 UTC |
| file | `Data/CryptoQuant/ETH/ETH 2.0/Ethereum Phase 0 Success Rate (%) - Day.csv` | 2026-04-12 05:50:01 UTC |
| file | `Data/CryptoQuant/ETH/ETH 2.0/Ethereum Staking Inflow Total - Day.csv` | 2026-04-12 05:50:02 UTC |
| file | `Data/CryptoQuant/ETH/ETH 2.0/Ethereum Total Value Staked - Day.csv` | 2026-04-12 05:50:02 UTC |
| file | `Data/CryptoQuant/ETH/ETH 2.0/README.md` | 2026-04-17 03:17:34 UTC |
| file | `Data/CryptoQuant/ETH/ETH_Metrics.txt` | 2026-04-12 06:09:00 UTC |
| dir | `Data/CryptoQuant/ETH/Exchange Flows` | 2026-04-12 06:08:59 UTC |
| file | `Data/CryptoQuant/ETH/Exchange Flows/Ethereum Exchange Depositing Addresses - All Exchanges - Day.csv` | 2026-04-12 05:50:01 UTC |
| file | `Data/CryptoQuant/ETH/Exchange Flows/Ethereum Exchange Depositing Transactions - All Exchanges - Day.csv` | 2026-04-12 05:50:01 UTC |
| file | `Data/CryptoQuant/ETH/Exchange Flows/Ethereum Exchange Inflow (Mean) - All Exchanges - Day.csv` | 2026-04-12 05:50:01 UTC |
| file | `Data/CryptoQuant/ETH/Exchange Flows/Ethereum Exchange Inflow (Top10) - All Exchanges - Day.csv` | 2026-04-12 05:50:01 UTC |
| file | `Data/CryptoQuant/ETH/Exchange Flows/Ethereum Exchange Inflow (Total) - All Exchanges - Day.csv` | 2026-04-12 05:50:01 UTC |
| file | `Data/CryptoQuant/ETH/Exchange Flows/Ethereum Exchange Netflow (Total) - All Exchanges - Day.csv` | 2026-04-12 05:50:01 UTC |
| file | `Data/CryptoQuant/ETH/Exchange Flows/Ethereum Exchange Outflow (Mean) - All Exchanges - Day.csv` | 2026-04-12 05:50:01 UTC |
| file | `Data/CryptoQuant/ETH/Exchange Flows/Ethereum Exchange Outflow (Top10) - All Exchanges - Day.csv` | 2026-04-12 05:50:01 UTC |
| file | `Data/CryptoQuant/ETH/Exchange Flows/Ethereum Exchange Outflow (Total) - All Exchanges - Day.csv` | 2026-04-12 05:50:01 UTC |
| file | `Data/CryptoQuant/ETH/Exchange Flows/Ethereum Exchange Reserve - All Exchanges - Day.csv` | 2026-04-12 05:50:01 UTC |
| file | `Data/CryptoQuant/ETH/Exchange Flows/Ethereum Exchange Reserve USD - All Exchanges - Day.csv` | 2026-04-12 05:50:01 UTC |
| file | `Data/CryptoQuant/ETH/Exchange Flows/Ethereum Exchange Withdrawing Addresses - All Exchanges - Day.csv` | 2026-04-12 05:50:01 UTC |
| file | `Data/CryptoQuant/ETH/Exchange Flows/Ethereum Exchange Withdrawing Transactions - All Exchanges - Day.csv` | 2026-04-12 05:50:01 UTC |
| file | `Data/CryptoQuant/ETH/Exchange Flows/README.md` | 2026-04-17 03:17:34 UTC |
| dir | `Data/CryptoQuant/ETH/Fees And Revenue` | 2026-04-12 06:08:59 UTC |
| file | `Data/CryptoQuant/ETH/Fees And Revenue/Ethereum Fees (Total) - Day.csv` | 2026-04-12 05:50:01 UTC |
| file | `Data/CryptoQuant/ETH/Fees And Revenue/Ethereum Fees Burnt (Total) - Day.csv` | 2026-04-12 05:50:01 UTC |
| file | `Data/CryptoQuant/ETH/Fees And Revenue/Ethereum Fees Burnt per Transaction (Mean) - Day.csv` | 2026-04-12 05:50:01 UTC |
| file | `Data/CryptoQuant/ETH/Fees And Revenue/Ethereum Fees Burnt per Transaction (Median) - Day.csv` | 2026-04-12 05:50:01 UTC |
| file | `Data/CryptoQuant/ETH/Fees And Revenue/Ethereum Fees Burnt per Transaction USD (Mean) - Day.csv` | 2026-04-12 05:50:01 UTC |
| file | `Data/CryptoQuant/ETH/Fees And Revenue/Ethereum Fees Burnt per Transaction USD (Median) - Day.csv` | 2026-04-12 05:50:01 UTC |
| file | `Data/CryptoQuant/ETH/Fees And Revenue/Ethereum Fees Burnt USD (Total) - Day.csv` | 2026-04-12 05:50:01 UTC |
| file | `Data/CryptoQuant/ETH/Fees And Revenue/Ethereum Fees per Transaction (Mean) - Day.csv` | 2026-04-12 05:50:01 UTC |
| file | `Data/CryptoQuant/ETH/Fees And Revenue/Ethereum Fees per Transaction USD (Mean) - Day.csv` | 2026-04-12 05:50:01 UTC |
| file | `Data/CryptoQuant/ETH/Fees And Revenue/README.md` | 2026-04-17 03:17:34 UTC |
| dir | `Data/CryptoQuant/ETH/Flow Indicator` | 2026-04-12 06:08:59 UTC |
| file | `Data/CryptoQuant/ETH/Flow Indicator/Ethereum Exchange Supply Ratio - All Exchanges - Day.csv` | 2026-04-12 05:50:01 UTC |
| file | `Data/CryptoQuant/ETH/Flow Indicator/README.md` | 2026-04-17 03:17:34 UTC |
| dir | `Data/CryptoQuant/ETH/Fund Data` | 2026-04-12 06:08:59 UTC |
| file | `Data/CryptoQuant/ETH/Fund Data/Ethereum Coinbase Premium Gap - Day.csv` | 2026-04-12 05:50:01 UTC |
| file | `Data/CryptoQuant/ETH/Fund Data/Ethereum Coinbase Premium Index - Day.csv` | 2026-04-12 05:50:01 UTC |
| file | `Data/CryptoQuant/ETH/Fund Data/Ethereum Fund Holdings - All Symbol - Day.csv` | 2026-04-12 05:50:01 UTC |
| file | `Data/CryptoQuant/ETH/Fund Data/Ethereum Fund Market Premium - All Symbol - Day.csv` | 2026-04-12 05:50:01 UTC |
| file | `Data/CryptoQuant/ETH/Fund Data/Ethereum Fund Price (USD) - ETHE - Day.csv` | 2026-04-12 05:50:01 UTC |
| file | `Data/CryptoQuant/ETH/Fund Data/Ethereum Fund Volume - All Symbol - Day.csv` | 2026-04-12 05:50:01 UTC |
| file | `Data/CryptoQuant/ETH/Fund Data/Ethereum Korea Premium Index - Day.csv` | 2026-04-12 05:50:01 UTC |
| file | `Data/CryptoQuant/ETH/Fund Data/README.md` | 2026-04-17 03:17:34 UTC |
| dir | `Data/CryptoQuant/ETH/Market Data` | 2026-04-12 06:08:59 UTC |
| file | `Data/CryptoQuant/ETH/Market Data/Ethereum Market Cap - Day.csv` | 2026-04-12 05:50:01 UTC |
| file | `Data/CryptoQuant/ETH/Market Data/Ethereum Price & Volume - Spot, All Exchanges, ETH-USD - Day.csv` | 2026-04-12 05:50:01 UTC |
| file | `Data/CryptoQuant/ETH/Market Data/Ethereum Price & Volume KRW - Spot - Day.csv` | 2026-04-12 05:50:01 UTC |
| file | `Data/CryptoQuant/ETH/Market Data/Ethereum Taker Buy Ratio - All Exchanges - Day.csv` | 2026-04-12 05:50:02 UTC |
| file | `Data/CryptoQuant/ETH/Market Data/Ethereum Taker Buy Sell Ratio - All Exchanges - Day.csv` | 2026-04-12 05:50:02 UTC |
| file | `Data/CryptoQuant/ETH/Market Data/Ethereum Taker Buy Volume - All Exchanges - Day.csv` | 2026-04-12 05:50:02 UTC |
| file | `Data/CryptoQuant/ETH/Market Data/Ethereum Taker Sell Ratio - All Exchanges - Day.csv` | 2026-04-12 05:50:02 UTC |
| file | `Data/CryptoQuant/ETH/Market Data/Ethereum Taker Sell Volume - All Exchanges - Day.csv` | 2026-04-12 05:50:02 UTC |
| file | `Data/CryptoQuant/ETH/Market Data/README.md` | 2026-04-17 03:17:34 UTC |
| dir | `Data/CryptoQuant/ETH/Network Stats` | 2026-04-12 06:08:59 UTC |
| file | `Data/CryptoQuant/ETH/Network Stats/Ethereum Destroyed Contracts - Day.csv` | 2026-04-12 05:50:01 UTC |
| file | `Data/CryptoQuant/ETH/Network Stats/Ethereum New Contracts - Day.csv` | 2026-04-12 05:50:01 UTC |
| file | `Data/CryptoQuant/ETH/Network Stats/Ethereum Number of Contracts - Day.csv` | 2026-04-12 05:50:01 UTC |
| file | `Data/CryptoQuant/ETH/Network Stats/README.md` | 2026-04-17 03:17:34 UTC |
| dir | `Data/CryptoQuant/ETH/Transactions` | 2026-04-12 06:08:59 UTC |
| file | `Data/CryptoQuant/ETH/Transactions/Ethereum Contract Calls (Mean) - Day.csv` | 2026-04-12 05:50:01 UTC |
| file | `Data/CryptoQuant/ETH/Transactions/Ethereum Contract Calls (Total) - Day.csv` | 2026-04-12 05:50:01 UTC |
| file | `Data/CryptoQuant/ETH/Transactions/Ethereum External Contract Calls (Mean) - Day.csv` | 2026-04-12 05:50:01 UTC |
| file | `Data/CryptoQuant/ETH/Transactions/Ethereum External Contract Calls (Total) - Day.csv` | 2026-04-12 05:50:01 UTC |
| file | `Data/CryptoQuant/ETH/Transactions/Ethereum Tokens Transferred (Mean) - Day.csv` | 2026-04-12 05:50:02 UTC |
| file | `Data/CryptoQuant/ETH/Transactions/Ethereum Tokens Transferred (Median) - Day.csv` | 2026-04-12 05:50:02 UTC |
| file | `Data/CryptoQuant/ETH/Transactions/Ethereum Tokens Transferred (Total) - Day.csv` | 2026-04-12 05:50:02 UTC |
| file | `Data/CryptoQuant/ETH/Transactions/Ethereum Tokens Transferred - Internal, External, EOA (Mean) - Day.csv` | 2026-04-12 05:50:02 UTC |
| file | `Data/CryptoQuant/ETH/Transactions/Ethereum Tokens Transferred - Internal, External, EOA (Median) - Day.csv` | 2026-04-12 05:50:02 UTC |
| file | `Data/CryptoQuant/ETH/Transactions/Ethereum Tokens Transferred - Internal, External, EOA (Total) - Day.csv` | 2026-04-12 05:50:02 UTC |
| file | `Data/CryptoQuant/ETH/Transactions/Ethereum Tokens Transferred Between EOA (Mean) - Day.csv` | 2026-04-12 05:50:02 UTC |
| file | `Data/CryptoQuant/ETH/Transactions/Ethereum Tokens Transferred Between EOA (Total) - Day.csv` | 2026-04-12 05:50:02 UTC |
| file | `Data/CryptoQuant/ETH/Transactions/Ethereum Tokens Transferred Between EOA USD (Mean) - Day.csv` | 2026-04-12 05:50:02 UTC |
| file | `Data/CryptoQuant/ETH/Transactions/Ethereum Tokens Transferred Between EOA USD (Median) - Day.csv` | 2026-04-12 05:50:02 UTC |
| file | `Data/CryptoQuant/ETH/Transactions/Ethereum Tokens Transferred Between EOA USD (Total) - Day.csv` | 2026-04-12 05:50:02 UTC |
| file | `Data/CryptoQuant/ETH/Transactions/Ethereum Tokens Transferred by Contract Calls (Mean) - Day.csv` | 2026-04-12 05:50:02 UTC |
| file | `Data/CryptoQuant/ETH/Transactions/Ethereum Tokens Transferred by Contract Calls (Median) - Day.csv` | 2026-04-12 05:50:02 UTC |
| file | `Data/CryptoQuant/ETH/Transactions/Ethereum Tokens Transferred by Contract Calls (Total) - Day.csv` | 2026-04-12 05:50:02 UTC |
| file | `Data/CryptoQuant/ETH/Transactions/Ethereum Tokens Transferred by Contract Calls USD (Mean) - Day.csv` | 2026-04-12 05:50:02 UTC |
| file | `Data/CryptoQuant/ETH/Transactions/Ethereum Tokens Transferred by Contract Calls USD (Median) - Day.csv` | 2026-04-12 05:50:02 UTC |
| file | `Data/CryptoQuant/ETH/Transactions/Ethereum Tokens Transferred by Contract Calls USD (Total) - Day.csv` | 2026-04-12 05:50:02 UTC |
| file | `Data/CryptoQuant/ETH/Transactions/Ethereum Tokens Transferred by External Contract Calls (Mean) - Day.csv` | 2026-04-12 05:50:02 UTC |
| file | `Data/CryptoQuant/ETH/Transactions/Ethereum Tokens Transferred by External Contract Calls (Median) - Day.csv` | 2026-04-12 05:50:02 UTC |
| file | `Data/CryptoQuant/ETH/Transactions/Ethereum Tokens Transferred by External Contract Calls (Total) - Day.csv` | 2026-04-12 05:50:02 UTC |
| file | `Data/CryptoQuant/ETH/Transactions/Ethereum Tokens Transferred by External Contract Calls USD (Mean) - Day.csv` | 2026-04-12 05:50:02 UTC |
| file | `Data/CryptoQuant/ETH/Transactions/Ethereum Tokens Transferred by External Contract Calls USD (Median) - Day.csv` | 2026-04-12 05:50:02 UTC |
| file | `Data/CryptoQuant/ETH/Transactions/Ethereum Tokens Transferred by External Contract Calls USD (Total) - Day.csv` | 2026-04-12 05:50:02 UTC |
| file | `Data/CryptoQuant/ETH/Transactions/Ethereum Tokens Transferred USD (Mean) - Day.csv` | 2026-04-12 05:50:02 UTC |
| file | `Data/CryptoQuant/ETH/Transactions/Ethereum Tokens Transferred USD (Median) - Day.csv` | 2026-04-12 05:50:02 UTC |
| file | `Data/CryptoQuant/ETH/Transactions/Ethereum Tokens Transferred USD (Total) - Day.csv` | 2026-04-12 05:50:02 UTC |
| file | `Data/CryptoQuant/ETH/Transactions/Ethereum Tokens Transferred USD - Internal, External, EOA (Mean) - Day.csv` | 2026-04-12 05:50:02 UTC |
| file | `Data/CryptoQuant/ETH/Transactions/Ethereum Tokens Transferred USD - Internal, External, EOA (Median) - Day.csv` | 2026-04-12 05:50:02 UTC |
| file | `Data/CryptoQuant/ETH/Transactions/Ethereum Tokens Transferred USD - Internal, External, EOA (Total) - Day.csv` | 2026-04-12 05:50:02 UTC |
| file | `Data/CryptoQuant/ETH/Transactions/Ethereum Transaction Count (Mean) - Day.csv` | 2026-04-12 05:50:02 UTC |
| file | `Data/CryptoQuant/ETH/Transactions/Ethereum Transaction Count (Total) - Day.csv` | 2026-04-12 05:50:02 UTC |
| file | `Data/CryptoQuant/ETH/Transactions/Ethereum Transaction Count - Internal, External, EOA (Total) - Day.csv` | 2026-04-12 05:50:02 UTC |
| file | `Data/CryptoQuant/ETH/Transactions/Ethereum Transactions Between EOA (Mean) - Day.csv` | 2026-04-12 05:50:02 UTC |
| file | `Data/CryptoQuant/ETH/Transactions/Ethereum Transactions Between EOA (Total) - Day.csv` | 2026-04-12 05:50:02 UTC |
| file | `Data/CryptoQuant/ETH/Transactions/Ethereum Transfer Count - Internal, External, EOA (Mean) - Day.csv` | 2026-04-12 05:50:02 UTC |
| file | `Data/CryptoQuant/ETH/Transactions/Ethereum Transfer Count - Internal, External, EOA (Total) - Day.csv` | 2026-04-12 05:50:02 UTC |
| file | `Data/CryptoQuant/ETH/Transactions/Ethereum Transfers Between EOA (Mean) - Day.csv` | 2026-04-12 05:50:02 UTC |
| file | `Data/CryptoQuant/ETH/Transactions/Ethereum Transfers Between EOA (Total) - Day.csv` | 2026-04-12 05:50:02 UTC |
| file | `Data/CryptoQuant/ETH/Transactions/Ethereum Transfers by Contract Calls (Mean) - Day.csv` | 2026-04-12 05:50:02 UTC |
| file | `Data/CryptoQuant/ETH/Transactions/Ethereum Transfers by External Contract Calls (Mean) - Day.csv` | 2026-04-12 05:50:02 UTC |
| file | `Data/CryptoQuant/ETH/Transactions/Ethereum Transfers by External Contract Calls (Total) - Day.csv` | 2026-04-12 05:50:02 UTC |
| file | `Data/CryptoQuant/ETH/Transactions/README.md` | 2026-04-17 03:17:34 UTC |
| dir | `Data/CryptoQuant/USDC` | 2026-04-12 05:50:02 UTC |
| dir | `Data/CryptoQuant/USDC/Addresses` | 2026-04-12 06:09:00 UTC |
| file | `Data/CryptoQuant/USDC/Addresses/README.md` | 2026-04-17 03:17:34 UTC |
| file | `Data/CryptoQuant/USDC/Addresses/USD Coin(ERC20) Active Addresses - Day.csv` | 2026-04-12 05:50:02 UTC |
| file | `Data/CryptoQuant/USDC/Addresses/USD Coin(ERC20) Active Receiving Addresses (%) - Day.csv` | 2026-04-12 05:50:02 UTC |
| file | `Data/CryptoQuant/USDC/Addresses/USD Coin(ERC20) Active Receiving Addresses - Day.csv` | 2026-04-12 05:50:02 UTC |
| file | `Data/CryptoQuant/USDC/Addresses/USD Coin(ERC20) Active Sending Addresses (%) - Day.csv` | 2026-04-12 05:50:02 UTC |
| file | `Data/CryptoQuant/USDC/Addresses/USD Coin(ERC20) Active Sending Addresses - Day.csv` | 2026-04-12 05:50:02 UTC |
| dir | `Data/CryptoQuant/USDC/Exchange Flows` | 2026-04-12 06:09:00 UTC |
| file | `Data/CryptoQuant/USDC/Exchange Flows/README.md` | 2026-04-17 03:17:34 UTC |
| file | `Data/CryptoQuant/USDC/Exchange Flows/USD Coin(ERC20) Exchange Depositing Addresses - All Exchanges - Day.csv` | 2026-04-12 05:50:02 UTC |
| file | `Data/CryptoQuant/USDC/Exchange Flows/USD Coin(ERC20) Exchange Depositing Transactions - All Exchanges - Day.csv` | 2026-04-12 05:50:02 UTC |
| file | `Data/CryptoQuant/USDC/Exchange Flows/USD Coin(ERC20) Exchange Inflow (Mean) - All Exchanges - Day.csv` | 2026-04-12 05:50:02 UTC |
| file | `Data/CryptoQuant/USDC/Exchange Flows/USD Coin(ERC20) Exchange Inflow (Top10) - All Exchanges - Day.csv` | 2026-04-12 05:50:02 UTC |
| file | `Data/CryptoQuant/USDC/Exchange Flows/USD Coin(ERC20) Exchange Inflow (Total) - All Exchanges - Day.csv` | 2026-04-12 05:50:02 UTC |
| file | `Data/CryptoQuant/USDC/Exchange Flows/USD Coin(ERC20) Exchange Netflow (Total) - All Exchanges - Day.csv` | 2026-04-12 05:50:02 UTC |
| file | `Data/CryptoQuant/USDC/Exchange Flows/USD Coin(ERC20) Exchange Outflow (Mean) - All Exchanges - Day.csv` | 2026-04-12 05:50:02 UTC |
| file | `Data/CryptoQuant/USDC/Exchange Flows/USD Coin(ERC20) Exchange Outflow (Top10) - All Exchanges - Day.csv` | 2026-04-12 05:50:02 UTC |
| file | `Data/CryptoQuant/USDC/Exchange Flows/USD Coin(ERC20) Exchange Outflow (Total) - All Exchanges - Day.csv` | 2026-04-12 05:50:02 UTC |
| file | `Data/CryptoQuant/USDC/Exchange Flows/USD Coin(ERC20) Exchange Reserve - All Exchanges - Day.csv` | 2026-04-12 05:50:02 UTC |
| file | `Data/CryptoQuant/USDC/Exchange Flows/USD Coin(ERC20) Exchange Withdrawing Addresses - All Exchanges - Day.csv` | 2026-04-12 05:50:02 UTC |
| file | `Data/CryptoQuant/USDC/Exchange Flows/USD Coin(ERC20) Exchange Withdrawing Transactions - All Exchanges - Day.csv` | 2026-04-12 05:50:02 UTC |
| dir | `Data/CryptoQuant/USDC/Flow Indicator` | 2026-04-12 06:09:00 UTC |
| file | `Data/CryptoQuant/USDC/Flow Indicator/README.md` | 2026-04-17 03:17:34 UTC |
| file | `Data/CryptoQuant/USDC/Flow Indicator/USD Coin(ERC20) Exchange Supply Ratio - All Exchanges - Day.csv` | 2026-04-12 05:50:02 UTC |
| dir | `Data/CryptoQuant/USDC/Transactions` | 2026-04-12 06:09:00 UTC |
| file | `Data/CryptoQuant/USDC/Transactions/README.md` | 2026-04-17 03:17:34 UTC |
| file | `Data/CryptoQuant/USDC/Transactions/USD Coin(ERC20) Tokens Transferred (Mean) - Day.csv` | 2026-04-12 05:50:02 UTC |
| file | `Data/CryptoQuant/USDC/Transactions/USD Coin(ERC20) Tokens Transferred (Total) - Day.csv` | 2026-04-12 05:50:02 UTC |
| file | `Data/CryptoQuant/USDC/Transactions/USD Coin(ERC20) Transfer Event Count - Day.csv` | 2026-04-12 05:50:02 UTC |
| file | `Data/CryptoQuant/USDC/USDC_Metrics.txt` | 2026-04-12 06:09:00 UTC |
| dir | `Data/CryptoQuant/USDT (TRX)` | 2026-04-12 05:50:02 UTC |
| dir | `Data/CryptoQuant/USDT (TRX)/Addresses` | 2026-04-12 06:09:00 UTC |
| file | `Data/CryptoQuant/USDT (TRX)/Addresses/README.md` | 2026-04-17 03:17:34 UTC |
| file | `Data/CryptoQuant/USDT (TRX)/Addresses/Tether USD(TRC20) Active Addresses - Day.csv` | 2026-04-12 05:50:02 UTC |
| file | `Data/CryptoQuant/USDT (TRX)/Addresses/Tether USD(TRC20) Active Receiving Addresses (%) - Day.csv` | 2026-04-12 05:50:02 UTC |
| file | `Data/CryptoQuant/USDT (TRX)/Addresses/Tether USD(TRC20) Active Receiving Addresses - Day.csv` | 2026-04-12 05:50:02 UTC |
| file | `Data/CryptoQuant/USDT (TRX)/Addresses/Tether USD(TRC20) Active Sending Addresses (%) - Day.csv` | 2026-04-12 05:50:02 UTC |
| file | `Data/CryptoQuant/USDT (TRX)/Addresses/Tether USD(TRC20) Active Sending Addresses - Day.csv` | 2026-04-12 05:50:02 UTC |
| dir | `Data/CryptoQuant/USDT (TRX)/Exchange Flows` | 2026-04-12 06:09:00 UTC |
| file | `Data/CryptoQuant/USDT (TRX)/Exchange Flows/README.md` | 2026-04-17 03:17:34 UTC |
| file | `Data/CryptoQuant/USDT (TRX)/Exchange Flows/Tether USD(TRC20) Exchange Depositing Transactions - All Exchanges - Day.csv` | 2026-04-12 05:50:02 UTC |
| file | `Data/CryptoQuant/USDT (TRX)/Exchange Flows/Tether USD(TRC20) Exchange Inflow (Mean) - All Exchanges - Day.csv` | 2026-04-12 05:50:02 UTC |
| file | `Data/CryptoQuant/USDT (TRX)/Exchange Flows/Tether USD(TRC20) Exchange Inflow (Top10) - All Exchanges - Day.csv` | 2026-04-12 05:50:02 UTC |
| file | `Data/CryptoQuant/USDT (TRX)/Exchange Flows/Tether USD(TRC20) Exchange Inflow (Total) - All Exchanges - Day.csv` | 2026-04-12 05:50:02 UTC |
| file | `Data/CryptoQuant/USDT (TRX)/Exchange Flows/Tether USD(TRC20) Exchange Netflow (Total) - All Exchanges - Day.csv` | 2026-04-12 05:50:02 UTC |
| file | `Data/CryptoQuant/USDT (TRX)/Exchange Flows/Tether USD(TRC20) Exchange Outflow (Mean) - All Exchanges - Day.csv` | 2026-04-12 05:50:02 UTC |
| file | `Data/CryptoQuant/USDT (TRX)/Exchange Flows/Tether USD(TRC20) Exchange Outflow (Top10) - All Exchanges - Day.csv` | 2026-04-12 05:50:02 UTC |
| file | `Data/CryptoQuant/USDT (TRX)/Exchange Flows/Tether USD(TRC20) Exchange Reserve - All Exchanges - Day.csv` | 2026-04-12 05:50:02 UTC |
| file | `Data/CryptoQuant/USDT (TRX)/Exchange Flows/Tether USD(TRC20) Exchange Withdrawing Transactions - All Exchanges - Day.csv` | 2026-04-12 05:50:03 UTC |
| file | `Data/CryptoQuant/USDT (TRX)/USDT_TRX_Metrics.txt` | 2026-04-12 06:09:00 UTC |
| dir | `Data/CryptoQuant/USDT ETH` | 2026-04-12 05:50:03 UTC |
| dir | `Data/CryptoQuant/USDT ETH/Addresses` | 2026-04-12 06:09:00 UTC |
| file | `Data/CryptoQuant/USDT ETH/Addresses/README.md` | 2026-04-17 03:17:34 UTC |
| file | `Data/CryptoQuant/USDT ETH/Addresses/Tether USD(ERC20) Active Addresses - Day.csv` | 2026-04-12 05:50:03 UTC |
| file | `Data/CryptoQuant/USDT ETH/Addresses/Tether USD(ERC20) Active Receiving Addresses (%) - Day.csv` | 2026-04-12 05:50:03 UTC |
| file | `Data/CryptoQuant/USDT ETH/Addresses/Tether USD(ERC20) Active Receiving Addresses - Day.csv` | 2026-04-12 05:50:03 UTC |
| file | `Data/CryptoQuant/USDT ETH/Addresses/Tether USD(ERC20) Active Sending Addresses (%) - Day.csv` | 2026-04-12 05:50:03 UTC |
| file | `Data/CryptoQuant/USDT ETH/Addresses/Tether USD(ERC20) Active Sending Addresses - Day.csv` | 2026-04-12 05:50:03 UTC |
| dir | `Data/CryptoQuant/USDT ETH/Exchange Flows` | 2026-04-12 06:09:00 UTC |
| file | `Data/CryptoQuant/USDT ETH/Exchange Flows/README.md` | 2026-04-17 03:17:34 UTC |
| file | `Data/CryptoQuant/USDT ETH/Exchange Flows/Tether USD(ERC20) Exchange Depositing Addresses - All Exchanges - Day.csv` | 2026-04-12 05:50:03 UTC |
| file | `Data/CryptoQuant/USDT ETH/Exchange Flows/Tether USD(ERC20) Exchange Depositing Transactions - All Exchanges - Day.csv` | 2026-04-12 05:50:03 UTC |
| file | `Data/CryptoQuant/USDT ETH/Exchange Flows/Tether USD(ERC20) Exchange Inflow (Mean) - All Exchanges - Day.csv` | 2026-04-12 05:50:03 UTC |
| file | `Data/CryptoQuant/USDT ETH/Exchange Flows/Tether USD(ERC20) Exchange Inflow (Top10) - All Exchanges - Day.csv` | 2026-04-12 05:50:03 UTC |
| file | `Data/CryptoQuant/USDT ETH/Exchange Flows/Tether USD(ERC20) Exchange Inflow (Total) - All Exchanges - Day.csv` | 2026-04-12 05:50:03 UTC |
| file | `Data/CryptoQuant/USDT ETH/Exchange Flows/Tether USD(ERC20) Exchange Netflow (Total) - All Exchanges - Day.csv` | 2026-04-12 05:50:03 UTC |
| file | `Data/CryptoQuant/USDT ETH/Exchange Flows/Tether USD(ERC20) Exchange Outflow (Mean) - All Exchanges - Day.csv` | 2026-04-12 05:50:03 UTC |
| file | `Data/CryptoQuant/USDT ETH/Exchange Flows/Tether USD(ERC20) Exchange Outflow (Top10) - All Exchanges - Day.csv` | 2026-04-12 05:50:03 UTC |
| file | `Data/CryptoQuant/USDT ETH/Exchange Flows/Tether USD(ERC20) Exchange Outflow (Total) - All Exchanges - Day.csv` | 2026-04-12 05:50:03 UTC |
| file | `Data/CryptoQuant/USDT ETH/Exchange Flows/Tether USD(ERC20) Exchange Reserve - All Exchanges - Day.csv` | 2026-04-12 05:50:03 UTC |
| file | `Data/CryptoQuant/USDT ETH/Exchange Flows/Tether USD(ERC20) Exchange Withdrawing Addresses - All Exchanges - Day.csv` | 2026-04-12 05:50:03 UTC |
| file | `Data/CryptoQuant/USDT ETH/Exchange Flows/Tether USD(ERC20) Exchange Withdrawing Transactions - All Exchanges - Day.csv` | 2026-04-12 05:50:03 UTC |
| dir | `Data/CryptoQuant/USDT ETH/Flow Indicator` | 2026-04-12 06:09:00 UTC |
| file | `Data/CryptoQuant/USDT ETH/Flow Indicator/README.md` | 2026-04-17 03:17:34 UTC |
| file | `Data/CryptoQuant/USDT ETH/Flow Indicator/Tether USD(ERC20) Exchange Supply Ratio - All Exchanges - Day.csv` | 2026-04-12 05:50:03 UTC |
| dir | `Data/CryptoQuant/USDT ETH/Market Data` | 2026-04-12 06:09:00 UTC |
| file | `Data/CryptoQuant/USDT ETH/Market Data/README.md` | 2026-04-17 03:17:34 UTC |
| file | `Data/CryptoQuant/USDT ETH/Market Data/Tether USD(ERC20) Market Cap - Day.csv` | 2026-04-12 05:50:03 UTC |
| dir | `Data/CryptoQuant/USDT ETH/Supply` | 2026-04-12 06:09:00 UTC |
| file | `Data/CryptoQuant/USDT ETH/Supply/README.md` | 2026-04-17 03:17:34 UTC |
| file | `Data/CryptoQuant/USDT ETH/Supply/Tether USD(ERC20) Total Supply - Day.csv` | 2026-04-12 05:50:03 UTC |
| dir | `Data/CryptoQuant/USDT ETH/Transactions` | 2026-04-12 06:09:00 UTC |
| file | `Data/CryptoQuant/USDT ETH/Transactions/README.md` | 2026-04-17 03:17:34 UTC |
| file | `Data/CryptoQuant/USDT ETH/Transactions/Tether USD(ERC20) Tokens Transferred (Total) - Day.csv` | 2026-04-12 05:50:03 UTC |
| file | `Data/CryptoQuant/USDT ETH/Transactions/Tether USD(ERC20) Transfer Event Count - Day.csv` | 2026-04-12 05:50:03 UTC |
| file | `Data/CryptoQuant/USDT ETH/USDT_ETH_Metrics.txt` | 2026-04-12 06:09:00 UTC |
| dir | `Data/CryptoQuant/WBTC` | 2026-04-12 05:50:03 UTC |
| dir | `Data/CryptoQuant/WBTC/Addresses` | 2026-04-12 06:09:00 UTC |
| file | `Data/CryptoQuant/WBTC/Addresses/README.md` | 2026-04-17 03:17:34 UTC |
| file | `Data/CryptoQuant/WBTC/Addresses/Wrapped BTC Active Addresses - Day.csv` | 2026-04-12 05:50:03 UTC |
| file | `Data/CryptoQuant/WBTC/Addresses/Wrapped BTC Active Receiving Addresses - Day.csv` | 2026-04-12 05:50:03 UTC |
| file | `Data/CryptoQuant/WBTC/Addresses/Wrapped BTC Active Sending Addresses - Day.csv` | 2026-04-12 05:50:03 UTC |
| dir | `Data/CryptoQuant/WBTC/Transactions` | 2026-04-12 06:09:00 UTC |
| file | `Data/CryptoQuant/WBTC/Transactions/README.md` | 2026-04-17 03:17:34 UTC |
| file | `Data/CryptoQuant/WBTC/Transactions/Wrapped BTC Tokens Transferred (Mean) - Day.csv` | 2026-04-12 05:50:03 UTC |
| file | `Data/CryptoQuant/WBTC/Transactions/Wrapped BTC Tokens Transferred (Median) - Day.csv` | 2026-04-12 05:50:03 UTC |
| file | `Data/CryptoQuant/WBTC/Transactions/Wrapped BTC Tokens Transferred (Total) - Day.csv` | 2026-04-12 05:50:03 UTC |
| file | `Data/CryptoQuant/WBTC/Transactions/Wrapped BTC Transaction Count (Mean) - Day.csv` | 2026-04-12 05:50:03 UTC |
| file | `Data/CryptoQuant/WBTC/Transactions/Wrapped BTC Transaction Count (Total) - Day.csv` | 2026-04-12 05:50:03 UTC |
| file | `Data/CryptoQuant/WBTC/Transactions/Wrapped BTC Transfer Count (Total) - Day.csv` | 2026-04-12 05:50:03 UTC |
| file | `Data/CryptoQuant/WBTC/WBTC_Metrics.txt` | 2026-04-12 06:09:00 UTC |
| dir | `Data/DefiLlama` | 2026-04-12 05:50:35 UTC |
| dir | `Data/DefiLlama/_raw_parts` | 2026-04-17 03:28:02 UTC |
| dir | `Data/DefiLlama/_raw_parts/cex_inflows` | 2026-04-17 03:28:02 UTC |
| file | `Data/DefiLlama/_raw_parts/cex_inflows/cex-inflows-chart_combined_2026-04-17 part 1.csv` | 2026-04-17 02:21:52 UTC |
| file | `Data/DefiLlama/_raw_parts/cex_inflows/cex-inflows-chart_combined_2026-04-17 part 2.csv` | 2026-04-17 02:22:34 UTC |
| file | `Data/DefiLlama/_raw_parts/cex_inflows/cex-inflows-chart_combined_2026-04-17 part 3.csv` | 2026-04-17 02:26:03 UTC |
| dir | `Data/DefiLlama/_raw_parts/duplicates` | 2026-04-17 22:31:26 UTC |
| file | `Data/DefiLlama/_raw_parts/duplicates/all_metrics_2026-04-17 (1) volume.csv` | 2026-04-17 02:37:35 UTC |
| file | `Data/DefiLlama/_raw_parts/duplicates/ethereum_metrics_2026-04-17 (1).csv` | 2026-04-17 02:32:22 UTC |
| file | `Data/DefiLlama/_raw_parts/duplicates/ethereum_metrics_2026-04-17 Fees and revenue.csv` | 2026-04-17 02:36:39 UTC |
| file | `Data/DefiLlama/_raw_parts/duplicates/rwa-time-series-chart-active-mcap-all-2026-04-14.csv` | 2026-04-14 23:07:26 UTC |
| file | `Data/DefiLlama/_raw_parts/duplicates/rwa-time-series-chart-onchain-mcap-all-2026-04-14.csv` | 2026-04-14 23:11:41 UTC |
| file | `Data/DefiLlama/_raw_parts/README.md` | 2026-04-17 03:17:34 UTC |
| dir | `Data/DefiLlama/_raw_parts/stablecoin_mcap` | 2026-04-17 03:28:02 UTC |
| file | `Data/DefiLlama/_raw_parts/stablecoin_mcap/stablecoin-mcap-chart_combined_2026-04-17 (1) part 5.csv` | 2026-04-17 02:43:54 UTC |
| file | `Data/DefiLlama/_raw_parts/stablecoin_mcap/stablecoin-mcap-chart_combined_2026-04-17 (1) part 6.csv` | 2026-04-17 02:45:35 UTC |
| file | `Data/DefiLlama/_raw_parts/stablecoin_mcap/stablecoin-mcap-chart_combined_2026-04-17 (1) part 7.csv` | 2026-04-17 02:45:58 UTC |
| file | `Data/DefiLlama/_raw_parts/stablecoin_mcap/stablecoin-mcap-chart_combined_2026-04-17 part 1.csv` | 2026-04-17 02:42:17 UTC |
| file | `Data/DefiLlama/_raw_parts/stablecoin_mcap/stablecoin-mcap-chart_combined_2026-04-17 part 2.csv` | 2026-04-17 02:42:37 UTC |
| file | `Data/DefiLlama/_raw_parts/stablecoin_mcap/stablecoin-mcap-chart_combined_2026-04-17 part 3.csv` | 2026-04-17 02:42:56 UTC |
| file | `Data/DefiLlama/_raw_parts/stablecoin_mcap/stablecoin-mcap-chart_combined_2026-04-17 part 4.csv` | 2026-04-17 02:43:17 UTC |
| file | `Data/DefiLlama/_raw_parts/stablecoin_mcap/stablecoin-mcap-chart_combined_2026-04-17.csv` | 2026-04-17 02:43:35 UTC |
| dir | `Data/DefiLlama/CEX` | 2026-04-17 03:28:02 UTC |
| file | `Data/DefiLlama/CEX/cex_net_inflows_by_exchange__daily.csv` | 2026-04-17 03:11:28 UTC |
| file | `Data/DefiLlama/CEX/README.md` | 2026-04-17 03:30:18 UTC |
| dir | `Data/DefiLlama/ChainMetrics` | 2026-04-17 03:28:02 UTC |
| file | `Data/DefiLlama/ChainMetrics/all_chains_metrics__daily.csv` | 2026-04-17 02:31:04 UTC |
| file | `Data/DefiLlama/ChainMetrics/all_chains_perp_volume_by_protocol__daily.csv` | 2026-04-17 20:26:01 UTC |
| file | `Data/DefiLlama/ChainMetrics/all_dex_metrics__daily.csv` | 2026-04-17 20:23:09 UTC |
| file | `Data/DefiLlama/ChainMetrics/chain_revenue_combined__daily.csv` | 2026-04-17 20:45:28 UTC |
| file | `Data/DefiLlama/ChainMetrics/chain_tvl_dominance__daily.csv` | 2026-04-17 20:20:39 UTC |
| file | `Data/DefiLlama/ChainMetrics/ethereum_metrics__daily.csv` | 2026-04-17 02:37:14 UTC |
| file | `Data/DefiLlama/ChainMetrics/README.md` | 2026-04-17 03:30:18 UTC |
| file | `Data/DefiLlama/ChainMetrics/solana_metrics__daily.csv` | 2026-04-17 02:33:38 UTC |
| dir | `Data/DefiLlama/DATs` | 2026-04-17 03:28:02 UTC |
| file | `Data/DefiLlama/DATs/dat-institutions.csv` | 2026-04-14 23:35:09 UTC |
| file | `Data/DefiLlama/DATs/README.md` | 2026-04-17 03:30:18 UTC |
| dir | `Data/DefiLlama/ETFs` | 2026-04-17 03:28:02 UTC |
| file | `Data/DefiLlama/ETFs/etf-history.csv` | 2026-04-14 23:34:18 UTC |
| file | `Data/DefiLlama/ETFs/etf-overview.csv` | 2026-04-14 23:34:47 UTC |
| file | `Data/DefiLlama/ETFs/README.md` | 2026-04-17 03:30:18 UTC |
| dir | `Data/DefiLlama/RWA` | 2026-04-17 03:28:02 UTC |
| file | `Data/DefiLlama/RWA/README.md` | 2026-04-17 03:30:18 UTC |
| file | `Data/DefiLlama/RWA/rwa_active_mcap_all__daily.csv` | 2026-04-17 20:30:42 UTC |
| file | `Data/DefiLlama/RWA/rwa_defi_active_tvl_all__daily.csv` | 2026-04-14 23:11:39 UTC |
| file | `Data/DefiLlama/RWA/rwa_mcap_by_category__daily.csv` | 2026-04-17 02:47:44 UTC |
| file | `Data/DefiLlama/RWA/rwa_onchain_mcap_all__daily.csv` | 2026-04-17 20:32:28 UTC |
| file | `Data/DefiLlama/RWA/rwa_onchain_mcap_by_platform__daily.csv` | 2026-04-17 20:33:19 UTC |
| dir | `Data/DefiLlama/Stablecoins` | 2026-04-17 03:28:02 UTC |
| file | `Data/DefiLlama/Stablecoins/README.md` | 2026-04-17 03:30:18 UTC |
| file | `Data/DefiLlama/Stablecoins/stablecoin_mcap_by_defillama_id__daily.csv` | 2026-04-17 03:11:27 UTC |
| file | `Data/DefiLlama/Stablecoins/stablecoin_mcap_id_to_name.csv` | 2026-04-17 03:11:28 UTC |
| file | `Data/DefiLlama/Stablecoins/stablecoins-chains.csv` | 2026-04-17 02:19:50 UTC |
| file | `Data/DefiLlama/Stablecoins/stablecoins.csv` | 2026-04-17 02:19:26 UTC |
| dir | `Data/DefiLlama/TVL` | 2026-04-14 23:16:30 UTC |
| dir | `Data/DefiLlama/TVL/Daily` | 2026-04-14 23:16:30 UTC |
| file | `Data/DefiLlama/TVL/Daily/README.md` | 2026-04-17 03:17:34 UTC |
| file | `Data/DefiLlama/TVL/Daily/tvl_all_chains_daily.csv` | 2026-04-14 23:16:32 UTC |
| file | `Data/DefiLlama/TVL/Daily/tvl_by_chain_long_daily.csv` | 2026-04-14 23:17:32 UTC |
| file | `Data/DefiLlama/TVL/Daily/tvl_by_chain_wide_daily.csv` | 2026-04-14 23:17:37 UTC |
| dir | `Data/DefiLlama/TVL/Snapshot` | 2026-04-14 23:16:30 UTC |
| file | `Data/DefiLlama/TVL/Snapshot/README.md` | 2026-04-17 03:17:34 UTC |
| file | `Data/DefiLlama/TVL/Snapshot/tvl_chains_current.csv` | 2026-04-14 23:16:31 UTC |
| file | `Data/DefiLlama/TVL/Snapshot/tvl_protocols_current.csv` | 2026-04-14 23:16:32 UTC |
| dir | `Data/DefiLlama/TVL/Weekly` | 2026-04-14 23:16:30 UTC |
| file | `Data/DefiLlama/TVL/Weekly/README.md` | 2026-04-17 03:17:34 UTC |
| file | `Data/DefiLlama/TVL/Weekly/tvl_all_chains_weekly.csv` | 2026-04-14 23:16:32 UTC |
| file | `Data/DefiLlama/TVL/Weekly/tvl_by_chain_long_weekly.csv` | 2026-04-14 23:17:34 UTC |
| file | `Data/DefiLlama/TVL/Weekly/tvl_by_chain_wide_weekly.csv` | 2026-04-14 23:17:38 UTC |
| dir | `Data/Farside ETF Data` | 2026-04-12 06:10:39 UTC |
| file | `Data/Farside ETF Data/farside_btc_etf_flows__daily.csv` | 2026-04-17 22:31:32 UTC |
| file | `Data/Farside ETF Data/Farside_ETF_Data_Summary.txt` | 2026-04-12 06:19:50 UTC |
| file | `Data/Farside ETF Data/farside_eth_etf_flows__daily.csv` | 2026-04-17 22:31:32 UTC |
| file | `Data/Farside ETF Data/farside_sol_etf_flows__daily.csv` | 2026-04-17 22:31:32 UTC |
| file | `Data/Farside ETF Data/README.md` | 2026-04-17 22:31:32 UTC |
| dir | `Data/FRED` | 2026-04-17 22:29:45 UTC |
| file | `Data/FRED/_fetch_status.json` | 2026-04-17 22:30:01 UTC |
| file | `Data/FRED/ANFCI__weekly.csv` | 2026-04-17 22:29:55 UTC |
| file | `Data/FRED/BAMLH0A0HYM2__daily.csv` | 2026-04-17 22:29:53 UTC |
| file | `Data/FRED/CPIAUCSL__monthly.csv` | 2026-04-17 22:29:59 UTC |
| file | `Data/FRED/DCOILWTICO__daily.csv` | 2026-04-17 22:29:59 UTC |
| file | `Data/FRED/DFF__daily.csv` | 2026-04-17 22:29:52 UTC |
| file | `Data/FRED/DFII10__daily.csv` | 2026-04-17 22:29:50 UTC |
| file | `Data/FRED/DGS10__daily.csv` | 2026-04-17 22:29:47 UTC |
| file | `Data/FRED/DGS2__daily.csv` | 2026-04-17 22:29:48 UTC |
| file | `Data/FRED/DGS30__daily.csv` | 2026-04-17 22:29:49 UTC |
| file | `Data/FRED/DTWEXBGS__daily.csv` | 2026-04-17 22:29:58 UTC |
| file | `Data/FRED/fred_macro_panel__daily.csv` | 2026-04-17 22:30:01 UTC |
| file | `Data/FRED/fred_series_metadata.csv` | 2026-04-17 22:30:01 UTC |
| file | `Data/FRED/NFCI__weekly.csv` | 2026-04-17 22:29:55 UTC |
| file | `Data/FRED/README.md` | 2026-04-17 22:30:01 UTC |
| file | `Data/FRED/RRPONTSYD__daily.csv` | 2026-04-17 22:29:57 UTC |
| file | `Data/FRED/SOFR__daily.csv` | 2026-04-17 22:29:52 UTC |
| file | `Data/FRED/STLFSI4__weekly.csv` | 2026-04-17 22:29:56 UTC |
| file | `Data/FRED/T10Y2Y__daily.csv` | 2026-04-17 22:29:50 UTC |
| file | `Data/FRED/UNRATE__monthly.csv` | 2026-04-17 22:30:00 UTC |
| file | `Data/FRED/USEPUINDXD__daily.csv` | 2026-04-17 22:30:01 UTC |
| file | `Data/FRED/VIXCLS__daily.csv` | 2026-04-17 22:29:53 UTC |
| file | `Data/FRED/WALCL__weekly.csv` | 2026-04-17 22:29:57 UTC |
| file | `Data/MASTER_DATA.csv` | 2026-04-17 03:17:34 UTC |
| file | `Data/MASTER_DATA.md` | 2026-04-17 03:17:34 UTC |
| file | `Data/MASTER_DATA.txt` | 2026-04-18 02:22:07 UTC |
| dir | `Data/Tradingview` | 2026-04-17 02:51:10 UTC |
| dir | `Data/Tradingview/Daily` | 2026-04-17 22:31:19 UTC |
| file | `Data/Tradingview/Daily/ARKK_innovation_etf__daily.csv` | 2026-04-17 22:31:19 UTC |
| file | `Data/Tradingview/Daily/CME_BTC_front_month_futures__daily.csv` | 2026-04-17 22:31:19 UTC |
| file | `Data/Tradingview/Daily/CME_BTC_futures_minus_SPOT_BTC_basis__daily.csv` | 2026-04-17 22:31:19 UTC |
| file | `Data/Tradingview/Daily/CME_BTC_futures_over_SPOT_BTC_ratio__daily.csv` | 2026-04-17 22:31:19 UTC |
| file | `Data/Tradingview/Daily/CME_ETH_front_month_futures__daily.csv` | 2026-04-17 22:31:19 UTC |
| file | `Data/Tradingview/Daily/CME_ETH_futures_minus_SPOT_ETH_basis__daily.csv` | 2026-04-17 22:31:19 UTC |
| file | `Data/Tradingview/Daily/CME_ETH_futures_over_SPOT_ETH_ratio__daily.csv` | 2026-04-17 22:31:19 UTC |
| file | `Data/Tradingview/Daily/CME_Micro_Bitcoin_futures__daily.csv` | 2026-04-17 22:31:19 UTC |
| file | `Data/Tradingview/Daily/CME_Micro_Ether_futures__daily.csv` | 2026-04-17 22:31:19 UTC |
| file | `Data/Tradingview/Daily/CME_Solana_futures__daily.csv` | 2026-04-17 22:31:19 UTC |
| file | `Data/Tradingview/Daily/COIN_coinbase_stock__daily.csv` | 2026-04-17 22:31:19 UTC |
| file | `Data/Tradingview/Daily/CRCL_circle_stock__daily.csv` | 2026-04-17 22:31:19 UTC |
| file | `Data/Tradingview/Daily/CRYPTOCAP_BTC_dominance__daily.csv` | 2026-04-19 00:37:30 UTC |
| file | `Data/Tradingview/Daily/CRYPTOCAP_ETH_dominance__daily.csv` | 2026-04-19 00:37:31 UTC |
| file | `Data/Tradingview/Daily/CRYPTOCAP_TOTAL3__daily.csv` | 2026-04-19 00:37:31 UTC |
| file | `Data/Tradingview/Daily/Deribit_BTC_volatility_index_DVOL__daily.csv` | 2026-04-17 22:31:19 UTC |
| file | `Data/Tradingview/Daily/DXY_us_dollar_index__daily.csv` | 2026-04-17 22:31:19 UTC |
| file | `Data/Tradingview/Daily/ETHA_ETF_over_SPOT_ETH__daily.csv` | 2026-04-17 22:31:19 UTC |
| file | `Data/Tradingview/Daily/GLD_gold_etf__daily.csv` | 2026-04-17 22:31:19 UTC |
| file | `Data/Tradingview/Daily/IBIT_ETF_over_SPOT_BTC__daily.csv` | 2026-04-17 22:31:19 UTC |
| file | `Data/Tradingview/Daily/IWM_russell2000_etf__daily.csv` | 2026-04-17 22:31:19 UTC |
| file | `Data/Tradingview/Daily/MARA_marathon_miner_stock__daily.csv` | 2026-04-17 22:31:19 UTC |
| file | `Data/Tradingview/Daily/MSTR_microstrategy_stock__daily.csv` | 2026-04-17 22:31:19 UTC |
| file | `Data/Tradingview/Daily/QQQ_nasdaq100_etf__daily.csv` | 2026-04-17 22:31:19 UTC |
| file | `Data/Tradingview/Daily/README.md` | 2026-04-17 22:33:47 UTC |
| file | `Data/Tradingview/Daily/RIOT_riot_miner_stock__daily.csv` | 2026-04-17 22:31:19 UTC |
| file | `Data/Tradingview/Daily/SMH_vaneck_semiconductor_etf__daily.csv` | 2026-04-17 22:31:19 UTC |
| file | `Data/Tradingview/Daily/SOXX_ishares_semiconductor_etf__daily.csv` | 2026-04-17 22:31:19 UTC |
| file | `Data/Tradingview/Daily/SPY_sp500_etf__daily.csv` | 2026-04-17 22:31:19 UTC |
| file | `Data/Tradingview/Daily/XAUUSD_gold_spot__daily.csv` | 2026-04-17 22:31:19 UTC |
| file | `Data/Tradingview/Daily/XLK_tech_sector_etf__daily.csv` | 2026-04-17 22:31:19 UTC |
| file | `Data/Tradingview/README.md` | 2026-04-17 03:17:34 UTC |
| dir | `Data/Tradingview/Weekly` | 2026-04-17 22:31:19 UTC |
| file | `Data/Tradingview/Weekly/CME_BTC1_continuous_futures__weekly.csv` | 2026-04-17 22:31:19 UTC |
| file | `Data/Tradingview/Weekly/CME_ETH1_continuous_futures__weekly.csv` | 2026-04-17 22:31:19 UTC |
| file | `Data/Tradingview/Weekly/CME_Micro_Bitcoin_MBT1_continuous__weekly.csv` | 2026-04-17 22:31:19 UTC |
| file | `Data/Tradingview/Weekly/CME_Micro_Ether_MET1_continuous__weekly.csv` | 2026-04-17 22:31:19 UTC |
| file | `Data/Tradingview/Weekly/COIN_coinbase_stock__weekly.csv` | 2026-04-17 22:31:19 UTC |
| file | `Data/Tradingview/Weekly/CRYPTOCAP_BTC_dominance__weekly.csv` | 2026-04-19 00:37:31 UTC |
| file | `Data/Tradingview/Weekly/CRYPTOCAP_ETH_dominance__weekly.csv` | 2026-04-19 00:37:31 UTC |
| file | `Data/Tradingview/Weekly/CRYPTOCAP_TOTAL3__weekly.csv` | 2026-04-19 00:37:31 UTC |
| file | `Data/Tradingview/Weekly/DXY_us_dollar_index__weekly.csv` | 2026-04-17 22:31:19 UTC |
| file | `Data/Tradingview/Weekly/MSTR_microstrategy_stock__weekly.csv` | 2026-04-17 22:31:19 UTC |
| file | `Data/Tradingview/Weekly/QQQ_nasdaq100_etf__weekly.csv` | 2026-04-17 22:31:19 UTC |
| file | `Data/Tradingview/Weekly/README.md` | 2026-04-17 22:33:47 UTC |
| file | `Data/Tradingview/Weekly/RIOT_riot_miner_stock__weekly.csv` | 2026-04-17 22:31:19 UTC |
| file | `Data/Tradingview/Weekly/SPY_sp500_etf__weekly.csv` | 2026-04-17 22:31:19 UTC |
| file | `Data/Tradingview/Weekly/XAUUSD_gold_spot__weekly.csv` | 2026-04-17 22:31:19 UTC |
| dir | `docs` | 2026-04-18 21:54:56 UTC |
| dir | `docs/context` | 2026-04-18 21:54:56 UTC |
| file | `docs/context/00_project_context_and_goals.md` | 2026-04-18 21:54:56 UTC |
| file | `docs/context/01_research_framework_and_candidate_pathways.md` | 2026-04-18 21:54:56 UTC |
| file | `docs/context/02_data_sources_factor_blocks_and_sample_design.md` | 2026-04-18 21:54:56 UTC |
| file | `docs/context/03_quantitative_methods_and_analysis_menu.md` | 2026-04-18 21:54:56 UTC |
| file | `docs/context/04_cursor_operating_model_and_agent_workflow.md` | 2026-04-18 21:54:56 UTC |
| file | `docs/context/05_state_of_the_art_tooling_notes_2026-04-15.md` | 2026-04-18 21:54:56 UTC |
| dir | `docs/decisions` | 2026-04-18 21:54:56 UTC |
| file | `docs/decisions/.gitkeep` | 2026-04-18 21:54:56 UTC |
| dir | `docs/literature` | 2026-04-18 21:54:56 UTC |
| file | `docs/literature/.gitkeep` | 2026-04-18 21:54:56 UTC |
| dir | `docs/onboarding` | 2026-04-18 21:54:56 UTC |
| file | `docs/onboarding/.gitkeep` | 2026-04-18 21:54:56 UTC |
| dir | `docs/specs` | 2026-04-18 21:54:56 UTC |
| file | `docs/specs/data_spec.md` | 2026-04-18 21:54:56 UTC |
| file | `docs/specs/methods_spec.md` | 2026-04-18 21:54:56 UTC |
| file | `docs/specs/paper_1_native_metrics.yml` | 2026-04-19 19:49:11 UTC |
| file | `docs/specs/research_spec.md` | 2026-04-18 21:54:56 UTC |
| file | `Makefile` | 2026-04-18 08:48:06 UTC |
| dir | `Manager` | 2026-04-19 01:10:25 UTC |
| dir | `Manager/Codex Manager` | 2026-04-19 01:10:30 UTC |
| file | `Manager/Codex Manager/codex_manager_review_2026-04-18.md` | 2026-04-19 02:03:21 UTC |
| file | `Manager/Codex Manager/data_analysis.md` | 2026-04-18 23:30:28 UTC |
| file | `Manager/Codex Manager/data_calendar_metric_strategy_v0.md` | 2026-04-19 02:03:21 UTC |
| file | `Manager/Codex Manager/FINAL_ENHANCED.md` | 2026-04-19 03:57:11 UTC |
| file | `Manager/Codex Manager/four_paper_protocols_v0.md` | 2026-04-19 02:03:21 UTC |
| file | `Manager/Codex Manager/multi_agent_workflow_and_quality_gates_v0.md` | 2026-04-19 02:03:21 UTC |
| file | `Manager/Codex Manager/p0_execution_backlog.md` | 2026-04-19 02:03:21 UTC |
| file | `Manager/Codex Manager/README.md` | 2026-04-19 02:03:21 UTC |
| dir | `Manager/Gemini Manager` | 2026-04-19 01:10:39 UTC |
| file | `Manager/Gemini Manager/FINAL_ENHANCED.md` | 2026-04-19 03:43:29 UTC |
| file | `Manager/Gemini Manager/Project_Audit_Report.md` | 2026-04-19 01:13:51 UTC |
| file | `Manager/Manager_Outline.md` | 2026-04-18 21:54:56 UTC |
| file | `Manager/Manager_workflow.md` | 2026-04-18 21:54:56 UTC |
| dir | `Manager/Opus Manager` | 2026-04-19 01:10:35 UTC |
| file | `Manager/Opus Manager/comprehensive_review.md` | 2026-04-19 01:56:35 UTC |
| file | `Manager/Opus Manager/FINAL_ENHANCED.md` | 2026-04-19 03:55:18 UTC |
| file | `Manager/Opus Manager/project_research_plan.md` | 2026-04-18 08:45:46 UTC |
| dir | `Manager/Paper 1` | 2026-04-19 06:55:05 UTC |
| file | `Manager/Paper 1/Paper 1 CLAUDE.md` | 2026-04-19 20:05:22 UTC |
| file | `Manager/Paper 1/Paper 1 CODEX.md` | 2026-04-19 20:10:07 UTC |
| file | `Manager/Paper 1/Paper 1 GEMINI.md` | 2026-04-19 19:48:10 UTC |
| file | `Manager/Paper 1/Paper 1 Opus.md` | 2026-04-19 19:55:23 UTC |
| dir | `notebooks` | 2026-04-18 21:54:56 UTC |
| file | `notebooks/01_data_profile.ipynb` | 2026-04-18 21:54:56 UTC |
| file | `notebooks/02_block_correlations.ipynb` | 2026-04-18 21:54:56 UTC |
| file | `notebooks/03_structural_break_viz.ipynb` | 2026-04-18 21:54:56 UTC |
| file | `notebooks/_template.ipynb` | 2026-04-18 21:54:56 UTC |
| dir | `prompts` | 2026-04-18 21:54:56 UTC |
| file | `prompts/01_data_cleaning_agent.md` | 2026-04-18 21:54:56 UTC |
| file | `prompts/02_exploratory_analysis_agent.md` | 2026-04-18 21:54:56 UTC |
| file | `prompts/03_quant_methods_agent.md` | 2026-04-18 21:54:56 UTC |
| file | `prompts/04_visualization_agent.md` | 2026-04-18 21:54:56 UTC |
| file | `prompts/05_writing_agent.md` | 2026-04-18 21:54:56 UTC |
| file | `prompts/06_cursor_workflow_agent.md` | 2026-04-18 21:54:56 UTC |
| file | `prompts/07_red_team_reviewer_agent.md` | 2026-04-18 21:54:56 UTC |
| file | `prompts/08_final_synthesis_agent.md` | 2026-04-18 21:54:56 UTC |
| file | `prompts/AGENTS.md` | 2026-04-18 08:49:05 UTC |
| file | `prompts/HANDOFF.md` | 2026-04-18 10:08:36 UTC |
| file | `prompts/PAPER_1_META_PROMPT.md` | 2026-04-19 06:58:14 UTC |
| file | `prompts/README.md` | 2026-04-18 21:54:56 UTC |
| dir | `prompts/templates` | 2026-04-18 21:54:56 UTC |
| file | `prompts/templates/agent_preamble.md` | 2026-04-18 21:54:56 UTC |
| file | `prompts/templates/handoff.md` | 2026-04-18 21:54:56 UTC |
| file | `pyproject.toml` | 2026-04-18 08:47:48 UTC |
| file | `README.md` | 2026-04-12 06:40:12 UTC |
| dir | `references` | 2026-04-18 08:46:04 UTC |
| dir | `reports` | 2026-04-18 08:46:04 UTC |
| dir | `reports/appendix` | 2026-04-18 21:54:56 UTC |
| file | `reports/appendix/.gitkeep` | 2026-04-18 21:54:56 UTC |
| dir | `reports/deep_research` | 2026-04-18 21:54:56 UTC |
| file | `reports/deep_research/.gitkeep` | 2026-04-18 21:54:56 UTC |
| dir | `reports/drafts` | 2026-04-18 21:54:56 UTC |
| file | `reports/drafts/paper_v0.1_2026-04-18.md` | 2026-04-18 21:54:56 UTC |
| file | `reports/drafts/paper_v1.0_2026-04-19.md` | 2026-04-19 19:55:37 UTC |
| dir | `reports/drafts/sections` | 2026-04-18 21:54:56 UTC |
| file | `reports/drafts/sections/.gitkeep` | 2026-04-18 21:54:56 UTC |
| dir | `reports/figures` | 2026-04-18 21:54:56 UTC |
| file | `reports/figures/.gitkeep` | 2026-04-18 21:54:56 UTC |
| dir | `reports/figures/2026-04-18` | 2026-04-18 21:54:56 UTC |
| file | `reports/figures/2026-04-18/F01_cumulative_returns.png` | 2026-04-18 21:54:56 UTC |
| file | `reports/figures/2026-04-18/F02_btc_rolling_r2.png` | 2026-04-18 21:54:56 UTC |
| file | `reports/figures/2026-04-18/F02_eth_rolling_r2.png` | 2026-04-18 21:54:56 UTC |
| file | `reports/figures/2026-04-18/F03_btc_partial_r2_stack.png` | 2026-04-18 21:54:56 UTC |
| file | `reports/figures/2026-04-18/F04_eth_partial_r2_stack.png` | 2026-04-18 21:54:56 UTC |
| file | `reports/figures/2026-04-18/F05_sup_f_btc.png` | 2026-04-18 21:54:56 UTC |
| file | `reports/figures/2026-04-18/F06_sup_f_eth.png` | 2026-04-18 21:54:56 UTC |
| file | `reports/figures/2026-04-18/F07_fevd_heatmap.png` | 2026-04-18 21:54:56 UTC |
| file | `reports/figures/2026-04-18/F08_event_cars.png` | 2026-04-18 21:54:56 UTC |
| file | `reports/figures/2026-04-18/F09_coverage.png` | 2026-04-18 21:54:56 UTC |
| file | `reports/figures/2026-04-18/F10_btc_tradfi_corr.png` | 2026-04-18 21:54:56 UTC |
| dir | `reports/figures/2026-04-19` | 2026-04-19 19:54:09 UTC |
| file | `reports/figures/2026-04-19/F01_cumulative_returns.png` | 2026-04-19 19:54:10 UTC |
| file | `reports/figures/2026-04-19/F02_btc_rolling_r2.png` | 2026-04-19 19:54:10 UTC |
| file | `reports/figures/2026-04-19/F02_eth_rolling_r2.png` | 2026-04-19 19:54:11 UTC |
| file | `reports/figures/2026-04-19/F03_btc_partial_r2_stack.png` | 2026-04-19 19:54:11 UTC |
| file | `reports/figures/2026-04-19/F04_eth_partial_r2_stack.png` | 2026-04-19 19:54:11 UTC |
| file | `reports/figures/2026-04-19/F05_sup_f_btc.png` | 2026-04-19 19:54:11 UTC |
| file | `reports/figures/2026-04-19/F06_sup_f_eth.png` | 2026-04-19 19:54:12 UTC |
| file | `reports/figures/2026-04-19/F07_fevd_heatmap.png` | 2026-04-19 19:54:12 UTC |
| file | `reports/figures/2026-04-19/F07b_fevd_heatmap_full.png` | 2026-04-19 19:54:12 UTC |
| file | `reports/figures/2026-04-19/F08_event_cars.png` | 2026-04-19 19:54:13 UTC |
| file | `reports/figures/2026-04-19/F09_coverage.png` | 2026-04-19 19:54:13 UTC |
| file | `reports/figures/2026-04-19/F10_btc_tradfi_corr.png` | 2026-04-19 19:54:14 UTC |
| dir | `reports/panels` | 2026-04-18 08:46:04 UTC |
| file | `reports/panels/.gitkeep` | 2026-04-18 08:46:12 UTC |
| file | `reports/panels/master_daily.parquet` | 2026-04-18 09:55:24 UTC |
| file | `reports/panels/master_daily_coverage.csv` | 2026-04-18 09:55:24 UTC |
| file | `reports/panels/master_daily_meta.json` | 2026-04-18 09:55:24 UTC |
| dir | `reports/prior_ai_outputs` | 2026-04-18 21:54:56 UTC |
| file | `reports/prior_ai_outputs/Beyond Correlation_ Quantifying Bitcoin's New Role in Financial Markets Through Structural Breaks, Flow Dynamics, and Systemic Risk.md` | 2026-04-18 21:54:56 UTC |
| file | `reports/prior_ai_outputs/Crypto Research Agenda Development.md` | 2026-04-18 21:54:56 UTC |
| file | `reports/prior_ai_outputs/deep-research-report.md` | 2026-04-18 21:54:56 UTC |
| file | `reports/prior_ai_outputs/FINAL_SYNTHESIS_TOP5_PROJECTS.md` | 2026-04-18 21:54:56 UTC |
| file | `reports/prior_ai_outputs/research_memo.md` | 2026-04-18 21:54:56 UTC |
| file | `reports/prior_ai_outputs/txt output p2.md` | 2026-04-18 21:54:56 UTC |
| file | `reports/prior_ai_outputs/txt output.md` | 2026-04-18 21:54:56 UTC |
| dir | `reports/run_summaries` | 2026-04-18 21:54:56 UTC |
| file | `reports/run_summaries/.gitkeep` | 2026-04-18 21:54:56 UTC |
| file | `reports/run_summaries/01_inspect_core_files.json` | 2026-04-18 21:54:56 UTC |
| file | `reports/run_summaries/01_inspect_core_files.md` | 2026-04-18 21:54:56 UTC |
| file | `reports/run_summaries/02_build_master_panel.md` | 2026-04-18 21:54:56 UTC |
| file | `reports/run_summaries/03_run_analyses.md` | 2026-04-18 21:54:56 UTC |
| dir | `reports/tables` | 2026-04-18 21:54:56 UTC |
| file | `reports/tables/.gitkeep` | 2026-04-18 21:54:56 UTC |
| dir | `reports/tables/2026-04-18` | 2026-04-18 21:54:56 UTC |
| file | `reports/tables/2026-04-18/block_r2_pre_post.csv` | 2026-04-18 21:54:56 UTC |
| file | `reports/tables/2026-04-18/correlation_matrix_post_etf.csv` | 2026-04-18 21:54:56 UTC |
| file | `reports/tables/2026-04-18/correlation_matrix_pre_etf.csv` | 2026-04-18 21:54:56 UTC |
| file | `reports/tables/2026-04-18/descriptive_stats.csv` | 2026-04-18 21:54:56 UTC |
| file | `reports/tables/2026-04-18/etf_flow_regression.csv` | 2026-04-18 21:54:56 UTC |
| file | `reports/tables/2026-04-18/event_studies.csv` | 2026-04-18 21:54:56 UTC |
| file | `reports/tables/2026-04-18/fevd_10d.csv` | 2026-04-18 21:54:56 UTC |
| dir | `reports/tables/2026-04-18/robustness` | 2026-04-18 21:54:56 UTC |
| file | `reports/tables/2026-04-18/robustness/R1_lagged_etf_flow.csv` | 2026-04-18 21:54:56 UTC |
| file | `reports/tables/2026-04-18/robustness/R2_no_winsor_post_etf.csv` | 2026-04-18 21:54:56 UTC |
| file | `reports/tables/2026-04-18/robustness/R3_hac_lag_sensitivity.csv` | 2026-04-18 21:54:56 UTC |
| file | `reports/tables/2026-04-18/robustness/R4_post2021_static_ols.csv` | 2026-04-18 21:54:56 UTC |
| file | `reports/tables/2026-04-18/robustness/R5_supF_split.csv` | 2026-04-18 21:54:56 UTC |
| file | `reports/tables/2026-04-18/robustness/R6_common_support.csv` | 2026-04-18 21:54:56 UTC |
| file | `reports/tables/2026-04-18/rolling_ols_btc_180d.csv` | 2026-04-18 21:54:56 UTC |
| file | `reports/tables/2026-04-18/rolling_ols_eth_180d.csv` | 2026-04-18 21:54:56 UTC |
| file | `reports/tables/2026-04-18/rolling_r2_btc_median_by_year.csv` | 2026-04-18 21:54:56 UTC |
| file | `reports/tables/2026-04-18/rolling_r2_eth_median_by_year.csv` | 2026-04-18 21:54:56 UTC |
| file | `reports/tables/2026-04-18/static_ols_pre_post_etf.csv` | 2026-04-18 21:54:56 UTC |
| file | `reports/tables/2026-04-18/structural_breaks_summary.csv` | 2026-04-18 21:54:56 UTC |
| file | `reports/tables/2026-04-18/sup_f_series_btc.csv` | 2026-04-18 21:54:56 UTC |
| file | `reports/tables/2026-04-18/sup_f_series_eth.csv` | 2026-04-18 21:54:56 UTC |
| file | `reports/tables/2026-04-18/var_fevd_meta.json` | 2026-04-18 21:54:56 UTC |
| dir | `reports/tables/2026-04-19` | 2026-04-19 19:50:05 UTC |
| file | `reports/tables/2026-04-19/block_r2_pre_post.csv` | 2026-04-19 19:54:06 UTC |
| file | `reports/tables/2026-04-19/correlation_matrix_post_etf.csv` | 2026-04-19 19:54:06 UTC |
| file | `reports/tables/2026-04-19/correlation_matrix_pre_etf.csv` | 2026-04-19 19:54:06 UTC |
| file | `reports/tables/2026-04-19/descriptive_stats.csv` | 2026-04-19 19:54:06 UTC |
| file | `reports/tables/2026-04-19/etf_flow_regression.csv` | 2026-04-19 19:54:06 UTC |
| file | `reports/tables/2026-04-19/event_studies.csv` | 2026-04-19 19:53:56 UTC |
| file | `reports/tables/2026-04-19/fevd_10d.csv` | 2026-04-19 19:53:52 UTC |
| file | `reports/tables/2026-04-19/fevd_10d_compact.csv` | 2026-04-19 19:53:51 UTC |
| dir | `reports/tables/2026-04-19/robustness` | 2026-04-19 19:54:07 UTC |
| file | `reports/tables/2026-04-19/robustness/R1_lagged_etf_flow.csv` | 2026-04-19 19:54:08 UTC |
| file | `reports/tables/2026-04-19/robustness/R2_no_winsor_post_etf.csv` | 2026-04-19 19:54:08 UTC |
| file | `reports/tables/2026-04-19/robustness/R3_hac_lag_sensitivity.csv` | 2026-04-19 19:54:08 UTC |
| file | `reports/tables/2026-04-19/robustness/R4_post2021_static_ols.csv` | 2026-04-19 19:54:08 UTC |
| file | `reports/tables/2026-04-19/robustness/R5_supF_split.csv` | 2026-04-19 19:54:08 UTC |
| file | `reports/tables/2026-04-19/robustness/R6_common_support.csv` | 2026-04-19 19:54:08 UTC |
| file | `reports/tables/2026-04-19/rolling_ols_btc_180d.csv` | 2026-04-19 19:50:08 UTC |
| file | `reports/tables/2026-04-19/rolling_ols_eth_180d.csv` | 2026-04-19 19:50:09 UTC |
| file | `reports/tables/2026-04-19/rolling_r2_btc_median_by_year.csv` | 2026-04-19 19:54:06 UTC |
| file | `reports/tables/2026-04-19/rolling_r2_eth_median_by_year.csv` | 2026-04-19 19:54:06 UTC |
| file | `reports/tables/2026-04-19/static_ols_pre_post_etf.csv` | 2026-04-19 19:50:06 UTC |
| file | `reports/tables/2026-04-19/structural_breaks_summary.csv` | 2026-04-19 19:53:51 UTC |
| file | `reports/tables/2026-04-19/sup_f_series_btc.csv` | 2026-04-19 19:52:10 UTC |
| file | `reports/tables/2026-04-19/sup_f_series_eth.csv` | 2026-04-19 19:53:51 UTC |
| file | `reports/tables/2026-04-19/var_fevd_meta.json` | 2026-04-19 19:53:52 UTC |
| file | `reports/tables/2026-04-19/var_fevd_meta_compact.json` | 2026-04-19 19:53:51 UTC |
| file | `run_pipeline.py` | 2026-04-18 08:51:01 UTC |
| dir | `scripts` | 2026-04-18 21:54:56 UTC |
| file | `scripts/01_build_master_panel.py` | 2026-04-18 21:54:56 UTC |
| file | `scripts/02_run_analyses.py` | 2026-04-18 21:54:56 UTC |
| file | `scripts/03_make_figures.py` | 2026-04-18 21:54:56 UTC |
| file | `scripts/04_descriptives_and_summaries.py` | 2026-04-18 21:54:56 UTC |
| file | `scripts/05_robustness.py` | 2026-04-18 21:54:56 UTC |
| file | `scripts/inspect_core_files.py` | 2026-04-18 21:54:56 UTC |
| file | `scripts/run_full_pipeline.py` | 2026-04-18 21:54:56 UTC |
| dir | `src` | 2026-04-18 08:46:04 UTC |
| dir | `src/cqresearch` | 2026-04-18 08:46:04 UTC |
| file | `src/cqresearch/__init__.py` | 2026-04-18 08:51:08 UTC |
| dir | `src/cqresearch/__pycache__` | 2026-04-18 09:03:32 UTC |
| file | `src/cqresearch/__pycache__/__init__.cpython-310.pyc` | 2026-04-19 01:15:56 UTC |
| dir | `src/cqresearch/analysis` | 2026-04-18 08:46:04 UTC |
| file | `src/cqresearch/analysis/__init__.py` | 2026-04-18 08:51:41 UTC |
| dir | `src/cqresearch/analysis/__pycache__` | 2026-04-18 09:03:32 UTC |
| file | `src/cqresearch/analysis/__pycache__/__init__.cpython-310.pyc` | 2026-04-19 01:15:56 UTC |
| dir | `src/cqresearch/data` | 2026-04-18 08:46:04 UTC |
| file | `src/cqresearch/data/__init__.py` | 2026-04-18 08:51:25 UTC |
| dir | `src/cqresearch/data/__pycache__` | 2026-04-18 09:03:32 UTC |
| file | `src/cqresearch/data/__pycache__/__init__.cpython-310.pyc` | 2026-04-19 01:15:56 UTC |
| file | `src/cqresearch/data/__pycache__/calendars.cpython-310.pyc` | 2026-04-19 19:49:21 UTC |
| file | `src/cqresearch/data/__pycache__/loaders.cpython-310.pyc` | 2026-04-19 19:49:52 UTC |
| file | `src/cqresearch/data/__pycache__/panel_builder.cpython-310.pyc` | 2026-04-19 19:49:51 UTC |
| file | `src/cqresearch/data/calendars.py` | 2026-04-18 09:52:00 UTC |
| file | `src/cqresearch/data/loaders.py` | 2026-04-18 09:52:40 UTC |
| file | `src/cqresearch/data/panel_builder.py` | 2026-04-18 09:53:11 UTC |
| dir | `src/cqresearch/features` | 2026-04-18 08:46:04 UTC |
| file | `src/cqresearch/features/__init__.py` | 2026-04-18 08:51:31 UTC |
| dir | `src/cqresearch/features/__pycache__` | 2026-04-18 09:03:32 UTC |
| file | `src/cqresearch/features/__pycache__/__init__.cpython-310.pyc` | 2026-04-19 01:15:56 UTC |
| file | `src/cqresearch/features/__pycache__/panel.cpython-310.pyc` | 2026-04-19 19:49:58 UTC |
| file | `src/cqresearch/features/__pycache__/returns.cpython-310.pyc` | 2026-04-19 19:49:58 UTC |
| file | `src/cqresearch/features/panel.py` | 2026-04-18 09:56:12 UTC |
| file | `src/cqresearch/features/returns.py` | 2026-04-18 09:53:27 UTC |
| dir | `src/cqresearch/modeling` | 2026-04-18 08:46:04 UTC |
| file | `src/cqresearch/modeling/__init__.py` | 2026-04-18 08:51:37 UTC |
| dir | `src/cqresearch/modeling/__pycache__` | 2026-04-18 09:03:32 UTC |
| file | `src/cqresearch/modeling/__pycache__/__init__.cpython-310.pyc` | 2026-04-19 01:15:56 UTC |
| file | `src/cqresearch/modeling/__pycache__/event_study.cpython-310.pyc` | 2026-04-19 19:50:05 UTC |
| file | `src/cqresearch/modeling/__pycache__/ols.cpython-310.pyc` | 2026-04-19 19:49:58 UTC |
| file | `src/cqresearch/modeling/__pycache__/rolling.cpython-310.pyc` | 2026-04-19 19:50:05 UTC |
| file | `src/cqresearch/modeling/__pycache__/structural_breaks.cpython-310.pyc` | 2026-04-19 19:50:05 UTC |
| file | `src/cqresearch/modeling/__pycache__/var_fevd.cpython-310.pyc` | 2026-04-19 19:50:05 UTC |
| file | `src/cqresearch/modeling/event_study.py` | 2026-04-18 09:54:56 UTC |
| file | `src/cqresearch/modeling/ols.py` | 2026-04-18 09:53:42 UTC |
| file | `src/cqresearch/modeling/rolling.py` | 2026-04-18 09:53:58 UTC |
| file | `src/cqresearch/modeling/structural_breaks.py` | 2026-04-18 09:54:21 UTC |
| file | `src/cqresearch/modeling/var_fevd.py` | 2026-04-18 09:54:32 UTC |
| dir | `src/cqresearch/utils` | 2026-04-18 08:46:04 UTC |
| file | `src/cqresearch/utils/__init__.py` | 2026-04-18 08:51:50 UTC |
| dir | `src/cqresearch/utils/__pycache__` | 2026-04-18 09:03:32 UTC |
| file | `src/cqresearch/utils/__pycache__/__init__.cpython-310.pyc` | 2026-04-19 01:15:56 UTC |
| dir | `src/cqresearch/viz` | 2026-04-18 08:46:04 UTC |
| file | `src/cqresearch/viz/__init__.py` | 2026-04-18 08:51:45 UTC |
| dir | `src/cqresearch/viz/__pycache__` | 2026-04-18 09:03:32 UTC |
| file | `src/cqresearch/viz/__pycache__/__init__.cpython-310.pyc` | 2026-04-19 01:15:56 UTC |
| file | `src/cqresearch/viz/__pycache__/style.cpython-310.pyc` | 2026-04-19 19:54:09 UTC |
| file | `src/cqresearch/viz/style.py` | 2026-04-18 10:01:38 UTC |
| dir | `tests` | 2026-04-18 08:46:04 UTC |
| file | `tests/__init__.py` | 2026-04-18 09:02:20 UTC |
| dir | `tests/__pycache__` | 2026-04-18 09:03:29 UTC |
| file | `tests/__pycache__/__init__.cpython-310.pyc` | 2026-04-19 01:15:56 UTC |
| dir | `tests/fixtures` | 2026-04-18 21:54:56 UTC |
| file | `tests/fixtures/.gitkeep` | 2026-04-18 21:54:56 UTC |
| file | `tests/fixtures/tiny_macro.csv` | 2026-04-18 21:54:56 UTC |
| file | `tests/fixtures/tiny_prices.csv` | 2026-04-18 21:54:56 UTC |
| dir | `tests/integration` | 2026-04-18 21:54:56 UTC |
| file | `tests/integration/.gitkeep` | 2026-04-18 21:54:56 UTC |
| dir | `tests/unit` | 2026-04-18 08:46:04 UTC |
| file | `tests/unit/__init__.py` | 2026-04-18 09:02:23 UTC |
| dir | `tests/unit/__pycache__` | 2026-04-18 09:03:29 UTC |
| file | `tests/unit/__pycache__/__init__.cpython-310.pyc` | 2026-04-19 01:15:56 UTC |
| file | `tests/unit/__pycache__/conftest.cpython-310-pytest-8.4.2.pyc` | 2026-04-19 01:15:56 UTC |
| file | `tests/unit/__pycache__/test_calendars.cpython-310-pytest-8.4.2.pyc` | 2026-04-19 19:54:44 UTC |
| file | `tests/unit/__pycache__/test_config_yamls.cpython-310-pytest-8.4.2.pyc` | 2026-04-19 01:15:56 UTC |
| file | `tests/unit/__pycache__/test_fixtures.cpython-310-pytest-8.4.2.pyc` | 2026-04-19 01:15:56 UTC |
| file | `tests/unit/__pycache__/test_imports_smoke.cpython-310-pytest-8.4.2.pyc` | 2026-04-19 01:15:56 UTC |
| file | `tests/unit/conftest.py` | 2026-04-18 09:02:36 UTC |
| file | `tests/unit/test_calendars.py` | 2026-04-19 19:49:03 UTC |
| file | `tests/unit/test_config_yamls.py` | 2026-04-18 09:03:07 UTC |
| file | `tests/unit/test_fixtures.py` | 2026-04-18 09:03:13 UTC |
| file | `tests/unit/test_imports_smoke.py` | 2026-04-18 09:02:58 UTC |
| dir | `tools` | 2026-04-12 06:08:45 UTC |
| file | `tools/_gen_arch.py` | 2026-04-20 04:15:40 UTC |
| dir | `tools/data_collection` | 2026-04-17 22:22:16 UTC |
| file | `tools/data_collection/__init__.py` | 2026-04-17 22:22:16 UTC |
| file | `tools/data_collection/fetch_farside_etf_csv.py` | 2026-04-12 06:19:29 UTC |
| file | `tools/data_collection/fetch_fear_greed.py` | 2026-04-17 22:23:38 UTC |
| file | `tools/data_collection/fetch_fred.py` | 2026-04-17 22:23:14 UTC |
| file | `tools/data_collection/harvest_defillama.py` | 2026-04-14 23:09:32 UTC |
| file | `tools/data_collection/organize_cryptoquant_metrics.py` | 2026-04-12 06:08:45 UTC |
| dir | `tools/data_curation` | 2026-04-17 03:09:20 UTC |
| file | `tools/data_curation/01_snapshot_raw_hashes.py` | 2026-04-17 03:09:43 UTC |
| file | `tools/data_curation/02_dedupe_defi.py` | 2026-04-17 03:10:32 UTC |
| file | `tools/data_curation/03_merge_defi_parts.py` | 2026-04-17 03:11:21 UTC |
| file | `tools/data_curation/04_normalize_dates.py` | 2026-04-17 03:12:30 UTC |
| file | `tools/data_curation/05_rename_tradingview.py` | 2026-04-17 03:15:15 UTC |
| file | `tools/data_curation/06_build_inventory.py` | 2026-04-17 03:17:25 UTC |
| file | `tools/data_curation/07_validate.py` | 2026-04-17 03:19:00 UTC |
| file | `tools/data_curation/08_consolidate_defi.py` | 2026-04-17 03:27:58 UTC |
| file | `tools/data_curation/09_reorg_tradingview.py` | 2026-04-17 22:25:06 UTC |
| file | `tools/data_curation/10_clean_new_defi.py` | 2026-04-17 22:26:44 UTC |
| file | `tools/data_curation/11_flatten_farside.py` | 2026-04-17 22:27:28 UTC |
| dir | `tools/data_curation/__pycache__` | 2026-04-17 03:09:47 UTC |
| file | `tools/data_curation/__pycache__/_common.cpython-310.pyc` | 2026-04-19 01:01:12 UTC |
| file | `tools/data_curation/_common.py` | 2026-04-17 03:09:33 UTC |
| file | `tools/README.md` | 2026-04-18 08:59:51 UTC |
| file | `tools/tradingview_curate_cryptocap.py` | 2026-04-19 00:37:09 UTC |
| file | `uv.lock` | 2026-04-19 19:54:38 UTC |

---

*End of Current_Architecture.md*