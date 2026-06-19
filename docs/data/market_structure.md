# Market-Structure Data Extension

The market-structure extension adds a curated public layer for DefiLlama,
Binance, and CoinMarketCap while preserving the frozen dataset.

## Storage Policy

- Raw API responses and large refresh payloads go to gitignored `data_cache/`.
- Release-ready normalized CSVs go to `Data/MarketStructure/`.
- Public tables, figures, and reports go to `outputs/`.
- Existing raw or curated source files under `Data/AlternativeMe`,
  `Data/DefiLlama`, `Data/Tradingview`, and other frozen folders are not
  modified by the extension.

## Source Roles

| Source | Role | Auth |
|---|---|---|
| DefiLlama | TVL, stablecoins, DeFi activity, RWA/DAT context | Free endpoints public; Pro endpoints optional |
| Binance | Spot/futures exchange-liquidity, funding, premium context | Public endpoints |
| CoinMarketCap | Optional Fear & Greed history | `CMC_API_KEY` for live refresh; cache-only rebuild after fetch |
| AlternativeMe | Tracked baseline Fear & Greed history | None |

## Guardrails

- Binance top100 is an exchange-liquidity rank based on rolling quote volume,
  not a historical market-cap rank.
- Historical market-cap top100 is skipped unless point-in-time market-cap
  snapshots are provided.
- Current order-book and ticker payloads are snapshots only.
- Stablecoin supply, TVL, and liquidity features are proxies, not causal shocks.
- API keys must live in `.env`; public outputs and manifests redact secrets.

## Commands

```powershell
uv run python scripts/audit_market_structure_endpoints.py --dry-run
uv run python scripts/fetch_market_structure_raw.py --cache-only
uv run python scripts/normalize_market_structure_cache.py --cache-only
uv run python scripts/build_market_structure_outputs.py
```
