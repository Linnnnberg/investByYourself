'use client';

import { useState, useEffect } from 'react';
import Link from 'next/link';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Badge } from '@/components/ui/badge';
import { Tabs, TabsContent, TabsList, TabsTrigger } from '@/components/ui/tabs';
import { HistoricalDataDashboard } from '@/components/charts/HistoricalDataDashboard';
import AppLayout from '@/components/layouts/AppLayout';

interface CompanyPageProps {
  params: {
    symbol: string;
  };
}

export default function CompanyPage({ params }: CompanyPageProps) {
  const [company, setCompany] = useState<any>(null);
  const [loading, setLoading] = useState(true);

  // Mock company data
  const mockCompany = {
    symbol: params.symbol.toUpperCase(),
    name: `${params.symbol.toUpperCase()} Inc.`,
    price: 175.43,
    change: 2.15,
    changePercent: 1.24,
    sector: 'Technology',
    marketCap: '2.8T',
    pe: 28.5,
    volume: '45.2M',
    description: 'A leading technology company focused on innovation and growth.',
  };

  useEffect(() => {
    // Simulate loading
    setTimeout(() => {
      setCompany(mockCompany);
      setLoading(false);
    }, 1000);
  }, [params.symbol]);

  if (loading) {
    return (
      <AppLayout>
        <div className="flex items-center justify-center min-h-96">
          <div className="text-center">
            <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-600 mx-auto mb-4"></div>
            <p className="text-gray-600">Loading company data...</p>
          </div>
        </div>
      </AppLayout>
    );
  }

  return (
    <AppLayout>
      <div className="flex items-center justify-between mb-6">
        <div className="flex items-center space-x-4">
          <Link href="/companies">
            <Button variant="outline">← Back to Companies</Button>
          </Link>
          <div>
            <h1 className="text-3xl font-bold text-gray-900">{company?.name}</h1>
            <p className="text-gray-600">{company?.symbol} • {company?.sector}</p>
          </div>
        </div>
        <div className="flex items-center space-x-4">
          <Button variant="outline">Add to Watchlist</Button>
          <Button>Buy Stock</Button>
        </div>
      </div>
        {/* Company Header */}
        <div className="mb-8">
          <div className="flex items-center space-x-4 mb-4">
            <div className="w-16 h-16 bg-blue-100 rounded-full flex items-center justify-center">
              <span className="text-blue-600 font-bold text-2xl">{company.symbol[0]}</span>
            </div>
            <div>
              <h1 className="text-3xl font-bold text-gray-900">{company.symbol}</h1>
              <p className="text-lg text-gray-600">{company.name}</p>
              <Badge variant="secondary" className="mt-2">{company.sector}</Badge>
            </div>
          </div>

          <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
            <Card>
              <CardContent className="p-4">
                <div className="text-2xl font-bold">${company.price.toFixed(2)}</div>
                <div className="text-sm text-gray-600">Current Price</div>
              </CardContent>
            </Card>
            <Card>
              <CardContent className="p-4">
                <div className={`text-2xl font-bold ${company.changePercent >= 0 ? 'text-green-600' : 'text-red-600'}`}>
                  {company.change >= 0 ? '+' : ''}${company.change.toFixed(2)}
                </div>
                <div className="text-sm text-gray-600">Change</div>
              </CardContent>
            </Card>
            <Card>
              <CardContent className="p-4">
                <div className="text-2xl font-bold">{company.marketCap}</div>
                <div className="text-sm text-gray-600">Market Cap</div>
              </CardContent>
            </Card>
            <Card>
              <CardContent className="p-4">
                <div className="text-2xl font-bold">{company.pe}</div>
                <div className="text-sm text-gray-600">P/E Ratio</div>
              </CardContent>
            </Card>
          </div>
        </div>

        {/* Company Details Tabs */}
        <Tabs defaultValue="overview" className="space-y-6">
          <TabsList>
            <TabsTrigger value="overview">Overview</TabsTrigger>
            <TabsTrigger value="charts">Charts</TabsTrigger>
            <TabsTrigger value="financials">Financials</TabsTrigger>
            <TabsTrigger value="news">News</TabsTrigger>
          </TabsList>

          <TabsContent value="overview" className="space-y-6">
            <Card>
              <CardHeader>
                <CardTitle>Company Description</CardTitle>
              </CardHeader>
              <CardContent>
                <p className="text-gray-600">{company.description}</p>
              </CardContent>
            </Card>

            <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
              <Card>
                <CardHeader>
                  <CardTitle>Key Metrics</CardTitle>
                </CardHeader>
                <CardContent className="space-y-3">
                  <div className="flex justify-between">
                    <span className="text-gray-600">Volume</span>
                    <span className="font-semibold">{company.volume}</span>
                  </div>
                  <div className="flex justify-between">
                    <span className="text-gray-600">Sector</span>
                    <span className="font-semibold">{company.sector}</span>
                  </div>
                  <div className="flex justify-between">
                    <span className="text-gray-600">P/E Ratio</span>
                    <span className="font-semibold">{company.pe}</span>
                  </div>
                </CardContent>
              </Card>

              <Card>
                <CardHeader>
                  <CardTitle>Price Performance</CardTitle>
                </CardHeader>
                <CardContent>
                  <div className="text-center">
                    <div className="text-3xl font-bold text-green-600">+{company.changePercent.toFixed(2)}%</div>
                    <div className="text-sm text-gray-600">Today's Performance</div>
                  </div>
                </CardContent>
              </Card>
            </div>
          </TabsContent>

          <TabsContent value="charts">
            <Card>
              <CardHeader>
                <CardTitle>Historical Data & Technical Analysis</CardTitle>
              </CardHeader>
              <CardContent>
                <HistoricalDataDashboard symbol={company.symbol} />
              </CardContent>
            </Card>
          </TabsContent>

          <TabsContent value="financials">
            <Card>
              <CardHeader>
                <CardTitle>Financial Statements</CardTitle>
              </CardHeader>
              <CardContent>
                <div className="text-center py-8">
                  <div className="text-4xl mb-4">📊</div>
                  <p className="text-gray-600">Financial data coming soon...</p>
                </div>
              </CardContent>
            </Card>
          </TabsContent>

          <TabsContent value="news">
            <Card>
              <CardHeader>
                <CardTitle>Latest News</CardTitle>
              </CardHeader>
              <CardContent>
                <div className="text-center py-8">
                  <div className="text-4xl mb-4">📰</div>
                  <p className="text-gray-600">News feed coming soon...</p>
                </div>
              </CardContent>
            </Card>
          </TabsContent>
        </Tabs>
    </AppLayout>
  );
}
