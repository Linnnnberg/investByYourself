import { WorkflowExecutionRequest, WorkflowExecutionResponse } from './workflowApi';

export interface Portfolio {
  id: string;
  name: string;
  description: string;
  value: number;
  change: number;
  changePercent: number;
  allocation: Record<string, number>;
  riskLevel: 'Low' | 'Medium' | 'High';
  lastUpdated: string;
  status: 'Active' | 'Draft' | 'Archived';
  workflowId?: string;
  executionId?: string;
}

export interface PortfolioCreationRequest {
  name: string;
  description?: string;
  workflowId: string;
  context: {
    template?: any;
    quickStart?: boolean;
    mode?: string;
    creationMethod?: string;
    [key: string]: any;
  };
}

export interface PortfolioUpdateRequest {
  id: string;
  name?: string;
  description?: string;
  allocation?: Record<string, number>;
  status?: 'Active' | 'Draft' | 'Archived';
}

class PortfolioApiService {
  private baseUrl = process.env.NEXT_PUBLIC_API_BASE_URL ? `${process.env.NEXT_PUBLIC_API_BASE_URL}/api/v1` : 'http://localhost:8000/api/v1';

  /**
   * Get all portfolios for the current user
   */
  async getPortfolios(): Promise<Portfolio[]> {
    try {
      const response = await fetch(`${this.baseUrl}/portfolios`, {
        method: 'GET',
        headers: {
          'Content-Type': 'application/json',
        },
      });

      if (!response.ok) {
        throw new Error(`Failed to fetch portfolios: ${response.statusText}`);
      }

      const data = await response.json();
      return data.portfolios || [];
    } catch (error) {
      console.error('Error fetching portfolios:', error);
      return [];
    }
  }

  /**
   * Get a specific portfolio by ID
   */
  async getPortfolio(portfolioId: string): Promise<Portfolio | null> {
    try {
      const response = await fetch(`${this.baseUrl}/portfolios/${portfolioId}`, {
        method: 'GET',
        headers: {
          'Content-Type': 'application/json',
        },
      });

      if (!response.ok) {
        if (response.status === 404) {
          return null;
        }
        throw new Error(`Failed to fetch portfolio: ${response.statusText}`);
      }

      const data = await response.json();
      return data.portfolio;
    } catch (error) {
      console.error('Error fetching portfolio:', error);
      return null;
    }
  }

  /**
   * Create a new portfolio using a workflow
   */
  async createPortfolio(request: PortfolioCreationRequest): Promise<WorkflowExecutionResponse> {
    try {
      const workflowRequest: WorkflowExecutionRequest = {
        workflow_id: request.workflowId,
        context: {
          user_id: 'current_user', // TODO: Get from auth context
          session_id: `session_${Date.now()}`,
          data: {
            ...request.context,
            portfolio_name: request.name,
            portfolio_description: request.description,
          },
        },
      };

      // First execute the workflow
      const workflowResponse = await fetch(`${this.baseUrl}/workflows/execute`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify(workflowRequest),
      });

      if (!workflowResponse.ok) {
        throw new Error(`Failed to execute workflow: ${workflowResponse.statusText}`);
      }

      const workflowData = await workflowResponse.json();

      // Then create the portfolio using the workflow execution
      const portfolioRequest = {
        workflow_id: request.workflowId,
        execution_id: workflowData.execution_id,
        context: request.context,
        user_id: 'current_user'
      };

      const portfolioResponse = await fetch(`${this.baseUrl}/portfolios/create`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify(portfolioRequest),
      });

      if (!portfolioResponse.ok) {
        throw new Error(`Failed to create portfolio: ${portfolioResponse.statusText}`);
      }

      const portfolioData = await portfolioResponse.json();

      return {
        ...workflowData,
        portfolio: portfolioData.portfolio
      };
    } catch (error) {
      console.error('Error creating portfolio:', error);
      throw error;
    }
  }

  /**
   * Update an existing portfolio
   */
  async updatePortfolio(request: PortfolioUpdateRequest): Promise<Portfolio> {
    try {
      const response = await fetch(`${this.baseUrl}/portfolios/${request.id}`, {
        method: 'PUT',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify(request),
      });

      if (!response.ok) {
        throw new Error(`Failed to update portfolio: ${response.statusText}`);
      }

      const data = await response.json();
      return data.portfolio;
    } catch (error) {
      console.error('Error updating portfolio:', error);
      throw error;
    }
  }

  /**
   * Delete a portfolio
   */
  async deletePortfolio(portfolioId: string): Promise<void> {
    try {
      const response = await fetch(`${this.baseUrl}/portfolios/${portfolioId}`, {
        method: 'DELETE',
        headers: {
          'Content-Type': 'application/json',
        },
      });

      if (!response.ok) {
        throw new Error(`Failed to delete portfolio: ${response.statusText}`);
      }
    } catch (error) {
      console.error('Error deleting portfolio:', error);
      throw error;
    }
  }

  /**
   * Get portfolio performance data
   */
  async getPortfolioPerformance(portfolioId: string, period: string = '1Y'): Promise<any> {
    try {
      const response = await fetch(`${this.baseUrl}/portfolios/${portfolioId}/performance?period=${period}`, {
        method: 'GET',
        headers: {
          'Content-Type': 'application/json',
        },
      });

      if (!response.ok) {
        throw new Error(`Failed to fetch portfolio performance: ${response.statusText}`);
      }

      const data = await response.json();
      return data.performance;
    } catch (error) {
      console.error('Error fetching portfolio performance:', error);
      return null;
    }
  }

  /**
   * Get portfolio analytics
   */
  async getPortfolioAnalytics(portfolioId: string): Promise<any> {
    try {
      const response = await fetch(`${this.baseUrl}/portfolios/${portfolioId}/analytics`, {
        method: 'GET',
        headers: {
          'Content-Type': 'application/json',
        },
      });

      if (!response.ok) {
        throw new Error(`Failed to fetch portfolio analytics: ${response.statusText}`);
      }

      const data = await response.json();
      return data.analytics;
    } catch (error) {
      console.error('Error fetching portfolio analytics:', error);
      return null;
    }
  }

  /**
   * Rebalance a portfolio
   */
  async rebalancePortfolio(portfolioId: string, targetAllocation?: Record<string, number>): Promise<any> {
    try {
      const response = await fetch(`${this.baseUrl}/portfolios/${portfolioId}/rebalance`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({ target_allocation: targetAllocation }),
      });

      if (!response.ok) {
        throw new Error(`Failed to rebalance portfolio: ${response.statusText}`);
      }

      const data = await response.json();
      return data.rebalance;
    } catch (error) {
      console.error('Error rebalancing portfolio:', error);
      throw error;
    }
  }
}

export const portfolioApi = new PortfolioApiService();
