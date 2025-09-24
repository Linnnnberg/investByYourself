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
  ComposedChart,
  Bar
} from 'recharts';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Badge } from '@/components/ui/badge';
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from '@/components/ui/select';
import { Download, RefreshCw, BarChart3 } from 'lucide-react';

interface TechnicalIndicatorData {
  date: string;
  [key: string]: any;
}

interface TechnicalIndicatorsChartProps {
  symbol: string;
  companyName?: string;
  className?: string;
}

const INDICATOR_TYPES = [
  { value: 'RSI', label: 'RSI (Relative Strength Index)', color: '#ef4444' },
  { value: 'MACD', label: 'MACD (Moving Average Convergence Divergence)', color: '#3b82f6' },
  { value: 'SMA', label: 'Simple Moving Averages', color: '#10b981' },
  { value: 'EMA', label: 'Exponential Moving Averages', color: '#f59e0b' },
  { value: 'BOLLINGER', label: 'Bollinger Bands', color: '#8b5cf6' },
  { value: 'STOCHASTIC', label: 'Stochastic Oscillator', color: '#06b6d4' },
  { value: 'WILLIAMS_R', label: 'Williams %R', color: '#84cc16' },
  { value: 'ATR', label: 'Average True Range', color: '#f97316' },
  { value: 'VOLUME', label: 'Volume Indicators', color: '#6366f1' }
];

export function TechnicalIndicatorsChart({
  symbol,
  companyName,
  className = ""
}: TechnicalIndicatorsChartProps) {
  const [indicatorData, setIndicatorData] = useState<TechnicalIndicatorData[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [selectedIndicator, setSelectedIndicator] = useState<string>('RSI');
  const [availableIndicators, setAvailableIndicators] = useState<string[]>([]);

  useEffect(() => {
    fetchTechnicalIndicators();
  }, [symbol]);

  const fetchTechnicalIndicators = async () => {
    try {
      setLoading(true);
      setError(null);

      const response = await fetch(
        `/api/v1/historical-data/companies/${symbol}/technical-indicators`
      );

      if (!response.ok) {
        throw new Error(`Failed to fetch indicators: ${response.statusText}`);
      }

      const data = await response.json();

      // Transform the grouped indicators into chart data
      const chartData = transformIndicatorData(data.indicators);
      setIndicatorData(chartData);

      // Extract available indicator types
      const types = Object.keys(data.indicators).map(key => {
        const parts = key.split('_');
        return parts[0];
      });
      const uniqueTypes = [...new Set(types)];
      setAvailableIndicators(uniqueTypes);

      if (uniqueTypes.length > 0 && !selectedIndicator) {
        setSelectedIndicator(uniqueTypes[0]);
      }
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to fetch technical indicators');
      console.error('Error fetching technical indicators:', err);
    } finally {
      setLoading(false);
    }
  };

  const transformIndicatorData = (indicators: Record<string, any[]>) => {
    const dateMap = new Map<string, any>();

    Object.entries(indicators).forEach(([key, values]) => {
      values.forEach(({ date, value }) => {
        if (!dateMap.has(date)) {
          dateMap.set(date, { date });
        }
        dateMap.get(date)[key] = value;
      });
    });

    return Array.from(dateMap.values()).sort((a, b) =>
      new Date(a.date).getTime() - new Date(b.date).getTime()
    );
  };

  const getIndicatorLines = () => {
    const lines: JSX.Element[] = [];
    const indicatorType = selectedIndicator;

    if (indicatorData.length === 0) return lines;

    // Get all keys that match the selected indicator type
    const relevantKeys = Object.keys(indicatorData[0]).filter(key =>
      key.startsWith(indicatorType) && key !== 'date'
    );

    relevantKeys.forEach((key, index) => {
      const color = getIndicatorColor(key, index);
      lines.push(
        <Line
          key={key}
          type="monotone"
          dataKey={key}
          stroke={color}
          strokeWidth={2}
          name={key.replace(`${indicatorType}_`, '').replace('_', ' ')}
          dot={false}
        />
      );
    });

    return lines;
  };

  const getIndicatorColor = (key: string, index: number) => {
    const colors = [
      '#ef4444', '#3b82f6', '#10b981', '#f59e0b', '#8b5cf6',
      '#06b6d4', '#84cc16', '#f97316', '#6366f1', '#ec4899'
    ];
    return colors[index % colors.length];
  };

  const formatTooltipValue = (value: number, name: string) => {
    if (name.includes('volume') || name.includes('Volume')) {
      return [value.toLocaleString(), name];
    }
    return [value.toFixed(4), name];
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
      ['Date', ...Object.keys(indicatorData[0] || {}).filter(key => key !== 'date')].join(','),
      ...indicatorData.map(d => [
        d.date,
        ...Object.keys(d).filter(key => key !== 'date').map(key => d[key] || '')
      ].join(','))
    ].join('\n');

    const blob = new Blob([csvContent], { type: 'text/csv' });
    const url = window.URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = url;
    a.download = `${symbol}_technical_indicators.csv`;
    a.click();
    window.URL.revokeObjectURL(url);
  };

  const getYAxisDomain = () => {
    if (selectedIndicator === 'RSI') return [0, 100];
    if (selectedIndicator === 'STOCHASTIC') return [0, 100];
    if (selectedIndicator === 'WILLIAMS_R') return [-100, 0];
    return ['dataMin - 5', 'dataMax + 5'];
  };

  if (loading) {
    return (
      <Card className={className}>
        <CardHeader>
          <CardTitle className="flex items-center gap-2">
            <RefreshCw className="h-4 w-4 animate-spin" />
            Loading Technical Indicators for {symbol}
          </CardTitle>
        </CardHeader>
        <CardContent>
          <div className="h-96 flex items-center justify-center">
            <div className="text-center">
              <RefreshCw className="h-8 w-8 animate-spin mx-auto mb-2" />
              <p className="text-muted-foreground">Loading technical indicators...</p>
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
          <CardTitle>Technical Indicators - {symbol}</CardTitle>
        </CardHeader>
        <CardContent>
          <div className="h-96 flex items-center justify-center">
            <div className="text-center">
              <p className="text-red-500 mb-4">{error}</p>
              <Button onClick={fetchTechnicalIndicators} variant="outline">
                <RefreshCw className="h-4 w-4 mr-2" />
                Retry
              </Button>
            </div>
          </div>
        </CardContent>
      </Card>
    );
  }

  if (indicatorData.length === 0) {
    return (
      <Card className={className}>
        <CardHeader>
          <CardTitle>Technical Indicators - {symbol}</CardTitle>
        </CardHeader>
        <CardContent>
          <div className="h-96 flex items-center justify-center">
            <div className="text-center">
              <p className="text-muted-foreground mb-4">No technical indicators available</p>
              <Button onClick={fetchTechnicalIndicators} variant="outline">
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
              <BarChart3 className="h-5 w-5" />
              Technical Indicators - {symbol}
              {companyName && (
                <span className="text-sm text-muted-foreground">({companyName})</span>
              )}
            </CardTitle>
            <p className="text-sm text-muted-foreground">
              {indicatorData.length} data points available
            </p>
          </div>
          <div className="flex items-center gap-2">
            <Select value={selectedIndicator} onValueChange={setSelectedIndicator}>
              <SelectTrigger className="w-48">
                <SelectValue placeholder="Select indicator" />
              </SelectTrigger>
              <SelectContent>
                {availableIndicators.map(type => {
                  const indicator = INDICATOR_TYPES.find(i => i.value === type);
                  return (
                    <SelectItem key={type} value={type}>
                      {indicator?.label || type}
                    </SelectItem>
                  );
                })}
              </SelectContent>
            </Select>
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
              onClick={fetchTechnicalIndicators}
            >
              <RefreshCw className="h-4 w-4" />
            </Button>
          </div>
        </div>
      </CardHeader>
      <CardContent>
        <div className="h-96 w-full">
          <ResponsiveContainer width="100%" height="100%">
            <LineChart data={indicatorData}>
              <CartesianGrid strokeDasharray="3 3" stroke="#f0f0f0" />
              <XAxis
                dataKey="date"
                tickFormatter={formatXAxisLabel}
                stroke="#666"
                fontSize={12}
              />
              <YAxis
                domain={getYAxisDomain()}
                stroke="#666"
                fontSize={12}
                tickFormatter={(value) => value.toFixed(2)}
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
              {getIndicatorLines()}
            </LineChart>
          </ResponsiveContainer>
        </div>
      </CardContent>
    </Card>
  );
}
