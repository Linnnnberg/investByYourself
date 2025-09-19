'use client';

import React, { useState, useEffect } from 'react';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Badge } from '@/components/ui/badge';

// Types for workflow engine
interface WorkflowStep {
  id: string;
  name: string;
  step_type: 'data_collection' | 'decision' | 'validation' | 'user_interaction';
  description: string;
  config: Record<string, any>;
  dependencies: string[];
}

interface WorkflowDefinition {
  id: string;
  name: string;
  description: string;
  steps: WorkflowStep[];
  entry_points: string[];
  exit_points: string[];
}

interface WorkflowContext {
  user_id: string;
  session_id: string;
  data: Record<string, any>;
  created_at: string;
}

interface WorkflowExecutionResult {
  status: 'completed' | 'failed' | 'running';
  result?: any;
  error?: string;
}

interface MinimalWorkflowEngineProps {
  workflow: WorkflowDefinition;
  context: WorkflowContext;
  onComplete: (result: any) => void;
  onError: (error: any) => void;
  onStepComplete?: (stepId: string, result: any) => void;
}

const MinimalWorkflowEngine: React.FC<MinimalWorkflowEngineProps> = ({
  workflow,
  context,
  onComplete,
  onError,
  onStepComplete
}) => {
  const [currentStep, setCurrentStep] = useState<string | null>(workflow.entry_points[0]);
  const [stepResults, setStepResults] = useState<Record<string, any>>({});
  const [isLoading, setIsLoading] = useState(false);
  const [workflowStatus, setWorkflowStatus] = useState<'pending' | 'running' | 'completed' | 'failed'>('pending');
  const [error, setError] = useState<string | null>(null);

  // Get current step object
  const currentStepObj = workflow.steps.find(step => step.id === currentStep);

  // Calculate progress
  const progress = currentStep ?
    ((workflow.steps.findIndex(step => step.id === currentStep) + 1) / workflow.steps.length) * 100 : 0;

  const executeStep = async (stepId: string) => {
    if (!currentStepObj) return;

    setIsLoading(true);
    setError(null);

    try {
      // For MVP, we'll simulate step execution
      // In the future, this will call the actual API
      const result = await simulateStepExecution(currentStepObj, context, stepResults);

      setStepResults(prev => ({ ...prev, [stepId]: result }));

      if (onStepComplete) {
        onStepComplete(stepId, result);
      }

      // Move to next step
      const nextStep = getNextStep(workflow, stepId);
      if (nextStep) {
        setCurrentStep(nextStep);
      } else {
        // Workflow completed
        setWorkflowStatus('completed');
        onComplete(stepResults);
      }
    } catch (error) {
      const errorMessage = error instanceof Error ? error.message : 'Unknown error';
      setError(errorMessage);
      setWorkflowStatus('failed');
      onError(error);
    } finally {
      setIsLoading(false);
    }
  };

  const getNextStep = (workflow: WorkflowDefinition, currentStepId: string): string | null => {
    const currentIndex = workflow.steps.findIndex(step => step.id === currentStepId);
    if (currentIndex === -1 || currentIndex >= workflow.steps.length - 1) {
      return null;
    }
    return workflow.steps[currentIndex + 1].id;
  };

  const simulateStepExecution = async (step: WorkflowStep, context: WorkflowContext, results: Record<string, any>) => {
    // Simulate API call delay
    await new Promise(resolve => setTimeout(resolve, 1000));

    // Mock step execution based on step type
    switch (step.step_type) {
      case 'data_collection':
        return {
          status: 'completed',
          step_type: 'data_collection',
          collected_data: {
            risk_tolerance: 'moderate',
            time_horizon: '10_years',
            investment_goals: 'retirement'
          },
          executed_at: new Date().toISOString()
        };

      case 'decision':
        return {
          status: 'completed',
          step_type: 'decision',
          decision: 'framework',
          options: step.config.options || [],
          executed_at: new Date().toISOString()
        };

      case 'validation':
        return {
          status: 'completed',
          step_type: 'validation',
          validation_results: {
            weight_validation: { passed: true },
            constraint_validation: { passed: true }
          },
          all_passed: true,
          executed_at: new Date().toISOString()
        };

      case 'user_interaction':
        return {
          status: 'completed',
          step_type: 'user_interaction',
          user_input: {
            selected_products: ['VTI', 'BND', 'VXUS'],
            weights: { VTI: 0.6, BND: 0.3, VXUS: 0.1 }
          },
          executed_at: new Date().toISOString()
        };

      default:
        throw new Error(`Unknown step type: ${step.step_type}`);
    }
  };

  const handleStepAction = (action: string, data?: any) => {
    if (action === 'execute') {
      executeStep(currentStep!);
    } else if (action === 'skip') {
      // Skip current step and move to next
      const nextStep = getNextStep(workflow, currentStep!);
      if (nextStep) {
        setCurrentStep(nextStep);
      } else {
        setWorkflowStatus('completed');
        onComplete(stepResults);
      }
    }
  };

  const startWorkflow = () => {
    setWorkflowStatus('running');
    executeStep(currentStep!);
  };

  const resetWorkflow = () => {
    setCurrentStep(workflow.entry_points[0]);
    setStepResults({});
    setWorkflowStatus('pending');
    setError(null);
  };

  if (workflowStatus === 'pending') {
    return (
      <Card className="w-full max-w-4xl mx-auto">
        <CardHeader>
          <CardTitle>{workflow.name}</CardTitle>
          <CardDescription>{workflow.description}</CardDescription>
        </CardHeader>
        <CardContent className="space-y-4">
          <div className="text-center">
            <p className="text-muted-foreground mb-4">
              This workflow will guide you through the portfolio creation process with allocation framework support.
            </p>
            <Button onClick={startWorkflow} size="lg">
              Start Workflow
            </Button>
          </div>
        </CardContent>
      </Card>
    );
  }

  if (workflowStatus === 'completed') {
    return (
      <Card className="w-full max-w-4xl mx-auto">
        <CardHeader>
          <CardTitle className="text-green-600">Workflow Completed!</CardTitle>
          <CardDescription>All steps have been executed successfully.</CardDescription>
        </CardHeader>
        <CardContent className="space-y-4">
          <div className="space-y-2">
            <h4 className="font-semibold">Results Summary:</h4>
            {Object.entries(stepResults).map(([stepId, result]) => (
              <div key={stepId} className="flex items-center justify-between p-2 bg-gray-50 rounded">
                <span className="font-medium">{stepId}</span>
                <Badge variant={result.status === 'completed' ? 'default' : 'destructive'}>
                  {result.status}
                </Badge>
              </div>
            ))}
          </div>
          <Button onClick={resetWorkflow} variant="outline">
            Start Over
          </Button>
        </CardContent>
      </Card>
    );
  }

  if (workflowStatus === 'failed') {
    return (
      <Card className="w-full max-w-4xl mx-auto">
        <CardHeader>
          <CardTitle className="text-red-600">Workflow Failed</CardTitle>
          <CardDescription>An error occurred during workflow execution.</CardDescription>
        </CardHeader>
        <CardContent className="space-y-4">
          <div className="p-4 bg-red-50 border border-red-200 rounded">
            <p className="text-red-800">{error}</p>
          </div>
          <Button onClick={resetWorkflow} variant="outline">
            Try Again
          </Button>
        </CardContent>
      </Card>
    );
  }

  return (
    <Card className="w-full max-w-4xl mx-auto">
      <CardHeader>
        <CardTitle>{workflow.name}</CardTitle>
        <CardDescription>{workflow.description}</CardDescription>
        <div className="flex items-center justify-between">
          <div className="flex items-center space-x-2">
            <span className="text-sm text-muted-foreground">Progress:</span>
            <div className="w-32 bg-gray-200 rounded-full h-2">
              <div
                className="bg-blue-600 h-2 rounded-full transition-all duration-300"
                style={{ width: `${progress}%` }}
              />
            </div>
            <span className="text-sm text-muted-foreground">{Math.round(progress)}%</span>
          </div>
          <Badge variant="outline">
            Step {workflow.steps.findIndex(step => step.id === currentStep) + 1} of {workflow.steps.length}
          </Badge>
        </div>
      </CardHeader>
      <CardContent className="space-y-6">
        {currentStepObj && (
          <div className="space-y-4">
            <div>
              <h3 className="text-lg font-semibold">{currentStepObj.name}</h3>
              <p className="text-muted-foreground">{currentStepObj.description}</p>
              <Badge variant="secondary" className="mt-2">
                {currentStepObj.step_type.replace('_', ' ').toUpperCase()}
              </Badge>
            </div>

            <WorkflowStepComponent
              step={currentStepObj}
              context={context}
              onAction={handleStepAction}
              isLoading={isLoading}
            />

            {error && (
              <div className="p-4 bg-red-50 border border-red-200 rounded">
                <p className="text-red-800">{error}</p>
              </div>
            )}
          </div>
        )}
      </CardContent>
    </Card>
  );
};

// Basic step component (will be enhanced in next step)
interface WorkflowStepComponentProps {
  step: WorkflowStep;
  context: WorkflowContext;
  onAction: (action: string, data?: any) => void;
  isLoading: boolean;
}

const WorkflowStepComponent: React.FC<WorkflowStepComponentProps> = ({
  step,
  context,
  onAction,
  isLoading
}) => {
  const renderStepByType = () => {
    switch (step.step_type) {
      case 'data_collection':
        return <DataCollectionStep step={step} context={context} onAction={onAction} isLoading={isLoading} />;
      case 'decision':
        return <DecisionStep step={step} context={context} onAction={onAction} isLoading={isLoading} />;
      case 'validation':
        return <ValidationStep step={step} context={context} onAction={onAction} isLoading={isLoading} />;
      case 'user_interaction':
        return <UserInteractionStep step={step} context={context} onAction={onAction} isLoading={isLoading} />;
      default:
        return <div>Unknown step type: {step.step_type}</div>;
    }
  };

  return (
    <div className="workflow-step">
      {renderStepByType()}
    </div>
  );
};

// Placeholder step components (will be implemented in next step)
const DataCollectionStep: React.FC<any> = ({ step, onAction, isLoading }) => (
  <div className="space-y-4">
    <p className="text-sm text-muted-foreground">
      This step will collect your investment profile data.
    </p>
    <Button onClick={() => onAction('execute')} disabled={isLoading}>
      {isLoading ? 'Collecting Data...' : 'Collect Data'}
    </Button>
  </div>
);

const DecisionStep: React.FC<any> = ({ step, onAction, isLoading }) => (
  <div className="space-y-4">
    <p className="text-sm text-muted-foreground">
      This step requires a decision. Choose your preferred option.
    </p>
    <Button onClick={() => onAction('execute')} disabled={isLoading}>
      {isLoading ? 'Processing Decision...' : 'Make Decision'}
    </Button>
  </div>
);

const ValidationStep: React.FC<any> = ({ step, onAction, isLoading }) => (
  <div className="space-y-4">
    <p className="text-sm text-muted-foreground">
      This step will validate your portfolio configuration.
    </p>
    <Button onClick={() => onAction('execute')} disabled={isLoading}>
      {isLoading ? 'Validating...' : 'Validate Portfolio'}
    </Button>
  </div>
);

const UserInteractionStep: React.FC<any> = ({ step, onAction, isLoading }) => (
  <div className="space-y-4">
    <p className="text-sm text-muted-foreground">
      This step requires user interaction. Please provide your input.
    </p>
    <Button onClick={() => onAction('execute')} disabled={isLoading}>
      {isLoading ? 'Processing...' : 'Continue'}
    </Button>
  </div>
);

export default MinimalWorkflowEngine;
