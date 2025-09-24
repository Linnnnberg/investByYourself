# Frontend-Backend Integration Plan
**Tech-028.1: FastAPI Backend Integration**

## 🎯 **Overview**

This document outlines the plan to integrate the Next.js frontend with the FastAPI backend, replacing the current Supabase service calls with direct FastAPI API calls.

## 🚨 **Current Problem**

- **Frontend**: Using Supabase services (`supabase.from('portfolios').select('*')`)
- **Backend**: FastAPI serving endpoints at `/api/v1/portfolio/`
- **Result**: 404 errors, no data loading in dashboard

## 🎯 **Solution: Hybrid Architecture**

### **Architecture Decision**
- **FastAPI Backend**: Core business logic, portfolio management, analysis
- **Supabase Auth**: User authentication and session management (free tier)
- **SQLite Database**: Development and production data storage

### **Cost Comparison**
| Approach | Development | Production | Total Monthly |
|----------|-------------|------------|---------------|
| **Supabase Only** | $0 | $25+ | $25+ |
| **FastAPI Only** | $0 | $10-20 | $10-20 |
| **Hybrid (Recommended)** | $0 | $15-25 | $15-25 |

## 📋 **Implementation Plan**

### **Phase 1: Service Layer Creation (Day 1)**

#### **1.1 Create API Client**
```typescript
// frontend/src/lib/api-client.ts
class ApiClient {
  private baseURL = 'http://localhost:8000/api/v1'
  private authToken?: string

  constructor(authToken?: string) {
    this.authToken = authToken
  }

  private async request<T>(endpoint: string, options?: RequestInit): Promise<T> {
    const url = `${this.baseURL}${endpoint}`
    const headers = {
      'Content-Type': 'application/json',
      ...(this.authToken && { Authorization: `Bearer ${this.authToken}` }),
      ...options?.headers,
    }

    const response = await fetch(url, { ...options, headers })

    if (!response.ok) {
      throw new ApiError(response.status, await response.text())
    }

    return response.json()
  }
}
```

#### **1.2 Portfolio Endpoints**
```typescript
// Portfolio management
async getPortfolios(): Promise<PortfolioSummary[]>
async getPortfolio(id: number): Promise<PortfolioDetail>
async createPortfolio(data: PortfolioCreate): Promise<Portfolio>
async updatePortfolio(id: number, data: PortfolioUpdate): Promise<Portfolio>
async deletePortfolio(id: number): Promise<void>

// Holdings management
async getHoldings(portfolioId: number): Promise<Holding[]>
async addHolding(portfolioId: number, data: HoldingCreate): Promise<Holding>
async updateHolding(portfolioId: number, holdingId: number, data: HoldingUpdate): Promise<Holding>
async removeHolding(portfolioId: number, holdingId: number): Promise<void>

// Analytics
async getPortfolioAnalytics(portfolioId: number): Promise<PortfolioAnalytics>
```

#### **1.3 Investment Profile Endpoints**
```typescript
// Profile management
async getProfiles(): Promise<InvestmentProfile[]>
async getProfile(id: number): Promise<InvestmentProfile>
async createProfile(data: ProfileCreate): Promise<InvestmentProfile>
async updateProfile(id: number, data: ProfileUpdate): Promise<InvestmentProfile>
async deleteProfile(id: number): Promise<void>

// Assessment
async getAssessment(): Promise<ProfileQuestion[]>
async calculateRiskScore(answers: ProfileAnswer[]): Promise<RiskScore>
async getRecommendations(profileId: number): Promise<InvestmentRecommendation[]>
```

### **Phase 2: Frontend Integration (Day 1-2)**

#### **2.1 Dashboard Integration**
```typescript
// frontend/src/app/(dashboard)/dashboard/page.tsx
// Before:
const portfoliosData = await services.portfolios.getUserPortfolios(DEMO_USER_ID)

// After:
const apiClient = new ApiClient(authToken)
const portfoliosData = await apiClient.getPortfolios()
```

#### **2.2 Portfolio Page Integration**
```typescript
// frontend/src/app/(dashboard)/portfolio/page.tsx
// Replace all Supabase calls with FastAPI calls
const portfolios = await apiClient.getPortfolios()
const portfolio = await apiClient.getPortfolio(portfolioId)
const holdings = await apiClient.getHoldings(portfolioId)
```

#### **2.3 Investment Profile Integration**
```typescript
// frontend/src/app/(dashboard)/investment-profile/page.tsx
// Replace Supabase calls with FastAPI calls
const questions = await apiClient.getAssessment()
const profile = await apiClient.createProfile(profileData)
const recommendations = await apiClient.getRecommendations(profileId)
```

### **Phase 3: Authentication Integration (Day 2)**

#### **3.1 JWT Token Management**
```typescript
// frontend/src/lib/auth.ts
export async function getApiClient(): Promise<ApiClient> {
  const { data: { session } } = await supabase.auth.getSession()
  return new ApiClient(session?.access_token)
}
```

#### **3.2 FastAPI JWT Validation**
```python
# api/src/core/auth.py
from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
import jwt

security = HTTPBearer()

async def get_current_user(credentials: HTTPAuthorizationCredentials = Depends(security)):
    try:
        # Validate Supabase JWT
        payload = jwt.decode(credentials.credentials, verify=False)  # Supabase handles validation
        user_id = payload.get("sub")
        if user_id is None:
            raise HTTPException(status_code=401, detail="Invalid token")
        return {"id": user_id, "email": payload.get("email")}
    except jwt.PyJWTError:
        raise HTTPException(status_code=401, detail="Invalid token")
```

### **Phase 4: Testing & Validation (Day 2)**

#### **4.1 End-to-End Testing**
- [ ] Test portfolio CRUD operations
- [ ] Test investment profile assessment flow
- [ ] Test error handling and edge cases
- [ ] Validate data consistency

#### **4.2 Error Handling**
```typescript
// Centralized error handling
try {
  const portfolios = await apiClient.getPortfolios()
} catch (error) {
  if (error.status === 401) {
    // Redirect to login
    router.push('/login')
  } else if (error.status === 404) {
    // Show empty state
    setPortfolios([])
  } else {
    // Show generic error
    setError('Failed to load portfolios')
  }
}
```

## 🔧 **Technical Specifications**

### **API Endpoint Mapping**

| Frontend Call | FastAPI Endpoint | Method | Description |
|---------------|------------------|--------|-------------|
| `getPortfolios()` | `/api/v1/portfolio/` | GET | List user portfolios |
| `getPortfolio(id)` | `/api/v1/portfolio/{id}` | GET | Get portfolio details |
| `createPortfolio(data)` | `/api/v1/portfolio/` | POST | Create new portfolio |
| `updatePortfolio(id, data)` | `/api/v1/portfolio/{id}` | PUT | Update portfolio |
| `deletePortfolio(id)` | `/api/v1/portfolio/{id}` | DELETE | Delete portfolio |
| `getHoldings(portfolioId)` | `/api/v1/portfolio/{id}/holdings` | GET | Get portfolio holdings |
| `addHolding(portfolioId, data)` | `/api/v1/portfolio/{id}/holdings` | POST | Add holding |
| `getProfiles()` | `/api/v1/investment-profile/profiles` | GET | List user profiles |
| `getAssessment()` | `/api/v1/investment-profile/assessment` | GET | Get assessment questions |
| `createProfile(data)` | `/api/v1/investment-profile/profiles` | POST | Create profile |

### **TypeScript Interfaces**

```typescript
// frontend/src/types/api.ts
export interface Portfolio {
  id: number
  name: string
  description?: string
  risk_profile: RiskProfile
  total_value: string
  total_cost: string
  total_gain_loss: string
  total_gain_loss_pct: string
  holdings_count: number
  last_updated: string
}

export interface InvestmentProfile {
  id: number
  user_id: string
  risk_score: number
  risk_level: RiskLevel
  investment_style: InvestmentStyle
  time_horizon: TimeHorizon
  created_at: string
  updated_at: string
}

export interface ProfileQuestion {
  id: number
  dimension: string
  question: string
  options: Array<{
    value: number
    text: string
  }>
}
```

## 🚀 **Success Criteria**

- [ ] All portfolio CRUD operations working
- [ ] Investment profile assessment functional
- [ ] No 404 errors in browser console
- [ ] Data loading correctly in dashboard
- [ ] Error handling working properly
- [ ] Authentication flow integrated
- [ ] End-to-end testing passing

## 📅 **Timeline**

- **Day 1**: Service layer creation and basic integration
- **Day 2**: Authentication integration and testing
- **Total**: 2 days for complete integration

## 🔄 **Rollback Plan**

If issues arise:
1. Keep current Supabase integration as fallback
2. Use feature flags to switch between implementations
3. Gradual migration of endpoints
4. Comprehensive testing before full switch

---

**Status**: Ready for implementation
**Priority**: Immediate (Tech-028.1)
**Dependencies**: Tech-028 ✅ COMPLETED
