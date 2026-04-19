# AGENTS.md - CryptoQuant Research Operating Constitution

This file is the single source of truth for any human or LLM agent working on this project. Read this file before making any edit, review, analysis, or plan.

This project is a research program, not a single-paper repo. Older files may still describe a one-paper goal; treat that language as historical until those files are updated.

---

## 1. Mission

Produce four defensible empirical-finance / crypto-market data-analysis papers:

1. Two papers on how crypto market evolution and dynamics changed before versus after institutionalization, especially the BTC and ETH spot-ETF era.
2. Two papers on specific, timely, niche topics that bridge traditional finance and crypto markets, such as stablecoins, RWA/tokenized assets, DeFi versus CEX structure, DeFi yields, crypto credit/liquidity, ETF flows, or institutional market plumbing.

Each paper must be evidence-grounded, reproducible from repository data/code, conservative about causal claims, and suitable for skeptical finance/data reviewers.

The current strongest candidate for Paper 1 remains BTC/ETH factor-exposure evolution around ETF institutionalization. This is a candidate anchor, not a constraint that prevents the other three papers.

---

## 2. Portfolio Requirements

The final research portfolio must include:

- Two institutionalization / market-evolution papers.
- Two non-ETF or ETF-adjacent niche papers that connect crypto markets to traditional finance.
- At least one paper that uses the repository's deep CryptoQuant BTC/ETH-native data.
- At least one paper that uses cross-vendor overlap checks across Farside, DefiLlama, Artemis, FRED, TradingView, or CryptoQuant.
- Clear separation between exploratory diagnostics, publishable tables/figures, and final paper claims.

Project selection criteria, in order:

1. Data quality and source coverage.
2. Defensible empirical design.
3. Relevance to current market structure.
4. Novelty relative to generic ETF/crypto narratives.
5. Feasibility with existing repo data and code.
6. Ability to survive hostile review.

---

## 3. Non-Goals

- Do not build trading strategies.
- Do not make return-prediction or alpha-generation the headline.
- Do not treat machine learning as a headline method. ML is allowed only for support diagnostics such as LASSO screening or boosted-tree importance.
- Do not hand-edit files under `Data/`; data changes must go through the curation pipeline under `tools/`.
- Do not invent citations or reuse unverified citations from prior AI outputs.
- Do not overclaim causality from observational regressions, event studies, rolling models, VARs, FEVDs, or break tests.

---

## 4. Evidence Hierarchy

When sources conflict, use this precedence:

1. `AGENTS.md`
2. `config/*.yml`
3. `Data/MASTER_DATA.md` and `Data/MASTER_DATA.csv`
4. `src/cqresearch/` and `scripts/`
5. `reports/run_summaries/`, `reports/tables/`, `reports/figures/`, `reports/panels/`
6. `CODEX/current_status_analysis.md`, `CODEX/data_analysis.md`, and other new audit outputs
7. `docs/specs/`
8. `project_research_plan.md`
9. `docs/context/`
10. `docs/manager/`
11. `reports/prior_ai_outputs/`
12. `Latest Output.txt`
13. `references/`

Prior AI outputs are hypotheses and planning inputs, not authority. Generated reports and tables are evidence of what the pipeline produced, not proof that the interpretation is correct.

---

## 5. Required Reads

For every substantial research, review, or implementation session, read the relevant subset of these files before acting:

1. `AGENTS.md`
2. `Data/MASTER_DATA.md` and/or `Data/MASTER_DATA.csv`
3. `config/factor_blocks.yml`
4. `config/events.yml`
5. `config/calendars.yml`
6. `config/chain_taxonomy.yml`
7. `CODEX/current_status_analysis.md`
8. `CODEX/data_analysis.md`
9. `CODEX/Manager_Reviewer_Prompt.md`
10. `project_research_plan.md`
11. `docs/context/`
12. `docs/manager/Manager_Outline.md`
13. `docs/manager/Manager_workflow.md`
14. `docs/specs/`
15. `.cursor/rules/`

For code or output work, also inspect the relevant files under:

- `src/cqresearch/`
- `scripts/`
- `reports/run_summaries/`
- `reports/tables/`
- `reports/figures/`
- `reports/drafts/`

---

## 6. Claim Discipline

## Empirical Claim Discipline

Every claim about data coverage, coefficients, results, figures, methods, or paper conclusions must cite a repository path.

Use confidence labels:
- Verified: directly supported by repo file, generated table, code, or data inventory.
- Inference: reasoned from evidence but not directly proven.
- Uncertain: requires additional validation.

Do not convert inference into fact.
Do not use narrative language such as "caused", "proved", "validated", or "confirmed" unless the method supports it.

---

## Method Label Accuracy

Do not call a method by a stronger name than the implementation supports.

Examples:
- Single unknown-break sup-F is not full Bai-Perron multiple-break evidence.
- Standalone block R2 is not Shapley/Owen partial R2.
- Flow divided by price is not flow divided by market cap.
- Diagnostic figures are not publication-ready figures unless visually reviewed.

---

## 7. Method Label Accuracy

Do not call a method by a stronger name than the implementation supports.

Examples:

- Single unknown-break sup-F is not full Bai-Perron multiple-break evidence.
- Standalone block R2 is not Shapley/Owen partial R2.
- Flow divided by price is not flow divided by market cap.
- A diagnostic figure is not publication-ready unless visually reviewed.
- A high correlation between vendor series does not make them interchangeable unless units, coverage, and definitions match.

If method language in a draft conflicts with implementation, fix the language or flag the implementation gap.

---

## 8. Prior AI Output Handling

Files under `reports/prior_ai_outputs/` and `Latest Output.txt` must be reviewed skeptically.

Rules:

- Do not treat repeated AI suggestions as evidence.
- Do not reuse external citations from prior AI outputs until verified through durable links, DOI, journal pages, SSRN, arXiv, or trusted source pages.
- The memos `Beyond Correlation_ Quantifying Bitcoin's New Role in Financial Markets Through Structural Breaks, Flow Dynamics, and Systemic Risk.md` and `deep-research-report.md` contain citation-risk material; do not reuse their 2025-2026 arXiv claims without verification.
- Treat `txt output p2.md` as low-authority unless a claim is independently validated against repository data.
- Treat `Latest Output.txt` as an untracked prior operator memo unless its claims are validated against tracked files and generated outputs.

---

## 9. Data Integrity

- `Data/` is governed by the curation pipeline at `tools/`.
- Do not hand-edit CSVs.
- `Data/_meta/curation_log.md` is append-only.
- `Data/MASTER_DATA.{md,txt,csv}` is machine-generated by `tools/data_curation/06_build_inventory.py`; never hand-edit it.
- Any data change must be reproducible via `make curate`.
- When comparing overlapping vendor metrics, document units, coverage window, frequency, missingness, construction, and source-precedence choice.

---

## 10. Agent Workflow

For audits and research-direction work:

1. Inspect repository reality before synthesizing.
2. Separate actual repo files, data inventory, generated outputs, manager/context docs, prior AI outputs, and external references.
3. Identify contradictions explicitly.
4. Rank project directions by data quality, relevance, novelty, feasibility, and defensibility.
5. Distinguish ETF/institutionalization projects from non-ETF bridge projects.
6. End with a quality gate.

For multi-LLM management reviews:

1. Use independent frontier-model passes where useful, especially GPT-5.4 extra-high reasoning, Claude Opus Thinking, and Gemini Pro-class agents.
2. Give each agent the same repository-grounded prompt and require evidence citations.
3. Compare outputs for convergence, contradictions, omissions, and unsupported claims.
4. Use the strongest arguments from each agent; do not average weak recommendations.
5. If agents disagree on a high-impact decision, ask the human while also giving a recommended default.
6. Use web search or official documentation when current literature, package capabilities, model/tool behavior, or market context materially affects a decision.

For implementation work:

1. Read relevant code and outputs first.
2. Keep edits scoped.
3. Do not modify unrelated files.
4. Prefer config-driven behavior over hardcoded research choices.
5. Add or update tests when changing methods, data construction, or public interfaces.
6. Verify outputs after changes.

---

## Research Execution Protocol

For audits, reviews, paper edits, and analysis plans:

1. Inspect repo reality before synthesizing.
2. Separate actual files, generated outputs, prior AI outputs, and intended specs.
3. Identify contradictions explicitly.
4. Prefer conservative interpretations.
5. End with quality gates: inputs read, outputs written, tests/checks run, confidence, open questions, next agent.

---

## Stop And Ask

Stop and ask before:
- changing pre-registered event dates,
- deleting or replacing core figures/tables,
- changing Data/ outside tools/,
- moving from descriptive evidence to causal claims,
- accepting unverified external citations,
- changing calendar/fill policy,
- changing the headline paper direction.


---

## 11. Quality Gates

Every handoff must include:

1. Inputs read - list file paths.
2. Outputs written - list file paths, row counts where relevant, and hashes for durable artifacts.
3. Claims made - identify the strongest empirical claims and their evidence.
4. Confidence score - 0-100% with supporting evidence.
5. Open questions - concrete blockers or unresolved choices.
6. Next agent - explicitly name the recommended next reviewer or builder role.

---

## 12. Citation Discipline

- Every empirical claim must cite a repository path in `reports/`, `Data/`, `docs/`, `config/`, `src/`, `scripts/`, or `CODEX/`.
- Every external citation must have a verified DOI, arXiv page, SSRN page, journal page, official documentation page, or durable source URL.
- Do not cite broken `turn...` placeholders from prior AI outputs.
- Do not cite unverified 2025-2026 arXiv IDs from prior AI outputs.
- Keep a clear distinction between literature claims, data claims, code claims, and interpretation.

---

## 13. Defensive Commits

- Checkpoint with a commit before any multi-file edit.
- Target three or fewer files per commit where feasible.
- Interface-freeze new modules after one consumer exists.
- Commit message style: `<type>(<scope>): <summary>` where `<type>` is one of `feat`, `fix`, `chore`, `refactor`, `docs`, `test`, or `reorg`.

---

## 14. Environment

- Python 3.11+ is the intended project standard.
- Dependencies are managed by `uv`.
- All dependencies belong in `pyproject.toml`; lockfile is `uv.lock`.
- Never commit `.env`; use `.env.example`.
- Notebooks use the `_template.ipynb` header-cell convention enforced by `nbstripout` and `.cursor/rules/04-notebook-hygiene.mdc`.

If the active interpreter, `pyproject.toml`, lockfile, or docs disagree about the Python version, flag it before changing dependencies.

---

## 15. Escalation

Stop and ask the human before:

- changing the four-paper portfolio goal,
- selecting the final four papers,
- changing pre-registered event dates,
- deleting or replacing core figures/tables,
- modifying `Data/` outside the curation pipeline,
- accepting prior AI citations into drafts,
- changing calendar/fill policy,
- changing headline method labels,
- turning exploratory diagnostics into final paper claims,
- making broad repo reorganizations.

---

## 16. Immediate Next Step

The next planned step is to give `CODEX/Manager_Reviewer_Prompt.md` to independent GPT-5.4 extra-high reasoning, Claude Opus Thinking, and Gemini Pro-class agents.

Those agents should:

- analyze the repository independently,
- identify the top six viable paper directions,
- select the top two institutionalization / market-evolution papers,
- select the top two non-ETF bridge papers,
- review the `CODEX/` audit files themselves,
- evaluate whether a maximum-inventory paper/project is feasible,
- propose a mixed-frequency and calendar strategy,
- evaluate workflow, agent, prompt, and repo structure,
- review `references/` only as workflow/method guidance, not empirical evidence,
- produce evidence-grounded recommendations with confidence labels.
