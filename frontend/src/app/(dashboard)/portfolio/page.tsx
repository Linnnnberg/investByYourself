'use client';

import { useState, useEffect } from 'react';
import { DashboardPageLayout, StatsCard } from '@/components/layouts';
import PortfolioCreationWizard from '@/components/portfolio/PortfolioCreationWizard';
import PortfolioList from '@/components/portfolio/PortfolioList';
import { portfolioApi, Portfolio } from '@/services/portfolioApi';
import { useWorkflowExecution } from '@/hooks/useWorkflowExecution';
import { Plus, TrendingUp, PieChart, DollarSign, Loader2 } from 'lucide-react';

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

      // Create proper WorkflowExecutionRequest
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

      // Note: The actual result will be handled by the onComplete callback
      // We'll reload portfolios when the workflow completes

    } catch (error) {
      console.error('Error starting portfolio creation workflow:', error);
    }
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

  const handleViewAnalytics = () => {
    // TODO: Navigate to analytics page or open analytics modal
    console.log('View analytics clicked');
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

      {/* Portfolio Analytics Section */}
      {portfolios.length > 0 && (
        <div className="mt-12">
          <div className="flex items-center justify-between mb-6">
            <h2 className="text-2xl font-bold">Portfolio Analytics</h2>
            <button
              onClick={handleViewAnalytics}
              className="text-blue-600 hover:text-blue-800 font-medium"
            >
              View Detailed Analytics →
            </button>
          </div>

          <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
            <StatsCard
              title="Total Portfolio Value"
              value={`$${portfolios.reduce((sum, p) => sum + p.value, 0).toLocaleString()}`}
              description="Combined value of all portfolios"
              icon={<PieChart className="h-8 w-8 text-blue-600" />}
            />
            <StatsCard
              title="Average Performance"
              value={`${(portfolios.reduce((sum, p) => sum + p.changePercent, 0) / portfolios.length).toFixed(2)}%`}
              description="Average return across portfolios"
              icon={<TrendingUp className="h-8 w-8 text-green-600" />}
            />
            <StatsCard
              title="Active Portfolios"
              value={portfolios.filter(p => p.status === 'Active').length.toString()}
              description="Currently active portfolios"
              icon={<DollarSign className="h-8 w-8 text-yellow-600" />}
            />
          </div>
        </div>
      )}

      {/* Workflow Execution Status */}
      {isLoading && (
        <div className="fixed bottom-4 right-4 bg-white border border-gray-200 rounded-lg shadow-lg p-4 flex items-center gap-3">
          <Loader2 className="h-5 w-5 animate-spin text-blue-600" />
          <span className="text-sm font-medium">Creating portfolio...</span>
        </div>
      )}
    </DashboardPageLayout>
  );
}
