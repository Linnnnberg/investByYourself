'use client';

import { useState, useEffect } from 'react';
import Link from 'next/link';
import { Card, CardHeader, CardContent, CardFooter } from '@/design-system/components/Card';
import { Button } from '@/design-system/components/Button';
import { services } from '@/lib/supabase-service';
import { useMarketDataRealtime, usePortfolioRealtime, useWatchlistRealtime } from '@/hooks/useSupabaseRealtime';
import { Tables } from '@/lib/supabase';

// Mock user ID for demo (in real app, this would come from auth)
const DEMO_USER_ID = 'demo-user-123';

export default function DashboardPage() {
  const [companies, setCompanies] = useState<Tables<'companies'>[]>([]);
  const [portfolios, setPortfolios] = useState<Tables<'portfolios'>[]>([]);
  const [watchlist, setWatchlist] = useState<Tables<'watchlist'>[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  // Real-time subscriptions
  const { data: marketUpdates, isConnected: marketConnected } = useMarketDataRealtime();
  const { data: portfolioUpdates, isConnected: portfolioConnected } = usePortfolioRealtime(DEMO_USER_ID);
  const { data: watchlistUpdates, isConnected: watchlistConnected } = useWatchlistRealtime(DEMO_USER_ID);

  // Load initial data
  useEffect(() => {
    const loadInitialData = async () => {
      try {
        setLoading(true);

        // Load companies
        const companiesData = await services.companies.getCompanies();
        setCompanies(companiesData.slice(0, 10)); // Show top 10 for demo

        // Load portfolios
        const portfoliosData = await services.portfolios.getUserPortfolios(DEMO_USER_ID);
        setPortfolios(portfoliosData);

        // Load watchlist
        const watchlistData = await services.watchlist.getUserWatchlist(DEMO_USER_ID);
        setWatchlist(watchlistData);

      } catch (err) {
        setError(err instanceof Error ? err.message : 'Failed to load data');
      } finally {
        setLoading(false);
      }
    };

    loadInitialData();
  }, []);

  // Update data when real-time updates come in
  useEffect(() => {
    if (marketUpdates.length > 0) {
      setCompanies(prev => {
        const updated = [...prev];
        marketUpdates.forEach(update => {
          const index = updated.findIndex(c => c.id === update.id);
          if (index >= 0) {
            updated[index] = { ...updated[index], ...update };
          }
        });
        return updated;
      });
    }
  }, [marketUpdates]);

  useEffect(() => {
    if (portfolioUpdates.length > 0) {
      setPortfolios(portfolioUpdates);
    }
  }, [portfolioUpdates]);

  useEffect(() => {
    if (watchlistUpdates.length > 0) {
      setWatchlist(watchlistUpdates);
    }
  }, [watchlistUpdates]);

  // Handle adding to watchlist
  const handleAddToWatchlist = async (symbol: string) => {
    try {
      await services.watchlist.addToWatchlist({
        user_id: DEMO_USER_ID,
        company_symbol: symbol,
      });
    } catch (err) {
      console.error('Failed to add to watchlist:', err);
    }
  };

  // Handle removing from watchlist
  const handleRemoveFromWatchlist = async (id: string) => {
    try {
      await services.watchlist.removeFromWatchlist(id);
    } catch (err) {
      console.error('Failed to remove from watchlist:', err);
    }
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
            <span className={`inline-block w-2 h-2 rounded-full mr-2 ${marketConnected ? 'bg-green-500' : 'bg-red-500'}`}></span>
            Market Data: {marketConnected ? 'Connected' : 'Disconnected'}
          </div>
          <div className="text-sm text-gray-500">
            <span className={`inline-block w-2 h-2 rounded-full mr-2 ${portfolioConnected ? 'bg-green-500' : 'bg-red-500'}`}></span>
            Portfolio: {portfolioConnected ? 'Connected' : 'Disconnected'}
          </div>
        </div>
      </div>

      {/* Quick Actions */}
      <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
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
                      <div className="font-semibold">{company.symbol}</div>
                      <div className="text-sm text-gray-600">{company.name}</div>
                    </div>
                  </div>
                  <div className="text-right">
                    <div className="font-semibold">${company.price.toFixed(2)}</div>
                    <div className={`text-sm ${company.change_percent >= 0 ? 'text-green-600' : 'text-red-600'}`}>
                      {company.change_percent >= 0 ? '+' : ''}{company.change_percent.toFixed(2)}%
                    </div>
                  </div>
                </div>
              ))}
            </div>
          </CardContent>
          <CardFooter>
            <Link href="/companies" className="w-full">
              <Button variant="outline" className="w-full">View All Companies</Button>
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
                    <div className="text-2xl font-bold text-green-600">
                      ${portfolio.total_value.toLocaleString()}
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
            <Link href="/portfolio" className="w-full">
              <Button variant="outline" className="w-full">Manage Portfolios</Button>
            </Link>
          </CardFooter>
        </Card>
      </div>

      {/* Watchlist */}
      <Card>
        <CardHeader>
          <h2 className="text-xl font-semibold">Watchlist</h2>
          <p className="text-gray-600">Companies you're monitoring</p>
        </CardHeader>
        <CardContent>
          {watchlist.length > 0 ? (
            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
              {watchlist.map((item) => {
                const company = companies.find(c => c.symbol === item.company_symbol);
                if (!company) return null;

                return (
                  <div key={item.id} className="p-4 border rounded-lg">
                    <div className="flex items-center justify-between mb-2">
                      <div className="flex items-center space-x-2">
                        <span className="font-semibold">{company.symbol}</span>
                        <span className="text-sm text-gray-600">{company.name}</span>
                      </div>
                      <Button
                        variant="ghost"
                        size="small"
                        onClick={() => handleRemoveFromWatchlist(item.id)}
                      >
                        ✕
                      </Button>
                    </div>
                    <div className="text-lg font-bold">${company.price.toFixed(2)}</div>
                    <div className={`text-sm ${company.change_percent >= 0 ? 'text-green-600' : 'text-red-600'}`}>
                      {company.change_percent >= 0 ? '+' : ''}{company.change_percent.toFixed(2)}%
                    </div>
                  </div>
                );
              })}
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
          <Link href="/watchlist" className="w-full">
            <Button variant="outline" className="w-full">Manage Watchlist</Button>
          </Link>
        </CardFooter>
      </Card>
    </div>
  );
}
