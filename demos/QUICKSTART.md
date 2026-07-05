# 🚀 Quick Start - TGA Liquidity Demo

## 30-Second Start

```bash
# Install dependencies
pip install plotly pandas requests

# Run demo with sample data (works offline)
python demos/tga_liquidity_demo_with_sample_data.py
```

**🌐 Opens interactive dashboard in your browser automatically!**

---

## Two Demo Versions

### 1️⃣ **Sample Data Demo** (Recommended for first-time users)
✅ Works offline
✅ No API dependencies
✅ Shows all features immediately

```bash
python demos/tga_liquidity_demo_with_sample_data.py
```

### 2️⃣ **Real Data Demo** (For actual analysis)
📊 Fetches real TGA data from US Treasury
🔄 Last 24 months of data
⚡ Requires internet connection

```bash
python demos/tga_liquidity_demo.py
```

---

## What You'll See

### 📊 Interactive Dashboard (3 Charts)

```
┌─────────────────────────────────────────────────────────────┐
│  Chart 1: TGA Balance & Moving Averages                     │
│  • Blue line = Daily TGA balance                            │
│  • Orange dashed = 7-day moving average                     │
│  • Red dotted = 30-day moving average                       │
│  • Red X marks = Liquidity stress periods ⚠️                │
├─────────────────────────────────────────────────────────────┤
│  Chart 2: Liquidity Index                                   │
│  • Green area = Cumulative liquidity contribution           │
│  • Above zero = Net liquidity ADDED to markets ✅           │
│  • Below zero = Net liquidity DRAINED from markets 📉       │
├─────────────────────────────────────────────────────────────┤
│  Chart 3: Daily Changes & Volatility                        │
│  • Green bars = Days TGA decreased (liquidity added)        │
│  • Red bars = Days TGA increased (liquidity drained)        │
│  • Pink line = 30-day volatility (right axis)               │
└─────────────────────────────────────────────────────────────┘
```

### 📈 Console Analysis

The demo prints comprehensive metrics:

```
📈 LATEST TGA METRICS (2025-11-11):
   Balance: $393.8B
   Daily Change: $3.66B
   7-day MA: $387.5B
   30-day MA: $355.8B
   Volatility: $27.91B
   Z-score: 2.38
   Liquidity Index: $103.0B
   Stress: ⚠️  YES

📊 LIQUIDITY ANALYSIS
   30-Day Trends:
      TGA Change: $83.3B
      Max Daily Drain: $14.21B
      Stress Days: 11 / 30

   Historical Context:
      Current TGA at 40.6th percentile
      Current volatility at 87.0th percentile

   Liquidity Phases (last 90 days):
      Draining: 53 days (58.9%) 📉
      Adding: 37 days (41.1%) 📈
```

---

## Interactive Features

Once the dashboard opens in your browser:

| Action | How To |
|--------|--------|
| **Zoom** | Click and drag on chart |
| **Pan** | Shift + drag |
| **Reset** | Double-click anywhere on chart |
| **Hover** | Mouse over for detailed tooltips |
| **Toggle** | Click legend items to show/hide |
| **Save** | Click camera icon (top-right) for PNG |

---

## Understanding the Metrics

### 🔵 TGA Balance
**What:** US Treasury's checking account balance at the Fed
**Typical Range:** $200B - $800B
**Why It Matters:** Changes directly affect bank reserves & market liquidity

### 🟢 Liquidity Index
**Formula:** `Cumulative sum of (-ΔTGA)`
**Interpretation:**
- Positive = Treasury operations have **added** liquidity to markets
- Negative = Treasury operations have **drained** liquidity from markets

**Example:**
- TGA rises $50B → Markets **lose** $50B in liquidity → Index: -50
- TGA drops $30B → Markets **gain** $30B in liquidity → Index: -50 + 30 = -20

### ⚠️ Stress Indicators
**Triggers:**
- Z-score > 2 (TGA is 2+ standard deviations above average)
- OR Volatility > 90th percentile (unusually high fluctuations)

**What It Means:**
- 🚨 Stress = Abnormal TGA behavior, potential market volatility ahead
- ✅ Normal = TGA within expected ranges

### 📊 Moving Averages
- **7-day MA:** Short-term trend (weekly direction)
- **30-day MA:** Medium-term trend (monthly direction)
- **Crossovers:** Signal trend changes (e.g., 7d crosses above 30d = rising trend)

---

## Sample Output Screenshots

### Terminal Output
```
======================================================================
📊 TGA LIQUIDITY TRACKING DEMO
======================================================================

🔄 Fetching TGA data from US Treasury (last 24 months)...
✅ Successfully fetched 520 records
📅 Date range: 2023-11-11 to 2025-11-11

🔢 Calculating liquidity metrics...
✅ Metrics calculated

🎨 Creating interactive dashboard...
🌐 Opening interactive dashboard in browser...

✅ Demo complete!
```

---

## Troubleshooting

### ❌ "ModuleNotFoundError: No module named 'plotly'"
**Fix:**
```bash
pip install plotly pandas requests
```

### ❌ "403 Forbidden" (Real data demo)
**Issue:** Treasury API blocking request
**Fix:** Use sample data version instead:
```bash
python demos/tga_liquidity_demo_with_sample_data.py
```

### ❌ "Dashboard doesn't open in browser"
**Issue:** Browser not launching automatically
**Fix:** Check terminal output for HTML file path, open manually:
```bash
# Look for: "Saved to: temp-plot.html"
# Then open file in browser
```

### ❌ "SSL Certificate Error"
**Fix:**
```bash
pip install --upgrade certifi
```

---

## Next Steps

### After running the demo:

1. **📖 Read the full analysis**
   ```bash
   cat docs/TGA_LIQUIDITY_ANALYSIS.md
   ```

2. **🧪 See production implementation**
   - `etl/src/collectors/tga_collector.py` - Async collector
   - `etl/src/transformers/tga_liquidity_transformer.py` - Advanced metrics
   - `database/migrations/002_tga_liquidity_tracking.sql` - Database schema

3. **🔬 Run production tests**
   ```bash
   python etl/scripts/test_tga_liquidity.py
   ```

4. **🏗️ Integrate into your platform**
   - Add to ETL orchestrator
   - Create API endpoints
   - Build React dashboard
   - Set up alerts

---

## FAQ

**Q: Is this real-time data?**
A: No, Treasury publishes TGA data daily (typically 4 PM ET, next business day)

**Q: Can I use this for trading decisions?**
A: This is educational/research. Always do your own analysis and consult professionals.

**Q: How accurate is the sample data demo?**
A: Sample data uses realistic patterns (trends, spikes, volatility) but is synthetic. Use real data demo for actual analysis.

**Q: What's the difference from my original code?**
A: Your original code concept is preserved (cumulative -ΔTGA), but enhanced with:
- ✅ Interactive visualizations (vs static matplotlib)
- ✅ Statistical measures (z-scores, volatility)
- ✅ Stress detection (automated alerts)
- ✅ Better error handling
- ✅ Production-ready architecture (async, retry logic, database)

**Q: Why two demo versions?**
A: Sample data version works immediately without internet/API issues. Real data version for actual analysis when needed.

---

## Technical Details

**Dependencies:**
- `plotly>=5.0.0` - Interactive charts
- `pandas>=1.3.0` - Data manipulation
- `requests>=2.25.0` - HTTP requests (real data version)
- `numpy>=1.20.0` - Sample data generation

**Data Source (Real Demo):**
- US Treasury Fiscal Data API
- Endpoint: https://fiscaldata.treasury.gov
- Dataset: Daily Treasury Statement - Operating Cash Balance
- Frequency: Daily (business days)
- No API key required

**Performance:**
- Fetch time: ~2-5 seconds
- Processing: <1 second
- Chart rendering: ~1-2 seconds
- Total runtime: ~5-10 seconds

---

## Support

**Found an issue?**
- Check `demos/README.md` for detailed documentation
- Review `docs/TGA_LIQUIDITY_ANALYSIS.md` for methodology
- Test with sample data version first to isolate API issues

**Want to learn more?**
- Read the 900-line analysis: `docs/TGA_LIQUIDITY_ANALYSIS.md`
- Explore production code: `etl/src/collectors/` and `etl/src/transformers/`
- Check database schema: `database/migrations/002_tga_liquidity_tracking.sql`

---

**Built for InvestByYourself Platform** | Demo Version v1.0
