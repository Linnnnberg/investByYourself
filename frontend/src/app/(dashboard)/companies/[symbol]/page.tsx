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
        setLoading(true);
        const [profileResponse, sectorComparisonResponse] = await Promise.all([
          apiClient.getCompanyProfile(symbol),
          apiClient.getSectorComparison(symbol),
        ]);

        console.log('Profile response:', profileResponse);
        if (profileResponse.success) {
          // Convert string values to numbers for financial metrics
          const companyData = profileResponse.data;
          if (companyData.financial_metrics) {
            const metrics = companyData.financial_metrics;
            Object.keys(metrics).forEach(key => {
              if (metrics[key] && typeof metrics[key] === 'string') {
                metrics[key] = parseFloat(metrics[key]);
              }
            });
          }
          setCompany(companyData);
        } else {
          console.error('Failed to fetch company profile:', profileResponse.error);
        }

        if (sectorComparisonResponse.success) {
          // Store sector comparison data for later use
          console.log('Sector comparison data:', sectorComparisonResponse.data);
        }

        // For now, use empty array for financials since we're using metrics instead
        setFinancials([]);
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

  // Fallback data for development
  const fallbackCompany: CompanyProfile = {
    symbol: symbol || 'N/A',
    name: 'Loading...',
    sector: 'Unknown',
    industry: 'Unknown',
    market_cap: 0,
    pe_ratio: 0,
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
  const displayCompany = company || fallbackCompany;
  const displayFinancials = financials.length > 0 ? financials : [];

  if (loading) {
    return (
      <div className="flex items-center justify-center h-64">
        <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-600"></div>
      </div>
    );
  }

  return (
    <div className="space-y-4">
      {/* Compact Company Header */}
      <div className="bg-white rounded-lg shadow-sm border border-gray-200 p-4">
        <div className="flex justify-between items-center">
          <div className="flex items-center space-x-4">
            <div className="w-12 h-12 bg-blue-100 rounded-lg flex items-center justify-center">
              <span className="text-xl font-bold text-blue-600">{displayCompany.symbol}</span>
            </div>
            <div>
              <h1 className="text-2xl font-bold text-gray-900">{displayCompany.name}</h1>
              <p className="text-gray-600 text-sm">{displayCompany.sector} • {displayCompany.industry}</p>
            </div>
          </div>
          <div className="text-right">
            <div className="text-2xl font-bold text-gray-900">
              {displayCompany.financial_metrics?.pe_ratio ? `P/E: ${displayCompany.financial_metrics.pe_ratio.toFixed(1)}` : 'N/A'}
            </div>
            <div className="text-sm text-gray-500">
              {displayCompany.market_cap ? `Market Cap: $${(displayCompany.market_cap / 1000000000).toFixed(1)}B` : 'N/A'}
            </div>
          </div>
        </div>
      </div>

      {/* Main Content Grid */}
      <div className="grid grid-cols-1 lg:grid-cols-3 gap-4">
        {/* Left Column - Company Info & Description */}
        <div className="lg:col-span-1 space-y-4">
          {/* Company Information */}
          <div className="bg-white rounded-lg shadow-sm border border-gray-200 p-4">
            <h3 className="text-lg font-semibold text-gray-900 mb-3">Company Information</h3>
            <div className="space-y-2 text-sm">
              <div className="flex justify-between">
                <span className="text-gray-500">Symbol</span>
                <span className="font-medium">{displayCompany.symbol}</span>
              </div>
              <div className="flex justify-between">
                <span className="text-gray-500">Exchange</span>
                <span className="font-medium">{displayCompany.exchange || 'N/A'}</span>
              </div>
              <div className="flex justify-between">
                <span className="text-gray-500">Country</span>
                <span className="font-medium">{displayCompany.country || 'N/A'}</span>
              </div>
              <div className="flex justify-between">
                <span className="text-gray-500">CEO</span>
                <span className="font-medium">{displayCompany.ceo || 'N/A'}</span>
              </div>
              <div className="flex justify-between">
                <span className="text-gray-500">Founded</span>
                <span className="font-medium">{displayCompany.founded_year || 'N/A'}</span>
              </div>
            </div>
          </div>

          {/* Company Description */}
          <div className="bg-white rounded-lg shadow-sm border border-gray-200 p-4">
            <h3 className="text-lg font-semibold text-gray-900 mb-3">Description</h3>
            <p className="text-gray-600 text-sm leading-relaxed">
              {displayCompany.description || `${displayCompany.name} is a company in the ${displayCompany.industry?.toLowerCase() || 'unknown'} industry. The company operates in the ${displayCompany.sector || 'unknown'} sector.`}
            </p>
          </div>
        </div>

        {/* Center Column - Financial Ratios */}
        <div className="lg:col-span-1 space-y-4">
          <div className="bg-white rounded-lg shadow-sm border border-gray-200 p-4">
            <h3 className="text-lg font-semibold text-gray-900 mb-3">Financial Ratios</h3>
            <div className="grid grid-cols-2 gap-4">
              <div className="text-center p-3 bg-gray-50 rounded-lg">
                <div className="text-sm text-gray-500">P/E Ratio</div>
                <div className="text-xl font-bold text-gray-900">
                  {displayCompany.financial_metrics?.pe_ratio?.toFixed(1) || 'N/A'}
                </div>
              </div>
              <div className="text-center p-3 bg-gray-50 rounded-lg">
                <div className="text-sm text-gray-500">P/B Ratio</div>
                <div className="text-xl font-bold text-gray-900">
                  {displayCompany.financial_metrics?.price_to_book?.toFixed(1) || 'N/A'}
                </div>
              </div>
              <div className="text-center p-3 bg-gray-50 rounded-lg">
                <div className="text-sm text-gray-500">ROE</div>
                <div className="text-xl font-bold text-gray-900">
                  {displayCompany.financial_metrics?.roe ? `${displayCompany.financial_metrics.roe.toFixed(1)}%` : 'N/A'}
                </div>
              </div>
              <div className="text-center p-3 bg-gray-50 rounded-lg">
                <div className="text-sm text-gray-500">Debt/Equity</div>
                <div className="text-xl font-bold text-gray-900">
                  {displayCompany.financial_metrics?.debt_to_equity?.toFixed(2) || 'N/A'}
                </div>
              </div>
              <div className="text-center p-3 bg-gray-50 rounded-lg">
                <div className="text-sm text-gray-500">Current Ratio</div>
                <div className="text-xl font-bold text-gray-900">
                  {displayCompany.financial_metrics?.current_ratio?.toFixed(2) || 'N/A'}
                </div>
              </div>
              <div className="text-center p-3 bg-gray-50 rounded-lg">
                <div className="text-sm text-gray-500">Net Margin</div>
                <div className="text-xl font-bold text-gray-900">
                  {displayCompany.financial_metrics?.net_margin ? `${displayCompany.financial_metrics.net_margin.toFixed(1)}%` : 'N/A'}
                </div>
              </div>
            </div>
          </div>
        </div>

        {/* Right Column - Chart */}
        <div className="lg:col-span-1">
          <div className="bg-white rounded-lg shadow-sm border border-gray-200 p-4 h-full">
            <h3 className="text-lg font-semibold text-gray-900 mb-3">Price Chart</h3>
            <div className="bg-gray-100 rounded-lg h-64 flex items-center justify-center">
              <div className="text-center">
                <svg className="w-12 h-12 text-gray-400 mx-auto mb-2" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 19v-6a2 2 0 00-2-2H5a2 2 0 00-2 2v6a2 2 0 002 2h2a2 2 0 002-2zm0 0V9a2 2 0 012-2h2a2 2 0 012 2v10m-6 0a2 2 0 002 2h2a2 2 0 002-2m0 0V5a2 2 0 012-2h2a2 2 0 012 2v14a2 2 0 01-2 2h-2a2 2 0 01-2-2z" />
                </svg>
                <p className="text-gray-500 text-sm">TradingView Chart</p>
                <p className="text-xs text-gray-400">Interactive price chart</p>
              </div>
            </div>
          </div>
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
        <Link href="/portfolio/new" className="btn-outline px-6 py-3">
          Add to Portfolio
        </Link>
      </div>
    </div>
  );
}
