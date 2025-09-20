# InvestByYourself API Design Plan
## Tech-027: Comprehensive API Architecture for Frontend Integration

---

## 🎯 **Overview**

This document outlines the comprehensive API design for the InvestByYourself platform, covering all modules and services to support the frontend application. The API follows RESTful principles with GraphQL for complex queries and real-time updates via WebSockets.

---

## 📋 **API Architecture Overview**

### **1. API Gateway Structure**
```
/api/v1/
├── /auth/                    # Authentication & Authorization
├── /portfolio/               # Portfolio Management
├── /market/                  # Market Data & Analysis
├── /watchlist/               # Watchlist Management
├── /analysis/                # Financial Analysis
├── /etl/                     # Data Pipeline Management
├── /user/                    # User Management
├── /notifications/           # Notifications
└── /admin/                   # Admin Functions
```

### **2. Technology Stack**
- **API Gateway**: FastAPI with automatic OpenAPI documentation
- **Authentication**: JWT tokens with refresh mechanism
- **Real-time**: WebSocket connections for live data
- **Caching**: Redis for performance optimization
- **Rate Limiting**: Per-user and per-endpoint limits
- **Monitoring**: Prometheus metrics and health checks

---

## 🔐 **Authentication & Authorization**

### **Base URL**: `/api/v1/auth`

| Endpoint | Method | Description | Request Body | Response |
|----------|--------|-------------|--------------|----------|
| `/login` | POST | User login | `{email, password}` | `{token, refresh_token, user}` |
| `/register` | POST | User registration | `{email, password, name}` | `{token, refresh_token, user}` |
| `/refresh` | POST | Refresh access token | `{refresh_token}` | `{token, refresh_token}` |
| `/logout` | POST | User logout | `{token}` | `{message}` |
| `/forgot-password` | POST | Password reset request | `{email}` | `{message}` |
| `/reset-password` | POST | Reset password | `{token, new_password}` | `{message}` |
| `/verify-email` | POST | Email verification | `{token}` | `{message}` |
| `/profile` | GET | Get user profile | - | `{user}` |
| `/profile` | PUT | Update user profile | `{name, preferences}` | `{user}` |

### **Request/Response Examples**

```typescript
// Login Request
interface LoginRequest {
  email: string;
  password: string;
}

// Login Response
interface LoginResponse {
  token: string;
  refresh_token: string;
  user: User;
  expires_in: number;
}

// User Profile
interface User {
  id: string;
  email: string;
  name: string;
  avatar?: string;
  preferences: UserPreferences;
  created_at: string;
  updated_at: string;
}
```

---

## 💼 **Portfolio Management API**

### **Base URL**: `/api/v1/portfolio`

| Endpoint | Method | Description | Request Body | Response |
|----------|--------|-------------|--------------|----------|
| `/` | GET | Get all portfolios | `?page=1&limit=10` | `PaginatedResponse<Portfolio>` |
| `/` | POST | Create new portfolio | `PortfolioFormData` | `Portfolio` |
| `/{id}` | GET | Get portfolio details | - | `Portfolio` |
| `/{id}` | PUT | Update portfolio | `PortfolioFormData` | `Portfolio` |
| `/{id}` | DELETE | Delete portfolio | - | `{message}` |
| `/{id}/holdings` | GET | Get portfolio holdings | `?page=1&limit=20` | `PaginatedResponse<Holding>` |
| `/{id}/holdings` | POST | Add holding | `TradeFormData` | `Holding` |
| `/{id}/holdings/{symbol}` | PUT | Update holding | `{shares, avg_price}` | `Holding` |
| `/{id}/holdings/{symbol}` | DELETE | Remove holding | - | `{message}` |
| `/{id}/performance` | GET | Get performance metrics | `?timeframe=1Y` | `PerformanceMetrics` |
| `/{id}/allocation` | GET | Get asset allocation | - | `AssetAllocation` |
| `/{id}/transactions` | GET | Get transaction history | `?page=1&limit=50` | `PaginatedResponse<Transaction>` |
| `/{id}/transactions` | POST | Add transaction | `TransactionFormData` | `Transaction` |

### **Data Models**

```typescript
interface Portfolio {
  id: string;
  name: string;
  description?: string;
  user_id: string;
  is_public: boolean;
  total_value: number;
  total_return: number;
  return_percentage: number;
  holdings_count: number;
  created_at: string;
  updated_at: string;
}

interface Holding {
  id: string;
  portfolio_id: string;
  symbol: string;
  shares: number;
  avg_price: number;
  current_price: number;
  total_value: number;
  total_return: number;
  return_percentage: number;
  last_updated: string;
}

interface PerformanceMetrics {
  total_return: number;
  return_percentage: number;
  sharpe_ratio: number;
  max_drawdown: number;
  volatility: number;
  beta: number;
  alpha: number;
  time_period: string;
  benchmark_comparison: BenchmarkComparison;
}

interface AssetAllocation {
  asset_classes: AssetClassAllocation[];
  sectors: SectorAllocation[];
  regions: RegionAllocation[];
  last_updated: string;
}

interface Transaction {
  id: string;
  portfolio_id: string;
  symbol: string;
  action: 'buy' | 'sell';
  shares: number;
  price: number;
  total_amount: number;
  fees: number;
  timestamp: string;
  notes?: string;
}
```

---

## 📊 **Market Data API**

### **Base URL**: `/api/v1/market`

| Endpoint | Method | Description | Request Body | Response |
|----------|--------|-------------|--------------|----------|
| `/indices` | GET | Get market indices | - | `MarketIndex[]` |
| `/sectors` | GET | Get sector performance | - | `SectorPerformance[]` |
| `/news` | GET | Get market news | `?page=1&limit=20` | `PaginatedResponse<MarketNews>` |
| `/news/{id}` | GET | Get news article | - | `MarketNews` |
| `/macro` | GET | Get macroeconomic data | - | `MacroeconomicIndicator[]` |
| `/quote/{symbol}` | GET | Get stock quote | - | `StockQuote` |
| `/quotes` | POST | Get multiple quotes | `{symbols: string[]}` | `StockQuote[]` |
| `/search` | GET | Search stocks | `?q=AAPL&limit=10` | `StockSearchResult[]` |
| `/chart/{symbol}` | GET | Get price chart data | `?timeframe=1M&interval=1d` | `ChartData` |
| `/screener` | POST | Stock screener | `ScreenerCriteria` | `PaginatedResponse<Stock>` |

### **Data Models**

```typescript
interface StockQuote {
  symbol: string;
  name: string;
  price: number;
  change: number;
  change_percentage: number;
  volume: number;
  market_cap: number;
  pe_ratio: number;
  eps: number;
  dividend_yield: number;
  high_52w: number;
  low_52w: number;
  last_updated: string;
}

interface ChartData {
  symbol: string;
  timeframe: string;
  interval: string;
  data: ChartDataPoint[];
  indicators?: TechnicalIndicator[];
}

interface ChartDataPoint {
  timestamp: string;
  open: number;
  high: number;
  low: number;
  close: number;
  volume: number;
}

interface TechnicalIndicator {
  name: string;
  data: IndicatorDataPoint[];
  color?: string;
}

interface ScreenerCriteria {
  market_cap_min?: number;
  market_cap_max?: number;
  pe_ratio_min?: number;
  pe_ratio_max?: number;
  dividend_yield_min?: number;
  price_min?: number;
  price_max?: number;
  sectors?: string[];
  sort_by?: string;
  sort_direction?: 'asc' | 'desc';
  page?: number;
  limit?: number;
}
```

---

## 👀 **Watchlist Management API**

### **Base URL**: `/api/v1/watchlist`

| Endpoint | Method | Description | Request Body | Response |
|----------|--------|-------------|--------------|----------|
| `/` | GET | Get user watchlist | `?page=1&limit=20` | `PaginatedResponse<WatchlistItem>` |
| `/` | POST | Add to watchlist | `{symbol}` | `WatchlistItem` |
| `/{symbol}` | DELETE | Remove from watchlist | - | `{message}` |
| `/alerts` | GET | Get price alerts | - | `PriceAlert[]` |
| `/alerts` | POST | Create price alert | `PriceAlertFormData` | `PriceAlert` |
| `/alerts/{id}` | PUT | Update price alert | `PriceAlertFormData` | `PriceAlert` |
| `/alerts/{id}` | DELETE | Delete price alert | - | `{message}` |

### **Data Models**

```typescript
interface WatchlistItem {
  id: string;
  user_id: string;
  symbol: string;
  name: string;
  current_price: number;
  change: number;
  change_percentage: number;
  added_at: string;
  notes?: string;
}

interface PriceAlert {
  id: string;
  user_id: string;
  symbol: string;
  alert_type: 'price_above' | 'price_below' | 'percentage_change';
  target_value: number;
  is_active: boolean;
  created_at: string;
  triggered_at?: string;
}
```

---

## 📈 **Financial Analysis API**

### **Base URL**: `/api/v1/analysis`

| Endpoint | Method | Description | Request Body | Response |
|----------|--------|-------------|--------------|----------|
| `/technical/{symbol}` | GET | Technical analysis | `?timeframe=1M` | `TechnicalAnalysis` |
| `/fundamental/{symbol}` | GET | Fundamental analysis | - | `FundamentalAnalysis` |
| `/portfolio/{id}/optimize` | POST | Portfolio optimization | `OptimizationParams` | `OptimizationResult` |
| `/backtest` | POST | Strategy backtesting | `BacktestParams` | `BacktestResult` |
| `/risk/{symbol}` | GET | Risk analysis | - | `RiskMetrics` |
| `/correlation` | POST | Correlation analysis | `{symbols: string[]}` | `CorrelationMatrix` |
| `/sector-analysis` | GET | Sector analysis | - | `SectorAnalysis` |

### **Data Models**

```typescript
interface TechnicalAnalysis {
  symbol: string;
  timeframe: string;
  signals: TechnicalSignal[];
  indicators: {
    rsi: number;
    macd: MACDData;
    bollinger_bands: BollingerBands;
    moving_averages: MovingAverage[];
  };
  trend: 'bullish' | 'bearish' | 'neutral';
  confidence: number;
  last_updated: string;
}

interface FundamentalAnalysis {
  symbol: string;
  company_info: CompanyInfo;
  financial_metrics: FinancialMetrics;
  valuation: ValuationMetrics;
  analyst_ratings: AnalystRating[];
  last_updated: string;
}

interface OptimizationResult {
  optimized_weights: {[symbol: string]: number};
  expected_return: number;
  expected_volatility: number;
  sharpe_ratio: number;
  efficient_frontier: EfficientFrontierPoint[];
  constraints_satisfied: boolean;
}

interface BacktestResult {
  strategy_name: string;
  start_date: string;
  end_date: string;
  total_return: number;
  annualized_return: number;
  volatility: number;
  sharpe_ratio: number;
  max_drawdown: number;
  trades: Trade[];
  equity_curve: ChartDataPoint[];
}
```

---

## 🔄 **ETL Pipeline Management API**

### **Base URL**: `/api/v1/etl`

| Endpoint | Method | Description | Request Body | Response |
|----------|--------|-------------|--------------|----------|
| `/status` | GET | Get ETL pipeline status | - | `ETLStatus` |
| `/pipelines` | GET | Get all pipelines | - | `ETLPipeline[]` |
| `/pipelines/{id}` | GET | Get pipeline details | - | `ETLPipeline` |
| `/pipelines/{id}/start` | POST | Start pipeline | - | `{message}` |
| `/pipelines/{id}/stop` | POST | Stop pipeline | - | `{message}` |
| `/pipelines/{id}/logs` | GET | Get pipeline logs | `?page=1&limit=50` | `PaginatedResponse<ETLLog>` |
| `/data-sources` | GET | Get data sources | - | `DataSource[]` |
| `/data-sources/{id}/test` | POST | Test data source | - | `{status, message}` |
| `/jobs` | GET | Get ETL jobs | `?status=running` | `ETLJob[]` |
| `/jobs/{id}` | GET | Get job details | - | `ETLJob` |

### **Data Models**

```typescript
interface ETLPipeline {
  id: string;
  name: string;
  description: string;
  status: 'idle' | 'running' | 'paused' | 'error';
  schedule: string;
  last_run: string;
  next_run: string;
  data_sources: string[];
  transformations: Transformation[];
  destinations: string[];
}

interface ETLJob {
  id: string;
  pipeline_id: string;
  status: 'pending' | 'running' | 'completed' | 'failed';
  start_time: string;
  end_time?: string;
  records_processed: number;
  errors: ETLJobError[];
}

interface DataSource {
  id: string;
  name: string;
  type: 'api' | 'database' | 'file' | 'stream';
  connection_config: any;
  is_active: boolean;
  last_sync: string;
}
```

---

## 🔔 **Notifications API**

### **Base URL**: `/api/v1/notifications`

| Endpoint | Method | Description | Request Body | Response |
|----------|--------|-------------|--------------|----------|
| `/` | GET | Get user notifications | `?page=1&limit=20` | `PaginatedResponse<Notification>` |
| `/{id}` | PUT | Mark as read | - | `{message}` |
| `/mark-all-read` | POST | Mark all as read | - | `{message}` |
| `/preferences` | GET | Get notification preferences | - | `NotificationPreferences` |
| `/preferences` | PUT | Update preferences | `NotificationPreferences` | `{message}` |
| `/subscribe` | POST | Subscribe to notifications | `{type, symbol?}` | `{message}` |
| `/unsubscribe` | POST | Unsubscribe from notifications | `{type, symbol?}` | `{message}` |

### **Data Models**

```typescript
interface Notification {
  id: string;
  user_id: string;
  type: 'price_alert' | 'portfolio_update' | 'market_news' | 'system';
  title: string;
  message: string;
  data?: any;
  is_read: boolean;
  created_at: string;
}

interface NotificationPreferences {
  email_enabled: boolean;
  push_enabled: boolean;
  sms_enabled: boolean;
  frequency: 'immediate' | 'daily' | 'weekly';
  types: {
    price_alerts: boolean;
    portfolio_updates: boolean;
    market_news: boolean;
    system_notifications: boolean;
  };
}
```

---

## 🔌 **WebSocket Real-time API**

### **Connection**: `wss://api.investbyyourself.com/ws`

| Event | Direction | Description | Data |
|-------|-----------|-------------|------|
| `connect` | Client → Server | Establish connection | `{token}` |
| `subscribe` | Client → Server | Subscribe to data stream | `{type, symbol?}` |
| `unsubscribe` | Client → Server | Unsubscribe from stream | `{type, symbol?}` |
| `price_update` | Server → Client | Real-time price updates | `{symbol, price, change}` |
| `portfolio_update` | Server → Client | Portfolio value changes | `{portfolio_id, total_value}` |
| `news_alert` | Server → Client | Breaking news | `{title, summary, impact}` |
| `error` | Server → Client | Error notification | `{code, message}` |

### **Subscription Types**

```typescript
interface SubscriptionRequest {
  type: 'price' | 'portfolio' | 'news' | 'market';
  symbol?: string;
  portfolio_id?: string;
}

interface PriceUpdate {
  symbol: string;
  price: number;
  change: number;
  change_percentage: number;
  volume: number;
  timestamp: string;
}

interface PortfolioUpdate {
  portfolio_id: string;
  total_value: number;
  total_return: number;
  return_percentage: number;
  timestamp: string;
}
```

---

## 📊 **Rate Limiting & Caching**

### **Rate Limits**
- **Authentication**: 5 requests/minute
- **Market Data**: 100 requests/minute
- **Portfolio Operations**: 50 requests/minute
- **Analysis**: 20 requests/minute
- **ETL Operations**: 10 requests/minute

### **Caching Strategy**
- **Market Data**: 1 minute TTL
- **Portfolio Data**: 30 seconds TTL
- **User Data**: 5 minutes TTL
- **Analysis Results**: 1 hour TTL

### **Headers**
```http
X-RateLimit-Limit: 100
X-RateLimit-Remaining: 95
X-RateLimit-Reset: 1640995200
X-Cache-Status: HIT
X-Cache-TTL: 60
```

---

## 🛡️ **Error Handling**

### **Standard Error Response**
```typescript
interface ErrorResponse {
  error: {
    code: string;
    message: string;
    details?: any;
    timestamp: string;
    request_id: string;
  };
}
```

### **Error Codes**
- `AUTH_REQUIRED`: Authentication required
- `AUTH_INVALID`: Invalid credentials
- `RATE_LIMITED`: Rate limit exceeded
- `VALIDATION_ERROR`: Request validation failed
- `NOT_FOUND`: Resource not found
- `PERMISSION_DENIED`: Insufficient permissions
- `INTERNAL_ERROR`: Internal server error
- `SERVICE_UNAVAILABLE`: Service temporarily unavailable

---

## 📚 **API Documentation**

### **OpenAPI Specification**
- **Swagger UI**: `/api/docs`
- **ReDoc**: `/api/redoc`
- **OpenAPI JSON**: `/api/openapi.json`

### **SDK Generation**
- **TypeScript**: Auto-generated from OpenAPI spec
- **Python**: Auto-generated client library
- **JavaScript**: Browser-compatible SDK

---

## 🚀 **Implementation Phases**

### **Phase 1: Core APIs (Weeks 1-2)**
- Authentication & Authorization
- Portfolio Management
- Basic Market Data
- User Management

### **Phase 2: Advanced Features (Weeks 3-4)**
- Financial Analysis
- Watchlist Management
- Real-time WebSocket
- Notifications

### **Phase 3: ETL & Admin (Weeks 5-6)**
- ETL Pipeline Management
- Admin Functions
- Advanced Analytics
- Performance Optimization

### **Phase 4: Production Ready (Weeks 7-8)**
- Security Hardening
- Monitoring & Logging
- Documentation
- SDK Generation

---

## 🔧 **Development Tools**

### **API Testing**
- **Postman Collection**: Complete API test suite
- **Insomnia**: Alternative API client
- **Newman**: Automated testing

### **Monitoring**
- **Health Checks**: `/health` endpoint
- **Metrics**: Prometheus integration
- **Logging**: Structured JSON logs
- **Tracing**: Distributed tracing support

---

This comprehensive API design provides a solid foundation for the InvestByYourself frontend application, ensuring scalability, security, and maintainability while supporting all the required functionality for a professional investment platform.
