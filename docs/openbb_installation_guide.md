# OpenBB Terminal Installation & Setup Guide

*Created: 2025-08-19*

## 🎯 **What is OpenBB Terminal?**

OpenBB Terminal is a **completely free** open-source investment research platform that provides:
- **Stock analysis and screening**
- **Technical indicators and charting**
- **Portfolio management**
- **Economic data integration**
- **News and sentiment analysis**
- **Custom Python scripting capabilities**

## 🚀 **Installation Options**

### **Option 1: OpenBB Terminal (Recommended)**
```bash
# Install the full terminal application
pip install openbb

# Launch the terminal
openbb
```

### **Option 2: OpenBB SDK (Python Library)**
```bash
# Install the Python SDK for programmatic access
pip install openbb-sdk

# Use in Python scripts
from openbb import obb
```

### **Option 3: Docker Installation**
```bash
# Pull and run OpenBB Terminal in Docker
docker pull ghcr.io/openbb-finance/openbbterminal:latest
docker run -it ghcr.io/openbb-finance/openbbterminal:latest
```

## 🔧 **System Requirements**

### **Minimum Requirements:**
- **Python**: 3.8 or higher
- **RAM**: 4GB minimum, 8GB recommended
- **Storage**: 2GB free space
- **OS**: Windows 10+, macOS 10.14+, or Linux

### **Recommended Requirements:**
- **Python**: 3.9 or higher
- **RAM**: 8GB or more
- **Storage**: 5GB free space
- **OS**: Latest stable version

## 📦 **Installation Steps**

### **Step 1: Prepare Python Environment**
```bash
# Create virtual environment (recommended)
python -m venv openbb_env

# Activate virtual environment
# Windows:
openbb_env\Scripts\activate
# macOS/Linux:
source openbb_env/bin/activate
```

### **Step 2: Install OpenBB Terminal**
```bash
# Install the terminal
pip install openbb

# Verify installation
openbb --version
```

### **Step 3: First Launch**
```bash
# Launch OpenBB Terminal
openbb

# The terminal will guide you through initial setup
# You may need to configure data sources and API keys
```

## 🔑 **API Key Configuration**

### **Required API Keys:**
OpenBB Terminal integrates with multiple data sources. You'll need to configure:

1. **Yahoo Finance**: Usually works without API key
2. **Alpha Vantage**: Your existing API key
3. **FRED**: Your existing API key
4. **Other sources**: Optional, based on your needs

### **Configuration File:**
```bash
# OpenBB creates a config file at:
# Windows: %USERPROFILE%\.openbb\config.ini
# macOS/Linux: ~/.openbb/config.ini

# You can edit this file to add API keys
```

## 📊 **Available Data Sources**

### **Free Data Sources:**
- **Yahoo Finance**: Stock data, company info
- **FRED**: Economic indicators
- **Alpha Vantage**: Technical indicators
- **Finnhub**: Basic market data

### **Paid Data Sources (Optional):**
- **Polygon.io**: High-quality market data
- **IEX Cloud**: Financial data
- **Quandl**: Alternative data

## 🎮 **Basic Usage**

### **Launching the Terminal:**
```bash
openbb
```

### **Basic Commands:**
```bash
# Stock analysis
stocks/load AAPL
stocks/ta/rsi
stocks/ta/macd

# Portfolio management
portfolio/load
portfolio/alloc
portfolio/risk

# Economic data
economy/overview
economy/fred
economy/treasury

# Technical analysis
ta/rsi
ta/macd
ta/bbands
```

### **Help and Documentation:**
```bash
# Get help on any command
help

# List available commands
?

# Get help on specific command
help stocks/load
```

## 🔍 **Testing Data Sources**

### **Test Yahoo Finance:**
```bash
stocks/load AAPL
stocks/quote AAPL
stocks/overview AAPL
```

### **Test FRED Integration:**
```bash
economy/fred
economy/fred/CPIAUCSL
```

### **Test Alpha Vantage:**
```bash
stocks/ta/rsi AAPL
stocks/ta/macd AAPL
```

## 📈 **Key Features to Explore**

### **1. Stock Analysis:**
- **Fundamental Analysis**: Financial statements, ratios
- **Technical Analysis**: Charts, indicators, patterns
- **Screening**: Find stocks based on criteria
- **Comparison**: Compare multiple stocks

### **2. Portfolio Management:**
- **Portfolio Loading**: Import your holdings
- **Performance Analysis**: Returns, risk metrics
- **Optimization**: Portfolio allocation suggestions
- **Risk Assessment**: VaR, Sharpe ratio, etc.

### **3. Economic Data:**
- **Macro Indicators**: GDP, inflation, employment
- **Interest Rates**: Treasury yields, Fed funds
- **Market Data**: VIX, sentiment indicators
- **Geopolitical**: News, sentiment analysis

### **4. Custom Analysis:**
- **Python Scripting**: Write custom analysis
- **Data Export**: Export data for external analysis
- **Chart Customization**: Modify charts and layouts
- **API Integration**: Connect with other tools

## 🚨 **Common Issues & Solutions**

### **Installation Issues:**
```bash
# If pip install fails, try:
pip install --upgrade pip
pip install openbb --no-cache-dir

# If you get permission errors:
pip install openbb --user
```

### **API Key Issues:**
```bash
# Check your config file
# Ensure API keys are correctly formatted
# Verify API key limits and permissions
```

### **Performance Issues:**
```bash
# Close other applications to free up RAM
# Check your internet connection
# Verify data source availability
```

## 💡 **Integration with Your Project**

### **Data Source Strategy:**
1. **Use OpenBB** for advanced analysis and technical indicators
2. **Keep your custom scripts** for specific analysis needs
3. **Integrate multiple sources** through OpenBB's unified interface
4. **Export data** from OpenBB to your custom analysis tools

### **Workflow Integration:**
```bash
# 1. Use OpenBB for initial analysis and screening
# 2. Export interesting data to your custom scripts
# 3. Perform detailed analysis with your tools
# 4. Generate custom visualizations and reports
```

## 🎯 **Next Steps After Installation**

### **Week 1: Basic Familiarity**
- [ ] Install and launch OpenBB Terminal
- [ ] Explore basic commands and features
- [ ] Test data source connectivity
- [ ] Configure API keys

### **Week 2: Feature Exploration**
- [ ] Test stock analysis capabilities
- [ ] Explore portfolio management features
- [ ] Test economic data integration
- [ ] Practice technical analysis tools

### **Week 3: Integration Planning**
- [ ] Identify complementary features
- [ ] Plan data export strategies
- [ ] Test custom scripting capabilities
- [ ] Evaluate workflow integration

---

*OpenBB Terminal provides a powerful, free platform for financial analysis that can significantly enhance your existing toolkit while maintaining the flexibility of your custom Python scripts.*
