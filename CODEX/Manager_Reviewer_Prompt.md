# Manager Reviewer Prompt

Use this prompt for independent senior-manager reviews by GPT-5.4 extra-high reasoning, Claude Opus Thinking, and Gemini Pro-class agents. Each agent should work independently first. Their outputs should then be compared, reconciled, and used to choose the four-paper research program and the operating workflow for the repository.

Repository:

`C:\Dev\Projects\CryptoQuant`

## Mission Context

This project is a four-paper empirical-finance / crypto-market data-analysis research program, not a one-paper project.

The goal is to produce:

1. Two papers on how crypto market evolution and dynamics changed before versus after institutionalization, especially the BTC and ETH spot-ETF era.
2. Two papers on specific, timely, niche topics that bridge traditional finance and crypto markets, such as stablecoins, RWA/tokenized assets, DeFi versus CEX structure, DeFi yields, crypto credit/liquidity, ETF flows, institutional market plumbing, or related market-structure topics.

Older repo files may still describe a one-paper goal. Treat that as stale historical context unless validated by the current `AGENTS.md`. `AGENTS.md` is now the controlling source of truth.

The current strongest candidate for one institutionalization paper is BTC/ETH factor-exposure evolution around ETF institutionalization. That is a candidate anchor, not the entire project.

## Your Role

You are acting as a skeptical principal research engineer, quantitative finance reviewer, empirical-finance project manager, and execution-focused codebase auditor.

Produce decision-quality guidance for the next stage of the project. Be evidence-first, conservative, precise, and professionally demanding. Treat repository reality, data inventory, generated outputs, specs, older context docs, prior AI outputs, and external references as separate evidence classes. Do not merge them blindly.

Your answer should help the project owner decide:

- which four paper directions are most defensible,
- how to handle the large mixed-frequency data inventory,
- whether a maximum-inventory paper/project is feasible,
- which existing outputs and prior AI work should be trusted or distrusted,
- what repo/workflow changes are needed,
- how to use multiple frontier LLM agents and tools professionally across the entire working directory.

## Operating Rules

1. Inspect repository reality before making claims.
2. Do not treat earlier AI-generated files as canonical unless validated by code, data inventory, generated reports, or current project goals.
3. Do not invent citations.
4. Distinguish `Verified`, `Inference`, and `Uncertain` findings.
5. Cite concrete repository paths for every major claim.
6. If you are unsure about a material decision, ask the human, but also state your own recommended decision and why.
7. You may recommend web search when it is necessary to verify current literature, tool choices, package capabilities, model/agent tooling, or market context. Repository evidence remains primary for repo-state claims.
8. Do not change files. This is a review, planning, and management task.
9. Be willing to challenge existing architecture, methods, visuals, prompts, and workflow. Do not preserve a weak approach just because it already exists.
10. Do not assume Python/matplotlib is optimal. Recommend better packages, languages, extensions, or report systems if they materially improve econometric correctness, visualization quality, reproducibility, or autonomous-agent reliability.

## Evidence Hierarchy

When sources conflict, use this precedence:

1. `AGENTS.md`
2. `config/*.yml`
3. `Data/MASTER_DATA.md` and `Data/MASTER_DATA.csv`
4. `src/cqresearch/` and `scripts/`
5. `reports/run_summaries/`, `reports/tables/`, `reports/figures/`, `reports/panels/`
6. `CODEX/current_status_analysis.md`, `CODEX/data_analysis.md`, this prompt, and any other `CODEX/` audit outputs
7. `docs/specs/`
8. `project_research_plan.md`
9. `docs/context/`
10. `docs/manager/`
11. `reports/prior_ai_outputs/`
12. `Latest Output.txt`
13. `references/`

Prior AI outputs are hypotheses and planning inputs, not authority. Generated reports and tables are evidence of what the pipeline produced, not proof that the interpretation is correct.

## Required Read Set

Read at least:

- `AGENTS.md`
- `CODEX/current_status_analysis.md`
- `CODEX/data_analysis.md`
- `CODEX/Manager_Reviewer_Prompt.md`
- `project_research_plan.md`
- `README.md`
- `HANDOFF.md`
- `pyproject.toml`
- `run_pipeline.py`
- `.cursor/rules/*.mdc`
- `config/factor_blocks.yml`
- `config/events.yml`
- `config/calendars.yml`
- `config/chain_taxonomy.yml`
- `Data/MASTER_DATA.md`
- `Data/MASTER_DATA.csv`
- `docs/context/*.md`
- `docs/manager/Manager_Outline.md`
- `docs/manager/Manager_workflow.md`
- `docs/specs/*.md`
- `src/cqresearch/`
- `scripts/`
- `tests/`
- `reports/run_summaries/`
- `reports/tables/2026-04-18/`
- `reports/figures/2026-04-18/`
- `reports/drafts/paper_v0.1_2026-04-18.md`
- `reports/prior_ai_outputs/`
- `Latest Output.txt`
- material files under `references/`

Review the `CODEX/` outputs themselves. Evaluate whether `current_status_analysis.md` and `data_analysis.md` are accurate, incomplete, biased, too conservative, too aggressive, or missing important repo evidence. Correct their conclusions in your own report if needed.

## Core Management Problem

The repository contains many data sources, variables, frequencies, and overlapping vendor metrics. This is not a small implementation detail; it is one of the central project-management problems.

The project owner is explicitly unsure how to handle:

- daily 24/7 crypto data,
- business-day TradFi data,
- weekly series,
- monthly series,
- one-time snapshots,
- stale or missing vendor metadata,
- overlapping sources with similar metric names,
- different coverage windows,
- forward-fill and zero-fill decisions,
- release lags and look-ahead risk,
- high-dimensional factor sets,
- whether to use most of the inventory in one project or distribute variables across multiple papers.

Give professional guidance. Explain what industry/research best practice suggests and what should be done in this repository.

## Required Analysis

### 1. Repository Reality

Describe what the repository actually contains today. Do not summarize intended architecture only.

Identify:

- active source modules,
- active execution scripts,
- configs,
- generated outputs,
- tests,
- data inventory,
- draft papers,
- prior AI outputs,
- `CODEX/` audit outputs,
- workflow references.

State what is real, stale, aspirational, contradicted, or missing.

### 2. Four-Paper Research Portfolio

Identify the top six viable paper/project directions supported by the current repository and data.

For each direction, report:

- title,
- one-sentence thesis,
- paper category: institutionalization / market-evolution / non-ETF bridge / data-atlas or platform,
- required data sources,
- required frequency/calendar design,
- current repo support,
- required new methods or tooling,
- biggest blocker,
- publication risk,
- estimated lift from current repo state,
- whether it aligns with `AGENTS.md`.

Then select the recommended four-paper portfolio:

- top two institutionalization / market-evolution papers,
- top two non-ETF or ETF-adjacent TradFi/crypto bridge papers.

For each selected paper, explain:

- why it belongs in the final portfolio,
- what unique question it answers,
- why it is not redundant with the other three papers,
- what the minimum viable empirical design is,
- what tables/figures would make it credible,
- what data/method risks could kill it.

### 3. Maximum-Inventory Paper / Project Feasibility

Evaluate seriously whether one paper/project should be designed to use as much of the data inventory as is defensible.

Possible framing:

> A broad map of crypto-market structure across macro, ETF, stablecoin, RWA, DeFi, CEX, derivatives, liquidity, and native-chain metrics.

Do not assume this is feasible or desirable.

Decide whether it should be:

- a standalone paper,
- a data atlas,
- a dashboard/exploratory platform,
- an appendix supporting all four papers,
- a shared factor-library/panel-construction project,
- or rejected as too broad/kitchen-sink.

Evaluate appropriate methods:

- PCA,
- dynamic factor models,
- clustering,
- sparse regression / LASSO / elastic net,
- partial least squares,
- Bayesian shrinkage,
- boosted-tree importance as support only,
- network/connectedness methods,
- dimensionality reduction by economic block,
- pre-registered factor-block screens.

Explain how to avoid overfitting, p-hacking, multiple-testing problems, and narrative fishing.

### 4. Current ETF / Institutionalization Work

Review the current ETF/factor-exposure paper direction as if you were a hostile but fair empirical-finance referee.

Evaluate:

- research question clarity,
- whether it should be Paper 1 or one of several institutionalization papers,
- data quality,
- source coverage,
- variable construction,
- calendar/fill handling,
- sample windows,
- econometric identification,
- rolling OLS diagnostics,
- block partial R2 claims,
- Chow and break-test evidence,
- VAR/FEVD design,
- event-study design,
- robustness coverage,
- visual quality,
- citation discipline,
- reproducibility.

Be explicit about where the paper currently overclaims and what must change before it can be credible.

### 5. Mixed-Frequency and Calendar Strategy

Give a professional data-design recommendation for:

- 24/7 crypto daily data versus business-day TradFi data,
- calendar-day panels versus business-day panels,
- weekend and holiday handling,
- forward-fill limits,
- zero-fill policies for ETF flows or missing reports,
- artificial returns created by fills,
- weekly and monthly aggregation,
- downsampling versus imputation,
- snapshot metrics,
- release lags and look-ahead risk,
- sample-window selection,
- paper-specific panels from a shared inventory,
- source precedence and vendor reconciliation.

Do not only list options. Make recommended decisions and explain tradeoffs.

### 6. Data and Metric Overlap Review

Use `Data/MASTER_DATA.md`, `Data/MASTER_DATA.csv`, and representative source files to identify overlapping metric categories across vendors.

At minimum evaluate:

- ETF flows across Farside, DefiLlama, and Artemis,
- ETF AUM across Artemis files,
- stablecoin supply across Artemis and DefiLlama,
- TVL across DefiLlama and Artemis,
- dollar index / USD strength across FRED and TradingView,
- ETH market cap across Artemis and CryptoQuant,
- open interest,
- fees,
- active addresses,
- exchange-flow categories,
- RWA/tokenized asset metrics,
- DeFi yields or lending metrics if present,
- CEX/DeFi structure metrics if present.

For each category, classify whether sources are:

- exact duplicates after unit conversion,
- near-duplicates,
- related but definitionally different,
- different concepts despite similar names,
- not comparable without additional metadata.

Recommend the primary source and robustness source for each category.

### 7. High-Dimensional Inventory Strategy

The project owner wants to use the inventory intelligently, not blindly.

Evaluate:

- which metric categories are likely useful,
- which are redundant,
- which are noisy,
- which are too sparse,
- which are irrelevant,
- which belong in main regressions,
- which belong in robustness,
- which belong in descriptive sections,
- which belong in appendices or a dashboard,
- which should be reserved for future papers.

Recommend a practical variable-selection framework:

- economic block first,
- source precedence second,
- missingness/coverage third,
- frequency compatibility fourth,
- statistical screening last.

If you recommend ML/statistical screening, keep it subordinate to economic design.

### 8. Prior AI Output Review

Review prior AI outputs separately. Do not merge them into one narrative.

Classify each material prior output as:

- high-value synthesis,
- useful but stale,
- speculative,
- citation-risk,
- low-authority,
- misleading.

Explain what should be salvaged and what should be ignored.

Pay special attention to:

- `reports/prior_ai_outputs/FINAL_SYNTHESIS_TOP5_PROJECTS.md`
- `reports/prior_ai_outputs/research_memo.md`
- `reports/prior_ai_outputs/deep-research-report.md`
- `reports/prior_ai_outputs/Beyond Correlation_ Quantifying Bitcoin's New Role in Financial Markets Through Structural Breaks, Flow Dynamics, and Systemic Risk.md`
- `reports/prior_ai_outputs/txt output p2.md`
- `reports/prior_ai_outputs/txt output.md`
- `Latest Output.txt`
- `CODEX/current_status_analysis.md`
- `CODEX/data_analysis.md`

### 9. Tooling, Packages, Languages, and Report System

Evaluate whether the current stack is sufficient.

Consider:

- Python/pandas versus Polars or DuckDB for data work,
- matplotlib/seaborn versus plotnine, Altair, Plotly, ggplot2, or other visualization systems,
- Python econometrics versus R packages for structural breaks, VARs, panel models, robust inference, and publication tables,
- Quarto, LaTeX, Typst, or another reproducible paper/report system,
- notebook versus script versus pipeline tradeoffs,
- whether `uv`, Make, nox, pytest, pre-commit, nbstripout, or hooks are sufficient,
- whether MCP servers, Codex skills, Cursor rules, browser/visual QA, citation tools, or local scripts should be added.

For every recommended new package/tool/language, state:

- what weakness it fixes,
- why current tools are insufficient,
- reproducibility cost,
- dependency/onboarding cost,
- implementation risk,
- verification plan.

Be willing to recommend leaving the current stack unchanged if that is the best professional decision.

### 10. Multi-LLM / Autonomous-Agent Operating Model

The project owner plans to leverage multiple frontier LLM systems heavily across the entire working directory and project scope, including GPT-5.4 extra-high reasoning, Claude Opus Thinking, and Gemini Pro-class agents.

Design a professional multi-agent operating model.

Address:

- which agent/model should do which kinds of work,
- how to split exploration, implementation, econometric review, visualization review, citation review, and red-team review,
- when agents should work independently versus sequentially,
- how to reconcile conflicting agent outputs,
- how to prevent stale-plan drift,
- how to prevent hallucinated citations,
- how to avoid agents overwriting each other's work,
- how to maintain source-of-truth docs,
- how to use `AGENTS.md`, prompts, rules, skills, MCP tools, browser/search, and local scripts,
- what should be automated with hooks or quality gates,
- what should always require human approval.

Assume the goal is to use LLMs for everything they can safely and effectively do in this project: repo auditing, data inventory reasoning, methods design, code implementation, statistical review, visual polish, paper drafting, citation checks, project management, and final synthesis.

Do not assume LLMs should make every decision silently. For ambiguous high-impact choices, state your recommended decision and ask the human to confirm.

### 11. Workflow, Prompts, Rules, and Repo Structure

Evaluate:

- whether `AGENTS.md` and `.cursor/rules/` are consistent,
- whether `CODEX/` should become a durable audit/handoff folder or be renamed,
- whether prompt files under `prompts/` are usable and role-specific,
- whether `docs/manager/` still reflects current repo state,
- whether `docs/specs/` are enforceable or still skeletal,
- whether `references/` provides useful workflow or method patterns,
- whether subagents should be used and how,
- what quality gates should be automated,
- where the current workflow permits hallucination or stale-plan drift.

Recommend a practical repo/workflow structure for autonomous, high-quality project exploration.

Address:

- canonical pipeline entry point,
- config ownership,
- paper/project folder structure,
- report/output versioning,
- draft-paper versioning,
- prior-output quarantine,
- data curation boundaries,
- test suite expansion,
- agent handoff files,
- citation verification workflow,
- visual QA workflow,
- reproducibility checklist.

Do not propose a large reorg unless it removes real confusion.

### 12. Decision Requests for the Human

If you need human input, ask targeted questions.

For every question:

- explain why it matters,
- give your recommended default,
- state what you would do if the human does not answer,
- state the risk of the default.

Do not stop at questions. Provide your own best professional recommendation based on repository evidence, web/literature/tool research where appropriate, and the current project goals.

## Required Output Format

Produce a Markdown report with this structure:

1. `Executive Judgment`
2. `Evidence Reviewed`
3. `Repository Reality`
4. `Assessment of CODEX Audit Files`
5. `Top 6 Paper / Project Directions`
6. `Recommended Four-Paper Portfolio`
7. `Maximum-Inventory Project Feasibility`
8. `Current ETF / Institutionalization Paper Review`
9. `Mixed-Frequency and Calendar Strategy`
10. `Data Overlap and Source Recommendation`
11. `High-Dimensional Inventory Strategy`
12. `Prior AI Output Review`
13. `Tooling / Packages / Language Recommendations`
14. `Multi-LLM Operating Model`
15. `Workflow / Prompts / Rules / Repo Structure`
16. `Highest-Priority Fixes`
17. `Human Decisions Needed`
18. `Open Questions`
19. `Confidence and Limits`

Every major claim must cite a repository path. Use concise citations like:

`Evidence: config/events.yml; reports/run_summaries/03_run_analyses.md`

If web search or external documentation is used, cite durable external sources separately and clearly distinguish them from repository evidence.

## Quality Bar

Be demanding. A useful answer should tell the project owner:

- what is actually true in the repo,
- what is probably true but not yet proven,
- what previous AI work should be distrusted,
- what `CODEX/` audit claims should be accepted or corrected,
- which four papers should be pursued,
- whether a maximum-inventory project is feasible,
- how to professionally handle mixed frequencies and calendars,
- how to use the large data inventory without creating a kitchen-sink paper,
- what tooling should change,
- how GPT-5.4, Opus, Gemini, Codex, skills, MCP tools, web search, and local scripts should be used together,
- what engineering changes are required before papers can be trusted,
- how to structure future autonomous exploration without hallucination, stale plans, or low-quality outputs.

Do not write motivational prose. Do not flatter prior work. Do not hide contradictions. Make decisions where evidence supports them, and ask the human only for high-impact choices that cannot be resolved from the repository or external verification.
