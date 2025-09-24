# -*- coding: utf-8 -*-
"""RSI debugging script for financial analysis."""

from datetime import datetime

import numpy as np
import pandas as pd
import yfinance as yf

# Get the actual data for 6098.T
ticker = yf.Ticker("6098.T")
hist = ticker.history(period="30d")

print("=== DATA FRESHNESS CHECK ===")
now = datetime.now()
print(f"Current time: {now}")
print(f"Data last updated: {hist.index[-1]}")
print(f"Data age: {now - hist.index[-1].to_pydatetime()}")
print()

# Check market info
info = ticker.info
print("=== MARKET STATUS ===")
print(f"Market state: {info.get('marketState', 'Unknown')}")
print(f"Regular market price: {info.get('regularMarketPrice', 'N/A')}")
print(f"Current price: {info.get('currentPrice', 'N/A')}")
print(f"Previous close: {info.get('previousClose', 'N/A')}")
print()

# Different RSI calculations
prices = hist["Close"]


# Method 1: Our current exponential method
def rsi_exponential(prices, period=12):
    """Calculate exponential RSI."""
    delta = prices.diff()
    gain = np.where(delta > 0, delta, 0.0)
    loss = np.where(delta < 0, -delta, 0.0)
    roll_up = (
        pd.Series(gain, index=prices.index).ewm(alpha=1 / period, adjust=False).mean()
    )
    roll_down = (
        pd.Series(loss, index=prices.index).ewm(alpha=1 / period, adjust=False).mean()
    )
    rs = roll_up / (roll_down.replace(0, np.nan))
    rsi = 100 - (100 / (1 + rs))
    return rsi


# Method 2: Simple moving average
def rsi_sma(prices, period=12):
    """Calculate SMA-based RSI."""
    delta = prices.diff()
    gain = (delta.where(delta > 0, 0)).rolling(window=period).mean()
    loss = (-delta.where(delta < 0, 0)).rolling(window=period).mean()
    rs = gain / loss
    rsi = 100 - (100 / (1 + rs))
    return rsi


# Method 3: Wilder RSI (most common)
def wilders_rsi(prices, period=12):
    """Calculate Wilder's RSI."""
    delta = prices.diff()
    gain = delta.where(delta > 0, 0)
    loss = -delta.where(delta < 0, 0)

    avg_gain = gain.rolling(window=period).mean()
    avg_loss = loss.rolling(window=period).mean()

    # Apply Wilder smoothing
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


print("=== RSI CALCULATION COMPARISON ===")
rsi_exp = rsi_exponential(prices, 12)
rsi_sma_12 = rsi_sma(prices, 12)
rsi_wilders_12 = wilders_rsi(prices, 12)
rsi_wilders_14 = wilders_rsi(prices, 14)

print(f"Exponential RSI 12: {rsi_exp.iloc[-1]:.2f}")
print(f"SMA RSI 12: {rsi_sma_12.iloc[-1]:.2f}")
print(f"Wilder RSI 12: {rsi_wilders_12.iloc[-1]:.2f}")
print(f"Wilder RSI 14: {rsi_wilders_14.iloc[-1]:.2f}")
print()

print("=== PRICE DATA FOR LAST 15 DAYS ===")
print(prices.tail(15))
