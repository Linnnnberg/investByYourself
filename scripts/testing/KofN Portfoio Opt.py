# Create a general-purpose script that selects the best K-of-N asset combination
# using robust, out-of-sample backtesting with multiple weighting schemes and objectives.
# The script downloads historical prices with yfinance and evaluates every N-choose-K subset.
# It outputs a CSV summary plus the equity curve and weights for the winning combo.
#
# It also includes walk-forward training for methods that require estimation (inverse-vol, MVO),
# realistic transaction cost modeling, and several metrics (CAGR, Vol, Sharpe, Sortino, MaxDD,
# Calmar, Ulcer, VaR, CVaR, Avg Pairwise Corr, Turnover).
#
# Users can choose the objective (Sharpe/Calmar/Sortino/composite), weighting scheme,
# rebalance cadence, and training window length.
#
# Save to /mnt/data for user download.


script_path = "/mnt/data/combo_selector_framework.py"

script = r'''#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
K-of-N Asset Combination Selector (General Framework)
====================================================

Goal
----
Given a set of assets (tickers) and a target combination size K, find the "best"
combination according to robust, out-of-sample backtests and chosen objective metrics.
This can *replace* a simple sector-rotation rule by directly evaluating stability
and efficiency of subsets over time.

Key Features
------------
- Data: Downloads Adjusted Close (dividends/splits-adjusted) via yfinance.
- Sampling: Converts to month-end prices by default (configurable).
- Rebalancing: Monthly (default) or quarterly rebalances.
- Weighting schemes:
  * equal: equal weight each rebalance
  * inv_vol: inverse of training-window volatility (long-only, normalized)
  * mvo: mean-variance optimizer (unconstrained Σ^-1 μ projected to long-only, with ridge)
- Training: Walk-forward. For inv_vol/mvo, compute weights from *past* returns only.
- Costs: Transaction costs modeled via turnover * (bps/1e4).
- Metrics: CAGR, Annualized Vol, Sharpe, Sortino, Max Drawdown, Calmar, Ulcer Index,
           VaR(95%), CVaR(95%), Avg Pairwise Corr, Average Turnover, Cost Drag.
- Objective: Choose winner by Sharpe/Calmar/Sortino or a composite score with corr penalty.
- Outputs: `combo_results.csv`, plus `equity_curve_best.csv` and `weights_best.csv` for the winner.

Usage Examples
--------------
python combo_selector_framework.py --tickers "SPY,TLT,GLD,EFA,IEF" --k 3 --start 2006-01-01 --objective sharpe

python combo_selector_framework.py --tickers_file tickers.txt --k 4 --weighting mvo --train_win 36 \
    --objective composite --alpha_sharpe 1.0 --beta_calmar 0.5 --gamma_maxdd 0.5 --delta_corr 0.5

Dependencies
------------
pip install yfinance pandas numpy tabulate

Notes
-----
- This is a research tool; always sanity-check results and avoid overfitting.
- If N is large, N-choose-K can be huge. Limit N or sample subsets.
"""

from __future__ import annotations

import argparse
import itertools
import math
import sys
from dataclasses import dataclass
from typing import Dict, Iterable, List, Optional, Sequence, Tuple

import numpy as np
import pandas as pd

try:
    import yfinance as yf
except Exception as e:
    raise SystemExit("Please install yfinance: pip install yfinance") from e

try:
    from tabulate import tabulate
except Exception:
    tabulate = None


# --------------------------- Utility functions ---------------------------

def _to_datetime_index(df: pd.DataFrame) -> pd.DataFrame:
    if not isinstance(df.index, pd.DatetimeIndex):
        df.index = pd.to_datetime(df.index)
    return df.sort_index()


def download_adj_close(tickers: Sequence[str], start: Optional[str] = None, end: Optional[str] = None,
                       interval: str = "1d") -> pd.DataFrame:
    """Download Adjusted Close for tickers via yfinance. Returns wide DataFrame (Date x Ticker)."""
    if not tickers:
        raise ValueError("No tickers provided.")
    data = yf.download(
        tickers=list(set(tickers)),
        start=start,
        end=end,
        auto_adjust=False,
        interval=interval,
        progress=False,
        threads=True,
        group_by="ticker",
    )
    # Build Adj Close wide table
    if isinstance(data.columns, pd.MultiIndex):
        out = {}
        for t in tickers:
            col = (t, "Adj Close")
            if col in data.columns:
                s = data[col].copy()
            else:
                # try lowercase for some locales
                s = data[(t, "Adj Close".lower())]
            s.name = t
            out[t] = s
        adj = pd.concat(out.values(), axis=1)
    else:
        # Single-index columns case: direct 'Adj Close'
        if "Adj Close" in data.columns:
            adj = data["Adj Close"].copy()
            # Ensure all requested tickers present
            missing = [t for t in tickers if t not in adj.columns]
            if missing:
                print("Warning: Missing tickers in download:", missing)
        else:
            raise RuntimeError("Unexpected yfinance response format. No 'Adj Close' found.")
    adj = _to_datetime_index(adj)
    return adj


def to_period_prices(adj: pd.DataFrame, freq: str = "M") -> pd.DataFrame:
    """Resample to period-end prices (M for month-end, Q for quarter-end)."""
    return adj.resample(freq).last()


def pct_change(ser: pd.Series) -> pd.Series:
    return ser.pct_change()


def max_drawdown(equity: pd.Series) -> float:
    roll = equity.cummax()
    dd = equity / roll - 1.0
    return float(dd.min())


def ulcer_index(equity: pd.Series) -> float:
    roll = equity.cummax()
    dd = (equity / roll - 1.0) * 100.0  # percent drawdown
    return float(np.sqrt(np.mean(np.square(dd))))


def annualized_return(returns: pd.Series, periods_per_year: int) -> float:
    if returns.empty:
        return np.nan
    growth = float((1.0 + returns).prod())
    years = len(returns) / periods_per_year
    if years <= 0:
        return np.nan
    return growth ** (1.0 / years) - 1.0


def annualized_vol(returns: pd.Series, periods_per_year: int) -> float:
    return float(returns.std(ddof=0) * math.sqrt(periods_per_year))


def sharpe_ratio(returns: pd.Series, periods_per_year: int, rf: float = 0.0) -> float:
    ar = annualized_return(returns, periods_per_year)
    av = annualized_vol(returns, periods_per_year)
    if av == 0 or np.isnan(av):
        return np.nan
    return (ar - rf) / av


def downside_deviation(returns: pd.Series, mar: float = 0.0, periods_per_year: int = 12) -> float:
    shortfall = np.minimum(0.0, returns - mar)
    return float(np.sqrt(np.mean(shortfall ** 2)) * math.sqrt(periods_per_year))


def sortino_ratio(returns: pd.Series, periods_per_year: int, rf: float = 0.0) -> float:
    ar = annualized_return(returns, periods_per_year)
    dd = downside_deviation(returns - (rf / periods_per_year), mar=0.0, periods_per_year=periods_per_year)
    if dd == 0 or np.isnan(dd):
        return np.nan
    return (ar - rf) / dd


def hist_var_cvar(returns: pd.Series, alpha: float = 0.95) -> Tuple[float, float]:
    if returns.empty:
        return (np.nan, np.nan)
    q = returns.quantile(1.0 - alpha)  # e.g., 5th percentile for 95% VaR
    tail = returns[returns <= q]
    var = float(q)
    cvar = float(tail.mean()) if len(tail) else np.nan
    return (var, cvar)


def avg_pairwise_corr(returns: pd.DataFrame) -> float:
    if returns.shape[1] < 2:
        return np.nan
    corr = returns.corr()
    tri = corr.where(np.triu(np.ones_like(corr, dtype=bool), k=1))
    vals = tri.stack().values
    return float(np.mean(vals)) if len(vals) else np.nan


def herfindahl_index(weights: pd.Series) -> float:
    """HHI diversification metric: sum(w_i^2). Lower is more diversified."""
    return float((weights ** 2).sum())


# --------------------------- Weighting schemes ---------------------------

def equal_weights(assets: Sequence[str]) -> pd.Series:
    n = len(assets)
    if n == 0:
        return pd.Series(dtype=float)
    w = pd.Series(1.0 / n, index=assets, dtype=float)
    return w


def inv_vol_weights(train_returns: pd.DataFrame, epsilon: float = 1e-8) -> pd.Series:
    vols = train_returns.std(ddof=0).replace(0.0, np.nan)
    inv = 1.0 / vols
    inv = inv.replace([np.inf, -np.inf], np.nan).fillna(0.0)
    if inv.sum() == 0.0:
        # fallback to equal weights
        return equal_weights(train_returns.columns)
    w = inv / inv.sum()
    return w


def mvo_weights(train_returns: pd.DataFrame, ridge: float = 1e-4, allow_negative: bool = False,
                wmax: float = 1.0) -> pd.Series:
    """
    Unconstrained mean-variance "max Sharpe" approximation: w ∝ Σ^-1 μ.
    Then project to long-only if allow_negative=False, clip to wmax, renormalize.
    """
    mu = train_returns.mean()
    Sigma = train_returns.cov()

    # Ridge for stability
    if ridge > 0:
        Sigma = Sigma + ridge * np.eye(Sigma.shape[0])

    try:
        invSigma = pd.DataFrame(np.linalg.inv(Sigma.values), index=Sigma.index, columns=Sigma.columns)
    except np.linalg.LinAlgError:
        # fallback: use diagonal k*I
        invSigma = pd.DataFrame(np.eye(Sigma.shape[0]) / (Sigma.values.diagonal() + 1e-8),
                                index=Sigma.index, columns=Sigma.columns)

    raw = invSigma.dot(mu)
    if raw.abs().sum() == 0.0:
        w = equal_weights(train_returns.columns)
    else:
        w = raw / raw.abs().sum()  # scale by L1 to control extremes

    if not allow_negative:
        w = w.clip(lower=0.0)

    # Cap and renormalize
    if wmax < 1.0:
        w = w.clip(upper=wmax)
    if w.sum() == 0.0:
        w = equal_weights(train_returns.columns)
    else:
        w = w / w.sum()
    return w


# --------------------------- Backtest Engine ---------------------------

@dataclass
class Config:
    k: int
    weighting: str = "equal"   # "equal"|"inv_vol"|"mvo"
    rebalance: str = "M"       # "M" (monthly) or "Q" (quarterly)
    train_win: int = 36        # months of training window (for inv_vol/mvo)
    start: Optional[str] = None
    end: Optional[str] = None
    tcost_bps: float = 5.0
    objective: str = "sharpe"  # "sharpe"|"calmar"|"sortino"|"composite"
    alpha_sharpe: float = 1.0  # composite weights
    beta_calmar: float = 0.5
    gamma_maxdd: float = 0.5   # penalty
    delta_corr: float = 0.5    # penalty
    periods_per_year: int = 12


def compute_weights(method: str, assets: Sequence[str], train_rets: pd.DataFrame, cfg: Config) -> pd.Series:
    if method == "equal":
        return equal_weights(assets)
    elif method == "inv_vol":
        return inv_vol_weights(train_rets[assets])
    elif method == "mvo":
        return mvo_weights(train_rets[assets], ridge=1e-3, allow_negative=False, wmax=0.5)
    else:
        raise ValueError(f"Unknown weighting method: {method}")


def backtest_combo(prices_m: pd.DataFrame, combo: Sequence[str], cfg: Config) -> Tuple[pd.Series, pd.DataFrame]:
    """Walk-forward backtest for a given combo. Returns (monthly returns, monthly weights)."""
    # Use prices for combo; drop incomplete months
    pr = prices_m[list(combo)].dropna(how="any")

    if pr.shape[0] < cfg.train_win + 12:  # need at least train + 1 year
        return pd.Series(dtype=float), pd.DataFrame()

    rets = pr.pct_change().dropna(how="any")

    # Rebalance dates: use all months after we have at least train_win months
    dates = rets.index
    weights = pd.DataFrame(index=rets.index, columns=combo, data=0.0)

    prev_w = pd.Series(0.0, index=combo)
    first_idx = cfg.train_win  # first rebalance after initial training window

    for i in range(first_idx, len(dates)):
        dt = dates[i]
        # Determine last rebalance depending on cadence
        if cfg.rebalance == "Q":
            # rebalance on quarter ends (every 3 months)
            is_reb = (dt.month in (3, 6, 9, 12))
        else:
            # monthly
            is_reb = True

        if is_reb:
            train_start = dates[i - cfg.train_win]
            train_end = dates[i - 1]
            train_slice = rets.loc[train_start:train_end]
            w = compute_weights(cfg.weighting, combo, train_slice, cfg)
        else:
            w = prev_w.copy()

        weights.loc[dt] = w.values
        prev_w = w

    # Shift weights to apply next-period returns (avoid look-ahead)
    weights = weights.shift(1).fillna(0.0)

    # Portfolio returns before costs
    port_rets_gross = (weights * rets).sum(axis=1)

    # Transaction costs via turnover each period
    weight_changes = weights.diff().abs().sum(axis=1).fillna(0.0)
    costs = (cfg.tcost_bps / 1e4) * weight_changes
    port_rets_net = port_rets_gross - costs

    return port_rets_net, weights


def summarize_metrics(returns: pd.Series, weights: pd.DataFrame, asset_daily: Optional[pd.DataFrame],
                      cfg: Config) -> Dict[str, float]:
    if returns.empty:
        return {k: np.nan for k in ["CAGR","AnnVol","Sharpe","Sortino","MaxDD","Calmar","Ulcer","VaR95","CVaR95","AvgPairCorr","TurnoverAvg","CostDrag"]}

    equity = (1.0 + returns).cumprod()
    cagr = annualized_return(returns, cfg.periods_per_year)
    vol = annualized_vol(returns, cfg.periods_per_year)
    sharpe = sharpe_ratio(returns, cfg.periods_per_year, rf=0.0)
    sortino = sortino_ratio(returns, cfg.periods_per_year, rf=0.0)
    mdd = max_drawdown(equity)
    calmar = (cagr / abs(mdd)) if mdd < 0 else np.nan
    ulcer = ulcer_index(equity)
    var95, cvar95 = hist_var_cvar(returns, alpha=0.95)

    # Average pairwise correlation using *daily* returns if provided (more granularity)
    if asset_daily is not None:
        daily_combo = asset_daily[weights.columns].dropna(how="any")
        avgcorr = avg_pairwise_corr(daily_combo.pct_change().dropna(how="any"))
    else:
        avgcorr = np.nan

    turnover = float(weights.diff().abs().sum(axis=1).mean()) if not weights.empty else np.nan
    cost_drag = float((cfg.tcost_bps / 1e4) * (weights.diff().abs().sum(axis=1).mean())) if not weights.empty else np.nan

    return {
        "CAGR": cagr,
        "AnnVol": vol,
        "Sharpe": sharpe,
        "Sortino": sortino,
        "MaxDD": mdd,
        "Calmar": calmar,
        "Ulcer": ulcer,
        "VaR95": var95,
        "CVaR95": cvar95,
        "AvgPairCorr": avgcorr,
        "TurnoverAvg": turnover,
        "CostDrag": cost_drag,
    }


def composite_score(row: pd.Series, cfg: Config) -> float:
    # Higher better. Penalize MaxDD magnitude and AvgPairCorr.
    sharpe = row.get("Sharpe", np.nan)
    calmar = row.get("Calmar", np.nan)
    maxdd = row.get("MaxDD", np.nan)
    corr = row.get("AvgPairCorr", np.nan)
    # Replace NaNs with -inf penalties
    sharpe = -1e9 if np.isnan(sharpe) else sharpe
    calmar = -1e9 if np.isnan(calmar) else calmar
    maxdd_pen = 0.0 if np.isnan(maxdd) else abs(maxdd)
    corr_pen = 0.0 if np.isnan(corr) else corr
    return float(cfg.alpha_sharpe * sharpe + cfg.beta_calmar * calmar - cfg.gamma_maxdd * maxdd_pen - cfg.delta_corr * corr_pen)


def choose_winner(df: pd.DataFrame, cfg: Config) -> pd.Series:
    dd = df.copy()
    if cfg.objective == "sharpe":
        dd = dd.sort_values(by=["Sharpe","MaxDD","CAGR"], ascending=[False, True, False])
    elif cfg.objective == "calmar":
        dd = dd.sort_values(by=["Calmar","MaxDD","Sharpe"], ascending=[False, True, False])
    elif cfg.objective == "sortino":
        dd = dd.sort_values(by=["Sortino","MaxDD","Sharpe"], ascending=[False, True, False])
    elif cfg.objective == "composite":
        dd["Composite"] = dd.apply(lambda r: composite_score(r, cfg), axis=1)
        dd = dd.sort_values(by=["Composite","MaxDD","Sharpe"], ascending=[False, True, False])
    else:
        raise ValueError(f"Unknown objective: {cfg.objective}")
    return dd.iloc[0]


# --------------------------- Main Runner ---------------------------

def run(cfg: Config, tickers: Sequence[str]) -> None:
    print(f"Tickers (N={len(tickers)}):", ", ".join(tickers))
    if cfg.k < 1 or cfg.k > len(tickers):
        raise SystemExit(f"--k must be between 1 and N={len(tickers)}")

    # Download daily first (for corr calc), then resample
    daily = download_adj_close(tickers, start=cfg.start, end=cfg.end, interval="1d")
    # Drop tickers with too little data
    min_daily = 252 * 3  # ~3 years minimum
    keep = [t for t in tickers if t in daily.columns and daily[t].notna().sum() >= min_daily]
    if len(keep) < cfg.k:
        raise SystemExit("Not enough tickers with sufficient history for the requested K.")

    if len(keep) < len(tickers):
        dropped = [t for t in tickers if t not in keep]
        print("Dropping due to insufficient history:", dropped)
    daily = daily[keep]

    prices_m = to_period_prices(daily, "M").dropna(how="any")

    # Evaluate all N-choose-K combos (warn if huge)
    from math import comb as nCk
    total_combos = nCk(len(keep), cfg.k)
    if total_combos > 5000:
        print(f"Warning: {total_combos} combinations — this may take a while. Consider reducing N or K.", file=sys.stderr)

    rows = []
    weight_book: Dict[str, pd.DataFrame] = {}
    eq_book: Dict[str, pd.Series] = {}

    for combo in itertools.combinations(keep, cfg.k):
        combo = tuple(combo)
        returns, weights = backtest_combo(prices_m, combo, cfg)
        if returns.empty:
            continue
        mets = summarize_metrics(returns, weights, asset_daily=daily, cfg=cfg)
        eq = (1.0 + returns).cumprod()
        key = ",".join(combo)
        rows.append({
            "Combo": key,
            "Start": str(returns.index.min().date()),
            "End": str(returns.index.max().date()),
            "Months": int(len(returns)),
            **mets,
        })
        weight_book[key] = weights
        eq_book[key] = eq

    if not rows:
        raise SystemExit("No valid combinations produced results. Try a later start date or smaller K.")

    results = pd.DataFrame(rows)

    # Choose winner
    winner = choose_winner(results, cfg)

    # Save outputs
    results_sorted = results.sort_values(
        by=["Sharpe","MaxDD","CAGR"], ascending=[False, True, False]
    ) if cfg.objective == "sharpe" else (
        results.sort_values(by=["Calmar","MaxDD","Sharpe"], ascending=[False, True, False]) if cfg.objective == "calmar" else (
            results.sort_values(by=["Sortino","MaxDD","Sharpe"], ascending=[False, True, False]) if cfg.objective == "sortino" else (
                results.assign(Composite=results.apply(lambda r: composite_score(r, cfg), axis=1)).sort_values(by=["Composite","MaxDD","Sharpe"], ascending=[False, True, False])
            )
        )
    )
    results_sorted.to_csv("combo_results.csv", index=False)

    wkey = winner["Combo"]
    eq_book[wkey].to_frame("Equity").to_csv("equity_curve_best.csv")
    weight_book[wkey].to_csv("weights_best.csv")

    print("\n=== Top Results ===")
    if tabulate is not None:
        print(tabulate(results_sorted.head(20), headers="keys", tablefmt="github", floatfmt=".4f"))
    else:
        print(results_sorted.head(20).to_string(index=False, float_format=lambda x: f"{x:.4f}"))

    print("\n=== Winner ===")
    print(winner.to_string())

    # Multiple testing advisory
    print(f"\n[Advisory] You evaluated {len(results)} combinations. Treat top metrics cautiously to avoid overfitting.")
    print("Consider re-running with a different date range, adding a holdout period, or tightening training windows.")


def parse_args() -> Tuple[Config, List[str]]:
    ap = argparse.ArgumentParser(description="Select best K-of-N asset combination via robust backtests.")
    g = ap.add_argument_group("Universe")
    g.add_argument("--tickers", type=str, default=None, help="Comma-separated list of tickers (e.g., 'SPY,TLT,GLD')")
    g.add_argument("--tickers_file", type=str, default=None, help="Path to a file with one ticker per line")

    h = ap.add_argument_group("Backtest")
    h.add_argument("--k", type=int, required=True, help="Number of assets per combination")
    h.add_argument("--start", type=str, default=None, help="Start date (YYYY-MM-DD)")
    h.add_argument("--end", type=str, default=None, help="End date (YYYY-MM-DD)")
    h.add_argument("--rebalance", type=str, choices=["M","Q"], default="M", help="Rebalance cadence: M or Q")
    h.add_argument("--tcost_bps", type=float, default=5.0, help="Transaction cost per side in basis points")

    w = ap.add_argument_group("Weighting & Training")
    w.add_argument("--weighting", type=str, choices=["equal","inv_vol","mvo"], default="equal", help="Weighting scheme")
    w.add_argument("--train_win", type=int, default=36, help="Training window in months for inv_vol/mvo")

    o = ap.add_argument_group("Objective")
    o.add_argument("--objective", type=str, choices=["sharpe","calmar","sortino","composite"], default="sharpe", help="Selection objective")
    o.add_argument("--alpha_sharpe", type=float, default=1.0, help="Composite: weight on Sharpe")
    o.add_argument("--beta_calmar", type=float, default=0.5, help="Composite: weight on Calmar")
    o.add_argument("--gamma_maxdd", type=float, default=0.5, help="Composite: penalty on |MaxDD|")
    o.add_argument("--delta_corr", type=float, default=0.5, help="Composite: penalty on AvgPairCorr")

    a = ap.parse_args()

    # Collect tickers
    tickers: List[str] = []
    if a.tickers:
        tickers += [t.strip() for t in a.tickers.split(",") if t.strip()]
    if a.tickers_file:
        with open(a.tickers_file, "r", encoding="utf-8") as f:
            tickers += [line.strip() for line in f if line.strip()]
    tickers = list(dict.fromkeys(tickers))  # de-duplicate preserving order
    if not tickers:
        raise SystemExit("Provide --tickers or --tickers_file.")

    cfg = Config(
        k=a.k, weighting=a.weighting, rebalance=a.rebalance,
        train_win=a.train_win, start=a.start, end=a.end, tcost_bps=a.tcost_bps,
        objective=a.objective, alpha_sharpe=a.alpha_sharpe, beta_calmar=a.beta_calmar,
        gamma_maxdd=a.gamma_maxdd, delta_corr=a.delta_corr
    )
    return cfg, tickers


if __name__ == "__main__":
    cfg, tickers = parse_args()
    run(cfg, tickers)
'''

with open(script_path, "w", encoding="utf-8") as f:
    f.write(script)

script_path
