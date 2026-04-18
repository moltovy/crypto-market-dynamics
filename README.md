# CryptoQuant Research

> **Project.** An MSc-level empirical-finance study of **how Bitcoin and Ethereum's factor exposures evolved around the 2024 US spot-ETF launch**, using rolling OLS with block-level partial R² as the headline diagnostic, Bai-Perron and Chow structural-break tests on pre-registered event dates, and compact VAR / FEVD systems for dynamic confirmation.
>
> **Team.** 3-student MSc research program.
>
> **Status.** Sprint 1 in progress. Canonical plan: [`project_research_plan.md`](./project_research_plan.md).

---

## Quick-start

```powershell
# 1. Install uv if you don't already have it.
#    See https://docs.astral.sh/uv/getting-started/installation/

# 2. Clone the repo, then:
uv sync --all-extras

# 3. Copy the env template and fill in API keys for ingestion:
Copy-Item .env.example .env
#    Edit .env to add FRED_API_KEY at minimum.

# 4. Inspect the data you already have:
Get-Content Data/MASTER_DATA.md | Select-Object -First 40

# 5. Run a dry-run of the curation pipeline (no writes):
python run_pipeline.py --dry-run

# 6. Run the test suite:
pytest
```

---

## Repository map

| Folder | Purpose |
|---|---|
| [`Data/`](./Data/) | Curated CSV data (484 files across 7 sources). Governed by [`tools/`](./tools/). Do not edit by hand. |
| [`config/`](./config/) | Single source of truth for paths, calendars, events, factor blocks, chain taxonomy, curation snapshots. |
| [`src/cqresearch/`](./src/cqresearch/) | Reusable Python package: `data` / `features` / `modeling` / `analysis` / `viz` / `utils`. |
| [`scripts/`](./scripts/) | Numbered top-level orchestration scripts (`00..99`). |
| [`notebooks/`](./notebooks/) | Exploratory notebooks (one per hypothesis). |
| [`tools/`](./tools/) | Ingestion and curation pipeline. |
| [`tests/`](./tests/) | `unit/`, `integration/`, `fixtures/`. |
| [`prompts/`](./prompts/) | Versioned agent prompts. |
| [`reports/`](./reports/) | Research artifacts: drafts, figures, tables, run summaries, prior AI outputs, panels. |
| [`docs/`](./docs/) | Onboarding, specs, ADRs, context, manager memos, literature. |
| [`references/`](./references/) | Third-party read-only references (teaching material, workflow tip corpora). |
| [`archive/`](./archive/) | Historical artifacts kept for provenance. |
| [`.cursor/`](./.cursor/) | Cursor rules + project skills + MCP stub. |

See the [full canonical tree in §19 of the plan](./project_research_plan.md#19-reorganization-specification).

---

## Data refresh

The 484 curated CSVs in `Data/` are produced by a reproducible pipeline. To refresh:

```powershell
make ingest      # ingest raw data from FRED, Farside, DefiLlama, Fear-Greed
make curate      # run curation steps 01..11
make inventory   # rebuild Data/MASTER_DATA.{md,txt,csv}
make validate    # run 07_validate.py
```

Full audit trail: [`Data/_meta/curation_log.md`](./Data/_meta/curation_log.md).

---

## Agent operating

Humans and agents working on this project should read [`AGENTS.md`](./AGENTS.md) first, then the three specs in [`docs/specs/`](./docs/specs/), then the six rules in [`.cursor/rules/`](./.cursor/rules/). Ready-to-paste prompts for each research role are in [`prompts/`](./prompts/).

---

## License

See [`LICENSE`](./LICENSE) if present, else defaults to MIT for `src/cqresearch/` code. External corpora under `references/` retain their upstream licenses.
