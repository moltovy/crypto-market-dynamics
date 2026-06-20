# ETF Market Plumbing Model Card

Purpose: describe ETF-era market plumbing through flow intensity, lag timing, and absorption ratios.

Calendar and timing: ETF trading-day panel computes BTC/ETH returns from the prior ETF trading date to the current ETF trading date. Lag 0 is current ETF trading-date flow intensity; lag 1 is prior ETF trading-date flow intensity.

Principal finding: BTC lag0 return corr=0.379 (n=820) vs lag1=0.049 (n=819); ETH lag0 return corr=0.226 (n=627) vs lag1=0.086 (n=626).

Limitations: short sample, reporting timing, and simultaneity.

Prohibited claims: ETF flows caused BTC or ETH returns.
