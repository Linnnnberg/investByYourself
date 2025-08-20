-- Database Schema for investByYourself Platform
-- Story-005: ETL & Database Architecture Design
-- Created: January 2025

-- Enable required extensions
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";
CREATE EXTENSION IF NOT EXISTS "pg_stat_statements";

-- Create custom types
CREATE TYPE market_cap_category AS ENUM ('small', 'mid', 'large', 'mega');
CREATE TYPE data_source_type AS ENUM ('yahoo_finance', 'alpha_vantage', 'fred', 'api_ninjas', 'manual');
CREATE TYPE data_frequency AS ENUM ('real_time', 'hourly', 'daily', 'weekly', 'monthly', 'quarterly');

-- ============================================================================
-- CORE FINANCIAL ENTITIES
-- ============================================================================

-- Companies table - Core company information
CREATE TABLE companies (
    id SERIAL PRIMARY KEY,
    symbol VARCHAR(10) UNIQUE NOT NULL,
    name VARCHAR(255) NOT NULL,
    long_name TEXT,
    sector VARCHAR(100),
    industry VARCHAR(100),
    market_cap DECIMAL(20,2),
    market_cap_category market_cap_category,
    pe_ratio DECIMAL(10,4),
    forward_pe DECIMAL(10,4),
    price_to_book DECIMAL(10,4),
    price_to_sales DECIMAL(10,4),
    dividend_yield DECIMAL(5,4),
    beta DECIMAL(6,4),
    enterprise_value DECIMAL(20,2),
    debt_to_equity DECIMAL(8,4),
    return_on_equity DECIMAL(8,4),
    return_on_assets DECIMAL(8,4),
    profit_margin DECIMAL(8,4),
    revenue_growth DECIMAL(8,4),
    earnings_growth DECIMAL(8,4),
    country VARCHAR(100) DEFAULT 'US',
    exchange VARCHAR(50) DEFAULT 'NASDAQ',
    is_active BOOLEAN DEFAULT TRUE,
    data_source data_source_type DEFAULT 'yahoo_finance',
    last_updated TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Stock prices table - Historical price data
CREATE TABLE stock_prices (
    id SERIAL PRIMARY KEY,
    company_id INTEGER REFERENCES companies(id) ON DELETE CASCADE,
    date DATE NOT NULL,
    open_price DECIMAL(10,4),
    high_price DECIMAL(10,4),
    low_price DECIMAL(10,4),
    close_price DECIMAL(10,4),
    adjusted_close DECIMAL(10,4),
    volume BIGINT,
    dividend_amount DECIMAL(8,4) DEFAULT 0,
    split_coefficient DECIMAL(10,6) DEFAULT 1,
    data_source data_source_type DEFAULT 'yahoo_finance',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,

    UNIQUE(company_id, date)
);

-- Economic indicators table - Economic data definitions
CREATE TABLE economic_indicators (
    id SERIAL PRIMARY KEY,
    indicator_code VARCHAR(20) UNIQUE NOT NULL,
    indicator_name VARCHAR(255) NOT NULL,
    category VARCHAR(100),
    subcategory VARCHAR(100),
    frequency data_frequency,
    units VARCHAR(50),
    source VARCHAR(100) DEFAULT 'FRED',
    description TEXT,
    is_active BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Economic data table - Economic indicator values
CREATE TABLE economic_data (
    id SERIAL PRIMARY KEY,
    indicator_id INTEGER REFERENCES economic_indicators(id) ON DELETE CASCADE,
    date DATE NOT NULL,
    value DECIMAL(15,6),
    change_from_prev DECIMAL(15,6),
    change_percent DECIMAL(8,4),
    data_source data_source_type DEFAULT 'fred',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,

    UNIQUE(indicator_id, date)
);

-- ============================================================================
-- PORTFOLIO MANAGEMENT
-- ============================================================================

-- Portfolios table - Portfolio definitions
CREATE TABLE portfolios (
    id SERIAL PRIMARY KEY,
    name VARCHAR(255) NOT NULL,
    description TEXT,
    benchmark_symbol VARCHAR(10),
    risk_tolerance VARCHAR(20) DEFAULT 'moderate',
    target_return DECIMAL(8,4),
    max_drawdown DECIMAL(8,4),
    rebalance_frequency VARCHAR(20) DEFAULT 'quarterly',
    is_active BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Portfolio holdings table - Individual positions
CREATE TABLE portfolio_holdings (
    id SERIAL PRIMARY KEY,
    portfolio_id INTEGER REFERENCES portfolios(id) ON DELETE CASCADE,
    company_id INTEGER REFERENCES companies(id) ON DELETE CASCADE,
    shares DECIMAL(15,6) NOT NULL,
    cost_basis DECIMAL(10,4),
    purchase_date DATE,
    last_rebalance_date DATE,
    target_allocation DECIMAL(5,4),
    current_allocation DECIMAL(5,4),
    is_active BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,

    UNIQUE(portfolio_id, company_id)
);

-- Portfolio transactions table - Buy/sell history
CREATE TABLE portfolio_transactions (
    id SERIAL PRIMARY KEY,
    portfolio_id INTEGER REFERENCES portfolios(id) ON DELETE CASCADE,
    company_id INTEGER REFERENCES companies(id) ON DELETE CASCADE,
    transaction_type VARCHAR(10) NOT NULL CHECK (transaction_type IN ('buy', 'sell', 'dividend', 'split')),
    shares DECIMAL(15,6) NOT NULL,
    price_per_share DECIMAL(10,4),
    total_amount DECIMAL(12,2),
    transaction_date DATE NOT NULL,
    commission DECIMAL(8,2) DEFAULT 0,
    notes TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- ============================================================================
-- EARNINGS & FUNDAMENTALS
-- ============================================================================

-- Earnings table - Company earnings data
CREATE TABLE earnings (
    id SERIAL PRIMARY KEY,
    company_id INTEGER REFERENCES companies(id) ON DELETE CASCADE,
    quarter VARCHAR(7) NOT NULL, -- Format: YYYY-Q1
    fiscal_year INTEGER NOT NULL,
    fiscal_quarter INTEGER NOT NULL CHECK (fiscal_quarter BETWEEN 1 AND 4),
    report_date DATE,
    earnings_date DATE,
    eps_estimate DECIMAL(8,4),
    eps_actual DECIMAL(8,4),
    eps_surprise DECIMAL(8,4),
    revenue_estimate DECIMAL(15,2),
    revenue_actual DECIMAL(15,2),
    revenue_surprise DECIMAL(15,2),
    surprise_percentage DECIMAL(8,4),
    data_source data_source_type DEFAULT 'api_ninjas',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,

    UNIQUE(company_id, quarter)
);

-- Earnings call transcripts table - Call transcripts and analysis
CREATE TABLE earnings_call_transcripts (
    id SERIAL PRIMARY KEY,
    earnings_id INTEGER REFERENCES earnings(id) ON DELETE CASCADE,
    transcript_text TEXT,
    transcript_url VARCHAR(500),
    call_date TIMESTAMP,
    duration_minutes INTEGER,
    participants JSONB,
    key_metrics JSONB,
    sentiment_score DECIMAL(3,2) CHECK (sentiment_score BETWEEN -1.0 AND 1.0),
    key_topics TEXT[],
    data_source data_source_type DEFAULT 'api_ninjas',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Financial statements table - Quarterly/annual financial data
CREATE TABLE financial_statements (
    id SERIAL PRIMARY KEY,
    company_id INTEGER REFERENCES companies(id) ON DELETE CASCADE,
    statement_type VARCHAR(20) NOT NULL CHECK (statement_type IN ('income', 'balance', 'cash_flow')),
    period_type VARCHAR(10) NOT NULL CHECK (period_type IN ('quarterly', 'annual')),
    fiscal_year INTEGER NOT NULL,
    fiscal_quarter INTEGER CHECK (fiscal_quarter BETWEEN 1 AND 4),
    period_end_date DATE NOT NULL,
    filing_date DATE,
    revenue DECIMAL(15,2),
    gross_profit DECIMAL(15,2),
    operating_income DECIMAL(15,2),
    net_income DECIMAL(15,2),
    total_assets DECIMAL(15,2),
    total_liabilities DECIMAL(15,2),
    total_equity DECIMAL(15,2),
    operating_cash_flow DECIMAL(15,2),
    investing_cash_flow DECIMAL(15,2),
    financing_cash_flow DECIMAL(15,2),
    free_cash_flow DECIMAL(15,2),
    data_source data_source_type DEFAULT 'yahoo_finance',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,

    UNIQUE(company_id, statement_type, period_type, fiscal_year, fiscal_quarter)
);

-- ============================================================================
-- TECHNICAL ANALYSIS
-- ============================================================================

-- Technical indicators table - Calculated technical metrics
CREATE TABLE technical_indicators (
    id SERIAL PRIMARY KEY,
    company_id INTEGER REFERENCES companies(id) ON DELETE CASCADE,
    date DATE NOT NULL,
    sma_20 DECIMAL(10,4),
    sma_50 DECIMAL(10,4),
    sma_200 DECIMAL(10,4),
    ema_12 DECIMAL(10,4),
    ema_26 DECIMAL(10,4),
    rsi_14 DECIMAL(5,2),
    macd DECIMAL(8,4),
    macd_signal DECIMAL(8,4),
    macd_histogram DECIMAL(8,4),
    bollinger_upper DECIMAL(10,4),
    bollinger_middle DECIMAL(10,4),
    bollinger_lower DECIMAL(10,4),
    volume_sma_20 BIGINT,
    atr_14 DECIMAL(8,4),
    data_source data_source_type DEFAULT 'alpha_vantage',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,

    UNIQUE(company_id, date)
);

-- ============================================================================
-- DATA QUALITY & MONITORING
-- ============================================================================

-- Data quality logs table - Track data quality issues
CREATE TABLE data_quality_logs (
    id SERIAL PRIMARY KEY,
    table_name VARCHAR(100) NOT NULL,
    record_id INTEGER,
    quality_score DECIMAL(5,2) CHECK (quality_score BETWEEN 0 AND 100),
    validation_errors JSONB,
    warnings JSONB,
    data_source data_source_type,
    check_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    resolved BOOLEAN DEFAULT FALSE,
    resolution_notes TEXT
);

-- API usage logs table - Track API calls and rate limits
CREATE TABLE api_usage_logs (
    id SERIAL PRIMARY KEY,
    api_name VARCHAR(50) NOT NULL,
    endpoint VARCHAR(200),
    request_count INTEGER DEFAULT 1,
    rate_limit_remaining INTEGER,
    rate_limit_reset TIMESTAMP,
    last_request_time TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    error_count INTEGER DEFAULT 0,
    last_error_time TIMESTAMP,
    last_error_message TEXT
);

-- ============================================================================
-- INDEXES FOR PERFORMANCE
-- ============================================================================

-- Company indexes
CREATE INDEX idx_companies_symbol ON companies(symbol);
CREATE INDEX idx_companies_sector ON companies(sector);
CREATE INDEX idx_companies_industry ON companies(industry);
CREATE INDEX idx_companies_market_cap ON companies(market_cap);
CREATE INDEX idx_companies_exchange ON companies(exchange);
CREATE INDEX idx_companies_active ON companies(is_active);

-- Stock price indexes
CREATE INDEX idx_stock_prices_company_date ON stock_prices(company_id, date);
CREATE INDEX idx_stock_prices_date ON stock_prices(date);
CREATE INDEX idx_stock_prices_company_date_desc ON stock_prices(company_id, date DESC);

-- Economic data indexes
CREATE INDEX idx_economic_data_indicator_date ON economic_data(indicator_id, date);
CREATE INDEX idx_economic_data_date ON economic_data(date);

-- Portfolio indexes
CREATE INDEX idx_portfolio_holdings_portfolio ON portfolio_holdings(portfolio_id);
CREATE INDEX idx_portfolio_holdings_company ON portfolio_holdings(company_id);
CREATE INDEX idx_portfolio_transactions_portfolio ON portfolio_transactions(portfolio_id);
CREATE INDEX idx_portfolio_transactions_date ON portfolio_transactions(transaction_date);

-- Earnings indexes
CREATE INDEX idx_earnings_company_quarter ON earnings(company_id, quarter);
CREATE INDEX idx_earnings_date ON earnings(report_date);
CREATE INDEX idx_earnings_fiscal_year ON earnings(fiscal_year);

-- Technical indicators indexes
CREATE INDEX idx_technical_indicators_company_date ON technical_indicators(company_id, date);

-- ============================================================================
-- PARTITIONING FOR LARGE TABLES
-- ============================================================================

-- Partition stock_prices by year for better performance
CREATE TABLE stock_prices_2024 PARTITION OF stock_prices
FOR VALUES FROM ('2024-01-01') TO ('2025-01-01');

CREATE TABLE stock_prices_2025 PARTITION OF stock_prices
FOR VALUES FROM ('2025-01-01') TO ('2026-01-01');

-- ============================================================================
-- MATERIALIZED VIEWS FOR COMMON QUERIES
-- ============================================================================

-- Daily portfolio performance summary
CREATE MATERIALIZED VIEW portfolio_daily_summary AS
SELECT
    p.id as portfolio_id,
    p.name as portfolio_name,
    ph.company_id,
    c.symbol,
    c.name as company_name,
    ph.shares,
    ph.cost_basis,
    sp.close_price as current_price,
    (ph.shares * sp.close_price) as current_value,
    (ph.shares * sp.close_price - ph.shares * ph.cost_basis) as pnl,
    CASE
        WHEN ph.cost_basis > 0 THEN
            ((ph.shares * sp.close_price - ph.shares * ph.cost_basis) / (ph.shares * ph.cost_basis)) * 100
        ELSE 0
    END as pnl_percentage,
    sp.date
FROM portfolios p
JOIN portfolio_holdings ph ON p.id = ph.portfolio_id
JOIN companies c ON ph.company_id = c.id
JOIN stock_prices sp ON c.id = sp.company_id
WHERE sp.date >= CURRENT_DATE - INTERVAL '30 days'
  AND ph.is_active = TRUE
  AND p.is_active = TRUE;

CREATE UNIQUE INDEX idx_portfolio_daily_summary
ON portfolio_daily_summary(portfolio_id, company_id, date);

-- Company fundamentals summary
CREATE MATERIALIZED VIEW company_fundamentals_summary AS
SELECT
    c.id,
    c.symbol,
    c.name,
    c.sector,
    c.industry,
    c.market_cap,
    c.market_cap_category,
    c.pe_ratio,
    c.forward_pe,
    c.dividend_yield,
    c.beta,
    c.return_on_equity,
    c.return_on_assets,
    sp.close_price as latest_price,
    sp.date as latest_price_date,
    e.eps_actual as latest_eps,
    e.revenue_actual as latest_revenue,
    e.quarter as latest_quarter
FROM companies c
LEFT JOIN LATERAL (
    SELECT close_price, date
    FROM stock_prices
    WHERE company_id = c.id
    ORDER BY date DESC
    LIMIT 1
) sp ON TRUE
LEFT JOIN LATERAL (
    SELECT eps_actual, revenue_actual, quarter
    FROM earnings
    WHERE company_id = c.id
    ORDER BY fiscal_year DESC, fiscal_quarter DESC
    LIMIT 1
) e ON TRUE
WHERE c.is_active = TRUE;

CREATE UNIQUE INDEX idx_company_fundamentals_summary ON company_fundamentals_summary(id);

-- ============================================================================
-- FUNCTIONS AND TRIGGERS
-- ============================================================================

-- Function to update updated_at timestamp
CREATE OR REPLACE FUNCTION update_updated_at_column()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = CURRENT_TIMESTAMP;
    RETURN NEW;
END;
$$ language 'plpgsql';

-- Triggers for updated_at columns
CREATE TRIGGER update_companies_updated_at BEFORE UPDATE ON companies
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_portfolios_updated_at BEFORE UPDATE ON portfolios
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_portfolio_holdings_updated_at BEFORE UPDATE ON portfolio_holdings
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

-- Function to refresh materialized views
CREATE OR REPLACE FUNCTION refresh_materialized_views()
RETURNS void AS $$
BEGIN
    REFRESH MATERIALIZED VIEW CONCURRENTLY portfolio_daily_summary;
    REFRESH MATERIALIZED VIEW CONCURRENTLY company_fundamentals_summary;
END;
$$ LANGUAGE plpgsql;

-- ============================================================================
-- INITIAL DATA
-- ============================================================================

-- Insert sample economic indicators
INSERT INTO economic_indicators (indicator_code, indicator_name, category, frequency, units, description) VALUES
('GDP', 'Gross Domestic Product', 'Economic Growth', 'quarterly', 'Billions of Dollars', 'Total economic output'),
('CPI', 'Consumer Price Index', 'Inflation', 'monthly', 'Index', 'Consumer price inflation measure'),
('UNRATE', 'Unemployment Rate', 'Employment', 'monthly', 'Percent', 'Unemployment rate'),
('FEDFUNDS', 'Federal Funds Rate', 'Interest Rates', 'monthly', 'Percent', 'Federal Reserve target rate'),
('DGS10', '10-Year Treasury Rate', 'Interest Rates', 'daily', 'Percent', '10-year government bond yield');

-- ============================================================================
-- COMMENTS
-- ============================================================================

COMMENT ON TABLE companies IS 'Core company information and fundamental data';
COMMENT ON TABLE stock_prices IS 'Historical stock price data with OHLCV information';
COMMENT ON TABLE economic_indicators IS 'Economic indicator definitions and metadata';
COMMENT ON TABLE economic_data IS 'Economic indicator time series data';
COMMENT ON TABLE portfolios IS 'Portfolio definitions and configuration';
COMMENT ON TABLE portfolio_holdings IS 'Individual positions within portfolios';
COMMENT ON TABLE portfolio_transactions IS 'Buy/sell transaction history';
COMMENT ON TABLE earnings IS 'Company earnings data and estimates';
COMMENT ON TABLE earnings_call_transcripts IS 'Earnings call transcripts and analysis';
COMMENT ON TABLE financial_statements IS 'Quarterly and annual financial statements';
COMMENT ON TABLE technical_indicators IS 'Calculated technical analysis indicators';
COMMENT ON TABLE data_quality_logs IS 'Data quality validation and monitoring logs';
COMMENT ON TABLE api_usage_logs IS 'API usage tracking and rate limit monitoring';

COMMENT ON COLUMN companies.market_cap_category IS 'Market capitalization category for filtering and analysis';
COMMENT ON COLUMN companies.data_source IS 'Source of the data for tracking and validation';
COMMENT ON COLUMN stock_prices.adjusted_close IS 'Price adjusted for dividends and splits';
COMMENT ON COLUMN earnings.quarter IS 'Fiscal quarter in YYYY-Q1 format';
COMMENT ON COLUMN earnings_call_transcripts.sentiment_score IS 'Sentiment analysis score from -1.0 (negative) to 1.0 (positive)';
COMMENT ON COLUMN technical_indicators.rsi_14 IS 'Relative Strength Index over 14 periods';
COMMENT ON COLUMN technical_indicators.macd IS 'Moving Average Convergence Divergence';

-- ============================================================================
-- GRANTS AND PERMISSIONS
-- ============================================================================

-- Create read-only role for analytics
CREATE ROLE analytics_readonly;
GRANT CONNECT ON DATABASE investbyyourself TO analytics_readonly;
GRANT USAGE ON SCHEMA public TO analytics_readonly;
GRANT SELECT ON ALL TABLES IN SCHEMA public TO analytics_readonly;
GRANT SELECT ON ALL SEQUENCES IN SCHEMA public TO analytics_readonly;

-- Create ETL role for data loading
CREATE ROLE etl_user;
GRANT CONNECT ON DATABASE investbyyourself TO etl_user;
GRANT USAGE ON SCHEMA public TO etl_user;
GRANT SELECT, INSERT, UPDATE, DELETE ON ALL TABLES IN SCHEMA public TO etl_user;
GRANT USAGE ON ALL SEQUENCES IN SCHEMA public TO etl_user;

-- ============================================================================
-- SCHEMA VERSION TRACKING
-- ============================================================================

-- Create schema version table
CREATE TABLE schema_versions (
    id SERIAL PRIMARY KEY,
    version VARCHAR(20) NOT NULL,
    applied_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    description TEXT,
    checksum VARCHAR(64)
);

-- Insert current version
INSERT INTO schema_versions (version, description) VALUES
('1.0.0', 'Initial schema for investByYourself platform - Core financial entities, portfolio management, and ETL infrastructure');

-- ============================================================================
-- COMPLETION
-- ============================================================================

-- Verify schema creation
SELECT 'Schema created successfully' as status,
       COUNT(*) as table_count
FROM information_schema.tables
WHERE table_schema = 'public'
  AND table_type = 'BASE TABLE';
