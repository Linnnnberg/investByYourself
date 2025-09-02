'use client';

import { useState, useEffect } from 'react';
import { useParams } from 'next/navigation';
import Link from 'next/link';
import { CompanyProfile, FinancialStatement, apiClient } from '@/lib/api';

export default function CompanyPage() {
  const params = useParams();
  const symbol = params.symbol as string;

  const [company, setCompany] = useState<CompanyProfile | null>(null);
  const [financials, setFinancials] = useState<FinancialStatement[]>([]);
  const [loading, setLoading] = useState(true);
  const [activeTab, setActiveTab] = useState<'overview' | 'financials' | 'ratios' | 'charts'>('overview');

  useEffect(() => {
    const fetchCompanyData = async () => {
      try {
        const [profileResponse, financialsResponse] = await Promise.all([
          apiClient.getCompanyProfile(symbol),
          apiClient.getCompanyFinancials(symbol, 'income'),
        ]);

        if (profileResponse.success) {
          setCompany(profileResponse.data);
        }

        if (financialsResponse.success) {
          setFinancials(financialsResponse.data || []);
        }
      } catch (error) {
        console.error('Failed to fetch company data:', error);
      } finally {
        setLoading(false);
      }
    };

    if (symbol) {
      fetchCompanyData();
    }
  }, [symbol]);

  // Mock data for development
  const mockCompany: CompanyProfile = {
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
  };

  const mockFinancials: FinancialStatement[] = [
    {
      period: '2024 Q4',
      revenue: 119575000000,
      grossProfit: 45687000000,
      operatingIncome: 33916000000,
      netIncome: 33916000000,
      totalAssets: 352755000000,
      totalLiabilities: 287912000000,
      totalEquity: 64843000000,
      operatingCashFlow: 39768000000,
      investingCashFlow: -10704000000,
      financingCashFlow: -11088000000,
    },
    {
      period: '2024 Q3',
      revenue: 117154000000,
      grossProfit: 44713000000,
      operatingIncome: 32322000000,
      netIncome: 32322000000,
      totalAssets: 340618000000,
      totalLiabilities: 279013000000,
      totalEquity: 61605000000,
      operatingCashFlow: 38868000000,
      investingCashFlow: -10204000000,
      financingCashFlow: -10888000000,
    },
  ];

  // Use mock data for now
  const displayCompany = company || mockCompany;
  const displayFinancials = financials.length > 0 ? financials : mockFinancials;

  if (loading) {
    return (
      <div className="flex items-center justify-center h-64">
        <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-600"></div>
      </div>
    );
  }

  return (
    <div className="space-y-6">
      {/* Company Header */}
      <div className="bg-white rounded-lg shadow-sm border border-gray-200 p-6">
        <div className="flex justify-between items-start">
          <div>
            <div className="flex items-center space-x-4">
              <div className="w-16 h-16 bg-blue-100 rounded-lg flex items-center justify-center">
                <span className="text-2xl font-bold text-blue-600">{displayCompany.symbol}</span>
              </div>
              <div>
                <h1 className="text-3xl font-bold text-gray-900">{displayCompany.name}</h1>
                <p className="text-gray-600">{displayCompany.sector} • {displayCompany.industry}</p>
              </div>
            </div>
          </div>

          <div className="text-right">
            <div className="text-3xl font-bold text-gray-900">${displayCompany.price.toFixed(2)}</div>
            <div className={`text-lg font-medium ${displayCompany.change >= 0 ? 'text-green-600' : 'text-red-600'}`}>
              {displayCompany.change >= 0 ? '+' : ''}{displayCompany.change.toFixed(2)} ({displayCompany.changePercent.toFixed(2)}%)
            </div>
            <div className="text-sm text-gray-500">Volume: {displayCompany.volume.toLocaleString()}</div>
          </div>
        </div>

        {/* Key Metrics */}
        <div className="grid grid-cols-2 md:grid-cols-4 gap-6 mt-8 pt-6 border-t border-gray-200">
          <div>
            <div className="text-sm text-gray-500">Market Cap</div>
            <div className="text-lg font-semibold">${(displayCompany.marketCap / 1000000000).toFixed(1)}B</div>
          </div>
          <div>
            <div className="text-sm text-gray-500">P/E Ratio</div>
            <div className="text-lg font-semibold">{displayCompany.peRatio.toFixed(1)}</div>
          </div>
          <div>
            <div className="text-sm text-gray-500">52W High</div>
            <div className="text-lg font-semibold">${displayCompany.high52Week.toFixed(2)}</div>
          </div>
          <div>
            <div className="text-sm text-gray-500">52W Low</div>
            <div className="text-lg font-semibold">${displayCompany.low52Week.toFixed(2)}</div>
          </div>
        </div>
      </div>

      {/* Navigation Tabs */}
      <div className="bg-white rounded-lg shadow-sm border border-gray-200">
        <div className="border-b border-gray-200">
          <nav className="flex space-x-8 px-6">
            {[
              { id: 'overview', label: 'Overview' },
              { id: 'financials', label: 'Financials' },
              { id: 'ratios', label: 'Ratios' },
              { id: 'charts', label: 'Charts' },
            ].map((tab) => (
              <button
                key={tab.id}
                onClick={() => setActiveTab(tab.id as any)}
                className={`py-4 px-1 border-b-2 font-medium text-sm ${
                  activeTab === tab.id
                    ? 'border-blue-500 text-blue-600'
                    : 'border-transparent text-gray-500 hover:text-gray-700 hover:border-gray-300'
                }`}
              >
                {tab.label}
              </button>
            ))}
          </nav>
        </div>

        <div className="p-6">
          {/* Overview Tab */}
          {activeTab === 'overview' && (
            <div className="space-y-6">
              <div>
                <h3 className="text-lg font-semibold text-gray-900 mb-4">Company Description</h3>
                <p className="text-gray-600 leading-relaxed">
                  {displayCompany.name} is a leading technology company in the {displayCompany.industry.toLowerCase()} industry.
                  The company operates in the {displayCompany.sector} sector and has established itself as a market leader
                  with innovative products and services.
                </p>
              </div>

              <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
                <div>
                  <h4 className="font-medium text-gray-900 mb-3">Trading Information</h4>
                  <div className="space-y-2 text-sm">
                    <div className="flex justify-between">
                      <span className="text-gray-500">Current Price</span>
                      <span className="font-medium">${displayCompany.price.toFixed(2)}</span>
                    </div>
                    <div className="flex justify-between">
                      <span className="text-gray-500">Day Change</span>
                      <span className={`font-medium ${displayCompany.change >= 0 ? 'text-green-600' : 'text-red-600'}`}>
                        {displayCompany.change >= 0 ? '+' : ''}{displayCompany.change.toFixed(2)} ({displayCompany.changePercent.toFixed(2)}%)
                      </span>
                    </div>
                    <div className="flex justify-between">
                      <span className="text-gray-500">Volume</span>
                      <span className="font-medium">{displayCompany.volume.toLocaleString()}</span>
                    </div>
                    <div className="flex justify-between">
                      <span className="text-gray-500">Avg Volume</span>
                      <span className="font-medium">{displayCompany.avgVolume.toLocaleString()}</span>
                    </div>
                  </div>
                </div>

                <div>
                  <h4 className="font-medium text-gray-900 mb-3">Valuation Metrics</h4>
                  <div className="space-y-2 text-sm">
                    <div className="flex justify-between">
                      <span className="text-gray-500">Market Cap</span>
                      <span className="font-medium">${(displayCompany.marketCap / 1000000000).toFixed(1)}B</span>
                    </div>
                    <div className="flex justify-between">
                      <span className="text-gray-500">P/E Ratio</span>
                      <span className="font-medium">{displayCompany.peRatio.toFixed(1)}</span>
                    </div>
                    <div className="flex justify-between">
                      <span className="text-gray-500">52W High</span>
                      <span className="font-medium">${displayCompany.high52Week.toFixed(2)}</span>
                    </div>
                    <div className="flex justify-between">
                      <span className="text-gray-500">52W Low</span>
                      <span className="font-medium">${displayCompany.low52Week.toFixed(2)}</span>
                    </div>
                  </div>
                </div>
              </div>
            </div>
          )}

          {/* Financials Tab */}
          {activeTab === 'financials' && (
            <div className="space-y-6">
              <div className="flex justify-between items-center">
                <h3 className="text-lg font-semibold text-gray-900">Financial Statements</h3>
                <div className="flex space-x-2">
                  <button className="px-3 py-1 text-sm border border-gray-300 rounded-md hover:bg-gray-50">Income Statement</button>
                  <button className="px-3 py-1 text-sm border border-gray-300 rounded-md hover:bg-gray-50">Balance Sheet</button>
                  <button className="px-3 py-1 text-sm border border-gray-300 rounded-md hover:bg-gray-50">Cash Flow</button>
                </div>
              </div>

              <div className="overflow-x-auto">
                <table className="min-w-full divide-y divide-gray-200">
                  <thead className="bg-gray-50">
                    <tr>
                      <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Period</th>
                      <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Revenue</th>
                      <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Gross Profit</th>
                      <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Operating Income</th>
                      <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Net Income</th>
                    </tr>
                  </thead>
                  <tbody className="bg-white divide-y divide-gray-200">
                    {displayFinancials.map((financial, index) => (
                      <tr key={index} className="hover:bg-gray-50">
                        <td className="px-6 py-4 whitespace-nowrap text-sm font-medium text-gray-900">
                          {financial.period}
                        </td>
                        <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-900">
                          ${(financial.revenue / 1000000000).toFixed(1)}B
                        </td>
                        <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-900">
                          ${(financial.grossProfit / 1000000000).toFixed(1)}B
                        </td>
                        <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-900">
                          ${(financial.operatingIncome / 1000000000).toFixed(1)}B
                        </td>
                        <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-900">
                          ${(financial.netIncome / 1000000000).toFixed(1)}B
                        </td>
                      </tr>
                    ))}
                  </tbody>
                </table>
              </div>
            </div>
          )}

          {/* Ratios Tab */}
          {activeTab === 'ratios' && (
            <div className="space-y-6">
              <h3 className="text-lg font-semibold text-gray-900">Financial Ratios</h3>
              <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
                <div className="bg-gray-50 rounded-lg p-4">
                  <div className="text-sm text-gray-500">Price-to-Earnings (P/E)</div>
                  <div className="text-2xl font-bold text-gray-900">{displayCompany.peRatio.toFixed(1)}</div>
                  <div className="text-xs text-gray-500 mt-1">Industry Avg: 22.5</div>
                </div>

                <div className="bg-gray-50 rounded-lg p-4">
                  <div className="text-sm text-gray-500">Price-to-Book (P/B)</div>
                  <div className="text-2xl font-bold text-gray-900">15.2</div>
                  <div className="text-xs text-gray-500 mt-1">Industry Avg: 12.8</div>
                </div>

                <div className="bg-gray-50 rounded-lg p-4">
                  <div className="text-sm text-gray-500">Debt-to-Equity</div>
                  <div className="text-2xl font-bold text-gray-900">0.45</div>
                  <div className="text-xs text-gray-500 mt-1">Industry Avg: 0.62</div>
                </div>

                <div className="bg-gray-50 rounded-lg p-4">
                  <div className="text-sm text-gray-500">Return on Equity</div>
                  <div className="text-2xl font-bold text-gray-900">28.5%</div>
                  <div className="text-xs text-gray-500 mt-1">Industry Avg: 18.2%</div>
                </div>

                <div className="bg-gray-50 rounded-lg p-4">
                  <div className="text-sm text-gray-500">Profit Margin</div>
                  <div className="text-2xl font-bold text-gray-900">25.8%</div>
                  <div className="text-xs text-gray-500 mt-1">Industry Avg: 15.6%</div>
                </div>

                <div className="bg-gray-50 rounded-lg p-4">
                  <div className="text-sm text-gray-500">Current Ratio</div>
                  <div className="text-2xl font-bold text-gray-900">1.85</div>
                  <div className="text-xs text-gray-500 mt-1">Industry Avg: 1.45</div>
                </div>
              </div>
            </div>
          )}

          {/* Charts Tab */}
          {activeTab === 'charts' && (
            <div className="space-y-6">
              <h3 className="text-lg font-semibold text-gray-900">Price Charts & Analysis</h3>
              <div className="bg-gray-100 rounded-lg h-96 flex items-center justify-center">
                <div className="text-center">
                  <svg className="w-16 h-16 text-gray-400 mx-auto mb-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 19v-6a2 2 0 00-2-2H5a2 2 0 00-2 2v6a2 2 0 002 2h2a2 2 0 002-2zm0 0V9a2 2 0 012-2h2a2 2 0 012 2v10m-6 0a2 2 0 002 2h2a2 2 0 002-2m0 0V5a2 2 0 012-2h2a2 2 0 012 2v14a2 2 0 01-2 2h-2a2 2 0 01-2-2z" />
                  </svg>
                  <p className="text-gray-500">TradingView charts will be integrated here</p>
                  <p className="text-sm text-gray-400">Interactive price charts, technical indicators, and analysis tools</p>
                </div>
              </div>
            </div>
          )}
        </div>
      </div>

      {/* Action Buttons */}
      <div className="flex justify-center space-x-4">
        <button className="btn-primary px-6 py-3">
          Add to Watchlist
        </button>
        <button className="btn-outline px-6 py-3">
          Buy {displayCompany.symbol}
        </button>
        <Link href="/dashboard/portfolio/new" className="btn-outline px-6 py-3">
          Add to Portfolio
        </Link>
      </div>
    </div>
  );
}
