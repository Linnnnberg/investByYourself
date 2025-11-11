# TGA Liquidity Tracking Demo

**Interactive prototype demonstrating Treasury General Account (TGA) liquidity tracking**

## Quick Start

### 1. Install Dependencies

```bash
pip install plotly pandas requests
```

### 2. Run the Demo

```bash
cd /home/user/investByYourself
python demos/tga_liquidity_demo.py
```

The demo will:
1. ✅ Fetch last 24 months of TGA data from US Treasury API
2. 📊 Calculate liquidity metrics (daily changes, moving averages, z-scores, stress indicators)
3. 🌐 Open an interactive dashboard in your default browser

## What You'll See

### Interactive Dashboard (3 Charts)

#### **Chart 1: TGA Balance & Moving Averages**
- Blue line: Daily TGA closing balance
- Orange dashed: 7-day moving average
- Red dotted: 30-day moving average
- Red X markers: Liquidity stress periods

#### **Chart 2: Liquidity Index**
- Green area: Cumulative liquidity contribution
- Above zero = Net liquidity ADDED to markets
- Below zero = Net liquidity DRAINED from markets

#### **Chart 3: Daily Changes & Volatility**
- Green bars: Days when TGA decreased (liquidity added)
- Red bars: Days when TGA increased (liquidity drained)
- Pink line: 30-day volatility (right axis)

### Console Output

The demo prints comprehensive analysis:
- Latest TGA metrics (balance, daily change, volatility, z-score)
- 30-day trends (average daily change, max drain/add, stress days)
- Historical context (percentiles)
- Liquidity phases (draining vs adding days)
- Current market liquidity interpretation

## Understanding the Metrics

### Liquidity Index
**Formula:** `Cumulative sum of (-ΔTGA)`

- TGA **increases** → Money **leaves** markets → Liquidity **drained** (negative)
- TGA **decreases** → Money **enters** markets → Liquidity **added** (positive)

**Example:**
- Day 1: TGA goes from $500B → $550B (+$50B change)
  - Liquidity Index: -$50B (markets drained)
- Day 2: TGA goes from $550B → $520B (-$30B change)
  - Liquidity Index: -$50B + $30B = -$20B (net drain)

### Stress Indicators
**Triggers:**
- |Z-score| > 2 (more than 2 standard deviations from 90-day mean)
- OR Volatility > 90th percentile (unusually high TGA fluctuations)

**Interpretation:**
- 🚨 Stress = Abnormal TGA behavior, potential market volatility
- ✅ Normal = TGA within expected ranges

### Moving Averages
- **7-day MA:** Short-term trend (weekly)
- **30-day MA:** Medium-term trend (monthly)
- Crossovers can signal trend changes

## Interactive Features

- **Hover:** Detailed data tooltips
- **Zoom:** Click and drag on chart
- **Pan:** Shift + drag to move view
- **Reset:** Double-click to reset zoom
- **Toggle:** Click legend items to show/hide series

## Example Output

```
======================================================================
📊 TGA LIQUIDITY TRACKING DEMO
======================================================================

🔄 Fetching TGA data from US Treasury (last 24 months)...
✅ Successfully fetched 520 records
📅 Date range: 2023-11-11 to 2025-11-11

🔢 Calculating liquidity metrics...
✅ Metrics calculated

📈 LATEST TGA METRICS (2025-11-11):
   Balance: $450.2B
   Daily Change: -$15.3B
   7-day MA: $455.7B
   30-day MA: $465.1B
   Volatility: $12.5B
   Z-score: 1.23
   Liquidity Index: $125.4B
   Stress: ✅ NO

======================================================================
📊 LIQUIDITY ANALYSIS
======================================================================

📈 30-Day Trends:
   TGA Change: -$45.2B
   Average Daily Change: -$1.5B
   Max Daily Drain: $35.2B
   Max Daily Add: -$28.7B
   Stress Days: 2 / 30

📊 Historical Context:
   Current TGA at 45.2th percentile (historical)
   Current volatility at 62.1th percentile

💧 Liquidity Phases (last 90 days):
   Draining: 38 days (42.2%) 📉
   Adding: 52 days (57.8%) 📈

🎯 Current Market Liquidity:
   ✅ Net liquidity ADDED: $125.4B since start
   💡 Interpretation: Treasury operations have added liquidity to markets
   ✅ Normal liquidity conditions

======================================================================
🌐 Opening interactive dashboard in browser...
======================================================================
```

## Methodology

This demo uses the **simple cumulative method** from your original code:

```python
# Daily change
dTGA = close_today_bal - close_yesterday_bal

# Liquidity Index (cumulative)
LiquidityIndex = cumsum(-dTGA)
```

**Plus enhanced metrics:**
- Moving averages (7d, 30d)
- Volatility (30d rolling std)
- Z-scores (statistical outliers)
- Stress detection (automated)

## Data Source

**US Treasury Fiscal Data API**
- Endpoint: https://fiscaldata.treasury.gov/
- Dataset: Daily Treasury Statement - Operating Cash Balance
- Frequency: Daily (business days)
- No API key required

## Troubleshooting

### "ModuleNotFoundError: No module named 'plotly'"
```bash
pip install plotly pandas requests
```

### "No data received from Treasury API"
- Check internet connection
- Treasury API may be temporarily down
- Try reducing lookback period: edit line 20 to `fetch_tga_data(lookback_months=12)`

### "Dashboard doesn't open in browser"
- Plotly saves HTML file, check for `temp-plot.html` in current directory
- Manually open the HTML file in browser

### "SSL Certificate Error"
```bash
pip install --upgrade certifi
```

## Next Steps

After running the demo:
1. ✅ See the **full production implementation** in:
   - `etl/src/collectors/tga_collector.py` (async, retry logic)
   - `etl/src/transformers/tga_liquidity_transformer.py` (advanced metrics)
   - `database/migrations/002_tga_liquidity_tracking.sql` (persistence)

2. 📖 Read comprehensive analysis:
   - `docs/TGA_LIQUIDITY_ANALYSIS.md` (900-line guide)

3. 🧪 Run production tests:
   ```bash
   python etl/scripts/test_tga_liquidity.py
   ```

## Questions?

- **What is TGA?** Treasury General Account - The US government's checking account at the Fed
- **Why track it?** TGA changes directly affect market liquidity (bank reserves)
- **Is this real-time?** No, Treasury publishes data daily (typically 4 PM ET)
- **Can I use this for trading?** This is educational/research. Always do your own analysis.

---

**Built for InvestByYourself Platform** | Simple Demo Version
