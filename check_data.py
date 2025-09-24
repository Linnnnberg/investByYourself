#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import numpy as np
import pandas as pd
import yfinance as yf

# Get the actual data for 6098.T with different periods
ticker = yf.Ticker("6098.T")

# Try different data periods
print("=== TESTING DIFFERENT DATA PERIODS ===")
for period in ["1mo", "3mo", "6mo", "1y"]:
    hist = ticker.history(period=period)
    if not hist.empty:
        print(
            f'{period}: {len(hist)} days, {hist.index[0].strftime("%Y-%m-%d")} to {hist.index[-1].strftime("%Y-%m-%d")}'
        )

print()
print("=== CHECKING INTRADAY DATA ===")
try:
    # Try to get intraday data
    intraday = ticker.history(period="1d", interval="1m")
    if not intraday.empty:
        print(f"Intraday data: {len(intraday)} minutes, latest: {intraday.index[-1]}")
        print(f'Latest intraday price: {intraday["Close"].iloc[-1]}')
    else:
        print("No intraday data available")
except Exception as e:
    print(f"Intraday data error: {e}")

print()
print("=== CHECKING YAHOO FINANCE RSI DIRECTLY ===")
# Check if Yahoo Finance provides RSI directly
info = ticker.info
rsi_keys = [k for k in info.keys() if "rsi" in k.lower() or "relative" in k.lower()]
if rsi_keys:
    print("RSI-related keys found:")
    for key in rsi_keys:
        print(f"  {key}: {info[key]}")
else:
    print("No RSI keys found in info")

print()
print("=== COMPARING RSI CALCULATIONS ===")
# Get 3 months of data for better RSI calculation
hist = ticker.history(period="3mo")
prices = hist["Close"]


# Method 1: Wilder's RSI 12
def wilders_rsi(prices, period=12):
    delta = prices.diff()
    gain = delta.where(delta > 0, 0)
    loss = -delta.where(delta < 0, 0)

    avg_gain = gain.rolling(window=period).mean()
    avg_loss = loss.rolling(window=period).mean()

    # Apply Wilder's smoothing
    for i in range(period, len(prices)):
        if not pd.isna(avg_gain.iloc[i - 1]) and not pd.isna(avg_loss.iloc[i - 1]):
            avg_gain.iloc[i] = (
                avg_gain.iloc[i - 1] * (period - 1) + gain.iloc[i]
            ) / period
            avg_loss.iloc[i] = (
                avg_loss.iloc[i - 1] * (period - 1) + loss.iloc[i]
            ) / period

    rs = avg_gain / avg_loss
    rsi = 100 - (100 / (1 + rs))
    return rsi


# Method 2: Standard RSI 14
def standard_rsi(prices, period=14):
    delta = prices.diff()
    gain = (delta.where(delta > 0, 0)).rolling(window=period).mean()
    loss = (-delta.where(delta < 0, 0)).rolling(window=period).mean()
    rs = gain / loss
    rsi = 100 - (100 / (1 + rs))
    return rsi


rsi_12 = wilders_rsi(prices, 12)
rsi_14 = standard_rsi(prices, 14)

print(f"Wilder RSI 12: {rsi_12.iloc[-1]:.2f}")
print(f"Standard RSI 14: {rsi_14.iloc[-1]:.2f}")
print(
    f'Data range: {hist.index[0].strftime("%Y-%m-%d")} to {hist.index[-1].strftime("%Y-%m-%d")}'
)
print(f"Total days: {len(hist)}")
