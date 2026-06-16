# Portfolio v2.1 Final Audit

**Audit date:** 2026-06-16  
**Branch:** `portfolio_v2`  
**Verdict:** Ready to serve as the primary polished portfolio release.

## 1. Executive Verdict

Portfolio v2.1 is public-ready for the current release scope. The packet
contains reports, model cards, manifest, tables, figures, and diagnostics for
block partial R^2, ablations, ETF lead-lag, rolling correlations, stablecoin
liquidity, and BTC-native diagnostics. The release preserves the frozen data
policy and reduced-form interpretation boundaries.

## 2. Files Reviewed

- `README.md`
- `docs/specs/portfolio_spec.md`
- `docs/specs/methods_spec_v2.md`
- `docs/specs/feature_registry.md`
- `reports/portfolio_v2_1/manifest.json`
- `reports/portfolio_v2_1/executive_summary.md`
- `reports/portfolio_v2_1/technical_report.md`
- `reports/portfolio_v2_1/analytics_summary.md`
- `reports/portfolio_v2_1/data_atlas.md`
- `reports/portfolio_v2_1/resume_bullets.md`
- `reports/portfolio_v2_1/model_cards/*.md`
- `reports/portfolio_v2_1/diagnostics/*.md`

## 3. Public-Readiness Checks

| Check | Result |
|---|---|
| README links exist locally | Pass |
| README image targets exist locally | Pass |
| v2.1 manifest has timestamp, git commit, panel metadata, commands, tables, figures, reports, and model cards | Pass |
| Model cards include required sections | Pass |
| `verification.md` records command results | Pass |
| `checkpoint.md` records checkpoint commits | Pass |
| `Data/` untouched | Pass |

## 4. Claim Audit

| Claim area | Result |
|---|---|
| Project framing | Pass: portfolio-grade analytics system, not academic-publication-first |
| ETF flows | Pass: association / market plumbing, not causal impact |
| Stablecoins | Pass: liquidity proxy / context, not proven causal driver |
| BTC-native factors | Pass: MVRV framed as valuation state and not a standalone trading signal |
| ETH framing | Pass: comparison asset, not forced BTC symmetry |

## 5. Figure Audit

The v2.1 figure set exists under `reports/portfolio_v2_1/figures/` and includes
the requested `F10-F13`, `F20-F25`, `F30-F33`, `F40-F44`, `F50-F52`, and copied
baseline reference figures. The README embeds the strongest figures for factor
attribution, ETF lead-lag, rolling correlations, and baseline coverage.

## 6. Method-Label Audit

| Method | Label status |
|---|---|
| Block partial R^2 | Correctly labeled full-vs-reduced block partial R^2 |
| Rolling attribution | Correctly separated from Shapley/Owen |
| Structural breaks | Correctly labeled Chow plus single-break sup-F |
| VAR/FEVD | Correctly framed as ordering-sensitive connectedness diagnostics |
| Event studies | Correctly framed as event-window association |

## 7. Link Audit

README local Markdown links and image paths were checked with a local path
existence script. No missing local targets were returned.

## 8. Commands Run

| Command | Result |
|---|---|
| `uv run pytest` | Pass: 26 passed |
| `uv run mypy src/cqresearch` | Pass |
| `uv run python scripts/run_portfolio_v2_1_pipeline.py` | Pass |
| Focused v2.1 Ruff command | Pass |
| `git status --short -- Data` | Pass: no entries |

## 9. Remaining Limitations

- The v2.1 pipeline emits two known pandas runtime warnings from existing
  log-return construction on nonpositive values.
- Daily ETF-flow and return data remain vulnerable to simultaneity and omitted
  news shocks.
- Current structural-break diagnostics are not full Bai-Perron.
- v2.1 attribution is not Shapley/Owen.

## 10. Merge Recommendation

Mergeable as the primary portfolio release after the continuation sprint adds
showcase docs, optional v2.2 advanced diagnostics, CI/release polish, and PR
materials.
