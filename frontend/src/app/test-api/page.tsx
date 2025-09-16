'use client';

import { useState, useEffect } from 'react';
import { useApiClient } from '@/hooks/useApiClient';
import { Portfolio } from '@/lib/api-client';

export default function TestApiPage() {
  const { client, isAuthenticated } = useApiClient();
  const [portfolios, setPortfolios] = useState<Portfolio[]>([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [healthStatus, setHealthStatus] = useState<{
    status: string;
    service: string;
    version: string;
    environment: string;
    database: {
      status: string;
      type: string;
    };
  } | null>(null);

  const testApiConnection = async () => {
    try {
      setLoading(true);
      setError(null);

      // Test health endpoint
      const health = await client.healthCheck();
      setHealthStatus(health);

      // Test portfolios endpoint
      const portfoliosData = await client.getPortfolios();
      setPortfolios(portfoliosData);
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Unknown error');
      console.error('API test failed:', err);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    testApiConnection();
  }, []); // eslint-disable-line react-hooks/exhaustive-deps

  return (
    <div className="min-h-screen bg-gray-50 py-8">
      <div className="max-w-4xl mx-auto px-4">
        <h1 className="text-3xl font-bold text-gray-900 mb-8">API Integration Test</h1>

        <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
          {/* API Status */}
          <div className="bg-white rounded-lg shadow p-6">
            <h2 className="text-xl font-semibold mb-4">API Status</h2>
            <div className="space-y-2">
              <div className="flex items-center">
                <span className="w-3 h-3 bg-green-500 rounded-full mr-2"></span>
                <span>API Server: Running</span>
              </div>
              <div className="flex items-center">
                <span className={`w-3 h-3 rounded-full mr-2 ${isAuthenticated ? 'bg-green-500' : 'bg-yellow-500'}`}></span>
                <span>Authentication: {isAuthenticated ? 'Connected' : 'Demo Mode'}</span>
              </div>
              <div className="flex items-center">
                <span className={`w-3 h-3 rounded-full mr-2 ${loading ? 'bg-yellow-500' : 'bg-green-500'}`}></span>
                <span>Loading: {loading ? 'In Progress' : 'Complete'}</span>
              </div>
            </div>
          </div>

          {/* Health Check */}
          <div className="bg-white rounded-lg shadow p-6">
            <h2 className="text-xl font-semibold mb-4">Health Check</h2>
            {healthStatus ? (
              <div className="space-y-2">
                <div><strong>Status:</strong> {healthStatus.status}</div>
                <div><strong>Service:</strong> {healthStatus.service}</div>
                <div><strong>Version:</strong> {healthStatus.version}</div>
                <div><strong>Environment:</strong> {healthStatus.environment}</div>
                <div><strong>Database:</strong> {healthStatus.database?.type} - {healthStatus.database?.status}</div>
              </div>
            ) : (
              <div className="text-gray-500">Loading health status...</div>
            )}
          </div>
        </div>

        {/* Portfolios Data */}
        <div className="mt-8 bg-white rounded-lg shadow p-6">
          <h2 className="text-xl font-semibold mb-4">Portfolios Data</h2>
          {error && (
            <div className="bg-red-50 border border-red-200 rounded-lg p-4 mb-4">
              <div className="text-red-800 font-semibold">Error:</div>
              <div className="text-red-600">{error}</div>
            </div>
          )}

          {loading ? (
            <div className="text-center py-8">
              <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-blue-600 mx-auto"></div>
              <div className="mt-2 text-gray-600">Loading portfolios...</div>
            </div>
          ) : portfolios.length > 0 ? (
            <div className="space-y-4">
              {portfolios.map((portfolio) => (
                <div key={portfolio.id} className="border rounded-lg p-4">
                  <div className="flex justify-between items-start mb-2">
                    <h3 className="text-lg font-semibold">{portfolio.name}</h3>
                    <span className="text-sm text-gray-500">ID: {portfolio.id}</span>
                  </div>
                  <p className="text-gray-600 mb-3">{portfolio.description}</p>
                  <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
                    <div>
                      <div className="text-sm text-gray-500">Total Value</div>
                      <div className="font-semibold">{portfolio.total_value}</div>
                    </div>
                    <div>
                      <div className="text-sm text-gray-500">Total Cost</div>
                      <div className="font-semibold">{portfolio.total_cost}</div>
                    </div>
                    <div>
                      <div className="text-sm text-gray-500">Gain/Loss</div>
                      <div className={`font-semibold ${portfolio.total_gain_loss.startsWith('+') ? 'text-green-600' : 'text-red-600'}`}>
                        {portfolio.total_gain_loss}
                      </div>
                    </div>
                    <div>
                      <div className="text-sm text-gray-500">Holdings</div>
                      <div className="font-semibold">{portfolio.holdings_count}</div>
                    </div>
                  </div>
                </div>
              ))}
            </div>
          ) : (
            <div className="text-center py-8 text-gray-500">
              No portfolios found
            </div>
          )}
        </div>

        {/* Test Button */}
        <div className="mt-8 text-center">
          <button
            onClick={testApiConnection}
            disabled={loading}
            className="bg-blue-600 text-white px-6 py-3 rounded-lg hover:bg-blue-700 disabled:opacity-50"
          >
            {loading ? 'Testing...' : 'Test API Connection'}
          </button>
        </div>
      </div>
    </div>
  );
}
