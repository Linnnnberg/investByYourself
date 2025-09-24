'use client';

import React, { useEffect, useState } from 'react';
import {
  LineChart,
  Line,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  ResponsiveContainer,
  Legend,
  ReferenceLine
} from 'recharts';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Badge } from '@/components/ui/badge';
import { Download, RefreshCw, TrendingUp, TrendingDown } from 'lucide-react';

interface HistoricalPriceData {
  date: string;
  open: number;
  high: number;
  low: number;
  close: number;
  volume: number;
  adjusted_close: number;
  [key: string]: any; // For technical indicators
}

interface HistoricalPriceChartProps {
  symbol: string;
  companyName?: string;
  onDataLoad?: (data: HistoricalPriceData[]) => void;
  className?: string;
}

export function HistoricalPriceChart({
  symbol,
  companyName,
  onDataLoad,
  className = ""
}: HistoricalPriceChartProps) {
  const [priceData, setPriceData] = useState<HistoricalPriceData[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [showIndicators, setShowIndicators] = useState(false);
  const [timeRange, setTimeRange] = useState<'1M' | '3M' | '6M' | '1Y' | '5Y'>('1Y');

  useEffect(() => {
    fetchHistoricalData();
  }, [symbol, timeRange]);

  const fetchHistoricalData = async () => {
    try {
      setLoading(true);
      setError(null);

      const response = await fetch(
        `/api/v1/historical-data/companies/${symbol}/chart-data?include_indicators=true&limit=1000`
      );

      if (!response.ok) {
        throw new Error(`Failed to fetch data: ${response.statusText}`);
      }

      const data = await response.json();
      setPriceData(data.price_data || []);

      if (onDataLoad) {
        onDataLoad(data.price_data || []);
      }
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to fetch historical data');
      console.error('Error fetching historical data:', err);
    } finally {
      setLoading(false);
    }
  };

  const calculatePriceChange = () => {
    if (priceData.length < 2) return { change: 0, percentage: 0, isPositive: true };

    const latest = priceData[0].close;
    const previous = priceData[1].close;
    const change = latest - previous;
    const percentage = (change / previous) * 100;

    return {
      change: change,
      percentage: percentage,
      isPositive: change >= 0
    };
  };

  const formatTooltipValue = (value: number, name: string) => {
    if (name.includes('volume')) {
      return [value.toLocaleString(), name];
    }
    return [`$${value.toFixed(2)}`, name];
  };

  const formatXAxisLabel = (tickItem: string) => {
    const date = new Date(tickItem);
    return date.toLocaleDateString('en-US', {
      month: 'short',
      day: 'numeric'
    });
  };

  const exportData = () => {
    const csvContent = [
      ['Date', 'Open', 'High', 'Low', 'Close', 'Volume', 'Adjusted Close'].join(','),
      ...priceData.map(d => [
        d.date,
        d.open,
        d.high,
        d.low,
        d.close,
        d.volume,
        d.adjusted_close
      ].join(','))
    ].join('\n');

    const blob = new Blob([csvContent], { type: 'text/csv' });
    const url = window.URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = url;
    a.download = `${symbol}_historical_data.csv`;
    a.click();
    window.URL.revokeObjectURL(url);
  };

  const priceChange = calculatePriceChange();

  if (loading) {
    return (
      <Card className={className}>
        <CardHeader>
          <CardTitle className="flex items-center gap-2">
            <RefreshCw className="h-4 w-4 animate-spin" />
            Loading Historical Data for {symbol}
          </CardTitle>
        </CardHeader>
        <CardContent>
          <div className="h-96 flex items-center justify-center">
            <div className="text-center">
              <RefreshCw className="h-8 w-8 animate-spin mx-auto mb-2" />
              <p className="text-muted-foreground">Loading price data...</p>
            </div>
          </div>
        </CardContent>
      </Card>
    );
  }

  if (error) {
    return (
      <Card className={className}>
        <CardHeader>
          <CardTitle>Historical Data - {symbol}</CardTitle>
        </CardHeader>
        <CardContent>
          <div className="h-96 flex items-center justify-center">
            <div className="text-center">
              <p className="text-red-500 mb-4">{error}</p>
              <Button onClick={fetchHistoricalData} variant="outline">
                <RefreshCw className="h-4 w-4 mr-2" />
                Retry
              </Button>
            </div>
          </div>
        </CardContent>
      </Card>
    );
  }

  if (priceData.length === 0) {
    return (
      <Card className={className}>
        <CardHeader>
          <CardTitle>Historical Data - {symbol}</CardTitle>
        </CardHeader>
        <CardContent>
          <div className="h-96 flex items-center justify-center">
            <div className="text-center">
              <p className="text-muted-foreground mb-4">No historical data available</p>
              <Button onClick={fetchHistoricalData} variant="outline">
                <RefreshCw className="h-4 w-4 mr-2" />
                Refresh
              </Button>
            </div>
          </div>
        </CardContent>
      </Card>
    );
  }

  return (
    <Card className={className}>
      <CardHeader>
        <div className="flex items-center justify-between">
          <div>
            <CardTitle className="flex items-center gap-2">
              {symbol} - {companyName || 'Historical Price Data'}
              <Badge variant={priceChange.isPositive ? "default" : "destructive"}>
                {priceChange.isPositive ? (
                  <TrendingUp className="h-3 w-3 mr-1" />
                ) : (
                  <TrendingDown className="h-3 w-3 mr-1" />
                )}
                {priceChange.percentage.toFixed(2)}%
              </Badge>
            </CardTitle>
            <p className="text-sm text-muted-foreground">
              Latest: ${priceData[0]?.close.toFixed(2)}
              {priceChange.change !== 0 && (
                <span className={`ml-2 ${priceChange.isPositive ? 'text-green-600' : 'text-red-600'}`}>
                  {priceChange.isPositive ? '+' : ''}${priceChange.change.toFixed(2)}
                </span>
              )}
            </p>
          </div>
          <div className="flex items-center gap-2">
            <Button
              variant="outline"
              size="sm"
              onClick={() => setShowIndicators(!showIndicators)}
            >
              {showIndicators ? 'Hide' : 'Show'} Indicators
            </Button>
            <Button
              variant="outline"
              size="sm"
              onClick={exportData}
            >
              <Download className="h-4 w-4 mr-2" />
              Export
            </Button>
            <Button
              variant="outline"
              size="sm"
              onClick={fetchHistoricalData}
            >
              <RefreshCw className="h-4 w-4" />
            </Button>
          </div>
        </div>
      </CardHeader>
      <CardContent>
        <div className="h-96 w-full">
          <ResponsiveContainer width="100%" height="100%">
            <LineChart data={priceData}>
              <CartesianGrid strokeDasharray="3 3" stroke="#f0f0f0" />
              <XAxis
                dataKey="date"
                tickFormatter={formatXAxisLabel}
                stroke="#666"
                fontSize={12}
              />
              <YAxis
                domain={['dataMin - 5', 'dataMax + 5']}
                stroke="#666"
                fontSize={12}
                tickFormatter={(value) => `$${value.toFixed(0)}`}
              />
              <Tooltip
                labelFormatter={(value) => new Date(value).toLocaleDateString()}
                formatter={formatTooltipValue}
                contentStyle={{
                  backgroundColor: 'white',
                  border: '1px solid #e0e0e0',
                  borderRadius: '6px',
                  boxShadow: '0 2px 8px rgba(0,0,0,0.1)'
                }}
              />
              <Legend />

              {/* Price lines */}
              <Line
                type="monotone"
                dataKey="close"
                stroke="#2563eb"
                strokeWidth={2}
                name="Close Price"
                dot={false}
              />
              <Line
                type="monotone"
                dataKey="open"
                stroke="#10b981"
                strokeWidth={1}
                name="Open Price"
                dot={false}
              />

              {/* Technical indicators */}
              {showIndicators && (
                <>
                  {priceData[0] && 'SMA_SMA_20' in priceData[0] && (
                    <Line
                      type="monotone"
                      dataKey="SMA_SMA_20"
                      stroke="#f59e0b"
                      strokeWidth={1}
                      name="SMA 20"
                      dot={false}
                    />
                  )}
                  {priceData[0] && 'SMA_SMA_50' in priceData[0] && (
                    <Line
                      type="monotone"
                      dataKey="SMA_SMA_50"
                      stroke="#ef4444"
                      strokeWidth={1}
                      name="SMA 50"
                      dot={false}
                    />
                  )}
                  {priceData[0] && 'SMA_SMA_200' in priceData[0] && (
                    <Line
                      type="monotone"
                      dataKey="SMA_SMA_200"
                      stroke="#8b5cf6"
                      strokeWidth={1}
                      name="SMA 200"
                      dot={false}
                    />
                  )}
                </>
              )}

              {/* Current price reference line */}
              <ReferenceLine
                y={priceData[0]?.close}
                stroke="#2563eb"
                strokeDasharray="2 2"
                label={{ value: "Current", position: "topRight" }}
              />
            </LineChart>
          </ResponsiveContainer>
        </div>
      </CardContent>
    </Card>
  );
}
