# Repository Reorganization Audit

## Baseline

- Branch: `main`
- Starting HEAD: `70bab5c`
- Local prompt handling: `Instructions P3.md` is excluded through
  `.git/info/exclude` and is not part of the repository.
- `Data/` check: `git status --short -- Data` returned no output.

## Current Top-Level Folders

- Public/code folders: `.github/`, `config/`, `Data/`, `docs/`, `scripts/`,
  `src/`, `tests/`, `tools/`, `notebooks/`, `optional_data/`.
- Generated/report folders: `reports/`, including dated figures/tables,
  panels, portfolio release packets, showcase docs, optional-data notes, and
  release-process documents.
- Internal/provenance folders: `Manager/`, `prompts/`, old report drafts, prior
  AI outputs, and legacy specs.

## Public-Facing Clutter

- Root README currently exposes release history through `portfolio_v2`,
  `portfolio_v2_1`, `portfolio_v2_2`, showcase docs, release notes, PR docs,
  and manual push instructions.
- `reports/artifact_index.md` maps internal release packets instead of one
  canonical public artifact root.
- `reports/portfolio_showcase/` contains job/career-oriented drafts that should
  not be public navigation.
- `Manager/` contains agent-manager notes and planning outputs that are useful
  provenance but not public product.
- `docs/specs/` mixes active methods with legacy paper-oriented specs.

## Files To Keep Public

- `README.md` as the single public landing page.
- `Data/` as the frozen source-data root, unchanged.
- `data/catalog/` as a clean catalog pointer into `Data/`.
- `outputs/` as the canonical public artifact packet.
- `docs/methodology/`, `docs/architecture/`, `docs/data/`, and
  `docs/decisions/` as concise public documentation.
- `src/`, `scripts/`, `tests/`, `config/`, `.github/`, `Makefile`,
  `pyproject.toml`, and `uv.lock`.

## Files To Archive

- `Manager/` -> `archive/manager_notes/`.
- `reports/portfolio_v2/`, `reports/portfolio_v2_1/`,
  `reports/portfolio_v2_2/` -> `archive/legacy_portfolio_releases/`.
- `reports/portfolio_showcase/` -> `archive/showcase_drafts/`, with career
  files moved to `archive/career_materials/`.
- Release/PR/manual-process docs under `reports/` ->
  `archive/release_process/`.
- Legacy specs from `docs/specs/` -> `archive/legacy_specs/`.
- Old report drafts, prior AI outputs, deep research, appendix, and dated
  report material not needed as canonical outputs -> `archive/old_reports/`
  where safe.

## Files To Keep In Place For Compatibility

- `reports/panels/`, `reports/tables/`, and `reports/figures/` may remain
  because active scripts and tests can rely on these generated-output paths.
- Existing `run_portfolio_*` scripts may remain for compatibility, but public
  README commands should point to canonical wrappers.

## Canonical Public Output Plan

- `outputs/report/`: executive summary, technical report, methodology,
  data atlas, limitations, and reorganization summary.
- `outputs/figures/`: eight canonical figures renamed from the strongest
  existing generated figures.
- `outputs/tables/`: ten canonical CSV tables copied from existing generated
  outputs.
- `outputs/model_cards/`: canonical model cards without release-version or
  career framing.
- `outputs/manifest.json`: source mappings, commands, panel metadata, and
  guardrails.

## Deletion Policy

No valuable artifact will be permanently deleted during this sprint. Internal
history is moved to `archive/` unless a file is a generated cache or already
duplicated by canonical outputs. Raw data under `Data/` is not modified.
