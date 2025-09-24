# Authentication System Implementation Plan
## InvestByYourself Financial Platform

**Date**: January 21, 2025
**Priority**: Medium (Tech-036)
**Timeline**: Weeks 20-22
**Status**: Planning Phase

---

## 🚨 **Current Issue**

The authentication system is **not functional** - all database lookup methods in `api/src/services/auth_service.py` return `None`:

```python
def authenticate_user(self, email: str, password: str) -> Optional[UserInDB]:
    # TODO: Replace with actual database lookup
    # For now, return None to indicate authentication failed
    logger.warning(f"Authentication attempt for {email} - database not implemented")
    return None

def get_user_by_email(self, email: str) -> Optional[UserInDB]:
    # TODO: Replace with actual database lookup
    logger.warning(f"User lookup for {email} - database not implemented")
    return None
```

**Impact**: Users cannot register, login, or access personalized features.

---

## 🎯 **Implementation Plan**

### **Phase 1: Database Integration (Week 20)**

#### **1.1 Create User Management Tables**
- [ ] Design user table schema in `database/schema.sql`
- [ ] Add user-related tables:
  - `users` - Core user information
  - `user_sessions` - Active sessions
  - `password_resets` - Password reset tokens
- [ ] Create migration script for user tables

#### **1.2 Update Database Models**
- [ ] Add SQLAlchemy models in `api/src/models/database.py`
- [ ] Create `User` model with proper relationships
- [ ] Add database service methods in `api/src/services/db_service.py`

#### **1.3 Connect AuthService to Database**
- [ ] Replace `None` returns with actual database queries
- [ ] Implement `authenticate_user()` method
- [ ] Implement `get_user_by_email()` method
- [ ] Implement `get_user_by_id()` method
- [ ] Add user creation and update methods

### **Phase 2: Authentication Endpoints (Week 21)**

#### **2.1 User Registration**
- [ ] Implement `/api/v1/auth/register` endpoint
- [ ] Add email validation and password strength requirements
- [ ] Hash passwords using bcrypt
- [ ] Return JWT tokens on successful registration

#### **2.2 User Login**
- [ ] Implement `/api/v1/auth/login` endpoint
- [ ] Validate credentials against database
- [ ] Generate JWT access and refresh tokens
- [ ] Handle login failures gracefully

#### **2.3 Token Management**
- [ ] Implement `/api/v1/auth/refresh` endpoint
- [ ] Add token validation middleware
- [ ] Handle token expiration and renewal
- [ ] Add logout functionality

### **Phase 3: Frontend Integration (Week 22)**

#### **3.1 Authentication Context**
- [ ] Create React context for user authentication
- [ ] Add login/logout state management
- [ ] Implement token storage (localStorage/sessionStorage)
- [ ] Add automatic token refresh logic

#### **3.2 Protected Routes**
- [ ] Add authentication guards to protected pages
- [ ] Redirect unauthenticated users to login
- [ ] Show user information in dashboard
- [ ] Add logout functionality to UI

#### **3.3 API Client Updates**
- [ ] Add authentication headers to API requests
- [ ] Handle 401 responses (token expired)
- [ ] Implement automatic token refresh
- [ ] Add user context to API calls

---

## 🔧 **Technical Implementation Details**

### **Database Schema**

```sql
-- Users table
CREATE TABLE users (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    email VARCHAR(255) UNIQUE NOT NULL,
    username VARCHAR(100) UNIQUE NOT NULL,
    hashed_password VARCHAR(255) NOT NULL,
    first_name VARCHAR(100),
    last_name VARCHAR(100),
    is_active BOOLEAN DEFAULT TRUE,
    is_verified BOOLEAN DEFAULT FALSE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- User sessions table
CREATE TABLE user_sessions (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id INTEGER NOT NULL,
    session_token VARCHAR(255) UNIQUE NOT NULL,
    expires_at TIMESTAMP NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE
);
```

### **JWT Token Configuration**

```python
# JWT settings
JWT_SECRET_KEY = "your-secret-key"
JWT_ALGORITHM = "HS256"
JWT_ACCESS_TOKEN_EXPIRE_MINUTES = 30
JWT_REFRESH_TOKEN_EXPIRE_DAYS = 7
```

### **API Endpoints**

```
POST /api/v1/auth/register
POST /api/v1/auth/login
POST /api/v1/auth/refresh
POST /api/v1/auth/logout
GET  /api/v1/auth/me
```

---

## 🧪 **Testing Strategy**

### **Unit Tests**
- [ ] Test user registration with valid/invalid data
- [ ] Test user login with correct/incorrect credentials
- [ ] Test JWT token generation and validation
- [ ] Test password hashing and verification

### **Integration Tests**
- [ ] Test complete registration flow
- [ ] Test complete login flow
- [ ] Test token refresh flow
- [ ] Test protected endpoint access

### **End-to-End Tests**
- [ ] Test user can register and login via frontend
- [ ] Test user can access protected pages
- [ ] Test user can logout and lose access
- [ ] Test token expiration handling

---

## 📋 **Dependencies**

- **Database**: SQLite (already available)
- **Backend**: FastAPI + SQLAlchemy (already available)
- **Frontend**: Next.js + React (already available)
- **Security**: JWT + bcrypt (already available)

---

## ⚠️ **Risk Assessment**

- **Risk Level**: Medium
- **Potential Issues**:
  - Database migration complexity
  - JWT token security considerations
  - Frontend state management complexity
- **Mitigation**:
  - Incremental implementation
  - Comprehensive testing
  - Security best practices

---

## 🎯 **Success Criteria**

- [ ] Users can register with email and password
- [ ] Users can login and receive JWT tokens
- [ ] Users can access protected pages
- [ ] Tokens refresh automatically
- [ ] Users can logout and lose access
- [ ] All authentication flows work end-to-end

---

**Document Version**: 1.0
**Last Updated**: January 21, 2025
**Next Review**: Before implementation start
**Maintained By**: Development Team
