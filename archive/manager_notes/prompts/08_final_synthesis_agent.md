# 08 — Final Synthesis Agent

<!-- prepend prompts/templates/agent_preamble.md -->

## Mission
Integrate the writing agent's draft with the red-team agent's patch file into a publishable `reports/drafts/paper_v1.0_<YYYY-MM-DD>.md`. Produce the submission packet.

## Inputs
- `reports/drafts/paper_v0.1_<YYYY-MM-DD>.md`
- `reports/drafts/red_team_patches.md`
- All `reports/tables/`, `reports/figures/`, `reports/run_summaries/`.
- `docs/specs/research_spec.md` for the final scope contract.

## Tasks
1. Apply every survived patch. Reject every patch flagged "rejected" with a one-line justification in an ADR under `docs/decisions/`.
2. Tighten abstract, intro, and conclusion. Final length target: 4000-6000 words main text + appendix.
3. Produce the **submission packet** under `reports/drafts/submission/<YYYY-MM-DD>/`:
   - `paper_v1.0.md`
   - `paper_v1.0.pdf` (pandoc build)
   - `figures/` copy of every PDF used
   - `tables/` CSV copies used
   - `appendix.md` with all robustness runs
   - `replication.md` with exact `uv sync` + `make pipeline` + `make figures` commands, and hashes of every input CSV/panel
4. Update `README.md` "Status" line and `AGENTS.md §6` with the final version tag.

## Rules
- Do not introduce new claims at synthesis. Only strengthen existing ones.
- Every confidence label in the final paper must be **High** or explicitly flagged Medium/Low in text.
- The submission packet must be hash-verifiable: the same `master_daily.parquet` hash should produce identical tables.

## Done when
- `reports/drafts/submission/<YYYY-MM-DD>/paper_v1.0.pdf` exists.
- `replication.md` verified on a clean `uv` env.
- Hand-off block filed in `reports/run_summaries/<YYYY-MM-DD>_final_synthesis.md`.
