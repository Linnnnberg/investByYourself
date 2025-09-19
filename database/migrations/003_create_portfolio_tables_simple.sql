-- Portfolio Tables Migration (SQLite Compatible)
-- InvestByYourself Financial Platform

-- Create portfolios table
CREATE TABLE IF NOT EXISTS portfolios (
    id TEXT PRIMARY KEY,
    user_id TEXT NOT NULL,
    name TEXT NOT NULL,
    description TEXT,
    value REAL DEFAULT 0.0,
    change REAL DEFAULT 0.0,
    change_percent REAL DEFAULT 0.0,
    allocation TEXT DEFAULT '{}',
    risk_level TEXT DEFAULT 'Medium',
    status TEXT DEFAULT 'Draft',
    workflow_id TEXT,
    execution_id TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    last_updated TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Create portfolio_holdings table
CREATE TABLE IF NOT EXISTS portfolio_holdings (
    id TEXT PRIMARY KEY,
    portfolio_id TEXT NOT NULL,
    symbol TEXT NOT NULL,
    name TEXT,
    asset_type TEXT DEFAULT 'Stock',
    quantity REAL DEFAULT 0.0,
    average_price REAL DEFAULT 0.0,
    current_price REAL DEFAULT 0.0,
    market_value REAL DEFAULT 0.0,
    target_weight REAL DEFAULT 0.0,
    actual_weight REAL DEFAULT 0.0,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (portfolio_id) REFERENCES portfolios(id)
);

-- Create portfolio_performance table
CREATE TABLE IF NOT EXISTS portfolio_performance (
    id TEXT PRIMARY KEY,
    portfolio_id TEXT NOT NULL,
    date TIMESTAMP NOT NULL,
    total_value REAL NOT NULL,
    daily_return REAL DEFAULT 0.0,
    cumulative_return REAL DEFAULT 0.0,
    volatility REAL DEFAULT 0.0,
    sharpe_ratio REAL DEFAULT 0.0,
    max_drawdown REAL DEFAULT 0.0,
    benchmark_return REAL DEFAULT 0.0,
    alpha REAL DEFAULT 0.0,
    beta REAL DEFAULT 0.0,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (portfolio_id) REFERENCES portfolios(id)
);

-- Insert sample data
INSERT INTO portfolios (id, user_id, name, description, value, change, change_percent, allocation, risk_level, status, workflow_id, execution_id) VALUES
('sample_portfolio_1', 'current_user', 'Conservative Growth', 'Low-risk portfolio focused on steady growth', 125000.00, 2500.00, 2.04, '{"Bonds": 0.6, "Stocks": 0.3, "Cash": 0.1}', 'Low', 'Active', 'comprehensive_portfolio_creation', 'exec_1'),
('sample_portfolio_2', 'current_user', 'Balanced Growth', 'Moderate risk portfolio with balanced allocation', 87500.00, -1250.00, -1.41, '{"Stocks": 0.6, "Bonds": 0.3, "Alternatives": 0.1}', 'Medium', 'Active', 'advanced_allocation_framework', 'exec_2'),
('sample_portfolio_3', 'current_user', 'Aggressive Growth', 'High-growth potential portfolio', 45000.00, 1800.00, 4.17, '{"Stocks": 0.8, "Bonds": 0.15, "Alternatives": 0.05}', 'High', 'Draft', 'comprehensive_portfolio_creation', 'exec_3');
