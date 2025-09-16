'use client';

import { DashboardPageLayout, ComingSoon, StatsCard } from '@/components/layouts';
import { Plus, TrendingUp, PieChart, DollarSign } from 'lucide-react';

export default function PortfolioPage() {
  const handleCreatePortfolio = () => {
    console.log('Create portfolio clicked');
    // TODO: Implement portfolio creation
  };

  const handleViewAnalytics = () => {
    console.log('View analytics clicked');
    // TODO: Implement analytics view
  };

  return (
    <DashboardPageLayout
      title="Portfolio Management"
      description="Track and manage your investment portfolios"
      status={[
        { label: 'API', value: 'Connected', color: 'green' },
        { label: 'Backend', value: 'FastAPI', color: 'blue' }
      ]}
    >
      <ComingSoon
        title="Portfolio Management"
        description="Coming soon..."
        features={[
          'Portfolio creation and management',
          'Real-time portfolio tracking',
          'Performance analytics',
          'Risk assessment integration',
          'Holdings management'
        ]}
        actions={[
          {
            label: 'Create Portfolio',
            onClick: handleCreatePortfolio,
            variant: 'outline',
            icon: <Plus className="h-4 w-4" />
          },
          {
            label: 'View Analytics',
            onClick: handleViewAnalytics,
            variant: 'outline',
            icon: <PieChart className="h-4 w-4" />
          }
        ]}
      />

      {/* Feature Preview Stats */}
      <div className="grid grid-cols-1 md:grid-cols-3 gap-6 mt-8">
        <StatsCard
          title="Portfolio Analytics"
          value="Coming Soon"
          description="Comprehensive portfolio performance analysis"
          icon={<PieChart className="h-8 w-8 text-blue-600" />}
        />
        <StatsCard
          title="Performance Tracking"
          value="Coming Soon"
          description="Real-time tracking with historical data"
          icon={<TrendingUp className="h-8 w-8 text-green-600" />}
        />
        <StatsCard
          title="Risk Management"
          value="Coming Soon"
          description="Advanced risk assessment tools"
          icon={<DollarSign className="h-8 w-8 text-yellow-600" />}
        />
      </div>
    </DashboardPageLayout>
  );
}
