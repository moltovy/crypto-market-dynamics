# 003: Public Output Layout

## Decision

Expose `outputs/` as the single canonical public artifact root.

## Rationale

One artifact root makes the repository easier to review than multiple historical
release folders.

## Consequence

Public docs and README links point to `outputs/`. Private process artifacts and
obsolete release packets are excluded from the public repository surface.
