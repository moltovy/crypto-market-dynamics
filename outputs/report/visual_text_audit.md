# Visual Text Audit

This audit evaluates the public figures in `outputs/figures/` for text density, focusing on whether explanatory prose, caveats, and methodology details should be removed from the charts and moved to the README or model cards.

## F00_project_summary_card.png
* **Current Title Text:** Crypto Market Factor Lab
* **Subtitle Text:** Reproducible BTC/ETH factor regimes, ETF-flow market plumbing, stablecoin liquidity, native factors, connectedness, and robustness diagnostics.
* **Annotation Count:** 2 paragraph blocks, multiple KPI badges and method pills.
* **Footer Text:** Source: frozen 2020-2026 panel | Public artifact root: outputs/ | No live or paid API dependency.
* **Contains paragraphs/badges/caveat text:** Yes, heavily text-based card wall with paragraphs and caveat statements.
* **Text to move to README:** The interpretations, caveats about causal impact and Chow tests.
* **Final Decision:** Demote/Redesign as a minimal visual pipeline, or remove from primary README surface.

## F01_data_coverage.png
* **Current Title Text:** Frozen BTC/ETH Multi-Source Panel
* **Subtitle Text:** 2,293 daily observations, 63 columns, and April 2026 data vintage across crypto, macro, ETF-flow, DeFi, sentiment, and native sources.
* **Annotation Count:** 1 long text block at the bottom about panel contract.
* **Footer Text:** Source: outputs/tables/T01_source_inventory.csv and T02_panel_coverage.csv | Method: grouped source coverage...
* **Contains paragraphs/badges/caveat text:** Yes, multi-line subtitle and contract text.
* **Text to move to README:** Details about rows, columns, and data vintage.
* **Final Decision:** Simplify to short title "Data Coverage", remove subtitle, move contract text to caption.

## F02_btc_block_attribution.png
* **Current Title Text:** BTC Factor Attribution Is Native-State Heavy
* **Subtitle Text:** Rolling block partial R2 and full-sample block removal show valuation/native state dominating the reduced-form fit.
* **Annotation Count:** 1 text label for MVRV pct.
* **Footer Text:** Source: ... | Method: full-vs-reduced block partial R2, not Shapley/Owen.
* **Contains paragraphs/badges/caveat text:** Long subtitle containing conclusion.
* **Text to move to README:** The conclusion and method details.
* **Final Decision:** Simplify title to "BTC Factor Attribution", remove subtitle and long method footer.

## F03_btc_etf_lead_lag.png
* **Current Title Text:** BTC ETF-Flow Lead-Lag: Strong Same-Day Association
* **Subtitle Text:** HAC t-statistics by lag, with lag < 0 meaning ETF-flow intensity is shifted earlier and leads the BTC return target.
* **Annotation Count:** 1 badge ("association, not causality"), 1 text box detailing specific same-day t-stat and coef.
* **Footer Text:** Source: ... | Method: HAC OLS lead-lag grid with controls; association, not causality.
* **Contains paragraphs/badges/caveat text:** Yes, caveats and badges.
* **Text to move to README:** Explanation of lag convention, warning about association vs causality.
* **Final Decision:** Simplify title to "ETF Flow Lead-Lag", remove subtitle, badge, and extra text boxes.

## F04_btc_rolling_correlations.png
* **Current Title Text:** Cross-Asset Co-Movement Is Time-Varying
* **Subtitle Text:** BTC 180-day rolling correlations move across crypto beta, equity risk, dollar, gold, and volatility regimes.
* **Annotation Count:** 0
* **Footer Text:** Source: ... | Method: rolling pairwise correlations.
* **Contains paragraphs/badges/caveat text:** Multi-line narrative subtitle.
* **Text to move to README:** The interpretation of the regimes.
* **Final Decision:** Simplify title to "Rolling Correlations", remove subtitle, optionally switch to small multiples or simplify lines.

## F05_stablecoin_supply_tvl.png
* **Current Title Text:** Stablecoin Supply And DeFi TVL Are Liquidity Context
* **Subtitle Text:** Indexed stablecoin supply and DeFi TVL provide a market-liquidity backdrop; they are proxies, not identified funding shocks.
* **Annotation Count:** 1 badge ("proxy, not shock"), 1 context text box with Apr 2026 stats.
* **Footer Text:** Source: ... | Method: indexed levels plus 30-day annualized realized volatility.
* **Contains paragraphs/badges/caveat text:** Yes, badges and large text boxes.
* **Text to move to README:** Proxy caveats and specific snapshot stats.
* **Final Decision:** Simplify title to "Stablecoins and TVL", remove subtitle, badge, and text box.

## F06_btc_native_dashboard.png
* **Current Title Text:** BTC-Native Dashboard Separates Valuation From Flow State
* **Subtitle Text:** MVRV-style valuation state is shown separately from exchange, miner, and basis variables to avoid over-reading mechanical co-movement.
* **Annotation Count:** 1 badge ("valuation state isolated").
* **Footer Text:** Source: ... | Method: ablation and correlation diagnostics.
* **Contains paragraphs/badges/caveat text:** Yes, narrative subtitle and badge.
* **Text to move to README:** The explanation of separation and correlation interpretation.
* **Final Decision:** Simplify title to "BTC Native State", remove subtitle and badge.

## F07_connectedness.png
* **Current Title Text:** Connectedness Depends On The VAR Design
* **Subtitle Text:** Compact 10-day FEVD and rolling connectedness summarize spillover structure, with Cholesky ordering treated as a sensitivity issue.
* **Annotation Count:** 1 badge ("ordering-sensitive").
* **Footer Text:** Source: ... | Method: compact VAR/FEVD, Cholesky-order sensitive.
* **Contains paragraphs/badges/caveat text:** Yes, narrative subtitle and badge.
* **Text to move to README:** The Cholesky ordering caveat and summary of spillover.
* **Final Decision:** Simplify title to "Connectedness", remove subtitle and badge.

## F08_robustness_grid.png
* **Current Title Text:** Robustness Grid Shows Sensitivity, Not Truth
* **Subtitle Text:** BTC model fit is stable at a high level when MVRV is included and materially lower without valuation-state variables.
* **Annotation Count:** 1 badge ("robustness, not truth").
* **Footer Text:** Source: ... | Method: mean R2 across winsorization/calendar choices by window, HAC lag, and MVRV inclusion.
* **Contains paragraphs/badges/caveat text:** Yes, narrative subtitle and badge.
* **Text to move to README:** Interpretation of MVRV impact and the "sensitivity vs truth" concept.
* **Final Decision:** Simplify title to "Robustness Grid", remove subtitle and badge.

## F09_key_results_cards.png / T00_key_results_table.png
* **Current Title Text:** Key Results, With Guardrails Attached / Key Results Table
* **Subtitle Text:** The public packet emphasizes evidence strength and method limits alongside the headline numbers. / A styled table card for quick review...
* **Annotation Count:** Multiple large text boxes wrapping sentences (results, interpretation, guardrails).
* **Footer Text:** Source...
* **Contains paragraphs/badges/caveat text:** Yes, entirely text-based cards/tables rendered as images.
* **Text to move to README:** All key results should be standard markdown tables or text in the README/report.
* **Final Decision:** Demote from the main visual packet. Replace with native markdown tables in README.
