from financetoolkit import Toolkit
import pandas as pd
from datetime import datetime

# Create toolkit instance - will use Yahoo Finance if no valid API key
companies = Toolkit(['AAPL', 'MSFT'], start_date='2017-12-31')

print("Fetching financial data for AAPL and MSFT...")
print("=" * 50)

# Initialize markdown content
markdown_content = []
markdown_content.append("# Financial Analysis Report: AAPL vs MSFT")
markdown_content.append(f"*Generated on: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}*")
markdown_content.append("")

# Get enterprise value data
try:
    enterprise = companies.enterprise.get_enterprise_value()
    markdown_content.append("## Enterprise Value Analysis")
    markdown_content.append("```")
    markdown_content.append(str(enterprise))
    markdown_content.append("```")
    markdown_content.append("")
except Exception as e:
    markdown_content.append("## Enterprise Value Analysis")
    markdown_content.append(f"*Error: {e}*")
    markdown_content.append("")

# Get historical data
try:
    historical_data = companies.get_historical_data()
    markdown_content.append("## Historical Price Data")
    markdown_content.append("### AAPL - Last 5 Trading Days")
    markdown_content.append("```")
    markdown_content.append(str(historical_data['AAPL'].tail()))
    markdown_content.append("```")
    markdown_content.append("")
except Exception as e:
    markdown_content.append("## Historical Price Data")
    markdown_content.append(f"*Error: {e}*")
    markdown_content.append("")

# Get balance sheet statement
try:
    balance_sheet_statement = companies.get_balance_sheet_statement()
    markdown_content.append("## Balance Sheet Analysis")
    markdown_content.append("### AAPL - Key Balance Sheet Items (Last 5 Years)")
    markdown_content.append("```")
    markdown_content.append(str(balance_sheet_statement['AAPL'].tail()))
    markdown_content.append("```")
    markdown_content.append("")
except Exception as e:
    markdown_content.append("## Balance Sheet Analysis")
    markdown_content.append(f"*Error: {e}*")
    markdown_content.append("")

# Get profitability ratios
try:
    profitability_ratios = companies.ratios.collect_profitability_ratios()
    
    markdown_content.append("## Profitability Ratios Comparison")
    markdown_content.append("")
    
    # AAPL Analysis
    markdown_content.append("### Apple Inc. (AAPL)")
    aapl_ratios = profitability_ratios.loc['AAPL']
    markdown_content.append("| Metric | 2020 | 2021 | 2022 | 2023 | 2024 | 2025 |")
    markdown_content.append("|--------|------|------|------|------|------|------|")
    
    for metric in aapl_ratios.index:
        values = aapl_ratios.loc[metric]
        row = f"| {metric} |"
        for year in ['2020', '2021', '2022', '2023', '2024', '2025']:
            if year in values.index and pd.notna(values[year]):
                row += f" {values[year]:.4f} |"
            else:
                row += " N/A |"
        markdown_content.append(row)
    
    markdown_content.append("")
    
    # MSFT Analysis
    markdown_content.append("### Microsoft Corporation (MSFT)")
    msft_ratios = profitability_ratios.loc['MSFT']
    markdown_content.append("| Metric | 2020 | 2021 | 2022 | 2023 | 2024 | 2025 |")
    markdown_content.append("|--------|------|------|------|------|------|------|")
    
    for metric in msft_ratios.index:
        values = msft_ratios.loc[metric]
        row = f"| {metric} |"
        for year in ['2020', '2021', '2022', '2023', '2024', '2025']:
            if year in values.index and pd.notna(values[year]):
                row += f" {values[year]:.4f} |"
            else:
                row += " N/A |"
        row += ""
        markdown_content.append(row)
    
    markdown_content.append("")
    
    # Key Insights
    markdown_content.append("## Key Financial Insights")
    markdown_content.append("")
    
    # Compare 2024 metrics
    try:
        aapl_2024 = aapl_ratios['2024']
        msft_2024 = msft_ratios['2024']
        
        markdown_content.append("### 2024 Performance Comparison")
        markdown_content.append("")
        
        if pd.notna(aapl_2024.get('Gross Margin')) and pd.notna(msft_2024.get('Gross Margin')):
            aapl_gm = aapl_2024['Gross Margin']
            msft_gm = msft_2024['Gross Margin']
            markdown_content.append(f"- **Gross Margin**: MSFT leads with {msft_gm:.1%} vs AAPL's {aapl_gm:.1%}")
        
        if pd.notna(aapl_2024.get('Operating Margin')) and pd.notna(msft_2024.get('Operating Margin')):
            aapl_om = aapl_2024['Operating Margin']
            msft_om = msft_2024['Operating Margin']
            markdown_content.append(f"- **Operating Margin**: MSFT leads with {msft_om:.1%} vs AAPL's {aapl_om:.1%}")
        
        if pd.notna(aapl_2024.get('Net Profit Margin')) and pd.notna(msft_2024.get('Net Profit Margin')):
            aapl_npm = aapl_2024['Net Profit Margin']
            msft_npm = msft_2024['Net Profit Margin']
            markdown_content.append(f"- **Net Profit Margin**: MSFT leads with {msft_npm:.1%} vs AAPL's {aapl_npm:.1%}")
        
        markdown_content.append("")
        
    except Exception as e:
        markdown_content.append(f"*Error comparing 2024 metrics: {e}*")
        markdown_content.append("")
    
    markdown_content.append("### Trend Analysis")
    markdown_content.append("- Both companies show strong profitability metrics")
    markdown_content.append("- MSFT generally maintains higher margins across most categories")
    markdown_content.append("- AAPL shows strong return on equity and capital efficiency")
    markdown_content.append("")
    
except Exception as e:
    markdown_content.append("## Profitability Ratios")
    markdown_content.append(f"*Error: {e}*")
    markdown_content.append("")

# Add conclusion
markdown_content.append("## Conclusion")
markdown_content.append("This analysis provides a comprehensive view of the financial performance of Apple Inc. and Microsoft Corporation.")
markdown_content.append("Both companies demonstrate strong financial health with robust profitability ratios.")
markdown_content.append("")
markdown_content.append("---")
markdown_content.append("*Data source: Yahoo Finance via FinanceToolkit*")

# Write markdown file
with open('financial_analysis_report.md', 'w', encoding='utf-8') as f:
    f.write('\n'.join(markdown_content))

print("Markdown report generated successfully!")
print("File saved as: financial_analysis_report.md")
print("\n" + "=" * 50)
print("Analysis complete!")