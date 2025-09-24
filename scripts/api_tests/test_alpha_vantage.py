#!/usr/bin/env python3
"""
Alpha Vantage API Test Script
Simple demonstration of Alpha Vantage capabilities

This script tests basic Alpha Vantage API endpoints to understand:
- API connectivity and authentication
- Data quality and format
- Rate limiting behavior
- Basic stock data retrieval
"""

import json
import os
import time
from datetime import datetime

import requests
from dotenv import load_dotenv

# Load environment variables
load_dotenv()


class AlphaVantageTester:
    """Simple Alpha Vantage API tester"""

    def __init__(self):
        """Initialize the tester with API key"""
        self.api_key = os.getenv("ALPHA_VANTAGE_API_KEY")
        self.base_url = "https://www.alphavantage.co/query"
        self.call_count = 0
        self.last_call_time = 0

        if not self.api_key:
            print("❌ ALPHA_VANTAGE_API_KEY not found in .env file")
            print("Please add your Alpha Vantage API key to .env file:")
            print("ALPHA_VANTAGE_API_KEY=your_api_key_here")
            print(
                "\nGet free API key from: https://www.alphavantage.co/support/#api-key"
            )
            return

        print(f"✅ Alpha Vantage API key found")
        print(f"🔑 API Key: {self.api_key[:8]}...")

    def rate_limit_check(self):
        """Check and enforce rate limiting (5 calls per minute for free tier)"""
        current_time = time.time()

        # Reset counter if more than 1 minute has passed
        if current_time - self.last_call_time > 60:
            self.call_count = 0

        # Check if we're at the limit
        if self.call_count >= 5:
            wait_time = 60 - (current_time - self.last_call_time)
            if wait_time > 0:
                print(f"⏳ Rate limit reached. Waiting {wait_time:.1f} seconds...")
                time.sleep(wait_time)
                self.call_count = 0

        self.last_call_time = time.time()
        self.call_count += 1

    def make_api_call(self, function, symbol=None, **params):
        """Make an API call with rate limiting"""
        self.rate_limit_check()

        # Prepare parameters
        params["function"] = function
        params["apikey"] = self.api_key
        if symbol:
            params["symbol"] = symbol

        try:
            print(f"🌐 Calling {function} endpoint...")
            response = requests.get(self.base_url, params=params)

            if response.status_code == 200:
                data = response.json()

                # Check for API error messages
                if "Error Message" in data:
                    print(f"❌ API Error: {data['Error Message']}")
                    return None
                elif "Note" in data:
                    print(f"⚠️  API Note: {data['Note']}")
                    return None
                else:
                    print(f"✅ API call successful")
                    return data
            else:
                print(f"❌ HTTP Error: {response.status_code}")
                return None

        except Exception as e:
            print(f"❌ Request Error: {e}")
            return None

    def test_company_overview(self, symbol="AAPL"):
        """Test company overview endpoint"""
        print(f"\n📊 Testing Company Overview for {symbol}")
        print("=" * 50)

        data = self.make_api_call("OVERVIEW", symbol)
        if data:
            print(f"Company: {data.get('Name', 'N/A')}")
            print(f"Symbol: {data.get('Symbol', 'N/A')}")
            print(f"Sector: {data.get('Sector', 'N/A')}")
            print(f"Industry: {data.get('Industry', 'N/A')}")
            print(f"Market Cap: {data.get('MarketCapitalization', 'N/A')}")
            print(f"P/E Ratio: {data.get('PERatio', 'N/A')}")
            print(f"Dividend Yield: {data.get('DividendYield', 'N/A')}")
            print(f"Description: {data.get('Description', 'N/A')[:200]}...")

        return data

    def test_stock_quote(self, symbol="AAPL"):
        """Test real-time stock quote endpoint"""
        print(f"\n📈 Testing Real-time Stock Quote for {symbol}")
        print("=" * 50)

        data = self.make_api_call("GLOBAL_QUOTE", symbol)
        if data and "Global Quote" in data:
            quote = data["Global Quote"]
            print(f"Symbol: {quote.get('01. symbol', 'N/A')}")
            print(f"Price: {quote.get('05. price', 'N/A')}")
            print(f"Change: {quote.get('09. change', 'N/A')}")
            print(f"Change %: {quote.get('10. change percent', 'N/A')}")
            print(f"Volume: {quote.get('06. volume', 'N/A')}")
            print(f"Previous Close: {quote.get('08. previous close', 'N/A')}")

        return data

    def test_technical_indicator(self, symbol="AAPL", indicator="RSI"):
        """Test technical indicator endpoint"""
        print(f"\n📊 Testing {indicator} Technical Indicator for {symbol}")
        print("=" * 50)

        data = self.make_api_call(
            indicator, symbol, interval="daily", time_period=14, series_type="close"
        )
        if data:
            if "Technical Analysis: RSI" in data:
                rsi_data = data["Technical Analysis: RSI"]
                # Show last 5 RSI values
                dates = list(rsi_data.keys())[:5]
                for date in dates:
                    rsi_value = rsi_data[date]["RSI"]
                    print(f"{date}: RSI = {rsi_value}")
            else:
                print("Data structure:", list(data.keys()))

        return data

    def test_economic_indicator(self, indicator="REAL_GDP"):
        """Test economic indicator endpoint"""
        print(f"\n🌍 Testing Economic Indicator: {indicator}")
        print("=" * 50)

        data = self.make_api_call(indicator)
        if data:
            if "data" in data:
                gdp_data = data["data"]
                # Show last 5 GDP values
                for i, entry in enumerate(gdp_data[:5]):
                    date = entry.get("date", "N/A")
                    value = entry.get("value", "N/A")
                    print(f"{date}: {value}")
            else:
                print("Data structure:", list(data.keys()))

        return data

    def test_forex_rate(self, from_currency="USD", to_currency="EUR"):
        """Test forex exchange rate endpoint"""
        print(f"\n💱 Testing Forex Rate: {from_currency} to {to_currency}")
        print("=" * 50)

        data = self.make_api_call(
            "CURRENCY_EXCHANGE_RATE",
            from_currency=from_currency,
            to_currency=to_currency,
        )
        if data and "Realtime Currency Exchange Rate" in data:
            rate_data = data["Realtime Currency Exchange Rate"]
            print(f"From: {rate_data.get('1. From_Currency Code', 'N/A')}")
            print(f"To: {rate_data.get('3. To_Currency Code', 'N/A')}")
            print(f"Rate: {rate_data.get('5. Exchange Rate', 'N/A')}")
            print(f"Last Updated: {rate_data.get('6. Last Refreshed', 'N/A')}")

        return data

    def run_basic_tests(self):
        """Run basic tests to demonstrate Alpha Vantage capabilities"""
        if not self.api_key:
            return

        print("🚀 Starting Alpha Vantage API Tests")
        print("=" * 60)
        print(f"⏰ Test started at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        print("📋 Free tier limits: 500 calls/day, 5 calls/minute")
        print("=" * 60)

        # Test 1: Company Overview
        self.test_company_overview("AAPL")

        # Test 2: Stock Quote
        self.test_stock_quote("MSFT")

        # Test 3: Technical Indicator
        self.test_technical_indicator("GOOGL", "RSI")

        # Test 4: Economic Indicator
        self.test_economic_indicator("REAL_GDP")

        # Test 5: Forex Rate
        self.test_forex_rate("USD", "EUR")

        print(f"\n🎉 Basic tests completed!")
        print(f"📊 Total API calls made: {self.call_count}")
        print(f"⏰ Test completed at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")

        print(f"\n💡 Next Steps:")
        print(f"1. Review the data quality and format")
        print(f"2. Compare with existing data sources")
        print(f"3. Test additional endpoints as needed")
        print(f"4. Implement data caching and error handling")


def main():
    """Main function to run Alpha Vantage tests"""
    tester = AlphaVantageTester()
    tester.run_basic_tests()


if __name__ == "__main__":
    main()
