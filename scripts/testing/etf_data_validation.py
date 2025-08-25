#!/usr/bin/env python3
"""
ETF Data Validation & Cleaning Script
-------------------------------------
Fetches 5-year daily Adjusted Close data for a 4-ETF sector set
(XLK, XLF, XLE, XLU) plus SPY baseline from Yahoo Finance and
runs validation + light cleaning before backtesting.

Usage:
  python etf_data_validation.py --start 2019-01-01 --end 2025-08-25 \
    --tickers XLK XLF XLE XLU SPY --outdir ./data --max_ffill 3

Requires:
  - Python 3.9+
  - pandas, numpy, yfinance, tabulate

Notes:
  - We use 'Adj Close' (total-return friendly for splits/dividends)
  - Cleans short gaps via limited forward-fill (configurable)
  - Writes raw and cleaned CSVs + JSON validation report
"""

import argparse
import datetime as dt
import json
import os
import sys

import numpy as np
import pandas as pd

try:
    import yfinance as yf
except ImportError:
    print("yfinance is required. Install with: pip install yfinance", file=sys.stderr)
    sys.exit(1)

try:
    from tabulate import tabulate
except ImportError:
    tabulate = None  # degrade gracefully


DEFAULT_TICKERS = ["XLK", "XLF", "XLE", "XLU", "SPY"]


def parse_args():
    """Parse command line arguments."""
    p = argparse.ArgumentParser(description="ETF data validation & cleaning")
    p.add_argument(
        "--start",
        type=str,
        default=(dt.date.today() - dt.timedelta(days=365 * 5)).isoformat(),
        help="Start date YYYY-MM-DD (default: 5Y ago)",
    )
    p.add_argument(
        "--end",
        type=str,
        default=dt.date.today().isoformat(),
        help="End date YYYY-MM-DD (default: today)",
    )
    p.add_argument(
        "--tickers",
        nargs="+",
        default=DEFAULT_TICKERS,
        help="List of tickers to download",
    )
    p.add_argument(
        "--outdir",
        type=str,
        default="./etf_data",
        help="Output directory for CSVs and reports",
    )
    p.add_argument(
        "--max_ffill",
        type=int,
        default=3,
        help="Max consecutive business days to forward-fill during cleaning",
    )
    p.add_argument("--debug", action="store_true", help="Print extra diagnostics")
    return p.parse_args()


def download_data(tickers, start, end):
    """Download daily OHLCV and extract Adj Close (and Volume for diagnostics)."""
    try:
        df = yf.download(
            tickers,
            start=start,
            end=end,
            progress=False,
            auto_adjust=False,
            group_by="ticker",
        )

        # yfinance returns a multiindex columns frame for multiple tickers
        # We'll build a tidy dict of DataFrames: adj_close, volume
        adj = pd.DataFrame(index=df.index)
        vol = pd.DataFrame(index=df.index)

        for t in tickers:
            if (t, "Adj Close") in df.columns:
                adj[t] = df[(t, "Adj Close")]
            elif "Adj Close" in df.columns:
                # single ticker case
                adj[t] = df["Adj Close"]
            else:
                print(f"[WARN] Adj Close not found for {t}", file=sys.stderr)

            if (t, "Volume") in df.columns:
                vol[t] = df[(t, "Volume")]
            elif "Volume" in df.columns:
                vol[t] = df["Volume"]

        return adj.sort_index(), vol.sort_index()

    except Exception as e:
        print(f"Error downloading data: {e}", file=sys.stderr)
        sys.exit(1)


def nyse_business_days(start, end):
    """Generate NYSE-like business days using pandas bdate_range (approx)."""
    try:
        idx = pd.bdate_range(
            start, end, freq="C"
        )  # business days (Mon-Fri, no holidays)
        # Note: For precise NYSE holidays, replace with pandas_market_calendars in production
        return idx
    except Exception as e:
        print(f"Error generating business days: {e}", file=sys.stderr)
        return pd.DatetimeIndex([])


def validate_prices(adj_close: pd.DataFrame, vol: pd.DataFrame, debug=False):
    """Run validation checks, return dict of issues + per-ticker stats."""
    report = {"per_ticker": {}, "global": {}}

    # Basic index validations
    idx = adj_close.index
    duplicate_idx = idx.duplicated().sum()
    not_monotonic = not idx.is_monotonic_increasing

    report["global"]["duplicate_index_entries"] = int(duplicate_idx)
    report["global"]["index_monotonic_increasing"] = bool(not not_monotonic)

    # Check for NaNs & non-positive prices
    for t in adj_close.columns:
        s = adj_close[t]
        nans = int(s.isna().sum())
        zeros = int((s == 0).sum())
        negs = int((s < 0).sum())

        # Daily returns & extreme moves
        rets = s.pct_change()
        # Exclude zeros/NaNs
        rz = rets.replace([np.inf, -np.inf], np.nan).dropna()
        if len(rz) > 2 and rz.std() > 0:
            z = (rz - rz.mean()) / rz.std()
            extreme = int((z.abs() > 6).sum())  # 6-sigma heuristic
        else:
            extreme = 0

        # Missing business days vs approximate calendar
        start_date, end_date = s.first_valid_index(), s.last_valid_index()
        if start_date is not None and end_date is not None:
            try:
                biz = nyse_business_days(start_date, end_date)
                missing_days = int(len(set(biz) - set(s.dropna().index)))
            except Exception:
                missing_days = -1
        else:
            missing_days = -1  # no data

        report["per_ticker"][t] = {
            "n_obs": int(s.dropna().shape[0]),
            "nans": nans,
            "zeros": zeros,
            "negs": negs,
            "extreme_return_days(>6σ)": extreme,
            "missing_business_days(approx)": missing_days,
        }

        if debug:
            print(
                f"[DEBUG] {t}: obs={report['per_ticker'][t]['n_obs']} "
                f"NaN={nans} zero={zeros} neg={negs} extreme6σ={extreme} missingDays≈{missing_days}"
            )

    # Cross-ticker aligned NaNs (dates where any ticker is NaN)
    any_nan_dates = adj_close.isna().any(axis=1).sum()
    all_nan_dates = adj_close.isna().all(axis=1).sum()
    report["global"]["rows_with_any_nan"] = int(any_nan_dates)
    report["global"]["rows_with_all_nan"] = int(all_nan_dates)

    return report


def clean_prices(adj_close: pd.DataFrame, max_ffill: int = 3):
    """Light cleaning: limited forward fill for short gaps; drop rows still all-NaN; ensure float."""
    cleaned = adj_close.copy()

    # Limit forward fill to short gaps only (up to max_ffill)
    cleaned = cleaned.fillna(method="ffill", limit=max_ffill)

    # Backward fill day-1 start if still missing
    cleaned = cleaned.fillna(method="bfill", limit=1)

    # Drop rows that are still entirely missing
    cleaned = cleaned.dropna(how="all")

    # Ensure numeric dtype
    cleaned = cleaned.astype(float)

    return cleaned


def print_report(report: dict):
    """Pretty print validation report."""
    print("\n=== ETF Data Validation Report ===")

    # Global
    g = report["global"]
    print(f"Duplicate index entries: {g['duplicate_index_entries']}")
    print(f"Index monotonic increasing: {g['index_monotonic_increasing']}")
    print(f"Rows with any NaN: {g['rows_with_any_nan']}")
    print(f"Rows with all NaN: {g['rows_with_all_nan']}")

    # Per ticker
    headers = ["Ticker", "Obs", "NaN", "Zero", "Neg", "Extreme>6σ", "Missing BizDays≈"]
    rows = []
    for t, d in report["per_ticker"].items():
        rows.append(
            [
                t,
                d["n_obs"],
                d["nans"],
                d["zeros"],
                d["negs"],
                d["extreme_return_days(>6σ)"],
                d["missing_business_days(approx)"],
            ]
        )

    if tabulate:
        print("\nPer-Ticker Summary:")
        print(tabulate(rows, headers=headers, tablefmt="github"))
    else:
        print("\nPer-Ticker Summary (install 'tabulate' for nicer table):")
        print(headers)
        for r in rows:
            print(r)


def main():
    """Main function."""
    args = parse_args()

    # Create output directory
    os.makedirs(args.outdir, exist_ok=True)

    print(f"Downloading ETF data for {', '.join(args.tickers)}")
    print(f"Date range: {args.start} to {args.end}")
    print(f"Output directory: {args.outdir}")

    # Download
    adj, vol = download_data(args.tickers, args.start, args.end)

    if adj.empty:
        print("No data downloaded. Exiting.", file=sys.stderr)
        sys.exit(1)

    # Save raw data
    raw_csv = os.path.join(args.outdir, "raw_adj_close.csv")
    adj.to_csv(raw_csv, index=True)
    vol_csv = os.path.join(args.outdir, "raw_volume.csv")
    vol.to_csv(vol_csv, index=True)

    # Validate raw
    print("\nValidating raw data...")
    raw_report = validate_prices(adj, vol, debug=args.debug)
    print_report(raw_report)

    with open(os.path.join(args.outdir, "validation_raw.json"), "w") as f:
        json.dump(raw_report, f, indent=2, default=str)

    # Clean
    print("\nCleaning data...")
    cleaned = clean_prices(adj, max_ffill=args.max_ffill)
    cleaned_csv = os.path.join(args.outdir, "cleaned_adj_close.csv")
    cleaned.to_csv(cleaned_csv, index=True)

    # Re-validate cleaned
    print("\nValidating cleaned data...")
    cleaned_report = validate_prices(cleaned, vol.loc[cleaned.index], debug=args.debug)
    print("\n--- After Cleaning ---")
    print_report(cleaned_report)

    with open(os.path.join(args.outdir, "validation_cleaned.json"), "w") as f:
        json.dump(cleaned_report, f, indent=2, default=str)

    # Save a quick README
    readme = f"""ETF Data Validation & Cleaning
================================
Tickers: {', '.join(args.tickers)}
Date Range: {args.start} → {args.end}

Files in this folder:
- raw_adj_close.csv        (Yahoo Finance 'Adj Close' by date)
- raw_volume.csv           (Yahoo Finance 'Volume' by date)
- cleaned_adj_close.csv    (forward-filled up to {args.max_ffill} business days, bfilled 1 day)
- validation_raw.json      (validation metrics before cleaning)
- validation_cleaned.json  (validation metrics after cleaning)

Notes:
- Use cleaned_adj_close.csv for backtests.
- Consider replacing the business-day approximation with an exchange calendar
  (pandas_market_calendars) for exact holiday handling in production.
"""
    with open(os.path.join(args.outdir, "README.txt"), "w") as f:
        f.write(readme)

    print(f"\n✅ Successfully saved files to: {args.outdir}")
    print(f"  - {raw_csv}")
    print(f"  - {vol_csv}")
    print(f"  - {cleaned_csv}")
    print("  - validation_raw.json, validation_cleaned.json, README.txt")


if __name__ == "__main__":
    main()
