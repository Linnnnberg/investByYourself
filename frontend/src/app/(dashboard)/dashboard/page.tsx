'use client';

import { useState, useEffect } from 'react';
import Link from 'next/link';
import { CompanyProfile, Portfolio, apiClient } from '@/lib/api';

export default function DashboardPage() {
  const [watchlist, setWatchlist] = useState<CompanyProfile[]>([]);
  const [portfolios, setPortfolios] = useState<Portfolio[]>([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    const fetchDashboardData = async () => {
      try {
        // Fetch watchlist and portfolios
        const [watchlistResponse, portfoliosResponse] = await Promise.all([
          apiClient.getWatchlist(),
          apiClient.getPortfolios(),
        ]);

        if (watchlistResponse.success) {
          setWatchlist(watchlistResponse.data || []);
        }

        if (portfoliosResponse.success) {
          setPortfolios(portfoliosResponse.data || []);
        }
      } catch (error) {
        console.error('Failed to fetch dashboard data:', error);
      } finally {
        setLoading(false);
      }
    };

    fetchDashboardData();
  }, []);

  // Mock data for development
  const mockWatchlist: CompanyProfile[] = [
    {
      symbol: 'AAPL',
      name: 'Apple Inc.',
      sector: 'Technology',
      industry: 'Consumer Electronics',
      marketCap: 3000000000000,
      peRatio: 25.5,
      price: 150.25,
      change: 2.15,
      changePercent: 1.45,
      volume: 50000000,
      avgVolume: 45000000,
      high52Week: 180.50,
      low52Week: 120.75,
    },
    {
      symbol: 'MSFT',
      name: 'Microsoft Corporation',
      sector: 'Technology',
      industry: 'Software',
      marketCap: 2800000000000,
      peRatio: 30.2,
      price: 320.80,
      change: -1.20,
      changePercent: -0.37,
      volume: 30000000,
      avgVolume: 28000000,
      high52Week: 350.00,
      low52Week: 250.25,
    },
    {
      symbol: 'GOOGL',
      name: 'Alphabet Inc.',
      sector: 'Technology',
      industry: 'Internet Services',
      marketCap: 1800000000000,
      peRatio: 22.8,
      price: 140.50,
      change: 0.75,
      changePercent: 0.54,
      volume: 25000000,
      avgVolume: 22000000,
      high52Week: 160.00,
      low52Week: 100.50,
    },
  ];

  const mockPortfolios: Portfolio[] = [
    {
      id: '1',
      name: 'Growth Portfolio',
      description: 'Technology and growth stocks',
      holdings: [
        { symbol: 'AAPL', shares: 100, costBasis: 120.00, currentPrice: 150.25, marketValue: 15025, totalReturn: 3025, totalReturnPercent: 25.21, sector: 'Technology', weight: 0.4 },
        { symbol: 'MSFT', shares: 50, costBasis: 280.00, currentPrice: 320.80, marketValue: 16040, totalReturn: 2040, totalReturnPercent: 14.57, sector: 'Technology', weight: 0.35 },
        { symbol: 'GOOGL', shares: 75, costBasis: 110.00, currentPrice: 140.50, marketValue: 10537.5, totalReturn: 2287.5, totalReturnPercent: 27.73, sector: 'Technology', weight: 0.25 },
      ],
      totalValue: 41602.5,
      totalCost: 33250,
      totalReturn: 7352.5,
      totalReturnPercent: 22.11,
      createdAt: '2025-01-01T00:00:00Z',
      updatedAt: '2025-01-27T00:00:00Z',
    },
  ];

  // Use mock data for now
  const displayWatchlist = watchlist.length > 0 ? watchlist : mockWatchlist;
  const displayPortfolios = portfolios.length > 0 ? portfolios : mockPortfolios;

  if (loading) {
    return (
      <div className="flex items-center justify-center h-64">
        <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-600"></div>
      </div>
    );
  }

  return (
    <div className="space-y-8">
      {/* Page Header */}
      <div className="flex justify-between items-center">
        <div>
          <h1 className="text-3xl font-bold text-gray-900">Dashboard</h1>
          <p className="text-gray-600 mt-2">Welcome back! Here's your investment overview.</p>
        </div>
        <div className="flex space-x-3">
          <Link
            href="/dashboard/portfolio/new"
            className="btn-primary px-4 py-2"
          >
            New Portfolio
          </Link>
          <Link
            href="/dashboard/watchlist/add"
            className="btn-outline px-4 py-2"
          >
            Add to Watchlist
          </Link>
        </div>
      </div>

      {/* Portfolio Overview */}
      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        {displayPortfolios.map((portfolio) => (
          <div key={portfolio.id} className="bg-white rounded-lg shadow-sm border border-gray-200 p-6">
            <div className="flex justify-between items-start mb-4">
              <div>
                <h3 className="text-lg font-semibold text-gray-900">{portfolio.name}</h3>
                <p className="text-sm text-gray-500">{portfolio.description}</p>
              </div>
              <Link
                href={`/dashboard/portfolio/${portfolio.id}`}
                className="text-blue-600 hover:text-blue-700 text-sm font-medium"
              >
                View Details →
              </Link>
            </div>

            <div className="space-y-3">
              <div className="flex justify-between">
                <span className="text-gray-600">Total Value</span>
                <span className="font-semibold">${portfolio.totalValue.toLocaleString()}</span>
              </div>
              <div className="flex justify-between">
                <span className="text-gray-600">Total Return</span>
                <span className={`font-semibold ${portfolio.totalReturn >= 0 ? 'text-green-600' : 'text-red-600'}`}>
                  {portfolio.totalReturn >= 0 ? '+' : ''}${portfolio.totalReturn.toLocaleString()} ({portfolio.totalReturnPercent.toFixed(2)}%)
                </span>
              </div>
              <div className="flex justify-between">
                <span className="text-gray-600">Holdings</span>
                <span className="font-semibold">{portfolio.holdings.length}</span>
              </div>
            </div>
          </div>
        ))}
      </div>

      {/* Watchlist */}
      <div className="bg-white rounded-lg shadow-sm border border-gray-200">
        <div className="px-6 py-4 border-b border-gray-200">
          <div className="flex justify-between items-center">
            <h2 className="text-xl font-semibold text-gray-900">Watchlist</h2>
            <Link
              href="/dashboard/watchlist"
              className="text-blue-600 hover:text-blue-700 text-sm font-medium"
            >
              View All →
            </Link>
          </div>
        </div>

        <div className="overflow-x-auto">
          <table className="min-w-full divide-y divide-gray-200">
            <thead className="bg-gray-50">
              <tr>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Symbol</th>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Name</th>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Price</th>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Change</th>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Market Cap</th>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">P/E Ratio</th>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Actions</th>
              </tr>
            </thead>
            <tbody className="bg-white divide-y divide-gray-200">
              {displayWatchlist.map((company) => (
                <tr key={company.symbol} className="hover:bg-gray-50">
                  <td className="px-6 py-4 whitespace-nowrap">
                    <Link
                      href={`/dashboard/companies/${company.symbol}`}
                      className="text-blue-600 hover:text-blue-700 font-medium"
                    >
                      {company.symbol}
                    </Link>
                  </td>
                  <td className="px-6 py-4 whitespace-nowrap">
                    <div>
                      <div className="text-sm font-medium text-gray-900">{company.name}</div>
                      <div className="text-sm text-gray-500">{company.sector}</div>
                    </div>
                  </td>
                  <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-900">
                    ${company.price.toFixed(2)}
                  </td>
                  <td className="px-6 py-4 whitespace-nowrap">
                    <span className={`text-sm font-medium ${company.change >= 0 ? 'text-green-600' : 'text-red-600'}`}>
                      {company.change >= 0 ? '+' : ''}{company.change.toFixed(2)} ({company.changePercent.toFixed(2)}%)
                    </span>
                  </td>
                  <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-900">
                    ${(company.marketCap / 1000000000).toFixed(1)}B
                  </td>
                  <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-900">
                    {company.peRatio.toFixed(1)}
                  </td>
                  <td className="px-6 py-4 whitespace-nowrap text-sm font-medium">
                    <button className="text-blue-600 hover:text-blue-700 mr-3">Buy</button>
                    <button className="text-red-600 hover:text-red-700">Remove</button>
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </div>

      {/* Quick Actions */}
      <div className="bg-white rounded-lg shadow-sm border border-gray-200 p-6">
        <h3 className="text-lg font-semibold text-gray-900 mb-4">Quick Actions</h3>
        <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
          <Link
            href="/dashboard/companies/search"
            className="flex flex-col items-center p-4 border border-gray-200 rounded-lg hover:border-blue-300 hover:bg-blue-50 transition-colors"
          >
            <svg className="w-8 h-8 text-blue-600 mb-2" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M21 21l-6-6m2-5a7 7 0 11-14 0 7 7 0 0114 0z" />
            </svg>
            <span className="text-sm font-medium text-gray-900">Search Companies</span>
          </Link>

          <Link
            href="/dashboard/portfolio/import"
            className="flex flex-col items-center p-4 border border-gray-200 rounded-lg hover:border-blue-300 hover:bg-blue-50 transition-colors"
          >
            <svg className="w-8 h-8 text-blue-600 mb-2" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M7 16a4 4 0 01-.88-7.903A5 5 0 1115.9 6L16 6a5 5 0 011 9.9M9 19l3 3m0 0l3-3m-3 3V10" />
            </svg>
            <span className="text-sm font-medium text-gray-900">Import Portfolio</span>
          </Link>

          <Link
            href="/dashboard/analysis/screening"
            className="flex flex-col items-center p-4 border border-gray-200 rounded-lg hover:border-blue-300 hover:bg-blue-50 transition-colors"
          >
            <svg className="w-8 h-8 text-blue-600 mb-2" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M3 4a1 1 0 011-1h16a1 1 0 011 1v2.586a1 1 0 01-.293.707l-6.414 6.414a1 1 0 00-.293.707V17l-4 4v-6.586a1 1 0 00-.293-.707L3.293 7.207A1 1 0 013 6.5V4z" />
            </svg>
            <span className="text-sm font-medium text-gray-900">Stock Screener</span>
          </Link>

          <Link
            href="/dashboard/reports/performance"
            className="flex flex-col items-center p-4 border border-gray-200 rounded-lg hover:border-blue-300 hover:bg-blue-50 transition-colors"
          >
            <svg className="w-8 h-8 text-blue-600 mb-2" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 17v-2m3 2v-4m3 4v-6m2 10H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z" />
            </svg>
            <span className="text-sm font-medium text-gray-900">Performance Report</span>
          </Link>
        </div>
      </div>
    </div>
  );
}
