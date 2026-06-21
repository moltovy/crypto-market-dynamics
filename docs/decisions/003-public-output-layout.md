# 003: Public Research Layout

## Decision

Expose `research/` as the single canonical public artifact root.

## Rationale

One module-oriented artifact root makes the repository easier to review than a
flat warehouse of generated files.

## Consequence

Public docs and README links point to `research/`. Each module owns its methods,
findings, interpretation, limitations, tables, figures, claims, and manifest.
Private process artifacts and obsolete release packets are excluded from the
public repository surface.
