'use client';

import { useState, useEffect } from 'react';
import Link from 'next/link';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { Badge } from '@/components/ui/badge';
import AppLayout from '@/components/layouts/AppLayout';
import { useApiClient, useApiCall } from '@/hooks/useApiClient';
import { Company } from '@/lib/api-client';

export default function CompaniesPage() {
  const { client, isAuthenticated, isLoading: authLoading } = useApiClient();
  const [searchTerm, setSearchTerm] = useState('');
  const [selectedSector, setSelectedSector] = useState('All');
  const [selectedCountry, setSelectedCountry] = useState('All');
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  // Load watchlist using FastAPI
  const { data: watchlistData, loading: watchlistLoading, error: watchlistError } = useApiCall(
    () => client.getWatchlist(),
    [isAuthenticated]
  );

  // Load sectors
  const { data: sectorsData } = useApiCall(
    () => client.getSectors(),
    [isAuthenticated]
  );

  // Update loading and error states
  useEffect(() => {
    setLoading(watchlistLoading || authLoading);
    setError(watchlistError);
  }, [watchlistLoading, authLoading, watchlistError]);

  const companies = watchlistData || [];

  // Filter watchlist items based on search term
  const filteredCompanies = companies.filter(company => {
    const matchesSearch = company.name.toLowerCase().includes(searchTerm.toLowerCase()) ||
                         company.symbol.toLowerCase().includes(searchTerm.toLowerCase());
    return matchesSearch;
  });

  if (loading) {
    return (
      <AppLayout>
        <div className="flex items-center justify-center min-h-screen">
          <div className="text-center">
            <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-600 mx-auto mb-4"></div>
            <p className="text-gray-600">Loading companies...</p>
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
            <h2 className="text-xl font-semibold text-gray-900 mb-2">Error Loading Companies</h2>
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
        <div className="mb-4">
          <h1 className="text-2xl font-bold text-gray-900" data-testid="markets-page-title">Markets</h1>
          <p className="text-gray-600 text-sm" data-testid="markets-page-description">
            Your watchlist companies
          </p>
        </div>

        {/* Search */}
        <div className="mb-4">
          <Input
            placeholder="Search your watchlist..."
            value={searchTerm}
            onChange={(e) => setSearchTerm(e.target.value)}
            className="max-w-md"
            data-testid="markets-search-input"
            data-feature="markets-search"
          />
        </div>

        {/* Companies Grid - Compact */}
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-3" data-testid="markets-companies-grid" data-feature="markets-companies">
          {filteredCompanies.map((company) => (
            <Card
              key={company.id}
              className="hover:shadow-md transition-shadow"
              data-testid={`markets-company-card-${company.symbol.toLowerCase()}`}
              data-feature="markets-company-card"
            >
              <CardContent className="p-4">
                <div className="flex items-center justify-between mb-2">
                  <div className="flex items-center space-x-2">
                    <div className="w-8 h-8 bg-blue-100 rounded-full flex items-center justify-center" data-testid="markets-company-symbol-icon">
                      <span className="text-blue-600 font-bold text-sm">{company.symbol[0]}</span>
                    </div>
                    <div>
                      <CardTitle className="text-sm font-semibold" data-testid="markets-company-symbol">{company.symbol}</CardTitle>
                      <p className="text-xs text-gray-600 truncate max-w-24" data-testid="markets-company-name">{company.name}</p>
                    </div>
                  </div>
                </div>
                <div className="flex justify-between items-center mb-2">
                  <span className="text-lg font-bold" data-testid="markets-company-price">${company.price.toFixed(2)}</span>
                  <div className="text-right">
                    <div className={`text-xs font-medium ${company.change_percent >= 0 ? 'text-green-600' : 'text-red-600'}`} data-testid="markets-company-change-amount">
                      {company.change >= 0 ? '+' : ''}${company.change.toFixed(2)}
                    </div>
                    <div className={`text-xs ${company.change_percent >= 0 ? 'text-green-600' : 'text-red-600'}`} data-testid="markets-company-change-percent">
                      {company.change_percent >= 0 ? '+' : ''}{company.change_percent.toFixed(2)}%
                    </div>
                  </div>
                </div>
                <Link href={`/companies/${company.symbol}`}>
                  <Button
                    className="w-full text-xs py-1"
                    variant="outline"
                    size="small"
                    data-testid={`markets-company-view-details-${company.symbol.toLowerCase()}-button`}
                    data-feature="markets-company-view-details"
                  >
                    View Details
                  </Button>
                </Link>
              </CardContent>
            </Card>
          ))}
        </div>

        {filteredCompanies.length === 0 && (
          <div className="text-center py-8">
            <div className="text-3xl mb-3">📈</div>
            <h3 className="text-lg font-semibold text-gray-900 mb-2">
              {searchTerm ? 'No companies found' : 'No companies in your watchlist'}
            </h3>
            <p className="text-gray-600 mb-4 text-sm">
              {searchTerm ? 'Try adjusting your search terms' : 'Add companies to your watchlist to see them here'}
            </p>
            <Link href="/watchlist">
              <Button size="small">
                {searchTerm ? 'Clear Search' : 'Go to Watchlist'}
              </Button>
            </Link>
          </div>
        )}
      </div>
    </AppLayout>
  );
}
