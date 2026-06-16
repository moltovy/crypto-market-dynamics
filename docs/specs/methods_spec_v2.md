# Methods Spec v2 - Portfolio Release

**Status:** v1.0 implementation contract  
**Scope:** honest portfolio analytics using the frozen panel

## Implemented Methods

| Area | Current implementation | Portfolio label |
|---|---|---|
| Static OLS | HAC/Newey-West OLS over full, pre-ETF, and post-ETF samples | Factor exposure diagnostics |
| Rolling OLS | 180-day rolling OLS with single-variable deletion | Drop-one marginal R^2 |
| Structural breaks | Chow tests at ETF dates plus single-break sup-F sweep | Regime diagnostics |
| VAR/FEVD | statsmodels VAR with 10-day FEVD | Connectedness diagnostics |
| Event study | Market-model abnormal returns around selected dates | Event-window association |
| ETF flow | Daily ETF total flow divided by prior-day market cap | ETF-flow intensity |
| Block partial R^2 | Full model vs reduced model that drops a named factor block | Full-vs-reduced block partial R^2 |
| Lead-lag grids | HAC OLS over lagged ETF/stablecoin proxy columns | Lead-lag association diagnostics |
| Realized volatility | 30-day rolling annualized return standard deviation | Realized-volatility feature |

## Recommended Method Decisions

- **Attribution:** keep drop-one marginal R^2 as Tier 0 because it is already
  implemented and reproducible. Add Shapley/Owen only as a later appendix.
- **Structural breaks:** keep Chow and single-break sup-F as Tier 0. Add full
  Bai-Perron only if a tested implementation is introduced with explicit
  assumptions and validation.
- **ETF flows:** report same-day association, lag checks, and event context.
  Avoid causal language.
- **Lead-lag convention:** in v2.1 tables, `lag < 0` means the proxy is shifted
  earlier and leads the target return or volatility series.
- **Stablecoins:** treat stablecoin market cap and related variables as
  liquidity/funding proxies unless a separate identification design is added.
- **BTC-native variables:** separate MVRV-like valuation state from non-MVRV
  native flow and market-structure variables.
- **BTC vs ETH:** present BTC as the strongest model-development case and ETH as
  the comparison asset.
- **Data add-ons:** keep external free APIs optional. The release should not
  depend on live downloads.

## Reporting Requirements

Every model card must include:

- purpose
- inputs
- method
- output files
- interpretation
- risks and limitations
- upgrade path

Every report must state that the evidence is reduced-form and observational.
