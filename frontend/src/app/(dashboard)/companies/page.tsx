'use client';

import { useState, useEffect } from 'react';
import Link from 'next/link';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Badge } from '@/components/ui/badge';
import { DashboardPageLayout, StatsCard, SearchFilterBar, EmptyState } from '@/components/layouts';
import { Search, TrendingUp, TrendingDown, Building2 } from 'lucide-react';

interface Company {
  symbol: string;
  name: string;
  sector: string;
  industry: string;
  market_cap: number;
  pe_ratio?: number;
  price_change?: number;
  price_change_percent?: number;
}

export default function CompaniesPage() {
  const [companies, setCompanies] = useState<Company[]>([]);
  const [loading, setLoading] = useState(true);
  const [searchTerm, setSearchTerm] = useState('');
  const [filteredCompanies, setFilteredCompanies] = useState<Company[]>([]);

  // Mock companies data - in real app, this would come from API
  const mockCompanies: Company[] = [
    {
      symbol: 'AAPL',
      name: 'Apple Inc.',
      sector: 'Technology',
      industry: 'Consumer Electronics',
      market_cap: 3000000000000,
      pe_ratio: 28.5,
      price_change: 2.15,
      price_change_percent: 1.2
    },
    {
      symbol: 'MSFT',
      name: 'Microsoft Corporation',
      sector: 'Technology',
      industry: 'Software',
      market_cap: 2800000000000,
      pe_ratio: 32.1,
      price_change: -1.25,
      price_change_percent: -0.8
    },
    {
      symbol: 'GOOGL',
      name: 'Alphabet Inc.',
      sector: 'Technology',
      industry: 'Internet',
      market_cap: 1800000000000,
      pe_ratio: 25.3,
      price_change: 5.75,
      price_change_percent: 2.1
    },
    {
      symbol: 'AMZN',
      name: 'Amazon.com Inc.',
      sector: 'Consumer Discretionary',
      industry: 'E-commerce',
      market_cap: 1500000000000,
      pe_ratio: 45.2,
      price_change: -0.85,
      price_change_percent: -0.5
    },
    {
      symbol: 'TSLA',
      name: 'Tesla Inc.',
      sector: 'Consumer Discretionary',
      industry: 'Electric Vehicles',
      market_cap: 800000000000,
      pe_ratio: 65.8,
      price_change: 12.30,
      price_change_percent: 3.2
    },
    {
      symbol: 'NVDA',
      name: 'NVIDIA Corporation',
      sector: 'Technology',
      industry: 'Semiconductors',
      market_cap: 1200000000000,
      pe_ratio: 55.4,
      price_change: 8.45,
      price_change_percent: 1.8
    }
  ];

  useEffect(() => {
    // Simulate API call
    const loadCompanies = async () => {
      setLoading(true);
      // In real app, this would be: const data = await apiClient.getCompanies();
      await new Promise(resolve => setTimeout(resolve, 1000)); // Simulate loading
      setCompanies(mockCompanies);
      setFilteredCompanies(mockCompanies);
      setLoading(false);
    };

    loadCompanies();
  }, []);

  useEffect(() => {
    const filtered = companies.filter(company =>
      company.symbol.toLowerCase().includes(searchTerm.toLowerCase()) ||
      company.name.toLowerCase().includes(searchTerm.toLowerCase()) ||
      company.sector.toLowerCase().includes(searchTerm.toLowerCase())
    );
    setFilteredCompanies(filtered);
  }, [searchTerm, companies]);

  const formatMarketCap = (marketCap: number) => {
    if (marketCap >= 1e12) {
      return `$${(marketCap / 1e12).toFixed(1)}T`;
    } else if (marketCap >= 1e9) {
      return `$${(marketCap / 1e9).toFixed(1)}B`;
    } else if (marketCap >= 1e6) {
      return `$${(marketCap / 1e6).toFixed(1)}M`;
    }
    return `$${marketCap.toLocaleString()}`;
  };

  const getSectorColor = (sector: string) => {
    const colors: { [key: string]: string } = {
      'Technology': 'bg-blue-100 text-blue-800',
      'Consumer Discretionary': 'bg-green-100 text-green-800',
      'Healthcare': 'bg-purple-100 text-purple-800',
      'Financials': 'bg-yellow-100 text-yellow-800',
      'Industrials': 'bg-gray-100 text-gray-800',
      'Energy': 'bg-orange-100 text-orange-800',
      'Utilities': 'bg-cyan-100 text-cyan-800',
      'Materials': 'bg-pink-100 text-pink-800',
      'Real Estate': 'bg-indigo-100 text-indigo-800',
      'Communication Services': 'bg-teal-100 text-teal-800'
    };
    return colors[sector] || 'bg-gray-100 text-gray-800';
  };

  return (
    <DashboardPageLayout
      title="Companies"
      description="Explore and analyze companies across different sectors"
      loading={loading}
      loadingText="Loading companies..."
      status={[
        { label: 'API', value: 'Connected', color: 'green' },
        { label: 'Backend', value: 'FastAPI', color: 'blue' }
      ]}
    >
      {/* Search and Filters */}
      <SearchFilterBar
        searchValue={searchTerm}
        onSearchChange={setSearchTerm}
        searchPlaceholder="Search companies by symbol, name, or sector..."
      />

      {/* Stats */}
      <div className="grid grid-cols-1 md:grid-cols-3 gap-4 mb-8">
        <StatsCard
          title="Total Companies"
          value={filteredCompanies.length}
          icon={<Building2 className="h-8 w-8 text-blue-600" />}
        />
        <StatsCard
          title="Gainers"
          value={filteredCompanies.filter(c => (c.price_change_percent || 0) > 0).length}
          icon={<TrendingUp className="h-8 w-8 text-green-600" />}
          trend="up"
        />
        <StatsCard
          title="Losers"
          value={filteredCompanies.filter(c => (c.price_change_percent || 0) < 0).length}
          icon={<TrendingDown className="h-8 w-8 text-red-600" />}
          trend="down"
        />
      </div>

      {/* Companies Grid */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
        {filteredCompanies.map((company) => (
          <Card key={company.symbol} className="hover:shadow-lg transition-shadow">
            <CardHeader>
              <div className="flex items-center justify-between">
                <div>
                  <Link href={`/companies/${company.symbol}`}>
                    <CardTitle className="text-xl text-blue-600 hover:text-blue-800 hover:underline cursor-pointer">{company.symbol}</CardTitle>
                  </Link>
                  <CardDescription className="text-sm">{company.name}</CardDescription>
                </div>
                <Badge className={getSectorColor(company.sector)}>
                  {company.sector}
                </Badge>
              </div>
            </CardHeader>
            <CardContent>
              <div className="space-y-3">
                <div className="flex justify-between">
                  <span className="text-sm text-gray-600">Market Cap</span>
                  <span className="font-medium">{formatMarketCap(company.market_cap)}</span>
                </div>

                {company.pe_ratio && (
                  <div className="flex justify-between">
                    <span className="text-sm text-gray-600">P/E Ratio</span>
                    <span className="font-medium">{company.pe_ratio.toFixed(1)}</span>
                  </div>
                )}

                {company.price_change_percent && (
                  <div className="flex justify-between">
                    <span className="text-sm text-gray-600">Change</span>
                    <div className="flex items-center">
                      {company.price_change_percent > 0 ? (
                        <TrendingUp className="h-4 w-4 text-green-600 mr-1" />
                      ) : (
                        <TrendingDown className="h-4 w-4 text-red-600 mr-1" />
                      )}
                      <span className={`font-medium ${
                        company.price_change_percent > 0 ? 'text-green-600' : 'text-red-600'
                      }`}>
                        {company.price_change_percent > 0 ? '+' : ''}{company.price_change_percent.toFixed(2)}%
                      </span>
                    </div>
                  </div>
                )}

                <div className="pt-3">
                  <Link href={`/companies/${company.symbol}`}>
                    <Button>
                      View Analysis
                    </Button>
                  </Link>
                </div>
              </div>
            </CardContent>
          </Card>
        ))}
      </div>

      {filteredCompanies.length === 0 && (
        <EmptyState
          icon={<Building2 className="h-12 w-12 text-gray-400" />}
          title="No companies found"
          description="Try adjusting your search terms"
        />
      )}
    </DashboardPageLayout>
  );
}
