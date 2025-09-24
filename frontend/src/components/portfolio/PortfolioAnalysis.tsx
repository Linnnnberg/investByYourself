'use client';

import { useState, useEffect } from 'react';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Badge } from '@/components/ui/badge';
import { Tabs, TabsContent, TabsList, TabsTrigger } from '@/components/ui/tabs';

// Mock portfolio analysis data
const MOCK_ANALYSIS_DATA = {
  performance: {
    totalReturn: 12.5,
    annualizedReturn: 8.2,
    volatility: 15.3,
    sharpeRatio: 0.54,
    maxDrawdown: -8.2,
    currentValue: 125000,
    initialValue: 100000
  },
  risk: {
    var95: -2.8,
    var99: -4.2,
    beta: 1.12,
    correlation: 0.78,
    trackingError: 3.2,
    informationRatio: 0.25
  },
  diversification: {
    sectorConcentration: {
      technology: 35,
      healthcare: 20,
      financials: 15,
      consumer: 12,
      industrials: 10,
      others: 8
    },
    geographicConcentration: {
      northAmerica: 60,
      europe: 25,
      asia: 10,
      others: 5
    },
    assetClassConcentration: {
      stocks: 70,
      bonds: 20,
      cash: 5,
      alternatives: 5
    }
  },
  optimization: {
    rebalancingNeeded: true,
    driftAmount: 3.2,
    taxLossHarvesting: 2400,
    concentrationRisk: {
      isHigh: true,
      description: '35% concentrated in technology stocks'
    }
  }
};

interface PortfolioAnalysisProps {
  portfolioId?: string;
  onOptimize?: () => void;
  onRebalance?: () => void;
}

export default function PortfolioAnalysis({
  portfolioId,
  onOptimize,
  onRebalance
}: PortfolioAnalysisProps) {
  const [analysisData, setAnalysisData] = useState(MOCK_ANALYSIS_DATA);
  const [activeTab, setActiveTab] = useState('performance');

  // In a real implementation, this would fetch data from the API
  useEffect(() => {
    // Simulate API call
    const fetchAnalysisData = async () => {
      // await client.getPortfolioAnalysis(portfolioId);
      setAnalysisData(MOCK_ANALYSIS_DATA);
    };

    if (portfolioId) {
      fetchAnalysisData();
    }
  }, [portfolioId]);

  const formatPercentage = (value: number) => `${value > 0 ? '+' : ''}${value.toFixed(1)}%`;
  const formatCurrency = (value: number) => `$${value.toLocaleString()}`;

  return (
    <div className="space-y-6">
      <div className="text-center">
        <h2 className="text-2xl font-bold text-gray-900 mb-2">Portfolio Analysis</h2>
        <p className="text-gray-600">
          Comprehensive analysis of your portfolio performance, risk, and diversification
        </p>
      </div>

      <Tabs value={activeTab} onValueChange={setActiveTab}>
        <TabsList className="grid w-full grid-cols-4">
          <TabsTrigger value="performance">Performance</TabsTrigger>
          <TabsTrigger value="risk">Risk</TabsTrigger>
          <TabsTrigger value="diversification">Diversification</TabsTrigger>
          <TabsTrigger value="optimization">Optimization</TabsTrigger>
        </TabsList>

        {/* Performance Tab */}
        <TabsContent value="performance" className="space-y-6">
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
            <Card>
              <CardHeader>
                <CardTitle>Total Return</CardTitle>
              </CardHeader>
              <CardContent>
                <div className="text-3xl font-bold text-green-600">
                  {formatPercentage(analysisData.performance.totalReturn)}
                </div>
                <p className="text-sm text-gray-600 mt-2">
                  Since inception
                </p>
              </CardContent>
            </Card>

            <Card>
              <CardHeader>
                <CardTitle>Annualized Return</CardTitle>
              </CardHeader>
              <CardContent>
                <div className="text-3xl font-bold text-blue-600">
                  {formatPercentage(analysisData.performance.annualizedReturn)}
                </div>
                <p className="text-sm text-gray-600 mt-2">
                  Per year
                </p>
              </CardContent>
            </Card>

            <Card>
              <CardHeader>
                <CardTitle>Volatility</CardTitle>
              </CardHeader>
              <CardContent>
                <div className="text-3xl font-bold text-orange-600">
                  {formatPercentage(analysisData.performance.volatility)}
                </div>
                <p className="text-sm text-gray-600 mt-2">
                  Annual volatility
                </p>
              </CardContent>
            </Card>

            <Card>
              <CardHeader>
                <CardTitle>Sharpe Ratio</CardTitle>
              </CardHeader>
              <CardContent>
                <div className="text-3xl font-bold text-purple-600">
                  {analysisData.performance.sharpeRatio.toFixed(2)}
                </div>
                <p className="text-sm text-gray-600 mt-2">
                  Risk-adjusted return
                </p>
              </CardContent>
            </Card>

            <Card>
              <CardHeader>
                <CardTitle>Max Drawdown</CardTitle>
              </CardHeader>
              <CardContent>
                <div className="text-3xl font-bold text-red-600">
                  {formatPercentage(analysisData.performance.maxDrawdown)}
                </div>
                <p className="text-sm text-gray-600 mt-2">
                  Largest loss
                </p>
              </CardContent>
            </Card>

            <Card>
              <CardHeader>
                <CardTitle>Current Value</CardTitle>
              </CardHeader>
              <CardContent>
                <div className="text-3xl font-bold text-gray-900">
                  {formatCurrency(analysisData.performance.currentValue)}
                </div>
                <p className="text-sm text-gray-600 mt-2">
                  Portfolio value
                </p>
              </CardContent>
            </Card>
          </div>

          {/* Performance Chart Placeholder */}
          <Card>
            <CardHeader>
              <CardTitle>Performance Over Time</CardTitle>
            </CardHeader>
            <CardContent>
              <div className="h-64 bg-gray-100 rounded-lg flex items-center justify-center">
                <div className="text-center">
                  <div className="text-4xl mb-2">📈</div>
                  <p className="text-gray-600">Performance chart will be displayed here</p>
                </div>
              </div>
            </CardContent>
          </Card>
        </TabsContent>

        {/* Risk Tab */}
        <TabsContent value="risk" className="space-y-6">
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
            <Card>
              <CardHeader>
                <CardTitle>Value at Risk (95%)</CardTitle>
              </CardHeader>
              <CardContent>
                <div className="text-3xl font-bold text-red-600">
                  {formatPercentage(analysisData.risk.var95)}
                </div>
                <p className="text-sm text-gray-600 mt-2">
                  Daily VaR
                </p>
              </CardContent>
            </Card>

            <Card>
              <CardHeader>
                <CardTitle>Beta</CardTitle>
              </CardHeader>
              <CardContent>
                <div className="text-3xl font-bold text-blue-600">
                  {analysisData.risk.beta.toFixed(2)}
                </div>
                <p className="text-sm text-gray-600 mt-2">
                  Market sensitivity
                </p>
              </CardContent>
            </Card>

            <Card>
              <CardHeader>
                <CardTitle>Correlation</CardTitle>
              </CardHeader>
              <CardContent>
                <div className="text-3xl font-bold text-purple-600">
                  {analysisData.risk.correlation.toFixed(2)}
                </div>
                <p className="text-sm text-gray-600 mt-2">
                  With market
                </p>
              </CardContent>
            </Card>

            <Card>
              <CardHeader>
                <CardTitle>Tracking Error</CardTitle>
              </CardHeader>
              <CardContent>
                <div className="text-3xl font-bold text-orange-600">
                  {formatPercentage(analysisData.risk.trackingError)}
                </div>
                <p className="text-sm text-gray-600 mt-2">
                  Active risk
                </p>
              </CardContent>
            </Card>

            <Card>
              <CardHeader>
                <CardTitle>Information Ratio</CardTitle>
              </CardHeader>
              <CardContent>
                <div className="text-3xl font-bold text-green-600">
                  {analysisData.risk.informationRatio.toFixed(2)}
                </div>
                <p className="text-sm text-gray-600 mt-2">
                  Risk-adjusted alpha
                </p>
              </CardContent>
            </Card>
          </div>

          {/* Risk Chart Placeholder */}
          <Card>
            <CardHeader>
              <CardTitle>Risk Analysis</CardTitle>
            </CardHeader>
            <CardContent>
              <div className="h-64 bg-gray-100 rounded-lg flex items-center justify-center">
                <div className="text-center">
                  <div className="text-4xl mb-2">⚠️</div>
                  <p className="text-gray-600">Risk analysis charts will be displayed here</p>
                </div>
              </div>
            </CardContent>
          </Card>
        </TabsContent>

        {/* Diversification Tab */}
        <TabsContent value="diversification" className="space-y-6">
          <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
            {/* Sector Diversification */}
            <Card>
              <CardHeader>
                <CardTitle>Sector Allocation</CardTitle>
              </CardHeader>
              <CardContent>
                <div className="space-y-3">
                  {Object.entries(analysisData.diversification.sectorConcentration).map(([sector, percentage]) => (
                    <div key={sector} className="flex items-center justify-between">
                      <span className="text-sm capitalize">{sector}</span>
                      <div className="flex items-center space-x-2">
                        <div className="w-20 h-2 bg-gray-200 rounded-full overflow-hidden">
                          <div
                            className="h-full bg-blue-500"
                            style={{ width: `${percentage}%` }}
                          ></div>
                        </div>
                        <span className="text-sm font-semibold">{percentage}%</span>
                      </div>
                    </div>
                  ))}
                </div>
              </CardContent>
            </Card>

            {/* Geographic Diversification */}
            <Card>
              <CardHeader>
                <CardTitle>Geographic Allocation</CardTitle>
              </CardHeader>
              <CardContent>
                <div className="space-y-3">
                  {Object.entries(analysisData.diversification.geographicConcentration).map(([region, percentage]) => (
                    <div key={region} className="flex items-center justify-between">
                      <span className="text-sm capitalize">{region}</span>
                      <div className="flex items-center space-x-2">
                        <div className="w-20 h-2 bg-gray-200 rounded-full overflow-hidden">
                          <div
                            className="h-full bg-green-500"
                            style={{ width: `${percentage}%` }}
                          ></div>
                        </div>
                        <span className="text-sm font-semibold">{percentage}%</span>
                      </div>
                    </div>
                  ))}
                </div>
              </CardContent>
            </Card>

            {/* Asset Class Diversification */}
            <Card>
              <CardHeader>
                <CardTitle>Asset Class Allocation</CardTitle>
              </CardHeader>
              <CardContent>
                <div className="space-y-3">
                  {Object.entries(analysisData.diversification.assetClassConcentration).map(([assetClass, percentage]) => (
                    <div key={assetClass} className="flex items-center justify-between">
                      <span className="text-sm capitalize">{assetClass}</span>
                      <div className="flex items-center space-x-2">
                        <div className="w-20 h-2 bg-gray-200 rounded-full overflow-hidden">
                          <div
                            className="h-full bg-purple-500"
                            style={{ width: `${percentage}%` }}
                          ></div>
                        </div>
                        <span className="text-sm font-semibold">{percentage}%</span>
                      </div>
                    </div>
                  ))}
                </div>
              </CardContent>
            </Card>
          </div>
        </TabsContent>

        {/* Optimization Tab */}
        <TabsContent value="optimization" className="space-y-6">
          <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
            {/* Rebalancing Recommendations */}
            <Card>
              <CardHeader>
                <CardTitle>Rebalancing Recommendations</CardTitle>
              </CardHeader>
              <CardContent>
                <div className="space-y-4">
                  {analysisData.optimization.rebalancingNeeded ? (
                    <div className="p-4 bg-yellow-50 border border-yellow-200 rounded-lg">
                      <div className="flex items-center space-x-2 mb-2">
                        <div className="text-yellow-600">⚠️</div>
                        <h4 className="font-semibold text-yellow-900">Rebalancing Needed</h4>
                      </div>
                      <p className="text-sm text-yellow-700 mb-3">
                        Your portfolio has drifted {formatPercentage(analysisData.optimization.driftAmount)} from target allocation.
                      </p>
                      <Button
                        onClick={onRebalance}
                        className="bg-yellow-600 hover:bg-yellow-700"
                      >
                        Rebalance Portfolio
                      </Button>
                    </div>
                  ) : (
                    <div className="p-4 bg-green-50 border border-green-200 rounded-lg">
                      <div className="flex items-center space-x-2 mb-2">
                        <div className="text-green-600">✅</div>
                        <h4 className="font-semibold text-green-900">Well Balanced</h4>
                      </div>
                      <p className="text-sm text-green-700">
                        Your portfolio is within target allocation ranges.
                      </p>
                    </div>
                  )}
                </div>
              </CardContent>
            </Card>

            {/* Tax Optimization */}
            <Card>
              <CardHeader>
                <CardTitle>Tax Optimization</CardTitle>
              </CardHeader>
              <CardContent>
                <div className="space-y-4">
                  <div className="p-4 bg-blue-50 border border-blue-200 rounded-lg">
                    <div className="flex items-center space-x-2 mb-2">
                        <div className="text-blue-600">💰</div>
                        <h4 className="font-semibold text-blue-900">Tax-Loss Harvesting</h4>
                    </div>
                    <p className="text-sm text-blue-700 mb-3">
                      You have {formatCurrency(analysisData.optimization.taxLossHarvesting)} in unrealized losses available for harvesting.
                    </p>
                    <Button
                      onClick={onOptimize}
                      className="bg-blue-600 hover:bg-blue-700"
                    >
                      Optimize Tax Strategy
                    </Button>
                  </div>
                </div>
              </CardContent>
            </Card>
          </div>

          {/* Concentration Risk Alert */}
          {analysisData.optimization.concentrationRisk.isHigh && (
            <Card className="border-red-200 bg-red-50">
              <CardContent className="p-6">
                <div className="flex items-start space-x-4">
                  <div className="text-red-600 text-xl">⚠️</div>
                  <div>
                    <h4 className="font-semibold text-red-900 mb-2">Concentration Risk Alert</h4>
                    <p className="text-red-700 mb-4">
                      {analysisData.optimization.concentrationRisk.description}. Consider diversifying across sectors to reduce risk.
                    </p>
                    <Button
                      onClick={onOptimize}
                      className="bg-red-600 hover:bg-red-700"
                    >
                      Optimize Diversification
                    </Button>
                  </div>
                </div>
              </CardContent>
            </Card>
          )}
        </TabsContent>
      </Tabs>
    </div>
  );
}
