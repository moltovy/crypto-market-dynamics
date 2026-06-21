# Crypto Market Dynamics - Repository Instructions

## Mission

Maintain a rigorous descriptive research-code repository explaining crypto market
evolution through measurement integrity, macro co-movement, institutional access,
leverage/liquidity state, market structure, and selected-major risk.

## Research Guardrails

- Never forecast prices or claim a trading strategy.
- Never describe association as causation.
- Same-day MVRV is a mechanical valuation-state diagnostic; exclude it from
  primary BTC/ETH models.
- ETF flow analysis is market plumbing with timing/endogeneity caveats.
- Stablecoin/DeFi measures are endogenous state proxies; raw USD TVL is
  valuation-sensitive.
- Monthly point-in-time data supports structure, concentration, and turnover only.
- Current-cohort daily analysis is survivorship-biased.
- Report weak results as weak; do not specification-shop.
- Public claims require sample, method, uncertainty, evidence grade, source
  artifact, and limitation.

## Repository Rules

- One canonical repository surface and output root: `outputs/`.
- No v2, v3, final-final, release-packet, manager, or duplicate output folders.
- Raw/provider data stays local under `data_local/` and outside Git.
- Do not commit provider exports, secrets, caches, machine-specific paths, or this
  manager pack.
- Do not advertise `archive/` on the public surface. Preserve only durable
  architecture decisions under `docs/decisions/`.
- Scripts remain thin entry points; analytical logic lives under `src/cqresearch/`.
- Avoid a large refactor unless it removes verified duplication or isolates a
  tested analytical boundary.
- Prefer existing dependencies. Add a production dependency only when it materially
  improves correctness or reproducibility and document the reason.

## Visualization Rules

- Four to six README figures maximum; replacement beats expansion.
- One analytical message per figure.
- No dashboards, 3-D, gradients, shadows, gauges, donuts, rainbow maps, dense
  legends, spaghetti lines, dual axes, or decorative AI imagery.
- Use direct labels where practical, explicit units/date range/sample, accessible
  color, and honest uncertainty.
- Bars start at zero. Mark partial periods and unequal coverage visibly.
- Inspect rendered images at full size and README width. A generated file is not
  automatically a good figure.

## Required Verification

Run applicable checks after changes:

```bash
uv sync --all-extras
uv run ruff check src/cqresearch scripts tests
uv run ruff format --check src/cqresearch scripts tests
uv run mypy src/cqresearch
uv run pytest -q
uv run python scripts/check_public_surface.py
```

When local provider data is available:

```bash
uv run python scripts/run_all.py
uv run python scripts/build_public_figures.py
uv run pytest -q
uv run python scripts/check_public_surface.py
```

Also verify generated-artifact determinism, README links, tracked-data policy, and
visual quality before completion.
