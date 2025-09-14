#!/usr/bin/env python3
"""
Company Comparison Demo Script
Creates visual demonstrations of the company comparison functionality

This script generates:
1. Comparison tables for financial metrics
2. Sample chart data for visualization
3. Search result examples
4. UI mockup data
"""

import json
import pandas as pd
from typing import List, Dict, Any
import matplotlib.pyplot as plt
import seaborn as sns
from datetime import datetime, timedelta
import random

def load_test_results():
    """Load the test results from the comparison test."""
    with open('../data/test_output/company_comparison_test_results.json', 'r') as f:
        return json.load(f)

def create_comparison_table(companies: List[Dict[str, Any]]) -> pd.DataFrame:
    """Create a comparison table for the companies."""
    # Extract key metrics for comparison
    comparison_data = []
    
    for company in companies:
        comparison_data.append({
            'Symbol': company['symbol'],
            'Name': company['name'],
            'Sector': company['sector'],
            'Market Cap ($B)': round(company['market_cap'] / 1e9, 1),
            'Price ($)': company['close_price'],
            'P/E Ratio': company['pe_ratio'],
            'P/B Ratio': company['pb_ratio'],
            'P/S Ratio': company['ps_ratio'],
            'Beta': company['beta'],
            'Div Yield (%)': round(company['dividend_yield'] * 100, 2),
            'Volume (M)': round(abs(company['volume']) / 1e6, 1) if company['volume'] else 0
        })
    
    return pd.DataFrame(comparison_data)

def create_metrics_comparison_chart(companies: List[Dict[str, Any]]):
    """Create a comparison chart for key financial metrics."""
    # Prepare data for visualization
    symbols = [company['symbol'] for company in companies]
    pe_ratios = [company['pe_ratio'] for company in companies]
    pb_ratios = [company['pb_ratio'] for company in companies]
    ps_ratios = [company['ps_ratio'] for company in companies]
    betas = [company['beta'] for company in companies]
    
    # Create subplots
    fig, axes = plt.subplots(2, 2, figsize=(15, 10))
    fig.suptitle('Company Financial Metrics Comparison', fontsize=16, fontweight='bold')
    
    # P/E Ratio comparison
    axes[0, 0].bar(symbols, pe_ratios, color='skyblue', alpha=0.7)
    axes[0, 0].set_title('Price-to-Earnings Ratio')
    axes[0, 0].set_ylabel('P/E Ratio')
    axes[0, 0].tick_params(axis='x', rotation=45)
    
    # P/B Ratio comparison
    axes[0, 1].bar(symbols, pb_ratios, color='lightgreen', alpha=0.7)
    axes[0, 1].set_title('Price-to-Book Ratio')
    axes[0, 1].set_ylabel('P/B Ratio')
    axes[0, 1].tick_params(axis='x', rotation=45)
    
    # P/S Ratio comparison
    axes[1, 0].bar(symbols, ps_ratios, color='lightcoral', alpha=0.7)
    axes[1, 0].set_title('Price-to-Sales Ratio')
    axes[1, 0].set_ylabel('P/S Ratio')
    axes[1, 0].tick_params(axis='x', rotation=45)
    
    # Beta comparison
    axes[1, 1].bar(symbols, betas, color='gold', alpha=0.7)
    axes[1, 1].set_title('Beta (Volatility)')
    axes[1, 1].set_ylabel('Beta')
    axes[1, 1].tick_params(axis='x', rotation=45)
    
    plt.tight_layout()
    plt.savefig('../data/test_output/company_metrics_comparison.png', dpi=300, bbox_inches='tight')
    plt.close()

def create_performance_chart(companies: List[Dict[str, Any]]):
    """Create a performance chart showing price movements."""
    # Generate mock historical data
    dates = pd.date_range(start='2024-01-01', end='2024-12-31', freq='D')
    
    plt.figure(figsize=(15, 8))
    
    colors = ['#1f77b4', '#ff7f0e', '#2ca02c', '#d62728', '#9467bd']
    
    for i, company in enumerate(companies):
        # Generate realistic price movements
        base_price = company['close_price']
        prices = [base_price]
        
        for j in range(1, len(dates)):
            # Random walk with slight upward bias
            change = random.uniform(-0.02, 0.01)
            new_price = prices[-1] * (1 + change)
            prices.append(new_price)
        
        plt.plot(dates, prices, label=f"{company['symbol']} - {company['name']}", 
                color=colors[i % len(colors)], linewidth=2)
    
    plt.title('Company Performance Comparison (2024)', fontsize=16, fontweight='bold')
    plt.xlabel('Date')
    plt.ylabel('Price ($)')
    plt.legend(bbox_to_anchor=(1.05, 1), loc='upper left')
    plt.grid(True, alpha=0.3)
    plt.xticks(rotation=45)
    plt.tight_layout()
    plt.savefig('../data/test_output/company_performance_comparison.png', dpi=300, bbox_inches='tight')
    plt.close()

def create_sector_analysis(companies: List[Dict[str, Any]]):
    """Create sector analysis visualization."""
    # Group companies by sector
    sector_data = {}
    for company in companies:
        sector = company['sector']
        if sector not in sector_data:
            sector_data[sector] = []
        sector_data[sector].append(company)
    
    # Create sector analysis
    sectors = list(sector_data.keys())
    sector_counts = [len(sector_data[sector]) for sector in sectors]
    sector_market_caps = [sum(company['market_cap'] for company in sector_data[sector]) / 1e9 for sector in sectors]
    
    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(15, 6))
    
    # Company count by sector
    ax1.pie(sector_counts, labels=sectors, autopct='%1.1f%%', startangle=90)
    ax1.set_title('Company Distribution by Sector')
    
    # Market cap by sector
    ax2.bar(sectors, sector_market_caps, color='lightblue', alpha=0.7)
    ax2.set_title('Total Market Cap by Sector')
    ax2.set_ylabel('Market Cap ($B)')
    ax2.tick_params(axis='x', rotation=45)
    
    plt.tight_layout()
    plt.savefig('../data/test_output/sector_analysis.png', dpi=300, bbox_inches='tight')
    plt.close()

def create_search_results_demo():
    """Create a demo of search results."""
    search_demo = {
        "search_queries": [
            {
                "query": "Apple",
                "results": [
                    {"symbol": "AAPL", "name": "Apple Inc.", "sector": "Technology", "match_score": 0.95}
                ]
            },
            {
                "query": "Tech",
                "results": [
                    {"symbol": "AAPL", "name": "Apple Inc.", "sector": "Technology", "match_score": 0.85},
                    {"symbol": "MSFT", "name": "Microsoft Corporation", "sector": "Technology", "match_score": 0.85},
                    {"symbol": "GOOGL", "name": "Alphabet Inc.", "sector": "Technology", "match_score": 0.85},
                    {"symbol": "NVDA", "name": "NVIDIA Corporation", "sector": "Technology", "match_score": 0.85}
                ]
            },
            {
                "query": "Financial",
                "results": [
                    {"symbol": "JPM", "name": "JPMorgan Chase & Co.", "sector": "Financial Services", "match_score": 0.90},
                    {"symbol": "BAC", "name": "Bank of America Corporation", "sector": "Financial Services", "match_score": 0.90},
                    {"symbol": "WFC", "name": "Wells Fargo & Company", "sector": "Financial Services", "match_score": 0.90}
                ]
            }
        ]
    }
    
    with open('../data/test_output/search_results_demo.json', 'w') as f:
        json.dump(search_demo, f, indent=2)

def create_ui_mockup_data():
    """Create data for UI mockup demonstration."""
    ui_mockup = {
        "compact_metrics_cards": [
            {
                "title": "Market Cap",
                "value": "$3.0T",
                "change": "+2.5%",
                "trend": "up",
                "format": "currency",
                "size": "lg"
            },
            {
                "title": "P/E Ratio",
                "value": "25.5",
                "change": "-0.3",
                "trend": "down",
                "format": "ratio",
                "size": "md"
            },
            {
                "title": "Beta",
                "value": "1.2",
                "change": "+0.1",
                "trend": "up",
                "format": "ratio",
                "size": "sm"
            },
            {
                "title": "Dividend Yield",
                "value": "2.5%",
                "change": "+0.1%",
                "trend": "up",
                "format": "percentage",
                "size": "sm"
            }
        ],
        "comparison_interface": {
            "selected_companies": ["AAPL", "MSFT", "GOOGL", "AMZN", "NVDA"],
            "comparison_metrics": [
                "market_cap", "pe_ratio", "pb_ratio", "ps_ratio", "beta", "dividend_yield"
            ],
            "chart_periods": ["1D", "1W", "1M", "3M", "6M", "1Y", "5Y"],
            "chart_types": ["line", "candlestick", "volume", "comparison"]
        },
        "news_section": {
            "categories": ["earnings", "corporate_action", "strategy", "general"],
            "sample_news": [
                {
                    "title": "Apple Reports Record Q4 Revenue",
                    "type": "earnings",
                    "date": "2024-10-25",
                    "sentiment": "positive",
                    "impact": "high"
                },
                {
                    "title": "Microsoft Announces AI Partnership",
                    "type": "strategy",
                    "date": "2024-10-24",
                    "sentiment": "positive",
                    "impact": "medium"
                },
                {
                    "title": "Amazon Stock Split Announcement",
                    "type": "corporate_action",
                    "date": "2024-10-23",
                    "sentiment": "positive",
                    "impact": "high"
                }
            ]
        }
    }
    
    with open('../data/test_output/ui_mockup_data.json', 'w') as f:
        json.dump(ui_mockup, f, indent=2)

def main():
    """Main demo function."""
    print("🎨 Company Comparison Demo Script")
    print("=" * 50)
    
    # Load test results
    print("\n1. Loading test results...")
    test_results = load_test_results()
    companies = test_results['companies']
    print(f"✅ Loaded {len(companies)} companies")
    
    # Create comparison table
    print("\n2. Creating comparison table...")
    comparison_df = create_comparison_table(companies)
    print("✅ Comparison table created:")
    print(comparison_df.to_string(index=False))
    
    # Save comparison table
    comparison_df.to_csv('../data/test_output/company_comparison_table.csv', index=False)
    print("✅ Comparison table saved to CSV")
    
    # Create metrics comparison chart
    print("\n3. Creating metrics comparison chart...")
    create_metrics_comparison_chart(companies)
    print("✅ Metrics comparison chart saved")
    
    # Create performance chart
    print("\n4. Creating performance comparison chart...")
    create_performance_chart(companies)
    print("✅ Performance comparison chart saved")
    
    # Create sector analysis
    print("\n5. Creating sector analysis...")
    create_sector_analysis(companies)
    print("✅ Sector analysis chart saved")
    
    # Create search results demo
    print("\n6. Creating search results demo...")
    create_search_results_demo()
    print("✅ Search results demo saved")
    
    # Create UI mockup data
    print("\n7. Creating UI mockup data...")
    create_ui_mockup_data()
    print("✅ UI mockup data saved")
    
    print("\n🎉 Company Comparison Demo Completed Successfully!")
    print("\nGenerated Files:")
    print("- company_comparison_table.csv - Comparison data table")
    print("- company_metrics_comparison.png - Financial metrics chart")
    print("- company_performance_comparison.png - Performance comparison chart")
    print("- sector_analysis.png - Sector distribution analysis")
    print("- search_results_demo.json - Search functionality demo")
    print("- ui_mockup_data.json - UI component mockup data")
    
    print("\nNext Steps:")
    print("1. Review generated visualizations")
    print("2. Use UI mockup data for frontend development")
    print("3. Implement API endpoints based on test results")
    print("4. Create React components for comparison interface")

if __name__ == "__main__":
    main()
