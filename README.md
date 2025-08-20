# Invest By Yourself 🚀

*A comprehensive self-directed investment platform that empowers individual investors with professional-grade market data, analysis tools, and portfolio management capabilities.*

## 🎯 **Project Vision**

**Invest By Yourself** is designed for individual investors who want to take control of their financial future. Instead of relying on financial advisors or robo-advisors, you get the tools, data, and insights to make informed investment decisions yourself.

### **Core Philosophy:**
- **Self-Directed**: You make the decisions, we provide the tools
- **Data-Driven**: Professional-grade market data and analysis
- **Educational**: Learn while you invest
- **Independent**: No hidden fees or conflicts of interest

### **📚 Planning & Documentation**
- **[📋 Master Todo List](MASTER_TODO.md)** - Complete project roadmap with phases, priorities, and progress tracking
- **[📊 Technical Implementation Plan](docs/comprehensive_market_data_plan.md)** - 8-week MVP roadmap with database schemas, data models, and frontend requirements
- **[🚀 Strategic Vision Document](docs/invest_by_yourself_vision.md)** - Complete project vision, user personas, and long-term roadmap
- **[📈 Data Architecture Plan](docs/price_data_model_plan.md)** - Detailed data models and system architecture

## 🏗️ **System Architecture**

### **Market Data Foundation**
- **Multi-Source Data**: Yahoo Finance, Alpha Vantage, FRED, OpenBB
- **Data Quality Assurance**: Cross-source validation and discrepancy alerts
- **Real-Time Updates**: Live market data and historical analysis
- **Economic Context**: Macro indicators and market sentiment

### **Investment Analysis Tools**
- **Company Research**: Fundamentals, financial ratios, and performance metrics
- **Technical Analysis**: Price charts, patterns, and technical indicators
- **Risk Assessment**: Portfolio risk metrics and stress testing
- **Market Screening**: Find investment opportunities based on your criteria

### **Portfolio Management**
- **Watchlists**: Track interesting stocks and ETFs
- **Portfolio Tracking**: Monitor your actual investments
- **Performance Analysis**: Risk-adjusted returns and attribution
- **Rebalancing Tools**: Asset allocation management

## 🚀 **Getting Started**

### **Prerequisites**
- Python 3.8+
- Required packages (see `requirements.txt`)
- API keys for data sources (Yahoo Finance, Alpha Vantage, FRED)

### **Installation**
```bash
git clone https://github.com/Linnnnberg/investByYourself.git
cd investByYourself

# Complete installation (recommended)
pip install -r requirements.txt

# Or core dependencies only
pip install pandas numpy matplotlib seaborn streamlit plotly pillow
```

### **Running the Application**
```bash
# Main app
python run_ui.py

# Or specific components
python run_ui.py portfolio      # Portfolio dashboard
python run_ui.py calculator     # Financial calculator
python run_ui.py charts         # Chart viewer
```

### **📦 Dependencies**

#### **Core Dependencies (Required)**
```bash
# Financial & Data Analysis
pandas>=1.5.0          # Data manipulation and analysis
numpy>=1.21.0          # Numerical computing foundation
matplotlib>=3.6.0      # Professional chart generation
seaborn>=0.12.0        # Statistical data visualization
yfinance>=0.2.55       # Yahoo Finance data integration
fredapi>=0.5.0         # Federal Reserve Economic Data
financetoolkit>=1.0.0  # Financial analysis toolkit

# UI Framework
streamlit>=1.28.0      # Web application framework
plotly>=5.17.0         # Interactive charts
pillow>=10.0.0         # Image processing

# HTTP & API
requests>=2.31.0       # HTTP library for API calls
httpx>=0.24.0          # Modern HTTP client with async support
python-dotenv>=1.0.0   # Environment variable management
```

#### **Development Dependencies (Optional)**
```bash
# Testing & Quality
pytest>=7.4.0          # Testing framework
black>=23.7.0          # Code formatter
flake8>=6.0.0          # Code linter
mypy>=1.5.0            # Static type checker
pre-commit>=3.3.0      # Pre-commit hooks
```

#### **Installation Options**
```bash
# Complete installation (recommended)
pip install -r requirements.txt

# Core platform only
pip install pandas numpy matplotlib seaborn streamlit plotly pillow yfinance fredapi

# Development setup
pip install pytest black flake8 mypy pre-commit
```

#### **Verify Installation**
```bash
# Test core functionality
python -c "import pandas, numpy, streamlit, plotly; print('✅ Core dependencies OK')"

# Test financial tools
python -c "import matplotlib, seaborn; print('✅ Chart generation OK')"

# Test UI components
python run_ui.py --help
```

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

### **📁 Project Structure & Documentation**
```
investByYourself/
├── README.md                                    # Main project overview
├── MASTER_TODO.md                               # 📋 Complete project roadmap
├── requirements.txt                             # Python dependencies
├── src/                                         # 🏗️ Main source code package
│   ├── core/                                   # Core financial modules
│   ├── data_sources/                           # Data source integrations
│   ├── analysis/                               # Analysis modules
│   ├── ui/                                     # 🎨 User interface components
│   │   ├── main_app.py                         # Main launcher & navigation
│   │   ├── portfolio_dashboard.py              # Portfolio management
│   │   ├── financial_calculator.py             # Financial tools
│   │   ├── chart_viewer.py                     # Chart display
│   │   └── README.md                           # UI documentation
│   └── utils/                                  # Utility functions
├── tests/                                       # 🧪 Test suite
│   ├── unit/                                   # Unit tests
│   ├── integration/                            # Integration tests
│   └── fixtures/                               # Test fixtures
├── scripts/                                     # Python analysis scripts
│   ├── generate_sample_charts.py                # Chart generation system
│   └── run_local_financial_ci.py               # Local CI pipeline runner
├── run_ui.py                                    # 🚀 UI launcher script
├── config/                                      # Configuration files
├── tools/                                       # Development tools
├── docker/                                      # Docker configuration
├── docs/                                        # 📚 Comprehensive documentation
│   ├── comprehensive_market_data_plan.md        # 🎯 MVP implementation roadmap
│   ├── invest_by_yourself_vision.md            # 🚀 Strategic vision & features
│   ├── price_data_model_plan.md                # 📈 Data architecture design
│   ├── company_profiles_report.md              # 📊 Company analysis examples
│   ├── inflation_analysis_report.md            # 🌍 Economic data analysis
│   ├── openbb_installation_guide.md            # 🛠️ Tool setup guides
│   └── project_organization.md                 # 📋 Project structure overview
├── charts/                                      # Generated visualizations
└── data/                                        # Raw data and JSON outputs
```

### **🔄 In Development**
- Real-time price data collection
- Security metrics calculation
- Data quality monitoring system
- Portfolio analysis tools
- Earnings data and transcript integration (API Ninjas vs Finnhub)

### **📋 Planned**
- Interactive dashboard
- Advanced screening tools
- Portfolio optimization
- Risk management alerts

## 🎯 **MVP Goals (Next 8 Weeks)**

**Target**: Working investment platform where you can:
- Collect and validate market data from multiple sources
- Research companies and analyze fundamentals
- Track your watchlist and portfolio
- Get alerts for data discrepancies and opportunities
- Use a clean, intuitive interface for all features

### **📋 Detailed Implementation Plans**
- **[📋 Master Todo List](MASTER_TODO.md)** - Complete project roadmap with phases, priorities, and progress tracking
- **[📊 Comprehensive Market Data System Plan](docs/comprehensive_market_data_plan.md)** - Complete technical implementation roadmap with MVP priorities
- **[🚀 Project Vision & Roadmap](docs/invest_by_yourself_vision.md)** - Strategic vision, user personas, and feature breakdown
- **[📈 Price Data Model Plan](docs/price_data_model_plan.md)** - Original detailed plan for price data architecture

## 🤝 **Contributing**

This is a personal project focused on building a professional-grade investment platform. Contributions and feedback are welcome!

### **💡 Why Review the Planning Documents?**

If you're interested in contributing or understanding the project better:

1. **[📋 Master Todo List](MASTER_TODO.md)** - See the complete project roadmap and current sprint
2. **[📊 Technical Implementation Plan](docs/comprehensive_market_data_plan.md)** - See exactly what's being built and when
3. **[🚀 Strategic Vision](docs/invest_by_yourself_vision.md)** - Understand the long-term goals and user experience
4. **[📈 Data Architecture](docs/price_data_model_plan.md)** - Learn about the database design and data flow
5. **[📋 Project Organization](docs/project_organization.md)** - Get familiar with the current codebase structure

### **🎯 Current Development Focus**
- **Phase 1 (Weeks 1-2)**: ✅ CI/CD Foundation & Core Infrastructure
- **Phase 2 (Weeks 3-4)**: Financial Data Validation & Testing Framework
- **Phase 3 (Weeks 5-6)**: Advanced CI/CD Features & API Integration
- **Phase 4 (Weeks 7-8)**: Production-Ready Features & Core Platform

*All phases include comprehensive testing, documentation, and quality assurance.*

## 📄 **License**

Personal use and educational purposes.

## 🙏 **Open Source Acknowledgments**

**Invest By Yourself** is built on the shoulders of amazing open-source projects. We're grateful to the developers and communities that make these tools available.

*Note: This project uses specific versions of these libraries as defined in `requirements.txt`. All licenses and acknowledgments apply to the versions specified there.*

### **Core Python Libraries**
- **[Pandas](https://pandas.pydata.org/)** - Data manipulation and analysis (BSD 3-Clause License)
- **[NumPy](https://numpy.org/)** - Numerical computing foundation (BSD 3-Clause License)
- **[Matplotlib](https://matplotlib.org/)** - Professional plotting and visualization (PSF License)
- **[Seaborn](https://seaborn.pydata.org/)** - Statistical data visualization (BSD 3-Clause License)
- **[yfinance](https://github.com/ranaroussi/yfinance)** - Yahoo Finance data access (Apache 2.0 License)
- **[fredapi](https://github.com/mortada/fredapi)** - Federal Reserve Economic Data API (MIT License)
- **[requests](https://requests.readthedocs.io/)** - HTTP library for API calls (Apache 2.0 License)
- **[python-dotenv](https://github.com/theskumar/python-dotenv)** - Environment variable management (BSD 3-Clause License)

### **Data Analysis & Financial Tools**
- **[FinanceToolkit](https://github.com/JerBouma/FinanceToolkit)** - Financial analysis toolkit (MIT License)
- **[OpenBB Terminal](https://github.com/OpenBB-finance/OpenBBTerminal)** - Investment research platform (MIT License)
- **[Alpha Vantage](https://www.alphavantage.co/)** - Financial data APIs (Commercial API with free tier)

### **Development & Infrastructure**
- **[Python](https://www.python.org/)** - Programming language (PSF License)
- **[Git](https://git-scm.com/)** - Version control (GPL v2)
- **[GitHub](https://github.com/)** - Code hosting and collaboration (GitHub Terms of Service)

### **License Compatibility**
All open-source libraries used in this project are compatible with our personal use and educational purposes license. We respect and comply with all original licenses.

### **Academic & Professional Citation**
If you use this project in academic research, professional work, or publications, please cite the open-source libraries appropriately:

```bibtex
@software{pandas,
  title={pandas: powerful Python data analysis toolkit},
  author={McKinney, Wes},
  year={2010},
  url={https://pandas.pydata.org/}
}

@software{matplotlib,
  title={Matplotlib: A 2D graphics environment},
  author={Hunter, John D},
  year={2007},
  url={https://matplotlib.org/}
}

@software{yfinance,
  title={yfinance: Yahoo Finance market data downloader},
  author={Ran Aroussi},
  year={2020},
  url={https://github.com/ranaroussi/yfinance}
}
```

### **Contributing to Open Source**
Consider supporting these amazing projects by:
- Starring their repositories on GitHub
- Contributing code or documentation
- Reporting bugs or requesting features
- Supporting their development financially if possible

---

**Built with ❤️ for self-directed investors who believe in taking control of their financial future.**
