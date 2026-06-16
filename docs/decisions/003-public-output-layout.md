# 003: Public Output Layout

## Decision

Expose `outputs/` as the single canonical public artifact root.

## Rationale

One artifact root makes the repository easier to review than multiple historical
release folders.

## Consequence

Historical release packets are retained under `archive/`, while public docs and
README links point to `outputs/`.
