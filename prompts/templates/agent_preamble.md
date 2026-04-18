# Agent preamble (prepend to every prompt)

You are an agent working in the **CryptoQuant Research** repo.

**Repo invariants (never violate):**
- Do not mutate files under `Data/` or `reports/prior_ai_outputs/`.
- Cite file paths for every data claim. Use confidence labels: `[conf: High|Medium|Low]`.
- Read `project_research_plan.md` and `AGENTS.md` at session start.
- Configs are authoritative: `config/calendars.yml`, `config/events.yml`, `config/factor_blocks.yml`, `config/chain_taxonomy.yml`, `config/curation_snapshots.yml`.
- All new analysis writes a `reports/run_summaries/<YYYY-MM-DD>_<task>.md`.
- Python ≥ 3.11 via `uv`. Do not `pip install` inline.

**Hand-off contract:**
When done, emit a markdown block in the format of `prompts/templates/handoff.md` listing: task, files read, files produced, key numbers, risks, confidence, and the next suggested agent.

**When uncertain:**
Stop. State the ambiguity. Cite the conflicting files. Propose 2-3 disambiguations. Ask.
