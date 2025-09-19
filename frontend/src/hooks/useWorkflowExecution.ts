/**
 * Workflow Execution Hook
 * InvestByYourself Financial Platform
 *
 * Custom React hook for managing workflow execution state and API calls.
 */

import { useState, useCallback, useRef, useEffect } from 'react';
import {
  WorkflowExecutionRequest,
  WorkflowExecutionResponse,
  WorkflowStatusResponse,
  StepExecutionRequest,
  WorkflowStatus,
  UseWorkflowExecutionOptions,
  UseWorkflowExecutionReturn
} from '@/types/workflow';
import { workflowApi, WorkflowApiError } from '@/services/workflowApi';

export function useWorkflowExecution(options: UseWorkflowExecutionOptions = {}): UseWorkflowExecutionReturn {
  const {
    onComplete,
    onError,
    onStepComplete,
    onStatusUpdate,
    pollInterval = 2000,
    maxPollAttempts = 30
  } = options;

  const [execution, setExecution] = useState<WorkflowExecutionResponse | null>(null);
  const [status, setStatus] = useState<WorkflowStatusResponse | null>(null);
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState<Error | null>(null);

  const pollingRef = useRef<NodeJS.Timeout | null>(null);
  const executionIdRef = useRef<string | null>(null);

  // Cleanup polling on unmount
  useEffect(() => {
    return () => {
      if (pollingRef.current) {
        clearTimeout(pollingRef.current);
      }
    };
  }, []);

  const handleError = useCallback((err: Error, context?: string) => {
    console.error(`Workflow error${context ? ` (${context})` : ''}:`, err);
    setError(err);
    setIsLoading(false);
    onError?.(err);
  }, [onError]);

  const startPolling = useCallback((executionId: string) => {
    if (pollingRef.current) {
      clearTimeout(pollingRef.current);
    }

    let attempts = 0;

    const poll = async () => {
      try {
        const currentStatus = await workflowApi.getExecutionStatus(executionId);
        setStatus(currentStatus);
        onStatusUpdate?.(currentStatus);

        // Stop polling if execution is complete
        if (['completed', 'failed', 'cancelled'].includes(currentStatus.status)) {
          setIsLoading(false);
          if (currentStatus.status === 'completed') {
            // Create a proper WorkflowExecutionResponse from the status
            const completedExecution: WorkflowExecutionResponse = {
              execution_id: currentStatus.execution_id,
              workflow_id: currentStatus.workflow_id,
              status: currentStatus.status,
              current_step: currentStatus.current_step,
              progress: currentStatus.progress,
              results: currentStatus.step_results || {},
              error_message: currentStatus.error_message,
              started_at: currentStatus.started_at,
              completed_at: currentStatus.completed_at,
            };
            onComplete?.(completedExecution);
          }
          return;
        }

        // Continue polling if not complete and within max attempts
        if (attempts < maxPollAttempts) {
          attempts++;
          pollingRef.current = setTimeout(poll, pollInterval);
        } else {
          setIsLoading(false);
          handleError(new Error('Polling timeout - maximum attempts reached'));
        }
      } catch (err) {
        handleError(err as Error, 'polling');
      }
    };

    poll();
  }, [execution, onComplete, onStatusUpdate, onError, pollInterval, maxPollAttempts, handleError]);

  const executeWorkflow = useCallback(async (request: WorkflowExecutionRequest) => {
    try {
      setError(null);
      setIsLoading(true);

      const response = await workflowApi.executeWorkflow(request);
      setExecution(response);
      executionIdRef.current = response.execution_id;

      // Start polling for status updates
      startPolling(response.execution_id);

    } catch (err) {
      handleError(err as Error, 'execute workflow');
    }
  }, [startPolling, handleError]);

  const executeStep = useCallback(async (request: StepExecutionRequest) => {
    try {
      setError(null);
      setIsLoading(true);

      const response = await workflowApi.executeStep(request);

      // Update execution results
      if (execution) {
        const updatedExecution = {
          ...execution,
          results: {
            ...execution.results,
            [request.step_id]: response.result
          }
        };
        setExecution(updatedExecution);
      }

      onStepComplete?.(request.step_id, response.result);

      // Refresh status
      if (executionIdRef.current) {
        const currentStatus = await workflowApi.getExecutionStatus(executionIdRef.current);
        setStatus(currentStatus);
        onStatusUpdate?.(currentStatus);
      }

      setIsLoading(false);

    } catch (err) {
      handleError(err as Error, 'execute step');
    }
  }, [execution, onStepComplete, onStatusUpdate, handleError]);

  const pauseWorkflow = useCallback(async () => {
    if (!executionIdRef.current) {
      handleError(new Error('No active execution to pause'));
      return;
    }

    try {
      setError(null);
      await workflowApi.pauseWorkflow(executionIdRef.current);

      // Refresh status
      const currentStatus = await workflowApi.getExecutionStatus(executionIdRef.current);
      setStatus(currentStatus);
      onStatusUpdate?.(currentStatus);

    } catch (err) {
      handleError(err as Error, 'pause workflow');
    }
  }, [onStatusUpdate, handleError]);

  const resumeWorkflow = useCallback(async () => {
    if (!executionIdRef.current) {
      handleError(new Error('No active execution to resume'));
      return;
    }

    try {
      setError(null);
      await workflowApi.resumeWorkflow(executionIdRef.current);

      // Refresh status and resume polling
      const currentStatus = await workflowApi.getExecutionStatus(executionIdRef.current);
      setStatus(currentStatus);
      onStatusUpdate?.(currentStatus);

      // Resume polling if not complete
      if (!['completed', 'failed', 'cancelled'].includes(currentStatus.status)) {
        startPolling(executionIdRef.current);
      }

    } catch (err) {
      handleError(err as Error, 'resume workflow');
    }
  }, [onStatusUpdate, startPolling, handleError]);

  const cancelWorkflow = useCallback(async () => {
    if (!executionIdRef.current) {
      handleError(new Error('No active execution to cancel'));
      return;
    }

    try {
      setError(null);
      await workflowApi.cancelWorkflow(executionIdRef.current);

      // Stop polling
      if (pollingRef.current) {
        clearTimeout(pollingRef.current);
        pollingRef.current = null;
      }

      // Refresh status
      const currentStatus = await workflowApi.getExecutionStatus(executionIdRef.current);
      setStatus(currentStatus);
      onStatusUpdate?.(currentStatus);

      setIsLoading(false);

    } catch (err) {
      handleError(err as Error, 'cancel workflow');
    }
  }, [onStatusUpdate, handleError]);

  const refreshStatus = useCallback(async () => {
    if (!executionIdRef.current) {
      handleError(new Error('No active execution to refresh'));
      return;
    }

    try {
      setError(null);
      const currentStatus = await workflowApi.getExecutionStatus(executionIdRef.current);
      setStatus(currentStatus);
      onStatusUpdate?.(currentStatus);

    } catch (err) {
      handleError(err as Error, 'refresh status');
    }
  }, [onStatusUpdate, handleError]);

  // Reset function
  const reset = useCallback(() => {
    setExecution(null);
    setStatus(null);
    setError(null);
    setIsLoading(false);
    executionIdRef.current = null;

    if (pollingRef.current) {
      clearTimeout(pollingRef.current);
      pollingRef.current = null;
    }
  }, []);

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
    refreshStatus,
    reset
  };
}
