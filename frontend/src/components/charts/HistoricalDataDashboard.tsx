'use client';

import React, { useState, useEffect } from 'react';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Badge } from '@/components/ui/badge';
import { Tabs, TabsContent, TabsList, TabsTrigger } from '@/components/ui/tabs';
import {
  TrendingUp,
  TrendingDown,
  BarChart3,
  Download,
  RefreshCw,
  Calendar,
  DollarSign,
  Activity
} from 'lucide-react';
import { HistoricalPriceChart } from './HistoricalPriceChart';
import { TechnicalIndicatorsChart } from './TechnicalIndicatorsChart';

interface CompanyInfo {
  symbol: string;
  name: string;
  sector?: string;
  industry?: string;
}

interface HistoricalDataDashboardProps {
  symbol: string;
  companyName?: string;
  className?: string;
}

interface DataQualityMetrics {
  total_records: number;
  missing_dates: number;
  anomalies: number;
  quality_score: number;
  date_range: {
    start: string;
    end: string;
  };
}

export function HistoricalDataDashboard({
  symbol,
  companyName,
  className = ""
}: HistoricalDataDashboardProps) {
  const [companyInfo, setCompanyInfo] = useState<CompanyInfo | null>(null);
  const [dataQuality, setDataQuality] = useState<DataQualityMetrics | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [activeTab, setActiveTab] = useState('price');

  useEffect(() => {
    fetchCompanyInfo();
    fetchDataQuality();
  }, [symbol]);

  const fetchCompanyInfo = async () => {
    try {
      const response = await fetch(`/api/v1/companies/${symbol}`);
      if (response.ok) {
        const data = await response.json();
        setCompanyInfo(data);
      }
    } catch (err) {
      console.error('Error fetching company info:', err);
    }
  };

  const fetchDataQuality = async () => {
    try {
      setLoading(true);
      setError(null);

      const response = await fetch(
        `/api/v1/historical-data/companies/${symbol}/data-quality`
      );

      if (!response.ok) {
        throw new Error(`Failed to fetch data quality: ${response.statusText}`);
      }

      const data = await response.json();
      setDataQuality(data.quality_metrics);
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to fetch data quality');
      console.error('Error fetching data quality:', err);
    } finally {
      setLoading(false);
    }
  };

  const collectHistoricalData = async () => {
    try {
      setLoading(true);
      const response = await fetch(
        `/api/v1/historical-data/companies/${symbol}/collect-data?years=5`,
        { method: 'POST' }
      );

      if (!response.ok) {
        throw new Error(`Failed to collect data: ${response.statusText}`);
      }

      const data = await response.json();
      console.log('Data collection result:', data);

      // Refresh data quality after collection
      await fetchDataQuality();
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to collect historical data');
      console.error('Error collecting historical data:', err);
    } finally {
      setLoading(false);
    }
  };

  const getQualityScoreColor = (score: number) => {
    if (score >= 0.9) return 'text-green-600';
    if (score >= 0.7) return 'text-yellow-600';
    return 'text-red-600';
  };

  const getQualityScoreBadge = (score: number) => {
    if (score >= 0.9) return 'default';
    if (score >= 0.7) return 'secondary';
    return 'destructive';
  };

  if (loading && !dataQuality) {
    return (
      <Card className={className}>
        <CardHeader>
          <CardTitle className="flex items-center gap-2">
            <RefreshCw className="h-4 w-4 animate-spin" />
            Loading Historical Data Dashboard for {symbol}
          </CardTitle>
        </CardHeader>
        <CardContent>
          <div className="h-96 flex items-center justify-center">
            <div className="text-center">
              <RefreshCw className="h-8 w-8 animate-spin mx-auto mb-2" />
              <p className="text-muted-foreground">Loading dashboard...</p>
            </div>
          </div>
        </CardContent>
      </Card>
    );
  }

  return (
    <div className={className}>
      {/* Header */}
      <div className="mb-6">
        <div className="flex items-center justify-between">
          <div>
            <h1 className="text-3xl font-bold">
              {symbol} - {companyName || companyInfo?.name || 'Historical Data'}
            </h1>
            {companyInfo && (
              <div className="flex items-center gap-4 mt-2 text-sm text-muted-foreground">
                {companyInfo.sector && (
                  <span>Sector: {companyInfo.sector}</span>
                )}
                {companyInfo.industry && (
                  <span>Industry: {companyInfo.industry}</span>
                )}
              </div>
            )}
          </div>
          <div className="flex items-center gap-2">
            <Button
              onClick={collectHistoricalData}
              disabled={loading}
              variant="outline"
            >
              {loading ? (
                <RefreshCw className="h-4 w-4 mr-2 animate-spin" />
              ) : (
                <Download className="h-4 w-4 mr-2" />
              )}
              Collect Data
            </Button>
            <Button
              onClick={fetchDataQuality}
              disabled={loading}
              variant="outline"
            >
              <RefreshCw className="h-4 w-4" />
            </Button>
          </div>
        </div>
      </div>

      {/* Data Quality Overview */}
      {dataQuality && (
        <div className="grid grid-cols-1 md:grid-cols-4 gap-4 mb-6">
          <Card>
            <CardHeader className="pb-2">
              <CardTitle className="text-sm font-medium flex items-center gap-2">
                <Activity className="h-4 w-4" />
                Data Quality
              </CardTitle>
            </CardHeader>
            <CardContent>
              <div className="flex items-center gap-2">
                <span className="text-2xl font-bold">
                  {(dataQuality.quality_score * 100).toFixed(1)}%
                </span>
                <Badge variant={getQualityScoreBadge(dataQuality.quality_score)}>
                  {dataQuality.quality_score >= 0.9 ? 'Excellent' :
                   dataQuality.quality_score >= 0.7 ? 'Good' : 'Poor'}
                </Badge>
              </div>
            </CardContent>
          </Card>

          <Card>
            <CardHeader className="pb-2">
              <CardTitle className="text-sm font-medium flex items-center gap-2">
                <BarChart3 className="h-4 w-4" />
                Total Records
              </CardTitle>
            </CardHeader>
            <CardContent>
              <div className="text-2xl font-bold">
                {dataQuality.total_records.toLocaleString()}
              </div>
            </CardContent>
          </Card>

          <Card>
            <CardHeader className="pb-2">
              <CardTitle className="text-sm font-medium flex items-center gap-2">
                <Calendar className="h-4 w-4" />
                Date Range
              </CardTitle>
            </CardHeader>
            <CardContent>
              <div className="text-sm">
                <div>{new Date(dataQuality.date_range.start).toLocaleDateString()}</div>
                <div className="text-muted-foreground">to</div>
                <div>{new Date(dataQuality.date_range.end).toLocaleDateString()}</div>
              </div>
            </CardContent>
          </Card>

          <Card>
            <CardHeader className="pb-2">
              <CardTitle className="text-sm font-medium flex items-center gap-2">
                <TrendingDown className="h-4 w-4" />
                Issues
              </CardTitle>
            </CardHeader>
            <CardContent>
              <div className="text-2xl font-bold">
                {dataQuality.missing_dates + dataQuality.anomalies}
              </div>
              <div className="text-xs text-muted-foreground">
                Missing: {dataQuality.missing_dates} | Anomalies: {dataQuality.anomalies}
              </div>
            </CardContent>
          </Card>
        </div>
      )}

      {/* Error Display */}
      {error && (
        <Card className="mb-6 border-red-200 bg-red-50">
          <CardContent className="pt-6">
            <div className="flex items-center gap-2 text-red-600">
              <TrendingDown className="h-4 w-4" />
              <span className="font-medium">Error:</span>
              <span>{error}</span>
            </div>
          </CardContent>
        </Card>
      )}

      {/* Main Content Tabs */}
      <Tabs value={activeTab} onValueChange={setActiveTab} className="w-full">
        <TabsList className="grid w-full grid-cols-2">
          <TabsTrigger value="price" className="flex items-center gap-2">
            <TrendingUp className="h-4 w-4" />
            Price Charts
          </TabsTrigger>
          <TabsTrigger value="indicators" className="flex items-center gap-2">
            <BarChart3 className="h-4 w-4" />
            Technical Indicators
          </TabsTrigger>
        </TabsList>

        <TabsContent value="price" className="mt-6">
          <HistoricalPriceChart
            symbol={symbol}
            companyName={companyName || companyInfo?.name}
            onDataLoad={() => {
              // Refresh data quality when new data is loaded
              fetchDataQuality();
            }}
          />
        </TabsContent>

        <TabsContent value="indicators" className="mt-6">
          <TechnicalIndicatorsChart
            symbol={symbol}
            companyName={companyName || companyInfo?.name}
          />
        </TabsContent>
      </Tabs>
    </div>
  );
}
