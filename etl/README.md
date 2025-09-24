# ETL Data Import System
InvestByYourself Financial Platform

## Overview

The ETL (Extract, Transform, Load) system is responsible for collecting, processing, and storing financial market data from various sources. This system is containerized using Docker and integrates seamlessly with the main application.

## Architecture

```
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│   Data Sources  │    │   ETL Service   │    │   Data Storage  │
│                 │    │                 │    │                 │
│ • Yahoo Finance │───▶│ • Collectors    │───▶│ • SQLite DB     │
│ • Alpha Vantage │    │ • Transformers  │    │ • Redis Cache   │
│ • FRED          │    │ • Loaders       │    │ • File Storage  │
└─────────────────┘    └─────────────────┘    └─────────────────┘
```

## Features

- **Multi-source Data Collection**: Yahoo Finance, Alpha Vantage, FRED
- **Automated Scheduling**: Cron-like scheduling for regular data updates
- **Data Validation**: Quality checks and validation rules
- **Error Handling**: Retry logic with exponential backoff
- **Rate Limiting**: Respects API rate limits
- **Health Monitoring**: Comprehensive health checks
- **Docker Integration**: Fully containerized and orchestrated

## Quick Start

### 1. Start the ETL Service

```bash
# Start all services including ETL
docker-compose -f docker-compose.dev.yml up -d

# Check ETL service status
docker-compose -f docker-compose.dev.yml logs etl
```

### 2. Run Manual Data Import

```bash
# Full data import
docker-compose -f docker-compose.dev.yml exec etl python scripts/etl_orchestrator.py --mode full

# Incremental data import
docker-compose -f docker-compose.dev.yml exec etl python scripts/etl_orchestrator.py --mode incremental
```

### 3. Test the ETL System

```bash
# Run ETL tests
docker-compose -f docker-compose.dev.yml exec etl python scripts/test_etl.py
```

### 4. Start Scheduled Operations

```bash
# Start the scheduler
docker-compose -f docker-compose.dev.yml exec etl python scripts/scheduler.py
```

## Configuration

### Environment Variables

| Variable | Description | Default |
|----------|-------------|---------|
| `DATABASE_URL` | SQLite database URL | `sqlite+aiosqlite:////shared_data/investbyyourself_dev.db` |
| `REDIS_URL` | Redis cache URL | `redis://:dev_redis_123@redis:6379/0` |
| `ALPHA_VANTAGE_API_KEY` | Alpha Vantage API key | (optional) |
| `FRED_API_KEY` | FRED API key | (optional) |
| `ETL_MODE` | ETL operation mode | `development` |
| `ETL_LOG_LEVEL` | Logging level | `INFO` |
| `ETL_BATCH_SIZE` | Batch size for processing | `50` |

### Data Sources Configuration

Edit `config/data_sources.yaml` to configure:
- Company symbols to track
- ETF symbols
- Economic indicators
- API settings and rate limits

### ETL Configuration

Edit `config/etl_config.yaml` to configure:
- Data source settings
- Database connections
- Redis settings
- Logging configuration
- Scheduling rules
- Data quality thresholds

## Data Sources

### Yahoo Finance
- **Data Types**: Stock prices, company profiles, financials
- **Rate Limit**: 1 request/second
- **Coverage**: Global
- **Cost**: Free

### Alpha Vantage
- **Data Types**: Technical indicators, fundamental data
- **Rate Limit**: 5 requests/minute
- **Coverage**: US-focused
- **Cost**: Free tier

### FRED (Federal Reserve)
- **Data Types**: Economic indicators, inflation, GDP
- **Rate Limit**: 120 requests/minute
- **Coverage**: US
- **Cost**: Free

## Scheduling

The ETL system supports automated scheduling for:

- **Daily Market Data**: Weekdays at 6 AM
- **Weekly Company Profiles**: Monday at 2 AM
- **Monthly Economic Data**: 1st of month at 3 AM
- **Weekly Data Validation**: Sunday at 4 AM

## Monitoring

### Health Checks

```bash
# Check ETL service health
docker-compose -f docker-compose.dev.yml exec etl python scripts/health_check.py
```

### Logs

```bash
# View ETL logs
docker-compose -f docker-compose.dev.yml logs -f etl

# View specific log files
docker-compose -f docker-compose.dev.yml exec etl tail -f /app/logs/etl.log
```

### Redis Cache

Access Redis Commander at `http://localhost:8081` to monitor cached data.

## Development

### Project Structure

```
etl/
├── Dockerfile              # ETL container configuration
├── requirements.txt        # Python dependencies
├── README.md              # This file
├── config/                # Configuration files
│   ├── etl_config.yaml    # ETL settings
│   └── data_sources.yaml  # Data source configuration
├── scripts/               # Executable scripts
│   ├── etl_orchestrator.py # Main ETL orchestrator
│   ├── scheduler.py       # ETL scheduler
│   ├── health_check.py    # Health check script
│   └── test_etl.py        # ETL test script
└── src/                   # Source code
    ├── collectors/        # Data collectors
    ├── transformers/      # Data transformers
    ├── loaders/          # Data loaders
    └── utils/            # Utility functions
```

### Adding New Data Sources

1. Create a new collector in `src/collectors/`
2. Implement the collector interface
3. Add configuration in `config/data_sources.yaml`
4. Update the orchestrator to use the new collector

### Adding New Data Types

1. Create a new transformer in `src/transformers/`
2. Create a new loader in `src/loaders/`
3. Update the orchestrator to process the new data type

## Troubleshooting

### Common Issues

1. **Database Connection Failed**
   - Check if the database file exists and has proper permissions
   - Verify the `DATABASE_URL` environment variable

2. **Redis Connection Failed**
   - Check if Redis service is running
   - Verify the `REDIS_URL` environment variable

3. **API Rate Limit Exceeded**
   - Check the rate limiting configuration
   - Verify API keys are valid

4. **Data Quality Issues**
   - Check data validation rules
   - Review source data quality

### Debug Mode

```bash
# Run ETL in debug mode
docker-compose -f docker-compose.dev.yml exec etl python scripts/etl_orchestrator.py --mode full --config config/etl_config.yaml
```

## API Integration

The ETL system integrates with the main API through:

- **Shared Database**: SQLite database shared between API and ETL
- **Redis Cache**: Shared cache for fast data access
- **Health Checks**: API can check ETL service health
- **Data Validation**: API can trigger data quality checks

## Performance

- **Batch Processing**: Configurable batch sizes for efficient processing
- **Rate Limiting**: Respects API rate limits to avoid throttling
- **Caching**: Redis caching for frequently accessed data
- **Incremental Updates**: Only processes new/changed data when possible

## Security

- **API Key Management**: Secure handling of API keys
- **Data Validation**: Input validation and sanitization
- **Error Handling**: Secure error messages without sensitive data
- **Logging**: Comprehensive logging for audit trails

## Contributing

1. Follow the existing code structure
2. Add appropriate tests for new functionality
3. Update documentation for any changes
4. Ensure all tests pass before submitting

## License

This project is part of the InvestByYourself Financial Platform.
