/**
 * Workflows List Hook
 * InvestByYourself Financial Platform
 *
 * Custom React hook for managing workflow definitions and listings.
 */

import { useState, useEffect, useCallback } from 'react';
import {
  WorkflowDefinition,
  WorkflowListResponse,
  WorkflowExecutionResponse
} from '@/types/workflow';
import { workflowApi, WorkflowApiError } from '@/services/workflowApi';

export interface UseWorkflowsOptions {
  autoFetch?: boolean;
  category?: string;
}

export interface UseWorkflowsReturn {
  workflows: WorkflowDefinition[];
  executions: WorkflowExecutionResponse[];
  isLoading: boolean;
  error: Error | null;
  fetchWorkflows: () => Promise<void>;
  fetchExecutions: (params?: {
    user_id?: string;
    workflow_id?: string;
    status?: string;
    limit?: number;
    offset?: number;
  }) => Promise<void>;
  getWorkflow: (workflowId: string) => Promise<WorkflowDefinition | null>;
  refresh: () => Promise<void>;
}

export function useWorkflows(options: UseWorkflowsOptions = {}): UseWorkflowsReturn {
  const { autoFetch = true, category } = options;

  const [workflows, setWorkflows] = useState<WorkflowDefinition[]>([]);
  const [executions, setExecutions] = useState<WorkflowExecutionResponse[]>([]);
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState<Error | null>(null);

  const handleError = useCallback((err: Error, context?: string) => {
    console.error(`Workflows error${context ? ` (${context})` : ''}:`, err);
    setError(err);
    setIsLoading(false);
  }, []);

  const fetchWorkflows = useCallback(async () => {
    try {
      setError(null);
      setIsLoading(true);

      const response = await workflowApi.listWorkflows();

      // Filter by category if specified
      let filteredWorkflows = response.workflows;
      if (category) {
        filteredWorkflows = response.workflows.filter(w => w.category === category);
      }

      setWorkflows(filteredWorkflows);

    } catch (err) {
      handleError(err as Error, 'fetch workflows');
    } finally {
      setIsLoading(false);
    }
  }, [category, handleError]);

  const fetchExecutions = useCallback(async (params?: {
    user_id?: string;
    workflow_id?: string;
    status?: string;
    limit?: number;
    offset?: number;
  }) => {
    try {
      setError(null);
      setIsLoading(true);

      const response = await workflowApi.listExecutions(params);
      setExecutions(response);

    } catch (err) {
      handleError(err as Error, 'fetch executions');
    } finally {
      setIsLoading(false);
    }
  }, [handleError]);

  const getWorkflow = useCallback(async (workflowId: string): Promise<WorkflowDefinition | null> => {
    try {
      setError(null);

      const workflow = await workflowApi.getWorkflow(workflowId);
      return workflow;

    } catch (err) {
      handleError(err as Error, 'get workflow');
      return null;
    }
  }, [handleError]);

  const refresh = useCallback(async () => {
    await Promise.all([
      fetchWorkflows(),
      fetchExecutions()
    ]);
  }, [fetchWorkflows, fetchExecutions]);

  // Auto-fetch on mount
  useEffect(() => {
    if (autoFetch) {
      fetchWorkflows();
    }
  }, [autoFetch, fetchWorkflows]);

  return {
    workflows,
    executions,
    isLoading,
    error,
    fetchWorkflows,
    fetchExecutions,
    getWorkflow,
    refresh
  };
}
