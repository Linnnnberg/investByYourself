import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
from fredapi import Fred
from datetime import datetime, timedelta
import numpy as np

# Set seaborn style for better looking charts
sns.set_style("whitegrid")
plt.rcParams['figure.figsize'] = (12, 8)

print("Testing FRED API for CPI data (5-Year Analysis)...")
print("=" * 50)

# Initialize FRED API
# Note: You'll need to get a free API key from https://fred.stlouisfed.org/docs/api/api_key.html
try:
    # Try to load .env file if it exists
    try:
        from dotenv import load_dotenv
        load_dotenv()
        print("✅ .env file loaded successfully")
    except ImportError:
        print("⚠️  python-dotenv not installed. Install with: pip install python-dotenv")
    except FileNotFoundError:
        print("⚠️  .env file not found. Create one with your FRED_API_KEY")
    except UnicodeDecodeError:
        print("⚠️  .env file has encoding issues. Using environment variable directly.")
    
    # Try to get API key from environment variable
    import os
    api_key = os.getenv('FRED_API_KEY')
    
    if not api_key:
        print("⚠️  FRED API key not found in environment variables.")
        print("Please set your FRED API key as an environment variable 'FRED_API_KEY'")
        print("Get a free API key from: https://fred.stlouisfed.org/docs/api/api_key.html")
        print("\nFor testing purposes, we'll create sample data structure...")
        
        # Create sample data for demonstration
        end_date = datetime.now()
        start_date = end_date - timedelta(days=1825)  # 5 years of data
        
        # Generate sample data (monthly)
        dates = pd.date_range(start=start_date, end=end_date, freq='ME')
        sample_cpi = [280 + i*0.3 + np.random.normal(0, 0.1) for i in range(len(dates))]
        sample_core_cpi = [280 + i*0.25 + np.random.normal(0, 0.08) for i in range(len(dates))]  # Core CPI typically more stable
        sample_ppi = [120 + i*0.2 + np.random.normal(0, 0.15) for i in range(len(dates))]  # PPI typically more volatile
        
        cpi_data = pd.DataFrame({
            'date': dates,
            'CPIAUCSL': sample_cpi,  # Consumer Price Index for All Urban Consumers: All Items
            'CPILFESL': sample_core_cpi,  # Core CPI (All items less food and energy)
            'PPIACO': sample_ppi  # Producer Price Index for All Commodities
        })
        cpi_data.set_index('date', inplace=True)
        
        print("✅ Sample CPI, Core CPI, and PPI data created for demonstration")
        
    else:
        print("✅ FRED API key found, fetching real data...")
        fred = Fred(api_key=api_key)
        
        # Get data for 5 years
        end_date = datetime.now()
        start_date = end_date - timedelta(days=1825)  # 5 years of data
        
        # Fetch multiple series
        cpi_data = fred.get_series('CPIAUCSL', start_date, end_date)  # CPI All Items
        core_cpi_data = fred.get_series('CPILFESL', start_date, end_date)  # Core CPI (All items less food and energy)
        ppi_data = fred.get_series('PPIACO', start_date, end_date)  # Producer Price Index
        
        # Combine into DataFrame
        combined_data = pd.DataFrame({
            'CPIAUCSL': cpi_data,
            'CPILFESL': core_cpi_data,
            'PPIACO': ppi_data
        })
        
        print(f"✅ Successfully fetched data:")
        print(f"   - CPI: {len(cpi_data)} data points")
        print(f"   - Core CPI: {len(core_cpi_data)} data points")
        print(f"   - PPI: {len(ppi_data)} data points")
        
        cpi_data = combined_data

except Exception as e:
    print(f"❌ Error initializing FRED API: {e}")
    print("Creating sample data for demonstration...")
    
    # Create sample data as fallback
    end_date = datetime.now()
    start_date = end_date - timedelta(days=1825)  # 5 years of data
    dates = pd.date_range(start=start_date, end=end_date, freq='ME')
    sample_cpi = [280 + i*0.3 + np.random.normal(0, 0.1) for i in range(len(dates))]
    sample_core_cpi = [280 + i*0.25 + np.random.normal(0, 0.08) for i in range(len(dates))]
    sample_ppi = [120 + i*0.2 + np.random.normal(0, 0.15) for i in range(len(dates))]
    
    cpi_data = pd.DataFrame({
        'date': dates,
        'CPIAUCSL': sample_cpi,
        'CPILFESL': sample_core_cpi,
        'PPIACO': sample_ppi
    })
    cpi_data.set_index('date', inplace=True)

# Display basic information about the data
print(f"\n📊 Inflation Data Summary:")
print(f"Date Range: {cpi_data.index.min().strftime('%Y-%m-%d')} to {cpi_data.index.max().strftime('%Y-%m-%d')}")
print(f"Number of observations: {len(cpi_data)}")

print(f"\n📈 Latest Values:")
print(f"CPI (All Items): {cpi_data.iloc[-1]['CPIAUCSL']:.2f}")
print(f"Core CPI (Ex Food & Energy): {cpi_data.iloc[-1]['CPILFESL']:.2f}")
print(f"PPI (Producer Price Index): {cpi_data.iloc[-1]['PPIACO']:.2f}")

print(f"\n📊 5-Year Changes:")
print(f"CPI change: {((cpi_data.iloc[-1]['CPIAUCSL'] / cpi_data.iloc[0]['CPIAUCSL']) - 1) * 100:.2f}%")
print(f"Core CPI change: {((cpi_data.iloc[-1]['CPILFESL'] / cpi_data.iloc[0]['CPILFESL']) - 1) * 100:.2f}%")
print(f"PPI change: {((cpi_data.iloc[-1]['PPIACO'] / cpi_data.iloc[0]['PPIACO']) - 1) * 100:.2f}%")

# Calculate year-over-year inflation rates
if len(cpi_data) >= 12:
    current_cpi = cpi_data.iloc[-1]['CPIAUCSL']
    current_core_cpi = cpi_data.iloc[-1]['CPILFESL']
    current_ppi = cpi_data.iloc[-1]['PPIACO']
    
    year_ago_cpi = cpi_data.iloc[-13]['CPIAUCSL']
    year_ago_core_cpi = cpi_data.iloc[-13]['CPILFESL']
    year_ago_ppi = cpi_data.iloc[-13]['PPIACO']
    
    yoy_cpi = ((current_cpi / year_ago_cpi) - 1) * 100
    yoy_core_cpi = ((current_core_cpi / year_ago_core_cpi) - 1) * 100
    yoy_ppi = ((current_ppi / year_ago_ppi) - 1) * 100
    
    print(f"\n📈 Year-over-Year Changes:")
    print(f"CPI YoY: {yoy_cpi:.2f}%")
    print(f"Core CPI YoY: {yoy_core_cpi:.2f}%")
    print(f"PPI YoY: {yoy_ppi:.2f}%")
    
    # Calculate 5-year inflation rates
    if len(cpi_data) >= 60:
        five_year_ago_cpi = cpi_data.iloc[0]['CPIAUCSL']
        five_year_ago_core_cpi = cpi_data.iloc[0]['CPILFESL']
        five_year_ago_ppi = cpi_data.iloc[0]['PPIACO']
        
        five_year_cpi = ((current_cpi / five_year_ago_cpi) - 1) * 100
        five_year_core_cpi = ((current_core_cpi / five_year_ago_core_cpi) - 1) * 100
        five_year_ppi = ((current_ppi / five_year_ago_ppi) - 1) * 100
        
        print(f"\n📊 5-Year Average Annual Inflation:")
        print(f"CPI: {five_year_cpi/5:.2f}%")
        print(f"Core CPI: {five_year_core_cpi/5:.2f}%")
        print(f"PPI: {five_year_ppi/5:.2f}%")

# Display first few and last few data points
print(f"\n📈 Data Preview:")
print("First 5 observations:")
print(cpi_data.head())
print("\nLast 5 observations:")
print(cpi_data.tail())

# Create visualizations
print(f"\n🎨 Creating CPI visualizations...")

# Create a comprehensive inflation analysis chart
fig, axes = plt.subplots(2, 2, figsize=(16, 12))
fig.suptitle('Inflation Indicators Analysis - 5 Year History', fontsize=16, fontweight='bold')

# Chart 1: All Indicators Trend Over Time
axes[0,0].plot(cpi_data.index, cpi_data['CPIAUCSL'], 'b-', linewidth=2, marker='o', markersize=4, label='CPI (All Items)')
axes[0,0].plot(cpi_data.index, cpi_data['CPILFESL'], 'r-', linewidth=2, marker='s', markersize=4, label='Core CPI (Ex Food & Energy)')
axes[0,0].plot(cpi_data.index, cpi_data['PPIACO'], 'g-', linewidth=2, marker='^', markersize=4, label='PPI (Producer Price Index)')
axes[0,0].set_title('Inflation Indicators Trend (5 Years)', fontweight='bold')
axes[0,0].set_xlabel('Date')
axes[0,0].set_ylabel('Index Value')
axes[0,0].legend()
axes[0,0].grid(True, alpha=0.3)
axes[0,0].tick_params(axis='x', rotation=45)

# Chart 2: Year-over-Year Changes Comparison
if len(cpi_data) >= 12:
    cpi_data['CPI_YoY'] = cpi_data['CPIAUCSL'].pct_change(periods=12) * 100
    cpi_data['Core_CPI_YoY'] = cpi_data['CPILFESL'].pct_change(periods=12) * 100
    cpi_data['PPI_YoY'] = cpi_data['PPIACO'].pct_change(periods=12) * 100
    
    axes[0,1].plot(cpi_data.index[12:], cpi_data['CPI_YoY'][12:], 'b-', linewidth=2, label='CPI YoY', marker='o', markersize=3)
    axes[0,1].plot(cpi_data.index[12:], cpi_data['Core_CPI_YoY'][12:], 'r-', linewidth=2, label='Core CPI YoY', marker='s', markersize=3)
    axes[0,1].plot(cpi_data.index[12:], cpi_data['PPI_YoY'][12:], 'g-', linewidth=2, label='PPI YoY', marker='^', markersize=3)
    axes[0,1].set_title('Year-over-Year Changes Comparison (%)', fontweight='bold')
    axes[0,1].set_xlabel('Date')
    axes[0,1].set_ylabel('YoY Change (%)')
    axes[0,1].legend()
    axes[0,1].grid(True, alpha=0.3)
    axes[0,1].tick_params(axis='x', rotation=45)
    axes[0,1].axhline(y=0, color='black', linestyle='-', alpha=0.5)
else:
    axes[0,1].text(0.5, 0.5, 'Insufficient data for YoY analysis\n(Need at least 12 months)', 
                   ha='center', va='center', transform=axes[0,1].transAxes, fontsize=12)
    axes[0,1].set_title('Year-over-Year Changes Comparison (%)', fontweight='bold')

# Chart 3: CPI vs Core CPI Comparison
axes[1,0].plot(cpi_data.index, cpi_data['CPIAUCSL'], 'b-', label='CPI (All Items)', linewidth=2)
axes[1,0].plot(cpi_data.index, cpi_data['CPILFESL'], 'r-', label='Core CPI (Ex Food & Energy)', linewidth=2)
axes[1,0].set_title('CPI vs Core CPI Comparison', fontweight='bold')
axes[1,0].set_xlabel('Date')
axes[1,0].set_ylabel('Index Value')
axes[1,0].legend()
axes[1,0].grid(True, alpha=0.3)
axes[1,0].tick_params(axis='x', rotation=45)

# Chart 4: PPI vs CPI Comparison
axes[1,1].plot(cpi_data.index, cpi_data['PPIACO'], 'g-', label='PPI (Producer Price Index)', linewidth=2)
axes[1,1].plot(cpi_data.index, cpi_data['CPIAUCSL'], 'b-', label='CPI (Consumer Price Index)', linewidth=2, alpha=0.7)
axes[1,1].set_title('PPI vs CPI Comparison', fontweight='bold')
axes[1,1].set_xlabel('Date')
axes[1,1].set_ylabel('Index Value')
axes[1,1].legend()
axes[1,1].grid(True, alpha=0.3)
axes[1,1].tick_params(axis='x', rotation=45)

plt.tight_layout()

# Save the chart
chart_filename = 'inflation_analysis_charts.png'
plt.savefig(chart_filename, dpi=300, bbox_inches='tight')
print(f"✅ Inflation analysis charts saved as: {chart_filename}")

# Create a simple comparison chart
fig2, ax = plt.subplots(figsize=(12, 6))
ax.plot(cpi_data.index, cpi_data['CPIAUCSL'], 'b-', linewidth=2, label='CPI (All Items)', marker='o', markersize=4)
ax.plot(cpi_data.index, cpi_data['CPILFESL'], 'r-', linewidth=2, label='Core CPI (Ex Food & Energy)', marker='s', markersize=4)
ax.plot(cpi_data.index, cpi_data['PPIACO'], 'g-', linewidth=2, label='PPI (Producer Price Index)', marker='^', markersize=4)
ax.set_title('Inflation Indicators Comparison - 5 Year Trend', fontsize=14, fontweight='bold')
ax.set_xlabel('Date')
ax.set_ylabel('Index Value')
ax.legend()
ax.grid(True, alpha=0.3)
ax.tick_params(axis='x', rotation=45)

plt.tight_layout()
plt.savefig('inflation_comparison_chart.png', dpi=300, bbox_inches='tight')
print(f"✅ Inflation comparison chart saved as: inflation_comparison_chart.png")

# Generate summary statistics
print(f"\n📋 Inflation Indicators Summary Statistics:")
print(f"\nCPI (All Items):")
print(f"  Mean: {cpi_data['CPIAUCSL'].mean():.2f}")
print(f"  Median: {cpi_data['CPIAUCSL'].median():.2f}")
print(f"  Std Dev: {cpi_data['CPIAUCSL'].std():.2f}")
print(f"  Range: {cpi_data['CPIAUCSL'].min():.2f} to {cpi_data['CPIAUCSL'].max():.2f}")

print(f"\nCore CPI (Ex Food & Energy):")
print(f"  Mean: {cpi_data['CPILFESL'].mean():.2f}")
print(f"  Median: {cpi_data['CPILFESL'].median():.2f}")
print(f"  Std Dev: {cpi_data['CPILFESL'].std():.2f}")
print(f"  Range: {cpi_data['CPILFESL'].min():.2f} to {cpi_data['CPILFESL'].max():.2f}")

print(f"\nPPI (Producer Price Index):")
print(f"  Mean: {cpi_data['PPIACO'].mean():.2f}")
print(f"  Median: {cpi_data['PPIACO'].median():.2f}")
print(f"  Std Dev: {cpi_data['PPIACO'].std():.2f}")
print(f"  Range: {cpi_data['PPIACO'].min():.2f} to {cpi_data['PPIACO'].max():.2f}")

# Calculate and display YoY statistics
if len(cpi_data) >= 12:
    print(f"\n💰 Year-over-Year Analysis:")
    
    if len(cpi_data) >= 60:
        # Calculate YoY statistics for all indicators
        cpi_data['CPI_YoY'] = cpi_data['CPIAUCSL'].pct_change(periods=12) * 100
        cpi_data['Core_CPI_YoY'] = cpi_data['CPILFESL'].pct_change(periods=12) * 100
        cpi_data['PPI_YoY'] = cpi_data['PPIACO'].pct_change(periods=12) * 100
        
        print(f"\nCPI YoY Statistics:")
        print(f"  Range: {cpi_data['CPI_YoY'].min():.2f}% to {cpi_data['CPI_YoY'].max():.2f}%")
        print(f"  Mean: {cpi_data['CPI_YoY'].mean():.2f}%")
        print(f"  Volatility: {cpi_data['CPI_YoY'].std():.2f}%")
        
        print(f"\nCore CPI YoY Statistics:")
        print(f"  Range: {cpi_data['Core_CPI_YoY'].min():.2f}% to {cpi_data['Core_CPI_YoY'].max():.2f}%")
        print(f"  Mean: {cpi_data['Core_CPI_YoY'].mean():.2f}%")
        print(f"  Volatility: {cpi_data['Core_CPI_YoY'].std():.2f}%")
        
        print(f"\nPPI YoY Statistics:")
        print(f"  Range: {cpi_data['PPI_YoY'].min():.2f}% to {cpi_data['PPI_YoY'].max():.2f}%")
        print(f"  Mean: {cpi_data['PPI_YoY'].mean():.2f}%")
        print(f"  Volatility: {cpi_data['PPI_YoY'].std():.2f}%")

print(f"\n" + "=" * 50)
print("Inflation indicators analysis complete!")
print("=" * 50)
