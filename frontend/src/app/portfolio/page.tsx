'use client';

import { useState, useEffect } from 'react';
import Link from 'next/link';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Badge } from '@/components/ui/badge';
import { useApiClient, useApiCall } from '@/hooks/useApiClient';
import { Portfolio } from '@/lib/api-client';
import AppLayout from '@/components/layouts/AppLayout';

export default function PortfolioPage() {
  const { client, isAuthenticated, isLoading: authLoading } = useApiClient();
  const [portfolios, setPortfolios] = useState<Portfolio[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

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
      <div className="flex items-center justify-between mb-6">
        <div>
          <h1 className="text-3xl font-bold text-gray-900">Portfolio Management</h1>
          <p className="text-gray-600">Manage your investment portfolios</p>
        </div>
        <Button>Create Portfolio</Button>
      </div>

      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
        <div className="mb-8">
          <h1 className="text-3xl font-bold text-gray-900">Portfolio Management</h1>
          <p className="text-gray-600 mt-2">
            Create, track, and optimize your investment portfolios
          </p>
        </div>

        {portfolios.length > 0 ? (
          <div className="space-y-6">
            {/* Portfolio Summary Cards */}
            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
              {portfolios.map((portfolio) => (
                <Card key={portfolio.id} className="hover:shadow-lg transition-shadow">
                  <CardHeader>
                    <div className="flex items-center justify-between">
                      <CardTitle className="text-lg">{portfolio.name}</CardTitle>
                      <Badge variant="secondary">{portfolio.risk_profile}</Badge>
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
                      <div className="pt-2">
                        <Button className="w-full">View Details</Button>
                      </div>
                    </div>
                  </CardContent>
                </Card>
              ))}
            </div>

            {/* Quick Actions */}
            <Card>
              <CardHeader>
                <CardTitle>Quick Actions</CardTitle>
              </CardHeader>
              <CardContent>
                <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
                  <Button className="h-20 flex flex-col items-center justify-center">
                    <div className="text-2xl mb-2">➕</div>
                    <div>Create New Portfolio</div>
                  </Button>
                  <Button variant="outline" className="h-20 flex flex-col items-center justify-center">
                    <div className="text-2xl mb-2">📊</div>
                    <div>Portfolio Analysis</div>
                  </Button>
                  <Button variant="outline" className="h-20 flex flex-col items-center justify-center">
                    <div className="text-2xl mb-2">⚖️</div>
                    <div>Risk Assessment</div>
                  </Button>
                </div>
              </CardContent>
            </Card>
          </div>
        ) : (
          <div className="text-center py-12">
            <div className="text-6xl mb-6">💼</div>
            <h2 className="text-2xl font-bold text-gray-900 mb-4">No Portfolios Yet</h2>
            <p className="text-gray-600 mb-8 max-w-md mx-auto">
              Create your first portfolio to start tracking your investments and building wealth.
            </p>
            <div className="space-y-4">
              <Button size="lg" className="mr-4">Create Portfolio</Button>
              <Button variant="outline" size="lg">Learn More</Button>
            </div>
          </div>
        )}
      </div>
    </AppLayout>
  );
}
