'use client';

import { useState, useEffect } from 'react';
import Link from 'next/link';
import { Portfolio, apiClient, useApiClient, useApiCall } from '@/lib/api-client';
import { useApiClient as useApiClientHook } from '@/hooks/useApiClient';

export default function PortfolioPage() {
  const { client, isAuthenticated } = useApiClientHook();
  const [showCreateForm, setShowCreateForm] = useState(false);

  // Load portfolios using FastAPI
  const { data: portfolios, loading, error } = useApiCall(
    () => client.getPortfolios(),
    [isAuthenticated]
  );

  // Mock data for development
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
    {
      id: '2',
      name: 'Dividend Portfolio',
      description: 'High-yield dividend stocks',
      holdings: [
        { symbol: 'JNJ', shares: 200, costBasis: 150.00, currentPrice: 165.50, marketValue: 33100, totalReturn: 3100, totalReturnPercent: 10.33, sector: 'Healthcare', weight: 0.5 },
        { symbol: 'PG', shares: 150, costBasis: 140.00, currentPrice: 155.75, marketValue: 23362.5, totalReturn: 2362.5, totalReturnPercent: 11.25, sector: 'Consumer Staples', weight: 0.35 },
        { symbol: 'KO', shares: 100, costBasis: 50.00, currentPrice: 55.25, marketValue: 5525, totalReturn: 525, totalReturnPercent: 10.5, sector: 'Consumer Staples', weight: 0.15 },
      ],
      totalValue: 61987.5,
      totalCost: 56000,
      totalReturn: 5987.5,
      totalReturnPercent: 10.69,
      createdAt: '2025-01-01T00:00:00Z',
      updatedAt: '2025-01-27T00:00:00Z',
    },
  ];

  // Use real data from API or fallback to empty array
  const displayPortfolios = portfolios || [];

  if (loading) {
    return (
      <div className="flex items-center justify-center h-64">
        <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-600"></div>
      </div>
    );
  }

  return (
    <div className="space-y-6">
      {/* Page Header */}
      <div className="flex justify-between items-center">
        <div>
          <h1 className="text-3xl font-bold text-gray-900">Portfolio Management</h1>
          <p className="text-gray-600 mt-2">Manage your investment portfolios and track performance.</p>
        </div>
        <div className="flex space-x-3">
          <button
            onClick={() => setShowCreateForm(true)}
            className="btn-primary px-4 py-2"
          >
            Create Portfolio
          </button>
          <Link
            href="/dashboard/portfolio/import"
            className="btn-outline px-4 py-2"
          >
            Import Portfolio
          </Link>
        </div>
      </div>

      {/* Portfolio Summary Cards */}
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

            {/* Sector Allocation Chart */}
            <div className="mt-4 pt-4 border-t border-gray-200">
              <h4 className="text-sm font-medium text-gray-900 mb-2">Sector Allocation</h4>
              <div className="space-y-2">
                {portfolio.holdings.reduce((acc, holding) => {
                  const existing = acc.find(item => item.sector === holding.sector);
                  if (existing) {
                    existing.weight += holding.weight;
                  } else {
                    acc.push({ sector: holding.sector, weight: holding.weight });
                  }
                  return acc;
                }, [] as { sector: string; weight: number }[]).map((sector, index) => (
                  <div key={index} className="flex justify-between items-center">
                    <span className="text-xs text-gray-600">{sector.sector}</span>
                    <span className="text-xs font-medium">{(sector.weight * 100).toFixed(1)}%</span>
                  </div>
                ))}
              </div>
            </div>
          </div>
        ))}
      </div>

      {/* Create Portfolio Form */}
      {showCreateForm && (
        <div className="bg-white rounded-lg shadow-sm border border-gray-200 p-6">
          <div className="flex justify-between items-center mb-6">
            <h3 className="text-lg font-semibold text-gray-900">Create New Portfolio</h3>
            <button
              onClick={() => setShowCreateForm(false)}
              className="text-gray-400 hover:text-gray-600"
            >
              <svg className="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M6 18L18 6M6 6l12 12" />
              </svg>
            </button>
          </div>

          <form className="space-y-4">
            <div>
              <label htmlFor="portfolioName" className="block text-sm font-medium text-gray-700 mb-1">
                Portfolio Name
              </label>
              <input
                type="text"
                id="portfolioName"
                name="portfolioName"
                className="w-full px-3 py-2 border border-gray-300 rounded-md focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                placeholder="e.g., Growth Portfolio"
                required
              />
            </div>

            <div>
              <label htmlFor="portfolioDescription" className="block text-sm font-medium text-gray-700 mb-1">
                Description (Optional)
              </label>
              <textarea
                id="portfolioDescription"
                name="portfolioDescription"
                rows={3}
                className="w-full px-3 py-2 border border-gray-300 rounded-md focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                placeholder="Brief description of your investment strategy"
              />
            </div>

            <div className="flex justify-end space-x-3 pt-4">
              <button
                type="button"
                onClick={() => setShowCreateForm(false)}
                className="btn-outline px-4 py-2"
              >
                Cancel
              </button>
              <button
                type="submit"
                className="btn-primary px-4 py-2"
              >
                Create Portfolio
              </button>
            </div>
          </form>
        </div>
      )}

      {/* Portfolio Performance Summary */}
      <div className="bg-white rounded-lg shadow-sm border border-gray-200 p-6">
        <h3 className="text-lg font-semibold text-gray-900 mb-4">Portfolio Performance Summary</h3>

        <div className="grid grid-cols-1 md:grid-cols-4 gap-6">
          <div className="text-center">
            <div className="text-2xl font-bold text-gray-900">
              ${displayPortfolios.reduce((sum, p) => sum + p.totalValue, 0).toLocaleString()}
            </div>
            <div className="text-sm text-gray-500">Total Portfolio Value</div>
          </div>

          <div className="text-center">
            <div className="text-2xl font-bold text-gray-900">
              {displayPortfolios.length}
            </div>
            <div className="text-sm text-gray-500">Active Portfolios</div>
          </div>

          <div className="text-center">
            <div className="text-2xl font-bold text-green-600">
              +${displayPortfolios.reduce((sum, p) => sum + p.totalReturn, 0).toLocaleString()}
            </div>
            <div className="text-sm text-gray-500">Total Unrealized Gain</div>
          </div>

          <div className="text-center">
            <div className="text-2xl font-bold text-green-600">
              +{((displayPortfolios.reduce((sum, p) => sum + p.totalReturn, 0) / displayPortfolios.reduce((sum, p) => sum + p.totalCost, 0)) * 100).toFixed(2)}%
            </div>
            <div className="text-sm text-gray-500">Overall Return</div>
          </div>
        </div>
      </div>

      {/* Quick Actions */}
      <div className="bg-white rounded-lg shadow-sm border border-gray-200 p-6">
        <h3 className="text-lg font-semibold text-gray-900 mb-4">Quick Actions</h3>
        <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
          <Link
            href="/dashboard/portfolio/rebalance"
            className="flex flex-col items-center p-4 border border-gray-200 rounded-lg hover:border-blue-300 hover:bg-blue-50 transition-colors"
          >
            <svg className="w-8 h-8 text-blue-600 mb-2" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M4 4v5h.582m15.356 2A8.001 8.001 0 004.582 9m0 0H9m11 11v-5h-.581m0 0a8.003 8.003 0 01-15.357-2m15.357 2H15" />
            </svg>
            <span className="text-sm font-medium text-gray-900">Rebalance Portfolio</span>
          </Link>

          <Link
            href="/dashboard/portfolio/analysis"
            className="flex flex-col items-center p-4 border border-gray-200 rounded-lg hover:border-blue-300 hover:bg-blue-50 transition-colors"
          >
            <svg className="w-8 h-8 text-blue-600 mb-2" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 19v-6a2 2 0 00-2-2H5a2 2 0 00-2 2v6a2 2 0 002 2h2a2 2 0 002-2zm0 0V9a2 2 0 012-2h2a2 2 0 012 2v10m-6 0a2 2 0 002 2h2a2 2 0 002-2m0 0V5a2 2 0 012-2h2a2 2 0 012 2v14a2 2 0 01-2 2h-2a2 2 0 01-2-2z" />
            </svg>
            <span className="text-sm font-medium text-gray-900">Portfolio Analysis</span>
          </Link>

          <Link
            href="/dashboard/portfolio/export"
            className="flex flex-col items-center p-4 border border-gray-200 rounded-lg hover:border-blue-300 hover:bg-blue-50 transition-colors"
          >
            <svg className="w-8 h-8 text-blue-600 mb-2" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 10v6m0 0l-3-3m3 3l3-3m2 8H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z" />
            </svg>
            <span className="text-sm font-medium text-gray-900">Export Data</span>
          </Link>
        </div>
      </div>
    </div>
  );
}
