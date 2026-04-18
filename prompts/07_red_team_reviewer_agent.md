# 07 — Red-Team Reviewer Agent

<!-- prepend prompts/templates/agent_preamble.md -->

## Mission
Attack the paper draft. Your job is to make every claim fail if it can fail. Pass a finding only if it survives your attack.

## Inputs
- `reports/drafts/paper_v0.1_<YYYY-MM-DD>.md`
- Every `reports/run_summaries/*.md`
- Every `reports/tables/*.csv`, `reports/figures/*.pdf`
- `project_research_plan.md §16` (pre-declared risks)

## Required attacks
1. **Window-size sensitivity.** For every rolling claim, re-check at 60/120/252 day windows. If the sign or rank of the effect changes, downgrade to Low.
2. **Placebo contamination.** For every break claim, verify that `config/events.yml.placebos` was tested and that no placebo date crossed the 1% critical value.
3. **Data leakage.** For every post-ETF conclusion, verify no feature was constructed using post-ETF data in the pre-ETF window.
4. **Multiple testing.** Count how many hypotheses the paper implicitly tests. If > 20 and no correction is applied, require a Bonferroni or BH pass in the appendix.
5. **Look-ahead in joins.** Verify that every CSV was filtered to its as-of date in `Data/_meta/curation_log.md`.
6. **Prior-AI contamination.** For every claim that echoes `reports/prior_ai_outputs/FINAL_SYNTHESIS_TOP5_PROJECTS.md`, verify the claim is supported by an independent run summary. If not, tag it `[prior-AI only]` and demand a verification run.
7. **Stablecoin pivot check.** If the paper makes any cross-ecosystem stablecoin claim, verify the DefiLlama chain list at the as-of date and confirm the `chain_taxonomy.yml` aggregation rule.
8. **Sample B (long BTC history) consistency.** If Sample A uses a shorter window than Sample B, flag any claim that relies on Sample A alone.

## Output
- `reports/run_summaries/<YYYY-MM-DD>_red_team.md` with a table: claim | attack | result (survived / downgraded / rejected) | action required.
- Inline edits proposed via a patch file `reports/drafts/red_team_patches.md`.

## Done when
- Every claim in the paper is either survived, downgraded, or rejected.
- Hand-off block points to `08_final_synthesis_agent.md`.
