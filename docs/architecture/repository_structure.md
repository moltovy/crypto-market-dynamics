# Repository Structure

The public repository is organized around one canonical product:

```text
README.md
data_local/           ignored local provider exports and generated feature stores
docs/                 public methodology, architecture, data, and decisions
outputs/              canonical reports, figures, tables, model cards, manifest
scripts/              reproducible entry points and legacy-compatible pipelines
src/cqresearch/       reusable Python package
tests/                unit tests
archive/              provenance and historical development artifacts
```

Public readers should start with `README.md` and `outputs/`. Raw provider data
is intentionally absent from the public Git history going forward. Archived
material is retained for provenance and should not be treated as the active
project surface.
