# Reorganization Summary

## What Changed

The repository was consolidated from a release-history layout into one clean
public project:

- `outputs/` is the canonical public artifact packet.
- `docs/` contains concise methodology, architecture, data, and decision docs.
- `archive/` retains internal manager notes, historical release packets, old
  drafts, career-oriented material, and release-process documents.
- `reports/` keeps compatibility generated tables, figures, and panel metadata
  used by legacy scripts.

## Public Structure

```text
README.md
Data/
docs/
outputs/
scripts/
src/cqresearch/
tests/
archive/
```

## Guardrails

- Raw `Data/` files are not modified by the canonical export path.
- ETF-flow outputs remain reduced-form diagnostics, not causal claims.
- Stablecoin and TVL outputs remain liquidity proxies.
- Structural-break diagnostics remain Chow plus single-break sup-F, not full
  Bai-Perron.
- Advanced attribution is labeled separately from block partial R2.

## Verification

- `uv run pytest` -> PASS, 43 passed.
- `uv run mypy src/cqresearch` -> PASS, no issues in 37 source files.
- `uv run python scripts/run_all.py` -> PASS, exported canonical outputs.
- `uv run ruff check src/cqresearch scripts tests` -> DOCUMENTED LEGACY FAIL,
  79 findings across older scripts/core/test files and legacy style rules.
- Focused Ruff on maintained public/portfolio paths -> PASS.
- Markdown link audit across public docs and outputs -> PASS.
- Public-surface scan for old release/career language -> PASS.
- `git status --short -- Data` -> PASS, no output.
