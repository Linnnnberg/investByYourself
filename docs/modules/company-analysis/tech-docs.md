# Company Analysis - Technical Documentation

## 🏗️ **Architecture Overview**

The Company Analysis module provides comprehensive financial data analysis with a focus on performance, scalability, and data accuracy.

## 🗄️ **Database Schema**

### **Core Tables**

```sql
-- Company master table
CREATE TABLE companies (
    id VARCHAR(50) PRIMARY KEY,
    symbol VARCHAR(20) UNIQUE NOT NULL,
    name VARCHAR(255) NOT NULL,
    sector VARCHAR(100),
    industry VARCHAR(100),
    market_cap BIGINT,
    description TEXT,
    website VARCHAR(255),
    headquarters VARCHAR(255),
    founded_year INTEGER,
    employee_count INTEGER,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Financial ratios table
CREATE TABLE financial_ratios (
    id SERIAL PRIMARY KEY,
    company_id VARCHAR(50) REFERENCES companies(id),
    ratio_name VARCHAR(100) NOT NULL,
    ratio_value DECIMAL(15,6),
    ratio_category VARCHAR(50),
    period VARCHAR(20),
    calculation_date DATE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Market data table
CREATE TABLE market_data (
    id SERIAL PRIMARY KEY,
    company_id VARCHAR(50) REFERENCES companies(id),
    date DATE NOT NULL,
    open_price DECIMAL(10,4),
    high_price DECIMAL(10,4),
    low_price DECIMAL(10,4),
    close_price DECIMAL(10,4),
    volume BIGINT,
    adjusted_close DECIMAL(10,4),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    UNIQUE(company_id, date)
);

-- Financial statements
CREATE TABLE financial_statements (
    id SERIAL PRIMARY KEY,
    company_id VARCHAR(50) REFERENCES companies(id),
    statement_type VARCHAR(50) NOT NULL, -- 'income', 'balance', 'cashflow'
    period VARCHAR(20) NOT NULL,
    fiscal_year INTEGER,
    fiscal_quarter INTEGER,
    data JSONB NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Sectors table
CREATE TABLE sectors (
    id SERIAL PRIMARY KEY,
    name VARCHAR(100) UNIQUE NOT NULL,
    description TEXT,
    parent_sector_id INTEGER REFERENCES sectors(id),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
```

### **Indexes for Performance**

```sql
-- Performance indexes
CREATE INDEX idx_companies_symbol ON companies(symbol);
CREATE INDEX idx_companies_sector ON companies(sector);
CREATE INDEX idx_financial_ratios_company ON financial_ratios(company_id);
CREATE INDEX idx_financial_ratios_category ON financial_ratios(ratio_category);
CREATE INDEX idx_market_data_company_date ON market_data(company_id, date);
CREATE INDEX idx_financial_statements_company ON financial_statements(company_id);
```

## 🔧 **API Endpoints**

### **Company Management**

```python
# List all companies
GET /api/v1/companies
Query Parameters:
  - sector: str (optional, filter by sector)
  - industry: str (optional, filter by industry)
  - limit: int (optional, pagination)
  - offset: int (optional, pagination)
  - search: str (optional, search by name or symbol)

Response:
{
  "companies": [
    {
      "id": "company_123",
      "symbol": "AAPL",
      "name": "Apple Inc.",
      "sector": "Technology",
      "industry": "Consumer Electronics",
      "marketCap": 3000000000000,
      "description": "Technology company...",
      "website": "https://apple.com",
      "headquarters": "Cupertino, CA",
      "foundedYear": 1976,
      "employeeCount": 164000
    }
  ],
  "total": 35,
  "limit": 10,
  "offset": 0
}

# Get specific company
GET /api/v1/companies/{company_id}
Response:
{
  "company": { /* company object */ },
  "ratios": [ /* financial ratios */ ],
  "marketData": [ /* recent market data */ ],
  "statements": [ /* financial statements */ ]
}

# Get company financial ratios
GET /api/v1/companies/{company_id}/ratios
Query Parameters:
  - category: str (optional, filter by ratio category)
  - period: str (optional, filter by period)

# Get company market data
GET /api/v1/companies/{company_id}/market-data
Query Parameters:
  - start_date: str (ISO date)
  - end_date: str (ISO date)
  - frequency: str (daily, weekly, monthly)
```

### **Sector Analysis**

```python
# List all sectors
GET /api/v1/sectors
Response:
{
  "sectors": [
    {
      "id": 1,
      "name": "Technology",
      "description": "Technology companies...",
      "companyCount": 8
    }
  ]
}

# Get sector companies
GET /api/v1/sectors/{sector_id}/companies
Response:
{
  "sector": { /* sector object */ },
  "companies": [ /* companies in sector */ ],
  "benchmarks": { /* sector benchmark ratios */ }
}

# Compare companies in sector
GET /api/v1/sectors/{sector_id}/compare
Query Parameters:
  - company_ids: str (comma-separated company IDs)
  - ratios: str (comma-separated ratio names)
```

### **Financial Analysis**

```python
# Get ratio analysis
GET /api/v1/analysis/ratios
Query Parameters:
  - company_ids: str (comma-separated company IDs)
  - ratio_names: str (comma-separated ratio names)
  - benchmark: str (optional, benchmark company)

# Get sector benchmarks
GET /api/v1/analysis/sector-benchmarks
Query Parameters:
  - sector_id: int
  - ratio_names: str (comma-separated ratio names)

# Get company comparison
GET /api/v1/analysis/compare
Query Parameters:
  - company_ids: str (comma-separated company IDs)
  - metrics: str (comma-separated metric names)
```

## 🏛️ **Service Layer Architecture**

### **CompanyService**

```python
class CompanyService:
    def __init__(self, db: Session):
        self.db = db

    def get_companies(self, filters: dict = None) -> List[Company]:
        """Get companies with optional filters"""

    def get_company(self, company_id: str) -> Optional[Company]:
        """Get specific company by ID"""

    def search_companies(self, query: str) -> List[Company]:
        """Search companies by name or symbol"""

    def get_company_ratios(self, company_id: str, filters: dict = None) -> List[FinancialRatio]:
        """Get financial ratios for a company"""

    def get_company_market_data(self, company_id: str, filters: dict = None) -> List[MarketData]:
        """Get market data for a company"""
```

### **FinancialAnalysisService**

```python
class FinancialAnalysisService:
    def __init__(self, db: Session):
        self.db = db

    def calculate_ratios(self, company_id: str) -> List[FinancialRatio]:
        """Calculate financial ratios for a company"""

    def get_sector_benchmarks(self, sector_id: int) -> dict:
        """Get sector benchmark ratios"""

    def compare_companies(self, company_ids: List[str], ratios: List[str]) -> dict:
        """Compare companies across selected ratios"""

    def get_ratio_trends(self, company_id: str, ratio_name: str) -> List[dict]:
        """Get historical trends for a specific ratio"""
```

### **MarketDataService**

```python
class MarketDataService:
    def __init__(self, db: Session):
        self.db = db

    def update_market_data(self, company_id: str, data: dict) -> None:
        """Update market data for a company"""

    def get_price_history(self, company_id: str, period: str) -> List[dict]:
        """Get price history for a company"""

    def calculate_returns(self, company_id: str, period: str) -> dict:
        """Calculate returns for a company"""
```

## 🎨 **Frontend Architecture**

### **Component Structure**

```
src/components/company-analysis/
├── CompanyList.tsx              # Company listing and search
├── CompanyProfile.tsx           # Individual company view
├── FinancialRatios.tsx          # Ratio analysis and display
├── MarketData.tsx               # Market data and charts
├── SectorAnalysis.tsx           # Sector comparison
├── CompanyComparison.tsx        # Side-by-side comparison
└── RatioAnalysis.tsx            # Ratio analysis tools
```

### **State Management**

```typescript
// Company analysis context
interface CompanyAnalysisContextType {
  companies: Company[];
  selectedCompany: Company | null;
  ratios: FinancialRatio[];
  marketData: MarketData[];
  loading: boolean;
  error: string | null;

  // Actions
  loadCompanies: (filters?: CompanyFilters) => Promise<void>;
  selectCompany: (company: Company) => void;
  loadRatios: (companyId: string) => Promise<void>;
  loadMarketData: (companyId: string) => Promise<void>;
  compareCompanies: (companyIds: string[]) => Promise<void>;
}
```

### **API Client**

```typescript
class CompanyAnalysisApiClient {
  private baseUrl: string;

  async getCompanies(filters?: CompanyFilters): Promise<Company[]>;
  async getCompany(id: string): Promise<Company>;
  async getCompanyRatios(id: string, filters?: RatioFilters): Promise<FinancialRatio[]>;
  async getCompanyMarketData(id: string, filters?: MarketDataFilters): Promise<MarketData[]>;
  async getSectors(): Promise<Sector[]>;
  async getSectorCompanies(sectorId: number): Promise<Company[]>;
  async compareCompanies(companyIds: string[], ratios: string[]): Promise<ComparisonData>;
}
```

## 🔄 **Data Flow**

### **Company Data Loading Flow**

1. **User Action**: User searches or selects company
2. **API Request**: Frontend requests company data
3. **Database Query**: Service queries company and related data
4. **Data Processing**: Service processes and formats data
5. **Response**: API returns formatted company data
6. **UI Update**: Frontend displays company information

### **Ratio Analysis Flow**

1. **Ratio Selection**: User selects ratios to analyze
2. **Data Retrieval**: Service retrieves ratio data from database
3. **Calculation**: Service calculates additional derived ratios
4. **Comparison**: Service compares with sector benchmarks
5. **Visualization**: Frontend displays ratios in charts/tables

## 🛡️ **Security Considerations**

### **Data Protection**
- All financial data encrypted at rest
- API endpoints require authentication
- Rate limiting on data-intensive endpoints
- Input validation on all user inputs

### **Access Control**
```python
# Example authorization check
def get_company(company_id: str, db: Session):
    company = db.query(Company).filter(Company.id == company_id).first()

    if not company:
        raise HTTPException(status_code=404, detail="Company not found")

    return company
```

## 📊 **Performance Optimization**

### **Database Optimization**
- Indexed queries for fast company retrieval
- Materialized views for complex ratio calculations
- Connection pooling for database connections
- Query optimization for analytics

### **Caching Strategy**
- Redis cache for frequently accessed company data
- Cache invalidation on data updates
- CDN for static financial charts
- Browser caching for ratio calculations

### **Frontend Optimization**
- Lazy loading for company components
- Virtual scrolling for large company lists
- Memoization for expensive calculations
- Code splitting for better bundle sizes

## 🧪 **Testing Strategy**

### **Unit Tests**
- Service layer business logic
- API endpoint validation
- Database model operations
- Financial calculation accuracy

### **Integration Tests**
- API endpoint integration
- Database integration
- Frontend-backend integration
- Market data integration

### **End-to-End Tests**
- Complete company research flow
- Ratio analysis workflows
- Sector comparison functionality
- Data accuracy validation

## 🚀 **Deployment Considerations**

### **Environment Configuration**
- Database connection strings
- Market data API keys
- Redis configuration
- Logging levels

### **Monitoring**
- Company data accuracy
- API response times
- Database query performance
- Market data update success rates

### **Scaling**
- Horizontal scaling for API services
- Database read replicas for analytics
- CDN for static assets
- Load balancing for high availability

---

*This technical documentation provides the implementation details for the Company Analysis module.*
