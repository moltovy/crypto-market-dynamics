# Repository Structure

The public repository is organized around one canonical product:

```text
README.md
Data/                 frozen source-data tree
docs/                 public methodology, architecture, data, and decisions
outputs/              canonical reports, figures, tables, model cards, manifest
scripts/              reproducible entry points and legacy-compatible pipelines
src/cqresearch/       reusable Python package
tests/                unit tests
archive/              provenance and historical development artifacts
```

Public readers should start with `README.md` and `outputs/`. Archived material
is retained for provenance and should not be treated as the active project
surface.
