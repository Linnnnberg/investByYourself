# Invest By Yourself 🚀

*A self-directed investment platform with professional-grade market data and analysis tools.*

## 🎯 **Project Vision**

**Invest By Yourself** empowers individual investors to take control of their financial future with professional-grade tools and data.

### **📚 Planning & Documentation**
- **[📚 Documentation Hub](docs/README.md)** - Complete documentation navigation and overview
- **[📋 Master Todo List](MASTER_TODO.md)** - Complete project roadmap with phases, priorities, and progress tracking (43% Complete)
- **[📈 Development Plan](docs/investbyyourself_plan.md)** - Main project roadmap, architecture decisions, and implementation phases
- **[🔍 Company Analysis Enhancement Summary](docs/company_analysis_enhancement_summary.md)** - Enhanced company analysis capabilities and implementation details
- **[🏗️ ETL & Database Architecture](docs/etl_architecture_plan.md)** - Comprehensive ETL pipeline design and database schema

## 🏗️ **System Architecture**

- **Data Sources**: Yahoo Finance, Alpha Vantage, FRED, API Ninjas
- **Database**: PostgreSQL with optimization and caching
- **ETL Pipeline**: Automated data collection and processing
- **Analysis Tools**: Company research, technical analysis, portfolio management

## 🚀 **Getting Started**

```bash
git clone https://github.com/Linnnnberg/investByYourself.git
cd investByYourself
pip install -r requirements.txt
python run_ui.py
```

### **📦 Dependencies**

Key packages: `pandas`, `numpy`, `streamlit`, `plotly`, `yfinance`, `fredapi`

See `requirements.txt` for complete list.

### **Configuration**
1. Set up your API keys in environment variables
2. Configure data source preferences
3. Set up your initial watchlist

### **🚨 Troubleshooting**

#### **Common Installation Issues**
```bash
# Matplotlib backend issues (Linux/macOS)
export MPLBACKEND=Agg

# Streamlit installation problems
pip install --upgrade pip setuptools wheel
pip install streamlit

# Chart generation issues
pip uninstall matplotlib && pip install matplotlib
python scripts/generate_sample_charts.py
```

#### **System Requirements**
- **Python**: 3.8+ (3.9+ recommended)
- **RAM**: 4GB minimum, 8GB recommended
- **Storage**: 2GB free space minimum
- **Browser**: Chrome 90+, Firefox 88+, Safari 14+, Edge 90+

## 📊 **Current Features**

### **✅ Implemented**
- Company profile collection and analysis
- Inflation and economic indicator analysis
- Financial chart generation
- Multi-source data validation framework
- CI/CD pipeline with financial-specific rules
- Comprehensive testing infrastructure
- **🎨 Complete UI Platform**: Portfolio dashboard, financial calculator, chart viewer
- **📊 Professional Charts**: 6 types of financial charts with high-resolution output
- **🚀 Interactive Components**: Streamlit-based professional financial tools

### **📁 Project Structure**
```
investByYourself/
├── src/                                        # Core application code
├── tests/                                      # Test suite
├── docs/                                       # Documentation
├── database/                                   # Database schema
├── docker/                                     # Container configuration
└── charts/                                     # Generated visualizations
```

## 🎯 **Current Status**

**Progress**: 43% Complete - See [Master Todo](MASTER_TODO.md) for detailed roadmap.

**Current Phase**: Phase 2 - Core Data & Company Analysis (70% Complete)
**Next Milestone**: ETL Architecture & Database Design (Weeks 5-6)

## 🤝 **Contributing**

This is a personal project. See [Master Todo](MASTER_TODO.md) for current development status and roadmap.

## 📄 **License**

Personal use and educational purposes.

---

**Built for self-directed investors.**
