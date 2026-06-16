# Data Sources, Factor Blocks, and Sample Design

## Confirmed / Core Data Resources
- CryptoQuant local exports
- DefiLlama API data
- Massive / Polygon market data
- Farside ETF flow data
- FRED macro data
- Dune as optional extension / validation layer

## Factor Blocks

### 1. Macro / Cross-Asset Block
Possible variables:
- SPY or QQQ
- DXY
- 10Y yield or real-yield proxy
- VIX
- gold
- optional: oil, credit spreads, HYG/LQD style proxies

### 2. Institutional Block
Possible variables:
- BTC ETF net flows
- ETH ETF net flows
- cumulative flows
- issuer concentration share
- AUM growth or flow share variants
- public-company / DAT holdings as an institutionalization extension

### 3. Crypto-Liquidity Block
Possible variables:
- total stablecoin market cap
- USDT growth
- USDC growth
- stablecoin chain allocation
- stablecoin concentration by chain
- chain TVL
- DEX volume
- protocol / chain fees and revenue
- bridge flow / chain migration metrics
- protocol USD inflows if available

### 4. BTC-Native Block
Possible variables:
- MVRV
- SOPR / aSOPR
- exchange netflows
- exchange reserves
- Coinbase premium
- whale ratio
- open interest
- funding rates
- leverage ratio
- holder cohort variables

### 5. ETH-Native Block
Possible variables:
- active addresses
- fees
- fees burnt
- staking rate
- total staked
- Ethereum / L2 activity metrics
- ETH ecosystem DeFi indicators
- exchange netflows / derivatives positioning

## Alternative Lenses for "What Moves Crypto" Beyond ETFs
1. Derivatives positioning lens
2. Stablecoin liquidity lens
3. On-chain supply / profit-taking lens
4. DeFi economic activity lens
5. Public-company / DAT lens
6. Macro / cross-asset lens

## Data Frequency Strategy
### Daily
Use as the main panel for:
- returns
- volatility
- ETF flows
- stablecoin market cap
- TVL
- DEX volume
- fees / revenue
- most on-chain metrics
- macro market variables

### Weekly
Use for robustness and smoothing:
- chain-level ecosystem activity
- protocol-level metrics
- stablecoin chain allocation
- smoothed factor regressions

### Monthly
Use only for slow variables and structural robustness:
- slow macro variables
- long-horizon comparisons
- cycle-style context

## Sample Design for Uneven Start Dates
Do not force everything into one giant universal sample.

### Sample A: Core Common Sample
Use the longest clean overlap for serious BTC/ETH comparison work.
Likely around 2021 onward.

### Sample B: Long-History Reduced BTC Model
Use for BTC-only historical context with fewer variables.

### Sample C: Short-History Specialized Modules
Use for later-starting variables such as:
- ETF flows
- newer stablecoin / DeFi metrics
- some ETH staking or ecosystem metrics
- dimensions datasets with short history

## Data Engineering Principle
Build broad raw archives first.
Then create curated analytical panels later.
