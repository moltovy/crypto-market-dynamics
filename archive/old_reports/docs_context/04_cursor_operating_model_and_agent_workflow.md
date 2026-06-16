# Cursor Operating Model and Agent Workflow

## Goal
Use frontier models inside Cursor Pro as a disciplined research-and-engineering team, not as random coders.

## Recommended High-Level Setup
One model should act as the lead project manager / implementation owner.
A second model should act as the critical reviewer / alternate implementation partner.
Grok 4.20 should be used as a workflow strategist and meta-advisor.

## Suggested Role Split

### Option A: GPT-5.4 Extra High as Lead
Best for:
- long-horizon implementation
- repo-wide reasoning
- tool use
- multi-file orchestration
- handling complex agent tasks over long context windows

### Option B: Claude Opus 4.6 as Lead
Best for:
- careful reasoning
- code review
- debugging and self-correction
- large codebase understanding
- specification critique and refinement

### Reviewer / Counterparty Model
Use the non-lead frontier model as:
- refactor reviewer
- methodological critic
- code auditor
- alternative implementation checker

## Core Operating Principle
Do not let one agent improvise the project structure from scratch every time.
Instead provide:
- a clear repo structure
- project rules
- named roles
- acceptance criteria
- artifact requirements
- explicit deliverables for each step

## Recommended Workflow in Cursor

### Phase 1: Project Definition
Use Ask / planning mode to refine:
- research question
- factor blocks
- main sample windows
- core methods
- output figures / tables

### Phase 2: Data Lake Construction
Agent builds raw archival ingestion pipelines for:
- CryptoQuant
- DefiLlama
- Massive / Polygon
- Farside
- FRED
- Dune if used

### Phase 3: Analytical Panels
Agent creates curated datasets:
- daily core panel
- weekly robustness panel
- monthly slow-variable panel
- BTC-only long-history panel
- BTC/ETH common-sample panel

### Phase 4: Baseline Methods
Agent implements:
- descriptive notebooks / scripts
- rolling correlations
- static OLS with HAC errors
- rolling OLS
- partial R^2 by factor block
- structural break tests

### Phase 5: Dynamic Systems
Agent implements:
- VAR / Granger / FEVD
- connectedness analysis
- event studies
- volatility modules

### Phase 6: Support Analytics
Agent implements only after core econometrics is stable:
- PCA / sparse PCA
- clustering / regime classification
- variable screening / nonlinear diagnostics

### Phase 7: Reporting Artifacts
Agent produces:
- tables
- figures
- data dictionaries
- run logs
- assumptions notes
- result summaries for paper drafting

## Engineering Standards
- deterministic scripts
- environment variables for secrets
- reproducible run commands
- clear folder structure
- separate raw vs cleaned vs analysis outputs
- inventory files for datasets
- tests for critical transformations where practical
- no silent data loss

## Repo / Folder Concepts
- raw data
- processed data
- intermediate analytical panels
- notebooks or scripts for each method family
- figures
- tables
- docs / planning notes
- prompts / specs / rules

## Agent Management Rules
- every major task should have explicit acceptance criteria
- every analytical module should write outputs to file, not just chat back prose
- every result promoted to the paper should survive a reviewer-model pass
- competing implementations are useful for convergence checking
- keep the paper logic simple even if the exploration layer is broad
