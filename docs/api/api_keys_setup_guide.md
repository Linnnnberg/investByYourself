# API Keys Setup Guide - InvestByYourself Data Collection Framework

## Overview
This guide explains how to obtain and configure API keys for the various data sources used in our ETL pipeline.

## Required API Keys

### 1. FRED API Key (Federal Reserve Economic Data)
**Status**: ✅ **AVAILABLE** - You have this key

**What it provides**:
- Economic indicators (GDP, unemployment, inflation)
- Federal Reserve data
- Historical economic time series
- Category and series information

**Rate Limits**: 120 calls per minute (generous)

**How to apply**:
1. Visit [FRED API Registration](https://fred.stlouisfed.org/docs/api/api_key.html)
2. Fill out the registration form
3. Receive your API key immediately via email
4. No approval process required

**Environment Variable**: `FRED_API_KEY`

---

### 2. Alpha Vantage API Key
**Status**: ⚠️ **NEEDED** - Apply for free tier

**What it provides**:
- Stock market data and time series
- Technical indicators
- Fundamental company data
- Forex and cryptocurrency data

**Rate Limits**: 5 calls per minute (free tier), 500+ calls per minute (paid)

**How to apply**:
1. Visit [Alpha Vantage](https://www.alphavantage.co/support/#api-key)
2. Click "Get Your Free API Key"
3. Fill out the form with your email
4. Receive your API key immediately
5. Free tier available with registration

**Environment Variable**: `ALPHA_VANTAGE_API_KEY`

---

### 3. Yahoo Finance
**Status**: ✅ **NO KEY REQUIRED** - Free public access

**What it provides**:
- Company profiles and fundamentals
- Financial statements
- Market data and quotes
- Options and dividend data

**Rate Limits**: 5000 calls per day (generous)

**Environment Variable**: None required

---

## Configuration Methods

### Method 1: Environment Variables (Recommended)
Set these in your shell or system environment:

```bash
# Windows PowerShell
$env:FRED_API_KEY="your_fred_api_key_here"
$env:ALPHA_VANTAGE_API_KEY="your_alpha_vantage_api_key_here"

# Windows Command Prompt
set FRED_API_KEY=your_fred_api_key_here
set ALPHA_VANTAGE_API_KEY=your_alpha_vantage_api_key_here

# Linux/macOS
export FRED_API_KEY="your_fred_api_key_here"
export ALPHA_VANTAGE_API_KEY="your_alpha_vantage_api_key_here"
```

### Method 2: .env File (Development)
Create a `.env` file in your project root:

```env
FRED_API_KEY=your_fred_api_key_here
ALPHA_VANTAGE_API_KEY=your_alpha_vantage_api_key_here
```

**Note**: Add `.env` to your `.gitignore` to keep keys secure.

### Method 3: Direct Configuration (Testing)
Pass keys directly to collectors in your code:

```python
async with FREDCollector(api_key="your_key") as collector:
    # Your code here
```

---

## Testing Your Setup

### Quick Test
Run the test script to verify your API keys work:

```bash
python scripts/test_data_collection_framework.py
```

### Expected Output
With all keys configured, you should see:
- ✅ Yahoo Finance tests (always work)
- ✅ Alpha Vantage tests (with valid key)
- ✅ FRED tests (with valid key)
- ✅ Orchestrator tests (with valid keys)

---

## Security Best Practices

1. **Never commit API keys to version control**
2. **Use environment variables in production**
3. **Rotate keys periodically**
4. **Monitor API usage and rate limits**
5. **Use least-privilege access when possible**

---

## Troubleshooting

### Common Issues

**"API key not available"**
- Check environment variable spelling
- Verify the variable is set in your current shell
- Restart your terminal/IDE after setting variables

**"Rate limit exceeded"**
- Alpha Vantage: Wait 1 minute between calls (free tier)
- FRED: Very generous limits, check your usage
- Yahoo Finance: Usually not an issue

**"Invalid API key"**
- Verify the key is correct
- Check if the service is experiencing issues
- Ensure you're using the right key for the right service

### Getting Help
- Check the [FRED API documentation](https://fred.stlouisfed.org/docs/api/)
- Check the [Alpha Vantage documentation](https://www.alphavantage.co/documentation/)
- Review our test scripts for usage examples

---

## Next Steps

1. **Apply for Alpha Vantage API key** (free)
2. **Set your FRED API key** in environment variables
3. **Test the framework** with all data sources
4. **Move to Phase 2** of Tech-009 implementation

Your FRED API key is already available, so you're ready to test economic data collection!
