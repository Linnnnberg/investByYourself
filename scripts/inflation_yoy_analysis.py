#!/usr/bin/env python3
"""
Year-over-Year Inflation Changes Plot
Plots YoY changes for CPI, Core CPI, and PPI with clean visualization
"""

import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
from fredapi import Fred
from datetime import datetime, timedelta
import numpy as np
import os

# Set seaborn style for better looking charts
sns.set_style("whitegrid")
plt.rcParams['figure.figsize'] = (14, 8)
plt.rcParams['font.size'] = 12

print("📊 Creating Year-over-Year Inflation Changes Plot...")
print("=" * 60)

def fetch_inflation_data():
    """Fetch inflation data from FRED API or create sample data"""
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
        api_key = os.getenv('FRED_API_KEY')
        
        if not api_key:
            print("⚠️  FRED API key not found. Using sample data for demonstration...")
            return create_sample_data()
        
        print("✅ FRED API key found, fetching real data...")
        fred = Fred(api_key=api_key)
        
        # Get data for 5 years
        end_date = datetime.now()
        start_date = end_date - timedelta(days=1825)  # 5 years of data
        
        # Fetch multiple series
        cpi_data = fred.get_series('CPIAUCSL', start_date, end_date)  # CPI All Items
        core_cpi_data = fred.get_series('CPILFESL', start_date, end_date)  # Core CPI
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
        
        return combined_data
        
    except Exception as e:
        print(f"❌ Error fetching data: {e}")
        print("Creating sample data for demonstration...")
        return create_sample_data()

def create_sample_data():
    """Create realistic sample data for demonstration"""
    end_date = datetime.now()
    start_date = end_date - timedelta(days=1825)  # 5 years of data
    
    # Generate sample data (monthly) with realistic inflation patterns
    dates = pd.date_range(start=start_date, end=end_date, freq='ME')
    
    # Create realistic inflation trends with some volatility
    base_cpi = 280
    base_core_cpi = 280
    base_ppi = 120
    
    # Add trend and seasonal components
    trend_cpi = [base_cpi + i*0.3 for i in range(len(dates))]
    trend_core_cpi = [base_core_cpi + i*0.25 for i in range(len(dates))]
    trend_ppi = [base_ppi + i*0.2 for i in range(len(dates))]
    
    # Add realistic volatility (CPI more stable than PPI)
    sample_cpi = [v + np.random.normal(0, 0.1) for v in trend_cpi]
    sample_core_cpi = [v + np.random.normal(0, 0.08) for v in trend_core_cpi]
    sample_ppi = [v + np.random.normal(0, 0.15) for v in trend_ppi]
    
    # Add some inflation spikes (like 2022-2023)
    spike_period = len(dates) // 2
    for i in range(spike_period, min(spike_period + 12, len(dates))):
        sample_cpi[i] += np.random.uniform(0.5, 1.0)
        sample_core_cpi[i] += np.random.uniform(0.3, 0.8)
        sample_ppi[i] += np.random.uniform(0.8, 1.5)
    
    sample_data = pd.DataFrame({
        'CPIAUCSL': sample_cpi,
        'CPILFESL': sample_core_cpi,
        'PPIACO': sample_ppi
    }, index=dates)
    
    print("✅ Sample inflation data created with realistic patterns")
    return sample_data

def calculate_yoy_changes(data):
    """Calculate year-over-year percentage changes"""
    if len(data) < 12:
        print("❌ Insufficient data for YoY analysis (need at least 12 months)")
        return None
    
    # Calculate YoY changes
    yoy_data = pd.DataFrame()
    yoy_data['CPI_YoY'] = data['CPIAUCSL'].pct_change(periods=12) * 100
    yoy_data['Core_CPI_YoY'] = data['CPILFESL'].pct_change(periods=12) * 100
    yoy_data['PPI_YoY'] = data['PPIACO'].pct_change(periods=12) * 100
    
    # Remove NaN values (first 12 months)
    yoy_data = yoy_data.dropna()
    
    return yoy_data

def create_yoy_plot(data, yoy_data):
    """Create the YoY changes plot"""
    fig, ax = plt.subplots(1, 1, figsize=(14, 8))
    
    # Plot: Year-over-Year Changes (Main Focus)
    ax.plot(yoy_data.index, yoy_data['CPI_YoY'], 'b-', linewidth=3, label='CPI YoY', marker='o', markersize=4)
    ax.plot(yoy_data.index, yoy_data['Core_CPI_YoY'], 'r-', linewidth=3, label='Core CPI YoY', marker='s', markersize=4)
    ax.plot(yoy_data.index, yoy_data['PPI_YoY'], 'g-', linewidth=3, label='PPI YoY', marker='^', markersize=4)
    
    # Add zero line for reference
    ax.axhline(y=0, color='black', linestyle='-', alpha=0.7, linewidth=1)
    
    # Add target inflation line (2% Fed target)
    ax.axhline(y=2, color='orange', linestyle='--', alpha=0.7, linewidth=1, label='Fed Target (2%)')
    
    ax.set_title('Year-over-Year Inflation Changes (%)', fontsize=16, fontweight='bold')
    ax.set_xlabel('Date')
    ax.set_ylabel('YoY Change (%)')
    ax.legend(loc='upper right')
    ax.grid(True, alpha=0.3)
    ax.tick_params(axis='x', rotation=45)
    
    # Set y-axis limits for better visualization
    y_max = max(yoy_data.max().max(), 2) * 1.1
    y_min = min(yoy_data.min().min(), 0) * 1.1
    ax.set_ylim(y_min, y_max)
    
    # Add annotations for key insights
    latest_cpi_yoy = yoy_data['CPI_YoY'].iloc[-1]
    latest_core_yoy = yoy_data['Core_CPI_YoY'].iloc[-1]
    latest_ppi_yoy = yoy_data['PPI_YoY'].iloc[-1]
    
    ax.annotate(f'Latest CPI: {latest_cpi_yoy:.1f}%', 
                 xy=(yoy_data.index[-1], latest_cpi_yoy),
                 xytext=(10, 10), textcoords='offset points',
                 bbox=dict(boxstyle='round,pad=0.3', facecolor='lightblue', alpha=0.7),
                 arrowprops=dict(arrowstyle='->', connectionstyle='arc3,rad=0'))
    
    ax.annotate(f'Latest Core CPI: {latest_core_yoy:.1f}%', 
                 xy=(yoy_data.index[-1], latest_core_yoy),
                 xytext=(10, -20), textcoords='offset points',
                 bbox=dict(boxstyle='round,pad=0.3', facecolor='lightcoral', alpha=0.7),
                 arrowprops=dict(arrowstyle='->', connectionstyle='arc3,rad=0'))
    
    ax.annotate(f'Latest PPI: {latest_ppi_yoy:.1f}%', 
                 xy=(yoy_data.index[-1], latest_ppi_yoy),
                 xytext=(10, 30), textcoords='offset points',
                 bbox=dict(boxstyle='round,pad=0.3', facecolor='lightgreen', alpha=0.7),
                 arrowprops=dict(arrowstyle='->', connectionstyle='arc3,rad=0'))
    
    plt.tight_layout()
    return fig

def main():
    """Main function to create YoY inflation plot"""
    # Fetch or create data
    inflation_data = fetch_inflation_data()
    
    # Calculate YoY changes
    yoy_data = calculate_yoy_changes(inflation_data)
    if yoy_data is None:
        return
    
    # Display summary statistics
    print(f"\n📊 Inflation Data Summary:")
    print(f"Date Range: {inflation_data.index.min().strftime('%Y-%m-%d')} to {inflation_data.index.max().strftime('%Y-%m-%d')}")
    print(f"Number of observations: {len(inflation_data)}")
    
    print(f"\n📈 Latest Values:")
    print(f"CPI (All Items): {inflation_data.iloc[-1]['CPIAUCSL']:.2f}")
    print(f"Core CPI (Ex Food & Energy): {inflation_data.iloc[-1]['CPILFESL']:.2f}")
    print(f"PPI (Producer Price Index): {inflation_data.iloc[-1]['PPIACO']:.2f}")
    
    print(f"\n📊 Latest Year-over-Year Changes:")
    print(f"CPI YoY: {yoy_data['CPI_YoY'].iloc[-1]:.2f}%")
    print(f"Core CPI YoY: {yoy_data['Core_CPI_YoY'].iloc[-1]:.2f}%")
    print(f"PPI YoY: {yoy_data['PPI_YoY'].iloc[-1]:.2f}%")
    
    # Create the plot
    print(f"\n🎨 Creating YoY inflation changes plot...")
    fig = create_yoy_plot(inflation_data, yoy_data)
    
    # Save the plot
    output_file = 'charts/yoy_inflation_analysis.png'
    os.makedirs('charts', exist_ok=True)
    fig.savefig(output_file, dpi=300, bbox_inches='tight')
    print(f"✅ Plot saved to: {output_file}")
    
    # Display additional insights
    print(f"\n🔍 Key Insights:")
    
    # Trend analysis
    recent_trend = yoy_data.tail(6)  # Last 6 months
    cpi_trend = recent_trend['CPI_YoY'].pct_change().mean()
    core_trend = recent_trend['Core_CPI_YoY'].pct_change().mean()
    ppi_trend = recent_trend['PPI_YoY'].pct_change().mean()
    
    print(f"Recent CPI trend: {'↗️ Increasing' if cpi_trend > 0 else '↘️ Decreasing'} ({cpi_trend:.2f}% per month)")
    print(f"Recent Core CPI trend: {'↗️ Increasing' if core_trend > 0 else '↘️ Decreasing'} ({core_trend:.2f}% per month)")
    print(f"Recent PPI trend: {'↗️ Increasing' if ppi_trend > 0 else '↘️ Decreasing'} ({ppi_trend:.2f}% per month)")
    
    # Volatility comparison
    cpi_vol = yoy_data['CPI_YoY'].std()
    core_vol = yoy_data['Core_CPI_YoY'].std()
    ppi_vol = yoy_data['PPI_YoY'].std()
    
    print(f"\n📊 Volatility (Standard Deviation):")
    print(f"CPI YoY: {cpi_vol:.2f}%")
    print(f"Core CPI YoY: {core_vol:.2f}%")
    print(f"PPI YoY: {ppi_vol:.2f}%")
    
    # Show the plot
    plt.show()
    
    print(f"\n🎉 YoY inflation analysis complete!")
    print(f"📁 Chart saved to: {output_file}")

if __name__ == "__main__":
    main()
