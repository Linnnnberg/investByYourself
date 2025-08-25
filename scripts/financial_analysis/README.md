# Financial Data Exploration System

## Overview

This system provides comprehensive financial data exploration and visualization capabilities for the InvestByYourself platform. It allows you to:

- **Query real financial data** from the database (top companies by market cap, sector analysis, etc.)
- **Generate interactive charts** (price trends, financial ratios, sector comparisons)
- **Show company profiles** with comprehensive financial metrics
- **Create a dashboard** for data exploration

## Features

### 🏢 Company Analysis
- **Top Companies by Market Cap**: Query and rank companies by market capitalization
- **Sector Performance**: Analyze performance across different sectors
- **Company Profiles**: Detailed company information with financial metrics
- **Peer Comparison**: Compare companies within the same sector

### 📊 Data Visualization
- **Market Cap Charts**: Bar charts showing company rankings
- **Price History**: Candlestick charts for stock price analysis
- **Financial Ratios**: Comparison charts for P/E, P/B, P/S ratios
- **Sector Analysis**: Sector performance and comparison charts

### 🔍 Data Exploration
- **SQL Query Interface**: Execute custom SQL queries
- **Predefined Queries**: Common financial analysis queries
- **Real-time Data**: Live data from the database
- **Interactive Filters**: Filter by sector, company count, time period

## Quick Start

### 1. Install Dependencies

```bash
cd scripts/financial_analysis
pip install -r requirements.txt
```

### 2. Populate Sample Data

First, populate the database with sample data to see the system in action:

```bash
python populate_sample_data.py
```

This will create:
- **16 major US companies** across 5 sectors
- **30 days of market data** with realistic price movements
- **12 months of financial ratios** for analysis
- **24 months of economic indicators** for macro analysis

### 3. Run the Data Explorer

Test the basic functionality:

```bash
python data_explorer.py
```

This will show:
- Top 5 US companies by market cap
- Sector performance overview
- Sample company profile (AAPL)

### 4. Launch the Interactive Dashboard

Start the Streamlit dashboard:

```bash
streamlit run financial_dashboard.py
```

The dashboard will open in your browser with:
- **Dashboard Overview**: Key metrics and charts
- **Market Analysis**: Interactive company rankings and filters
- **Company Profiles**: Detailed company information and charts
- **Sector Analysis**: Sector performance and comparisons
- **Data Explorer**: Custom SQL queries and data exploration

## System Architecture

### Core Components

1. **FinancialDataExplorer**: Database connection and query execution
2. **FinancialCharts**: Chart generation using Plotly
3. **CompanyProfile**: Company profile generation and analysis
4. **Streamlit Dashboard**: Interactive web interface

### Database Schema

The system works with the following tables:
- `companies`: Company information and metadata
- `market_data`: Daily market data (prices, volumes, ratios)
- `financial_ratios`: Historical financial ratios
- `economic_indicators`: Macroeconomic data
- `data_quality`: Data quality tracking
- `data_collection_logs`: Collection operation logs

## Example Queries

### Top 5 Companies by Market Cap

```sql
SELECT
    c.symbol, c.name, c.sector, c.market_cap, md.close_price
FROM companies c
LEFT JOIN market_data md ON c.id = md.company_id
WHERE c.is_active = TRUE AND c.market_cap IS NOT NULL
ORDER BY c.market_cap DESC LIMIT 5
```

### Sector Performance Analysis

```sql
SELECT
    sector,
    COUNT(*) as company_count,
    AVG(market_cap) as avg_market_cap,
    SUM(market_cap) as total_market_cap
FROM companies
WHERE is_active = TRUE AND sector IS NOT NULL
GROUP BY sector
ORDER BY total_market_cap DESC
```

### High P/E Companies

```sql
SELECT
    c.symbol, c.name, c.sector, md.pe_ratio, md.close_price
FROM companies c
LEFT JOIN market_data md ON c.id = md.company_id
WHERE c.is_active = TRUE AND md.pe_ratio > 20
ORDER BY md.pe_ratio DESC
```

## Usage Examples

### 1. Find Top Technology Companies

```python
from data_explorer import FinancialDataExplorer

explorer = FinancialDataExplorer()
tech_companies = explorer.get_top_companies_by_market_cap(limit=10, sector='Technology')
print(tech_companies)
```

### 2. Generate Company Profile

```python
from data_explorer import CompanyProfile

profile_generator = CompanyProfile(explorer)
aapl_profile = profile_generator.generate_company_profile('AAPL')
print(f"Company: {aapl_profile['overview']['name']}")
print(f"Market Cap: ${aapl_profile['overview']['market_cap']:,.0f}")
```

### 3. Create Market Cap Chart

```python
from data_explorer import FinancialCharts

charts = FinancialCharts()
top_companies = explorer.get_top_companies_by_market_cap(limit=10)
fig = charts.create_market_cap_chart(top_companies)
fig.show()
```

## Configuration

### Environment Variables

Ensure your `.env` file contains the database connection details:

```env
POSTGRES_HOST=localhost
POSTGRES_PORT=5432
POSTGRES_DB=investbyyourself
POSTGRES_USER=etl_user
POSTGRES_PASSWORD=your_password
REDIS_HOST=localhost
REDIS_PORT=6379
MINIO_HOST=localhost
MINIO_PORT=9000
MINIO_ACCESS_KEY=minio_admin
MINIO_SECRET_KEY=your_secret_key
```

### Database Connection

The system automatically connects to the database using the configuration from `config/database.py`. Make sure:

1. PostgreSQL is running and accessible
2. The database schema has been created
3. Sample data has been populated

## Troubleshooting

### Common Issues

1. **Database Connection Failed**
   - Check if PostgreSQL is running
   - Verify connection credentials in `.env`
   - Ensure database exists and schema is created

2. **No Data Found**
   - Run `populate_sample_data.py` to create sample data
   - Check if tables exist and contain data
   - Verify database permissions

3. **Import Errors**
   - Install all requirements: `pip install -r requirements.txt`
   - Check Python path and project structure
   - Ensure all dependencies are compatible

### Performance Tips

1. **Database Indexes**: The schema includes performance indexes for common queries
2. **Connection Pooling**: Uses connection pooling for efficient database access
3. **Caching**: Consider implementing Redis caching for frequently accessed data
4. **Query Optimization**: Use the predefined queries for best performance

## Next Steps

### Enhancements

1. **Real-time Data**: Integrate with live market data feeds
2. **Advanced Analytics**: Add technical indicators and analysis tools
3. **Portfolio Management**: Build portfolio tracking and analysis
4. **Risk Assessment**: Implement risk metrics and stress testing
5. **API Endpoints**: Create REST API for external access

### Integration

1. **ETL Pipeline**: Connect with the ETL service for automated data updates
2. **Microservices**: Extract into separate microservice for scalability
3. **Monitoring**: Add performance monitoring and alerting
4. **Security**: Implement authentication and authorization

## Support

For issues or questions:
1. Check the troubleshooting section above
2. Review the database schema and configuration
3. Check the logs for detailed error messages
4. Verify all dependencies are properly installed

---

**Note**: This system is designed to work with the InvestByYourself database infrastructure. Ensure the database is properly set up before using these tools.
