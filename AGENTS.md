# Crypto Market Dynamics - Repository Instructions

## Mission

Maintain a rigorous descriptive and associational crypto research-code
repository explaining market evolution through measurement integrity, macro
co-movement, institutional access, leverage/liquidity state, market structure,
and selected-major risk.

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
- Prefer existing dependencies. Add a production dependency only when it
  materially improves correctness or reproducibility and document the reason.

## Analysis Rules

- Define the research question before selecting a method.
- Use descriptive statistics, correlations, z-scores, regressions, financial risk
  models, tail models, panel models, and sensitivity analysis where appropriate.
- Same-day variables are contemporaneous associations, not lead-lag evidence.
- Same-day MVRV is a measurement-mechanics diagnostic.
- ETF flows are timing-sensitive market-plumbing measures.
- Raw USD TVL and USD-valued OI require price-content audits.
- Monthly PIT data supports monthly state analysis, not daily historical
  constituent returns.
- Use same-support samples for nested model comparisons.
- Report uncertainty, sample, transformation, frequency, and sensitivity.
- Do not add random ML or forecasting work.

## Visualization Rules

- Four to six README figures maximum; replacement beats expansion.
- Figures must be generated from analytical tables.
- Prefer coefficient forests, confidence intervals, rolling betas, quantile
  curves, marginal effects, sensitivity plots, event/placebo plots, and risk
  decompositions.
- No market-share, stacked-composition, decorative, dashboard, AI-image,
  rainbow, 3-D, or dual-axis public charts.
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
- Root README is an index and synthesis, not a report dump.

## Required Verification

```bash
uv sync --all-extras
uv run ruff check src/cqresearch scripts tests
uv run ruff format --check src/cqresearch scripts tests
uv run mypy src/cqresearch
uv run pytest -q
uv run python scripts/run_research.py --module all
uv run python scripts/build_research_figures.py --module all
uv run python scripts/check_research_surface.py
```

When local provider data is available, also run the full local build and verify
determinism, README links, tracked-data policy, clean-worktree behavior, and
visual quality before completion.
