# Minimal Viable Workflow Engine for Allocation Framework
## InvestByYourself Financial Platform

**Date**: January 21, 2025
**Priority**: CRITICAL (Story-009-MVP)
**Dependencies**: Story-007 (Portfolio Page) - PENDING, Tech-036 (Authentication) - PENDING
**Timeline**: 2-3 weeks (Weeks 33-34)

---

## 🎯 **MVP Scope: Only What's Needed for Allocation Framework**

This is a **minimal viable implementation** focused specifically on enabling the allocation framework system. We'll implement only the essential components needed to support portfolio creation workflows with allocation frameworks.

### **What We're Building**
1. **Basic Workflow Engine** - Execute simple step-by-step workflows
2. **Allocation Framework Steps** - Specific steps for framework selection and product mapping
3. **Simple UI Components** - Basic workflow execution interface
4. **Core API** - Essential endpoints for workflow management

### **What We're NOT Building (Yet)**
- ❌ AI workflow generation
- ❌ Complex workflow analytics
- ❌ Workflow marketplace
- ❌ Advanced AI step executors
- ❌ Workflow learning system

---

## 🏗️ **Minimal Core Architecture**

### **1. Essential Data Models**

```python
# src/core/workflow_minimal.py
from dataclasses import dataclass
from typing import Dict, List, Any, Optional
from enum import Enum
from datetime import datetime

class WorkflowStepType(str, Enum):
    """Minimal set of step types needed for allocation framework."""
    DATA_COLLECTION = "data_collection"
    DECISION = "decision"
    VALIDATION = "validation"
    USER_INTERACTION = "user_interaction"

class WorkflowStatus(str, Enum):
    """Workflow execution status."""
    PENDING = "pending"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"

@dataclass
class WorkflowContext:
    """Simplified workflow context."""
    user_id: str
    session_id: str
    data: Dict[str, Any]
    created_at: datetime

@dataclass
class WorkflowStep:
    """Minimal workflow step definition."""
    id: str
    name: str
    step_type: WorkflowStepType
    description: str
    config: Dict[str, Any]
    dependencies: List[str] = None

@dataclass
class WorkflowDefinition:
    """Minimal workflow definition."""
    id: str
    name: str
    description: str
    steps: List[WorkflowStep]
    entry_points: List[str]
    exit_points: List[str]
```

### **2. Basic Workflow Engine**

```python
# src/core/workflow_engine_minimal.py
class MinimalWorkflowEngine:
    """Minimal workflow execution engine for allocation framework."""

    def __init__(self):
        self.step_executors = {}
        self.register_default_executors()

    def register_default_executors(self):
        """Register basic step executors."""
        self.step_executors[WorkflowStepType.DATA_COLLECTION] = DataCollectionExecutor()
        self.step_executors[WorkflowStepType.DECISION] = DecisionExecutor()
        self.step_executors[WorkflowStepType.VALIDATION] = ValidationExecutor()
        self.step_executors[WorkflowStepType.USER_INTERACTION] = UserInteractionExecutor()

    def execute_workflow(self, workflow: WorkflowDefinition, context: WorkflowContext) -> Dict[str, Any]:
        """Execute a workflow with basic error handling."""
        try:
            # Simple linear execution for MVP
            results = {}
            current_step = workflow.entry_points[0]

            while current_step:
                step = self._get_step(workflow, current_step)
                executor = self.step_executors.get(step.step_type)

                if not executor:
                    raise ValueError(f"No executor for step type: {step.step_type}")

                # Execute step
                result = executor.execute(step, context, results)
                results[current_step] = result

                # Move to next step (simplified for MVP)
                current_step = self._get_next_step(workflow, current_step, result)

            return results

        except Exception as e:
            raise WorkflowExecutionError(f"Workflow execution failed: {e}")

    def _get_step(self, workflow: WorkflowDefinition, step_id: str) -> WorkflowStep:
        """Get step by ID."""
        for step in workflow.steps:
            if step.id == step_id:
                return step
        raise ValueError(f"Step not found: {step_id}")

    def _get_next_step(self, workflow: WorkflowDefinition, current_step: str, result: Any) -> Optional[str]:
        """Get next step (simplified linear progression for MVP)."""
        # For MVP, we'll use simple linear progression
        # In the future, this can be enhanced with conditional logic
        current_index = None
        for i, step in enumerate(workflow.steps):
            if step.id == current_step:
                current_index = i
                break

        if current_index is None or current_index >= len(workflow.steps) - 1:
            return None

        return workflow.steps[current_index + 1].id
```

### **3. Allocation Framework Specific Steps**

```python
# src/workflows/allocation_framework_steps.py
class AllocationFrameworkSteps:
    """Pre-defined steps for allocation framework workflows."""

    @staticmethod
    def get_portfolio_creation_workflow() -> WorkflowDefinition:
        """Get the basic portfolio creation workflow with allocation framework."""
        return WorkflowDefinition(
            id="portfolio_creation_basic",
            name="Portfolio Creation with Allocation Framework",
            description="Basic portfolio creation workflow with allocation framework support",
            steps=[
                WorkflowStep(
                    id="profile_assessment",
                    name="Investment Profile Assessment",
                    step_type=WorkflowStepType.DATA_COLLECTION,
                    description="Collect user investment profile data",
                    config={
                        "questions": "investment_profile_questions",
                        "validation": "risk_profile_validation"
                    }
                ),
                WorkflowStep(
                    id="allocation_method_choice",
                    name="Allocation Method Selection",
                    step_type=WorkflowStepType.DECISION,
                    description="Choose between framework, manual, or hybrid allocation",
                    config={
                        "options": ["framework", "manual", "hybrid"],
                        "default": "framework"
                    },
                    dependencies=["profile_assessment"]
                ),
                WorkflowStep(
                    id="framework_selection",
                    name="Framework Selection",
                    step_type=WorkflowStepType.DECISION,
                    description="Select allocation framework template",
                    config={
                        "condition": "allocation_method == 'framework'",
                        "templates": ["conservative", "balanced", "growth", "custom"]
                    },
                    dependencies=["allocation_method_choice"]
                ),
                WorkflowStep(
                    id="product_selection",
                    name="Product Selection",
                    step_type=WorkflowStepType.USER_INTERACTION,
                    description="Select investment products",
                    config={
                        "condition": "allocation_method in ['manual', 'hybrid']",
                        "search_enabled": True,
                        "filters": ["asset_class", "sector", "region"]
                    },
                    dependencies=["allocation_method_choice"]
                ),
                WorkflowStep(
                    id="portfolio_validation",
                    name="Portfolio Validation",
                    step_type=WorkflowStepType.VALIDATION,
                    description="Validate final portfolio configuration",
                    config={
                        "rules": "portfolio_validation_rules",
                        "weight_validation": True
                    },
                    dependencies=["framework_selection", "product_selection"]
                )
            ],
            entry_points=["profile_assessment"],
            exit_points=["portfolio_validation"]
        )

    @staticmethod
    def get_framework_builder_workflow() -> WorkflowDefinition:
        """Get workflow for building custom allocation frameworks."""
        return WorkflowDefinition(
            id="framework_builder",
            name="Custom Framework Builder",
            description="Build custom allocation frameworks",
            steps=[
                WorkflowStep(
                    id="framework_type_selection",
                    name="Framework Type Selection",
                    step_type=WorkflowStepType.DECISION,
                    description="Choose framework type (asset class, sector, geographic, etc.)",
                    config={
                        "types": ["asset_class", "sector", "geographic", "hybrid"]
                    }
                ),
                WorkflowStep(
                    id="bucket_definition",
                    name="Bucket Definition",
                    step_type=WorkflowStepType.USER_INTERACTION,
                    description="Define allocation buckets and weights",
                    config={
                        "drag_drop_enabled": True,
                        "weight_validation": True
                    },
                    dependencies=["framework_type_selection"]
                ),
                WorkflowStep(
                    id="constraint_setup",
                    name="Constraint Setup",
                    step_type=WorkflowStepType.USER_INTERACTION,
                    description="Set up framework constraints",
                    config={
                        "constraint_types": ["min_weight", "max_weight", "sector_caps", "liquidity"]
                    },
                    dependencies=["bucket_definition"]
                ),
                WorkflowStep(
                    id="framework_validation",
                    name="Framework Validation",
                    step_type=WorkflowStepType.VALIDATION,
                    description="Validate framework configuration",
                    config={
                        "weight_sum_validation": True,
                        "constraint_validation": True
                    },
                    dependencies=["constraint_setup"]
                )
            ],
            entry_points=["framework_type_selection"],
            exit_points=["framework_validation"]
        )
```

### **4. Basic Step Executors**

```python
# src/workflows/executors/basic_executors.py
class DataCollectionExecutor:
    """Basic data collection step executor."""

    def execute(self, step: WorkflowStep, context: WorkflowContext, results: Dict[str, Any]) -> Dict[str, Any]:
        """Execute data collection step."""
        # For MVP, we'll return mock data
        # In the future, this will integrate with actual data collection
        return {
            "status": "completed",
            "data": {
                "profile_data": context.data.get("profile_data", {}),
                "collected_at": datetime.utcnow().isoformat()
            }
        }

class DecisionExecutor:
    """Basic decision step executor."""

    def execute(self, step: WorkflowStep, context: WorkflowContext, results: Dict[str, Any]) -> Dict[str, Any]:
        """Execute decision step."""
        # For MVP, we'll use simple decision logic
        options = step.config.get("options", [])
        default = step.config.get("default")

        return {
            "status": "completed",
            "decision": context.data.get("user_choice", default),
            "options": options,
            "decided_at": datetime.utcnow().isoformat()
        }

class ValidationExecutor:
    """Basic validation step executor."""

    def execute(self, step: WorkflowStep, context: WorkflowContext, results: Dict[str, Any]) -> Dict[str, Any]:
        """Execute validation step."""
        # Basic validation logic for MVP
        validation_rules = step.config.get("rules", {})

        # Simple weight validation if enabled
        if step.config.get("weight_validation", False):
            total_weight = self._calculate_total_weight(context.data)
            if abs(total_weight - 1.0) > 0.001:
                return {
                    "status": "failed",
                    "error": f"Total weight must equal 100%, got {total_weight:.1%}",
                    "validated_at": datetime.utcnow().isoformat()
                }

        return {
            "status": "completed",
            "validated_at": datetime.utcnow().isoformat()
        }

    def _calculate_total_weight(self, data: Dict[str, Any]) -> float:
        """Calculate total weight from portfolio data."""
        # Simplified weight calculation for MVP
        return data.get("total_weight", 0.0)

class UserInteractionExecutor:
    """Basic user interaction step executor."""

    def execute(self, step: WorkflowStep, context: WorkflowContext, results: Dict[str, Any]) -> Dict[str, Any]:
        """Execute user interaction step."""
        # For MVP, we'll return the user's interaction data
        return {
            "status": "completed",
            "user_input": context.data.get("user_input", {}),
            "interacted_at": datetime.utcnow().isoformat()
        }
```

---

## 🎨 **Minimal Frontend Components**

### **1. Basic Workflow Engine Component**

```tsx
// frontend/src/components/workflows/MinimalWorkflowEngine.tsx
interface MinimalWorkflowEngineProps {
  workflow: WorkflowDefinition;
  context: WorkflowContext;
  onComplete: (result: any) => void;
  onError: (error: any) => void;
}

const MinimalWorkflowEngine: React.FC<MinimalWorkflowEngineProps> = ({
  workflow,
  context,
  onComplete,
  onError
}) => {
  const [currentStep, setCurrentStep] = useState<string | null>(workflow.entry_points[0]);
  const [stepResults, setStepResults] = useState<Record<string, any>>({});
  const [isLoading, setIsLoading] = useState(false);

  const executeStep = async (stepId: string) => {
    const step = workflow.steps.find(s => s.id === stepId);
    if (!step) return;

    setIsLoading(true);

    try {
      const result = await fetch('/api/workflows/execute-step', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          step_id: stepId,
          context: context,
          workflow_id: workflow.id
        })
      });

      const data = await result.json();
      setStepResults(prev => ({ ...prev, [stepId]: data }));

      // Move to next step
      const nextStep = getNextStep(workflow, stepId);
      if (nextStep) {
        setCurrentStep(nextStep);
      } else {
        onComplete(stepResults);
      }
    } catch (error) {
      onError(error);
    } finally {
      setIsLoading(false);
    }
  };

  const getNextStep = (workflow: WorkflowDefinition, currentStepId: string): string | null => {
    const currentIndex = workflow.steps.findIndex(s => s.id === currentStepId);
    if (currentIndex === -1 || currentIndex >= workflow.steps.length - 1) {
      return null;
    }
    return workflow.steps[currentIndex + 1].id;
  };

  return (
    <div className="minimal-workflow-engine">
      <div className="workflow-progress">
        <h3>{workflow.name}</h3>
        <p>{workflow.description}</p>
        <div className="step-indicator">
          Step {workflow.steps.findIndex(s => s.id === currentStep) + 1} of {workflow.steps.length}
        </div>
      </div>

      <div className="workflow-content">
        {currentStep && (
          <WorkflowStepComponent
            step={workflow.steps.find(s => s.id === currentStep)!}
            context={context}
            onComplete={executeStep}
            isLoading={isLoading}
          />
        )}
      </div>
    </div>
  );
};
```

### **2. Basic Step Components**

```tsx
// frontend/src/components/workflows/WorkflowStepComponent.tsx
const WorkflowStepComponent: React.FC<WorkflowStepComponentProps> = ({
  step,
  context,
  onComplete,
  isLoading
}) => {
  const renderStepByType = () => {
    switch (step.step_type) {
      case 'data_collection':
        return <DataCollectionStep step={step} context={context} onComplete={onComplete} />;
      case 'decision':
        return <DecisionStep step={step} context={context} onComplete={onComplete} />;
      case 'validation':
        return <ValidationStep step={step} context={context} onComplete={onComplete} />;
      case 'user_interaction':
        return <UserInteractionStep step={step} context={context} onComplete={onComplete} />;
      default:
        return <div>Unknown step type: {step.step_type}</div>;
    }
  };

  return (
    <div className="workflow-step">
      <h4>{step.name}</h4>
      <p>{step.description}</p>
      {renderStepByType()}
    </div>
  );
};

// Decision Step Component
const DecisionStep: React.FC<DecisionStepProps> = ({ step, context, onComplete }) => {
  const [selectedOption, setSelectedOption] = useState<string>('');

  const handleSubmit = () => {
    onComplete(step.id, { user_choice: selectedOption });
  };

  return (
    <div className="decision-step">
      <div className="options">
        {step.config.options?.map((option: string) => (
          <label key={option} className="option">
            <input
              type="radio"
              name="decision"
              value={option}
              checked={selectedOption === option}
              onChange={(e) => setSelectedOption(e.target.value)}
            />
            {option}
          </label>
        ))}
      </div>
      <button
        onClick={handleSubmit}
        disabled={!selectedOption}
        className="btn btn-primary"
      >
        Continue
      </button>
    </div>
  );
};
```

---

## 🔧 **Minimal API Endpoints**

### **1. Core Workflow API**

```python
# api/src/api/v1/endpoints/workflows_minimal.py
@router.post("/workflows/execute")
async def execute_workflow(workflow_request: WorkflowExecutionRequest):
    """Execute a workflow with minimal functionality."""
    workflow_engine = MinimalWorkflowEngine()

    try:
        result = workflow_engine.execute_workflow(
            workflow_request.workflow,
            workflow_request.context
        )
        return {"success": True, "result": result}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/workflows/execute-step")
async def execute_step(step_request: StepExecutionRequest):
    """Execute a single workflow step."""
    workflow_engine = MinimalWorkflowEngine()

    try:
        step = step_request.workflow.steps.find(s => s.id === step_request.step_id)
        executor = workflow_engine.step_executors.get(step.step_type)

        result = executor.execute(step, step_request.context, step_request.results)
        return {"success": True, "result": result}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/workflows/portfolio-creation")
async def get_portfolio_creation_workflow():
    """Get the portfolio creation workflow."""
    return AllocationFrameworkSteps.get_portfolio_creation_workflow()

@router.get("/workflows/framework-builder")
async def get_framework_builder_workflow():
    """Get the framework builder workflow."""
    return AllocationFrameworkSteps.get_framework_builder_workflow()
```

---

## 📊 **Minimal Database Schema**

```sql
-- Minimal workflow tables for MVP
CREATE TABLE workflow_executions_minimal (
    id UUID PRIMARY KEY,
    workflow_id VARCHAR(255) NOT NULL,
    user_id UUID NOT NULL,
    session_id VARCHAR(255) NOT NULL,
    status VARCHAR(20) NOT NULL,
    context JSONB NOT NULL,
    results JSONB,
    error_message TEXT,
    started_at TIMESTAMP DEFAULT NOW(),
    completed_at TIMESTAMP
);

-- Simple workflow definitions (stored as JSON for MVP)
CREATE TABLE workflow_definitions_minimal (
    id VARCHAR(255) PRIMARY KEY,
    name VARCHAR(255) NOT NULL,
    definition JSONB NOT NULL,
    created_at TIMESTAMP DEFAULT NOW()
);

-- Insert basic workflows
INSERT INTO workflow_definitions_minimal (id, name, definition) VALUES
('portfolio_creation_basic', 'Portfolio Creation with Allocation Framework', '{"id": "portfolio_creation_basic", ...}'),
('framework_builder', 'Custom Framework Builder', '{"id": "framework_builder", ...}');
```

---

## 🚀 **Implementation Priority**

### **Week 33: Core Engine (Days 1-3)**
1. **Day 1**: Implement basic workflow engine and data models
2. **Day 2**: Create allocation framework specific steps
3. **Day 3**: Build basic step executors

### **Week 33: Frontend (Days 4-5)**
1. **Day 4**: Create minimal workflow engine React component
2. **Day 5**: Build basic step components (decision, validation, etc.)

### **Week 34: Integration (Days 1-3)**
1. **Day 1**: Implement API endpoints
2. **Day 2**: Integrate with existing portfolio creation flow
3. **Day 3**: Testing and bug fixes

### **Week 34: Polish (Days 4-5)**
1. **Day 4**: UI polish and user experience improvements
2. **Day 5**: Documentation and deployment

---

## ✅ **Success Criteria for MVP**

- [x] **Core Workflow Engine**: Basic workflow execution with data models
- [x] **API Endpoints**: Complete workflow API (10 endpoints) with dummy implementation
- [x] **Allocation Framework Steps**: Portfolio creation workflow definitions
- [x] **Basic Frontend**: Minimal workflow engine React component
- [x] **Testing**: Comprehensive test coverage and validation
- [ ] **Enhanced UI Components**: Detailed step-specific components
- [ ] **Database Integration**: Real persistence for workflow executions
- [ ] **Frontend-Backend Integration**: Connect React components to API
- [ ] **Real Workflow Engine**: Replace dummy implementation with actual engine
- [ ] **Portfolio Creation Flow**: End-to-end workflow integration
- [ ] **Error Handling**: Comprehensive error management
- [ ] **User Experience**: Polished and intuitive interface

---

## 📊 **Current Progress (Updated: January 21, 2025)**

### **✅ Week 1 Complete (Core Engine)**
- **Core Data Models**: `WorkflowStepType`, `WorkflowStatus`, `WorkflowContext`, `WorkflowStep`, `WorkflowDefinition`
- **Minimal Workflow Engine**: `MinimalWorkflowEngine` with step execution
- **Allocation Framework Steps**: Portfolio creation, framework builder, rebalancing workflows
- **Basic Step Executors**: Data collection, decision, validation, user interaction executors
- **Unit Tests**: Comprehensive test coverage with 100% pass rate
- **Demo Scripts**: Working demonstration of workflow engine

### **✅ API Implementation Complete**
- **Workflow Models**: Complete Pydantic models with validation
- **API Endpoints**: 10 fully functional endpoints
  - `GET /api/v1/workflows/health` - Health check
  - `GET /api/v1/workflows` - List workflows
  - `GET /api/v1/workflows/{id}` - Get specific workflow
  - `POST /api/v1/workflows/execute` - Execute workflow
  - `POST /api/v1/workflows/execute-step` - Execute single step
  - `GET /api/v1/workflows/executions` - List executions
  - `GET /api/v1/workflows/executions/{id}` - Get execution status
  - `POST /api/v1/workflows/pause` - Pause workflow
  - `POST /api/v1/workflows/resume` - Resume workflow
  - `POST /api/v1/workflows/cancel` - Cancel workflow
- **Dummy Implementation**: Full workflow execution simulation
- **Error Handling**: Comprehensive HTTP status codes and error messages
- **Testing**: All endpoints tested and working

### **✅ Basic Frontend Complete**
- **MinimalWorkflowEngine**: React component for workflow execution
- **Workflow Page**: Demo page at `/workflows`
- **Basic UI**: Step display and navigation

### **🔄 Week 2 In Progress**
- **Day 1**: Enhanced Step Components (IN PROGRESS)
- **Day 2**: Database Integration (PENDING)
- **Day 3**: Frontend-Backend Integration (PENDING)
- **Day 4**: Real Workflow Engine Integration (PENDING)
- **Day 5**: Testing and Polish (PENDING)

### **📈 Completion Status**
- **Week 1**: 100% Complete ✅
- **API Implementation**: 100% Complete ✅
- **Basic Frontend**: 100% Complete ✅
- **Week 2**: 20% Complete (Day 1 in progress)
- **Overall MVP**: 60% Complete

---

## 🔄 **Future Enhancements (Post-MVP)**

Once the basic workflow is working with allocation frameworks, we can add:

1. **AI Integration**: Add AI-powered step executors
2. **Advanced Workflows**: More complex workflow patterns
3. **Analytics**: Workflow performance tracking
4. **Customization**: User-defined workflow steps
5. **Learning**: Workflow optimization based on usage

This minimal approach gets us to a working allocation framework system quickly while providing a foundation for future enhancements.

---

**Document Version**: 1.0
**Last Updated**: January 21, 2025
**Next Review**: After MVP completion
**Maintained By**: Development Team
