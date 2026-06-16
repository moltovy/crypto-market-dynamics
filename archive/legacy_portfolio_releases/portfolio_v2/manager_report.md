# Deep Research Manager Report - Crypto Market Factor Lab

Generated: 2026-06-16 01:24 UTC
Source tables: `reports\tables\2026-06-16`
Source figures: `reports\figures\2026-06-16`

## 1. Executive Diagnosis

**Verified from repo.** The repository is a working Python research system with
curated data, feature engineering, econometric modules, dated outputs, figures,
run summaries, and tests. The frozen panel spans 2020-01-01
through 2026-04-11 with 2,293 rows and
63 columns (`reports/panels/master_daily_meta.json`).

**Inference.** The highest-value portfolio positioning is **Crypto Market Factor
Lab**: a reproducible crypto factor analytics and market-structure system. The
repo should lead with the data atlas, model cards, factor-regime diagnostics,
ETF-flow plumbing, and careful visual interpretation.

**External research context.** Academic crypto factor work supports factor-style
crypto return analysis; official SEC materials anchor ETF event dates; official
FRED, DefiLlama, CoinGecko, and Binance docs show that free data can extend the
project, but the frozen repo already has enough coverage for a shippable v2.

## 2. Repo Evidence Summary

**Verified from repo paths.**

- `Data/MASTER_DATA.md` and `Data/MASTER_DATA.csv` document 490
  curated CSV inventory rows across AlternativeMe,
  Artemis, CryptoQuant, DefiLlama, FRED, Farside ETF Data, and TradingView.
- `Data/_meta/curation_log.md` records the curation/audit trail.
- `src/cqresearch/features/panel.py` scales ETF flow intensity by prior-day USD
  market cap.
- `src/cqresearch/modeling/rolling.py` explicitly implements drop-one marginal
  R^2, not Shapley/Owen.
- `src/cqresearch/modeling/structural_breaks.py` implements Chow and a
  single-break sup-F sweep, not full Bai-Perron.
- `reports\tables\2026-06-16` and `reports\figures\2026-06-16` are the complete bundles selected for
  portfolio v2.
- `tests/` contains 13 passing tests after adding the portfolio-bundle selector
  guardrail.

Source inventory:

| source           |   files |    rows |
|:-----------------|--------:|--------:|
| CryptoQuant      |     345 | 1181712 |
| Artemis          |      48 |   75302 |
| Tradingview      |      44 |   92157 |
| DefiLlama        |      28 |  306856 |
| FRED             |      21 |  166529 |
| Farside ETF Data |       3 |    1032 |
| AlternativeMe    |       1 |    2994 |

**Inspection coverage.**

| Requested inspection area | Current evidence |
|---|---|
| README and project framing | `README.md` rewritten for Crypto Market Factor Lab |
| Data inventory and curation | `Data/MASTER_DATA.md`, `Data/MASTER_DATA.csv`, `Data/_meta/curation_log.md` |
| Research plan location | root `project_research_plan.md` absent; historical plan is under `Manager/Opus Manager/project_research_plan.md` |
| Config contracts | `config/factor_blocks.yml`, `config/events.yml`, `config/calendars.yml` |
| Specs | legacy warnings in `docs/specs/research_spec.md`, `data_spec.md`, `methods_spec.md`; active v2 specs added |
| Native metrics | `docs/specs/paper_1_native_metrics.yml` retained as historical native-metric context |
| Data pipeline | `src/cqresearch/data/loaders.py`, `panel_builder.py`, feature construction in `features/panel.py` |
| Modeling code | OLS, rolling, structural-break, VAR/FEVD, and event-study modules under `src/cqresearch/modeling/` |
| Scripts | `scripts/01_build_master_panel.py` through `05_robustness.py`, `run_full_pipeline.py`, and `run_portfolio_pipeline.py` |
| Outputs | panel metadata/coverage, latest complete tables/figures, run summaries, drafts, and portfolio v2 packet |
| Tests/tooling | `tests/`, `pyproject.toml`, `Makefile`, `.cursor/rules`, and `prompts/` |

**Verified suspected-fact verdicts.**

| Prior suspected fact | Verdict | Evidence |
|---|---|---|
| Hundreds of curated CSVs across major crypto/macro sources | Confirmed | `Data/MASTER_DATA.csv`, `Data/MASTER_DATA.md` |
| Master panel around 2020-01-01 to 2026-04-11 with about 63 columns | Confirmed | `reports/panels/master_daily_meta.json` |
| ETF-flow intensity equals ETF flow divided by prior-day market cap | Confirmed | `src/cqresearch/features/panel.py` |
| Rolling code computes drop-one marginal R^2, not true block partial R^2 | Confirmed | `src/cqresearch/modeling/rolling.py` |
| Break code is Chow plus single-break sup-F, not full Bai-Perron | Confirmed | `src/cqresearch/modeling/structural_breaks.py` |
| Specs drifted from implementation | Confirmed and corrected for portfolio v2 | legacy warnings in `docs/specs/*.md`; v2 specs added |
| BTC-native variables dominate BTC model fit | Confirmed for current block table | post-ETF BTC native R^2 snapshot 0.969 |
| ETF-flow intensity is strong contemporaneously while lag-only evidence is weaker | Confirmed as a reduced-form association | `etf_flow_regression.csv`, `robustness/R1_lagged_etf_flow.csv` |
| Pre/post correlations and VAR/FEVD exist but needed packaging | Confirmed and packaged | `reports/portfolio_v2/tables/`, `reports/portfolio_v2/figures/` |

## 3. Critique of the Crypto Market Factor Lab Direction

**Recommendation: accept and sharpen.** The direction is right because it uses
the repo's actual strengths: curated data breadth, reproducible Python
orchestration, factor blocks, ETF-flow diagnostics, event studies, and
connectedness. The key refinement is to avoid overclaiming structural breaks or
causality.

**Refinement.** The best v2 is a static, reproducible GitHub portfolio packet
with curated visuals and model cards, not a live-data app or a new methodology
rewrite. The tradeoff is that v2 stays narrower than a dashboard product, but it
is more reliable for public review and interviews.

## 4. Best Project Framing for Resume and GitHub

**Title:** Crypto Market Factor Lab
**Subtitle:** Reproducible BTC/ETH factor-regime analytics across ETF flows,
stablecoin liquidity, macro risk, and crypto-native market structure.

The first 60 seconds should communicate:

- frozen multi-source panel through April 2026
- reproducible one-command portfolio packet
- honest reduced-form econometrics
- curated figures and model cards
- no paid-data dependency for the portfolio release

## 5. Recommended Analysis Modules

| Module | Tier | Purpose | Inputs | Methods | Outputs / figures | Resume value | Difficulty | Risks |
|---|---|---|---|---|---|---|---|---|
| Data Atlas | Tier 0 | Prove data engineering depth | `Data/MASTER_DATA.csv`, panel metadata | inventory and coverage summaries | `data_atlas.md`, coverage figure/table | data engineering, reproducibility | Low | too much detail |
| Market Regime / Rolling Dashboard | Tier 0 | Show time-varying fit | rolling OLS outputs | 180-day rolling R^2 | rolling R^2 figures | quant visualization | Low | over-reading fit |
| Factor-Block Attribution | Tier 0 | Compare macro/institutional/liquidity/native blocks | feature panel, block tables | drop-one marginal R^2 and block R^2 | block tables, stacked R^2 figures | factor modeling | Medium | not fair Shapley allocation |
| ETF-Flow Intensity Lab | Tier 0 | Explain ETF market plumbing | Farside flows, market cap, returns | intensity regression and robustness | ETF regression table, event text | crypto market structure | Medium | simultaneity |
| Stablecoin Liquidity Lab | Tier 1 | Frame crypto-dollar liquidity | stablecoin supply, TVL, returns | descriptive and VAR context | atlas and FEVD context | liquidity research | Medium | weak identification |
| Crypto-Native Factor Lab | Tier 0 | Show BTC valuation/flow insight | MVRV, exchange/miner flows | first-difference native block | BTC native block result | on-chain research | Medium | BTC/ETH asymmetry |
| Structural-Break Diagnostics | Tier 0 | Test regime-change claims carefully | returns and macro/institutional regressors | Chow and single-break sup-F | break table, sup-F figures | econometrics judgment | Medium | not full Bai-Perron |
| VAR/FEVD Connectedness | Tier 1 | Show dynamic connectedness | returns, SPY, VIX, liquidity proxies | statsmodels VAR, 10-day FEVD | compact/full FEVD heatmaps | time-series modeling | Medium | Cholesky ordering |
| Event Studies | Tier 1 | Add event-window context | BTC/ETH returns and SPY | market-model abnormal returns | event CAR table/figure | empirical finance | Medium | confounding and low power |
| Optional Free Data Add-ons | Tier 2 | Future enrichments | free APIs/docs | evaluate and cache only if useful | docs-only decision table | research PM judgment | Low | scope creep |

## 6. Methodology Decisions and Recommendations

| Decision | Options considered | Recommendation | Why |
|---|---|---|---|
| Attribution | true block partial R^2, drop-one marginal R^2, Shapley/Owen | Drop-one for v2; Shapley/Owen later | implemented, honest, reproducible |
| Feature representation | raw stationary variables, PCA factors, LASSO screening | stationary variables plus clear labels | easiest to audit and explain |
| Break tests | Chow/sup-F, Bai-Perron, CUSUM | Chow/sup-F for v2 | current implementation supports it |
| ETF-flow timing | contemporaneous, lagged, event-style | report contemporaneous association plus lag/event caveats | avoids causality overreach |
| Stablecoins | local projections, VAR, descriptive | descriptive and VAR context | enough for portfolio without new identification |
| BTC/ETH symmetry | BTC-primary, fully symmetric | BTC-primary with ETH comparison | BTC-native variables are stronger |
| Data policy | frozen only, optional free add-ons, refresh core | frozen core; free add-ons optional | avoids API/subscription fragility |
| Delivery format | technical report, dashboard, notebook gallery | static GitHub reports and figures | shippable and reviewable |
| App layer | Streamlit/Dash, static packet | static packet for v2 | avoids maintenance burden |

## 7. Data-Source Decision Table

| Source | Variables added | Overlap | Core-story value | Maintenance burden | Decision |
|---|---|---|---|---|---|
| Existing CryptoQuant exports | BTC/ETH native, MVRV, flows | unique/high | high | none for frozen release | Keep core |
| Existing Farside ETF flows | spot ETF fund flows | unique/high | high | none for frozen release | Keep core |
| Existing DefiLlama/Artemis data | TVL, stablecoins, DEX/perps context | medium | high | none for frozen release | Keep core |
| Existing FRED macro | rates, VIX, dollar, macro controls | low | high | none for frozen release | Keep core |
| DefiLlama free API | refreshed TVL/stablecoin/chain metrics | overlaps existing | medium | medium | Optional add-on |
| CoinGecko free/demo API | prices, market caps, volumes | high overlap | low/medium | medium | Optional validation only |
| Binance public data | candles, trades, funding-adjacent market data | partial | medium for microstructure | medium/high | Optional future module |
| SEC filings/orders | ETF dates and regulatory context | low | high as citations | low | Use as context |
| Yahoo/Stooq/free equity endpoints | equity/ETF prices | overlaps TradingView/FRED | low | medium | Reject for v2 |
| Paid data | any premium signals | unknown | not allowed | high | Reject |

## 8. Codex Orchestration Strategy

**Manager owns:** framing, scope, interpretation, causal-language guardrails,
method decisions, acceptance criteria, and review sign-off.

**Codex implementers own:** narrow code/doc patches, artifact generation,
tests, manifests, and evidence collection. In the requested manager/implementer
split, Codex GPT-5.5 extra-high agents should be treated as implementation
agents with bounded tickets, not as scope owners.

**Owner approves:** title/framing, whether to add optional data, whether to add
new methods, and whether to publish/push.

**Task format:** every Codex task should include files to read, likely files to
edit, exact outputs, tests/commands, acceptance criteria, and "do not change"
boundaries. Prevent scope creep by forbidding raw-data edits, new unapproved
models, and unrelated notebook/tooling lint cleanups.

**Branch/PR strategy:** keep `portfolio_v2` as the release branch; use small
follow-up branches for any future optional add-ons; open the PR with generated
portfolio artifacts and verification output.

## 9. Proposed Codex Work Packages

| Ticket | Goal | Files to read | Files likely to edit | Exact outputs | Tests | Acceptance criteria | Do not change | Manager review |
|---|---|---|---|---|---|---|---|---|
| WP1 Reproduction audit | prove baseline | `pyproject.toml`, scripts, tests | dependency files only if needed | command log | `uv sync`, `pytest`, full pipeline | pipeline passes or failure recorded | raw data | reproducibility evidence |
| WP2 Portfolio packet | create v2 artifacts | latest tables/figures, specs | `scripts/run_portfolio_pipeline.py`, `reports/portfolio_v2/` | reports, tables, figures, cards | portfolio pipeline | one-command regeneration | model results | artifact completeness |
| WP3 Method labels | align language | modeling code/specs/reports | README/specs/report text | corrected labels | phrase scans | no false Shapley/Bai-Perron claims | model code | claim accuracy |
| WP4 Model cards | disclose methods | model modules/tables | `model_cards/*.md` | five cards | section check | all required sections present | results | interpretation limits |
| WP5 README polish | public first screen | README, artifacts | README | figure links and quick start | link check | all links resolve | data/results | recruiter clarity |
| WP6 Final audit | public-readiness gate | all active artifacts | `final_audit.md` | audit report | pytest, mypy, Ruff, scans | all required checks pass | unrelated lint | PR readiness |

## 10. Final Artifact Map

- `reports/portfolio_v2/executive_summary.md`
- `reports/portfolio_v2/technical_report.md`
- `reports/portfolio_v2/data_atlas.md`
- `reports/portfolio_v2/manager_report.md`
- `reports/portfolio_v2/resume_bullets.md`
- `reports/portfolio_v2/figures/hero_cumulative_returns.png`
- `reports/portfolio_v2/figures/btc_rolling_r2.png`
- `reports/portfolio_v2/figures/btc_drop_one_r2_stack.png`
- `reports/portfolio_v2/figures/event_study_cars.png`
- `reports/portfolio_v2/figures/fevd_compact_heatmap.png`
- `reports/portfolio_v2/figures/data_coverage.png`
- `reports/portfolio_v2/tables/*.csv`
- `reports/portfolio_v2/model_cards/*.md`
- `reports/portfolio_v2/final_audit.md`
- `reports/portfolio_v2/manifest.json`
- `docs/specs/portfolio_spec.md`
- `docs/specs/methods_spec_v2.md`
- `docs/specs/feature_registry.md`
- `README.md` with hero figure links

## 11. Resume / LinkedIn Positioning

- Built a reproducible Python crypto factor analytics framework over 490 curated
  multi-source CSVs and a 2,293-day BTC/ETH panel through April 2026.
- Engineered stationary factor features for macro, ETF-flow, stablecoin
  liquidity, DeFi, and crypto-native market-structure diagnostics.
- Implemented reduced-form OLS, rolling drop-one R^2, Chow/sup-F break tests,
  VAR/FEVD connectedness, and event-study outputs with model cards.
- Reframed ETF-flow evidence as association and market plumbing rather than
  unsupported causality.

## 12. Questions and Decisions for the Owner

| Decision | Options | Recommendation | If different |
|---|---|---|---|
| Public title | Crypto Market Factor Lab vs legacy title | Crypto Market Factor Lab | Legacy framing narrows recruiter appeal |
| Core data | Frozen only vs refresh | Frozen only | Refresh adds brittle API risk |
| Attribution | Drop-one vs Shapley | Drop-one in v2 | Shapley adds scope and runtime risk |
| Break tests | Chow/sup-F vs Bai-Perron | Chow/sup-F in v2 | Bai-Perron needs tested implementation |
| App layer | Static reports vs dashboard | Static reports first | Dashboard adds maintenance burden |
| Optional data | No add-ons, validation-only add-ons, new core add-ons | No core add-ons for v2 | Core add-ons create maintenance burden |
| BTC/ETH emphasis | BTC-primary, symmetric BTC/ETH | BTC-primary with ETH comparison | Forced symmetry weakens interpretation |

## Verified Headline Corrections

- BTC post-ETF native-block R^2 snapshot: 0.969.
- BTC ETF-flow same-day intensity: beta=46.13,
  t=8.67, p=<0.001.
- BTC Chow at ETF date: F=0.79,
  p=0.624.
- ETH Chow at ETF date: F=2.12,
  p=0.025.

## External Research Sources

Sources are separated by role: academic factor context, official regulatory/data
documentation, and methods references. They inform framing and optional add-on
decisions; they do not override the frozen repo evidence.

| source                                                                                                                               | use                                                                    |
|:-------------------------------------------------------------------------------------------------------------------------------------|:-----------------------------------------------------------------------|
| [Common Risk Factors in Cryptocurrency](https://onlinelibrary.wiley.com/doi/10.1111/jofi.13119)                                      | Academic context for factor-style crypto return analysis.              |
| [SEC statement on spot bitcoin ETP approval](https://www.sec.gov/newsroom/speeches-statements/gensler-statement-spot-bitcoin-011023) | Official context for the January 10, 2024 spot bitcoin ETP approval.   |
| [SEC spot ether ETP approval order](https://www.sec.gov/files/rules/sro/nysearca/2024/34-100224.pdf)                                 | Official context for the May 23, 2024 ether ETP rule-change approvals. |
| [FRED API documentation](https://fred.stlouisfed.org/docs/api/fred/)                                                                 | Official macro data API context.                                       |
| [DefiLlama API documentation](https://api-docs.defillama.com/)                                                                       | Official DeFi/stablecoin/TVL API context.                              |
| [CoinGecko API documentation](https://docs.coingecko.com/)                                                                           | Official crypto market data API context.                               |
| [Binance public market data documentation](https://developers.binance.com/docs/binance-spot-api-docs/rest-api)                       | Official public exchange market-data context.                          |
| [Bai and Perron multiple structural changes](https://ideas.repec.org/a/ecm/emetrp/v66y1998i1p47-78.html)                             | Methods context for full multi-break models not implemented here.      |
| [MacKinlay event-study survey](https://www.bu.edu/econ/files/2011/01/MacKinlay-1996-Event-Studies-in-Economics-and-Finance.pdf)      | Methods context for abnormal-return event studies.                     |
| [Diebold-Yilmaz connectedness research](https://financialconnectedness.org/research.html)                                            | Methods context for FEVD-based connectedness framing.                  |

**Research topic coverage.**

| Topic requested | Portfolio v2 takeaway |
|---|---|
| Crypto factor models and asset pricing | Use reduced-form factor exposure diagnostics; avoid pretending daily regressions identify structural risk premia. |
| BTC/ETH market structure after US spot ETFs | Treat spot ETFs as market-plumbing/institutionalization context, not a single causal break by itself. |
| ETF-flow analysis | Scale flows by prior-day market cap; report contemporaneous association and lag/event caveats. |
| Stablecoin liquidity | Keep stablecoin supply as a crypto-dollar liquidity proxy; avoid causal funding-channel claims in v2. |
| DeFi/perps/DEX/open-interest variables | Existing Artemis/DefiLlama coverage is useful context; do not add live add-ons unless cached. |
| On-chain indicators | BTC MVRV and flow-state variables are strong in the current BTC block; ETH-native coverage is weaker. |
| Structural-break/regime methods | Chow and single-break sup-F are defensible portfolio diagnostics; full Bai-Perron is future work. |
| Rolling R^2, Shapley/Owen, PCA/LASSO, VAR/FEVD, events | Use implemented drop-one R^2, VAR/FEVD, and event studies now; keep Shapley/Owen/PCA/LASSO as optional extensions. |
| Public quant repo best practices | Lead with README, reproducible commands, data atlas, model cards, figures, and honest limitations. |
| Codex agent best practices | Use narrow tickets, explicit acceptance criteria, raw-data guardrails, and verification commands. |
