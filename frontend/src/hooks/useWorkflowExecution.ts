'use client';

import { useState, useCallback } from 'react';
import { WorkflowContext, WorkflowDefinition } from '@/types/workflow';

interface WorkflowExecution {
  execution_id: string;
  workflow_id: string;
  user_id: string;
  status: string;
  progress: number;
  results: Record<string, any>;
  error_message?: string;
  started_at: string;
  completed_at?: string;
}

interface WorkflowStatus {
  execution_id: string;
  workflow_id: string;
  user_id: string;
  status: string;
  current_step?: string;
  progress: number;
  step_results: Record<string, any>;
  error_message?: string;
  started_at: string;
  completed_at?: string;
}

interface UseWorkflowExecutionOptions {
  onComplete?: (result: any) => void;
  onError?: (error: Error) => void;
  onStepComplete?: (stepId: string, result: any) => void;
  onStatusUpdate?: (status: WorkflowStatus) => void;
}

interface UseWorkflowExecutionReturn {
  execution: WorkflowExecution | null;
  status: WorkflowStatus | null;
  isLoading: boolean;
  error: Error | null;
  executeWorkflow: (params: { workflow_id: string; context: WorkflowContext }) => Promise<void>;
  executeStep: (params: { execution_id: string; workflow_id: string; step_id: string; context: WorkflowContext; step_input: any }) => Promise<void>;
  pauseWorkflow: () => Promise<void>;
  resumeWorkflow: () => Promise<void>;
  cancelWorkflow: () => Promise<void>;
  refreshStatus: () => Promise<void>;
}

const API_BASE_URL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000';

export function useWorkflowExecution(options: UseWorkflowExecutionOptions = {}): UseWorkflowExecutionReturn {
  const [execution, setExecution] = useState<WorkflowExecution | null>(null);
  const [status, setStatus] = useState<WorkflowStatus | null>(null);
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState<Error | null>(null);

  const { onComplete, onError, onStepComplete, onStatusUpdate } = options;

  const executeWorkflow = useCallback(async (params: { workflow_id: string; context: WorkflowContext }) => {
    setIsLoading(true);
    setError(null);

    try {
      const response = await fetch(`${API_BASE_URL}/api/v1/workflows/execute`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          workflow_id: params.workflow_id,
          context: {
            user_id: params.context.user_id,
            session_id: params.context.session_id,
            data: params.context.data || {}
          }
        }),
      });

      if (!response.ok) {
        throw new Error(`HTTP error! status: ${response.status}`);
      }

      const result: WorkflowExecution = await response.json();
      setExecution(result);

      // Convert to status format
      const statusResult: WorkflowStatus = {
        execution_id: result.execution_id,
        workflow_id: result.workflow_id,
        user_id: result.user_id,
        status: result.status,
        progress: result.progress,
        step_results: result.results,
        error_message: result.error_message,
        started_at: result.started_at,
        completed_at: result.completed_at
      };
      setStatus(statusResult);

      if (result.status === 'completed') {
        onComplete?.(result.results);
      } else if (result.status === 'failed') {
        onError?.(new Error(result.error_message || 'Workflow execution failed'));
      }

      onStatusUpdate?.(statusResult);

    } catch (err) {
      const error = err instanceof Error ? err : new Error('Unknown error');
      setError(error);
      onError?.(error);
    } finally {
      setIsLoading(false);
    }
  }, [onComplete, onError, onStatusUpdate]);

  const executeStep = useCallback(async (params: { execution_id: string; workflow_id: string; step_id: string; context: WorkflowContext; step_input: any }) => {
    setIsLoading(true);
    setError(null);

    try {
      const response = await fetch(`${API_BASE_URL}/api/v1/workflows/execute-step`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          execution_id: params.execution_id,
          workflow_id: params.workflow_id,
          step_id: params.step_id,
          context: {
            user_id: params.context.user_id,
            session_id: params.context.session_id,
            data: params.context.data || {}
          },
          step_input: params.step_input,
          results: status?.step_results || {}
        }),
      });

      if (!response.ok) {
        throw new Error(`HTTP error! status: ${response.status}`);
      }

      const result = await response.json();

      // Update step results
      if (status) {
        const updatedStatus = {
          ...status,
          step_results: {
            ...status.step_results,
            [params.step_id]: result.result
          }
        };
        setStatus(updatedStatus);
        onStepComplete?.(params.step_id, result.result);
        onStatusUpdate?.(updatedStatus);
      }

    } catch (err) {
      const error = err instanceof Error ? err : new Error('Unknown error');
      setError(error);
      onError?.(error);
    } finally {
      setIsLoading(false);
    }
  }, [status, onStepComplete, onError, onStatusUpdate]);

  const pauseWorkflow = useCallback(async () => {
    if (!execution) return;

    try {
      const response = await fetch(`${API_BASE_URL}/api/v1/workflows/pause`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          execution_id: execution.execution_id
        }),
      });

      if (!response.ok) {
        throw new Error(`HTTP error! status: ${response.status}`);
      }

      // Refresh status after pause
      await refreshStatus();

    } catch (err) {
      const error = err instanceof Error ? err : new Error('Unknown error');
      setError(error);
      onError?.(error);
    }
  }, [execution]);

  const resumeWorkflow = useCallback(async () => {
    if (!execution) return;

    try {
      const response = await fetch(`${API_BASE_URL}/api/v1/workflows/resume`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          execution_id: execution.execution_id
        }),
      });

      if (!response.ok) {
        throw new Error(`HTTP error! status: ${response.status}`);
      }

      // Refresh status after resume
      await refreshStatus();

    } catch (err) {
      const error = err instanceof Error ? err : new Error('Unknown error');
      setError(error);
      onError?.(error);
    }
  }, [execution]);

  const cancelWorkflow = useCallback(async () => {
    if (!execution) return;

    try {
      const response = await fetch(`${API_BASE_URL}/api/v1/workflows/cancel`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          execution_id: execution.execution_id
        }),
      });

      if (!response.ok) {
        throw new Error(`HTTP error! status: ${response.status}`);
      }

      // Refresh status after cancel
      await refreshStatus();

    } catch (err) {
      const error = err instanceof Error ? err : new Error('Unknown error');
      setError(error);
      onError?.(error);
    }
  }, [execution]);

  const refreshStatus = useCallback(async () => {
    if (!execution) return;

    try {
      const response = await fetch(`${API_BASE_URL}/api/v1/workflows/executions/${execution.execution_id}`, {
        method: 'GET',
        headers: {
          'Content-Type': 'application/json',
        },
      });

      if (!response.ok) {
        throw new Error(`HTTP error! status: ${response.status}`);
      }

      const result: WorkflowStatus = await response.json();
      setStatus(result);
      onStatusUpdate?.(result);

    } catch (err) {
      const error = err instanceof Error ? err : new Error('Unknown error');
      setError(error);
      onError?.(error);
    }
  }, [execution, onStatusUpdate]);

  return {
    execution,
    status,
    isLoading,
    error,
    executeWorkflow,
    executeStep,
    pauseWorkflow,
    resumeWorkflow,
    cancelWorkflow,
    refreshStatus
  };
}
