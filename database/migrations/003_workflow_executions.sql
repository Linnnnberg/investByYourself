-- Migration: Add workflow execution tables
-- Created: 2025-01-21
-- Description: Database schema for workflow engine execution tracking

-- Workflow executions table
CREATE TABLE IF NOT EXISTS workflow_executions (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    workflow_id VARCHAR(255) NOT NULL,
    user_id VARCHAR(255) NOT NULL,
    session_id VARCHAR(255) NOT NULL,
    status VARCHAR(50) NOT NULL DEFAULT 'pending',
    current_step_id VARCHAR(255),
    progress DECIMAL(5,2) DEFAULT 0.0,
    context_data JSONB DEFAULT '{}',
    results JSONB DEFAULT '{}',
    error_message TEXT,
    started_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    completed_at TIMESTAMP WITH TIME ZONE,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

-- Workflow step executions table
CREATE TABLE IF NOT EXISTS workflow_step_executions (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    execution_id UUID NOT NULL REFERENCES workflow_executions(id) ON DELETE CASCADE,
    step_id VARCHAR(255) NOT NULL,
    step_name VARCHAR(255) NOT NULL,
    step_type VARCHAR(50) NOT NULL,
    status VARCHAR(50) NOT NULL DEFAULT 'pending',
    input_data JSONB DEFAULT '{}',
    output_data JSONB DEFAULT '{}',
    error_message TEXT,
    started_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    completed_at TIMESTAMP WITH TIME ZONE,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

-- Workflow definitions table (for storing custom workflows)
CREATE TABLE IF NOT EXISTS workflow_definitions (
    id VARCHAR(255) PRIMARY KEY,
    name VARCHAR(255) NOT NULL,
    description TEXT,
    version VARCHAR(50) DEFAULT '1.0',
    category VARCHAR(100),
    definition JSONB NOT NULL,
    is_active BOOLEAN DEFAULT true,
    created_by VARCHAR(255),
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

-- Workflow execution logs table (for audit trail)
CREATE TABLE IF NOT EXISTS workflow_execution_logs (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    execution_id UUID NOT NULL REFERENCES workflow_executions(id) ON DELETE CASCADE,
    step_id VARCHAR(255),
    action VARCHAR(100) NOT NULL,
    message TEXT,
    data JSONB DEFAULT '{}',
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

-- Indexes for performance
CREATE INDEX IF NOT EXISTS idx_workflow_executions_user_id ON workflow_executions(user_id);
CREATE INDEX IF NOT EXISTS idx_workflow_executions_workflow_id ON workflow_executions(workflow_id);
CREATE INDEX IF NOT EXISTS idx_workflow_executions_status ON workflow_executions(status);
CREATE INDEX IF NOT EXISTS idx_workflow_executions_created_at ON workflow_executions(created_at);

CREATE INDEX IF NOT EXISTS idx_workflow_step_executions_execution_id ON workflow_step_executions(execution_id);
CREATE INDEX IF NOT EXISTS idx_workflow_step_executions_step_id ON workflow_step_executions(step_id);
CREATE INDEX IF NOT EXISTS idx_workflow_step_executions_status ON workflow_step_executions(status);

CREATE INDEX IF NOT EXISTS idx_workflow_execution_logs_execution_id ON workflow_execution_logs(execution_id);
CREATE INDEX IF NOT EXISTS idx_workflow_execution_logs_created_at ON workflow_execution_logs(created_at);

-- Triggers for updated_at
CREATE OR REPLACE FUNCTION update_updated_at_column()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = CURRENT_TIMESTAMP;
    RETURN NEW;
END;
$$ language 'plpgsql';

CREATE TRIGGER update_workflow_executions_updated_at
    BEFORE UPDATE ON workflow_executions
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_workflow_step_executions_updated_at
    BEFORE UPDATE ON workflow_step_executions
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_workflow_definitions_updated_at
    BEFORE UPDATE ON workflow_definitions
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

-- Insert default workflow definitions
INSERT INTO workflow_definitions (id, name, description, version, category, definition, is_active, created_by) VALUES
(
    'portfolio_creation',
    'Portfolio Creation Workflow',
    'Complete workflow for creating a new investment portfolio with allocation framework',
    '1.0',
    'portfolio_management',
    '{
        "id": "portfolio_creation",
        "name": "Portfolio Creation Workflow",
        "description": "Complete workflow for creating a new investment portfolio with allocation framework",
        "steps": [
            {
                "id": "profile_assessment",
                "name": "Investment Profile Assessment",
                "step_type": "data_collection",
                "description": "Collect user investment profile and preferences",
                "config": {
                    "fields": [
                        {
                            "id": "risk_tolerance",
                            "label": "Risk Tolerance",
                            "type": "select",
                            "options": ["conservative", "moderate", "aggressive"],
                            "required": true
                        },
                        {
                            "id": "time_horizon",
                            "label": "Investment Time Horizon",
                            "type": "number",
                            "required": true,
                            "validation": {"min": 1, "max": 50}
                        },
                        {
                            "id": "investment_goals",
                            "label": "Investment Goals",
                            "type": "textarea",
                            "required": true
                        }
                    ]
                },
                "dependencies": []
            },
            {
                "id": "framework_selection",
                "name": "Allocation Framework Selection",
                "step_type": "decision",
                "description": "Select or create allocation framework",
                "config": {
                    "options": [
                        {"id": "balanced_60_40", "label": "Balanced 60/40", "value": "balanced_60_40"},
                        {"id": "aggressive_growth", "label": "Aggressive Growth", "value": "aggressive_growth"},
                        {"id": "conservative_income", "label": "Conservative Income", "value": "conservative_income"},
                        {"id": "custom", "label": "Create Custom Framework", "value": "custom"}
                    ],
                    "inputType": "radio",
                    "required": true
                },
                "dependencies": ["profile_assessment"]
            },
            {
                "id": "product_mapping",
                "name": "Product Mapping",
                "step_type": "user_interaction",
                "description": "Map investment products to framework buckets",
                "config": {
                    "items": [],
                    "selectionType": "multiple",
                    "maxSelections": 10,
                    "minSelections": 3
                },
                "dependencies": ["framework_selection"]
            },
            {
                "id": "portfolio_validation",
                "name": "Portfolio Validation",
                "step_type": "validation",
                "description": "Validate final portfolio configuration",
                "config": {
                    "results": [],
                    "overallStatus": "pending",
                    "allowRetry": true
                },
                "dependencies": ["product_mapping"]
            }
        ],
        "entry_points": ["profile_assessment"],
        "exit_points": ["portfolio_validation"]
    }',
    true,
    'system'
),
(
    'framework_builder',
    'Allocation Framework Builder',
    'Interactive workflow for building custom allocation frameworks',
    '1.0',
    'framework_management',
    '{
        "id": "framework_builder",
        "name": "Allocation Framework Builder",
        "description": "Interactive workflow for building custom allocation frameworks",
        "steps": [
            {
                "id": "framework_requirements",
                "name": "Framework Requirements",
                "step_type": "data_collection",
                "description": "Define framework requirements and constraints",
                "config": {
                    "fields": [
                        {
                            "id": "framework_name",
                            "label": "Framework Name",
                            "type": "text",
                            "required": true
                        },
                        {
                            "id": "target_risk_level",
                            "label": "Target Risk Level",
                            "type": "select",
                            "options": ["conservative", "moderate", "aggressive"],
                            "required": true
                        },
                        {
                            "id": "rebalancing_frequency",
                            "label": "Rebalancing Frequency",
                            "type": "select",
                            "options": ["monthly", "quarterly", "annually"],
                            "required": true
                        }
                    ]
                },
                "dependencies": []
            },
            {
                "id": "asset_allocation",
                "name": "Asset Allocation Setup",
                "step_type": "data_collection",
                "description": "Define asset class allocations",
                "config": {
                    "fields": [
                        {
                            "id": "stocks_percentage",
                            "label": "Stocks Percentage",
                            "type": "percentage",
                            "required": true,
                            "validation": {"min": 0, "max": 100}
                        },
                        {
                            "id": "bonds_percentage",
                            "label": "Bonds Percentage",
                            "type": "percentage",
                            "required": true,
                            "validation": {"min": 0, "max": 100}
                        },
                        {
                            "id": "alternatives_percentage",
                            "label": "Alternatives Percentage",
                            "type": "percentage",
                            "required": true,
                            "validation": {"min": 0, "max": 100}
                        }
                    ]
                },
                "dependencies": ["framework_requirements"]
            },
            {
                "id": "constraints_setup",
                "name": "Constraints Setup",
                "step_type": "data_collection",
                "description": "Define portfolio constraints and rules",
                "config": {
                    "fields": [
                        {
                            "id": "max_single_holding",
                            "label": "Max Single Holding (%)",
                            "type": "percentage",
                            "required": true,
                            "validation": {"min": 1, "max": 50}
                        },
                        {
                            "id": "min_diversification",
                            "label": "Minimum Diversification (number of holdings)",
                            "type": "number",
                            "required": true,
                            "validation": {"min": 3, "max": 50}
                        }
                    ]
                },
                "dependencies": ["asset_allocation"]
            },
            {
                "id": "framework_validation",
                "name": "Framework Validation",
                "step_type": "validation",
                "description": "Validate framework configuration",
                "config": {
                    "results": [],
                    "overallStatus": "pending",
                    "allowRetry": true
                },
                "dependencies": ["constraints_setup"]
            }
        ],
        "entry_points": ["framework_requirements"],
        "exit_points": ["framework_validation"]
    }',
    true,
    'system'
);

-- Comments
COMMENT ON TABLE workflow_executions IS 'Stores workflow execution instances and their current state';
COMMENT ON TABLE workflow_step_executions IS 'Stores individual step execution details within workflows';
COMMENT ON TABLE workflow_definitions IS 'Stores workflow templates and definitions';
COMMENT ON TABLE workflow_execution_logs IS 'Audit trail for workflow execution events';

COMMENT ON COLUMN workflow_executions.status IS 'Current execution status: pending, running, paused, completed, failed, cancelled';
COMMENT ON COLUMN workflow_executions.progress IS 'Execution progress percentage (0.00 to 100.00)';
COMMENT ON COLUMN workflow_executions.context_data IS 'Workflow context and user data';
COMMENT ON COLUMN workflow_executions.results IS 'Step execution results and outputs';

COMMENT ON COLUMN workflow_step_executions.step_type IS 'Type of workflow step: data_collection, decision, validation, user_interaction';
COMMENT ON COLUMN workflow_step_executions.input_data IS 'Step input data and configuration';
COMMENT ON COLUMN workflow_step_executions.output_data IS 'Step output data and results';
