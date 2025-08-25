import os

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from caas_jupyter_tools import display_dataframe_to_user
from dateutil.relativedelta import relativedelta
from reportlab.lib import colors
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.platypus import (
    Image,
    Paragraph,
    SimpleDocTemplate,
    Spacer,
    Table,
    TableStyle,
)

np.random.seed(123)


# ----- Helper to generate daily price paths with target annual returns -----
def generate_year_path(dates, annual_return, ann_vol, start_price=100.0):
    n = len(dates)
    # target log-return for the year
    target_lr = np.log(1 + annual_return)
    # baseline daily log return
    base_lr = target_lr / n
    # daily vol for logs approximately ann_vol/sqrt(252)
    daily_vol = ann_vol / np.sqrt(252.0)
    noise = np.random.randn(n) * daily_vol
    # force zero-mean noise to keep annual on target in log space
    noise = noise - noise.mean()
    daily_lr = base_lr + noise
    # adjust last point to hit target exactly
    adj = target_lr - daily_lr.sum()
    daily_lr[-1] += adj
    prices = [start_price]
    for lr in daily_lr:
        prices.append(prices[-1] * np.exp(lr))
    return np.array(prices[1:])


# ----- Dates -----
dates = pd.bdate_range("2020-01-01", "2024-12-31")

# Split by year
years = sorted(set(dates.year))

# Target annual returns (illustrative) and volatilities per ETF per year
targets = {
    "XLK": {2020: 0.40, 2021: 0.35, 2022: -0.30, 2023: 0.55, 2024: 0.25},
    "XLF": {2020: -0.02, 2021: 0.25, 2022: -0.12, 2023: 0.24, 2024: 0.12},
    "XLE": {2020: -0.35, 2021: 0.50, 2022: 0.65, 2023: -0.05, 2024: 0.15},
    "XLU": {2020: 0.02, 2021: 0.12, 2022: -0.01, 2023: -0.05, 2024: 0.06},
    "SPY": {2020: 0.18, 2021: 0.28, 2022: -0.18, 2023: 0.26, 2024: 0.16},
}

vols = {
    "XLK": {2020: 0.30, 2021: 0.28, 2022: 0.35, 2023: 0.30, 2024: 0.22},
    "XLF": {2020: 0.25, 2021: 0.22, 2022: 0.28, 2023: 0.22, 2024: 0.18},
    "XLE": {2020: 0.45, 2021: 0.40, 2022: 0.50, 2023: 0.35, 2024: 0.30},
    "XLU": {2020: 0.18, 2021: 0.16, 2022: 0.20, 2023: 0.18, 2024: 0.15},
    "SPY": {2020: 0.24, 2021: 0.20, 2022: 0.28, 2023: 0.20, 2024: 0.18},
}

# Build price series
prices = {}
for ticker in ["XLK", "XLF", "XLE", "XLU", "SPY"]:
    series = []
    start_price = 100.0
    for y in years:
        year_dates = dates[dates.year == y]
        p = generate_year_path(
            year_dates, targets[ticker][y], vols[ticker][y], start_price=start_price
        )
        series.append(pd.Series(p, index=year_dates))
        start_price = p[-1]
    prices[ticker] = pd.concat(series)

prices_df = pd.DataFrame(prices)

# Compute daily returns
rets = prices_df.pct_change().fillna(0.0)

# Quarterly rebalance portfolio with 25% in each sector ETF
tickers = ["XLK", "XLF", "XLE", "XLU"]
weights = pd.Series([0.25, 0.25, 0.25, 0.25], index=tickers)

# Rebalance dates = last business day of each quarter
quarter_ends = rets.resample("Q").last().index
quarter_ends = [d for d in quarter_ends if d in rets.index]

port_val = 100.0
port_vals = []
current_weights = weights.copy()
holdings = (port_val * current_weights) / prices_df.loc[dates[0], tickers]

last_date = dates[0]
for dt in dates:
    if dt == dates[0]:
        port_vals.append((dt, port_val))
        continue
    # update holdings by returns
    day_ret = rets.loc[dt, tickers]  # vector of returns
    holdings = holdings * (1 + day_ret)
    port_val = (
        holdings * prices_df.loc[dt, tickers] / prices_df.loc[dt, tickers]
    ).sum()  # sums holdings value
    # rebalance on quarter end
    if dt in quarter_ends:
        port_val = (
            holdings * prices_df.loc[dt, tickers] / prices_df.loc[dt, tickers]
        ).sum()
        holdings = (port_val * weights) / prices_df.loc[dt, tickers]
    port_vals.append((dt, port_val))

port_series = pd.Series({d: v for d, v in port_vals})
bench_series = prices_df["SPY"] / prices_df["SPY"].iloc[0] * 100.0


# Compute metrics
def compute_metrics(equity):
    daily_rets = equity.pct_change().dropna()
    ann_ret = (equity.iloc[-1] / equity.iloc[0]) ** (252 / len(daily_rets)) - 1
    ann_vol = daily_rets.std() * np.sqrt(252)
    sharpe = ann_ret / ann_vol if ann_vol != 0 else np.nan
    # max drawdown
    roll_max = equity.cummax()
    dd = equity / roll_max - 1.0
    max_dd = dd.min()
    return ann_ret, ann_vol, sharpe, max_dd


port_metrics = compute_metrics(port_series)
spy_metrics = compute_metrics(bench_series)


# Yearly returns
def yearly_returns(equity):
    yr = equity.resample("Y").last()
    yr_rets = yr.pct_change().dropna()
    yr_rets.index = yr_rets.index.year
    return yr_rets


yr_port = yearly_returns(port_series)
yr_spy = yearly_returns(bench_series)

metrics_df = pd.DataFrame(
    {
        "Metric": ["CAGR", "Ann. Volatility", "Sharpe (rf=0)", "Max Drawdown"],
        "Sector 25%x4 (Quarterly Rebal.)": [
            f"{port_metrics[0]:.2%}",
            f"{port_metrics[1]:.2%}",
            f"{port_metrics[2]:.2f}",
            f"{port_metrics[3]:.2%}",
        ],
        "SPY Baseline": [
            f"{spy_metrics[0]:.2%}",
            f"{spy_metrics[1]:.2%}",
            f"{spy_metrics[2]:.2f}",
            f"{spy_metrics[3]:.2%}",
        ],
    }
)

# Save data to CSVs
out_dir = "/mnt/data/sector_backtest"
os.makedirs(out_dir, exist_ok=True)
prices_df.to_csv(os.path.join(out_dir, "sim_prices_2020_2024.csv"))
port_series.to_frame("sector_portfolio").to_csv(
    os.path.join(out_dir, "sector_portfolio_equity.csv")
)
bench_series.to_frame("SPY").to_csv(os.path.join(out_dir, "spy_equity.csv"))
yr_comp = pd.DataFrame(
    {"Sector 25%x4": yr_port.values, "SPY": yr_spy.reindex(yr_port.index).values},
    index=yr_port.index,
)
yr_comp.to_csv(os.path.join(out_dir, "yearly_returns.csv"))

# Charts: Equity curves
plt.figure(figsize=(8, 4))
plt.plot(
    port_series.index,
    port_series / port_series.iloc[0] * 100,
    label="Sector 25%x4 (Quarterly Rebal.)",
)
plt.plot(
    bench_series.index, bench_series / bench_series.iloc[0] * 100, label="SPY Baseline"
)
plt.title("Equity Curve (Normalized to 100) — 2020–2024 (Illustrative)")
plt.legend()
eq_curve = os.path.join(out_dir, "equity_curve.png")
plt.savefig(eq_curve)
plt.close()

# Rolling 6M excess return
rolling_window = 126
port_roll = (
    port_series.pct_change().add(1).rolling(rolling_window).apply(np.prod, raw=True) - 1
)
spy_roll = (
    bench_series.pct_change().add(1).rolling(rolling_window).apply(np.prod, raw=True)
    - 1
)
excess_roll = port_roll - spy_roll
plt.figure(figsize=(8, 4))
plt.plot(
    excess_roll.index,
    excess_roll,
    label="Sector Portfolio - SPY (6M Rolling Excess Return)",
)
plt.axhline(0, linestyle="--")
plt.title("Rolling 6-Month Relative Performance")
plt.legend()
rel_perf = os.path.join(out_dir, "rolling_excess.png")
plt.savefig(rel_perf)
plt.close()


# Drawdowns
def drawdown_curve(equity):
    roll_max = equity.cummax()
    return equity / roll_max - 1.0


port_dd = drawdown_curve(port_series)
spy_dd = drawdown_curve(bench_series)

plt.figure(figsize=(8, 4))
plt.plot(port_dd.index, port_dd, label="Sector Portfolio Drawdown")
plt.title("Drawdown — Sector Portfolio")
dd_port_png = os.path.join(out_dir, "drawdown_port.png")
plt.legend()
plt.savefig(dd_port_png)
plt.close()

plt.figure(figsize=(8, 4))
plt.plot(spy_dd.index, spy_dd, label="SPY Drawdown")
plt.title("Drawdown — SPY")
dd_spy_png = os.path.join(out_dir, "drawdown_spy.png")
plt.legend()
plt.savefig(dd_spy_png)
plt.close()

# Sector weights drift between rebalances (simulate by tracking market weights)
weights_df = pd.DataFrame(index=dates, columns=tickers, dtype=float)
# Start at equal
weights_df.iloc[0] = weights.values
# Track weights via price drift; rebalance quarterly
last_holdings = (100 * weights) / prices_df.loc[dates[0], tickers]
for i, dt in enumerate(dates[1:], 1):
    # update holdings
    last_holdings = last_holdings * (1 + rets.loc[dt, tickers])
    # compute weights
    total_val = (
        last_holdings * prices_df.loc[dt, tickers] / prices_df.loc[dt, tickers]
    ).sum()
    weights_df.loc[dt] = (
        last_holdings * prices_df.loc[dt, tickers] / prices_df.loc[dt, tickers]
    ) / total_val
    # Rebalance on quarter end
    if dt in quarter_ends:
        last_holdings = (total_val * weights) / prices_df.loc[dt, tickers]
        weights_df.loc[dt] = weights

plt.figure(figsize=(8, 4))
for t in tickers:
    plt.plot(weights_df.index, weights_df[t], label=t)
plt.title("Sector Weights Over Time (Quarterly Rebalance)")
plt.legend()
weights_png = os.path.join(out_dir, "weights_over_time.png")
plt.savefig(weights_png)
plt.close()

# Build PDF report
pdf_path = os.path.join(out_dir, "Sector_4ETF_5yr_Backtest.pdf")
styles = getSampleStyleSheet()
doc = SimpleDocTemplate(pdf_path, pagesize=A4)
elements = []
elements.append(
    Paragraph(
        "<b>Sector Rotation — 4 ETF Portfolio vs S&P 500 (2020–2024)</b>",
        styles["Title"],
    )
)
elements.append(Spacer(1, 12))
elements.append(
    Paragraph(
        "Method: Equal-weight XLK, XLF, XLE, XLU at 25% each; rebalance at quarter-end. "
        "Baseline: SPY. <br/><i>Note: This is an illustrative simulation calibrated to plausible annual returns; "
        "use live data for precise figures.</i>",
        styles["Normal"],
    )
)
elements.append(Spacer(1, 12))

# Metrics table
data = [metrics_df.columns.tolist()] + metrics_df.values.tolist()
t = Table(data, hAlign="LEFT")
t.setStyle(
    TableStyle(
        [
            ("BACKGROUND", (0, 0), (-1, 0), colors.lightgrey),
            ("TEXTCOLOR", (0, 0), (-1, 0), colors.black),
            ("ALIGN", (0, 0), (-1, -1), "LEFT"),
            ("GRID", (0, 0), (-1, -1), 0.25, colors.grey),
            ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
        ]
    )
)
elements.append(t)
elements.append(Spacer(1, 12))

elements.append(Paragraph("<b>Equity Curve</b>", styles["Heading2"]))
elements.append(Image(eq_curve, width=400, height=200))
elements.append(Spacer(1, 12))

elements.append(
    Paragraph(
        "<b>Rolling 6-Month Relative Performance (Portfolio minus SPY)</b>",
        styles["Heading2"],
    )
)
elements.append(Image(rel_perf, width=400, height=200))
elements.append(Spacer(1, 12))

elements.append(Paragraph("<b>Drawdowns</b>", styles["Heading2"]))
elements.append(Image(dd_port_png, width=400, height=200))
elements.append(Image(dd_spy_png, width=400, height=200))
elements.append(Spacer(1, 12))

elements.append(Paragraph("<b>Sector Weights Over Time</b>", styles["Heading2"]))
elements.append(Image(weights_png, width=400, height=200))
elements.append(Spacer(1, 12))

doc.build(elements)

# Display metrics table to user
display_dataframe_to_user(
    "Sector 4-ETF vs SPY — Key Metrics (Illustrative 2020–2024)",
    pd.DataFrame(
        {
            "Metric": metrics_df["Metric"],
            "Sector 25%x4 (Quarterly Rebal.)": metrics_df[
                "Sector 25%x4 (Quarterly Rebal.)"
            ],
            "SPY Baseline": metrics_df["SPY Baseline"],
        }
    ).set_index("Metric"),
)

pdf_path
