"""
Demo Data Collector for ETL Service
Tech-021: ETL Service Extraction

Collects real data for the Magnificent 7 stocks using Yahoo Finance API for testing purposes.
"""

import asyncio
import time
from datetime import datetime, timedelta
from typing import Any, Dict, List, Optional

import pandas as pd
import yfinance as yf
from models.test_universe import UniverseManager, get_stock_info, get_test_symbols


class DemoDataCollector:
    """Demo data collector for testing ETL functionality with real data."""

    def __init__(self):
        """Initialize the demo collector."""
        self.universe_manager = UniverseManager()
        self.rate_limit_delay = 0.1  # 100ms delay between requests
        self.max_retries = 3
        self.retry_delay = 1.0

    async def collect_company_profiles(
        self, symbols: Optional[List[str]] = None
    ) -> Dict[str, Any]:
        """Collect company profile data for the specified symbols."""
        if symbols is None:
            symbols = get_test_symbols()

        profiles = {}

        for symbol in symbols:
            try:
                print(f"Collecting profile data for {symbol}...")

                # Get stock info from universe
                stock_info = get_stock_info(symbol)
                if not stock_info:
                    print(f"Warning: {symbol} not found in test universe")
                    continue

                # Fetch data from Yahoo Finance
                ticker = yf.Ticker(symbol)
                info = ticker.info

                # Create standardized profile
                profile = {
                    "symbol": symbol,
                    "company_name": info.get("longName", stock_info.company_name),
                    "sector": info.get("sector", stock_info.sector),
                    "industry": info.get("industry", stock_info.industry),
                    "market_cap": info.get("marketCap"),
                    "enterprise_value": info.get("enterpriseValue"),
                    "description": info.get(
                        "longBusinessSummary", stock_info.description
                    ),
                    "website": info.get("website", stock_info.website),
                    "exchange": info.get("exchange", stock_info.exchange),
                    "country": info.get("country", stock_info.country),
                    "currency": info.get("currency"),
                    "employees": info.get("fullTimeEmployees"),
                    "founded_year": info.get("founded"),
                    "ceo": (
                        info.get("companyOfficers", [{}])[0].get("name")
                        if info.get("companyOfficers")
                        else None
                    ),
                    "headquarters": info.get("city", "")
                    + ", "
                    + info.get("state", "")
                    + ", "
                    + info.get("country", ""),
                    "phone": info.get("phone"),
                    "industry_rank": info.get("industryDisp"),
                    "sector_rank": info.get("sectorDisp"),
                    "collected_at": datetime.utcnow().isoformat(),
                    "data_source": "yahoo_finance",
                }

                profiles[symbol] = profile
                print(f"✅ Collected profile for {symbol}")

                # Rate limiting
                await asyncio.sleep(self.rate_limit_delay)

            except Exception as e:
                print(f"❌ Error collecting profile for {symbol}: {str(e)}")
                profiles[symbol] = {
                    "symbol": symbol,
                    "error": str(e),
                    "collected_at": datetime.utcnow().isoformat(),
                }

        return profiles

    async def collect_financial_data(
        self, symbols: Optional[List[str]] = None
    ) -> Dict[str, Any]:
        """Collect financial data for the specified symbols."""
        if symbols is None:
            symbols = get_test_symbols()

        financials = {}

        for symbol in symbols:
            try:
                print(f"Collecting financial data for {symbol}...")

                ticker = yf.Ticker(symbol)

                # Get financial statements
                income_stmt = ticker.income_stmt
                balance_sheet = ticker.balance_sheet
                cash_flow = ticker.cashflow

                # Get key financial metrics
                info = ticker.info

                financial_data = {
                    "symbol": symbol,
                    "collected_at": datetime.utcnow().isoformat(),
                    "data_source": "yahoo_finance",
                    "key_metrics": {
                        "pe_ratio": info.get("trailingPE"),
                        "forward_pe": info.get("forwardPE"),
                        "price_to_book": info.get("priceToBook"),
                        "price_to_sales": info.get("priceToSalesTrailing12Months"),
                        "debt_to_equity": info.get("debtToEquity"),
                        "current_ratio": info.get("currentRatio"),
                        "quick_ratio": info.get("quickRatio"),
                        "return_on_equity": info.get("returnOnEquity"),
                        "return_on_assets": info.get("returnOnAssets"),
                        "profit_margin": info.get("profitMargins"),
                        "operating_margin": info.get("operatingMargins"),
                        "gross_margin": info.get("grossMargins"),
                        "ebitda_margins": info.get("ebitdaMargins"),
                        "revenue_growth": info.get("revenueGrowth"),
                        "earnings_growth": info.get("earningsGrowth"),
                        "revenue_per_share": info.get("revenuePerShare"),
                        "book_value": info.get("bookValue"),
                        "cash_per_share": info.get("totalCashPerShare"),
                        "dividend_yield": info.get("dividendYield"),
                        "payout_ratio": info.get("payoutRatio"),
                        "beta": info.get("beta"),
                        "52_week_change": info.get("52WeekChange"),
                        "shares_outstanding": info.get("sharesOutstanding"),
                        "float_shares": info.get("floatShares"),
                        "shares_short": info.get("sharesShort"),
                        "shares_short_prior_month": info.get("sharesShortPriorMonth"),
                        "short_ratio": info.get("shortRatio"),
                        "short_percent_of_float": info.get("shortPercentOfFloat"),
                    },
                }

                # Add financial statements if available
                if income_stmt is not None and not income_stmt.empty:
                    financial_data["income_statement"] = {
                        "total_revenue": (
                            income_stmt.loc["Total Revenue"].iloc[0]
                            if "Total Revenue" in income_stmt.index
                            else None
                        ),
                        "gross_profit": (
                            income_stmt.loc["Gross Profit"].iloc[0]
                            if "Gross Profit" in income_stmt.index
                            else None
                        ),
                        "operating_income": (
                            income_stmt.loc["Operating Income"].iloc[0]
                            if "Operating Income" in income_stmt.index
                            else None
                        ),
                        "net_income": (
                            income_stmt.loc["Net Income"].iloc[0]
                            if "Net Income" in income_stmt.index
                            else None
                        ),
                        "ebitda": (
                            income_stmt.loc["EBITDA"].iloc[0]
                            if "EBITDA" in income_stmt.index
                            else None
                        ),
                        "period": (
                            income_stmt.columns[0].strftime("%Y-%m-%d")
                            if not income_stmt.empty
                            else None
                        ),
                    }

                if balance_sheet is not None and not balance_sheet.empty:
                    financial_data["balance_sheet"] = {
                        "total_assets": (
                            balance_sheet.loc["Total Assets"].iloc[0]
                            if "Total Assets" in balance_sheet.index
                            else None
                        ),
                        "total_liabilities": (
                            balance_sheet.loc["Total Liabilities"].iloc[0]
                            if "Total Liabilities" in balance_sheet.index
                            else None
                        ),
                        "total_equity": (
                            balance_sheet.loc["Total Equity"].iloc[0]
                            if "Total Equity" in balance_sheet.index
                            else None
                        ),
                        "cash_and_equivalents": (
                            balance_sheet.loc["Cash and Cash Equivalents"].iloc[0]
                            if "Cash and Cash Equivalents" in balance_sheet.index
                            else None
                        ),
                        "total_debt": (
                            balance_sheet.loc["Total Debt"].iloc[0]
                            if "Total Debt" in balance_sheet.index
                            else None
                        ),
                        "period": (
                            balance_sheet.columns[0].strftime("%Y-%m-%d")
                            if not balance_sheet.empty
                            else None
                        ),
                    }

                if cash_flow is not None and not cash_flow.empty:
                    financial_data["cash_flow"] = {
                        "operating_cash_flow": (
                            cash_flow.loc["Operating Cash Flow"].iloc[0]
                            if "Operating Cash Flow" in cash_flow.index
                            else None
                        ),
                        "investing_cash_flow": (
                            cash_flow.loc["Investing Cash Flow"].iloc[0]
                            if "Investing Cash Flow" in cash_flow.index
                            else None
                        ),
                        "financing_cash_flow": (
                            cash_flow.loc["Financing Cash Flow"].iloc[0]
                            if "Financing Cash Flow" in cash_flow.index
                            else None
                        ),
                        "free_cash_flow": (
                            cash_flow.loc["Free Cash Flow"].iloc[0]
                            if "Free Cash Flow" in cash_flow.index
                            else None
                        ),
                        "period": (
                            cash_flow.columns[0].strftime("%Y-%m-%d")
                            if not cash_flow.empty
                            else None
                        ),
                    }

                financials[symbol] = financial_data
                print(f"✅ Collected financial data for {symbol}")

                # Rate limiting
                await asyncio.sleep(self.rate_limit_delay)

            except Exception as e:
                print(f"❌ Error collecting financial data for {symbol}: {str(e)}")
                financials[symbol] = {
                    "symbol": symbol,
                    "error": str(e),
                    "collected_at": datetime.utcnow().isoformat(),
                }

        return financials

    async def collect_market_data(
        self, symbols: Optional[List[str]] = None, period: str = "1mo"
    ) -> Dict[str, Any]:
        """Collect market data for the specified symbols."""
        if symbols is None:
            symbols = get_test_symbols()

        market_data = {}

        for symbol in symbols:
            try:
                print(f"Collecting market data for {symbol}...")

                ticker = yf.Ticker(symbol)

                # Get historical data
                hist = ticker.history(period=period)

                if hist.empty:
                    print(f"Warning: No historical data available for {symbol}")
                    continue

                # Get current market info
                info = ticker.info

                # Calculate additional metrics
                if len(hist) > 1:
                    hist_returns = hist["Close"].pct_change()
                    volatility = hist_returns.std() * (
                        252**0.5
                    )  # Annualized volatility
                    max_drawdown = (hist["Close"] / hist["Close"].cummax() - 1).min()
                else:
                    volatility = None
                    max_drawdown = None

                market_info = {
                    "symbol": symbol,
                    "collected_at": datetime.utcnow().isoformat(),
                    "data_source": "yahoo_finance",
                    "current_price": info.get("currentPrice"),
                    "previous_close": info.get("previousClose"),
                    "open": info.get("open"),
                    "day_low": info.get("dayLow"),
                    "day_high": info.get("dayHigh"),
                    "volume": info.get("volume"),
                    "avg_volume": info.get("averageVolume"),
                    "market_cap": info.get("marketCap"),
                    "52_week_low": info.get("fiftyTwoWeekLow"),
                    "52_week_high": info.get("fiftyTwoWeekHigh"),
                    "50_day_average": info.get("fiftyDayAverage"),
                    "200_day_average": info.get("twoHundredDayAverage"),
                    "price_change": (
                        info.get("currentPrice", 0) - info.get("previousClose", 0)
                        if info.get("currentPrice") and info.get("previousClose")
                        else None
                    ),
                    "price_change_percent": (
                        (
                            (info.get("currentPrice", 0) - info.get("previousClose", 0))
                            / info.get("previousClose", 1)
                            * 100
                        )
                        if info.get("currentPrice") and info.get("previousClose")
                        else None
                    ),
                    "volatility": volatility,
                    "max_drawdown": max_drawdown,
                    "historical_data": {
                        "period": period,
                        "data_points": len(hist),
                        "start_date": (
                            hist.index[0].strftime("%Y-%m-%d")
                            if not hist.empty
                            else None
                        ),
                        "end_date": (
                            hist.index[-1].strftime("%Y-%m-%d")
                            if not hist.empty
                            else None
                        ),
                        "latest_close": (
                            hist["Close"].iloc[-1] if not hist.empty else None
                        ),
                        "latest_volume": (
                            hist["Volume"].iloc[-1] if not hist.empty else None
                        ),
                    },
                }

                market_data[symbol] = market_info
                print(f"✅ Collected market data for {symbol}")

                # Rate limiting
                await asyncio.sleep(self.rate_limit_delay)

            except Exception as e:
                print(f"❌ Error collecting market data for {symbol}: {str(e)}")
                market_data[symbol] = {
                    "symbol": symbol,
                    "error": str(e),
                    "collected_at": datetime.utcnow().isoformat(),
                }

        return market_data

    async def collect_comprehensive_data(
        self, symbols: Optional[List[str]] = None
    ) -> Dict[str, Any]:
        """Collect comprehensive data for all data types."""
        if symbols is None:
            symbols = get_test_symbols()

        print(f"🚀 Starting comprehensive data collection for {len(symbols)} symbols...")
        start_time = time.time()

        # Collect all data types
        profiles = await self.collect_company_profiles(symbols)
        financials = await self.collect_financial_data(symbols)
        market_data = await self.collect_market_data(symbols)

        # Combine all data
        comprehensive_data = {}
        for symbol in symbols:
            comprehensive_data[symbol] = {
                "profile": profiles.get(symbol, {}),
                "financials": financials.get(symbol, {}),
                "market_data": market_data.get(symbol, {}),
                "collection_summary": {
                    "symbol": symbol,
                    "profile_collected": symbol in profiles
                    and "error" not in profiles[symbol],
                    "financials_collected": symbol in financials
                    and "error" not in financials[symbol],
                    "market_data_collected": symbol in market_data
                    and "error" not in market_data[symbol],
                    "total_data_points": sum(
                        [
                            (
                                1
                                if symbol in profiles
                                and "error" not in profiles[symbol]
                                else 0
                            ),
                            (
                                1
                                if symbol in financials
                                and "error" not in financials[symbol]
                                else 0
                            ),
                            (
                                1
                                if symbol in market_data
                                and "error" not in market_data[symbol]
                                else 0
                            ),
                        ]
                    ),
                },
            }

        end_time = time.time()
        collection_time = end_time - start_time

        # Create summary
        summary = {
            "collection_summary": {
                "total_symbols": len(symbols),
                "successful_profiles": len(
                    [s for s in symbols if s in profiles and "error" not in profiles[s]]
                ),
                "successful_financials": len(
                    [
                        s
                        for s in symbols
                        if s in financials and "error" not in financials[s]
                    ]
                ),
                "successful_market_data": len(
                    [
                        s
                        for s in symbols
                        if s in market_data and "error" not in market_data[s]
                    ]
                ),
                "collection_time_seconds": round(collection_time, 2),
                "average_time_per_symbol": round(collection_time / len(symbols), 2),
                "collected_at": datetime.utcnow().isoformat(),
            },
            "data": comprehensive_data,
        }

        print(
            f"✅ Comprehensive data collection completed in {collection_time:.2f} seconds"
        )
        print(
            f"   - Profiles: {summary['collection_summary']['successful_profiles']}/{len(symbols)}"
        )
        print(
            f"   - Financials: {summary['collection_summary']['successful_financials']}/{len(symbols)}"
        )
        print(
            f"   - Market Data: {summary['collection_summary']['successful_market_data']}/{len(symbols)}"
        )

        return summary

    def get_universe_summary(self) -> Dict[str, Any]:
        """Get a summary of the test universe."""
        return self.universe_manager.get_universe_summary()

    def validate_collected_data(self, collected_data: Dict[str, Any]) -> Dict[str, Any]:
        """Validate collected data against expected values."""
        return self.universe_manager.validate_data_availability(
            collected_data.get("data", {})
        )


# Convenience functions
async def demo_collect_magnificent_7():
    """Demo function to collect data for all Magnificent 7 stocks."""
    collector = DemoDataCollector()

    print("🎯 Magnificent 7 Stocks Data Collection Demo")
    print("=" * 60)

    # Show universe summary
    universe_summary = collector.get_universe_summary()
    print(f"Universe: {universe_summary['name']}")
    print(f"Description: {universe_summary['description']}")
    print(f"Total Stocks: {universe_summary['total_stocks']}")
    print(f"Sectors: {', '.join(universe_summary['sectors'])}")
    print(f"Industries: {', '.join(universe_summary['industries'])}")
    print()

    # Collect comprehensive data
    data = await collector.collect_comprehensive_data()

    # Validate data quality
    validation_results = collector.validate_collected_data(data)

    print("\n📊 Data Quality Validation Results:")
    print("-" * 40)

    for symbol, results in validation_results.items():
        print(f"{symbol}:")
        print(
            f"  Profile: {results['profile_completeness_met']} ({results['actual_profile_completeness']:.1%})"
        )
        print(f"  Financials: {results['financials_met']}")
        print(f"  Market Data: {results['market_data_met']}")
        print(f"  Quality Score: {results['overall_quality_score']:.1%}")

    return data


if __name__ == "__main__":
    # Run the demo
    asyncio.run(demo_collect_magnificent_7())
