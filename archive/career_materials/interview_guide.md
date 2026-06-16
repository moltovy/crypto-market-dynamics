# Interview Guide

## 30-Second Explanation

I built Crypto Market Factor Lab, a reproducible Python analytics framework for
BTC/ETH factor regimes, ETF-flow market plumbing, stablecoin liquidity, and
crypto-native market structure on a frozen 2020-2026 panel.

## 2-Minute Explanation

The project takes curated crypto, macro, ETF-flow, stablecoin, DeFi, and
on-chain data and turns it into portfolio-grade reports, figures, tables, model
cards, and manifests. It emphasizes reduced-form diagnostics rather than causal
claims. The strongest release is Portfolio v2.1, which adds block partial R2,
ETF lead-lag checks, rolling correlations, stablecoin liquidity proxies, and a
BTC-native factor lab.

## 5-Minute Technical Walkthrough

Start with `Data/MASTER_DATA.csv`, build the frozen daily panel, derive
stationary features, estimate reduced-form models, package reports under
`reports/portfolio_v2_1/`, and verify with pytest, mypy, Ruff, and manifest
checks.

## Architecture Explanation

The repository separates data loading, feature construction, modeling helpers,
analysis orchestration, and generated portfolio packets. Scripts are thin entry
points; reusable logic lives under `src/cqresearch/`.

## Data Engineering Explanation

The data system freezes source CSVs and panel outputs so public reviewers can
reproduce the same report without live APIs or paid data. Coverage and source
inventories make missingness explicit.

## Feature Engineering Explanation

Prices become log returns. Rates, spreads, sentiment, and native levels become
first differences. ETF flow is scaled by prior-day market cap. Realized
volatility is a 30-day annualized rolling standard deviation.

## Econometric Methods Explanation

The project uses HAC OLS, full-vs-reduced block partial R2, nested ablations,
lead-lag grids, rolling correlations, Chow/single-break sup-F diagnostics,
VAR/FEVD connectedness, and event-window association.

## Crypto Market-Structure Explanation

ETF flows are treated as market plumbing. Stablecoins and TVL are liquidity
context. BTC-native variables are split into valuation-state and flow-state
families because they have different interpretation risks.

## Interpretation Boundaries

The project does not claim ETF flows caused returns, does not label current
break tests as full Bai-Perron, and does not call v2.1 attribution Shapley/Owen.

## Likely Interviewer Questions And Answers

**Why not claim ETFs caused a structural break?**  
Daily ETF flows, returns, macro news, and risk appetite move together. The
evidence is reduced-form association, not identification.

**Why frozen data?**  
Frozen data makes the portfolio reproducible and avoids live API drift.

**Why ETF-flow intensity instead of raw ETF flow?**  
Scaling by prior-day market cap makes the flow measure comparable across time
and across BTC/ETH.

**What is full-vs-reduced block partial R2?**  
It compares a full model to a reduced model that removes one factor block:
`(RSS_reduced - RSS_full) / TSS`.

**How is that different from Shapley/Owen?**  
Block partial R2 is conditional on a specified full model. Shapley/Owen averages
marginal contributions across many model orderings or coalitions.

**Why separate MVRV from non-MVRV native factors?**  
MVRV is a valuation-state variable that can mechanically co-move with price, so
it should not be blended with exchange/miner flow variables.

**Why BTC-primary and ETH-comparison?**  
The current frozen panel has stronger BTC-native coverage and thinner ETH-native
coverage.

**How do you avoid lookahead bias?**  
Stationary transforms use current/past daily observations, ETF intensity uses
prior-day market cap as the denominator, and lead-lag conventions are explicit.

**What does VAR/FEVD add?**  
It provides connectedness diagnostics under a declared ordering, not structural
shock identification.

**What are the limits of daily data?**  
Daily aggregation hides intraday sequencing and increases simultaneity risk.

**What would intraday data add?**  
It would help separate ETF-flow timing, price response, and market-maker
inventory dynamics.

**How would you productionize this for a fund/research desk?**  
Add scheduled refresh jobs, data QA gates, immutable snapshots, model monitoring,
dashboard publishing, and reviewable release notes.

**How would you extend this to altcoins?**  
Start with liquid assets, define chain-native features, add exchange liquidity
and derivatives proxies, and use common-support diagnostics.

**How would you add risk forecasting?**  
Add volatility targets, rolling cross-validation, benchmark loss functions, and
out-of-sample model cards.

**What is the biggest weakness?**  
The project is daily and observational, so timing and causality remain limited.

**What are you most proud of technically?**  
The end-to-end release discipline: frozen panel, features, models, figures,
model cards, manifests, tests, and careful language.
