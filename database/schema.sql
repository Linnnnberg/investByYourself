-- =====================================================
-- InvestByYourself Database Schema
-- Tech-008: Database Infrastructure Setup
-- =====================================================

-- Enable UUID extension for PostgreSQL
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";

-- =====================================================
-- CORE ENTITIES
-- =====================================================

-- Companies table - Core company information
CREATE TABLE companies (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    symbol VARCHAR(20) UNIQUE NOT NULL,
    name VARCHAR(255) NOT NULL,
    sector VARCHAR(100),
    industry VARCHAR(100),
    exchange VARCHAR(20),
    currency VARCHAR(3) DEFAULT 'USD',
    country VARCHAR(100),
    website VARCHAR(255),
    description TEXT,
    employee_count INTEGER,
    market_cap DECIMAL(20,2),
    enterprise_value DECIMAL(20,2),
    ceo VARCHAR(255),
    headquarters VARCHAR(255),
    founded_year INTEGER,
    is_active BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Company profiles - Extended company data
CREATE TABLE company_profiles (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    company_id UUID REFERENCES companies(id) ON DELETE CASCADE,
    profile_date DATE NOT NULL,
    business_summary TEXT,
    key_products TEXT[],
    competitors TEXT[],
    risk_factors TEXT[],
    growth_drivers TEXT[],
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    UNIQUE(company_id, profile_date)
);

-- =====================================================
-- FINANCIAL DATA
-- =====================================================

-- Financial ratios table
CREATE TABLE financial_ratios (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    company_id UUID REFERENCES companies(id) ON DELETE CASCADE,
    ratio_date DATE NOT NULL,
    ratio_type VARCHAR(50) NOT NULL,
    ratio_value DECIMAL(15,6),
    ratio_unit VARCHAR(20),
    source VARCHAR(50) DEFAULT 'yfinance',
    confidence_score DECIMAL(3,2) DEFAULT 1.0,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    UNIQUE(company_id, ratio_date, ratio_type)
);

-- Financial statements table
CREATE TABLE financial_statements (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    company_id UUID REFERENCES companies(id) ON DELETE CASCADE,
    statement_date DATE NOT NULL,
    statement_type VARCHAR(20) NOT NULL, -- 'income', 'balance', 'cash_flow'
    period_type VARCHAR(20) NOT NULL, -- 'annual', 'quarterly'
    fiscal_year INTEGER,
    fiscal_quarter INTEGER,
    total_revenue DECIMAL(20,2),
    net_income DECIMAL(20,2),
    total_assets DECIMAL(20,2),
    total_liabilities DECIMAL(20,2),
    cash_equivalents DECIMAL(20,2),
    total_debt DECIMAL(20,2),
    source VARCHAR(50) DEFAULT 'yfinance',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    UNIQUE(company_id, statement_date, statement_type, period_type)
);

-- Market data table
CREATE TABLE market_data (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    company_id UUID REFERENCES companies(id) ON DELETE CASCADE,
    data_date DATE NOT NULL,
    open_price DECIMAL(10,4),
    high_price DECIMAL(10,4),
    low_price DECIMAL(10,4),
    close_price DECIMAL(10,4),
    adjusted_close DECIMAL(10,4),
    volume BIGINT,
    market_cap DECIMAL(20,2),
    enterprise_value DECIMAL(20,2),
    pe_ratio DECIMAL(10,4),
    pb_ratio DECIMAL(10,4),
    ps_ratio DECIMAL(10,4),
    dividend_yield DECIMAL(5,4),
    beta DECIMAL(5,4),
    source VARCHAR(50) DEFAULT 'yfinance',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    UNIQUE(company_id, data_date)
);

-- =====================================================
-- MACRO ECONOMIC DATA
-- =====================================================

-- Economic indicators table
CREATE TABLE economic_indicators (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    indicator_date DATE NOT NULL,
    indicator_type VARCHAR(50) NOT NULL, -- 'CPI', 'PPI', 'GDP', 'Unemployment'
    indicator_value DECIMAL(15,6),
    indicator_unit VARCHAR(20),
    period_type VARCHAR(20) DEFAULT 'monthly',
    source VARCHAR(50) DEFAULT 'FRED',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    UNIQUE(indicator_date, indicator_type)
);

-- =====================================================
-- DATA QUALITY & TRACKING
-- =====================================================

-- Data quality tracking table
CREATE TABLE data_quality (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    data_source VARCHAR(50) NOT NULL,
    data_type VARCHAR(50) NOT NULL,
    quality_date DATE NOT NULL,
    record_count INTEGER,
    completeness_score DECIMAL(3,2),
    accuracy_score DECIMAL(3,2),
    freshness_score DECIMAL(3,2),
    overall_score DECIMAL(3,2),
    issues_found TEXT[],
    last_updated TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    UNIQUE(data_source, data_type, quality_date)
);

-- Data collection logs table
CREATE TABLE data_collection_logs (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    collection_date TIMESTAMP NOT NULL,
    data_source VARCHAR(50) NOT NULL,
    data_type VARCHAR(50) NOT NULL,
    status VARCHAR(20) NOT NULL, -- 'success', 'partial', 'failed'
    records_collected INTEGER,
    records_processed INTEGER,
    errors TEXT[],
    duration_seconds INTEGER,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- =====================================================
-- INDEXES FOR PERFORMANCE
-- =====================================================

-- Companies indexes
CREATE INDEX idx_companies_symbol ON companies(symbol);
CREATE INDEX idx_companies_sector ON companies(sector);
CREATE INDEX idx_companies_industry ON companies(industry);
CREATE INDEX idx_companies_active ON companies(is_active);

-- Financial data indexes
CREATE INDEX idx_financial_ratios_company_date ON financial_ratios(company_id, ratio_date);
CREATE INDEX idx_financial_ratios_type ON financial_ratios(ratio_type);
CREATE INDEX idx_financial_statements_company_date ON financial_statements(company_id, statement_date);
CREATE INDEX idx_financial_statements_type ON financial_statements(statement_type);
CREATE INDEX idx_market_data_company_date ON market_data(company_id, data_date);

-- Economic data indexes
CREATE INDEX idx_economic_indicators_date ON economic_indicators(indicator_date);
CREATE INDEX idx_economic_indicators_type ON economic_indicators(indicator_type);

-- Data quality indexes
CREATE INDEX idx_data_quality_source_date ON data_quality(data_source, quality_date);
CREATE INDEX idx_data_collection_logs_date ON data_collection_logs(collection_date);
CREATE INDEX idx_data_collection_logs_source ON data_collection_logs(data_source);

-- =====================================================
-- VIEWS FOR COMMON QUERIES
-- =====================================================

-- Company overview view
CREATE VIEW company_overview AS
SELECT
    c.id,
    c.symbol,
    c.name,
    c.sector,
    c.industry,
    c.market_cap,
    c.enterprise_value,
    md.close_price as current_price,
    md.pe_ratio,
    md.pb_ratio,
    md.dividend_yield,
    md.beta,
    c.updated_at as last_updated
FROM companies c
LEFT JOIN market_data md ON c.id = md.company_id
WHERE c.is_active = TRUE
AND md.data_date = (
    SELECT MAX(data_date)
    FROM market_data md2
    WHERE md2.company_id = c.id
);

-- Financial ratios summary view
CREATE VIEW financial_ratios_summary AS
SELECT
    c.symbol,
    c.name,
    c.sector,
    fr.ratio_type,
    AVG(fr.ratio_value) as avg_ratio,
    MIN(fr.ratio_value) as min_ratio,
    MAX(fr.ratio_value) as max_ratio,
    COUNT(*) as data_points
FROM companies c
JOIN financial_ratios fr ON c.id = fr.company_id
WHERE c.is_active = TRUE
GROUP BY c.symbol, c.name, c.sector, fr.ratio_type;

-- =====================================================
-- FUNCTIONS & TRIGGERS
-- =====================================================

-- Function to update updated_at timestamp
CREATE OR REPLACE FUNCTION update_updated_at_column()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = CURRENT_TIMESTAMP;
    RETURN NEW;
END;
$$ language 'plpgsql';

-- Trigger to automatically update updated_at
CREATE TRIGGER update_companies_updated_at
    BEFORE UPDATE ON companies
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

-- Function to calculate data quality score
CREATE OR REPLACE FUNCTION calculate_quality_score(
    completeness DECIMAL,
    accuracy DECIMAL,
    freshness DECIMAL
)
RETURNS DECIMAL AS $$
BEGIN
    RETURN (completeness + accuracy + freshness) / 3.0;
END;
$$ LANGUAGE plpgsql;

-- =====================================================
-- INITIAL DATA
-- =====================================================

-- Insert sample sectors and industries
INSERT INTO companies (symbol, name, sector, industry, exchange, country) VALUES
('AAPL', 'Apple Inc.', 'Technology', 'Consumer Electronics', 'NASDAQ', 'United States'),
('MSFT', 'Microsoft Corporation', 'Technology', 'Software', 'NASDAQ', 'United States'),
('GOOGL', 'Alphabet Inc.', 'Technology', 'Internet Content & Information', 'NASDAQ', 'United States'),
('AMZN', 'Amazon.com Inc.', 'Consumer Cyclical', 'Internet Retail', 'NASDAQ', 'United States'),
('TSLA', 'Tesla Inc.', 'Consumer Cyclical', 'Auto Manufacturers', 'NASDAQ', 'United States')
ON CONFLICT (symbol) DO NOTHING;

-- =====================================================
-- SCHEMA VERSION TRACKING
-- =====================================================

-- Schema version table
CREATE TABLE schema_versions (
    id SERIAL PRIMARY KEY,
    version VARCHAR(20) NOT NULL,
    applied_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    description TEXT,
    applied_by VARCHAR(100) DEFAULT 'system'
);

-- Insert current schema version
INSERT INTO schema_versions (version, description) VALUES
('1.0.0', 'Initial schema for InvestByYourself ETL infrastructure');

-- =====================================================
-- COMMENTS
-- =====================================================

COMMENT ON TABLE companies IS 'Core company information and metadata';
COMMENT ON TABLE financial_ratios IS 'Financial ratios and metrics for companies';
COMMENT ON TABLE market_data IS 'Daily market data including prices and key ratios';
COMMENT ON TABLE economic_indicators IS 'Macroeconomic indicators from FRED and other sources';
COMMENT ON TABLE data_quality IS 'Data quality metrics and tracking';
COMMENT ON TABLE data_collection_logs IS 'Logs of data collection operations';

COMMENT ON COLUMN companies.market_cap IS 'Market capitalization in USD';
COMMENT ON COLUMN companies.enterprise_value IS 'Enterprise value in USD';
COMMENT ON COLUMN financial_ratios.confidence_score IS 'Data quality confidence score (0.0 to 1.0)';
COMMENT ON COLUMN data_quality.overall_score IS 'Overall data quality score (0.0 to 1.0)';
