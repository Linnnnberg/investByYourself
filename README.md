# InvestByYourself Financial Platform

A comprehensive self-directed investment platform that empowers individual investors with professional-grade tools, data, and insights.

## 🚀 **Quick Start for Team Members**

### **1. Environment Setup**
```bash
# Run the interactive setup script
cd scripts
python setup_team_environment.py
```

This will:
- Create your secure `.env` file
- Configure database connection
- Validate your setup
- Guide you through next steps

### **2. Test the System**
```bash
# Check and populate database
python scripts/check_and_populate_database.py

# Test financial exploration system
python scripts/financial_analysis/data_explorer.py

# Launch interactive dashboard
streamlit run scripts/financial_analysis/financial_dashboard.py
```

### **3. Full Documentation**
- **Team Setup Guide**: [docs/TEAM_ENVIRONMENT_SETUP.md](docs/TEAM_ENVIRONMENT_SETUP.md)
- **Database Reference**: [docs/database_quick_reference.md](docs/database_quick_reference.md)
- **Project Status**: [MASTER_TODO.md](MASTER_TODO.md) *(Single Source of Truth)*

---

## 📊 **Current Status**

> **📋 For the most up-to-date project status, see [MASTER_TODO.md](MASTER_TODO.md) - Single Source of Truth**

- **Overall Progress**: 75%+ Complete (25+/31 tasks)
- **Phase 3**: ✅ **100% Complete** (Database & ETL Infrastructure)
- **Phase 4**: 🔄 **In Progress** (Microservices Architecture Implementation)
- **Current Focus**: Tech-014 Yahoo Finance CAGR Fix ✅ **COMPLETED** + Next: Story-005 Enhanced Company Analysis

### **Recent Achievements**
- ✅ **Complete Database Infrastructure** with 13 tables
- ✅ **ETL Pipeline** with data collectors and processors
- ✅ **Financial Data Exploration System** with interactive dashboard
- ✅ **Sample Data Population** for testing and development
- ✅ **Story-015 Complete** - Investment Strategy Module (100%)
- ✅ **21 API Endpoints** implemented for strategy management and backtesting
- ✅ **Production-ready microservice** with FastAPI, SQLAlchemy, and JWT auth
- ✅ **Tech-014 Complete** - Yahoo Finance CAGR data fix for momentum strategies

---

## 🏗️ **System Architecture**

### **Data Infrastructure**
- **PostgreSQL**: Primary database with optimized financial schema
- **Redis**: High-performance caching layer
- **MinIO**: S3-compatible object storage for data lake
- **ETL Pipeline**: Automated data collection, transformation, and loading

### **Core Components**
- **Data Collectors**: Multi-source financial data collection
- **Data Processors**: Transformation, validation, and enrichment
- **Data Loaders**: Efficient storage and retrieval systems
- **Analysis Tools**: Company research, screening, and portfolio management
- **Financial Analysis Service**: Investment strategy management and backtesting
- **Microservices Architecture**: Scalable, maintainable service structure

---

## 🔧 **Technology Stack**

- **Backend**: Python 3.13, FastAPI, SQLAlchemy
- **Database**: PostgreSQL 17, Redis, MinIO
- **Data Processing**: Pandas, NumPy, Pydantic
- **Visualization**: Plotly, Streamlit
- **Testing**: Pytest, Pre-commit hooks
- **Infrastructure**: Docker, Docker Compose

---

## 📈 **Key Features**

### **Financial Data Exploration**
- **Real-time Market Data**: Live stock prices and financial ratios
- **Interactive Charts**: Professional-grade financial visualizations
- **Company Profiles**: Comprehensive company analysis and metrics
- **Sector Analysis**: Performance comparison across industries
- **Custom Queries**: Advanced SQL-based data exploration

### **ETL Pipeline**
- **Multi-source Collection**: Yahoo Finance, Alpha Vantage, FRED
- **Data Quality**: Validation, cleaning, and confidence scoring
- **Incremental Loading**: Efficient data updates and versioning
- **Monitoring**: Comprehensive logging and health checks

### **Investment Strategy Module**
- **Strategy Management**: Create, update, and manage investment strategies
- **Backtesting Engine**: Execute and monitor strategy backtests
- **Results Analysis**: Comprehensive performance metrics and reporting
- **API-First Design**: RESTful API for integration and automation

---

## 🎯 **Development Roadmap**

### **Phase 4: Microservices Implementation (Current)**
- **Tech-020**: ✅ **COMPLETED** - Microservices Foundation & Structure
- **Story-015**: 🔄 **IN PROGRESS** - Investment Strategy Module (Week 2)
- **Tech-021**: ETL Service Extraction (Next Priority)
- **Tech-022**: Financial Analysis Service Extraction
- **Tech-023**: Inter-Service Communication Setup
- **Tech-024**: Data Service & Database Management

### **Phase 5: Advanced Features**
- **Portfolio Management**: Tracking and analysis tools
- **Risk Assessment**: Advanced risk metrics and stress testing
- **AI/ML Integration**: Predictive analytics and insights
- **Mobile Applications**: Cross-platform investment tools

---

## 🤝 **Contributing**

### **For Team Members**
1. **Setup Environment**: Follow the [Team Setup Guide](docs/TEAM_ENVIRONMENT_SETUP.md)
2. **Choose Task**: Pick from the [Master TODO](MASTER_TODO.md)
3. **Development**: Follow the established patterns and testing
4. **Documentation**: Update docs as you implement features

### **Development Standards**
- **Code Quality**: Pre-commit hooks and linting
- **Testing**: Comprehensive test coverage
- **Documentation**: Clear docstrings and README updates
- **Security**: No credentials in version control

---

## 📚 **Documentation**

- **Project Overview**: [docs/project_organization.md](docs/project_organization.md)
- **Database Schema**: [database/schema.sql](database/schema.sql)
- **API Documentation**: [docs/api/](docs/api/)
- **Testing Guide**: [scripts/testing/README.md](scripts/testing/README.md)
- **Microservices Plan**: [docs/microservices_architecture_plan.md](docs/microservices_architecture_plan.md)
- **Story-015 Week 1 Report**: [docs/story-015-week1-completion-report.md](docs/story-015-week1-completion-report.md)
- **Financial Analysis Service**: [services/financial-analysis-service/README.md](services/financial-analysis-service/README.md)

---

## 🆘 **Support & Help**

### **Team Resources**
- **Team Setup Guide**: [docs/TEAM_ENVIRONMENT_SETUP.md](docs/TEAM_ENVIRONMENT_SETUP.md)
- **Current Status**: [MASTER_TODO.md](MASTER_TODO.md) *(Single Source of Truth)*
- **Master TODO**: [MASTER_TODO.md](MASTER_TODO.md)

### **Getting Help**
- Check existing documentation first
- Ask in team meetings/chats
- Create issues for bugs or feature requests
- Review the troubleshooting section in setup guides

---

## 📄 **License**

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

---

**Status**: 🚧 **Active Development** - Phase 4: Microservices Implementation
**Last Updated**: August 26, 2025
**Next Milestone**: Story-005 - Enhanced Company Analysis with working CAGR data
