/**
 * Workflow API Client Service
 * InvestByYourself Financial Platform
 *
 * Service for communicating with the workflow API endpoints.
 */

import {
  WorkflowDefinition,
  WorkflowExecutionRequest,
  WorkflowExecutionResponse,
  WorkflowStatusResponse,
  WorkflowListResponse,
  WorkflowStatus,
  StepExecutionRequest
} from '@/types/workflow';

const API_BASE_URL = process.env.NEXT_PUBLIC_API_BASE_URL ? `${process.env.NEXT_PUBLIC_API_BASE_URL}/api/v1` : 'http://localhost:8000/api/v1';

class WorkflowApiError extends Error {
  constructor(
    message: string,
    public status?: number,
    public response?: any
  ) {
    super(message);
    this.name = 'WorkflowApiError';
  }
}

class WorkflowApiClient {
  private baseUrl: string;

  constructor(baseUrl: string = API_BASE_URL) {
    this.baseUrl = baseUrl;
  }

  private async request<T>(
    endpoint: string,
    options: RequestInit = {}
  ): Promise<T> {
    const url = `${this.baseUrl}/workflows${endpoint}`;

    const defaultHeaders = {
      'Content-Type': 'application/json',
    };

    const config: RequestInit = {
      ...options,
      headers: {
        ...defaultHeaders,
        ...options.headers,
      },
    };

    try {
      const response = await fetch(url, config);

      if (!response.ok) {
        const errorData = await response.json().catch(() => ({}));
        throw new WorkflowApiError(
          errorData.detail || `HTTP ${response.status}: ${response.statusText}`,
          response.status,
          errorData
        );
      }

      return await response.json();
    } catch (error) {
      if (error instanceof WorkflowApiError) {
        throw error;
      }

      throw new WorkflowApiError(
        `Network error: ${error instanceof Error ? error.message : 'Unknown error'}`,
        undefined,
        error
      );
    }
  }

  // Health check
  async healthCheck(): Promise<{ status: string; service: string }> {
    return this.request('/health');
  }

  // List all available workflows
  async listWorkflows(): Promise<WorkflowListResponse> {
    return this.request('/');
  }

  // Get specific workflow definition
  async getWorkflow(workflowId: string): Promise<WorkflowDefinition> {
    return this.request(`/${workflowId}`);
  }

  // Execute a workflow
  async executeWorkflow(request: WorkflowExecutionRequest): Promise<WorkflowExecutionResponse> {
    return this.request('/execute', {
      method: 'POST',
      body: JSON.stringify(request),
    });
  }

  // Execute a single step
  async executeStep(request: StepExecutionRequest): Promise<any> {
    return this.request('/execute-step', {
      method: 'POST',
      body: JSON.stringify(request),
    });
  }

  // List workflow executions
  async listExecutions(params?: {
    user_id?: string;
    workflow_id?: string;
    status?: WorkflowStatus;
    limit?: number;
    offset?: number;
  }): Promise<WorkflowExecutionResponse[]> {
    const searchParams = new URLSearchParams();

    if (params?.user_id) searchParams.append('user_id', params.user_id);
    if (params?.workflow_id) searchParams.append('workflow_id', params.workflow_id);
    if (params?.status) searchParams.append('status', params.status);
    if (params?.limit) searchParams.append('limit', params.limit.toString());
    if (params?.offset) searchParams.append('offset', params.offset.toString());

    const queryString = searchParams.toString();
    const endpoint = queryString ? `/executions?${queryString}` : '/executions';

    return this.request(endpoint);
  }

  // Get execution status
  async getExecutionStatus(executionId: string): Promise<WorkflowStatusResponse> {
    return this.request(`/executions/${executionId}`);
  }

  // Pause workflow
  async pauseWorkflow(executionId: string): Promise<{ message: string }> {
    return this.request('/pause', {
      method: 'POST',
      body: JSON.stringify({ execution_id: executionId }),
    });
  }

  // Resume workflow
  async resumeWorkflow(executionId: string): Promise<{ message: string }> {
    return this.request('/resume', {
      method: 'POST',
      body: JSON.stringify({ execution_id: executionId }),
    });
  }

  // Cancel workflow
  async cancelWorkflow(executionId: string): Promise<{ message: string }> {
    return this.request('/cancel', {
      method: 'POST',
      body: JSON.stringify({ execution_id: executionId }),
    });
  }

  // Poll execution status (for real-time updates)
  async pollExecutionStatus(
    executionId: string,
    onUpdate: (status: WorkflowStatusResponse) => void,
    interval: number = 2000,
    maxAttempts: number = 30
  ): Promise<WorkflowStatusResponse> {
    let attempts = 0;

    const poll = async (): Promise<WorkflowStatusResponse> => {
      try {
        const status = await this.getExecutionStatus(executionId);
        onUpdate(status);

        // Stop polling if execution is complete
        if (['completed', 'failed', 'cancelled'].includes(status.status)) {
          return status;
        }

        // Continue polling if not complete and within max attempts
        if (attempts < maxAttempts) {
          attempts++;
          setTimeout(poll, interval);
        }

        return status;
      } catch (error) {
        console.error('Error polling execution status:', error);
        throw error;
      }
    };

    return poll();
  }
}

// Export singleton instance
export const workflowApi = new WorkflowApiClient();
export { WorkflowApiError };
export default WorkflowApiClient;
