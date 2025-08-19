# Project Organization & Structure

*Last Updated: 2025-08-19*

## 🎯 **Project Overview**

This Financial & Macro Economic Analysis Toolkit is organized for clarity, maintainability, and scalability. The project follows a logical structure that separates different types of analysis, data, and documentation.

## 📁 **Directory Structure**

```
NewProject/
├── README.md                           # Main project documentation
├── requirements.txt                    # Python dependencies
├── .gitignore                         # Git ignore rules (includes .env)
├── .env                               # API keys (not in git - create manually)
├── charts/                            # Generated visualizations
│   ├── financial_comparison_charts.png
│   ├── comprehensive_financial_analysis.png
│   ├── inflation_analysis_charts.png
│   └── yoy_inflation_analysis.png
├── data/                              # Raw data and JSON outputs
│   └── company_profiles_20250819_213912.json
├── scripts/                           # Python analysis scripts
│   ├── company_financial_analysis.py
│   ├── inflation_analysis.py
│   ├── inflation_yoy_analysis.py
│   ├── company_profile_collector.py
│   ├── create_financial_charts.py
│   └── test_alpha_vantage.py
└── docs/                              # Documentation and reports
    ├── project_organization.md        # This file
    ├── macro_data_todo.md            # Economic data roadmap
    ├── company_fundamentals_todo.md  # Company profile & fundamentals roadmap
    ├── company_profiles_report.md    # Comprehensive company analysis report
    └── inflation_analysis_report.md  # Inflation indicators analysis report
```

## 🔧 **Scripts Organization**

### **Company Analysis Scripts**
- **`company_financial_analysis.py`**: Main financial analysis for company comparisons (AAPL vs MSFT)
- **`company_profile_collector.py`**: Company profile and fundamental data collection using Yahoo Finance

### **Economic Analysis Scripts**
- **`inflation_analysis.py`**: Comprehensive inflation analysis (CPI, Core CPI, PPI)
- **`inflation_yoy_analysis.py`**: Focused Year-over-Year inflation changes analysis
- **`create_financial_charts.py`**: Standalone chart generation for financial metrics

### **API Testing Scripts**
- **`test_alpha_vantage.py`**: Alpha Vantage API testing and exploration

## 📊 **Charts Organization**

### **Financial Charts**
- **`financial_comparison_charts.png`**: Company profitability and efficiency comparisons
- **`comprehensive_financial_analysis.png`**: Multi-panel financial dashboard

### **Inflation Charts**
- **`inflation_analysis_charts.png`**: Comprehensive inflation indicators analysis
- **`yoy_inflation_analysis.png`**: Year-over-Year inflation changes (CPI, Core CPI, PPI)

## 📋 **Documentation Organization**

### **Project Documentation**
- **`README.md`**: Main project overview, setup, and usage instructions
- **`project_organization.md`**: This file - detailed project structure explanation

### **Roadmaps & Planning**
- **`macro_data_todo.md`**: Economic data collection and analysis roadmap
- **`company_fundamentals_todo.md`**: Company profile and fundamentals expansion roadmap

### **Analysis Reports**
- **`company_profiles_report.md`**: Detailed company analysis for 5 major companies
- **`inflation_analysis_report.md`**: Inflation indicators analysis and insights

## 🗂️ **Data Organization**

### **Raw Data**
- **`data/`**: Contains JSON outputs and raw data files
- **`.env`**: Environment variables and API keys (not in git)

### **Generated Outputs**
- **`charts/`**: All visualization outputs
- **`docs/`**: All documentation and reports

## 🚀 **Development Workflow**

### **1. Script Development**
- Scripts are organized by analysis type
- Each script has a clear, descriptive name
- Consistent coding standards and documentation

### **2. Data Collection**
- FRED API for economic data
- Yahoo Finance for company data
- Fallback to sample data when APIs unavailable

### **3. Visualization Generation**
- Professional charts using matplotlib and seaborn
- Consistent styling and formatting
- High-resolution outputs for reports

### **4. Documentation Updates**
- README updated with each major change
- Reports generated for significant analyses
- Roadmaps track development progress

## 🔍 **Naming Conventions**

### **Scripts**
- **`company_*`**: Company-related analysis
- **`inflation_*`**: Inflation-related analysis
- **`*_analysis.py`**: Main analysis scripts
- **`*_collector.py`**: Data collection scripts

### **Charts**
- **`*_charts.png`**: Multi-panel visualizations
- **`*_analysis.png`**: Single comprehensive charts
- **`yoy_*`**: Year-over-Year specific analysis

### **Documentation**
- **`*_todo.md`**: Planning and roadmap documents
- **`*_report.md`**: Analysis results and insights
- **`project_*`**: Project structure and organization

## 📈 **Scalability Features**

### **Modular Design**
- Each script focuses on a specific analysis type
- Easy to add new analysis categories
- Consistent interface patterns

### **Data Management**
- Centralized data directory
- API key management via environment variables
- Fallback data generation for testing

### **Documentation Structure**
- Hierarchical documentation organization
- Clear separation of concerns
- Easy to find specific information

## 🎯 **Best Practices**

### **File Organization**
- Keep root directory clean
- Group related files in appropriate directories
- Use descriptive, consistent naming

### **Script Development**
- Single responsibility principle
- Clear function and variable names
- Comprehensive error handling

### **Documentation**
- Update README with each major change
- Generate reports for significant analyses
- Maintain clear roadmaps for future development

---

*This organization structure ensures the project remains maintainable, scalable, and easy to navigate as it grows.*
