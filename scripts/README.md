# Scripts Directory Organization

This directory contains all executable scripts organized by functionality for better maintainability and discovery.

## 📁 Directory Structure

### **`etl_tests/`** - ETL Pipeline Testing Scripts
Scripts for testing and validating the ETL (Extract, Transform, Load) pipeline components.

- **`test_data_collection_framework.py`** - Tests the data collection framework (Phase 1)
- **`test_data_processing_engine.py`** - Tests the data processing engine (Phase 2)
- **`test_aapl_example.py`** - AAPL-specific testing example
- **`test_multiple_companies.py`** - Multi-company analysis and chart generation
- **`test_debt_equity_fix.py`** - Specific fix validation for debt/equity ratios

### **`testing/`** - Security & Functionality Validation Scripts
Comprehensive testing scripts created after security fixes to validate ETL pipeline functionality.

- **`test_env_loading.py`** - Environment variable loading validation
- **`test_config_classes.py`** - Configuration class functionality testing
- **`test_etl_core.py`** - Core ETL component testing
- **`test_etl_functionality.py`** - Comprehensive ETL functionality testing
- **`test_etl_workflow.py`** - End-to-end ETL workflow validation
- **`test.env`** - Test environment configuration file

### **`financial_analysis/`** - Financial Analysis & Strategy Scripts
Scripts for financial data analysis, chart generation, and investment strategy testing.

- **`company_financial_analysis.py`** - Company financial data analysis
- **`inflation_analysis.py`** - Inflation data analysis and visualization
- **`inflation_yoy_analysis.py`** - Year-over-year inflation analysis
- **`create_financial_charts.py`** - Financial chart generation utilities
- **`test_hedging_by_stocks_backtesting.py`** - Hedge strategy backtesting framework

### **`api_tests/`** - API Integration Testing Scripts
Scripts for testing external API integrations and data sources.

- **`test_alpha_vantage.py`** - Alpha Vantage API testing
- **`test_fmp_api.py`** - Financial Modeling Prep API testing

### **`utilities/`** - Utility & CI/CD Scripts
General utility scripts and CI/CD related tools.

- **`run_local_financial_ci.py`** - Local financial CI/CD pipeline execution
- **`company_profile_collector.py`** - Company profile data collection utility

### **`examples/`** - Example Scripts
Example implementations and demonstrations.

### **`cli/`** - Command Line Interface Scripts
Command-line tools and utilities.

## 🚀 Usage

### Running ETL Tests
```bash
# Test data collection framework
python scripts/etl_tests/test_data_collection_framework.py

# Test data processing engine
python scripts/etl_tests/test_data_processing_engine.py

# Test multi-company analysis
python scripts/etl_tests/test_multiple_companies.py
```

### Running Security & Functionality Tests
```bash
# Test environment variable loading
python scripts/testing/test_env_loading.py

# Test configuration classes
python scripts/testing/test_config_classes.py

# Test core ETL components
python scripts/testing/test_etl_core.py

# Test complete ETL workflow
python scripts/testing/test_etl_workflow.py
```

### Running Financial Analysis
```bash
# Company financial analysis
python scripts/financial_analysis/company_financial_analysis.py

# Inflation analysis
python scripts/financial_analysis/inflation_analysis.py

# Hedge strategy backtesting
python scripts/financial_analysis/test_hedging_by_stocks_backtesting.py
```

### Running API Tests
```bash
# Test Alpha Vantage API
python scripts/api_tests/test_alpha_vantage.py

# Test FMP API
python scripts/api_tests/test_fmp_api.py
```

### Running Utilities
```bash
# Local CI/CD execution
python scripts/utilities/run_local_financial_ci.py

# Company profile collection
python scripts/utilities/company_profile_collector.py
```

## 📊 Script Dependencies

### **Phase 1 Dependencies** (Data Collection)
- `test_data_collection_framework.py` - Requires FRED API key
- `company_profile_collector.py` - Requires Alpha Vantage API key

### **Phase 2 Dependencies** (Data Processing)
- `test_data_processing_engine.py` - Requires Phase 1 completion
- `test_aapl_example.py` - Requires Phase 2 completion
- `test_multiple_companies.py` - Requires Phase 2 completion

### **External Dependencies**
- `test_hedging_by_stocks_backtesting.py` - Requires matplotlib, pandas, numpy
- `create_financial_charts.py` - Requires matplotlib, pandas
- `inflation_analysis.py` - Requires FRED API key

## 🔧 Development Notes

- **ETL Tests**: Run these first to validate pipeline functionality
- **Financial Analysis**: Run after ETL pipeline is working
- **API Tests**: Use for debugging external API integrations
- **Utilities**: General-purpose tools for development and CI/CD

## 📈 Progress Tracking

- **Phase 1**: ✅ Data Collection Framework (100% Complete)
- **Phase 2**: ✅ Data Processing Engine (100% Complete)
- **Phase 3**: 🚧 Data Loading & Storage (In Progress)

---

*Last Updated: August 2025*
*Maintained By: investByYourself Development Team*
