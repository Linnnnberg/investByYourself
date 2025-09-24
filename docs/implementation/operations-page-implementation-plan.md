# Operations Page Implementation Plan
## InvestByYourself Financial Platform

**Date**: January 21, 2025
**Priority**: Medium (Story-037)
**Timeline**: Weeks 23-25
**Status**: Planning Phase

---

## 🎯 **Overview**

The Operations Page will be a comprehensive admin interface that provides direct CRUD (Create, Read, Update, Delete) access to all database entities. This will enable administrators and developers to manage data directly through the UI, bypassing the need for direct database access or API testing tools.

---

## 🏗️ **Architecture Design**

### **Page Layout**
```
┌─────────────────────────────────────────────────────────────┐
│                    Operations Dashboard                     │
├─────────────┬───────────────────────────────────────────────┤
│   Sidebar   │                Main Content Area              │
│             │                                               │
│ • Companies │  ┌─────────────────────────────────────────┐  │
│ • Sectors   │  │         Entity Management Panel        │  │
│ • Ratios    │  │                                         │  │
│ • Users     │  │  [Search] [Filter] [Add New] [Export]  │  │
│ • Portfolios│  │                                         │  │
│ • Strategies│  │  ┌─────────────────────────────────┐   │  │
│ • Sessions  │  │  │        Data Table/Grid         │   │  │
│ • Logs      │  │  │                                 │   │  │
│             │  │  │  [Edit] [Delete] [View] [Copy] │   │  │
│             │  │  │                                 │   │  │
│             │  │  └─────────────────────────────────┘   │  │
│             │  │                                         │  │
│             │  │  [Pagination] [Bulk Actions] [Refresh] │  │
│             │  └─────────────────────────────────────────┘  │
└─────────────┴───────────────────────────────────────────────┘
```

### **Sidebar Navigation Structure**
```
📊 Operations
├── 🏢 Companies
│   ├── List All Companies
│   ├── Add New Company
│   ├── Company Categories
│   └── Bulk Import/Export
├── 📈 Financial Data
│   ├── Financial Ratios
│   ├── Market Data
│   ├── Price History
│   └── Sector Data
├── 👥 User Management
│   ├── Users
│   ├── User Sessions
│   ├── User Roles
│   └── Activity Logs
├── 💼 Portfolio Management
│   ├── Portfolios
│   ├── Portfolio Items
│   ├── Investment Profiles
│   └── Strategy Assignments
├── 🔧 System Management
│   ├── Database Status
│   ├── API Logs
│   ├── Error Logs
│   └── Performance Metrics
└── ⚙️ Settings
    ├── System Configuration
    ├── API Keys
    ├── Data Sources
    └── Backup/Restore
```

---

## 🗄️ **Database Entities & CRUD Operations**

### **1. Companies Entity**
```sql
-- Companies table
CREATE TABLE companies (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    symbol VARCHAR(10) UNIQUE NOT NULL,
    name VARCHAR(255) NOT NULL,
    sector VARCHAR(100),
    industry VARCHAR(100),
    market_cap DECIMAL(15,2),
    description TEXT,
    website VARCHAR(255),
    ceo VARCHAR(100),
    founded_year INTEGER,
    employees INTEGER,
    headquarters VARCHAR(255),
    is_active BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
```

**CRUD Operations:**
- **Create**: Add new company with validation
- **Read**: List, search, filter, paginate companies
- **Update**: Edit company details, toggle active status
- **Delete**: Soft delete (set is_active = FALSE)

### **2. Financial Ratios Entity**
```sql
-- Financial ratios table
CREATE TABLE financial_ratios (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    company_id INTEGER NOT NULL,
    ratio_name VARCHAR(100) NOT NULL,
    ratio_value DECIMAL(15,6),
    period_end_date DATE,
    data_source VARCHAR(100),
    confidence_score DECIMAL(3,2),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (company_id) REFERENCES companies(id)
);
```

**CRUD Operations:**
- **Create**: Add new financial ratio data
- **Read**: Filter by company, ratio type, date range
- **Update**: Modify ratio values and metadata
- **Delete**: Remove outdated or incorrect data

### **3. Users Entity**
```sql
-- Users table (for authentication system)
CREATE TABLE users (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    email VARCHAR(255) UNIQUE NOT NULL,
    username VARCHAR(100) UNIQUE NOT NULL,
    hashed_password VARCHAR(255) NOT NULL,
    first_name VARCHAR(100),
    last_name VARCHAR(100),
    role VARCHAR(50) DEFAULT 'user',
    is_active BOOLEAN DEFAULT TRUE,
    is_verified BOOLEAN DEFAULT FALSE,
    last_login TIMESTAMP,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
```

**CRUD Operations:**
- **Create**: Register new users (with password hashing)
- **Read**: List users with role filtering
- **Update**: Edit user details, change roles, reset passwords
- **Delete**: Deactivate users (soft delete)

### **4. Portfolios Entity**
```sql
-- Portfolios table
CREATE TABLE portfolios (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id INTEGER NOT NULL,
    name VARCHAR(255) NOT NULL,
    description TEXT,
    strategy_id INTEGER,
    total_value DECIMAL(15,2),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES users(id),
    FOREIGN KEY (strategy_id) REFERENCES strategies(id)
);
```

**CRUD Operations:**
- **Create**: Create new portfolios for users
- **Read**: List portfolios by user, strategy, or date
- **Update**: Modify portfolio details and holdings
- **Delete**: Remove portfolios (with confirmation)

---

## 🔧 **Technical Implementation**

### **Phase 1: Backend API Development (Week 23)**

#### **1.1 Generic CRUD Service**
```python
# api/src/services/crud_service.py
from typing import Type, TypeVar, Generic, List, Optional, Dict, Any
from sqlalchemy.orm import Session
from sqlalchemy import and_, or_

T = TypeVar('T')

class CRUDService(Generic[T]):
    def __init__(self, model: Type[T]):
        self.model = model

    def create(self, db: Session, obj_in: Dict[str, Any]) -> T:
        """Create a new record"""
        db_obj = self.model(**obj_in)
        db.add(db_obj)
        db.commit()
        db.refresh(db_obj)
        return db_obj

    def get(self, db: Session, id: int) -> Optional[T]:
        """Get a single record by ID"""
        return db.query(self.model).filter(self.model.id == id).first()

    def get_multi(self, db: Session, skip: int = 0, limit: int = 100,
                  filters: Dict[str, Any] = None) -> List[T]:
        """Get multiple records with pagination and filtering"""
        query = db.query(self.model)
        if filters:
            for key, value in filters.items():
                if hasattr(self.model, key):
                    query = query.filter(getattr(self.model, key) == value)
        return query.offset(skip).limit(limit).all()

    def update(self, db: Session, id: int, obj_in: Dict[str, Any]) -> Optional[T]:
        """Update a record"""
        db_obj = self.get(db, id)
        if db_obj:
            for key, value in obj_in.items():
                if hasattr(db_obj, key):
                    setattr(db_obj, key, value)
            db.commit()
            db.refresh(db_obj)
        return db_obj

    def delete(self, db: Session, id: int) -> bool:
        """Delete a record (soft delete if supported)"""
        db_obj = self.get(db, id)
        if db_obj:
            if hasattr(db_obj, 'is_active'):
                db_obj.is_active = False
                db.commit()
            else:
                db.delete(db_obj)
                db.commit()
            return True
        return False
```

#### **1.2 Entity-Specific Services**
```python
# api/src/services/company_crud_service.py
from .crud_service import CRUDService
from ..models.database import Company

class CompanyCRUDService(CRUDService[Company]):
    def search_by_symbol(self, db: Session, symbol: str) -> List[Company]:
        """Search companies by symbol"""
        return db.query(Company).filter(
            Company.symbol.ilike(f"%{symbol}%")
        ).all()

    def get_by_sector(self, db: Session, sector: str) -> List[Company]:
        """Get companies by sector"""
        return db.query(Company).filter(Company.sector == sector).all()

    def bulk_update(self, db: Session, updates: List[Dict[str, Any]]) -> List[Company]:
        """Bulk update multiple companies"""
        updated_companies = []
        for update_data in updates:
            company = self.update(db, update_data['id'], update_data)
            if company:
                updated_companies.append(company)
        return updated_companies
```

#### **1.3 API Endpoints**
```python
# api/src/api/v1/endpoints/operations.py
from fastapi import APIRouter, Depends, HTTPException, Query
from typing import List, Optional, Dict, Any
from sqlalchemy.orm import Session

router = APIRouter()

@router.get("/entities/{entity_name}")
async def list_entities(
    entity_name: str,
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=1000),
    filters: Optional[Dict[str, Any]] = None,
    db: Session = Depends(get_database_session)
):
    """List entities with pagination and filtering"""
    service = get_crud_service(entity_name)
    entities = service.get_multi(db, skip=skip, limit=limit, filters=filters)
    return {
        "entities": entities,
        "total": len(entities),
        "skip": skip,
        "limit": limit
    }

@router.post("/entities/{entity_name}")
async def create_entity(
    entity_name: str,
    entity_data: Dict[str, Any],
    db: Session = Depends(get_database_session)
):
    """Create a new entity"""
    service = get_crud_service(entity_name)
    entity = service.create(db, entity_data)
    return {"entity": entity, "message": "Entity created successfully"}

@router.put("/entities/{entity_name}/{entity_id}")
async def update_entity(
    entity_name: str,
    entity_id: int,
    entity_data: Dict[str, Any],
    db: Session = Depends(get_database_session)
):
    """Update an entity"""
    service = get_crud_service(entity_name)
    entity = service.update(db, entity_id, entity_data)
    if not entity:
        raise HTTPException(status_code=404, detail="Entity not found")
    return {"entity": entity, "message": "Entity updated successfully"}

@router.delete("/entities/{entity_name}/{entity_id}")
async def delete_entity(
    entity_name: str,
    entity_id: int,
    db: Session = Depends(get_database_session)
):
    """Delete an entity"""
    service = get_crud_service(entity_name)
    success = service.delete(db, entity_id)
    if not success:
        raise HTTPException(status_code=404, detail="Entity not found")
    return {"message": "Entity deleted successfully"}
```

### **Phase 2: Frontend Development (Week 24)**

#### **2.1 Operations Page Layout**
```tsx
// frontend/src/app/(dashboard)/operations/page.tsx
'use client';

import { useState } from 'react';
import { DashboardPageLayout } from '@/components/layouts';
import { OperationsSidebar } from '@/components/operations/OperationsSidebar';
import { EntityManagementPanel } from '@/components/operations/EntityManagementPanel';

export default function OperationsPage() {
  const [selectedEntity, setSelectedEntity] = useState('companies');
  const [selectedAction, setSelectedAction] = useState('list');

  return (
    <div className="flex h-screen bg-gray-50">
      <OperationsSidebar
        selectedEntity={selectedEntity}
        onEntitySelect={setSelectedEntity}
        selectedAction={selectedAction}
        onActionSelect={setSelectedAction}
      />
      <div className="flex-1 overflow-hidden">
        <EntityManagementPanel
          entity={selectedEntity}
          action={selectedAction}
        />
      </div>
    </div>
  );
}
```

#### **2.2 Operations Sidebar Component**
```tsx
// frontend/src/components/operations/OperationsSidebar.tsx
'use client';

import { useState } from 'react';
import {
  Building2,
  TrendingUp,
  Users,
  Briefcase,
  Settings,
  Database,
  FileText,
  BarChart3
} from 'lucide-react';

const ENTITY_SECTIONS = [
  {
    title: 'Data Management',
    entities: [
      { id: 'companies', name: 'Companies', icon: Building2 },
      { id: 'sectors', name: 'Sectors', icon: BarChart3 },
      { id: 'ratios', name: 'Financial Ratios', icon: TrendingUp },
    ]
  },
  {
    title: 'User Management',
    entities: [
      { id: 'users', name: 'Users', icon: Users },
      { id: 'sessions', name: 'Sessions', icon: Database },
    ]
  },
  {
    title: 'Portfolio Management',
    entities: [
      { id: 'portfolios', name: 'Portfolios', icon: Briefcase },
      { id: 'strategies', name: 'Strategies', icon: FileText },
    ]
  },
  {
    title: 'System',
    entities: [
      { id: 'logs', name: 'System Logs', icon: FileText },
      { id: 'settings', name: 'Settings', icon: Settings },
    ]
  }
];

export function OperationsSidebar({
  selectedEntity,
  onEntitySelect,
  selectedAction,
  onActionSelect
}) {
  return (
    <div className="w-64 bg-white shadow-lg h-full overflow-y-auto">
      <div className="p-4 border-b">
        <h2 className="text-lg font-semibold text-gray-900">Operations</h2>
      </div>

      {ENTITY_SECTIONS.map((section) => (
        <div key={section.title} className="p-4">
          <h3 className="text-sm font-medium text-gray-500 uppercase tracking-wide mb-2">
            {section.title}
          </h3>
          <div className="space-y-1">
            {section.entities.map((entity) => (
              <button
                key={entity.id}
                onClick={() => onEntitySelect(entity.id)}
                className={`w-full flex items-center px-3 py-2 text-sm rounded-md transition-colors ${
                  selectedEntity === entity.id
                    ? 'bg-blue-100 text-blue-700'
                    : 'text-gray-700 hover:bg-gray-100'
                }`}
              >
                <entity.icon className="h-4 w-4 mr-3" />
                {entity.name}
              </button>
            ))}
          </div>
        </div>
      ))}
    </div>
  );
}
```

#### **2.3 Entity Management Panel**
```tsx
// frontend/src/components/operations/EntityManagementPanel.tsx
'use client';

import { useState, useEffect } from 'react';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import {
  Search,
  Plus,
  Download,
  Upload,
  Filter,
  Edit,
  Trash2,
  Eye
} from 'lucide-react';

export function EntityManagementPanel({ entity, action }) {
  const [data, setData] = useState([]);
  const [loading, setLoading] = useState(false);
  const [searchTerm, setSearchTerm] = useState('');
  const [selectedItems, setSelectedItems] = useState([]);

  // Fetch data based on selected entity
  useEffect(() => {
    fetchEntityData();
  }, [entity]);

  const fetchEntityData = async () => {
    setLoading(true);
    try {
      const response = await fetch(`/api/v1/operations/entities/${entity}`);
      const result = await response.json();
      setData(result.entities);
    } catch (error) {
      console.error('Error fetching data:', error);
    } finally {
      setLoading(false);
    }
  };

  const handleCreate = () => {
    // Open create modal
    console.log('Create new', entity);
  };

  const handleEdit = (id) => {
    // Open edit modal
    console.log('Edit', entity, id);
  };

  const handleDelete = async (id) => {
    if (confirm('Are you sure you want to delete this item?')) {
      try {
        await fetch(`/api/v1/operations/entities/${entity}/${id}`, {
          method: 'DELETE'
        });
        fetchEntityData(); // Refresh data
      } catch (error) {
        console.error('Error deleting item:', error);
      }
    }
  };

  return (
    <div className="p-6">
      <div className="mb-6">
        <h1 className="text-2xl font-bold text-gray-900 capitalize">
          {entity} Management
        </h1>
        <p className="text-gray-600">
          Manage {entity} data with full CRUD operations
        </p>
      </div>

      {/* Action Bar */}
      <Card className="mb-6">
        <CardContent className="p-4">
          <div className="flex items-center justify-between">
            <div className="flex items-center space-x-4">
              <div className="relative">
                <Search className="absolute left-3 top-1/2 transform -translate-y-1/2 h-4 w-4 text-gray-400" />
                <Input
                  placeholder="Search..."
                  value={searchTerm}
                  onChange={(e) => setSearchTerm(e.target.value)}
                  className="pl-10 w-64"
                />
              </div>
              <Button variant="outline" size="sm">
                <Filter className="h-4 w-4 mr-2" />
                Filter
              </Button>
            </div>
            <div className="flex items-center space-x-2">
              <Button onClick={handleCreate} size="sm">
                <Plus className="h-4 w-4 mr-2" />
                Add New
              </Button>
              <Button variant="outline" size="sm">
                <Download className="h-4 w-4 mr-2" />
                Export
              </Button>
              <Button variant="outline" size="sm">
                <Upload className="h-4 w-4 mr-2" />
                Import
              </Button>
            </div>
          </div>
        </CardContent>
      </Card>

      {/* Data Table */}
      <Card>
        <CardHeader>
          <CardTitle>
            {entity.charAt(0).toUpperCase() + entity.slice(1)} List
            {selectedItems.length > 0 && (
              <span className="ml-2 text-sm text-gray-500">
                ({selectedItems.length} selected)
              </span>
            )}
          </CardTitle>
        </CardHeader>
        <CardContent>
          {loading ? (
            <div className="text-center py-8">Loading...</div>
          ) : (
            <div className="overflow-x-auto">
              <table className="w-full">
                <thead>
                  <tr className="border-b">
                    <th className="text-left p-3">
                      <input
                        type="checkbox"
                        onChange={(e) => {
                          if (e.target.checked) {
                            setSelectedItems(data.map(item => item.id));
                          } else {
                            setSelectedItems([]);
                          }
                        }}
                      />
                    </th>
                    {data.length > 0 && Object.keys(data[0]).map((key) => (
                      <th key={key} className="text-left p-3 font-medium">
                        {key.replace(/_/g, ' ').toUpperCase()}
                      </th>
                    ))}
                    <th className="text-left p-3 font-medium">Actions</th>
                  </tr>
                </thead>
                <tbody>
                  {data.map((item) => (
                    <tr key={item.id} className="border-b hover:bg-gray-50">
                      <td className="p-3">
                        <input
                          type="checkbox"
                          checked={selectedItems.includes(item.id)}
                          onChange={(e) => {
                            if (e.target.checked) {
                              setSelectedItems([...selectedItems, item.id]);
                            } else {
                              setSelectedItems(selectedItems.filter(id => id !== item.id));
                            }
                          }}
                        />
                      </td>
                      {Object.entries(item).map(([key, value]) => (
                        <td key={key} className="p-3 text-sm">
                          {typeof value === 'object' ? JSON.stringify(value) : String(value)}
                        </td>
                      ))}
                      <td className="p-3">
                        <div className="flex items-center space-x-2">
                          <Button
                            variant="ghost"
                            size="sm"
                            onClick={() => handleEdit(item.id)}
                          >
                            <Edit className="h-4 w-4" />
                          </Button>
                          <Button
                            variant="ghost"
                            size="sm"
                            onClick={() => handleDelete(item.id)}
                          >
                            <Trash2 className="h-4 w-4" />
                          </Button>
                        </div>
                      </td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          )}
        </CardContent>
      </Card>
    </div>
  );
}
```

### **Phase 3: Advanced Features (Week 25)**

#### **3.1 Bulk Operations**
- Bulk delete, update, and export
- CSV import/export functionality
- Data validation and error handling

#### **3.2 Advanced Filtering**
- Multi-column filtering
- Date range filters
- Search across multiple fields
- Saved filter presets

#### **3.3 Audit Logging**
- Track all CRUD operations
- User action logging
- Data change history
- Rollback capabilities

---

## 🔒 **Security Considerations**

### **Access Control**
- Role-based access control (RBAC)
- Admin-only access to operations page
- API endpoint protection
- Audit logging for all operations

### **Data Validation**
- Input validation on all forms
- SQL injection prevention
- XSS protection
- CSRF tokens

### **Rate Limiting**
- API rate limiting
- Bulk operation throttling
- User action limits

---

## 📊 **Success Criteria**

- [ ] All database entities accessible through UI
- [ ] Full CRUD operations for each entity
- [ ] Bulk operations (import/export/delete)
- [ ] Advanced search and filtering
- [ ] Real-time data updates
- [ ] Audit logging for all operations
- [ ] Role-based access control
- [ ] Responsive design for all screen sizes

---

## 🎯 **Dependencies**

- **Backend**: FastAPI + SQLAlchemy (already available)
- **Frontend**: Next.js + React (already available)
- **Database**: SQLite (already available)
- **Authentication**: Tech-036 (Authentication System)

---

**Document Version**: 1.0
**Last Updated**: January 21, 2025
**Next Review**: Before implementation start
**Maintained By**: Development Team
