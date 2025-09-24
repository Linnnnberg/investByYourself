# Hedge Strategy Backtest (Stocks/ETFs only, no options)
# ---------------------------------------------------------
# This notebook builds and runs a simple, practical hedge strategy that uses
# just two ETFs (or stocks): a risk asset (e.g., SPY) and a defensive asset
# (e.g., TLT). It:
#   1) Simulates or loads historical prices,
#   2) Applies a trend regime filter (200D SMA of the risk asset),
#   3) Allocates using inverse-vol weighting in Risk-ON, 100% defensive in Risk-OFF,
#   4) Backtests the portfolio with daily rebalancing (weights lagged by 1 day),
#   5) Outputs charts (equity curve, rolling vol), RSI, and a metrics table.
#
# Notes:
# - If you upload CSVs to /mnt/data named "SPY.csv" and "TLT.csv" with columns ["Date","Close"],
#   the code will automatically use them instead of simulation.
# - With no files present (the current case), we simulate realistic, correlated price paths
#   so you can see the strategy and charts run end-to-end immediately.
#
# You can download the generated backtest series at the end as a CSV.


import os
from datetime import datetime
from math import sqrt

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd

# === Helper functions ===


def rsi(series: pd.Series, period: int = 14) -> pd.Series:
    delta = series.diff()
    up = delta.clip(lower=0)
    down = -delta.clip(upper=0)
    gain = up.ewm(alpha=1 / period, adjust=False).mean()
    loss = down.ewm(alpha=1 / period, adjust=False).mean()
    rs = gain / (loss.replace(0, np.nan))
    rsi_val = 100 - (100 / (1 + rs))
    return rsi_val.fillna(50.0)


def ann_return(daily_returns: pd.Series, freq: int = 252) -> float:
    cum = (1 + daily_returns).prod()
    years = len(daily_returns) / freq
    if years == 0:
        return np.nan
    return cum ** (1 / years) - 1


def ann_vol(daily_returns: pd.Series, freq: int = 252) -> float:
    return daily_returns.std() * sqrt(freq)


def sharpe(daily_returns: pd.Series, rf: float = 0.0, freq: int = 252) -> float:
    # rf is annual risk-free; convert to daily approximation
    if len(daily_returns) == 0:
        return np.nan
    daily_rf = (1 + rf) ** (1 / freq) - 1
    excess = daily_returns - daily_rf
    vol = excess.std() * sqrt(freq)
    if vol == 0:
        return np.nan
    return (excess.mean() * freq) / vol


def max_drawdown(cum_returns: pd.Series) -> float:
    # cum_returns should be cumulative equity curve (not returns)
    peak = cum_returns.cummax()
    dd = (cum_returns / peak) - 1.0
    return dd.min()


def calmar(daily_returns: pd.Series) -> float:
    cagr = ann_return(daily_returns)
    mdd = abs(max_drawdown((1 + daily_returns).cumprod()))
    if mdd == 0:
        return np.nan
    return cagr / mdd


def inverse_vol_weights(vol_spy: float, vol_tlt: float) -> tuple:
    inv = np.array(
        [1 / vol_spy if vol_spy > 0 else 0, 1 / vol_tlt if vol_tlt > 0 else 0]
    )
    if inv.sum() == 0:
        return (0.5, 0.5)
    w = inv / inv.sum()
    return (float(w[0]), float(w[1]))


# === Load data (CSV if provided; else simulate) ===


def load_or_simulate():
    spy_path = "/mnt/data/SPY.csv"
    tlt_path = "/mnt/data/TLT.csv"

    if os.path.exists(spy_path) and os.path.exists(tlt_path):
        spy = (
            pd.read_csv(spy_path, parse_dates=["Date"])
            .sort_values("Date")
            .set_index("Date")
        )
        tlt = (
            pd.read_csv(tlt_path, parse_dates=["Date"])
            .sort_values("Date")
            .set_index("Date")
        )
        spy = spy.rename(columns={"Close": "SPY"})
        tlt = tlt.rename(columns={"Close": "TLT"})
        df = spy[["SPY"]].join(tlt[["TLT"]], how="inner").dropna()
        source = "Loaded CSVs from /mnt/data"
        return df, source

    # Simulate 10.5 years of business days ending today (Europe/Berlin date is 2025-08-21)
    dates = pd.bdate_range(end=pd.Timestamp("2025-08-20"), periods=2650)  # ~10.5 years
    n = len(dates)
    # Parameters for SPY (risk) and TLT (defensive)
    mu = np.array([0.08, 0.04])  # annual drift
    vol = np.array([0.18, 0.12])  # annual vol
    rho = -0.30  # correlation
    cov = (
        np.array(
            [[vol[0] ** 2, rho * vol[0] * vol[1]], [rho * vol[0] * vol[1], vol[1] ** 2]]
        )
        / 252.0
    )  # daily covariance

    # Cholesky for correlated daily returns
    L = np.linalg.cholesky(cov)
    z = np.random.normal(size=(n, 2))
    daily_returns = (L @ z.T).T + (mu / 252.0)  # GBM log-return approx

    # Build price paths (start 100)
    prices = np.zeros((n, 2))
    prices[0, :] = 100.0
    for i in range(1, n):
        prices[i, :] = prices[i - 1, :] * (1 + daily_returns[i, :])

    df = pd.DataFrame(prices, index=dates, columns=["SPY", "TLT"])
    source = "Simulated correlated price paths (since no CSVs were found)"
    return df, source


prices, data_source = load_or_simulate()

# === Compute indicators and signals ===

# Daily returns
rets = prices.pct_change().fillna(0.0)

# 200-day SMA trend on SPY to determine regime
sma_200 = prices["SPY"].rolling(200).mean()
risk_on = prices["SPY"] >= sma_200

# 60-day realized vol for inverse-vol weights (use rolling std of daily returns)
roll_vol_spy = rets["SPY"].rolling(60).std()
roll_vol_tlt = rets["TLT"].rolling(60).std()

# Default weights
w_spy = pd.Series(0.5, index=prices.index)
w_tlt = pd.Series(0.5, index=prices.index)

# Apply regime & inverse-vol weighting
for dt in prices.index:
    if np.isnan(roll_vol_spy.loc[dt]) or np.isnan(roll_vol_tlt.loc[dt]):
        # warm-up period
        w_s, w_b = 0.5, 0.5
    else:
        w_s, w_b = inverse_vol_weights(roll_vol_spy.loc[dt], roll_vol_tlt.loc[dt])
    if not bool(risk_on.loc[dt]):
        # Risk-OFF: 100% in TLT
        w_s, w_b = 0.0, 1.0
    w_spy.loc[dt], w_tlt.loc[dt] = w_s, w_b

# Lag weights by 1 day to avoid look-ahead bias
w_spy_lag = w_spy.shift(1).fillna(0.5)
w_tlt_lag = w_tlt.shift(1).fillna(0.5)

# Strategy daily returns
strategy_rets = (w_spy_lag * rets["SPY"]) + (w_tlt_lag * rets["TLT"])
strategy_equity = (1 + strategy_rets).cumprod()

# Benchmarks equity curves
spy_equity = (1 + rets["SPY"]).cumprod()
tlt_equity = (1 + rets["TLT"]).cumprod()

# RSI(14) for SPY and TLT
rsi_spy = rsi(prices["SPY"], 14)
rsi_tlt = rsi(prices["TLT"], 14)

# Rolling annualized vol (63-day ~ 3 months)
roll_vol_strategy_ann = strategy_rets.rolling(63).std() * sqrt(252)
roll_vol_spy_ann = rets["SPY"].rolling(63).std() * sqrt(252)

# === Metrics table ===
metrics = pd.DataFrame(
    {
        "CAGR": [
            ann_return(strategy_rets),
            ann_return(rets["SPY"]),
            ann_return(rets["TLT"]),
        ],
        "Ann. Vol": [
            ann_vol(strategy_rets),
            ann_vol(rets["SPY"]),
            ann_vol(rets["TLT"]),
        ],
        "Sharpe (rf=0%)": [
            sharpe(strategy_rets, rf=0.0),
            sharpe(rets["SPY"], rf=0.0),
            sharpe(rets["TLT"], rf=0.0),
        ],
        "Max Drawdown": [
            max_drawdown(strategy_equity),
            max_drawdown(spy_equity),
            max_drawdown(tlt_equity),
        ],
        "Calmar": [
            calmar(strategy_rets),
            calmar(rets["SPY"]),
            calmar(rets["TLT"]),
        ],
    },
    index=["Strategy", "SPY", "TLT"],
)

# Round for display
metrics_disp = metrics * np.array(
    [100, 100, 1, 100, 1]
)  # turn rates to % for readability
metrics_disp = metrics_disp.rename(
    columns={
        "CAGR": "CAGR (%)",
        "Ann. Vol": "Ann. Vol (%)",
        "Max Drawdown": "Max DD (%)",
    }
)
metrics_disp = metrics_disp.round(
    {
        "CAGR (%)": 2,
        "Ann. Vol (%)": 2,
        "Sharpe (rf=0%)": 2,
        "Max DD (%)": 2,
        "Calmar": 2,
    }
)

# Save detailed series for download
out = pd.DataFrame(
    {
        "SPY_Close": prices["SPY"],
        "TLT_Close": prices["TLT"],
        "SPY_Return": rets["SPY"],
        "TLT_Return": rets["TLT"],
        "Weight_SPY": w_spy_lag,
        "Weight_TLT": w_tlt_lag,
        "Strategy_Return": strategy_rets,
        "Strategy_Equity": strategy_equity,
        "SPY_Equity": spy_equity,
        "TLT_Equity": tlt_equity,
        "RSI_SPY": rsi_spy,
        "RSI_TLT": rsi_tlt,
        "RollVol_Strategy_Ann": roll_vol_strategy_ann,
        "RollVol_SPY_Ann": roll_vol_spy_ann,
    }
)
csv_path = "/mnt/data/hedge_backtest_series.csv"
out.to_csv(csv_path, index_label="Date")

# === Display outputs ===

# 1) Equity curves
plt.figure(figsize=(10, 5))
plt.plot(strategy_equity.index, strategy_equity.values, label="Strategy")
plt.plot(spy_equity.index, spy_equity.values, label="SPY")
plt.plot(tlt_equity.index, tlt_equity.values, label="TLT")
plt.title("Cumulative Growth of $1")
plt.xlabel("Date")
plt.ylabel("Equity")
plt.legend()
plt.tight_layout()
plt.show()

# 2) Rolling annualized volatility
plt.figure(figsize=(10, 5))
plt.plot(roll_vol_strategy_ann.index, roll_vol_strategy_ann.values, label="Strategy")
plt.plot(roll_vol_spy_ann.index, roll_vol_spy_ann.values, label="SPY")
plt.title("63-Day Rolling Annualized Volatility")
plt.xlabel("Date")
plt.ylabel("Annualized Volatility")
plt.legend()
plt.tight_layout()
plt.show()

# 3) RSI(14) of SPY and TLT
plt.figure(figsize=(10, 4))
plt.plot(rsi_spy.index, rsi_spy.values, label="RSI SPY")
plt.plot(rsi_tlt.index, rsi_tlt.values, label="RSI TLT")
plt.axhline(70, linestyle="--", linewidth=1, label="Overbought ~70")
plt.axhline(30, linestyle="--", linewidth=1, label="Oversold ~30")
plt.ylim(0, 100)
plt.title("RSI(14)")
plt.xlabel("Date")
plt.ylabel("RSI")
plt.legend()
plt.tight_layout()
plt.show()

# 4) Show metrics table in an interactive view
from caas_jupyter_tools import display_dataframe_to_user

display_dataframe_to_user("Hedge Strategy Metrics", metrics_disp)

# Also show where data came from (loaded vs simulated)
data_source
