# Portfolio Management - Technical Documentation

## 🏗️ **Architecture Overview**

The Portfolio Management module follows a clean, layered architecture with clear separation of concerns and robust error handling.

## 🗄️ **Database Schema**

### **Core Tables**

```sql
-- Portfolio master table
CREATE TABLE portfolios (
    id VARCHAR(50) PRIMARY KEY,
    name VARCHAR(255) NOT NULL,
    description TEXT,
    user_id VARCHAR(50) NOT NULL,
    allocation JSONB NOT NULL,
    risk_level VARCHAR(20) NOT NULL,
    status VARCHAR(20) DEFAULT 'Active',
    value DECIMAL(15,2) DEFAULT 100000,
    change DECIMAL(15,2) DEFAULT 0,
    change_percent DECIMAL(8,4) DEFAULT 0,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Portfolio holdings (individual assets)
CREATE TABLE portfolio_holdings (
    id SERIAL PRIMARY KEY,
    portfolio_id VARCHAR(50) REFERENCES portfolios(id),
    asset_symbol VARCHAR(20) NOT NULL,
    asset_name VARCHAR(255),
    asset_type VARCHAR(20) NOT NULL,
    quantity DECIMAL(15,6) NOT NULL,
    current_price DECIMAL(10,4),
    total_value DECIMAL(15,2),
    allocation_weight DECIMAL(8,4),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Portfolio performance time series
CREATE TABLE portfolio_performance (
    id SERIAL PRIMARY KEY,
    portfolio_id VARCHAR(50) REFERENCES portfolios(id),
    date DATE NOT NULL,
    total_value DECIMAL(15,2) NOT NULL,
    daily_return DECIMAL(8,4),
    cumulative_return DECIMAL(8,4),
    allocation_snapshot JSONB,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    UNIQUE(portfolio_id, date)
);
```

### **Indexes for Performance**

```sql
-- Performance indexes
CREATE INDEX idx_portfolios_user_id ON portfolios(user_id);
CREATE INDEX idx_portfolios_status ON portfolios(status);
CREATE INDEX idx_portfolio_holdings_portfolio_id ON portfolio_holdings(portfolio_id);
CREATE INDEX idx_portfolio_performance_portfolio_date ON portfolio_performance(portfolio_id, date);
CREATE INDEX idx_portfolio_performance_date ON portfolio_performance(date);
```

## 🔧 **API Endpoints**

### **Portfolio Management**

```python
# List all portfolios for a user
GET /api/v1/portfolios
Query Parameters:
  - user_id: str (optional, defaults to current user)
  - status: str (optional, filter by status)
  - limit: int (optional, pagination)
  - offset: int (optional, pagination)

Response:
{
  "portfolios": [
    {
      "id": "portfolio_123",
      "name": "Conservative Growth",
      "description": "Low-risk portfolio",
      "value": 125000,
      "change": 2500,
      "changePercent": 2.04,
      "allocation": {"Bonds": 0.6, "Stocks": 0.3, "Cash": 0.1},
      "riskLevel": "Low",
      "status": "Active",
      "createdAt": "2025-01-15T10:30:00Z",
      "updatedAt": "2025-01-15T10:30:00Z"
    }
  ],
  "total": 1,
  "limit": 10,
  "offset": 0
}

# Get specific portfolio
GET /api/v1/portfolios/{portfolio_id}
Response:
{
  "portfolio": { /* portfolio object */ },
  "holdings": [ /* portfolio holdings */ ],
  "performance": [ /* recent performance data */ ]
}

# Create portfolio directly
POST /api/v1/portfolios/create-direct
Request Body:
{
  "name": "My Portfolio",
  "description": "Portfolio description",
  "allocation": {"AAPL": 0.3, "MSFT": 0.2, "Cash": 0.5},
  "risk_level": "Medium",
  "user_id": "user_123"
}
Response:
{
  "portfolio": { /* created portfolio */ },
  "message": "Portfolio created successfully"
}

# Update portfolio
PUT /api/v1/portfolios/{portfolio_id}
Request Body:
{
  "name": "Updated Name",
  "description": "Updated description",
  "allocation": { /* updated allocation */ }
}

# Delete portfolio
DELETE /api/v1/portfolios/{portfolio_id}
Response:
{
  "message": "Portfolio deleted successfully"
}
```

### **Portfolio Analytics**

```python
# Get portfolio performance history
GET /api/v1/portfolios/{portfolio_id}/performance
Query Parameters:
  - start_date: str (ISO date)
  - end_date: str (ISO date)
  - frequency: str (daily, weekly, monthly)

# Get portfolio analytics
GET /api/v1/portfolios/{portfolio_id}/analytics
Response:
{
  "totalReturn": 12.5,
  "annualizedReturn": 8.3,
  "volatility": 15.2,
  "sharpeRatio": 0.55,
  "maxDrawdown": -8.7,
  "assetAllocation": { /* breakdown by asset class */ },
  "sectorAllocation": { /* breakdown by sector */ },
  "regionAllocation": { /* breakdown by region */ }
}
```

## 🏛️ **Service Layer Architecture**

### **PortfolioService**

```python
class PortfolioService:
    def __init__(self, db: Session):
        self.db = db

    def get_portfolios(self, user_id: str, status: str = None) -> List[Portfolio]:
        """Get portfolios for a user with optional status filter"""

    def get_portfolio(self, portfolio_id: str) -> Optional[Portfolio]:
        """Get specific portfolio by ID"""

    def create_portfolio_direct(self, **kwargs) -> Portfolio:
        """Create portfolio directly without workflow"""

    def update_portfolio(self, portfolio_id: str, **kwargs) -> Portfolio:
        """Update portfolio properties"""

    def delete_portfolio(self, portfolio_id: str) -> bool:
        """Delete portfolio and related data"""

    def calculate_portfolio_value(self, portfolio_id: str) -> float:
        """Calculate current portfolio value"""

    def update_portfolio_performance(self, portfolio_id: str) -> None:
        """Update portfolio performance metrics"""
```

### **PortfolioAnalyticsService**

```python
class PortfolioAnalyticsService:
    def __init__(self, db: Session):
        self.db = db

    def get_performance_history(self, portfolio_id: str, **filters) -> List[dict]:
        """Get historical performance data"""

    def calculate_returns(self, portfolio_id: str) -> dict:
        """Calculate various return metrics"""

    def calculate_risk_metrics(self, portfolio_id: str) -> dict:
        """Calculate risk metrics (volatility, Sharpe ratio, etc.)"""

    def get_allocation_breakdown(self, portfolio_id: str) -> dict:
        """Get allocation breakdown by various dimensions"""
```

## 🎨 **Frontend Architecture**

### **Component Structure**

```
src/components/portfolio/
├── PortfolioList.tsx              # Main portfolio listing
├── PortfolioCreationWizard.tsx    # Portfolio creation flow
├── PortfolioTemplateConfirmation.tsx  # Template confirmation
├── PortfolioDetail.tsx            # Individual portfolio view
├── PortfolioAnalytics.tsx         # Analytics and charts
├── PortfolioHoldings.tsx          # Holdings table
└── PortfolioPerformance.tsx       # Performance charts
```

### **State Management**

```typescript
// Portfolio context for global state
interface PortfolioContextType {
  portfolios: Portfolio[];
  selectedPortfolio: Portfolio | null;
  loading: boolean;
  error: string | null;

  // Actions
  loadPortfolios: () => Promise<void>;
  createPortfolio: (data: CreatePortfolioData) => Promise<void>;
  updatePortfolio: (id: string, data: UpdatePortfolioData) => Promise<void>;
  deletePortfolio: (id: string) => Promise<void>;
  selectPortfolio: (portfolio: Portfolio) => void;
}
```

### **API Client**

```typescript
class PortfolioApiClient {
  private baseUrl: string;

  async getPortfolios(userId?: string): Promise<Portfolio[]>;
  async getPortfolio(id: string): Promise<Portfolio>;
  async createPortfolioDirect(data: CreatePortfolioData): Promise<Portfolio>;
  async updatePortfolio(id: string, data: UpdatePortfolioData): Promise<Portfolio>;
  async deletePortfolio(id: string): Promise<void>;
  async getPortfolioPerformance(id: string, filters?: PerformanceFilters): Promise<PerformanceData[]>;
  async getPortfolioAnalytics(id: string): Promise<AnalyticsData>;
}
```

## 🔄 **Data Flow**

### **Portfolio Creation Flow**

1. **User Action**: User clicks "Create New Portfolio"
2. **Template Selection**: User selects from available templates
3. **Confirmation**: User reviews and customizes allocation
4. **Validation**: System validates allocation (sums to 100%, valid assets)
5. **Database Insert**: Portfolio created in database
6. **UI Update**: Portfolio list refreshed with new portfolio

### **Portfolio Value Update Flow**

1. **Market Data Update**: ETL pipeline updates market prices
2. **Trigger**: Portfolio value calculation triggered
3. **Calculation**: Service calculates new portfolio value
4. **Database Update**: Portfolio value and performance updated
5. **UI Refresh**: Frontend displays updated values

## 🛡️ **Security Considerations**

### **Data Protection**
- All portfolio data encrypted at rest
- API endpoints require authentication
- User can only access their own portfolios
- Input validation on all user inputs

### **Access Control**
```python
# Example authorization check
def get_portfolio(portfolio_id: str, user_id: str, db: Session):
    portfolio = db.query(Portfolio).filter(
        Portfolio.id == portfolio_id,
        Portfolio.user_id == user_id
    ).first()

    if not portfolio:
        raise HTTPException(status_code=404, detail="Portfolio not found")

    return portfolio
```

## 📊 **Performance Optimization**

### **Database Optimization**
- Indexed queries for fast portfolio retrieval
- Pagination for large portfolio lists
- Connection pooling for database connections
- Query optimization for analytics calculations

### **Caching Strategy**
- Redis cache for frequently accessed portfolio data
- Cache invalidation on portfolio updates
- CDN for static assets and charts

### **Frontend Optimization**
- Lazy loading for portfolio components
- Virtual scrolling for large lists
- Memoization for expensive calculations
- Code splitting for better bundle sizes

## 🧪 **Testing Strategy**

### **Unit Tests**
- Service layer business logic
- API endpoint validation
- Database model operations
- Frontend component rendering

### **Integration Tests**
- API endpoint integration
- Database integration
- Frontend-backend integration
- Third-party service integration

### **End-to-End Tests**
- Complete portfolio creation flow
- Portfolio management workflows
- Performance calculation accuracy
- User interface functionality

## 🚀 **Deployment Considerations**

### **Environment Configuration**
- Database connection strings
- API keys for market data
- Redis configuration
- Logging levels

### **Monitoring**
- Portfolio creation success rates
- API response times
- Database query performance
- Error rates and types

### **Scaling**
- Horizontal scaling for API services
- Database read replicas for analytics
- CDN for static assets
- Load balancing for high availability

---

*This technical documentation provides the implementation details for the Portfolio Management module.*
