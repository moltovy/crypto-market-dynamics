"""Produce all publication figures into reports/figures/YYYY-MM-DD/.

F01 — BTC / ETH cumulative log returns with event markers.
F02 — Rolling R² of BTC returns on the full factor stack (180-day).
F03 — Rolling partial R² stacked area by factor block for BTC.
F04 — Rolling partial R² stacked area by factor block for ETH.
F05 — sup-F series for BTC with placebo 95th percentile.
F06 — sup-F series for ETH with placebo 95th percentile.
F07 — FEVD heatmap (10-day horizon).
F08 — Event-study CARs around the BTC spot-ETF launch.
F09 — Coverage timeline (column × date heat-map proxy).
F10 — Pre/post-ETF rolling 60-day correlation: BTC vs SPY, BTC vs GLD, BTC vs DXY.
"""
from __future__ import annotations

import sys
from datetime import datetime
from pathlib import Path

import numpy as np
import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
sys.path.insert(0, str(ROOT / "src"))

import matplotlib.pyplot as plt

from cqresearch.viz.style import PALETTE, setup, add_footer
from config.paths import PANELS_DIR, REPORTS_FIGURES_DIR, REPORTS_TABLES_DIR  # noqa: E402

setup()

STAMP = datetime.utcnow().strftime("%Y-%m-%d")
FIG = REPORTS_FIGURES_DIR / STAMP
FIG.mkdir(parents=True, exist_ok=True)
TAB = REPORTS_TABLES_DIR / STAMP

FOOTER = "CryptoQuant research v0.1 · data: CryptoQuant, DefiLlama, Farside, FRED, Tradingview, AlternativeMe · 2020-01-01..2026-04-11"

BTC_ETF = pd.Timestamp("2024-01-11")
ETH_ETF = pd.Timestamp("2024-07-23")
FTX = pd.Timestamp("2022-11-08")
SVB = pd.Timestamp("2023-03-10")
COVID = pd.Timestamp("2020-03-12")


def load_panel() -> pd.DataFrame:
    return pd.read_parquet(PANELS_DIR / "master_daily.parquet")


def _save(fig: plt.Figure, name: str) -> Path:
    path = FIG / f"{name}.png"
    add_footer(fig, FOOTER)
    fig.savefig(path)
    plt.close(fig)
    return path


# ---------------------------------------------------------------------------
# F01 — cumulative returns
# ---------------------------------------------------------------------------
def f01_cumulative_returns(panel: pd.DataFrame) -> Path:
    btc = np.log(panel["btc_close"]).diff()
    eth = np.log(panel["eth_close"]).diff()
    fig, ax = plt.subplots(figsize=(9, 4.5))
    ax.plot(btc.index, btc.cumsum(), label="BTC", color=PALETTE["btc"], lw=1.6)
    ax.plot(eth.index, eth.cumsum(), label="ETH", color=PALETTE["eth"], lw=1.6)
    for d, lbl in [(COVID, "COVID"), (FTX, "FTX"), (SVB, "SVB"), (BTC_ETF, "BTC ETF"), (ETH_ETF, "ETH ETF")]:
        ax.axvline(d, color=PALETTE["event"], lw=0.7, alpha=0.55, ls=":")
        ax.text(d, ax.get_ylim()[1] if False else 2.5, lbl, rotation=90, fontsize=8, color="#333")
    ax.set_title("BTC & ETH cumulative log returns, Jan-2020 through Apr-2026")
    ax.set_ylabel("cumulative log return")
    ax.legend(loc="upper left")
    return _save(fig, "F01_cumulative_returns")


# ---------------------------------------------------------------------------
# F02 — rolling R² for BTC
# ---------------------------------------------------------------------------
def f02_rolling_r2(asset: str) -> Path:
    roll = pd.read_csv(TAB / f"rolling_ols_{asset}_180d.csv", parse_dates=["date"]).set_index("date")
    fig, ax = plt.subplots(figsize=(9, 3.8))
    ax.plot(roll.index, roll["r2"], color=PALETTE["btc" if asset == "btc" else "eth"], lw=1.4)
    ax.axhline(roll["r2"].mean(), color="#555", lw=0.8, ls="--",
               label=f"mean R²={roll['r2'].mean():.2f}")
    for d, lbl in [(BTC_ETF, "BTC ETF"), (ETH_ETF, "ETH ETF"), (FTX, "FTX"), (SVB, "SVB")]:
        ax.axvline(d, color="#222", lw=0.7, alpha=0.5, ls=":")
    ax.set_ylabel("R²")
    ax.set_title(f"Rolling 180-day R² — {asset.upper()} return ~ macro + institutional + DeFi + native")
    ax.legend(loc="upper left")
    return _save(fig, f"F02_{asset}_rolling_r2")


# ---------------------------------------------------------------------------
# F03/F04 — stacked partial R² by block
# ---------------------------------------------------------------------------
BLOCKS: dict[str, list[str]] = {
    "Macro": ["DGS10_d1", "DGS2_d1", "VIXCLS_d1", "DTWEXBGS_d1", "DFF_d1"],
    "Institutional": ["spy_ret", "qqq_ret", "gld_ret"],
    "Liquidity": ["defi_tvl_usd_ret", "stables_total_usd_ret"],
    "Sentiment": ["fng_value_d1"],
    "Native": ["cme_btc_basis_close_d1", "cme_eth_basis_close_d1"],
}
BLOCK_COLORS = {
    "Macro": PALETTE["macro"],
    "Institutional": PALETTE["institutional"],
    "Liquidity": PALETTE["liquidity"],
    "Sentiment": PALETTE["sentiment"],
    "Native": PALETTE["crypto_native"],
}


def f03_partial_r2(asset: str) -> Path:
    roll = pd.read_csv(TAB / f"rolling_ols_{asset}_180d.csv", parse_dates=["date"]).set_index("date")
    # Aggregate partial R² by block
    block_series = {}
    for block, cols in BLOCKS.items():
        cols_here = [f"pr2_{c}" for c in cols if f"pr2_{c}" in roll.columns]
        if not cols_here:
            continue
        # Partial R² can be slightly negative due to sampling; clip at 0 for stacking
        block_series[block] = roll[cols_here].sum(axis=1).clip(lower=0)

    df = pd.DataFrame(block_series).dropna()
    fig, ax = plt.subplots(figsize=(9.5, 4.5))
    ax.stackplot(
        df.index,
        *[df[b] for b in df.columns],
        labels=list(df.columns),
        colors=[BLOCK_COLORS[b] for b in df.columns],
        alpha=0.85,
    )
    for d, lbl in [(BTC_ETF, "BTC ETF"), (ETH_ETF, "ETH ETF"), (FTX, "FTX"), (SVB, "SVB")]:
        ax.axvline(d, color="#111", lw=0.6, alpha=0.6, ls=":")
    ax.set_ylabel("partial R² (stacked)")
    ax.set_title(f"{asset.upper()} return variance decomposition — rolling 180-day partial R² by factor block")
    ax.legend(loc="upper left", ncol=3)
    ax.set_ylim(bottom=0)
    return _save(fig, f"F03_{asset}_partial_r2_stack" if asset == "btc" else f"F04_{asset}_partial_r2_stack")


# ---------------------------------------------------------------------------
# F05 / F06 — sup-F series
# ---------------------------------------------------------------------------
def f05_sup_f(asset: str) -> Path:
    s = pd.read_csv(TAB / f"sup_f_series_{asset}.csv", parse_dates=["date"]).set_index("date")["supF"]
    fig, ax = plt.subplots(figsize=(9, 3.5))
    ax.plot(s.index, s.values, color=PALETTE["btc" if asset == "btc" else "eth"], lw=1.3)
    for d, lbl in [(BTC_ETF, "BTC ETF"), (ETH_ETF, "ETH ETF"), (FTX, "FTX"), (SVB, "SVB")]:
        ax.axvline(d, color="#111", lw=0.7, alpha=0.55, ls=":")
    ax.set_ylabel("F statistic")
    ax.set_title(f"{asset.upper()} — sup-F break test across all interior dates (trim=0.15)")
    return _save(fig, f"F05_sup_f_{asset}" if asset == "btc" else f"F06_sup_f_{asset}")


# ---------------------------------------------------------------------------
# F07 — FEVD heatmap
# ---------------------------------------------------------------------------
def f07_fevd_heatmap() -> Path:
    fev = pd.read_csv(TAB / "fevd_10d.csv", index_col=0)
    fig, ax = plt.subplots(figsize=(7.5, 6.2))
    im = ax.imshow(fev.values, cmap="viridis", vmin=0, vmax=1, aspect="auto")
    ax.set_xticks(range(fev.shape[1]))
    ax.set_xticklabels(fev.columns, rotation=45, ha="right")
    ax.set_yticks(range(fev.shape[0]))
    ax.set_yticklabels(fev.index)
    ax.set_xlabel("explained by shocks to →")
    ax.set_ylabel("variance of ↓")
    ax.set_title("10-day FEVD — share of variance of row explained by shocks to column")
    for i in range(fev.shape[0]):
        for j in range(fev.shape[1]):
            val = fev.values[i, j]
            ax.text(j, i, f"{val:.2f}", ha="center", va="center",
                    color="white" if val < 0.55 else "black", fontsize=8)
    fig.colorbar(im, ax=ax, fraction=0.046)
    return _save(fig, "F07_fevd_heatmap")


# ---------------------------------------------------------------------------
# F08 — event-study bars
# ---------------------------------------------------------------------------
def f08_event_cars() -> Path:
    ev = pd.read_csv(TAB / "event_studies.csv")
    ev = ev.sort_values(["event", "window"]).reset_index(drop=True)
    # Short label for each event
    short = {
        "BTC spot ETF launch (2024-01-11)": "BTC ETF 2024-01-11",
        "ETH spot ETF launch (2024-07-23)": "ETH ETF 2024-07-23",
        "Fed pivot signal (2022-11-02 FOMC)": "Fed FOMC 2022-11-02",
        "FTX collapse (2022-11-08)": "FTX 2022-11-08",
        "Silicon Valley Bank failure (2023-03-10)": "SVB 2023-03-10",
    }
    ev["_short"] = ev["event"].map(short).fillna(ev["event"])
    ev["_label"] = ev["_short"] + "  " + ev["window"]

    fig, ax = plt.subplots(figsize=(9.5, 6.0))
    ys = np.arange(len(ev))
    colors = [PALETTE["bad"] if c < 0 else PALETTE["ok"] for c in ev["car"]]
    ax.barh(ys, ev["car"], color=colors, edgecolor="white", linewidth=0.6)
    ax.set_yticks(ys)
    ax.set_yticklabels(ev["_label"], fontsize=8)
    ax.axvline(0, color="#333", lw=0.8)
    # annotate t-statistics
    for y, (car, t, p) in enumerate(zip(ev["car"], ev["t_stat"], ev["placebo_p_m5_p5"])):
        txt = f"  t={t:.2f}  p(pl.)={p:.2f}"
        ax.text(car, y, txt, va="center",
                ha="left" if car >= 0 else "right", fontsize=7, color="#222")
    ax.set_xlabel("CAR (log return)")
    ax.set_title("Event-study CARs — BTC/ETH around major events (market-model benchmark = SPY)")
    ax.invert_yaxis()
    return _save(fig, "F08_event_cars")


# ---------------------------------------------------------------------------
# F09 — coverage heatmap
# ---------------------------------------------------------------------------
def f09_coverage(panel: pd.DataFrame) -> Path:
    # Binary "data present today?" matrix
    keep = [c for c in panel.columns if panel[c].notna().sum() > 0]
    present = panel[keep].notna().astype(int)
    fig, ax = plt.subplots(figsize=(10, 6))
    im = ax.imshow(present.T.values, aspect="auto", cmap="Greens", interpolation="none",
                   extent=[0, len(present), 0, len(keep)])
    ax.set_yticks(np.arange(len(keep)) + 0.5)
    ax.set_yticklabels(keep, fontsize=6)
    n_ticks = 10
    idx_ticks = np.linspace(0, len(present) - 1, n_ticks).astype(int)
    ax.set_xticks(idx_ticks)
    ax.set_xticklabels([present.index[i].strftime("%Y-%m") for i in idx_ticks], rotation=45)
    ax.set_title("Master panel — data coverage by date")
    return _save(fig, "F09_coverage")


# ---------------------------------------------------------------------------
# F10 — rolling 60-day correlation of BTC vs TradFi
# ---------------------------------------------------------------------------
def f10_rolling_corr(panel: pd.DataFrame) -> Path:
    btc = np.log(panel["btc_close"]).diff()
    spy = np.log(panel["spy_close"]).diff()
    gld = np.log(panel["gld_close"]).diff()
    dxy = np.log(panel["dxy_tv_close"]).diff()
    df = pd.concat({"SPY": spy, "GLD": gld, "DXY": dxy}, axis=1)
    fig, ax = plt.subplots(figsize=(9, 4.5))
    for col, color in zip(df.columns, [PALETTE["institutional"], PALETTE["liquidity"], PALETTE["macro"]]):
        c = btc.rolling(60, min_periods=60).corr(df[col])
        ax.plot(c.index, c.values, label=f"BTC vs {col}", color=color, lw=1.4)
    ax.axhline(0, color="#555", lw=0.6)
    for d, lbl in [(BTC_ETF, "BTC ETF"), (ETH_ETF, "ETH ETF"), (FTX, "FTX"), (SVB, "SVB")]:
        ax.axvline(d, color="#111", lw=0.6, alpha=0.5, ls=":")
    ax.set_title("Rolling 60-day correlation — BTC daily log return vs SPY / GLD / DXY")
    ax.set_ylabel("correlation")
    ax.legend()
    return _save(fig, "F10_btc_tradfi_corr")


def main() -> None:
    panel = load_panel()

    out_paths: list[Path] = []
    out_paths.append(f01_cumulative_returns(panel))
    out_paths.append(f02_rolling_r2("btc"))
    out_paths.append(f02_rolling_r2("eth"))
    out_paths.append(f03_partial_r2("btc"))
    out_paths.append(f03_partial_r2("eth"))
    out_paths.append(f05_sup_f("btc"))
    out_paths.append(f05_sup_f("eth"))
    out_paths.append(f07_fevd_heatmap())
    out_paths.append(f08_event_cars())
    out_paths.append(f09_coverage(panel))
    out_paths.append(f10_rolling_corr(panel))

    for p in out_paths:
        print("[ok]", p)


if __name__ == "__main__":
    main()
