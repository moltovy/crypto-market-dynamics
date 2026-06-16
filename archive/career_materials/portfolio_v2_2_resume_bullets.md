# Portfolio v2.2 Resume Bullets

- Built an advanced crypto factor diagnostics extension over a frozen
  `2293`-row daily BTC/ETH panel, adding PCA block factors,
  exact block Shapley R2, rolling VAR/FEVD connectedness, CUSUM diagnostics, and
  a robustness grid without changing raw data.
- Implemented exact subset-enumerated block Shapley attribution and a bounded
  rolling version (`window=180`, `step=30`) to separate tested attribution from
  simpler drop-one partial R2 used in earlier release packets.
- Hardened interpretation language around ETF flows, PCA, FEVD, and CUSUM so the
  public portfolio reads as reduced-form analytics rather than causal claims.
