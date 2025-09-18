#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Nikkei 225 RSI Analysis Script
==============================
Finds the 7 companies with lowest RSI 12 values below 33.
Uses yfinance for data collection and leverages existing patterns.
"""

from datetime import datetime
from typing import Dict, List

import numpy as np
import pandas as pd
import yfinance as yf


class Nikkei225RSIAnalyzer:
    """Analyzes RSI 12 for Nikkei 225 companies."""

    def __init__(self):
        """Initialize the analyzer."""
        # Top 30 Nikkei 225 companies by market cap
        self.nikkei225_symbols = [
            "7203.T",  # Toyota Motor
            "6758.T",  # Sony Group
            "6861.T",  # Keyence
            "9984.T",  # SoftBank Group
            "8306.T",  # Mitsubishi UFJ Financial Group
            "9432.T",  # NTT
            "8035.T",  # Tokyo Electron
            "4063.T",  # Shin-Etsu Chemical
            "4568.T",  # Daiichi Sankyo
            "6954.T",  # Fanuc
            "7741.T",  # Hoya
            "4519.T",  # Chugai Pharmaceutical
            "6098.T",  # Recruit Holdings
            "6981.T",  # Murata Manufacturing
            "4503.T",  # Astellas Pharma
            "7974.T",  # Nintendo
            "8031.T",  # Mitsui & Co
            "7267.T",  # Honda Motor
            "4502.T",  # Takeda Pharmaceutical
            "6752.T",  # Panasonic
            "4901.T",  # Fujifilm Holdings
            "2801.T",  # Kikkoman
            "8001.T",  # ITOCHU
            "3407.T",  # Asahi Kasei
            "2914.T",  # Japan Tobacco
            "6503.T",  # Mitsubishi Electric
            "8058.T",  # Mitsubishi
            "8002.T",  # Marubeni
            "3401.T",  # Teijin
            "6501.T",  # Hitachi
        ]

    def compute_rsi(self, prices: pd.Series, period: int) -> pd.Series:
        """Calculate RSI with specified period using Wilder's method (matches Yahoo Finance)."""
        delta = prices.diff()
        gain = delta.where(delta > 0, 0)
        loss = -delta.where(delta < 0, 0)

        # Wilder's RSI calculation
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
        return rsi.fillna(50.0)

    def compute_multiple_rsi(
        self, prices: pd.Series, periods: List[int] = [6, 12, 30]
    ) -> Dict[str, pd.Series]:
        """Calculate RSI for multiple periods."""
        rsi_data = {}
        for period in periods:
            rsi_data[f"rsi_{period}"] = self.compute_rsi(prices, period)
        return rsi_data

    def get_company_name(self, symbol: str) -> str:
        """Get company name from symbol."""
        company_names = {
            "7203.T": "Toyota Motor",
            "6758.T": "Sony Group",
            "6861.T": "Keyence",
            "9984.T": "SoftBank Group",
            "8306.T": "Mitsubishi UFJ Financial Group",
            "9432.T": "NTT",
            "8035.T": "Tokyo Electron",
            "4063.T": "Shin-Etsu Chemical",
            "4568.T": "Daiichi Sankyo",
            "6954.T": "Fanuc",
            "7741.T": "Hoya",
            "4519.T": "Chugai Pharmaceutical",
            "6098.T": "Recruit Holdings",
            "6981.T": "Murata Manufacturing",
            "4503.T": "Astellas Pharma",
            "7974.T": "Nintendo",
            "8031.T": "Mitsui & Co",
            "7267.T": "Honda Motor",
            "4502.T": "Takeda Pharmaceutical",
            "6752.T": "Panasonic",
            "4901.T": "Fujifilm Holdings",
            "2801.T": "Kikkoman",
            "8001.T": "ITOCHU",
            "3407.T": "Asahi Kasei",
            "2914.T": "Japan Tobacco",
            "6503.T": "Mitsubishi Electric",
            "8058.T": "Mitsubishi",
            "8002.T": "Marubeni",
            "3401.T": "Teijin",
            "6501.T": "Hitachi",
        }
        return company_names.get(symbol, symbol)

    def collect_market_data(
        self, symbols: List[str], days: int = 90
    ) -> Dict[str, pd.DataFrame]:
        """Collect market data for symbols using yfinance."""
        print(f"📊 Collecting market data for {len(symbols)} Nikkei 225 companies...")

        market_data = {}
        for symbol in symbols:
            try:
                # Download data using yfinance
                ticker = yf.Ticker(symbol)
                hist = ticker.history(period=f"{days}d")

                if not hist.empty:
                    market_data[symbol] = hist
                    print(f"✅ Collected data for {symbol}")
                else:
                    print(f"❌ No data for {symbol}")

            except Exception as e:
                print(f"❌ Error collecting {symbol}: {str(e)}")
                continue

        return market_data

    def calculate_rsi_analysis(
        self, market_data: Dict[str, pd.DataFrame]
    ) -> pd.DataFrame:
        """Calculate RSI 6, 12, 30 for all companies and find lowest values."""
        print("🧮 Calculating RSI 6, 12, 30 for all companies...")

        results = []
        for symbol, df in market_data.items():
            if df.empty or len(df) < 30:  # Need at least 30 days for RSI 30
                continue

            # Get closing prices
            prices = df["Close"]

            # Calculate multiple RSI periods
            rsi_data = self.compute_multiple_rsi(prices, [6, 12, 30])

            # Get company name from symbol
            company_name = self.get_company_name(symbol)

            # Debug info for 6098.T
            if symbol == "6098.T":
                print(f"\n🔍 DEBUG INFO FOR {symbol} ({company_name}):")
                print(
                    f"   Data range: {df.index[0].strftime('%Y-%m-%d')} to {df.index[-1].strftime('%Y-%m-%d')}"
                )
                print(f"   Total days: {len(df)}")
                print(f"   Last 5 prices: {prices.tail().tolist()}")
                print(f"   RSI 6: {rsi_data['rsi_6'].iloc[-1]:.2f}")
                print(f"   RSI 12: {rsi_data['rsi_12'].iloc[-1]:.2f}")
                print(f"   RSI 30: {rsi_data['rsi_30'].iloc[-1]:.2f}")
                print(f"   Price range: {prices.min():.2f} - {prices.max():.2f}")

                # Check if we can get more recent data
                try:
                    ticker = yf.Ticker(symbol)
                    info = ticker.info
                    print(f"   Market state: {info.get('marketState', 'Unknown')}")
                    print(f"   Current price: {info.get('currentPrice', 'N/A')}")
                    print(f"   Previous close: {info.get('previousClose', 'N/A')}")
                except:
                    print("   Could not get additional market info")

            # Calculate price change metrics
            price_change_1d = (
                ((prices.iloc[-1] - prices.iloc[-2]) / prices.iloc[-2] * 100)
                if len(prices) > 1
                else 0
            )
            price_change_5d = (
                ((prices.iloc[-1] - prices.iloc[-6]) / prices.iloc[-6] * 100)
                if len(prices) > 5
                else 0
            )
            price_change_30d = (
                ((prices.iloc[-1] - prices.iloc[-31]) / prices.iloc[-31] * 100)
                if len(prices) > 30
                else 0
            )

            results.append(
                {
                    "symbol": symbol,
                    "company_name": company_name,
                    "rsi_6": round(rsi_data["rsi_6"].iloc[-1], 2),
                    "rsi_12": round(rsi_data["rsi_12"].iloc[-1], 2),
                    "rsi_30": round(rsi_data["rsi_30"].iloc[-1], 2),
                    "current_price": round(prices.iloc[-1], 2),
                    "price_change_1d": round(price_change_1d, 2),
                    "price_change_5d": round(price_change_5d, 2),
                    "price_change_30d": round(price_change_30d, 2),
                    "date": df.index[-1].strftime("%Y-%m-%d"),
                }
            )

        # Convert to DataFrame and sort by RSI 12
        df_results = pd.DataFrame(results)
        df_results = df_results.sort_values("rsi_12")

        return df_results

    def find_lowest_rsi_companies(
        self, df_results: pd.DataFrame, threshold: float = 33.0, top_n: int = 7
    ) -> pd.DataFrame:
        """Find companies with lowest RSI 12 values below threshold."""
        # Filter companies with RSI below threshold
        low_rsi = df_results[df_results["rsi_12"] < threshold]

        # Get top N lowest RSI companies
        top_lowest = low_rsi.head(top_n)

        return top_lowest

    def save_price_time_series(
        self, market_data: Dict[str, pd.DataFrame], output_dir: str = "."
    ):
        """Save price time series data for all companies."""
        print("💾 Saving price time series data...")

        for symbol, df in market_data.items():
            if df.empty:
                continue

            # Create price time series with RSI data
            prices = df["Close"]
            rsi_data = self.compute_multiple_rsi(prices, [6, 12, 30])

            # Create comprehensive time series DataFrame
            time_series = pd.DataFrame(
                {
                    "date": df.index,
                    "open": df["Open"],
                    "high": df["High"],
                    "low": df["Low"],
                    "close": df["Close"],
                    "volume": df["Volume"],
                    "rsi_6": rsi_data["rsi_6"],
                    "rsi_12": rsi_data["rsi_12"],
                    "rsi_30": rsi_data["rsi_30"],
                }
            )

            # Save to CSV
            filename = f"{output_dir}/price_timeseries_{symbol.replace('.T', '')}.csv"
            time_series.to_csv(filename, index=False)
            print(f"   ✅ Saved {symbol} time series: {filename}")

    def run_analysis(self):
        """Run the complete Nikkei 225 RSI analysis."""
        print("🚀 Starting Nikkei 225 RSI Analysis")
        print("=" * 50)

        # Collect market data
        market_data = self.collect_market_data(self.nikkei225_symbols)

        if not market_data:
            print("❌ No market data collected. Exiting.")
            return

        # Calculate RSI analysis
        df_results = self.calculate_rsi_analysis(market_data)

        if df_results.empty:
            print("❌ No RSI calculations completed. Exiting.")
            return

        # Find lowest RSI companies
        lowest_rsi = self.find_lowest_rsi_companies(df_results, threshold=33.0, top_n=7)

        # Display results
        print("\n📈 NIKKEI 225 RSI ANALYSIS RESULTS")
        print("=" * 70)
        print(f"Total companies analyzed: {len(df_results)}")
        print(
            f"Companies with RSI 12 < 33: {len(df_results[df_results['rsi_12'] < 33])}"
        )
        print(f"Companies with RSI 6 < 30: {len(df_results[df_results['rsi_6'] < 30])}")
        print(
            f"Companies with RSI 30 < 40: {len(df_results[df_results['rsi_30'] < 40])}"
        )
        print("\n🏆 TOP 7 LOWEST RSI 12 COMPANIES:")
        print("-" * 70)
        print(
            f"{'#':<2} {'Company':<25} {'Symbol':<8} {'RSI6':<6} {'RSI12':<6} {'RSI30':<6} {'Price':<10} {'1D%':<6} {'5D%':<6} {'30D%':<6}"
        )
        print("-" * 70)

        for i, (_, row) in enumerate(lowest_rsi.iterrows(), 1):
            print(
                f"{i:2d}. {row['company_name']:<25} {row['symbol']:<8} {row['rsi_6']:5.1f}  {row['rsi_12']:5.1f}  {row['rsi_30']:5.1f}  ¥{row['current_price']:8.2f} {row['price_change_1d']:5.1f}% {row['price_change_5d']:5.1f}% {row['price_change_30d']:5.1f}%"
            )

        # Save to CSV
        output_file = (
            f"nikkei225_rsi_analysis_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv"
        )
        df_results.to_csv(output_file, index=False)
        print(f"\n💾 Results saved to: {output_file}")

        # Save price time series data
        self.save_price_time_series(market_data)

        return df_results


def main():
    """Main function to run the analysis."""
    analyzer = Nikkei225RSIAnalyzer()
    analyzer.run_analysis()


if __name__ == "__main__":
    main()
