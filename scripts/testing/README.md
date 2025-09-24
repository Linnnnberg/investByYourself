# Testing Directory - Portfolio Optimization Concepts

## Overview

This directory contains a clean, focused implementation of portfolio optimization concepts using PyPortfolioOpt. The focus is on understanding general principles rather than specific test cases.

## Key Files

### 1. **Portfolio Optimization Framework** (`portfolio_optimization_framework.py`)
- **Purpose**: Demonstrates core portfolio optimization concepts
- **Features**:
  - Mean-Variance Optimization (MVO)
  - Hierarchical Risk Parity (HRP)
  - Efficient Frontier Analysis
  - Comprehensive Risk Metrics
  - Generic Strategy Framework

### 2. **Portfolio Optimization Guide** (`PORTFOLIO_OPTIMIZATION_GUIDE.md`)
- **Purpose**: Comprehensive guide to portfolio optimization concepts
- **Content**:
  - Core concepts and principles
  - Implementation guidelines
  - Best practices and common pitfalls
  - Advanced topics and resources

## Core Concepts Demonstrated

### **Portfolio Optimization Methods**
1. **MVO (Mean-Variance Optimization)**
   - Maximize Sharpe ratio
   - Target return/volatility optimization
   - Efficient frontier generation

2. **HRP (Hierarchical Risk Parity)**
   - Non-parametric approach
   - Robust to estimation errors
   - Hierarchical clustering-based

3. **Risk Management**
   - VaR and CVaR calculations
   - Maximum drawdown analysis
   - Comprehensive risk metrics

### **Strategy Framework**
1. **Generic Momentum Strategy**
   - Applicable to any asset universe
   - Configurable lookback and selection
   - Integrated optimization

2. **Sector Rotation Strategy**
   - Sector-level momentum calculation
   - Asset allocation within sectors
   - Flexible sector mapping

## Usage

### **Basic Example**
```python
from portfolio_optimization_framework import PortfolioOptimizer, StrategyFramework

# Initialize optimizer
optimizer = PortfolioOptimizer(risk_free_rate=0.02)

# Prepare data
optimizer.prepare_data(prices_df)

# Optimize portfolio
weights, performance = optimizer.optimize_mvo(max_sharpe=True)

# Calculate risk metrics
risk_metrics = optimizer.calculate_risk_metrics(weights)
```

### **Strategy Implementation**
```python
# Create strategy framework
strategy = StrategyFramework(optimizer)

# Implement momentum strategy
returns, weights = strategy.momentum_strategy(
    prices_df,
    lookback=12,
    top_k=2,
    rebalance_freq='M'
)
```

## Key Benefits

### **1. General Applicability**
- Works with any asset universe
- Configurable parameters
- No hardcoded tickers or strategies

### **2. Robust Implementation**
- Proper error handling
- Fallback strategies
- Covariance shrinkage for stability

### **3. Comprehensive Analysis**
- Multiple optimization methods
- Extensive risk metrics
- Efficient frontier visualization

### **4. Educational Value**
- Clear concept demonstration
- Well-documented code
- Practical examples

## Requirements

```bash
pip install PyPortfolioOpt yfinance pandas numpy matplotlib seaborn
```

## Running the Framework

```bash
python portfolio_optimization_framework.py
```

This will demonstrate all the key concepts with synthetic data and show how the framework works.

## What This Replaces

This clean implementation replaces the previous overlapping test files:
- ❌ `sector_rotation_4of5.py` - Specific ETF test
- ❌ `sector_rotation_pypfopt_enhanced.py` - Complex test case
- ❌ `sector_rotation_simple_enhanced.py` - Another test case
- ❌ `analyze_etf_choices.py` - Specific analysis
- ❌ Various report files - Specific results

## Key Takeaways

1. **Focus on Concepts**: Understand the general principles, not specific implementations
2. **Reusable Framework**: Apply to any asset universe or strategy
3. **Robust Implementation**: Handle errors gracefully with fallbacks
4. **Educational Value**: Learn portfolio optimization fundamentals
5. **Practical Application**: Ready to use with real data

## Next Steps

1. **Understand the Concepts**: Read the guide and framework code
2. **Apply to Your Data**: Use with your own asset universe
3. **Customize Strategies**: Modify the framework for your needs
4. **Add Advanced Features**: Implement Black-Litterman, factor models, etc.
5. **Production Use**: Add proper testing and monitoring for live trading

This framework provides a solid foundation for understanding and implementing portfolio optimization concepts that can be applied to any investment strategy.
