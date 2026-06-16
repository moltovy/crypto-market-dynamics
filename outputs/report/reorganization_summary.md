# Reorganization Summary

## What Changed

The repository was consolidated from a release-history layout into one clean public project:

- `outputs/` is the canonical public artifact packet.
- `docs/` contains concise methodology, architecture, data, and decision docs.
- `archive/` retains internal manager notes, historical release packets, old drafts, and release-process documents.
- `reports/` keeps compatibility generated tables, figures, and panel metadata used by legacy scripts.

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
- Structural-break diagnostics remain Chow plus single-break sup-F, not full Bai-Perron.
- Advanced attribution is labeled separately from block partial R2.
- The new Feature Strength & Regime Analysis tables (T11-T27) and figures (F01-F08) are fully integrated into the public analytical surface.
