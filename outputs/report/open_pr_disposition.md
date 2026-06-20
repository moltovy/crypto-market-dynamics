# Open PR Disposition

Task 00 requires open PR review before implementation. One open PR was found with `gh pr list` on 2026-06-19 local workspace time.

## PR #3

| Field | Value |
|---|---|
| Number | 3 |
| Title | Improve market-structure visualization quality |
| URL | https://github.com/moltovy/Crypto-Research-Paper-Data-Factors-Analysis-/pull/3 |
| Base | `main` |
| Head | `codex/improve-market-structure-visuals` |
| Commits | `95c8703 chore(viz): improve market structure figure quality`; `af310e8 chore(viz): govern public figure surface` |
| Merge state | Clean |
| Changed files | 141 |
| Additions/deletions | 61,322 additions / 60,168 deletions |

## Diff Summary

The PR:

- moves many old public figures and visual audit artifacts into `archive/visuals/legacy_diagnostics/`;
- regenerates or moves F30-F53 market-structure/current-cohort figures into `outputs/figures/gallery/`;
- adds `outputs/figures/public_contact_sheet.png`;
- updates `outputs/report/visualization_quality_audit.md`;
- modifies market-structure taxonomy and visualization code;
- updates README and `outputs/README.md`;
- modifies T40-T58 market-structure and current-cohort tables.

## Disposition

| Area | Classification | Rationale |
|---|---|---|
| Archive moves for old visual diagnostics | Retain concept, reimplement selectively | The final program wants old diagnostics isolated from public output, but the final branch should archive/delete based on the new canonical nine-figure registry rather than inherit the PR's exact F-numbered layout. |
| Visual QA/reporting idea | Retain | `visualization_quality_audit.md` and public-only contact-sheet discipline align with Task 15. |
| `config/asset_classification_overrides.yml` taxonomy refinements | Fix before reuse | The direction is useful, but the final taxonomy must be governed by canonical IDs and the required stable/productized/governance distinctions. |
| Market-structure code changes | Fix before reuse | Some helper ideas may be reusable, but final architecture requires splitting ingestion, analysis, reporting, manifest writing, and plotting. |
| F30-F53 gallery/public figure changes | Supersede | Final program requires exactly nine semantic public figures and gallery-only current-cohort appendix material. |
| README/output index edits | Supersede | Final README must be rewritten around research questions, evidence ledger, and nine semantic figures. |
| Generated T40-T58 table churn | Fix before reuse | PIT monthly outputs are useful, but the final branch must regenerate semantic canonical tables with corrected taxonomy and no historical current-cohort claims. |
| PR as a whole | Supersede | Do not merge. The final consolidation branch will replace it with a broader research-design and public-surface correction. |

## Action

Start `codex/final-research-consolidation` from `main`. Selectively reuse PR #3 ideas only after reviewing the exact file-level changes, especially visual QA, archive isolation, and taxonomy guardrails. Do not merge PR #3 automatically.
