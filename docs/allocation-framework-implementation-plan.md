# Allocation Framework Implementation Plan
## InvestByYourself Financial Platform

**Date**: January 21, 2025
**Priority**: HIGH (Story-008)
**Dependencies**: Story-009 (Workflow Engine) - PENDING, Story-007 (Portfolio Page) - PENDING, Tech-036 (Authentication) - PENDING
**Timeline**: 4-6 weeks (Weeks 36-39)

---

## 🚨 **Critical Gap Analysis**

### **Current State: MISSING ALLOCATION FRAMEWORK**
- **Portfolio Plan**: Basic portfolio construction and analysis only
- **Missing**: Sophisticated allocation framework system
- **Impact**: Users cannot create structured, rule-based portfolios
- **Business Value**: High - Enables professional portfolio management

### **Detailed Specification Analysis**
The provided specification is **comprehensive and production-ready** with:
- **12 detailed sections** covering UX, data model, API, validation, and rollout
- **Professional-grade features** including templates, custom frameworks, and mapping logic
- **Advanced capabilities** like band-based rebalancing and factor-aware templates

### **Enhanced UX Flow Integration**
The allocation framework **cleanly extends** the existing portfolio journey:

1. **Pick/Create Investment Profile** (required) - ✅ Already implemented
2. **Choose Allocation Framework** (new step):
   - Pick a Template (Conservative/Balanced/Growth)
   - Build Custom Framework (asset classes, regions, sectors, sleeves)
   - Import JSON/CSV
3. **Review Targets** → constraints & drift bands
4. **Map Framework → Products** (auto-suggest ETFs/stocks per bucket)
5. **Finalize Portfolio** (weights initialized from framework)

---

## 📊 **Feature Comparison Matrix**

| Feature Category | Detailed Spec | Current Plan | Gap Level | Priority |
|------------------|---------------|--------------|-----------|----------|
| **Allocation Templates** | ✅ Complete | ❌ Missing | HIGH | CRITICAL |
| **Custom Framework Builder** | ✅ Complete | ❌ Missing | HIGH | CRITICAL |
| **Framework-to-Product Mapping** | ✅ Complete | ❌ Missing | HIGH | CRITICAL |
| **Band-based Rebalancing** | ✅ Complete | ❌ Missing | MEDIUM | HIGH |
| **Constraint Management** | ✅ Complete | ❌ Missing | MEDIUM | HIGH |
| **Education System** | ✅ Complete | ❌ Missing | LOW | MEDIUM |
| **Validation & Error Handling** | ✅ Complete | ⚠️ Basic | HIGH | CRITICAL |
| **Backtesting Integration** | ✅ Complete | ⚠️ Basic | MEDIUM | HIGH |

---

## 🎯 **Implementation Plan**

### **Phase 1: Core Framework System (Weeks 36-37)**

#### **1.1 Data Model Implementation**
```sql
-- Allocation Framework (matches detailed spec exactly)
CREATE TABLE allocation_frameworks (
    id UUID PRIMARY KEY,
    user_id UUID NOT NULL,
    profile_id UUID REFERENCES investment_profiles(id),
    name VARCHAR(255) NOT NULL,
    description TEXT,
    benchmark_id UUID REFERENCES benchmarks(id),
    base_ccy VARCHAR(3) DEFAULT 'USD',
    method VARCHAR(20) NOT NULL, -- 'template', 'custom', 'imported'
    rebalancing JSONB, -- {cadence: 'Q'|'A', drift_bps: 300}
    constraints JSONB, -- portfolio-level rules (max_single_name, min_bonds, etc.)
    version INTEGER DEFAULT 1,
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW()
);

-- Allocation Buckets (hierarchical tree structure)
CREATE TABLE allocation_buckets (
    id UUID PRIMARY KEY,
    framework_id UUID REFERENCES allocation_frameworks(id),
    path VARCHAR(500) NOT NULL, -- e.g., "AssetClass/Equity/US/Large"
    label VARCHAR(255) NOT NULL, -- e.g., "US Large Cap"
    target_weight DECIMAL(5,4) NOT NULL, -- 0-1 (must sum to 1.0 at root)
    min_weight DECIMAL(5,4),
    max_weight DECIMAL(5,4),
    rules JSONB, -- {include_tags:[], exclude_tags:[], min_liquidity, allowed_types:['ETF','Stock']}
    parent_id UUID REFERENCES allocation_buckets(id),
    created_at TIMESTAMP DEFAULT NOW()
);

-- Framework Constraints (portfolio-level rules)
CREATE TABLE framework_constraints (
    id UUID PRIMARY KEY,
    framework_id UUID REFERENCES allocation_frameworks(id),
    constraint_type VARCHAR(50) NOT NULL, -- 'max_single_name', 'min_bonds', 'max_sector', etc.
    constraint_value DECIMAL(8,4) NOT NULL, -- e.g., 0.10 for 10%
    constraint_unit VARCHAR(20), -- 'percentage', 'bps', 'dollars'
    created_at TIMESTAMP DEFAULT NOW()
);

-- Portfolio Framework Link
ALTER TABLE portfolios ADD COLUMN framework_id UUID REFERENCES allocation_frameworks(id);
ALTER TABLE portfolios ADD COLUMN framework_version_used INTEGER;
```

#### **1.2 Framework Types (matches detailed spec)**
```python
class AllocationTemplate:
    """Pre-built allocation templates - matches detailed specification exactly"""

    # Model Templates (fast path; tie to risk bands)
    TEMPLATES = {
        "conservative": {
            "name": "Conservative",
            "description": "Bonds 60 / Equity 35 / Alt 5",
            "risk_band": "low",
            "buckets": [
                {"path": "AssetClass/Bonds", "target_weight": 0.60, "label": "Fixed Income"},
                {"path": "AssetClass/Equity", "target_weight": 0.35, "label": "Equity"},
                {"path": "AssetClass/Alternatives", "target_weight": 0.05, "label": "Alternatives"}
            ]
        },
        "balanced": {
            "name": "Balanced",
            "description": "Equity 60 / Bonds 35 / Alt 5",
            "risk_band": "medium",
            "buckets": [
                {"path": "AssetClass/Equity", "target_weight": 0.60, "label": "Equity"},
                {"path": "AssetClass/Bonds", "target_weight": 0.35, "label": "Fixed Income"},
                {"path": "AssetClass/Alternatives", "target_weight": 0.05, "label": "Alternatives"}
            ]
        },
        "growth": {
            "name": "Growth",
            "description": "Equity 80 / Bonds 15 / Alt 5",
            "risk_band": "high",
            "buckets": [
                {"path": "AssetClass/Equity", "target_weight": 0.80, "label": "Equity"},
                {"path": "AssetClass/Bonds", "target_weight": 0.15, "label": "Fixed Income"},
                {"path": "AssetClass/Alternatives", "target_weight": 0.05, "label": "Alternatives"}
            ]
        }
    }

    # Sleeve-based Templates
    SLEEVE_TEMPLATES = {
        "core_satellite": {
            "name": "Core-Satellite",
            "description": "Core 70, Satellite 20, Hedge 10",
            "buckets": [
                {"path": "Sleeve/Core", "target_weight": 0.70, "label": "Core Beta"},
                {"path": "Sleeve/Satellite", "target_weight": 0.20, "label": "Active Satellites"},
                {"path": "Sleeve/Hedge", "target_weight": 0.10, "label": "Hedge Sleeve"}
            ]
        }
    }

    # Factor/Region/Sector Templates (user-defined buckets)
    FACTOR_TEMPLATES = {
        "geographic": {
            "name": "Geographic Allocation",
            "description": "US 50 / Intl 30 / EM 20",
            "buckets": [
                {"path": "Region/US", "target_weight": 0.50, "label": "United States"},
                {"path": "Region/International", "target_weight": 0.30, "label": "International Developed"},
                {"path": "Region/Emerging", "target_weight": 0.20, "label": "Emerging Markets"}
            ]
        },
        "sector_risk_band": {
            "name": "Sector by Risk Band",
            "description": "Sectors by risk profile",
            "buckets": [
                {"path": "Sector/Defensive", "target_weight": 0.30, "label": "Defensive Sectors"},
                {"path": "Sector/Cyclical", "target_weight": 0.40, "label": "Cyclical Sectors"},
                {"path": "Sector/Growth", "target_weight": 0.30, "label": "Growth Sectors"}
            ]
        }
    }

    # Custom: blank tree builder (drag-and-drop buckets + target weights)
    CUSTOM_TEMPLATE = {
        "name": "Custom Framework",
        "description": "Build your own allocation structure",
        "buckets": []  # User builds from scratch
    }
```

#### **1.3 Framework Builder UI**
```tsx
const FrameworkBuilder: React.FC = () => {
  const [framework, setFramework] = useState<AllocationFramework | null>(null);
  const [buckets, setBuckets] = useState<AllocationBucket[]>([]);
  const [totalWeight, setTotalWeight] = useState(0);

  return (
    <div className="framework-builder">
      <div className="framework-header">
        <h2>Allocation Framework Builder</h2>
        <div className="weight-validator">
          <span className={`weight-display ${totalWeight === 100 ? 'valid' : 'invalid'}`}>
            {totalWeight.toFixed(1)}%
          </span>
          <span className="weight-label">Target Allocation</span>
        </div>
      </div>

      <div className="buckets-tree">
        {buckets.map(bucket => (
          <BucketNode
            key={bucket.id}
            bucket={bucket}
            onUpdate={handleBucketUpdate}
            onDelete={handleBucketDelete}
            onAddChild={handleAddChild}
          />
        ))}
      </div>

      <div className="framework-actions">
        <Button onClick={addBucket}>Add Bucket</Button>
        <Button onClick={validateFramework} disabled={totalWeight !== 100}>
          Validate Framework
        </Button>
        <Button onClick={saveFramework} disabled={totalWeight !== 100}>
          Save Framework
        </Button>
      </div>
    </div>
  );
};
```

### **Phase 2: Product Mapping & Validation (Weeks 37-38)**

#### **2.1 Product Mapping Engine**
```python
class ProductMappingEngine:
    """Maps allocation buckets to specific securities"""

    def map_products_to_buckets(self, framework_id: str, universe_filters: dict = None):
        """Map products to each bucket based on rules and constraints"""
        framework = self.get_framework(framework_id)
        buckets = self.get_framework_buckets(framework_id)

        mapped_products = {}
        for bucket in buckets:
            # Apply bucket rules
            candidates = self.get_candidate_products(bucket, universe_filters)

            # Filter by constraints
            filtered = self.apply_constraints(candidates, bucket.rules)

            # Rank by suitability
            ranked = self.rank_products(filtered, bucket)

            mapped_products[bucket.id] = {
                'products': ranked[:5],  # Top 5 suggestions
                'data_health': self.check_data_health(ranked),
                'coverage_gaps': self.identify_gaps(bucket, ranked)
            }

        return mapped_products

    def get_candidate_products(self, bucket: AllocationBucket, filters: dict):
        """Get candidate products for a bucket"""
        query = self.build_product_query(bucket, filters)
        return self.database.execute(query)

    def apply_constraints(self, products: List[dict], rules: dict):
        """Apply bucket-specific constraints"""
        filtered = products

        if 'allowed_types' in rules:
            filtered = [p for p in filtered if p['type'] in rules['allowed_types']]

        if 'min_adv_usd' in rules:
            filtered = [p for p in filtered if p['avg_daily_volume'] >= rules['min_adv_usd']]

        if 'exclude_tags' in rules:
            filtered = [p for p in filtered if not any(tag in p['tags'] for tag in rules['exclude_tags'])]

        return filtered
```

#### **2.2 Validation System**
```python
class FrameworkValidator:
    """Validates allocation frameworks"""

    def validate_framework(self, framework: AllocationFramework) -> ValidationResult:
        """Comprehensive framework validation"""
        errors = []
        warnings = []

        # Weight validation
        total_weight = sum(bucket.target_weight for bucket in framework.buckets)
        if abs(total_weight - 1.0) > 0.001:
            errors.append(f"Total weight must equal 100%, got {total_weight:.1%}")

        # Bucket validation
        for bucket in framework.buckets:
            if bucket.target_weight < 0 or bucket.target_weight > 1:
                errors.append(f"Bucket {bucket.label} weight must be between 0-100%")

            if bucket.min_weight and bucket.target_weight < bucket.min_weight:
                errors.append(f"Bucket {bucket.label} target below minimum")

            if bucket.max_weight and bucket.target_weight > bucket.max_weight:
                errors.append(f"Bucket {bucket.label} target above maximum")

        # Coverage validation
        coverage_issues = self.check_coverage(framework)
        if coverage_issues:
            warnings.extend(coverage_issues)

        return ValidationResult(
            valid=len(errors) == 0,
            errors=errors,
            warnings=warnings
        )
```

### **Phase 3: Integration & Advanced Features (Weeks 38-39)**

#### **3.1 Portfolio Integration**
```python
class PortfolioFrameworkIntegration:
    """Integrates allocation frameworks with portfolios"""

    def initialize_portfolio_from_framework(self, portfolio_id: str, framework_id: str, overrides: dict = None):
        """Initialize portfolio weights from framework"""
        framework = self.get_framework(framework_id)
        mapped_products = self.map_products_to_framework(framework_id)

        positions = []
        for bucket in framework.buckets:
            if bucket.id in mapped_products:
                products = mapped_products[bucket.id]['products']
                if products:
                    # Use top-ranked product
                    product = products[0]
                    position = Position(
                        portfolio_id=portfolio_id,
                        instrument_id=product['id'],
                        weight=bucket.target_weight,
                        locked=False
                    )
                    positions.append(position)

        # Apply overrides if provided
        if overrides:
            positions = self.apply_overrides(positions, overrides)

        # Normalize weights
        total_weight = sum(p.weight for p in positions)
        for position in positions:
            position.weight = position.weight / total_weight

        return positions
```

#### **3.2 Band-based Rebalancing**
```python
class BandBasedRebalancer:
    """Implements band-based rebalancing logic"""

    def check_rebalance_needed(self, portfolio: Portfolio, framework: AllocationFramework):
        """Check if portfolio needs rebalancing based on bands"""
        current_positions = portfolio.get_positions()
        target_weights = {b.instrument_id: b.target_weight for b in framework.buckets}

        rebalance_needed = False
        drift_details = []

        for position in current_positions:
            target_weight = target_weights.get(position.instrument_id, 0)
            current_weight = position.weight
            drift = abs(current_weight - target_weight)

            # Check if drift exceeds band
            band_bps = framework.rebalance.get('band_bps', 500)  # 5% default
            band_threshold = band_bps / 10000

            if drift > band_threshold:
                rebalance_needed = True
                drift_details.append({
                    'instrument_id': position.instrument_id,
                    'current_weight': current_weight,
                    'target_weight': target_weight,
                    'drift': drift,
                    'exceeds_band': True
                })

        return {
            'rebalance_needed': rebalance_needed,
            'drift_details': drift_details,
            'next_check': self.get_next_check_date(framework)
        }
```

### **Phase 4: Education & Advanced Features (Weeks 36-37)**

#### **4.1 Education System**
```tsx
const EducationSystem: React.FC = () => {
  return (
    <div className="education-system">
      <EduPopover
        trigger={<Button>Add Framework</Button>}
        content={
          <div>
            <h3>Why Use an Allocation Framework?</h3>
            <ul>
              <li>Improves diversification across asset classes</li>
              <li>Reduces emotional decision making</li>
              <li>Provides clear rebalancing rules</li>
              <li>Helps maintain target risk profile</li>
            </ul>
          </div>
        }
      />

      <TemplateExplainer
        templates={['conservative', 'balanced', 'growth', 'core_satellite']}
        onSelect={handleTemplateSelect}
      />

      <DriftBandsExplainer
        content="Set drift bands to automatically trigger rebalancing when allocations drift too far from targets"
      />
    </div>
  );
};
```

#### **4.2 Advanced Analytics**
```python
class FrameworkAnalytics:
    """Analytics for allocation frameworks"""

    def generate_allocation_report(self, portfolio_id: str, framework_id: str):
        """Generate allocation vs target report"""
        portfolio = self.get_portfolio(portfolio_id)
        framework = self.get_framework(framework_id)

        actual_weights = portfolio.get_allocation_by_bucket()
        target_weights = {b.path: b.target_weight for b in framework.buckets}

        report = {
            'summary': {
                'total_drift': self.calculate_total_drift(actual_weights, target_weights),
                'rebalance_needed': self.check_rebalance_needed(portfolio, framework),
                'last_rebalance': portfolio.last_rebalance_date
            },
            'bucket_analysis': [],
            'drift_heatmap': self.generate_drift_heatmap(actual_weights, target_weights)
        }

        for bucket in framework.buckets:
            actual = actual_weights.get(bucket.path, 0)
            target = bucket.target_weight
            drift = actual - target

            report['bucket_analysis'].append({
                'bucket': bucket.label,
                'path': bucket.path,
                'actual_weight': actual,
                'target_weight': target,
                'drift': drift,
                'drift_pct': (drift / target) * 100 if target > 0 else 0,
                'status': 'within_band' if abs(drift) < 0.05 else 'exceeds_band'
            })

        return report
```

---

## 🔧 **API Endpoints (matches detailed spec exactly)**

### **Framework Management**
```python
# Framework CRUD (matches detailed spec)
@router.get("/allocation-frameworks")
async def list_frameworks(user_id: str):
    """GET /allocation-frameworks?user_id=…"""

@router.post("/allocation-frameworks")
async def create_framework(framework: AllocationFrameworkCreate):
    """POST /allocation-frameworks (create)"""

@router.get("/allocation-frameworks/{framework_id}")
async def get_framework(framework_id: str):
    """GET /allocation-frameworks/:id"""

@router.put("/allocation-frameworks/{framework_id}")
async def update_framework(framework_id: str, updates: AllocationFrameworkUpdate):
    """PUT /allocation-frameworks/:id (edit targets/constraints)"""

# Validation & Mapping (matches detailed spec)
@router.post("/allocation-frameworks/{framework_id}/map-products")
async def map_products(framework_id: str, filters: MappingFilters = None):
    """POST /allocation-frameworks/:id/map-products
    → returns suggested holdings per bucket with data-health"""

@router.post("/analytics/validate-framework")
async def validate_framework(framework: AllocationFramework):
    """POST /analytics/validate-framework (weights sum, constraints, coverage)"""

# Portfolio Integration (matches detailed spec)
@router.post("/portfolios")
async def create_portfolio_with_framework(portfolio: PortfolioCreate, framework_id: str = None, overrides: dict = None):
    """POST /portfolios with { framework_id, overrides? }"""

# Backtesting Integration (matches detailed spec)
@router.post("/backtest")
async def run_framework_backtest(backtest_params: BacktestParams, framework_id: str = None):
    """POST /backtest supports { framework_id, params… }"""
```

---

## 🎨 **Frontend Components (matches detailed spec exactly)**

### **Core Components**
```tsx
// FrameworkPicker (templates/custom/import)
const FrameworkPicker: React.FC = () => {
  return (
    <div className="framework-picker">
      <h3>Choose Allocation Framework</h3>
      <div className="template-grid">
        <TemplateCard template="conservative" />
        <TemplateCard template="balanced" />
        <TemplateCard template="growth" />
        <TemplateCard template="core_satellite" />
        <CustomFrameworkCard />
        <ImportFrameworkCard />
      </div>
    </div>
  );
};

// FrameworkEditor (tree of buckets with target sliders, min/max, rules)
const FrameworkEditor: React.FC = () => {
  return (
    <div className="framework-editor">
      <BucketTree buckets={buckets} onUpdate={handleBucketUpdate} />
      <TargetSliders buckets={buckets} onWeightChange={handleWeightChange} />
      <MinMaxConstraints buckets={buckets} onConstraintChange={handleConstraintChange} />
    </div>
  );
};

// ConstraintEditor (global + per-bucket)
const ConstraintEditor: React.FC = () => {
  return (
    <div className="constraint-editor">
      <GlobalConstraints constraints={globalConstraints} />
      <PerBucketConstraints buckets={buckets} />
    </div>
  );
};

// MappingWizard (per-bucket product suggestions + accept/replace)
const MappingWizard: React.FC = () => {
  return (
    <div className="mapping-wizard">
      {buckets.map(bucket => (
        <BucketMapping
          key={bucket.id}
          bucket={bucket}
          suggestions={mappedProducts[bucket.id]}
          onAccept={handleProductAccept}
          onReplace={handleProductReplace}
        />
      ))}
    </div>
  );
};

// TargetsBar (sum validator; color goes green at 100%)
const TargetsBar: React.FC = () => {
  const totalWeight = buckets.reduce((sum, bucket) => sum + bucket.target_weight, 0);
  const isValid = Math.abs(totalWeight - 1.0) < 0.001;

  return (
    <div className={`targets-bar ${isValid ? 'valid' : 'invalid'}`}>
      <span className="weight-display">{totalWeight.toFixed(1)}%</span>
      <span className="weight-label">Target Allocation</span>
    </div>
  );
};

// RebalanceBandControl (±bps)
const RebalanceBandControl: React.FC = () => {
  return (
    <div className="rebalance-band-control">
      <label>Drift Band (bps)</label>
      <input
        type="number"
        value={driftBps}
        onChange={(e) => setDriftBps(parseInt(e.target.value))}
        min="50"
        max="1000"
        step="50"
      />
    </div>
  );
};

// DiagnosticsDrawer (coverage, missing data, conflicts)
const DiagnosticsDrawer: React.FC = () => {
  return (
    <Drawer>
      <h3>Framework Diagnostics</h3>
      <CoverageIssues issues={coverageIssues} />
      <MissingDataWarnings warnings={missingDataWarnings} />
      <ConstraintViolations violations={constraintViolations} />
    </Drawer>
  );
};
```

### **Integration with Existing Stack**
- **Next.js + shadcn/ui**: All components use existing design system
- **Table/Chart Libraries**: Reuse existing visualization components
- **Form Handling**: Integrate with existing form validation
- **State Management**: Use existing portfolio state management

---

## 📊 **Success Criteria**

### **Phase 1 Success Criteria**
- [ ] Users can create custom allocation frameworks
- [ ] Template system works with 4+ pre-built templates
- [ ] Framework validation prevents invalid configurations
- [ ] Bucket tree structure supports hierarchical allocation

### **Phase 2 Success Criteria**
- [ ] Product mapping suggests appropriate securities per bucket
- [ ] Data health indicators show coverage status
- [ ] Constraint system filters products correctly
- [ ] Mapping wizard provides intuitive product selection

### **Phase 3 Success Criteria**
- [ ] Portfolios can be initialized from frameworks
- [ ] Band-based rebalancing works correctly
- [ ] Framework analytics show actual vs target allocation
- [ ] Rebalancing suggestions are accurate and actionable

### **Phase 4 Success Criteria**
- [ ] Education system provides helpful guidance
- [ ] Advanced analytics generate meaningful insights
- [ ] Export functionality works for all framework data
- [ ] Performance meets sub-5s response requirements

---

## 🚀 **Quick Implementation Steps (matches detailed spec exactly)**

### **Step 1: DB & Models**
- Add `AllocationFramework`, `AllocationBucket`, `FrameworkConstraint` tables
- Extend existing `portfolios` table with framework links
- Create Pydantic models for API serialization

### **Step 2: API Development**
- CRUD endpoints for frameworks and buckets
- Validation endpoint for weights and constraints
- Mapping endpoint for product suggestions
- Integration with existing portfolio endpoints

### **Step 3: Frontend Implementation**
- `FrameworkPicker` → `FrameworkEditor` → `MappingWizard` flow
- Gate Portfolio Builder until framework chosen
- Integrate with existing Next.js + shadcn/ui stack

### **Step 4: Analytics Integration**
- Reuse covariance/vol & allocation aggregations on buckets
- Add framework validator to existing analytics service
- Extend backtest service to support framework-driven reweighting

### **Step 5: Backtesting Integration**
- Support framework-driven reweighting at cadence/bands
- Add framework-aware backtest modes (static, periodic, band-based)
- Extend existing backtest error-handling & exports

### **Step 6: QA & Testing**
- Unit tests for validator logic
- E2E happy path: template → mapping → backtest
- Integration tests with existing portfolio system

---

## 🚀 **Implementation Priority**

### **Immediate Actions (Week 33)**
1. **Create data model** for allocation frameworks and buckets
2. **Implement template system** with 4 core templates
3. **Build framework builder UI** with tree structure
4. **Add validation system** for weights and constraints

### **Week 34 Tasks**
1. **Implement product mapping engine** with rule-based filtering
2. **Create mapping wizard UI** for product selection
3. **Add data health indicators** for coverage validation
4. **Build constraint management system**

### **Week 35 Tasks**
1. **Integrate with portfolio system** for framework application
2. **Implement band-based rebalancing** logic
3. **Create allocation analytics** and reporting
4. **Add rebalancing suggestions** and automation

### **Week 36 Tasks**
1. **Build education system** with tooltips and modals
2. **Implement advanced analytics** and drift analysis
3. **Add export functionality** for framework data
4. **Create comprehensive testing suite**

---

## 🤖 **Workflow Engine Integration**

### **Allocation Framework as Workflow Steps**

The allocation framework system integrates seamlessly with the generalized workflow engine, allowing for AI-powered customization and flexible user experiences.

#### **Workflow Step Integration**
```python
# Allocation Framework Workflow Steps
class AllocationFrameworkWorkflowSteps:
    @staticmethod
    def get_framework_selection_step() -> WorkflowStep:
        return WorkflowStep(
            id="framework_selection",
            name="Allocation Framework Selection",
            step_type=WorkflowStepType.DECISION,
            description="Select or create allocation framework",
            config={
                "ai_suggestions": True,
                "template_integration": True,
                "custom_framework_builder": True
            },
            dependencies=["profile_assessment"]
        )

    @staticmethod
    def get_product_mapping_step() -> WorkflowStep:
        return WorkflowStep(
            id="product_mapping",
            name="Product Mapping",
            step_type=WorkflowStepType.AI_GENERATED,
            description="AI-powered product mapping to framework buckets",
            config={
                "ai_model": "product_mapper",
                "data_health_indicators": True,
                "constraint_validation": True
            },
            dependencies=["framework_selection"],
            ai_generated=True,
            ai_prompt="Map investment products to allocation framework buckets based on user profile and constraints"
        )
```

#### **AI-Powered Framework Generation**
```python
# AI Framework Generator Integration
class AIAllocationFrameworkGenerator:
    """Generates custom allocation frameworks using AI."""

    def generate_framework(self, user_requirements: Dict[str, Any]) -> AllocationFramework:
        """Generate custom allocation framework based on user needs."""
        prompt = f"""
        Generate an allocation framework based on these requirements:

        User Profile: {user_requirements.get('profile')}
        Risk Tolerance: {user_requirements.get('risk_tolerance')}
        Investment Goals: {user_requirements.get('goals')}
        Preferences: {user_requirements.get('preferences')}

        Create a framework that includes:
        1. Appropriate asset class allocation
        2. Regional diversification
        3. Sector allocation if needed
        4. Rebalancing rules
        5. Constraint definitions

        Return a structured allocation framework.
        """

        ai_response = self.llm_client.generate_framework(prompt)
        return self._parse_framework_response(ai_response)
```

#### **Workflow-Driven Portfolio Creation**
```python
# Enhanced Portfolio Creation with Framework Integration
class PortfolioCreationWorkflow:
    @staticmethod
    def create_with_allocation_framework(user_requirements: Dict[str, Any]) -> WorkflowDefinition:
        """Create portfolio creation workflow with allocation framework integration."""
        return WorkflowDefinition(
            id="portfolio_creation_with_framework",
            name="Portfolio Creation with Allocation Framework",
            description="Complete portfolio creation workflow with AI-powered allocation framework",
            version="1.0",
            category="portfolio_creation",
            steps=[
                WorkflowStep(
                    id="profile_assessment",
                    name="Investment Profile Assessment",
                    step_type=WorkflowStepType.DATA_COLLECTION,
                    description="Collect user investment profile",
                    config={"ai_questions": True},
                    dependencies=[]
                ),
                WorkflowStep(
                    id="framework_generation",
                    name="AI Framework Generation",
                    step_type=WorkflowStepType.AI_GENERATED,
                    description="Generate custom allocation framework",
                    config={"ai_model": "framework_generator"},
                    dependencies=["profile_assessment"],
                    ai_generated=True
                ),
                WorkflowStep(
                    id="product_mapping",
                    name="Product Mapping",
                    step_type=WorkflowStepType.AI_GENERATED,
                    description="Map products to framework buckets",
                    config={"ai_model": "product_mapper"},
                    dependencies=["framework_generation"],
                    ai_generated=True
                ),
                WorkflowStep(
                    id="portfolio_validation",
                    name="Portfolio Validation",
                    step_type=WorkflowStepType.VALIDATION,
                    description="Validate final portfolio",
                    config={"ai_validation": True},
                    dependencies=["product_mapping"]
                )
            ],
            entry_points=["profile_assessment"],
            exit_points=["portfolio_validation"],
            ai_configurable=True
        )
```

---

## 📋 **Dependencies & Integration**

### **Required Dependencies**
- **Story-009 (Workflow Engine)**: AI-powered workflow generation and execution
- **Story-007 (Portfolio Page)**: Framework integration with portfolios
- **Tech-036 (Authentication)**: User management and security
- **Story-038 (Historical Data)**: Product data for mapping
- **Story-005 (Company Analysis)**: Security metadata and classification

### **Integration Points**
- **Workflow Engine**: Allocation framework as workflow steps
- **AI Generation**: AI-powered custom framework creation
- **Portfolio Creation**: Framework selection during portfolio setup
- **Portfolio Editing**: Framework application and weight adjustment
- **Rebalancing**: Band-based rebalancing integration
- **Analytics**: Allocation vs target reporting
- **Backtesting**: Framework-aware backtesting with rebalancing

---

**Document Version**: 1.0
**Last Updated**: January 21, 2025
**Next Review**: After Phase 1 completion
**Maintained By**: Development Team
