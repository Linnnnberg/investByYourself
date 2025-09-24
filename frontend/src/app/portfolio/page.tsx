'use client';

import { useState, useEffect } from 'react';
import Link from 'next/link';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Badge } from '@/components/ui/badge';
import { Tabs, TabsContent, TabsList, TabsTrigger } from '@/components/ui/tabs';
import { useApiClient, useApiCall } from '@/hooks/useApiClient';
import { Portfolio } from '@/lib/api-client';
import AppLayout from '@/components/layouts/AppLayout';
import { toast } from 'sonner';

// Enhanced Portfolio Construction & Analysis Page
export default function PortfolioPage() {
  const { client, isAuthenticated, isLoading: authLoading } = useApiClient();
  const [portfolios, setPortfolios] = useState<Portfolio[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [activeTab, setActiveTab] = useState('overview');
  const [selectedPortfolio, setSelectedPortfolio] = useState<Portfolio | null>(null);
  const [isCreatingPortfolio, setIsCreatingPortfolio] = useState(false);
  const [showCreateModal, setShowCreateModal] = useState(false);

  // Load portfolios using FastAPI
  const { data: portfoliosData, loading: portfoliosLoading, error: portfoliosError } = useApiCall(
    () => client.getPortfolios(),
    [isAuthenticated]
  );

  // Update portfolios when data loads
  useEffect(() => {
    if (portfoliosData) {
      setPortfolios(portfoliosData);
    }
  }, [portfoliosData]);

  // Set loading and error states
  useEffect(() => {
    setLoading(portfoliosLoading || authLoading);
    setError(portfoliosError);
  }, [portfoliosLoading, authLoading, portfoliosError]);

  // Functional handlers
  const handleCreatePortfolio = async () => {
    try {
      setIsCreatingPortfolio(true);
      const newPortfolio = await client.createPortfolio({
        name: `New Portfolio - ${new Date().toLocaleTimeString()}`,
        description: 'Portfolio created via UI',
        risk_profile: 'Medium'
      });

      setPortfolios(prev => [...prev, newPortfolio]);
      toast.success('Portfolio created successfully!');
      setShowCreateModal(false);
    } catch (error) {
      toast.error('Failed to create portfolio');
      console.error('Error creating portfolio:', error);
    } finally {
      setIsCreatingPortfolio(false);
    }
  };

  const handleViewPortfolio = (portfolio: Portfolio) => {
    setSelectedPortfolio(portfolio);
    setActiveTab('analysis');
    toast.info(`Viewing ${portfolio.name}`);
  };

  const handleAnalyzePortfolio = async (portfolio: Portfolio) => {
    try {
      setSelectedPortfolio(portfolio);
      setActiveTab('analysis');
      toast.info(`Analyzing ${portfolio.name}...`);
      // Here you would call the analysis API
    } catch (error) {
      toast.error('Failed to analyze portfolio');
      console.error('Error analyzing portfolio:', error);
    }
  };

  const handleOptimizePortfolio = (portfolio: Portfolio) => {
    setSelectedPortfolio(portfolio);
    setActiveTab('optimization');
    toast.info(`Optimizing ${portfolio.name}...`);
  };

  const handleSelectTemplate = (templateId: string) => {
    toast.info(`Selected template: ${templateId}`);
    setActiveTab('construction');
  };

  const handleBuildCustom = () => {
    toast.info('Opening custom framework builder...');
    setActiveTab('construction');
  };

  const handleImportFramework = () => {
    toast.info('Framework import feature coming soon!');
  };

  if (loading) {
    return (
      <div className="min-h-screen bg-gray-50 flex items-center justify-center">
        <div className="text-center">
          <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-600 mx-auto mb-4"></div>
          <p className="text-gray-600">Loading portfolios...</p>
        </div>
      </div>
    );
  }

  if (error) {
    return (
      <div className="min-h-screen bg-gray-50 flex items-center justify-center">
        <div className="text-center">
          <div className="text-red-600 text-6xl mb-4">⚠️</div>
          <h2 className="text-xl font-semibold text-gray-900 mb-2">Error Loading Portfolios</h2>
          <p className="text-gray-600 mb-4">{error}</p>
          <Button onClick={() => window.location.reload()}>Retry</Button>
        </div>
      </div>
    );
  }

  return (
    <AppLayout>
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
        {/* Header Section */}
        <div className="flex items-center justify-between mb-8">
          <div>
            <h1 className="text-3xl font-bold text-gray-900">Portfolio Construction & Analysis</h1>
            <p className="text-gray-600 mt-2">
              Build, analyze, and optimize your investment portfolios with professional-grade tools
            </p>
          </div>
          <div className="flex space-x-3">
            <Button
              variant="outline"
              onClick={() => setActiveTab('analysis')}
            >
              <span className="mr-2">📊</span>
              Portfolio Analysis
            </Button>
            <Button
              onClick={() => setShowCreateModal(true)}
              disabled={isCreatingPortfolio}
            >
              <span className="mr-2">➕</span>
              {isCreatingPortfolio ? 'Creating...' : 'Create Portfolio'}
            </Button>
          </div>
        </div>

        {/* Main Content with Tabs */}
        <Tabs value={activeTab} onValueChange={setActiveTab} className="space-y-6">
          <TabsList className="grid w-full grid-cols-4">
            <TabsTrigger value="overview">Overview</TabsTrigger>
            <TabsTrigger value="construction">Construction</TabsTrigger>
            <TabsTrigger value="analysis">Analysis</TabsTrigger>
            <TabsTrigger value="optimization">Optimization</TabsTrigger>
          </TabsList>

          {/* Overview Tab */}
          <TabsContent value="overview" className="space-y-6">
            {/* Portfolio Summary Cards */}
            {portfolios.length > 0 ? (
              <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
                {portfolios.map((portfolio) => (
                  <Card key={portfolio.id} className="hover:shadow-lg transition-shadow cursor-pointer">
                    <CardHeader>
                      <div className="flex items-center justify-between">
                        <CardTitle className="text-lg">{portfolio.name}</CardTitle>
                        <Badge
                          variant={portfolio.risk_profile === 'High' ? 'destructive' :
                                  portfolio.risk_profile === 'Medium' ? 'default' : 'secondary'}
                        >
                          {portfolio.risk_profile}
                        </Badge>
                      </div>
                      <p className="text-sm text-gray-600">{portfolio.description}</p>
                    </CardHeader>
                    <CardContent>
                      <div className="space-y-4">
                        <div className="grid grid-cols-2 gap-4">
                          <div>
                            <div className="text-2xl font-bold">{portfolio.total_value}</div>
                            <div className="text-sm text-gray-600">Total Value</div>
                          </div>
                          <div>
                            <div className={`text-2xl font-bold ${portfolio.total_gain_loss.startsWith('+') ? 'text-green-600' : 'text-red-600'}`}>
                              {portfolio.total_gain_loss}
                            </div>
                            <div className="text-sm text-gray-600">Gain/Loss</div>
                          </div>
                        </div>
                        <div className="pt-2 border-t">
                          <div className="flex justify-between text-sm text-gray-600">
                            <span>{portfolio.holdings_count} holdings</span>
                            <span>Risk: {portfolio.risk_profile}</span>
                          </div>
                        </div>
                        <div className="pt-2 space-y-2">
                          <Button
                            className="w-full"
                            onClick={() => handleViewPortfolio(portfolio)}
                          >
                            View Details
                          </Button>
                          <Button
                            variant="outline"
                            className="w-full"
                            onClick={() => handleAnalyzePortfolio(portfolio)}
                          >
                            Analyze
                          </Button>
                        </div>
                      </div>
                    </CardContent>
                  </Card>
                ))}
              </div>
            ) : (
              <div className="text-center py-12">
                <div className="text-6xl mb-6">💼</div>
                <h2 className="text-2xl font-bold text-gray-900 mb-4">No Portfolios Yet</h2>
                <p className="text-gray-600 mb-8 max-w-md mx-auto">
                  Create your first portfolio to start tracking your investments and building wealth.
                </p>
                <div className="space-y-4">
                  <Button
                    size="lg"
                    className="mr-4"
                    onClick={() => setShowCreateModal(true)}
                    disabled={isCreatingPortfolio}
                  >
                    {isCreatingPortfolio ? 'Creating...' : 'Create Portfolio'}
                  </Button>
                  <Button
                    variant="outline"
                    size="lg"
                    onClick={() => setActiveTab('construction')}
                  >
                    Learn More
                  </Button>
                </div>
              </div>
            )}

            {/* Quick Actions */}
            <Card>
              <CardHeader>
                <CardTitle>Quick Actions</CardTitle>
              </CardHeader>
              <CardContent>
                <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
                  <Button
                    className="h-20 flex flex-col items-center justify-center"
                    onClick={() => setShowCreateModal(true)}
                    disabled={isCreatingPortfolio}
                  >
                    <div className="text-2xl mb-2">➕</div>
                    <div>{isCreatingPortfolio ? 'Creating...' : 'Create Portfolio'}</div>
                  </Button>
                  <Button
                    variant="outline"
                    className="h-20 flex flex-col items-center justify-center"
                    onClick={() => setActiveTab('analysis')}
                  >
                    <div className="text-2xl mb-2">📊</div>
                    <div>Portfolio Analysis</div>
                  </Button>
                  <Button
                    variant="outline"
                    className="h-20 flex flex-col items-center justify-center"
                    onClick={() => setActiveTab('analysis')}
                  >
                    <div className="text-2xl mb-2">⚖️</div>
                    <div>Risk Assessment</div>
                  </Button>
                  <Button
                    variant="outline"
                    className="h-20 flex flex-col items-center justify-center"
                    onClick={() => setActiveTab('optimization')}
                  >
                    <div className="text-2xl mb-2">🎯</div>
                    <div>Optimization</div>
                  </Button>
                </div>
              </CardContent>
            </Card>
          </TabsContent>

          {/* Construction Tab */}
          <TabsContent value="construction" className="space-y-6">
            <Card>
              <CardHeader>
                <CardTitle>Portfolio Construction Tools</CardTitle>
                <p className="text-gray-600">Build your portfolio using professional allocation frameworks</p>
              </CardHeader>
              <CardContent>
                <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
                  {/* Allocation Framework Templates */}
                  <Card className="border-2 border-dashed border-gray-300 hover:border-blue-500 transition-colors cursor-pointer">
                    <CardContent className="p-6 text-center">
                      <div className="text-4xl mb-4">📋</div>
                      <h3 className="text-lg font-semibold mb-2">Allocation Templates</h3>
                      <p className="text-sm text-gray-600 mb-4">
                        Choose from pre-built allocation frameworks (Conservative, Balanced, Growth)
                      </p>
                      <Button
                        variant="outline"
                        size="sm"
                        onClick={() => handleSelectTemplate('conservative')}
                      >
                        Select Template
                      </Button>
                    </CardContent>
                  </Card>

                  {/* Custom Framework Builder */}
                  <Card className="border-2 border-dashed border-gray-300 hover:border-blue-500 transition-colors cursor-pointer">
                    <CardContent className="p-6 text-center">
                      <div className="text-4xl mb-4">🛠️</div>
                      <h3 className="text-lg font-semibold mb-2">Custom Framework</h3>
                      <p className="text-sm text-gray-600 mb-4">
                        Build your own allocation framework with custom asset classes and weights
                      </p>
                      <Button
                        variant="outline"
                        size="sm"
                        onClick={handleBuildCustom}
                      >
                        Build Custom
                      </Button>
                    </CardContent>
                  </Card>

                  {/* Import Framework */}
                  <Card className="border-2 border-dashed border-gray-300 hover:border-blue-500 transition-colors cursor-pointer">
                    <CardContent className="p-6 text-center">
                      <div className="text-4xl mb-4">📁</div>
                      <h3 className="text-lg font-semibold mb-2">Import Framework</h3>
                      <p className="text-sm text-gray-600 mb-4">
                        Import allocation frameworks from JSON/CSV files
                      </p>
                      <Button
                        variant="outline"
                        size="sm"
                        onClick={handleImportFramework}
                      >
                        Import File
                      </Button>
                    </CardContent>
                  </Card>
                </div>
              </CardContent>
            </Card>

            {/* Portfolio Builder Steps */}
            <Card>
              <CardHeader>
                <CardTitle>Portfolio Construction Steps</CardTitle>
              </CardHeader>
              <CardContent>
                <div className="space-y-4">
                  <div className="flex items-center space-x-4">
                    <div className="w-8 h-8 bg-blue-100 text-blue-600 rounded-full flex items-center justify-center font-semibold">1</div>
                    <div>
                      <h4 className="font-semibold">Choose Allocation Framework</h4>
                      <p className="text-sm text-gray-600">Select a template or create custom allocation rules</p>
                    </div>
                  </div>
                  <div className="flex items-center space-x-4">
                    <div className="w-8 h-8 bg-gray-100 text-gray-600 rounded-full flex items-center justify-center font-semibold">2</div>
                    <div>
                      <h4 className="font-semibold">Map Framework to Products</h4>
                      <p className="text-sm text-gray-600">Select specific ETFs, stocks, or funds for each allocation bucket</p>
                    </div>
                  </div>
                  <div className="flex items-center space-x-4">
                    <div className="w-8 h-8 bg-gray-100 text-gray-600 rounded-full flex items-center justify-center font-semibold">3</div>
                    <div>
                      <h4 className="font-semibold">Set Constraints & Bands</h4>
                      <p className="text-sm text-gray-600">Define rebalancing triggers and risk constraints</p>
                    </div>
                  </div>
                  <div className="flex items-center space-x-4">
                    <div className="w-8 h-8 bg-gray-100 text-gray-600 rounded-full flex items-center justify-center font-semibold">4</div>
                    <div>
                      <h4 className="font-semibold">Review & Finalize</h4>
                      <p className="text-sm text-gray-600">Validate allocation and create your portfolio</p>
                    </div>
                  </div>
                </div>
              </CardContent>
            </Card>
          </TabsContent>

          {/* Analysis Tab */}
          <TabsContent value="analysis" className="space-y-6">
            <Card>
              <CardHeader>
                <CardTitle>Portfolio Analysis Tools</CardTitle>
                <p className="text-gray-600">Analyze your portfolio performance, risk, and diversification</p>
              </CardHeader>
              <CardContent>
                <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
                  {/* Performance Analysis */}
                  <Card className="hover:shadow-lg transition-shadow cursor-pointer">
                    <CardContent className="p-6">
                      <div className="text-4xl mb-4">📈</div>
                      <h3 className="text-lg font-semibold mb-2">Performance Analysis</h3>
                      <p className="text-sm text-gray-600 mb-4">
                        Track returns, volatility, and risk-adjusted performance metrics
                      </p>
                      <Button
                        variant="outline"
                        size="sm"
                        onClick={() => toast.info('Performance analysis feature coming soon!')}
                      >
                        Analyze Performance
                      </Button>
                    </CardContent>
                  </Card>

                  {/* Risk Analysis */}
                  <Card className="hover:shadow-lg transition-shadow cursor-pointer">
                    <CardContent className="p-6">
                      <div className="text-4xl mb-4">⚠️</div>
                      <h3 className="text-lg font-semibold mb-2">Risk Analysis</h3>
                      <p className="text-sm text-gray-600 mb-4">
                        Assess portfolio risk, VaR, and stress testing scenarios
                      </p>
                      <Button
                        variant="outline"
                        size="sm"
                        onClick={() => toast.info('Risk analysis feature coming soon!')}
                      >
                        Analyze Risk
                      </Button>
                    </CardContent>
                  </Card>

                  {/* Diversification Analysis */}
                  <Card className="hover:shadow-lg transition-shadow cursor-pointer">
                    <CardContent className="p-6">
                      <div className="text-4xl mb-4">🌐</div>
                      <h3 className="text-lg font-semibold mb-2">Diversification</h3>
                      <p className="text-sm text-gray-600 mb-4">
                        Analyze sector, geographic, and asset class diversification
                      </p>
                      <Button
                        variant="outline"
                        size="sm"
                        onClick={() => toast.info('Diversification analysis feature coming soon!')}
                      >
                        Analyze Diversification
                      </Button>
                    </CardContent>
                  </Card>
                </div>
              </CardContent>
            </Card>

            {/* Analysis Features */}
            <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
              <Card>
                <CardHeader>
                  <CardTitle>Performance Metrics</CardTitle>
                </CardHeader>
                <CardContent>
                  <div className="space-y-4">
                    <div className="flex justify-between">
                      <span className="text-gray-600">Total Return</span>
                      <span className="font-semibold">+12.5%</span>
                    </div>
                    <div className="flex justify-between">
                      <span className="text-gray-600">Annualized Return</span>
                      <span className="font-semibold">+8.2%</span>
                    </div>
                    <div className="flex justify-between">
                      <span className="text-gray-600">Volatility</span>
                      <span className="font-semibold">15.3%</span>
                    </div>
                    <div className="flex justify-between">
                      <span className="text-gray-600">Sharpe Ratio</span>
                      <span className="font-semibold">0.54</span>
                    </div>
                  </div>
                </CardContent>
              </Card>

              <Card>
                <CardHeader>
                  <CardTitle>Risk Metrics</CardTitle>
                </CardHeader>
                <CardContent>
                  <div className="space-y-4">
                    <div className="flex justify-between">
                      <span className="text-gray-600">Value at Risk (95%)</span>
                      <span className="font-semibold">-2.8%</span>
                    </div>
                    <div className="flex justify-between">
                      <span className="text-gray-600">Maximum Drawdown</span>
                      <span className="font-semibold">-8.2%</span>
                    </div>
                    <div className="flex justify-between">
                      <span className="text-gray-600">Beta</span>
                      <span className="font-semibold">1.12</span>
                    </div>
                    <div className="flex justify-between">
                      <span className="text-gray-600">Correlation</span>
                      <span className="font-semibold">0.78</span>
                    </div>
                  </div>
                </CardContent>
              </Card>
            </div>
          </TabsContent>

          {/* Optimization Tab */}
          <TabsContent value="optimization" className="space-y-6">
            <Card>
              <CardHeader>
                <CardTitle>Portfolio Optimization</CardTitle>
                <p className="text-gray-600">Optimize your portfolio for better risk-adjusted returns</p>
              </CardHeader>
              <CardContent>
                <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
                  {/* Rebalancing */}
                  <Card className="hover:shadow-lg transition-shadow cursor-pointer">
                    <CardContent className="p-6">
                      <div className="text-4xl mb-4">⚖️</div>
                      <h3 className="text-lg font-semibold mb-2">Rebalancing</h3>
                      <p className="text-sm text-gray-600 mb-4">
                        Optimize portfolio weights and rebalancing strategies
                      </p>
                      <Button
                        variant="outline"
                        size="sm"
                        onClick={() => toast.info('Rebalancing optimization feature coming soon!')}
                      >
                        Optimize Rebalancing
                      </Button>
                    </CardContent>
                  </Card>

                  {/* Tax Optimization */}
                  <Card className="hover:shadow-lg transition-shadow cursor-pointer">
                    <CardContent className="p-6">
                      <div className="text-4xl mb-4">💰</div>
                      <h3 className="text-lg font-semibold mb-2">Tax Optimization</h3>
                      <p className="text-sm text-gray-600 mb-4">
                        Minimize tax impact with tax-loss harvesting and optimization
                      </p>
                      <Button
                        variant="outline"
                        size="sm"
                        onClick={() => toast.info('Tax optimization feature coming soon!')}
                      >
                        Optimize Taxes
                      </Button>
                    </CardContent>
                  </Card>

                  {/* Factor Analysis */}
                  <Card className="hover:shadow-lg transition-shadow cursor-pointer">
                    <CardContent className="p-6">
                      <div className="text-4xl mb-4">🔍</div>
                      <h3 className="text-lg font-semibold mb-2">Factor Analysis</h3>
                      <p className="text-sm text-gray-600 mb-4">
                        Analyze factor exposures and optimize factor tilts
                      </p>
                      <Button
                        variant="outline"
                        size="sm"
                        onClick={() => toast.info('Factor analysis feature coming soon!')}
                      >
                        Analyze Factors
                      </Button>
                    </CardContent>
                  </Card>
                </div>
              </CardContent>
            </Card>

            {/* Optimization Recommendations */}
            <Card>
              <CardHeader>
                <CardTitle>Optimization Recommendations</CardTitle>
              </CardHeader>
              <CardContent>
                <div className="space-y-4">
                  <div className="flex items-start space-x-4 p-4 bg-blue-50 rounded-lg">
                    <div className="text-blue-600 text-xl">💡</div>
                    <div>
                      <h4 className="font-semibold text-blue-900">Rebalancing Opportunity</h4>
                      <p className="text-sm text-blue-700">
                        Your portfolio has drifted 3.2% from target allocation. Consider rebalancing to maintain risk profile.
                      </p>
                    </div>
                  </div>
                  <div className="flex items-start space-x-4 p-4 bg-green-50 rounded-lg">
                    <div className="text-green-600 text-xl">✅</div>
                    <div>
                      <h4 className="font-semibold text-green-900">Tax-Loss Harvesting</h4>
                      <p className="text-sm text-green-700">
                        You have $2,400 in unrealized losses that could be harvested for tax benefits.
                      </p>
                    </div>
                  </div>
                  <div className="flex items-start space-x-4 p-4 bg-yellow-50 rounded-lg">
                    <div className="text-yellow-600 text-xl">⚠️</div>
                    <div>
                      <h4 className="font-semibold text-yellow-900">Concentration Risk</h4>
                      <p className="text-sm text-yellow-700">
                        Your portfolio is 35% concentrated in technology stocks. Consider diversifying across sectors.
                      </p>
                    </div>
                  </div>
                </div>
              </CardContent>
            </Card>
          </TabsContent>
        </Tabs>

        {/* Create Portfolio Modal */}
        {showCreateModal && (
          <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50">
            <div className="bg-white rounded-lg p-6 w-full max-w-md mx-4">
              <h3 className="text-lg font-semibold mb-4">Create New Portfolio</h3>
              <p className="text-gray-600 mb-6">
                Create a new portfolio to start tracking your investments.
              </p>
              <div className="flex space-x-3">
                <Button
                  onClick={handleCreatePortfolio}
                  disabled={isCreatingPortfolio}
                  className="flex-1"
                >
                  {isCreatingPortfolio ? 'Creating...' : 'Create Portfolio'}
                </Button>
                <Button
                  variant="outline"
                  onClick={() => setShowCreateModal(false)}
                  disabled={isCreatingPortfolio}
                >
                  Cancel
                </Button>
              </div>
            </div>
          </div>
        )}
      </div>
    </AppLayout>
  );
}
