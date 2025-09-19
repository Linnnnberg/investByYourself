'use client';

import React, { useState } from 'react';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Badge } from '@/components/ui/badge';
import { MinimalWorkflowEngine } from '@/components/workflows';

// Mock workflow definitions (in real app, these would come from API)
const mockWorkflows = [
  {
    id: 'portfolio_creation_basic',
    name: 'Portfolio Creation with Allocation Framework',
    description: 'Basic portfolio creation workflow with allocation framework support',
    steps: [
      {
        id: 'profile_assessment',
        name: 'Investment Profile Assessment',
        step_type: 'data_collection' as const,
        description: 'Collect user investment profile data',
        config: {
          required_fields: ['risk_tolerance', 'time_horizon', 'investment_goals']
        },
        dependencies: []
      },
      {
        id: 'allocation_method_choice',
        name: 'Allocation Method Selection',
        step_type: 'decision' as const,
        description: 'Choose between framework, manual, or hybrid allocation',
        config: {
          options: ['framework', 'manual', 'hybrid'],
          default: 'framework'
        },
        dependencies: ['profile_assessment']
      },
      {
        id: 'framework_selection',
        name: 'Framework Selection',
        step_type: 'decision' as const,
        description: 'Select allocation framework template',
        config: {
          templates: [
            { id: 'conservative', name: 'Conservative', description: '60% Bonds, 35% Equity, 5% Alternatives' },
            { id: 'balanced', name: 'Balanced', description: '60% Equity, 35% Bonds, 5% Alternatives' },
            { id: 'growth', name: 'Growth', description: '80% Equity, 15% Bonds, 5% Alternatives' }
          ]
        },
        dependencies: ['allocation_method_choice']
      },
      {
        id: 'product_selection',
        name: 'Product Selection',
        step_type: 'user_interaction' as const,
        description: 'Select investment products',
        config: {
          search_enabled: true,
          filters: ['asset_class', 'sector', 'region']
        },
        dependencies: ['allocation_method_choice']
      },
      {
        id: 'portfolio_validation',
        name: 'Portfolio Validation',
        step_type: 'validation' as const,
        description: 'Validate final portfolio configuration',
        config: {
          weight_validation: true,
          constraint_validation: true
        },
        dependencies: ['framework_selection', 'product_selection']
      }
    ],
    entry_points: ['profile_assessment'],
    exit_points: ['portfolio_validation']
  },
  {
    id: 'framework_builder',
    name: 'Custom Framework Builder',
    description: 'Build custom allocation frameworks',
    steps: [
      {
        id: 'framework_type_selection',
        name: 'Framework Type Selection',
        step_type: 'decision' as const,
        description: 'Choose framework type (asset class, sector, geographic, etc.)',
        config: {
          types: ['asset_class', 'sector', 'geographic', 'market_cap', 'hybrid']
        },
        dependencies: []
      },
      {
        id: 'bucket_definition',
        name: 'Bucket Definition',
        step_type: 'user_interaction' as const,
        description: 'Define allocation buckets and weights',
        config: {
          drag_drop_enabled: true,
          weight_validation: true
        },
        dependencies: ['framework_type_selection']
      },
      {
        id: 'constraint_setup',
        name: 'Constraint Setup',
        step_type: 'user_interaction' as const,
        description: 'Set up framework constraints',
        config: {
          constraint_types: ['min_weight', 'max_weight', 'sector_caps', 'liquidity_requirements']
        },
        dependencies: ['bucket_definition']
      },
      {
        id: 'framework_validation',
        name: 'Framework Validation',
        step_type: 'validation' as const,
        description: 'Validate framework configuration',
        config: {
          weight_sum_validation: true,
          constraint_validation: true
        },
        dependencies: ['constraint_setup']
      }
    ],
    entry_points: ['framework_type_selection'],
    exit_points: ['framework_validation']
  }
];

const WorkflowsPage: React.FC = () => {
  const [selectedWorkflow, setSelectedWorkflow] = useState<any>(null);
  const [workflowResults, setWorkflowResults] = useState<any>(null);
  const [workflowError, setWorkflowError] = useState<string | null>(null);

  const mockContext = {
    user_id: 'demo_user',
    session_id: 'demo_session',
    data: {
      profile_data: {
        risk_tolerance: 'moderate',
        time_horizon: '10_years',
        investment_goals: 'retirement'
      }
    },
    created_at: new Date().toISOString()
  };

  const handleWorkflowComplete = (result: any) => {
    setWorkflowResults(result);
    console.log('Workflow completed:', result);
  };

  const handleWorkflowError = (error: any) => {
    setWorkflowError(error.message || 'Unknown error');
    console.error('Workflow error:', error);
  };

  const handleStepComplete = (stepId: string, result: any) => {
    console.log(`Step ${stepId} completed:`, result);
  };

  const resetWorkflow = () => {
    setSelectedWorkflow(null);
    setWorkflowResults(null);
    setWorkflowError(null);
  };

  if (selectedWorkflow) {
    return (
      <div className="container mx-auto py-8">
        <div className="mb-6">
          <Button onClick={resetWorkflow} variant="outline" className="mb-4">
            ← Back to Workflows
          </Button>
        </div>

        <MinimalWorkflowEngine
          workflow={selectedWorkflow}
          context={mockContext}
          onComplete={handleWorkflowComplete}
          onError={handleWorkflowError}
          onStepComplete={handleStepComplete}
        />

        {workflowResults && (
          <Card className="mt-6">
            <CardHeader>
              <CardTitle>Workflow Results</CardTitle>
              <CardDescription>Detailed results from workflow execution</CardDescription>
            </CardHeader>
            <CardContent>
              <pre className="bg-gray-100 p-4 rounded text-sm overflow-auto">
                {JSON.stringify(workflowResults, null, 2)}
              </pre>
            </CardContent>
          </Card>
        )}

        {workflowError && (
          <Card className="mt-6 border-red-200">
            <CardHeader>
              <CardTitle className="text-red-600">Workflow Error</CardTitle>
            </CardHeader>
            <CardContent>
              <p className="text-red-800">{workflowError}</p>
            </CardContent>
          </Card>
        )}
      </div>
    );
  }

  return (
    <div className="container mx-auto py-8">
      <div className="mb-8">
        <h1 className="text-3xl font-bold mb-2">Workflow Engine Demo</h1>
        <p className="text-muted-foreground">
          Test the minimal workflow engine with allocation framework workflows.
        </p>
      </div>

      <div className="grid gap-6 md:grid-cols-2">
        {mockWorkflows.map((workflow) => (
          <Card key={workflow.id} className="hover:shadow-lg transition-shadow">
            <CardHeader>
              <CardTitle className="flex items-center justify-between">
                {workflow.name}
                <Badge variant="outline">
                  {workflow.steps.length} steps
                </Badge>
              </CardTitle>
              <CardDescription>{workflow.description}</CardDescription>
            </CardHeader>
            <CardContent className="space-y-4">
              <div>
                <h4 className="font-semibold mb-2">Workflow Steps:</h4>
                <ul className="space-y-1 text-sm text-muted-foreground">
                  {workflow.steps.map((step, index) => (
                    <li key={step.id} className="flex items-center space-x-2">
                      <span className="w-6 h-6 bg-blue-100 text-blue-600 rounded-full flex items-center justify-center text-xs font-semibold">
                        {index + 1}
                      </span>
                      <span>{step.name}</span>
                      <Badge variant="secondary" className="text-xs">
                        {step.step_type.replace('_', ' ')}
                      </Badge>
                    </li>
                  ))}
                </ul>
              </div>

              <div className="pt-4 border-t">
                <Button
                  onClick={() => setSelectedWorkflow(workflow)}
                  className="w-full"
                >
                  Start Workflow
                </Button>
              </div>
            </CardContent>
          </Card>
        ))}
      </div>

      <Card className="mt-8">
        <CardHeader>
          <CardTitle>About the Workflow Engine</CardTitle>
          <CardDescription>
            This is a minimal viable implementation of the workflow engine for allocation framework support.
          </CardDescription>
        </CardHeader>
        <CardContent className="space-y-4">
          <div className="grid gap-4 md:grid-cols-2">
            <div>
              <h4 className="font-semibold mb-2">Features Implemented:</h4>
              <ul className="space-y-1 text-sm text-muted-foreground">
                <li>✅ Step-by-step workflow execution</li>
                <li>✅ Progress tracking and status management</li>
                <li>✅ Error handling and recovery</li>
                <li>✅ Multiple step types (data collection, decision, validation, user interaction)</li>
                <li>✅ Workflow completion and results display</li>
              </ul>
            </div>
            <div>
              <h4 className="font-semibold mb-2">Next Steps:</h4>
              <ul className="space-y-1 text-sm text-muted-foreground">
                <li>🔲 Enhanced step components</li>
                <li>🔲 API integration</li>
                <li>🔲 Database persistence</li>
                <li>🔲 Real-time updates</li>
                <li>🔲 Advanced validation</li>
              </ul>
            </div>
          </div>
        </CardContent>
      </Card>
    </div>
  );
};

export default WorkflowsPage;
