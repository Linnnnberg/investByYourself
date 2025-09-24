'use client';

import { useState, useEffect } from 'react';
import Link from 'next/link';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { Badge } from '@/components/ui/badge';
import AppLayout from '@/components/layouts/AppLayout';
import { useApiClient, useApiCall } from '@/hooks/useApiClient';
import { WatchlistItem, Company } from '@/lib/api-client';

export default function WatchlistPage() {
  const { client, isAuthenticated, isLoading: authLoading } = useApiClient();
  const [searchTerm, setSearchTerm] = useState('');
  const [showAddCompany, setShowAddCompany] = useState(false);
  const [companySearchTerm, setCompanySearchTerm] = useState('');
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  // Load watchlist using FastAPI
  const { data: watchlistData, loading: watchlistLoading, error: watchlistError } = useApiCall(
    () => client.getWatchlist(),
    [isAuthenticated]
  );

  // Load watchlist summary
  const { data: summaryData } = useApiCall(
    () => client.getWatchlistSummary(),
    [isAuthenticated]
  );

  // Search companies for adding to watchlist
  const { data: searchResults, loading: searchLoading } = useApiCall(
    () => companySearchTerm.length > 2 ? client.getCompanies({
      search: companySearchTerm,
      limit: 10
    }) : Promise.resolve([]),
    [companySearchTerm]
  );

  // Update loading and error states
  useEffect(() => {
    setLoading(watchlistLoading || authLoading);
    setError(watchlistError);
  }, [watchlistLoading, authLoading, watchlistError]);

  const watchlist = watchlistData || [];

  const filteredWatchlist = watchlist.filter(item =>
    item.name.toLowerCase().includes(searchTerm.toLowerCase()) ||
    item.symbol.toLowerCase().includes(searchTerm.toLowerCase())
  );

  const handleRemoveFromWatchlist = async (symbol: string) => {
    try {
      await client.removeFromWatchlist(symbol);
      // The watchlist will be refetched automatically due to the useApiCall hook
    } catch (error) {
      console.error('Failed to remove from watchlist:', error);
    }
  };

  const handleAddToWatchlist = async (symbol: string) => {
    try {
      await client.addToWatchlist(symbol);
      setShowAddCompany(false);
      setCompanySearchTerm('');
      // The watchlist will be refetched automatically due to the useApiCall hook
    } catch (error) {
      console.error('Failed to add to watchlist:', error);
    }
  };

  if (loading) {
    return (
      <AppLayout>
        <div className="flex items-center justify-center min-h-screen">
          <div className="text-center">
            <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-600 mx-auto mb-4"></div>
            <p className="text-gray-600">Loading watchlist...</p>
          </div>
        </div>
      </AppLayout>
    );
  }

  if (error) {
    return (
      <AppLayout>
        <div className="flex items-center justify-center min-h-screen">
          <div className="text-center">
            <div className="text-red-600 text-6xl mb-4">⚠️</div>
            <h2 className="text-xl font-semibold text-gray-900 mb-2">Error Loading Watchlist</h2>
            <p className="text-gray-600 mb-4">{error}</p>
            <Button onClick={() => window.location.reload()}>Retry</Button>
          </div>
        </div>
      </AppLayout>
    );
  }

  return (
    <AppLayout>
      <div className="mb-4">
        <div className="flex items-center justify-between mb-4">
          <div>
            <h1 className="text-2xl font-bold text-gray-900" data-testid="watchlist-page-title">Watchlist</h1>
            <p className="text-gray-600 text-sm" data-testid="watchlist-page-description">Track companies you're interested in</p>
          </div>
          <Button
            onClick={() => setShowAddCompany(!showAddCompany)}
            size="small"
            data-testid="watchlist-add-company-button"
            data-feature="watchlist-add-company"
          >
            {showAddCompany ? 'Cancel' : 'Add Company'}
          </Button>
        </div>

        {/* Add Company Search */}
        {showAddCompany && (
          <Card className="mb-4" data-testid="watchlist-add-company-card" data-feature="watchlist-add-company">
            <CardContent className="p-4">
              <div className="mb-3">
                <label className="text-sm font-medium text-gray-700 mb-2 block" data-testid="watchlist-search-label">Search Companies</label>
                <Input
                  placeholder="Type company name or symbol..."
                  value={companySearchTerm}
                  onChange={(e) => setCompanySearchTerm(e.target.value)}
                  className="max-w-md"
                  data-testid="watchlist-company-search-input"
                  data-feature="search-companies"
                />
              </div>
              {searchResults && searchResults.length > 0 && (
                <div className="space-y-2 max-h-48 overflow-y-auto" data-testid="watchlist-search-results" data-feature="search-results">
                  {searchResults.map((company) => (
                    <div
                      key={company.id}
                      className="flex items-center justify-between p-2 border rounded hover:bg-gray-50"
                      data-testid={`search-result-${company.symbol.toLowerCase()}`}
                      data-feature="search-result-item"
                    >
                      <div className="flex items-center space-x-2">
                        <div className="w-6 h-6 bg-blue-100 rounded-full flex items-center justify-center" data-testid="company-symbol-icon">
                          <span className="text-blue-600 font-bold text-xs">{company.symbol[0]}</span>
                        </div>
                        <div>
                          <span className="font-medium text-sm" data-testid="company-symbol">{company.symbol}</span>
                          <span className="text-xs text-gray-600 ml-2" data-testid="company-name">{company.name}</span>
                        </div>
                      </div>
                      <Button
                        size="small"
                        onClick={() => handleAddToWatchlist(company.symbol)}
                        disabled={watchlist.some(item => item.symbol === company.symbol)}
                        data-testid={`add-company-${company.symbol.toLowerCase()}-button`}
                        data-feature="add-company-button"
                      >
                        {watchlist.some(item => item.symbol === company.symbol) ? 'Added' : 'Add'}
                      </Button>
                    </div>
                  ))}
                </div>
              )}
            </CardContent>
          </Card>
        )}

        {/* Search */}
        <div className="mb-4">
          <Input
            placeholder="Search your watchlist..."
            value={searchTerm}
            onChange={(e) => setSearchTerm(e.target.value)}
            className="max-w-md"
            data-testid="watchlist-search-input"
            data-feature="watchlist-search"
          />
        </div>

        {/* Watchlist Summary - Compact */}
        <div className="grid grid-cols-4 gap-3 mb-4" data-testid="watchlist-summary-stats" data-feature="watchlist-stats">
          <Card data-testid="watchlist-total-card" data-feature="stats-total">
            <CardContent className="p-3">
              <div className="text-center">
                <div className="text-lg font-bold text-blue-600" data-testid="watchlist-total-count">{summaryData?.total_items || watchlist.length}</div>
                <div className="text-xs text-gray-600">Total</div>
              </div>
            </CardContent>
          </Card>
          <Card data-testid="watchlist-gainers-card" data-feature="stats-gainers">
            <CardContent className="p-3">
              <div className="text-center">
                <div className="text-lg font-bold text-green-600" data-testid="watchlist-gainers-count">
                  {summaryData?.gainers || watchlist.filter(item => item.change_percent > 0).length}
                </div>
                <div className="text-xs text-gray-600">Gainers</div>
              </div>
            </CardContent>
          </Card>
          <Card data-testid="watchlist-losers-card" data-feature="stats-losers">
            <CardContent className="p-3">
              <div className="text-center">
                <div className="text-lg font-bold text-red-600" data-testid="watchlist-losers-count">
                  {summaryData?.losers || watchlist.filter(item => item.change_percent < 0).length}
                </div>
                <div className="text-xs text-gray-600">Losers</div>
              </div>
            </CardContent>
          </Card>
          <Card data-testid="watchlist-avg-change-card" data-feature="stats-avg-change">
            <CardContent className="p-3">
              <div className="text-center">
                <div className="text-lg font-bold text-gray-600" data-testid="watchlist-avg-change-percent">
                  {summaryData?.avg_change_percent?.toFixed(2) ||
                   (watchlist.length > 0
                    ? (watchlist.reduce((sum, item) => sum + item.change_percent, 0) / watchlist.length).toFixed(2)
                    : '0.00'
                   )}%
                </div>
                <div className="text-xs text-gray-600">Avg Change</div>
              </div>
            </CardContent>
          </Card>
        </div>

        {/* Watchlist Items - Compact */}
        {filteredWatchlist.length > 0 ? (
          <div className="space-y-2" data-testid="watchlist-items-container" data-feature="watchlist-items">
            {filteredWatchlist.map((item) => (
              <Card
                key={item.id}
                className="hover:shadow-md transition-shadow"
                data-testid={`watchlist-item-${item.symbol.toLowerCase()}`}
                data-feature="watchlist-item"
              >
                <CardContent className="p-3">
                  <div className="flex items-center justify-between">
                    <div className="flex items-center space-x-3">
                      <div className="w-8 h-8 bg-blue-100 rounded-full flex items-center justify-center" data-testid="watchlist-item-symbol-icon">
                        <span className="text-blue-600 font-bold text-sm">{item.symbol[0]}</span>
                      </div>
                      <div className="flex-1">
                        <div className="flex items-center space-x-2">
                          <Link href={`/companies/${item.symbol}`}>
                            <span
                              className="font-semibold text-blue-600 hover:text-blue-800 hover:underline cursor-pointer text-sm"
                              data-testid="watchlist-item-symbol-link"
                            >
                              {item.symbol}
                            </span>
                          </Link>
                          <Badge variant="outline" className="text-xs" data-testid="watchlist-item-added-date">
                            {new Date(item.added_date).toLocaleDateString()}
                          </Badge>
                        </div>
                        <p className="text-xs text-gray-600 truncate max-w-48" data-testid="watchlist-item-name">{item.name}</p>
                      </div>
                    </div>

                    <div className="flex items-center space-x-4">
                      <div className="text-right">
                        <div className="text-lg font-bold" data-testid="watchlist-item-price">${item.price.toFixed(2)}</div>
                        <div className={`text-xs font-medium ${item.change_percent >= 0 ? 'text-green-600' : 'text-red-600'}`} data-testid="watchlist-item-change">
                          {item.change >= 0 ? '+' : ''}${item.change.toFixed(2)} ({item.change_percent >= 0 ? '+' : ''}{item.change_percent.toFixed(2)}%)
                        </div>
                      </div>
                      <Button
                        variant="ghost"
                        size="small"
                        onClick={() => handleRemoveFromWatchlist(item.symbol)}
                        className="text-red-600 hover:text-red-800 hover:bg-red-50 text-xs px-2 py-1"
                        data-testid={`remove-watchlist-item-${item.symbol.toLowerCase()}-button`}
                        data-feature="remove-watchlist-item"
                      >
                        ✕
                      </Button>
                    </div>
                  </div>
                </CardContent>
              </Card>
            ))}
          </div>
        ) : (
          <div className="text-center py-8">
            <div className="text-3xl mb-3">⭐</div>
            <h3 className="text-lg font-semibold text-gray-900 mb-2">
              {searchTerm ? 'No matching companies found' : 'Your watchlist is empty'}
            </h3>
            <p className="text-gray-600 mb-4 text-sm">
              {searchTerm
                ? 'Try adjusting your search terms'
                : 'Add companies to your watchlist to start monitoring their performance'
              }
            </p>
            {!searchTerm && (
              <Button size="small" onClick={() => setShowAddCompany(true)}>
                Add Your First Company
              </Button>
            )}
          </div>
        )}
      </div>
    </AppLayout>
  );
}
