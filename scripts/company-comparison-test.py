#!/usr/bin/env python3
"""
Company Comparison Test Script
Tests the company comparison functionality with real data from Story-032

This script demonstrates:
1. Fetching multiple companies from the database
2. Comparing financial metrics side by side
3. Generating comparison data for charts
4. Testing search functionality
"""

import sqlite3
import json
import pandas as pd
from typing import List, Dict, Any
from datetime import datetime, timedelta
import random

def connect_to_database():
    """Connect to the SQLite database."""
    return sqlite3.connect('../api/investbyyourself_dev.db')

def get_companies_for_comparison(limit: int = 5) -> List[Dict[str, Any]]:
    """Get a sample of companies for comparison testing."""
    conn = connect_to_database()
    cursor = conn.cursor()
    
    # Get companies with their basic info
    query = """
    SELECT 
        c.symbol,
        c.name,
        c.sector,
        c.industry,
        c.market_cap,
        c.avg_volume_3m,
        md.close_price,
        md.volume,
        md.pe_ratio,
        md.pb_ratio,
        md.ps_ratio,
        md.beta,
        md.dividend_yield
    FROM companies c
    LEFT JOIN market_data md ON c.id = md.company_id
    WHERE c.is_active = TRUE
    ORDER BY c.market_cap DESC
    LIMIT ?
    """
    
    cursor.execute(query, (limit,))
    columns = [description[0] for description in cursor.description]
    companies = [dict(zip(columns, row)) for row in cursor.fetchall()]
    
    conn.close()
    return companies

def get_financial_ratios_for_comparison(symbols: List[str]) -> Dict[str, List[Dict[str, Any]]]:
    """Get financial ratios for multiple companies."""
    conn = connect_to_database()
    cursor = conn.cursor()
    
    ratios_by_company = {}
    
    for symbol in symbols:
        query = """
        SELECT 
            fr.ratio_type,
            fr.ratio_value,
            fr.ratio_date,
            fr.confidence_score
        FROM financial_ratios fr
        JOIN companies c ON fr.company_id = c.id
        WHERE c.symbol = ?
        ORDER BY fr.ratio_date DESC
        LIMIT 20
        """
        
        cursor.execute(query, (symbol,))
        columns = [description[0] for description in cursor.description]
        ratios = [dict(zip(columns, row)) for row in cursor.fetchall()]
        ratios_by_company[symbol] = ratios
    
    conn.close()
    return ratios_by_company

def generate_comparison_metrics(companies: List[Dict[str, Any]]) -> Dict[str, Any]:
    """Generate comparison metrics for the companies."""
    comparison = {
        'companies': companies,
        'metrics': {},
        'summary': {}
    }
    
    # Key metrics to compare
    key_metrics = [
        'market_cap', 'close_price', 'pe_ratio', 'pb_ratio', 'ps_ratio', 
        'beta', 'dividend_yield', 'volume', 'avg_volume_3m'
    ]
    
    for metric in key_metrics:
        values = []
        for company in companies:
            value = company.get(metric)
            if value is not None:
                values.append(value)
        
        if values:
            comparison['metrics'][metric] = {
                'values': values,
                'min': min(values),
                'max': max(values),
                'avg': sum(values) / len(values),
                'count': len(values)
            }
    
    # Generate summary insights
    comparison['summary'] = {
        'total_companies': len(companies),
        'sectors': list(set(company['sector'] for company in companies if company['sector'])),
        'market_cap_range': f"${comparison['metrics']['market_cap']['min']:,.0f} - ${comparison['metrics']['market_cap']['max']:,.0f}",
        'pe_ratio_range': f"{comparison['metrics']['pe_ratio']['min']:.2f} - {comparison['metrics']['pe_ratio']['max']:.2f}",
        'beta_range': f"{comparison['metrics']['beta']['min']:.2f} - {comparison['metrics']['beta']['max']:.2f}"
    }
    
    return comparison

def generate_chart_data(companies: List[Dict[str, Any]], days: int = 365) -> Dict[str, Any]:
    """Generate mock chart data for comparison visualization."""
    chart_data = {
        'companies': [],
        'data_points': []
    }
    
    # Generate mock historical data for each company
    base_date = datetime.now() - timedelta(days=days)
    
    for i, company in enumerate(companies):
        symbol = company['symbol']
        current_price = company.get('close_price', 100)
        
        # Generate realistic price movements
        prices = []
        current = current_price
        
        for day in range(days):
            # Add some random walk with slight upward bias
            change = random.uniform(-0.05, 0.03)  # -5% to +3% daily change
            current = current * (1 + change)
            prices.append({
                'date': (base_date + timedelta(days=day)).strftime('%Y-%m-%d'),
                'price': round(current, 2),
                'volume': random.randint(1000000, 10000000)
            })
        
        chart_data['companies'].append({
            'symbol': symbol,
            'name': company['name'],
            'sector': company['sector'],
            'color': f'hsl({i * 60}, 70%, 50%)',  # Different colors
            'data': prices
        })
    
    return chart_data

def test_search_functionality(query: str) -> List[Dict[str, Any]]:
    """Test search functionality with fuzzy matching."""
    conn = connect_to_database()
    cursor = conn.cursor()
    
    # Simple fuzzy search implementation
    search_query = """
    SELECT 
        c.symbol,
        c.name,
        c.sector,
        c.industry,
        c.market_cap,
        md.close_price,
        md.pe_ratio
    FROM companies c
    LEFT JOIN market_data md ON c.id = md.company_id
    WHERE 
        c.name LIKE ? OR 
        c.symbol LIKE ? OR 
        c.sector LIKE ? OR
        c.industry LIKE ?
    ORDER BY c.market_cap DESC
    LIMIT 10
    """
    
    search_term = f"%{query}%"
    cursor.execute(search_query, (search_term, search_term, search_term, search_term))
    
    columns = [description[0] for description in cursor.description]
    results = [dict(zip(columns, row)) for row in cursor.fetchall()]
    
    conn.close()
    return results

def test_sector_filtering(sector: str) -> List[Dict[str, Any]]:
    """Test sector-based filtering."""
    conn = connect_to_database()
    cursor = conn.cursor()
    
    query = """
    SELECT 
        c.symbol,
        c.name,
        c.sector,
        c.market_cap,
        md.close_price,
        md.pe_ratio,
        md.beta
    FROM companies c
    LEFT JOIN market_data md ON c.id = md.company_id
    WHERE c.sector = ?
    ORDER BY c.market_cap DESC
    """
    
    cursor.execute(query, (sector,))
    columns = [description[0] for description in cursor.description]
    results = [dict(zip(columns, row)) for row in cursor.fetchall()]
    
    conn.close()
    return results

def main():
    """Main test function."""
    print("🚀 Company Comparison Test Script")
    print("=" * 50)
    
    # Test 1: Get companies for comparison
    print("\n1. Fetching companies for comparison...")
    companies = get_companies_for_comparison(5)
    print(f"✅ Found {len(companies)} companies:")
    for company in companies:
        print(f"   - {company['symbol']}: {company['name']} ({company['sector']})")
    
    # Test 2: Generate comparison metrics
    print("\n2. Generating comparison metrics...")
    comparison = generate_comparison_metrics(companies)
    print(f"✅ Comparison metrics generated for {comparison['summary']['total_companies']} companies")
    print(f"   Sectors: {', '.join(comparison['summary']['sectors'])}")
    print(f"   Market Cap Range: {comparison['summary']['market_cap_range']}")
    print(f"   P/E Ratio Range: {comparison['summary']['pe_ratio_range']}")
    
    # Test 3: Generate chart data
    print("\n3. Generating chart data for visualization...")
    chart_data = generate_chart_data(companies, 30)  # 30 days for testing
    print(f"✅ Chart data generated for {len(chart_data['companies'])} companies")
    print(f"   Data points per company: {len(chart_data['companies'][0]['data'])}")
    
    # Test 4: Test search functionality
    print("\n4. Testing search functionality...")
    search_queries = ['Apple', 'Tech', 'Financial', 'MSFT']
    for query in search_queries:
        results = test_search_functionality(query)
        print(f"   Search '{query}': {len(results)} results")
        if results:
            print(f"      Top result: {results[0]['symbol']} - {results[0]['name']}")
    
    # Test 5: Test sector filtering
    print("\n5. Testing sector filtering...")
    sectors = ['Technology', 'Financial Services', 'Healthcare']
    for sector in sectors:
        results = test_sector_filtering(sector)
        print(f"   Sector '{sector}': {len(results)} companies")
        if results:
            print(f"      Top company: {results[0]['symbol']} - {results[0]['name']}")
    
    # Test 6: Save test results
    print("\n6. Saving test results...")
    test_results = {
        'timestamp': datetime.now().isoformat(),
        'companies': companies,
        'comparison': comparison,
        'chart_data': chart_data,
        'search_tests': {
            'queries': search_queries,
            'results': {q: test_search_functionality(q) for q in search_queries}
        },
        'sector_tests': {
            'sectors': sectors,
            'results': {s: test_sector_filtering(s) for s in sectors}
        }
    }
    
    with open('../data/test_output/company_comparison_test_results.json', 'w') as f:
        json.dump(test_results, f, indent=2, default=str)
    
    print("✅ Test results saved to data/test_output/company_comparison_test_results.json")
    
    # Test 7: Generate sample API responses
    print("\n7. Generating sample API responses...")
    
    # Sample search API response
    search_api_response = {
        'success': True,
        'data': {
            'query': 'Apple',
            'results': test_search_functionality('Apple'),
            'total': len(test_search_functionality('Apple')),
            'filters_applied': {}
        }
    }
    
    # Sample comparison API response
    comparison_api_response = {
        'success': True,
        'data': {
            'companies': [c['symbol'] for c in companies],
            'metrics': comparison['metrics'],
            'summary': comparison['summary'],
            'chart_data': chart_data
        }
    }
    
    # Save API response samples
    with open('../data/test_output/search_api_sample.json', 'w') as f:
        json.dump(search_api_response, f, indent=2, default=str)
    
    with open('../data/test_output/comparison_api_sample.json', 'w') as f:
        json.dump(comparison_api_response, f, indent=2, default=str)
    
    print("✅ Sample API responses saved")
    
    print("\n🎉 Company Comparison Test Completed Successfully!")
    print("\nNext Steps:")
    print("1. Review test results in data/test_output/")
    print("2. Implement API endpoints based on sample responses")
    print("3. Create frontend components for comparison interface")
    print("4. Integrate with real charting library (Plotly/Recharts)")

if __name__ == "__main__":
    main()
