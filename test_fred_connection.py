import os
from dotenv import load_dotenv
from fredapi import Fred

# Load environment variables
load_dotenv()

# Get API key
api_key = os.getenv('FRED_API_KEY')
print(f"API Key found: {'Yes' if api_key else 'No'}")
if api_key:
    print(f"API Key length: {len(api_key)}")
    print(f"API Key starts with: {api_key[:8]}...")

try:
    # Initialize FRED API
    fred = Fred(api_key=api_key)
    print("✅ FRED API initialized successfully")
    
    # Test with a simple series
    cpi_data = fred.get_series('CPIAUCSL', limit=5)
    print(f"✅ Successfully fetched CPI data: {len(cpi_data)} observations")
    print("Latest CPI values:")
    print(cpi_data.tail())
    
except Exception as e:
    print(f"❌ Error: {e}")
    print(f"Error type: {type(e)}")
