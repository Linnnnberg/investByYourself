#!/usr/bin/env python3
"""
Financial Modeling Prep (FMP) API Test Script
Test and evaluate FMP API capabilities for company data

This script helps you:
- Test FMP API connectivity
- Compare data quality with Yahoo Finance
- Evaluate integration complexity
- Make informed decisions about data sources
"""

import requests
import json
import time
import os
from datetime import datetime
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

class FMPTester:
    """Financial Modeling Prep API tester"""
    
    def __init__(self):
        """Initialize the tester with API key"""
        self.api_key = os.getenv('FMP_API_KEY')
        self.base_url = 'https://financialmodelingprep.com/api/v3'
        self.call_count = 0
        
        if not self.api_key:
            print("❌ FMP_API_KEY not found in .env file")
            print("Please add your FMP API key to .env file:")
            print("FMP_API_KEY=your_api_key_here")
            print("\nGet free API key from: https://financialmodelingprep.com/developer")
            print("Free tier: 250 calls/day")
            return
        
        print(f"✅ FMP API key found")
        print(f"🔑 API Key: {self.api_key[:8]}...")
        print(f"📊 Free tier: 250 calls/day")
    
    def make_api_call(self, endpoint, **params):
        """Make an API call to FMP"""
        if self.call_count >= 250:
            print(f"⚠️  Free tier limit reached (250 calls/day)")
            return None
        
        url = f"{self.base_url}{endpoint}"
        params['apikey'] = self.api_key
        
        try:
            print(f"🌐 Calling FMP endpoint: {endpoint}")
            response = requests.get(url, params=params)
            
            if response.status_code == 200:
                data = response.json()
                self.call_count += 1
                print(f"✅ API call successful (calls used: {self.call_count}/250)")
                return data
            else:
                print(f"❌ HTTP Error: {response.status_code}")
                return None
                
        except Exception as e:
            print(f"❌ Request Error: {e}")
            return None
    
    def test_company_profile(self, symbol='AAPL'):
        """Test company profile endpoint"""
        print(f"\n📊 Testing Company Profile for {symbol}")
        print("=" * 50)
        
        data = self.make_api_call(f'/company-profile/{symbol}')
        if data and len(data) > 0:
            profile = data[0]
            print(f"Company: {profile.get('companyName', 'N/A')}")
            print(f"Symbol: {profile.get('symbol', 'N/A')}")
            print(f"Sector: {profile.get('sector', 'N/A')}")
            print(f"Industry: {profile.get('industry', 'N/A')}")
            print(f"Market Cap: {profile.get('mktCap', 'N/A')}")
            print(f"P/E Ratio: {profile.get('pe', 'N/A')}")
            print(f"Dividend Yield: {profile.get('dividend', 'N/A')}")
            print(f"Description: {profile.get('description', 'N/A')[:200]}...")
        
        return data
    
    def test_income_statement(self, symbol='AAPL'):
        """Test income statement endpoint"""
        print(f"\n📈 Testing Income Statement for {symbol}")
        print("=" * 50)
        
        data = self.make_api_call(f'/income-statement/{symbol}', limit=5)
        if data and len(data) > 0:
            print(f"Found {len(data)} income statements")
            latest = data[0]
            print(f"Latest Period: {latest.get('period', 'N/A')}")
            print(f"Revenue: {latest.get('revenue', 'N/A')}")
            print(f"Gross Profit: {latest.get('grossProfit', 'N/A')}")
            print(f"Operating Income: {latest.get('operatingIncome', 'N/A')}")
            print(f"Net Income: {latest.get('netIncome', 'N/A')}")
        
        return data
    
    def test_balance_sheet(self, symbol='AAPL'):
        """Test balance sheet endpoint"""
        print(f"\n💰 Testing Balance Sheet for {symbol}")
        print("=" * 50)
        
        data = self.make_api_call(f'/balance-sheet-statement/{symbol}', limit=5)
        if data and len(data) > 0:
            print(f"Found {len(data)} balance sheets")
            latest = data[0]
            print(f"Latest Period: {latest.get('period', 'N/A')}")
            print(f"Total Assets: {latest.get('totalAssets', 'N/A')}")
            print(f"Total Liabilities: {latest.get('totalLiabilities', 'N/A')}")
            print(f"Total Equity: {latest.get('totalStockholdersEquity', 'N/A')}")
            print(f"Cash: {latest.get('cashAndCashEquivalents', 'N/A')}")
        
        return data
    
    def test_financial_ratios(self, symbol='AAPL'):
        """Test financial ratios endpoint"""
        print(f"\n📊 Testing Financial Ratios for {symbol}")
        print("=" * 50)
        
        data = self.make_api_call(f'/ratios/{symbol}', limit=5)
        if data and len(data) > 0:
            print(f"Found {len(data)} ratio records")
            latest = data[0]
            print(f"Latest Period: {latest.get('period', 'N/A')}")
            print(f"ROE: {latest.get('returnOnEquity', 'N/A')}")
            print(f"ROA: {latest.get('returnOnAssets', 'N/A')}")
            print(f"Gross Margin: {latest.get('grossProfitMargin', 'N/A')}")
            print(f"Operating Margin: {latest.get('operatingIncomeMargin', 'N/A')}")
            print(f"Net Margin: {latest.get('netProfitMargin', 'N/A')}")
        
        return data
    
    def test_stock_quote(self, symbol='AAPL'):
        """Test real-time stock quote endpoint"""
        print(f"\n📈 Testing Real-time Stock Quote for {symbol}")
        print("=" * 50)
        
        data = self.make_api_call(f'/quote/{symbol}')
        if data and len(data) > 0:
            quote = data[0]
            print(f"Symbol: {quote.get('symbol', 'N/A')}")
            print(f"Price: {quote.get('price', 'N/A')}")
            print(f"Change: {quote.get('change', 'N/A')}")
            print(f"Change %: {quote.get('changesPercentage', 'N/A')}")
            print(f"Volume: {quote.get('volume', 'N/A')}")
            print(f"Previous Close: {quote.get('previousClose', 'N/A')}")
        
        return data
    
    def compare_with_yahoo_finance(self, symbol='AAPL'):
        """Compare FMP data with Yahoo Finance data"""
        print(f"\n🔄 Comparing FMP vs Yahoo Finance for {symbol}")
        print("=" * 50)
        
        # Get FMP data
        fmp_profile = self.make_api_call(f'/company-profile/{symbol}')
        fmp_quote = self.make_api_call(f'/quote/{symbol}')
        
        if fmp_profile and fmp_quote:
            fmp_data = {
                'market_cap': fmp_profile[0].get('mktCap', 'N/A'),
                'pe_ratio': fmp_profile[0].get('pe', 'N/A'),
                'price': fmp_quote[0].get('price', 'N/A'),
                'volume': fmp_quote[0].get('volume', 'N/A')
            }
            
            print("FMP Data:")
            for key, value in fmp_data.items():
                print(f"  {key.replace('_', ' ').title()}: {value}")
            
            print("\nNote: Install yfinance to compare with Yahoo Finance data")
            print("Run: pip install yfinance")
            print("Then add comparison logic to this script")
        
        return fmp_profile, fmp_quote
    
    def run_comprehensive_tests(self):
        """Run comprehensive tests to evaluate FMP capabilities"""
        if not self.api_key:
            return
        
        print("🚀 Starting FMP API Comprehensive Tests")
        print("=" * 60)
        print(f"⏰ Test started at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        print("📋 Free tier limits: 250 calls/day")
        print("=" * 60)
        
        # Test 1: Company Profile
        self.test_company_profile('AAPL')
        
        # Test 2: Income Statement
        self.test_income_statement('MSFT')
        
        # Test 3: Balance Sheet
        self.test_balance_sheet('GOOGL')
        
        # Test 4: Financial Ratios
        self.test_financial_ratios('AMZN')
        
        # Test 5: Stock Quote
        self.test_stock_quote('TSLA')
        
        # Test 6: Comparison
        self.compare_with_yahoo_finance('AAPL')
        
        print(f"\n🎉 Comprehensive tests completed!")
        print(f"📊 Total API calls made: {self.call_count}/250")
        print(f"⏰ Test completed at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        
        print(f"\n💡 Evaluation Results:")
        print(f"1. Data Quality: Review the data completeness and accuracy")
        print(f"2. API Reliability: Check response times and error rates")
        print(f"3. Data Freshness: Compare with other sources")
        print(f"4. Integration Complexity: Evaluate ease of use")
        
        print(f"\n📋 Next Steps:")
        print(f"1. Compare data quality with Yahoo Finance")
        print(f"2. Test additional endpoints as needed")
        print(f"3. Evaluate paid plans if free tier insufficient")
        print(f"4. Plan integration strategy")

def main():
    """Main function to run FMP tests"""
    tester = FMPTester()
    tester.run_comprehensive_tests()

if __name__ == "__main__":
    main()
