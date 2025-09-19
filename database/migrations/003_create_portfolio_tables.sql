-- Portfolio Tables Migration
-- InvestByYourself Financial Platform
-- Migration: 003_create_portfolio_tables.sql

-- Create portfolios table
CREATE TABLE IF NOT EXISTS portfolios (
    id VARCHAR(255) PRIMARY KEY,
    user_id VARCHAR(255) NOT NULL,
    name VARCHAR(255) NOT NULL,
    description TEXT,
    value DECIMAL(15,2) DEFAULT 0.00,
    change DECIMAL(15,2) DEFAULT 0.00,
    change_percent DECIMAL(8,4) DEFAULT 0.0000,
    allocation JSON DEFAULT '{}',
    risk_level VARCHAR(20) DEFAULT 'Medium',
    status VARCHAR(20) DEFAULT 'Draft',
    workflow_id VARCHAR(255),
    execution_id VARCHAR(255),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    last_updated TIMESTAMP DEFAULT CURRENT_TIMESTAMP,

);

-- Create portfolio_holdings table
CREATE TABLE IF NOT EXISTS portfolio_holdings (
    id VARCHAR(255) PRIMARY KEY,
    portfolio_id VARCHAR(255) NOT NULL,
    symbol VARCHAR(20) NOT NULL,
    name VARCHAR(255),
    asset_type VARCHAR(50) DEFAULT 'Stock',
    quantity DECIMAL(15,6) DEFAULT 0.000000,
    average_price DECIMAL(10,4) DEFAULT 0.0000,
    current_price DECIMAL(10,4) DEFAULT 0.0000,
    market_value DECIMAL(15,2) DEFAULT 0.00,
    target_weight DECIMAL(8,6) DEFAULT 0.000000,
    actual_weight DECIMAL(8,6) DEFAULT 0.000000,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,

    FOREIGN KEY (portfolio_id) REFERENCES portfolios(id)
);

-- Create portfolio_performance table
CREATE TABLE IF NOT EXISTS portfolio_performance (
    id VARCHAR(255) PRIMARY KEY,
    portfolio_id VARCHAR(255) NOT NULL,
    date TIMESTAMP NOT NULL,
    total_value DECIMAL(15,2) NOT NULL,
    daily_return DECIMAL(8,6) DEFAULT 0.000000,
    cumulative_return DECIMAL(8,6) DEFAULT 0.000000,
    volatility DECIMAL(8,6) DEFAULT 0.000000,
    sharpe_ratio DECIMAL(8,6) DEFAULT 0.000000,
    max_drawdown DECIMAL(8,6) DEFAULT 0.000000,
    benchmark_return DECIMAL(8,6) DEFAULT 0.000000,
    alpha DECIMAL(8,6) DEFAULT 0.000000,
    beta DECIMAL(8,6) DEFAULT 0.000000,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,

    FOREIGN KEY (portfolio_id) REFERENCES portfolios(id)
);

-- Insert some sample data for testing
INSERT INTO portfolios (id, user_id, name, description, value, change, change_percent, allocation, risk_level, status, workflow_id, execution_id) VALUES
('sample_portfolio_1', 'current_user', 'Conservative Growth', 'Low-risk portfolio focused on steady growth', 125000.00, 2500.00, 2.04, '{"Bonds": 0.6, "Stocks": 0.3, "Cash": 0.1}', 'Low', 'Active', 'comprehensive_portfolio_creation', 'exec_1'),
('sample_portfolio_2', 'current_user', 'Balanced Growth', 'Moderate risk portfolio with balanced allocation', 87500.00, -1250.00, -1.41, '{"Stocks": 0.6, "Bonds": 0.3, "Alternatives": 0.1}', 'Medium', 'Active', 'advanced_allocation_framework', 'exec_2'),
('sample_portfolio_3', 'current_user', 'Aggressive Growth', 'High-growth potential portfolio', 45000.00, 1800.00, 4.17, '{"Stocks": 0.8, "Bonds": 0.15, "Alternatives": 0.05}', 'High', 'Draft', 'comprehensive_portfolio_creation', 'exec_3');

-- Insert sample holdings
INSERT INTO portfolio_holdings (id, portfolio_id, symbol, name, asset_type, quantity, average_price, current_price, market_value, target_weight, actual_weight) VALUES
('holding_1', 'sample_portfolio_1', 'BND', 'Vanguard Total Bond Market ETF', 'ETF', 1000.0, 80.50, 82.00, 82000.00, 0.6, 0.656),
('holding_2', 'sample_portfolio_1', 'VTI', 'Vanguard Total Stock Market ETF', 'ETF', 200.0, 220.00, 225.00, 45000.00, 0.3, 0.36),
('holding_3', 'sample_portfolio_1', 'CASH', 'Cash Position', 'Cash', 10000.0, 1.00, 1.00, 10000.00, 0.1, 0.08),
('holding_4', 'sample_portfolio_2', 'VTI', 'Vanguard Total Stock Market ETF', 'ETF', 300.0, 220.00, 225.00, 67500.00, 0.6, 0.771),
('holding_5', 'sample_portfolio_2', 'BND', 'Vanguard Total Bond Market ETF', 'ETF', 150.0, 80.50, 82.00, 12300.00, 0.3, 0.141),
('holding_6', 'sample_portfolio_2', 'REIT', 'Real Estate Investment Trust', 'ETF', 50.0, 100.00, 102.00, 5100.00, 0.1, 0.058);

-- Insert sample performance data
INSERT INTO portfolio_performance (id, portfolio_id, date, total_value, daily_return, cumulative_return, volatility, sharpe_ratio, max_drawdown, benchmark_return, alpha, beta) VALUES
('perf_1', 'sample_portfolio_1', '2025-01-20 00:00:00', 122500.00, 0.5, 2.5, 0.08, 1.2, -0.05, 0.3, 0.02, 0.7),
('perf_2', 'sample_portfolio_1', '2025-01-21 00:00:00', 125000.00, 2.04, 4.6, 0.08, 1.2, -0.05, 0.3, 0.02, 0.7),
('perf_3', 'sample_portfolio_2', '2025-01-20 00:00:00', 88950.00, -1.0, -1.0, 0.12, 0.8, -0.08, 0.5, -0.01, 1.1),
('perf_4', 'sample_portfolio_2', '2025-01-21 00:00:00', 87500.00, -1.41, -2.4, 0.12, 0.8, -0.08, 0.5, -0.01, 1.1),
('perf_5', 'sample_portfolio_3', '2025-01-20 00:00:00', 43200.00, 3.0, 3.0, 0.18, 0.6, -0.12, 0.8, -0.02, 1.4),
('perf_6', 'sample_portfolio_3', '2025-01-21 00:00:00', 45000.00, 4.17, 7.3, 0.18, 0.6, -0.12, 0.8, -0.02, 1.4);
