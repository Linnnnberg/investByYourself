'use client';

import { useState, useEffect } from 'react';
import Link from 'next/link';
import { Card, CardHeader, CardContent, CardFooter } from '@/design-system/components/Card';
import { Button } from '@/design-system/components/Button';
import { useApiClient, useApiCall } from '@/hooks/useApiClient';
import { Portfolio } from '@/lib/api-client';

export default function DashboardPage() {
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

  // Mock companies data for demo (will be replaced with real market data later)
  const companies = [
    { id: 1, symbol: 'AAPL', name: 'Apple Inc.', price: 175.43, change: 2.15, changePercent: 1.24 },
    { id: 2, symbol: 'GOOGL', name: 'Alphabet Inc.', price: 142.56, change: -1.23, changePercent: -0.86 },
    { id: 3, symbol: 'MSFT', name: 'Microsoft Corporation', price: 378.85, change: 5.67, changePercent: 1.52 },
    { id: 4, symbol: 'TSLA', name: 'Tesla, Inc.', price: 248.42, change: -3.21, changePercent: -1.27 },
  ];

  // Mock watchlist data for demo
  const watchlist = companies.slice(0, 3);

  // Handle removing from watchlist (mock for now)
  const handleRemoveFromWatchlist = async (id: string) => {
    console.log('Removing from watchlist:', id);
    // TODO: Implement watchlist API
  };

  if (loading) {
    return (
      <div className="flex items-center justify-center min-h-screen">
        <div className="text-center">
          <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-600 mx-auto mb-4"></div>
          <p className="text-gray-600">Loading dashboard...</p>
        </div>
      </div>
    );
  }

  if (error) {
    return (
      <div className="flex items-center justify-center min-h-screen">
        <div className="text-center">
          <div className="text-red-600 text-6xl mb-4">⚠️</div>
          <h2 className="text-xl font-semibold text-gray-900 mb-2">Error Loading Dashboard</h2>
          <p className="text-gray-600 mb-4">{error}</p>
          <Button onClick={() => window.location.reload()}>Retry</Button>
        </div>
      </div>
    );
  }

  return (
    <div className="p-6 space-y-6">
      {/* Header */}
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-3xl font-bold text-gray-900">Dashboard</h1>
          <p className="text-gray-600">Welcome to your investment dashboard</p>
        </div>
        <div className="flex items-center space-x-4">
          <div className="text-sm text-gray-500">
            <span className={`inline-block w-2 h-2 rounded-full mr-2 ${isAuthenticated ? 'bg-green-500' : 'bg-yellow-500'}`}></span>
            API: {isAuthenticated ? 'Connected' : 'Demo Mode'}
          </div>
          <div className="text-sm text-gray-500">
            <span className="inline-block w-2 h-2 rounded-full mr-2 bg-blue-500"></span>
            Backend: FastAPI
          </div>
        </div>
      </div>

      {/* Quick Actions */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
        <Card variant="interactive" onClick={() => window.location.href = '/investment-profile'}>
          <CardContent className="text-center p-6">
            <div className="text-4xl mb-2">📊</div>
            <h3 className="text-lg font-semibold mb-2">Investment Profile</h3>
            <p className="text-gray-600">Get your personalized risk assessment</p>
          </CardContent>
        </Card>

        <Card variant="interactive" onClick={() => window.location.href = '/companies'}>
          <CardContent className="text-center p-6">
            <div className="text-4xl mb-2">🔍</div>
            <h3 className="text-lg font-semibold mb-2">Browse Companies</h3>
            <p className="text-gray-600">Discover and analyze companies</p>
          </CardContent>
        </Card>

        <Card variant="interactive" onClick={() => window.location.href = '/portfolio'}>
          <CardContent className="text-center p-6">
            <div className="text-4xl mb-2">💼</div>
            <h3 className="text-lg font-semibold mb-2">Manage Portfolio</h3>
            <p className="text-gray-600">Track your investments</p>
          </CardContent>
        </Card>

        <Card variant="interactive" onClick={() => window.location.href = '/watchlist'}>
          <CardContent className="text-center p-6">
            <div className="text-4xl mb-2">⭐</div>
            <h3 className="text-lg font-semibold mb-2">Watchlist</h3>
            <p className="text-gray-600">Monitor your favorite stocks</p>
          </CardContent>
        </Card>
      </div>

      {/* Market Overview */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        {/* Top Companies */}
        <Card>
          <CardHeader>
            <h2 className="text-xl font-semibold">Top Companies</h2>
            <p className="text-gray-600">Real-time market data</p>
          </CardHeader>
          <CardContent>
            <div className="space-y-3">
              {companies.map((company) => (
                <div key={company.id} className="flex items-center justify-between p-3 bg-gray-50 rounded-lg">
                  <div className="flex items-center space-x-3">
                    <div className="w-10 h-10 bg-blue-100 rounded-full flex items-center justify-center">
                      <span className="text-blue-600 font-semibold">{company.symbol[0]}</span>
                    </div>
                    <div>
                      <Link href={`/companies/${company.symbol}`}>
                        <div className="font-semibold text-blue-600 hover:text-blue-800 hover:underline cursor-pointer">{company.symbol}</div>
                      </Link>
                      <div className="text-sm text-gray-600">{company.name}</div>
                    </div>
                  </div>
                  <div className="text-right">
                    <div className="font-semibold">${company.price.toFixed(2)}</div>
                    <div className={`text-sm ${company.changePercent >= 0 ? 'text-green-600' : 'text-red-600'}`}>
                      {company.changePercent >= 0 ? '+' : ''}{company.changePercent.toFixed(2)}%
                    </div>
                  </div>
                </div>
              ))}
            </div>
          </CardContent>
          <CardFooter>
            <Link href="/companies">
              <Button variant="outline">View All Companies</Button>
            </Link>
          </CardFooter>
        </Card>

        {/* Portfolio Summary */}
        <Card>
          <CardHeader>
            <h2 className="text-xl font-semibold">Portfolio Summary</h2>
            <p className="text-gray-600">Your investment overview</p>
          </CardHeader>
          <CardContent>
            {portfolios.length > 0 ? (
              <div className="space-y-4">
                {portfolios.map((portfolio) => (
                  <div key={portfolio.id} className="p-4 bg-gray-50 rounded-lg">
                    <div className="flex items-center justify-between mb-2">
                      <h3 className="font-semibold">{portfolio.name}</h3>
                      <span className="text-sm text-gray-500">{portfolio.description}</span>
                    </div>
                    <div className="grid grid-cols-2 gap-4">
                      <div>
                        <div className="text-sm text-gray-600">Total Value</div>
                        <div className="text-xl font-bold">{portfolio.total_value}</div>
                      </div>
                      <div>
                        <div className="text-sm text-gray-600">Gain/Loss</div>
                        <div className={`text-xl font-bold ${portfolio.total_gain_loss.startsWith('+') ? 'text-green-600' : 'text-red-600'}`}>
                          {portfolio.total_gain_loss} ({portfolio.total_gain_loss_pct})
                        </div>
                      </div>
                    </div>
                    <div className="mt-2 text-sm text-gray-500">
                      {portfolio.holdings_count} holdings • Risk: {portfolio.risk_profile}
                    </div>
                  </div>
                ))}
              </div>
            ) : (
              <div className="text-center py-8">
                <div className="text-4xl mb-4">💼</div>
                <p className="text-gray-600 mb-4">No portfolios yet</p>
                <Link href="/portfolio">
                  <Button>Create Portfolio</Button>
                </Link>
              </div>
            )}
          </CardContent>
          <CardFooter>
            <Link href="/portfolio">
              <Button variant="outline">Manage Portfolios</Button>
            </Link>
          </CardFooter>
        </Card>
      </div>

      {/* Watchlist */}
      <Card>
        <CardHeader>
          <h2 className="text-xl font-semibold">Watchlist</h2>
          <p className="text-gray-600">Companies you&apos;re monitoring</p>
        </CardHeader>
        <CardContent>
          {watchlist.length > 0 ? (
            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
              {watchlist.map((company) => (
                <div key={company.id} className="p-4 border rounded-lg">
                  <div className="flex items-center justify-between mb-2">
                    <div className="flex items-center space-x-2">
                      <Link href={`/companies/${company.symbol}`}>
                        <span className="font-semibold text-blue-600 hover:text-blue-800 hover:underline cursor-pointer">{company.symbol}</span>
                      </Link>
                      <span className="text-sm text-gray-600">{company.name}</span>
                    </div>
                    <Button
                      variant="ghost"
                      size="small"
                      onClick={() => handleRemoveFromWatchlist(company.id.toString())}
                    >
                      ✕
                    </Button>
                  </div>
                  <div className="text-lg font-bold">${company.price.toFixed(2)}</div>
                  <div className={`text-sm ${company.changePercent >= 0 ? 'text-green-600' : 'text-red-600'}`}>
                    {company.changePercent >= 0 ? '+' : ''}{company.changePercent.toFixed(2)}%
                  </div>
                </div>
              ))}
            </div>
          ) : (
            <div className="text-center py-8">
              <div className="text-4xl mb-4">⭐</div>
              <p className="text-gray-600 mb-4">Your watchlist is empty</p>
              <p className="text-sm text-gray-500">Add companies to start monitoring them</p>
            </div>
          )}
        </CardContent>
        <CardFooter>
          <Link href="/watchlist">
            <Button variant="outline">Manage Watchlist</Button>
          </Link>
        </CardFooter>
      </Card>
    </div>
  );
}
