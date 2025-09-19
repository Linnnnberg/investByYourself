# Generalized Workflow Engine Implementation Plan
## InvestByYourself Financial Platform

**Date**: January 21, 2025
**Priority**: HIGH (Story-009)
**Dependencies**: Story-007 (Portfolio Page) - PENDING, Tech-036 (Authentication) - PENDING
**Timeline**: 4-6 weeks (Weeks 33-36)

---

## 🚀 **Overview**

The Generalized Workflow Engine is a foundational system that enables AI-driven custom workflows and flexible user experiences across all platform features. This system allows for dynamic workflow generation, execution, and adaptation based on user needs and behavior.

### **Core Value Proposition**
- **AI-Powered Customization**: Generate workflows tailored to individual user needs
- **Flexible User Experience**: Support multiple workflow patterns (guided, self-service, hybrid)
- **Extensible Architecture**: Easy integration with existing and future features
- **Intelligent Adaptation**: Workflows that learn and adapt to user preferences

---

## 🎯 **Implementation Plan**

### **Phase 1: Core Workflow Engine (Weeks 33-34)**

#### **1.1 Core Architecture Implementation**

```python
# src/core/workflow.py
from abc import ABC, abstractmethod
from typing import Dict, List, Any, Optional, Union
from enum import Enum
from dataclasses import dataclass
from datetime import datetime

class WorkflowStepType(str, Enum):
    """Types of workflow steps that can be executed."""
    DATA_COLLECTION = "data_collection"
    ANALYSIS = "analysis"
    DECISION = "decision"
    VALIDATION = "validation"
    TRANSFORMATION = "transformation"
    INTEGRATION = "integration"
    USER_INTERACTION = "user_interaction"
    AI_GENERATED = "ai_generated"

class WorkflowStatus(str, Enum):
    """Workflow execution status."""
    PENDING = "pending"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"
    PAUSED = "paused"
    CANCELLED = "cancelled"

@dataclass
class WorkflowContext:
    """Shared context passed between workflow steps."""
    user_id: str
    session_id: str
    data: Dict[str, Any]
    metadata: Dict[str, Any]
    created_at: datetime
    updated_at: datetime

@dataclass
class WorkflowStep:
    """Individual step in a workflow."""
    id: str
    name: str
    step_type: WorkflowStepType
    description: str
    config: Dict[str, Any]
    dependencies: List[str]  # Step IDs this step depends on
    ai_generated: bool = False
    ai_prompt: Optional[str] = None
    validation_rules: Optional[Dict[str, Any]] = None

@dataclass
class WorkflowDefinition:
    """Complete workflow definition."""
    id: str
    name: str
    description: str
    version: str
    category: str  # 'portfolio_creation', 'risk_assessment', 'rebalancing', etc.
    steps: List[WorkflowStep]
    entry_points: List[str]  # Starting step IDs
    exit_points: List[str]   # Ending step IDs
    ai_configurable: bool = True
    created_by: str = "system"  # 'system', 'user', 'ai'
    created_at: datetime
    updated_at: datetime
```

#### **1.2 Workflow Execution Engine**

```python
# src/core/workflow_engine.py
class WorkflowStepExecutor(ABC):
    """Base class for workflow step executors."""

    @abstractmethod
    def execute(self, step: WorkflowStep, context: WorkflowContext) -> Dict[str, Any]:
        """Execute a workflow step and return results."""
        pass

    @abstractmethod
    def validate(self, step: WorkflowStep, context: WorkflowContext) -> bool:
        """Validate step configuration and context."""
        pass

    @abstractmethod
    def get_required_inputs(self) -> List[str]:
        """Return list of required input keys."""
        pass

    @abstractmethod
    def get_outputs(self) -> List[str]:
        """Return list of output keys this step produces."""
        pass

class WorkflowEngine:
    """Main workflow execution engine."""

    def __init__(self):
        self.step_executors: Dict[WorkflowStepType, WorkflowStepExecutor] = {}
        self.ai_workflow_generator = AIWorkflowGenerator()
        self.workflow_registry = WorkflowRegistry()

    def register_step_executor(self, step_type: WorkflowStepType, executor: WorkflowStepExecutor):
        """Register a step executor for a specific step type."""
        self.step_executors[step_type] = executor

    def execute_workflow(self, workflow: WorkflowDefinition, context: WorkflowContext) -> Dict[str, Any]:
        """Execute a complete workflow."""
        execution_context = WorkflowExecutionContext(workflow, context)

        try:
            # Validate workflow
            if not self._validate_workflow(workflow):
                raise WorkflowValidationError("Invalid workflow definition")

            # Execute workflow steps in dependency order
            execution_order = self._calculate_execution_order(workflow)

            for step_id in execution_order:
                step = workflow.steps[step_id]
                executor = self.step_executors.get(step.step_type)

                if not executor:
                    raise WorkflowExecutionError(f"No executor for step type: {step.step_type}")

                # Execute step
                result = executor.execute(step, execution_context.context)
                execution_context.add_step_result(step_id, result)

            return execution_context.get_final_result()

        except Exception as e:
            execution_context.mark_failed(str(e))
            raise WorkflowExecutionError(f"Workflow execution failed: {e}")

    def _calculate_execution_order(self, workflow: WorkflowDefinition) -> List[str]:
        """Calculate the order in which steps should be executed."""
        # Topological sort based on dependencies
        pass
```

#### **1.3 Database Schema**

```sql
-- Workflow Definitions
CREATE TABLE workflow_definitions (
    id UUID PRIMARY KEY,
    name VARCHAR(255) NOT NULL,
    description TEXT,
    version VARCHAR(20) NOT NULL,
    category VARCHAR(100) NOT NULL,
    definition JSONB NOT NULL, -- WorkflowDefinition serialized
    ai_configurable BOOLEAN DEFAULT TRUE,
    created_by VARCHAR(50) DEFAULT 'system',
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW()
);

-- Workflow Executions
CREATE TABLE workflow_executions (
    id UUID PRIMARY KEY,
    workflow_id UUID REFERENCES workflow_definitions(id),
    user_id UUID NOT NULL,
    session_id VARCHAR(255) NOT NULL,
    status VARCHAR(20) NOT NULL,
    context JSONB NOT NULL, -- WorkflowContext serialized
    results JSONB, -- Step results
    error_message TEXT,
    started_at TIMESTAMP DEFAULT NOW(),
    completed_at TIMESTAMP,
    created_at TIMESTAMP DEFAULT NOW()
);

-- Workflow Step Executions
CREATE TABLE workflow_step_executions (
    id UUID PRIMARY KEY,
    execution_id UUID REFERENCES workflow_executions(id),
    step_id VARCHAR(255) NOT NULL,
    step_type VARCHAR(50) NOT NULL,
    status VARCHAR(20) NOT NULL,
    input_data JSONB,
    output_data JSONB,
    error_message TEXT,
    started_at TIMESTAMP DEFAULT NOW(),
    completed_at TIMESTAMP
);

-- Workflow Templates
CREATE TABLE workflow_templates (
    id UUID PRIMARY KEY,
    name VARCHAR(255) NOT NULL,
    description TEXT,
    category VARCHAR(100) NOT NULL,
    template JSONB NOT NULL, -- Template configuration
    ai_generated BOOLEAN DEFAULT FALSE,
    usage_count INTEGER DEFAULT 0,
    created_at TIMESTAMP DEFAULT NOW()
);
```

### **Phase 2: AI Integration (Weeks 34-35)**

#### **2.1 AI Workflow Generation System**

```python
# src/core/ai_workflow_generator.py
class AIWorkflowGenerator:
    """Generates custom workflows using AI based on user requirements."""

    def __init__(self):
        self.llm_client = self._initialize_llm()
        self.workflow_templates = self._load_workflow_templates()
        self.step_library = self._load_step_library()
        self.pattern_analyzer = WorkflowPatternAnalyzer()

    def generate(self, requirements: Dict[str, Any]) -> WorkflowDefinition:
        """Generate a workflow based on requirements."""

        # Step 1: Analyze requirements
        analysis = self._analyze_requirements(requirements)

        # Step 2: Generate workflow structure
        workflow_structure = self._generate_workflow_structure(analysis)

        # Step 3: Select appropriate steps
        selected_steps = self._select_workflow_steps(workflow_structure)

        # Step 4: Configure step parameters
        configured_steps = self._configure_steps(selected_steps, requirements)

        # Step 5: Validate workflow
        validated_workflow = self._validate_workflow(configured_steps)

        return validated_workflow

    def _analyze_requirements(self, requirements: Dict[str, Any]) -> Dict[str, Any]:
        """Analyze user requirements to understand workflow needs."""
        prompt = f"""
        Analyze these workflow requirements and determine the optimal workflow structure:

        Requirements: {requirements}

        Consider:
        1. User experience level
        2. Data requirements
        3. Decision points needed
        4. Validation requirements
        5. Integration needs
        6. AI assistance level preferred

        Return a structured analysis with:
        - Required step types
        - User guidance level
        - Complexity assessment
        - AI integration points
        """

        return self.llm_client.analyze(prompt)

    def _generate_workflow_structure(self, analysis: Dict[str, Any]) -> Dict[str, Any]:
        """Generate the high-level workflow structure."""
        prompt = f"""
        Based on this analysis, generate a workflow structure:

        Analysis: {analysis}

        Available step types: {[t.value for t in WorkflowStepType]}

        Generate a workflow that includes:
        1. Required steps with dependencies
        2. Entry and exit points
        3. Decision logic and branching
        4. AI integration points
        5. User interaction points

        Return a structured workflow definition.
        """

        return self.llm_client.generate_structure(prompt)
```

#### **2.2 AI-Powered Step Executors**

```python
# src/workflows/executors/ai_executors.py
class AIStepExecutor(WorkflowStepExecutor):
    """Executor for AI-generated workflow steps."""

    def __init__(self, llm_client):
        self.llm_client = llm_client
        self.context_manager = WorkflowContextManager()

    def execute(self, step: WorkflowStep, context: WorkflowContext) -> Dict[str, Any]:
        """Execute an AI-generated step."""

        # Prepare context for AI
        ai_context = self._prepare_ai_context(step, context)

        # Generate AI prompt
        prompt = self._generate_ai_prompt(step, ai_context)

        # Execute AI request
        ai_response = self.llm_client.execute(prompt, ai_context)

        # Process and validate response
        result = self._process_ai_response(ai_response, step)

        return result

    def _generate_ai_prompt(self, step: WorkflowStep, context: Dict[str, Any]) -> str:
        """Generate AI prompt for step execution."""
        base_prompt = step.ai_prompt or step.description

        return f"""
        {base_prompt}

        Context:
        - User ID: {context.get('user_id')}
        - Session Data: {context.get('data', {})}
        - Previous Results: {context.get('previous_results', {})}

        Requirements:
        - Step Type: {step.step_type}
        - Expected Outputs: {self.get_outputs()}
        - Validation Rules: {step.validation_rules}

        Please provide a structured response that includes:
        1. The main result/outcome
        2. Any additional data needed for next steps
        3. Confidence score for the result
        4. Explanation of the reasoning
        """

class AIPortfolioOptimizer(AIStepExecutor):
    """AI-powered portfolio optimization step executor."""

    def execute(self, step: WorkflowStep, context: WorkflowContext) -> Dict[str, Any]:
        """Execute AI portfolio optimization."""

        # Get portfolio data from context
        profile = context.data.get("profile")
        products = context.data.get("products", [])
        constraints = context.data.get("constraints", {})

        # Generate optimization prompt
        prompt = self._generate_optimization_prompt(profile, products, constraints)

        # Execute AI optimization
        optimization_result = self.llm_client.optimize(prompt)

        return {
            "optimized_allocation": optimization_result["allocation"],
            "expected_return": optimization_result["return"],
            "risk_metrics": optimization_result["risk"],
            "ai_explanation": optimization_result["explanation"],
            "confidence_score": optimization_result["confidence"]
        }
```

### **Phase 3: Advanced Features (Weeks 35-36)**

#### **3.1 Workflow Analytics and Learning**

```python
# src/core/workflow_analytics.py
class WorkflowAnalytics:
    """Analytics and learning system for workflows."""

    def __init__(self):
        self.metrics_collector = WorkflowMetricsCollector()
        self.pattern_analyzer = WorkflowPatternAnalyzer()
        self.recommendation_engine = WorkflowRecommendationEngine()

    def analyze_workflow_performance(self, workflow_id: str) -> Dict[str, Any]:
        """Analyze performance metrics for a workflow."""
        executions = self.metrics_collector.get_executions(workflow_id)

        return {
            "completion_rate": self._calculate_completion_rate(executions),
            "average_duration": self._calculate_average_duration(executions),
            "step_success_rates": self._calculate_step_success_rates(executions),
            "user_satisfaction": self._calculate_user_satisfaction(executions),
            "common_failure_points": self._identify_failure_points(executions)
        }

    def learn_user_preferences(self, user_id: str) -> Dict[str, Any]:
        """Learn user workflow preferences from execution history."""
        user_executions = self.metrics_collector.get_user_executions(user_id)

        return {
            "preferred_workflow_types": self._analyze_preferred_types(user_executions),
            "optimal_guidance_level": self._analyze_guidance_preferences(user_executions),
            "common_workflow_patterns": self._analyze_workflow_patterns(user_executions),
            "ai_assistance_preferences": self._analyze_ai_preferences(user_executions)
        }

    def recommend_workflows(self, user_id: str, context: Dict[str, Any]) -> List[WorkflowDefinition]:
        """Recommend workflows based on user preferences and context."""
        user_preferences = self.learn_user_preferences(user_id)

        return self.recommendation_engine.recommend(
            user_preferences=user_preferences,
            context=context,
            available_workflows=self._get_available_workflows()
        )
```

#### **3.2 Workflow Marketplace and Sharing**

```python
# src/core/workflow_marketplace.py
class WorkflowMarketplace:
    """Marketplace for sharing and discovering workflows."""

    def __init__(self):
        self.workflow_repository = WorkflowRepository()
        self.rating_system = WorkflowRatingSystem()
        self.search_engine = WorkflowSearchEngine()

    def publish_workflow(self, workflow: WorkflowDefinition, author_id: str) -> str:
        """Publish a workflow to the marketplace."""
        # Validate workflow
        if not self._validate_workflow_for_publication(workflow):
            raise WorkflowValidationError("Workflow not suitable for publication")

        # Add marketplace metadata
        marketplace_workflow = self._add_marketplace_metadata(workflow, author_id)

        # Store in repository
        workflow_id = self.workflow_repository.store(marketplace_workflow)

        return workflow_id

    def search_workflows(self, query: Dict[str, Any]) -> List[WorkflowDefinition]:
        """Search for workflows in the marketplace."""
        return self.search_engine.search(query)

    def rate_workflow(self, workflow_id: str, user_id: str, rating: int, review: str = None):
        """Rate and review a workflow."""
        self.rating_system.add_rating(workflow_id, user_id, rating, review)

    def get_trending_workflows(self, category: str = None) -> List[WorkflowDefinition]:
        """Get trending workflows in a category."""
        return self.workflow_repository.get_trending(category)
```

---

## 🎨 **Frontend Implementation**

### **Workflow Engine UI Components**

```tsx
// frontend/src/components/workflows/WorkflowEngine.tsx
interface WorkflowEngineProps {
  workflow: WorkflowDefinition;
  context: WorkflowContext;
  onStepComplete: (stepId: string, result: any) => void;
  onWorkflowComplete: (result: any) => void;
}

const WorkflowEngine: React.FC<WorkflowEngineProps> = ({
  workflow,
  context,
  onStepComplete,
  onWorkflowComplete
}) => {
  const [currentStep, setCurrentStep] = useState<string | null>(workflow.entry_points[0]);
  const [stepResults, setStepResults] = useState<Record<string, any>>({});
  const [workflowStatus, setWorkflowStatus] = useState<WorkflowStatus>(WorkflowStatus.PENDING);

  const executeStep = async (stepId: string) => {
    const step = workflow.steps.find(s => s.id === stepId);
    if (!step) return;

    setWorkflowStatus(WorkflowStatus.RUNNING);

    try {
      const result = await executeStepByType(step, context, stepResults);

      setStepResults(prev => ({ ...prev, [stepId]: result }));
      onStepComplete(stepId, result);

      const nextStep = determineNextStep(workflow, stepId, result);

      if (nextStep) {
        setCurrentStep(nextStep);
      } else {
        setWorkflowStatus(WorkflowStatus.COMPLETED);
        onWorkflowComplete(stepResults);
      }
    } catch (error) {
      setWorkflowStatus(WorkflowStatus.FAILED);
      console.error('Step execution failed:', error);
    }
  };

  return (
    <div className="workflow-engine">
      <WorkflowProgress
        workflow={workflow}
        currentStep={currentStep}
        status={workflowStatus}
      />

      <div className="workflow-content">
        {currentStep && (
          <WorkflowStepRenderer
            step={workflow.steps.find(s => s.id === currentStep)!}
            context={context}
            results={stepResults}
            onComplete={executeStep}
          />
        )}
      </div>
    </div>
  );
};

// AI Step Component
const AIStep: React.FC<AIStepProps> = ({ step, context, onComplete }) => {
  const [aiResult, setAiResult] = useState<any>(null);
  const [isLoading, setIsLoading] = useState(false);

  const executeAI = async () => {
    setIsLoading(true);

    try {
      const result = await fetch('/api/workflows/ai/execute-step', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          step_id: step.id,
          context: context,
          prompt: step.ai_prompt
        })
      });

      const data = await result.json();
      setAiResult(data);
      onComplete(step.id, data);
    } catch (error) {
      console.error('AI execution failed:', error);
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <div className="ai-step">
      <h3>{step.name}</h3>
      <p>{step.description}</p>

      {isLoading ? (
        <div className="ai-loading">
          <Spinner />
          <p>AI is analyzing and optimizing...</p>
        </div>
      ) : (
        <div className="ai-results">
          {aiResult && (
            <AIResultDisplay
              result={aiResult}
              onAccept={() => onComplete(step.id, aiResult)}
            />
          )}
        </div>
      )}
    </div>
  );
};
```

---

## 🔧 **API Endpoints**

### **Workflow Management**

```python
# api/src/api/v1/endpoints/workflows.py
@router.post("/workflows/generate")
async def generate_ai_workflow(requirements: WorkflowRequirements):
    """Generate a custom workflow using AI."""
    workflow_generator = AIWorkflowGenerator()
    workflow = workflow_generator.generate(requirements.dict())
    return workflow

@router.post("/workflows/{workflow_id}/execute")
async def execute_workflow(workflow_id: str, context: WorkflowContext):
    """Execute a workflow with given context."""
    workflow_engine = WorkflowEngine()
    result = workflow_engine.execute_workflow(workflow_id, context)
    return result

@router.get("/workflows/templates")
async def get_workflow_templates(category: str = None):
    """Get available workflow templates."""
    template_service = WorkflowTemplateService()
    return template_service.get_templates(category)

@router.post("/workflows/ai/optimize")
async def ai_optimize_portfolio(optimization_request: AIOptimizationRequest):
    """AI-powered portfolio optimization."""
    ai_optimizer = AIPortfolioOptimizer()
    result = ai_optimizer.optimize(optimization_request)
    return result

@router.get("/workflows/marketplace/search")
async def search_workflows(query: WorkflowSearchQuery):
    """Search workflows in the marketplace."""
    marketplace = WorkflowMarketplace()
    return marketplace.search_workflows(query.dict())
```

---

## 📊 **Success Criteria**

### **Phase 1 Success Criteria**
- [ ] Workflow engine can execute basic workflows
- [ ] Step executors are pluggable and extensible
- [ ] Workflow context is properly managed
- [ ] Basic workflow templates are available

### **Phase 2 Success Criteria**
- [ ] AI can generate custom workflows based on requirements
- [ ] AI-powered steps execute correctly
- [ ] Workflow recommendations work based on user preferences
- [ ] Dynamic workflow adaptation is functional

### **Phase 3 Success Criteria**
- [ ] Workflow analytics provide meaningful insights
- [ ] User preferences are learned and applied
- [ ] Workflow marketplace is functional
- [ ] Advanced AI features work correctly

---

## 🚀 **Integration with Existing Features**

### **Portfolio Creation Integration**
```python
# Enhanced Portfolio Creation with Workflow Engine
class PortfolioCreationWorkflow:
    @staticmethod
    def create_with_workflow(user_requirements: Dict[str, Any]) -> WorkflowDefinition:
        """Create portfolio creation workflow based on user requirements."""
        ai_generator = AIWorkflowGenerator()

        requirements = {
            "feature": "portfolio_creation",
            "user_experience": user_requirements.get("experience", "beginner"),
            "ai_assistance": user_requirements.get("ai_level", "moderate"),
            "customization": user_requirements.get("customization", "standard")
        }

        return ai_generator.generate(requirements)
```

### **Allocation Framework Integration**
```python
# Allocation Framework as Workflow Steps
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
                "template_integration": True
            },
            dependencies=["profile_assessment"]
        )
```

---

## 📋 **Dependencies & Integration**

### **Required Dependencies**
- **Story-007 (Portfolio Page)**: Workflow integration with portfolio creation
- **Tech-036 (Authentication)**: User management and security
- **Story-008 (Allocation Framework)**: Framework integration with workflows

### **Integration Points**
- **Portfolio Creation**: Workflow-driven portfolio creation process
- **Risk Assessment**: AI-powered risk assessment workflows
- **Allocation Management**: Framework-based allocation workflows
- **Analytics**: Workflow performance and user behavior analytics

---

**Document Version**: 1.0
**Last Updated**: January 21, 2025
**Next Review**: After Phase 1 completion
**Maintained By**: Development Team
