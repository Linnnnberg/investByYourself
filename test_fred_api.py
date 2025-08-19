import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
from fredapi import Fred
from datetime import datetime, timedelta
import numpy as np

# Set seaborn style for better looking charts
sns.set_style("whitegrid")
plt.rcParams['figure.figsize'] = (12, 8)

print("Testing FRED API for CPI data...")
print("=" * 50)

# Initialize FRED API
# Note: You'll need to get a free API key from https://fred.stlouisfed.org/docs/api/api_key.html
try:
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
        start_date = end_date - timedelta(days=365)
        
        # Generate sample CPI data (monthly)
        dates = pd.date_range(start=start_date, end=end_date, freq='ME')
        sample_cpi = [300 + i*0.5 + np.random.normal(0, 0.1) for i in range(len(dates))]
        
        cpi_data = pd.DataFrame({
            'date': dates,
            'CPIAUCSL': sample_cpi
        })
        cpi_data.set_index('date', inplace=True)
        
        print("✅ Sample CPI data created for demonstration")
        
    else:
        print("✅ FRED API key found, fetching real data...")
        fred = Fred(api_key=api_key)
        
        # Get CPI data (Consumer Price Index for All Urban Consumers: All Items)
        # CPIAUCSL is the most commonly used CPI series
        end_date = datetime.now()
        start_date = end_date - timedelta(days=365)
        
        cpi_data = fred.get_series('CPIAUCSL', start_date, end_date)
        print(f"✅ Successfully fetched {len(cpi_data)} CPI data points")

except Exception as e:
    print(f"❌ Error initializing FRED API: {e}")
    print("Creating sample data for demonstration...")
    
    # Create sample data as fallback
    end_date = datetime.now()
    start_date = end_date - timedelta(days=365)
    dates = pd.date_range(start=start_date, end=end_date, freq='ME')
    sample_cpi = [300 + i*0.5 + np.random.normal(0, 0.1) for i in range(len(dates))]
    
    cpi_data = pd.DataFrame({
        'date': dates,
        'CPIAUCSL': sample_cpi
    })
    cpi_data.set_index('date', inplace=True)

# Display basic information about the data
print(f"\n📊 CPI Data Summary:")
print(f"Date Range: {cpi_data.index.min().strftime('%Y-%m-%d')} to {cpi_data.index.max().strftime('%Y-%m-%d')}")
print(f"Number of observations: {len(cpi_data)}")
print(f"Latest CPI value: {cpi_data.iloc[-1]['CPIAUCSL']:.2f}")
print(f"CPI change over period: {((cpi_data.iloc[-1]['CPIAUCSL'] / cpi_data.iloc[0]['CPIAUCSL']) - 1) * 100:.2f}%")

# Calculate year-over-year inflation rate
if len(cpi_data) >= 12:
    current_cpi = cpi_data.iloc[-1]['CPIAUCSL']
    year_ago_cpi = cpi_data.iloc[0]['CPIAUCSL']  # First observation (1 year ago)
    yoy_inflation = ((current_cpi / year_ago_cpi) - 1) * 100
    print(f"Year-over-year inflation rate: {yoy_inflation:.2f}%")

# Display first few and last few data points
print(f"\n📈 CPI Data Preview:")
print("First 5 observations:")
print(cpi_data.head())
print("\nLast 5 observations:")
print(cpi_data.tail())

# Create visualizations
print(f"\n🎨 Creating CPI visualizations...")

# Create a comprehensive CPI analysis chart
fig, axes = plt.subplots(2, 2, figsize=(16, 12))
fig.suptitle('Consumer Price Index (CPI) Analysis - 1 Year History', fontsize=16, fontweight='bold')

# Chart 1: CPI Trend Over Time
axes[0,0].plot(cpi_data.index, cpi_data['CPIAUCSL'], 'b-', linewidth=2, marker='o', markersize=4)
axes[0,0].set_title('CPI Trend (1 Year)', fontweight='bold')
axes[0,0].set_xlabel('Date')
axes[0,0].set_ylabel('CPI Value')
axes[0,0].grid(True, alpha=0.3)
axes[0,0].tick_params(axis='x', rotation=45)

# Chart 2: Month-over-Month Change
cpi_data['MoM_Change'] = cpi_data['CPIAUCSL'].pct_change() * 100
axes[0,1].bar(cpi_data.index[1:], cpi_data['MoM_Change'][1:], color='orange', alpha=0.7)
axes[0,1].set_title('Month-over-Month CPI Change (%)', fontweight='bold')
axes[0,1].set_xlabel('Date')
axes[0,1].set_ylabel('Change (%)')
axes[0,1].grid(True, alpha=0.3)
axes[0,1].tick_params(axis='x', rotation=45)
axes[0,1].axhline(y=0, color='black', linestyle='-', alpha=0.5)

# Chart 3: Rolling 3-Month Average
cpi_data['Rolling_3M'] = cpi_data['CPIAUCSL'].rolling(window=3).mean()
axes[1,0].plot(cpi_data.index, cpi_data['CPIAUCSL'], 'b-', label='Actual CPI', alpha=0.7)
axes[1,0].plot(cpi_data.index, cpi_data['Rolling_3M'], 'r-', label='3-Month Rolling Average', linewidth=2)
axes[1,0].set_title('CPI with 3-Month Rolling Average', fontweight='bold')
axes[1,0].set_xlabel('Date')
axes[1,0].set_ylabel('CPI Value')
axes[1,0].legend()
axes[1,0].grid(True, alpha=0.3)
axes[1,0].tick_params(axis='x', rotation=45)

# Chart 4: Year-over-Year Change
if len(cpi_data) >= 12:
    cpi_data['YoY_Change'] = cpi_data['CPIAUCSL'].pct_change(periods=12) * 100
    axes[1,1].plot(cpi_data.index[12:], cpi_data['YoY_Change'][12:], 'g-', linewidth=2, marker='s')
    axes[1,1].set_title('Year-over-Year CPI Change (%)', fontweight='bold')
    axes[1,1].set_xlabel('Date')
    axes[1,1].set_ylabel('YoY Change (%)')
    axes[1,1].grid(True, alpha=0.3)
    axes[1,1].tick_params(axis='x', rotation=45)
    axes[1,1].axhline(y=0, color='black', linestyle='-', alpha=0.5)
else:
    axes[1,1].text(0.5, 0.5, 'Insufficient data for YoY analysis\n(Need at least 12 months)', 
                   ha='center', va='center', transform=axes[1,1].transAxes, fontsize=12)
    axes[1,1].set_title('Year-over-Year CPI Change (%)', fontweight='bold')

plt.tight_layout()

# Save the chart
chart_filename = 'cpi_analysis_charts.png'
plt.savefig(chart_filename, dpi=300, bbox_inches='tight')
print(f"✅ CPI analysis charts saved as: {chart_filename}")

# Create a simple trend chart
fig2, ax = plt.subplots(figsize=(12, 6))
ax.plot(cpi_data.index, cpi_data['CPIAUCSL'], 'b-', linewidth=3, marker='o', markersize=6)
ax.set_title('Consumer Price Index (CPI) - 1 Year Trend', fontsize=14, fontweight='bold')
ax.set_xlabel('Date')
ax.set_ylabel('CPI Value')
ax.grid(True, alpha=0.3)
ax.tick_params(axis='x', rotation=45)

# Add trend line
z = np.polyfit(range(len(cpi_data)), cpi_data['CPIAUCSL'], 1)
p = np.poly1d(z)
ax.plot(cpi_data.index, p(range(len(cpi_data))), "r--", alpha=0.8, label=f'Trend Line (slope: {z[0]:.3f})')
ax.legend()

plt.tight_layout()
plt.savefig('cpi_trend_chart.png', dpi=300, bbox_inches='tight')
print(f"✅ CPI trend chart saved as: cpi_trend_chart.png")

# Generate summary statistics
print(f"\n📋 CPI Summary Statistics:")
print(f"Mean CPI: {cpi_data['CPIAUCSL'].mean():.2f}")
print(f"Median CPI: {cpi_data['CPIAUCSL'].median():.2f}")
print(f"Standard Deviation: {cpi_data['CPIAUCSL'].std():.2f}")
print(f"Minimum CPI: {cpi_data['CPIAUCSL'].min():.2f}")
print(f"Maximum CPI: {cpi_data['CPIAUCSL'].max():.2f}")

# Calculate and display inflation metrics
if len(cpi_data) >= 12:
    print(f"\n💰 Inflation Analysis:")
    print(f"Starting CPI: {cpi_data.iloc[0]['CPIAUCSL']:.2f}")
    print(f"Ending CPI: {cpi_data.iloc[-1]['CPIAUCSL']:.2f}")
    print(f"Total Change: {((cpi_data.iloc[-1]['CPIAUCSL'] / cpi_data.iloc[0]['CPIAUCSL']) - 1) * 100:.2f}%")
    print(f"Average Monthly Change: {cpi_data['MoM_Change'].mean():.2f}%")
    print(f"Year-over-Year Inflation: {yoy_inflation:.2f}%")

print(f"\n" + "=" * 50)
print("CPI analysis complete!")
print("=" * 50)
