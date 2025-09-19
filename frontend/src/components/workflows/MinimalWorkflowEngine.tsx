'use client';

import React, { useState, useEffect } from 'react';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Badge } from '@/components/ui/badge';
import { Alert, AlertDescription } from '@/components/ui/alert';
import {
  DecisionStepComponent,
  DataCollectionStepComponent,
  ValidationStepComponent,
  UserInteractionStepComponent
} from './steps';
import { useWorkflowExecution } from '@/hooks/useWorkflowExecution';
import {
  WorkflowDefinition,
  WorkflowContext,
  WorkflowStatus,
  WorkflowError
} from '@/types/workflow';

// Types for workflow engine
import { WorkflowStep as WorkflowStepType, WorkflowStepType as StepType } from '@/types/workflow';

interface WorkflowStep {
  id: string;
  name: string;
  step_type: StepType;
  description?: string;
  config: Record<string, any>;
  dependencies: string[];
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
  const [workflowStatus, setWorkflowStatus] = useState<'pending' | 'running' | 'completed' | 'failed'>('pending');
  const [error, setError] = useState<string | null>(null);

  // Use the workflow execution hook
  const {
    execution,
    status,
    isLoading,
    error: apiError,
    executeWorkflow,
    executeStep: executeStepApi,
    pauseWorkflow,
    resumeWorkflow,
    cancelWorkflow,
    refreshStatus
  } = useWorkflowExecution({
    onComplete: (result) => {
      setWorkflowStatus('completed');
      onComplete(result);
    },
    onError: (err) => {
      setWorkflowStatus('failed');
      setError(err.message);
      onError(err);
    },
    onStepComplete: (stepId, result) => {
      setStepResults(prev => ({ ...prev, [stepId]: result }));
      onStepComplete?.(stepId, result);
    },
    onStatusUpdate: (status) => {
      // Update current step based on status
      if (status.current_step) {
        setCurrentStep(status.current_step);
      }

      // Update workflow status
      if (status.status === 'completed') {
        setWorkflowStatus('completed');
      } else if (status.status === 'failed') {
        setWorkflowStatus('failed');
        setError(status.error_message || 'Workflow execution failed');
      } else if (status.status === 'running') {
        setWorkflowStatus('running');
      }
    }
  });

  // Get current step object
  const currentStepObj = workflow.steps.find(step => step.id === currentStep);

  // Calculate progress
  const progress = currentStep ?
    ((workflow.steps.findIndex(step => step.id === currentStep) + 1) / workflow.steps.length) * 100 : 0;

  const handleStepAction = (action: string, data?: any) => {
    if (action === 'continue') {
      // Move to next step
      const nextStep = getNextStep(workflow, currentStep!);
      if (nextStep) {
        setCurrentStep(nextStep);
      } else {
        setWorkflowStatus('completed');
        onComplete(stepResults);
      }
    } else if (action === 'back') {
      // Move to previous step
      const prevStep = getPreviousStep(workflow, currentStep!);
      if (prevStep) {
        setCurrentStep(prevStep);
      }
    } else if (action === 'data_change') {
      // Update context data
      // This would typically update the execution context via API
      console.log('Data changed:', data);
    } else if (action === 'selection_change') {
      // Update selection data
      console.log('Selection changed:', data);
    } else if (action === 'retry') {
      // Retry current step
      if (currentStep && execution) {
        executeStepApi({
          execution_id: execution.execution_id,
          workflow_id: workflow.id,
          step_id: currentStep,
          context: context,
          step_input: data || {}
        });
      }
    }
  };

  const getNextStep = (workflow: WorkflowDefinition, currentStepId: string): string | null => {
    const currentIndex = workflow.steps.findIndex(step => step.id === currentStepId);
    if (currentIndex === -1 || currentIndex >= workflow.steps.length - 1) {
      return null;
    }
    return workflow.steps[currentIndex + 1].id;
  };

  const getPreviousStep = (workflow: WorkflowDefinition, currentStepId: string): string | null => {
    const currentIndex = workflow.steps.findIndex(step => step.id === currentStepId);
    if (currentIndex <= 0) {
      return null;
    }
    return workflow.steps[currentIndex - 1].id;
  };

  const startWorkflow = async () => {
    try {
      setWorkflowStatus('running');
      setError(null);

      await executeWorkflow({
        workflow_id: workflow.id,
        context: context
      });
    } catch (err) {
      const errorMessage = err instanceof Error ? err.message : 'Unknown error';
      setError(errorMessage);
      setWorkflowStatus('failed');
      onError(err);
    }
  };

  const resetWorkflow = () => {
    setCurrentStep(workflow.entry_points[0]);
    setStepResults({});
    setWorkflowStatus('pending');
    setError(null);
  };

  // Handle API errors
  useEffect(() => {
    if (apiError) {
      setError(apiError.message);
      setWorkflowStatus('failed');
    }
  }, [apiError]);

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
            <Button
              onClick={startWorkflow}
              className="text-lg px-6 py-3"
              disabled={isLoading}
            >
              {isLoading ? 'Starting...' : 'Start Workflow'}
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
          <Alert variant="destructive">
            <AlertDescription>{error}</AlertDescription>
          </Alert>
          <div className="flex gap-2">
            <Button onClick={resetWorkflow} variant="outline">
              Try Again
            </Button>
            <Button onClick={refreshStatus} variant="outline">
              Refresh Status
            </Button>
          </div>
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
          <div className="flex items-center gap-2">
            <Badge variant="outline">
              Step {workflow.steps.findIndex(step => step.id === currentStep) + 1} of {workflow.steps.length}
            </Badge>
            {status && (
              <Badge variant={status.status === 'running' ? 'default' : 'secondary'}>
                {status.status}
              </Badge>
            )}
          </div>
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

            <EnhancedWorkflowStepComponent
              step={currentStepObj}
              context={context}
              onAction={handleStepAction}
              isLoading={isLoading}
            />

            {error && (
              <Alert variant="destructive">
                <AlertDescription>{error}</AlertDescription>
              </Alert>
            )}

            {/* Workflow Controls */}
            <div className="flex justify-between items-center pt-4 border-t">
              <div className="flex gap-2">
                <Button
                  variant="outline"
                  onClick={pauseWorkflow}
                  disabled={isLoading || !execution}
                >
                  Pause
                </Button>
                <Button
                  variant="outline"
                  onClick={resumeWorkflow}
                  disabled={isLoading || !execution}
                >
                  Resume
                </Button>
              </div>
              <div className="flex gap-2">
                <Button
                  variant="outline"
                  onClick={refreshStatus}
                  disabled={isLoading}
                >
                  Refresh
                </Button>
                <Button
                  variant="outline"
                  onClick={cancelWorkflow}
                  disabled={isLoading || !execution}
                  className="text-red-600 border-red-600 hover:bg-red-50"
                >
                  Cancel
                </Button>
              </div>
            </div>
          </div>
        )}
      </CardContent>
    </Card>
  );
};

// Enhanced step component using the new step components
interface EnhancedWorkflowStepComponentProps {
  step: WorkflowStep;
  context: WorkflowContext;
  onAction: (action: string, data?: any) => void;
  isLoading: boolean;
}

const EnhancedWorkflowStepComponent: React.FC<EnhancedWorkflowStepComponentProps> = ({
  step,
  context,
  onAction,
  isLoading
}) => {
  const handleStepAction = (action: string, data?: any) => {
    onAction(action, data);
  };

  const handleContinue = () => {
    handleStepAction('continue');
  };

  const handleBack = () => {
    handleStepAction('back');
  };

  const handleDataChange = (data: any) => {
    handleStepAction('data_change', data);
  };

  const handleSelectionChange = (selection: any) => {
    handleStepAction('selection_change', selection);
  };

  const renderStepByType = () => {
    switch (step.step_type) {
      case 'data_collection':
        return (
          <DataCollectionStepComponent
            stepId={step.id}
            title={step.name}
            description={step.description || ''}
            fields={step.config.fields || []}
            progress={step.config.progress}
            helpText={step.config.helpText}
            onDataChange={handleDataChange}
            onContinue={handleContinue}
            onBack={handleBack}
            isLoading={isLoading}
            initialData={context.data}
          />
        );
      case 'decision':
        return (
          <DecisionStepComponent
            stepId={step.id}
            title={step.name}
            description={step.description || ''}
            options={step.config.options || []}
            inputType={step.config.inputType || 'radio'}
            required={step.config.required !== false}
            helpText={step.config.helpText}
            validation={step.config.validation}
            onSelectionChange={handleSelectionChange}
            onContinue={handleContinue}
            onBack={handleBack}
            isLoading={isLoading}
            selectedValue={context.data[`decision_${step.id}`]}
          />
        );
      case 'validation':
        return (
          <ValidationStepComponent
            stepId={step.id}
            title={step.name}
            description={step.description || ''}
            results={step.config.results || []}
            overallStatus={step.config.overallStatus || 'pending'}
            summary={step.config.summary}
            onRetry={step.config.allowRetry ? () => handleStepAction('retry') : undefined}
            onContinue={handleContinue}
            onBack={handleBack}
            isLoading={isLoading}
            showDetails={step.config.showDetails !== false}
          />
        );
      case 'user_interaction':
        return (
          <UserInteractionStepComponent
            stepId={step.id}
            title={step.name}
            description={step.description || ''}
            items={step.config.items || []}
            selectionType={step.config.selectionType || 'single'}
            searchEnabled={step.config.searchEnabled !== false}
            filters={step.config.filters || []}
            maxSelections={step.config.maxSelections}
            minSelections={step.config.minSelections || 1}
            helpText={step.config.helpText}
            onSelectionChange={handleSelectionChange}
            onContinue={handleContinue}
            onBack={handleBack}
            isLoading={isLoading}
            initialSelection={context.data[`selection_${step.id}`] || []}
          />
        );
      default:
        return (
          <div className="p-4 border rounded-lg">
            <h3 className="font-semibold">{step.name}</h3>
            <p className="text-muted-foreground">{step.description}</p>
            <p className="text-sm text-red-500 mt-2">Unknown step type: {step.step_type}</p>
            <Button onClick={handleContinue} className="mt-4">
              Continue
            </Button>
          </div>
        );
    }
  };

  return (
    <div className="space-y-4">
      {renderStepByType()}
    </div>
  );
};

export default MinimalWorkflowEngine;
