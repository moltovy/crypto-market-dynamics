# Multi-Agent Workflow and Quality Gates v0

Date: 2026-04-18

Purpose: define a professional operating model for GPT-5.4/Codex-class agents, Claude Opus-class reviewers, Gemini/Deep Research-class external research agents, and Cursor/background implementation agents.

## Operating Principles

1. Repository evidence outranks AI summaries.
2. `AGENTS.md` is controlling when files conflict.
3. Prior AI outputs are hypotheses, not authority.
4. Agents must cite concrete repo paths for empirical claims.
5. Agents may disagree; reconciliation is by evidence quality, not majority vote.
6. High-impact decisions require human approval.

Evidence: `AGENTS.md`; `reports/prior_ai_outputs/`; `Manager/Gemini Manager/Project_Audit_Report.md`; `Manager/Opus Manager/comprehensive_review.md`.

## Agent Roles

| Role | Best use | Must not do silently |
|---|---|---|
| Codex / GPT-5.4-class local agent | Repo audit, code implementation, tests, reproducibility, panel construction, exact file edits | Change Data, calendar policy, event dates, or headline methods without approval |
| Claude Opus-class reviewer | Hostile method review, code review, paper-claim critique, red-team of interpretations | Become the canonical source for repo facts without local verification |
| Gemini / Deep Research-class agent | External literature discovery, citation trails, current market context, tool documentation | Assert repo-state claims or accept citations without durable source checks |
| Cursor background agents | Bounded implementation on isolated branches with clear file ownership | Touch broad repo surfaces, raw Data, or shared generated outputs without ownership |
| Human project owner | Final portfolio, calendar/fill policy, method-label decisions, citation acceptance, paper claims | Delegate high-impact ambiguity without reviewing evidence |

## Standard Agent Assignment

For each major task:

1. Codex inspects repo state and prepares a concrete implementation plan.
2. Claude/Opus red-teams the plan for method, claim, and code risks.
3. Gemini/Deep Research validates external literature or package choices with durable links.
4. Codex implements scoped changes on the approved files.
5. A separate review pass checks tests, output hashes, method labels, and draft claims.

## Conflict Resolution

When agents disagree:

- Check which claim cites `AGENTS.md`, config, data inventory, source code, or generated output.
- Reject claims based only on another AI memo.
- Preserve minority objections if they identify a plausible fatal flaw.
- Ask the human only for high-impact unresolved decisions, with a recommended default.

## File Ownership Rules

Use disjoint write ownership for parallel agents:

- Paper protocols: `docs/specs/` or `Manager/` only.
- Data curation: `tools/data_curation/` only, never hand-edit `Data/`.
- Panel construction: `src/cqresearch/data/` and tests.
- Modeling: `src/cqresearch/modeling/` and tests.
- Figures: `src/cqresearch/viz/`, `scripts/03_make_figures.py`, and figure tests/visual QA.
- Drafting: `reports/drafts/` or Quarto manuscript folders after approval.

Evidence: `AGENTS.md`; `tools/`; `src/cqresearch/`; `scripts/`; `reports/`.

## Quality Gates

Every handoff must include:

- Inputs read.
- Outputs written.
- Tests/checks run.
- Strongest empirical claims and evidence.
- Known limitations.
- Confidence score.
- Open questions.
- Recommended next agent.

Evidence: `AGENTS.md`.

## Automated Gates To Add Later

Recommended checks:

- `make test`: run unit and integration tests.
- `make lint`: Ruff and formatting.
- `make type`: mypy if kept.
- `make check-config-paths`: verify config paths exist.
- `make check-method-labels`: scan drafts for overclaim terms such as Bai-Perron, Shapley, causal, driver, proved, validated.
- `make check-citations`: reject `turn...` placeholders and require DOI/SSRN/arXiv/journal/official URLs.
- `make check-data-integrity`: ensure no hand-edited `Data/` files outside curation outputs.
- `make check-figures`: verify figure source data, vector/PNG render, dimensions, and label readability.

## Human Approval Gates

Human approval required before:

- Final four-paper selection.
- Calendar/fill policy changes.
- Event-date changes.
- Data curation changes.
- Accepting prior AI citations.
- Upgrading method labels.
- Replacing core figures/tables.
- Broad repo reorganization.

Evidence: `AGENTS.md`.

## Recommended Prompt Contract

Every future manager prompt should require:

- Read `AGENTS.md` first.
- Separate Verified, Inference, and Uncertain.
- Cite repo paths for repo claims.
- Cite durable external URLs for external claims.
- State files read and files written.
- State tests run.
- State what must not be changed without approval.
- Treat prior AI outputs as hypotheses.

## Durable Source-of-Truth Layout

Minimal, not a broad reorg:

- Keep `AGENTS.md` as constitution.
- Keep `Manager/` for independent manager reviews and synthesis.
- Keep `reports/prior_ai_outputs/` quarantined.
- Add per-paper protocol/status files only after human confirms portfolio.
- Keep generated dated outputs under `reports/`.
- Build a metric dictionary and source-overlap registry before expanding models.

