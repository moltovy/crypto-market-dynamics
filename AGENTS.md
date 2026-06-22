# Crypto Market Dynamics - Repository Instructions

## Mission

Maintain a rigorous broad empirical crypto research repository using available
crypto, macro, derivatives, ETF, stablecoin/DeFi, on-chain, chain,
point-in-time, major-asset, and sector data to study price behavior,
cross-asset relationships, liquidity, leverage, market-microstructure proxies,
risk transmission, and market evolution.

## Research Guardrails

- Never forecast prices or claim a trading strategy.
- Never describe association as causation.
- Same-day MVRV is a mechanical valuation-state diagnostic; exclude it from
  primary BTC/ETH models.
- ETF flow analysis is market plumbing with timing/endogeneity caveats.
- Stablecoin/DeFi measures are endogenous state proxies; raw USD TVL is
  valuation-sensitive.
- Monthly point-in-time data supports monthly structure, concentration, turnover,
  and state analysis only.
- Current-cohort daily analysis is survivorship-biased.
- Do not force the project into one research question.
- Report weak/null results as weak; do not specification-shop.
- Public claims require sample, method, uncertainty, evidence grade, source
  artifact, and limitation.

## Repository Rules

- The canonical public research surface is `research/`.
- Each module owns its `README.md`, `methodology.md`, `findings.md`,
  `interpretation.md`, `limitations.md`, `module.yml`, `tables/`, `figures/`,
  and `manifest.json`.
- Do not maintain a competing flat `outputs/` surface after migration.
- Raw/provider data stays local under `data_local/` and outside Git.
- Do not commit provider exports, secrets, caches, machine-specific paths, or
  manager packs.
- Every available series must appear in the data-usage matrix.
- Scripts remain thin entry points; analytical logic lives under
  `src/cqresearch/`.
- Maintain one module registry and one artifact registry.
- Prefer existing dependencies. Add a production dependency only when it
  materially improves correctness or reproducibility and document the reason.

## Analysis Rules

- Define the module question before selecting a method.
- Use multiple assets, not only BTC/ETH.
- Use descriptive statistics, correlation matrices, heatmaps, partial
  correlations, rolling exposure, PCA, HAC models, partial/block R-squared,
  quantile regression, tail logit, z-score states, financial risk metrics,
  panel models, and sensitivity analysis where supported.
- Same-day variables are contemporaneous associations, not lead-lag evidence.
- Same-day MVRV is a measurement-mechanics diagnostic.
- ETF flows are timing-sensitive market-plumbing measures.
- Raw USD TVL and USD-valued OI require price-content audits.
- Monthly PIT data supports monthly state analysis, not daily historical
  constituent returns.
- Use same-support samples for nested model comparisons.
- Report uncertainty, sample, transformation, frequency, and sensitivity.
- Do not add random ML or forecasting work. PCA and hierarchical clustering are
  allowed for dependence/common-factor description.
- Do not estimate order-book microstructure models without order-book,
  trade-level, or quote data.

## Visualization Rules

- Four or five root README figures maximum; replacement beats expansion.
- Figures must be generated from analytical tables.
- Prefer correlation heatmaps, coefficient forests, confidence intervals,
  rolling betas, PCA/factor loadings, quantile curves, marginal effects,
  sensitivity plots, event/placebo plots, and risk decompositions.
- No ETF pre-inception zero fills.
- No raw HHI/rank-persistence, market-share, stacked-composition, decorative,
  dashboard, AI-image, rainbow, 3-D, or dual-axis headline charts.
- No simple volatility/drawdown scatter as a headline selected-major result.
- Use direct labels where practical, explicit units/date range/sample,
  accessible color, and honest uncertainty.
- Bars start at zero. Mark partial periods and unequal coverage visibly.
- Inspect every generated PNG/SVG at full size and README width; file existence
  is not visual QA.

## Writing Rules

- No generic AI language, repeated boilerplate caveats, or public raw snake_case
  table dumps.
- Findings state numbers and uncertainty.
- Interpretation explains economic meaning and alternatives.
- Root README starts with Project Overview, not a single Research Question.
- Every module README embeds and interprets its figures and includes sample,
  method/calculation, formula, result, sensitivity, and provenance tables.

## Required Verification

```bash
uv sync --all-extras
uv run ruff check src/cqresearch scripts tests
uv run ruff format --check src/cqresearch scripts tests
uv run mypy src/cqresearch
uv run pytest -q
uv run python scripts/run_research.py --module all
uv run python scripts/build_research_figures.py --module all
uv run python scripts/check_research_surface.py --module all
```

When local provider data is available, also run the full local build and verify
determinism, README links, tracked-data policy, clean-worktree behavior, and
visual quality before completion.
