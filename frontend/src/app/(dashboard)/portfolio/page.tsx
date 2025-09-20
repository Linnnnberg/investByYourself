'use client';

import { useState, useEffect } from 'react';
import { DashboardPageLayout } from '@/components/layouts';
import PortfolioCreationWizard from '@/components/portfolio/PortfolioCreationWizard';
import PortfolioList from '@/components/portfolio/PortfolioList';
import { portfolioApi, Portfolio } from '@/services/portfolioApi';
import { useWorkflowExecution } from '@/hooks/useWorkflowExecution';
import { Loader2 } from 'lucide-react';

export default function PortfolioPage() {
  const [portfolios, setPortfolios] = useState<Portfolio[]>([]);
  const [loading, setLoading] = useState(true);
  const [showCreationWizard, setShowCreationWizard] = useState(false);
  const [selectedPortfolio, setSelectedPortfolio] = useState<Portfolio | null>(null);

  const { executeWorkflow, isLoading } = useWorkflowExecution({
    onComplete: async (result) => {
      console.log('Portfolio creation workflow completed:', result);
      // Reload portfolios to show the new one
      await loadPortfolios();
    },
    onError: (error) => {
      console.error('Portfolio creation workflow failed:', error);
    }
  });

  // Load portfolios on component mount
  useEffect(() => {
    loadPortfolios();
  }, []);

  const loadPortfolios = async () => {
    try {
      setLoading(true);
      const portfolioData = await portfolioApi.getPortfolios();
      setPortfolios(portfolioData);
    } catch (error) {
      console.error('Error loading portfolios:', error);
    } finally {
      setLoading(false);
    }
  };

  const handleCreatePortfolio = () => {
    setShowCreationWizard(true);
  };

  const handleWorkflowStart = async (workflowId: string, context: any) => {
    try {
      setShowCreationWizard(false);

      if (workflowId === 'create_portfolio_direct') {
        // Direct portfolio creation
        const portfolio = await portfolioApi.createPortfolioDirect({
          name: context.name,
          description: context.description,
          allocation: context.allocation,
          riskLevel: context.riskLevel
        });

        // Refresh portfolio list
        await loadPortfolios();
        console.log('Portfolio created successfully:', portfolio);
      } else {
        // Workflow-based creation (for other workflows)
        const workflowRequest = {
          workflow_id: workflowId,
          context: {
            user_id: 'current_user', // TODO: Get from auth context
            session_id: `session_${Date.now()}`,
            data: context
          }
        };

        // Execute workflow - this is async and will update state via polling
        await executeWorkflow(workflowRequest);
      }

    } catch (error) {
      console.error('Error creating portfolio:', error);
    }
  };

  const handleWorkflowComplete = async (result: any) => {
    console.log('Workflow completed:', result);
    // Reload portfolios to show the new one
    await loadPortfolios();
  };

  const handleViewPortfolio = (portfolioId: string) => {
    const portfolio = portfolios.find(p => p.id === portfolioId);
    if (portfolio) {
      setSelectedPortfolio(portfolio);
      // TODO: Navigate to portfolio detail page or open modal
      console.log('View portfolio:', portfolio);
    }
  };

  const handleEditPortfolio = (portfolioId: string) => {
    const portfolio = portfolios.find(p => p.id === portfolioId);
    if (portfolio) {
      // TODO: Open edit modal or navigate to edit page
      console.log('Edit portfolio:', portfolio);
    }
  };

  const handleDeletePortfolio = async (portfolioId: string) => {
    if (confirm('Are you sure you want to delete this portfolio?')) {
      try {
        await portfolioApi.deletePortfolio(portfolioId);
        await loadPortfolios();
      } catch (error) {
        console.error('Error deleting portfolio:', error);
      }
    }
  };


  if (loading) {
    return (
      <DashboardPageLayout
        title="Portfolio Management"
        description="Track and manage your investment portfolios"
        status={[
          { label: 'API', value: 'Connected', color: 'green' },
          { label: 'Backend', value: 'FastAPI', color: 'blue' }
        ]}
      >
        <div className="flex items-center justify-center py-12">
          <Loader2 className="h-8 w-8 animate-spin" />
          <span className="ml-2">Loading portfolios...</span>
        </div>
      </DashboardPageLayout>
    );
  }

  return (
    <DashboardPageLayout
      title="Portfolio Management"
      description="Track and manage your investment portfolios"
      status={[
        { label: 'API', value: 'Connected', color: 'green' },
        { label: 'Backend', value: 'FastAPI', color: 'blue' }
      ]}
    >
      {/* Portfolio Creation Wizard Modal */}
      {showCreationWizard && (
        <PortfolioCreationWizard
          onWorkflowStart={handleWorkflowStart}
          onClose={() => setShowCreationWizard(false)}
        />
      )}

      {/* Portfolio List */}
      <PortfolioList
        portfolios={portfolios}
        onViewPortfolio={handleViewPortfolio}
        onEditPortfolio={handleEditPortfolio}
        onDeletePortfolio={handleDeletePortfolio}
        onCreatePortfolio={handleCreatePortfolio}
      />


      {/* Workflow Execution Status */}
      {isLoading && (
        <div className="fixed bottom-4 right-4 bg-white border border-gray-200 rounded-lg shadow-lg p-4 flex items-center gap-3">
          <Loader2 className="h-5 w-5 animate-spin text-blue-600" />
          <span className="text-sm font-medium">Creating portfolio...</span>
        </div>
      )}

      {/* Workflow execution is handled by useWorkflowExecution hook */}
    </DashboardPageLayout>
  );
}
