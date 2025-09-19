'use client';

import { useState } from 'react';
import { Button } from '@/components/ui/button';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card';
import { Badge } from '@/components/ui/badge';
import {
  MoreHorizontal,
  TrendingUp,
  TrendingDown,
  PieChart,
  Settings,
  Eye,
  Edit,
  Trash2
} from 'lucide-react';

interface Portfolio {
  id: string;
  name: string;
  description: string;
  value: number;
  change: number;
  changePercent: number;
  allocation: Record<string, number>;
  riskLevel: 'Low' | 'Medium' | 'High';
  lastUpdated: string;
  status: 'Active' | 'Draft' | 'Archived';
}

interface PortfolioListProps {
  portfolios: Portfolio[];
  onViewPortfolio: (portfolioId: string) => void;
  onEditPortfolio: (portfolioId: string) => void;
  onDeletePortfolio: (portfolioId: string) => void;
  onCreatePortfolio: () => void;
}

export default function PortfolioList({
  portfolios,
  onViewPortfolio,
  onEditPortfolio,
  onDeletePortfolio,
  onCreatePortfolio
}: PortfolioListProps) {
  const [selectedPortfolio, setSelectedPortfolio] = useState<string | null>(null);

  const formatCurrency = (value: number) => {
    return new Intl.NumberFormat('en-US', {
      style: 'currency',
      currency: 'USD',
      minimumFractionDigits: 0,
      maximumFractionDigits: 0,
    }).format(value);
  };

  const formatPercent = (value: number) => {
    return `${value >= 0 ? '+' : ''}${value.toFixed(2)}%`;
  };

  const getRiskColor = (riskLevel: string) => {
    switch (riskLevel) {
      case 'Low': return 'bg-green-100 text-green-800';
      case 'Medium': return 'bg-yellow-100 text-yellow-800';
      case 'High': return 'bg-red-100 text-red-800';
      default: return 'bg-gray-100 text-gray-800';
    }
  };

  const getStatusColor = (status: string) => {
    switch (status) {
      case 'Active': return 'bg-green-100 text-green-800';
      case 'Draft': return 'bg-yellow-100 text-yellow-800';
      case 'Archived': return 'bg-gray-100 text-gray-800';
      default: return 'bg-gray-100 text-gray-800';
    }
  };

  if (portfolios.length === 0) {
    return (
      <Card className="text-center py-12">
        <CardContent>
          <PieChart className="h-12 w-12 mx-auto mb-4 text-gray-400" />
          <h3 className="text-lg font-semibold mb-2">No Portfolios Yet</h3>
          <p className="text-muted-foreground mb-6">
            Create your first portfolio to start tracking your investments
          </p>
          <Button onClick={onCreatePortfolio}>
            Create Your First Portfolio
          </Button>
        </CardContent>
      </Card>
    );
  }

  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <div>
          <h2 className="text-2xl font-bold">Your Portfolios</h2>
          <p className="text-muted-foreground">
            Manage and track your investment portfolios
          </p>
        </div>
        <Button onClick={onCreatePortfolio}>
          Create Portfolio
        </Button>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
        {portfolios.map((portfolio) => (
          <Card
            key={portfolio.id}
            className="hover:shadow-md transition-shadow cursor-pointer"
            onClick={() => onViewPortfolio(portfolio.id)}
          >
            <CardHeader className="pb-3">
              <div className="flex items-start justify-between">
                <div className="space-y-1">
                  <CardTitle className="text-lg">{portfolio.name}</CardTitle>
                  <CardDescription className="text-sm">
                    {portfolio.description}
                  </CardDescription>
                </div>
                <div className="flex items-center gap-2">
                  <Badge className={getRiskColor(portfolio.riskLevel)}>
                    {portfolio.riskLevel}
                  </Badge>
                  <Badge variant="outline" className={getStatusColor(portfolio.status)}>
                    {portfolio.status}
                  </Badge>
                </div>
              </div>
            </CardHeader>

            <CardContent className="space-y-4">
              <div className="space-y-2">
                <div className="flex items-center justify-between">
                  <span className="text-2xl font-bold">
                    {formatCurrency(portfolio.value)}
                  </span>
                  <div className={`flex items-center gap-1 text-sm ${
                    portfolio.change >= 0 ? 'text-green-600' : 'text-red-600'
                  }`}>
                    {portfolio.change >= 0 ? (
                      <TrendingUp className="h-4 w-4" />
                    ) : (
                      <TrendingDown className="h-4 w-4" />
                    )}
                    {formatPercent(portfolio.changePercent)}
                  </div>
                </div>
                <p className="text-sm text-muted-foreground">
                  Last updated: {new Date(portfolio.lastUpdated).toLocaleDateString()}
                </p>
              </div>

              <div className="space-y-2">
                <h4 className="text-sm font-medium">Allocation</h4>
                <div className="space-y-1">
                  {Object.entries(portfolio.allocation)
                    .sort(([,a], [,b]) => b - a)
                    .slice(0, 3)
                    .map(([asset, weight]) => (
                    <div key={asset} className="flex justify-between text-sm">
                      <span>{asset}</span>
                      <span className="font-medium">{weight.toFixed(1)}%</span>
                    </div>
                  ))}
                  {Object.keys(portfolio.allocation).length > 3 && (
                    <div className="text-xs text-muted-foreground">
                      +{Object.keys(portfolio.allocation).length - 3} more
                    </div>
                  )}
                </div>
              </div>

              <div className="flex items-center gap-2 pt-2">
                <Button
                  variant="outline"
                  size="sm"
                  onClick={(e) => {
                    e.stopPropagation();
                    onViewPortfolio(portfolio.id);
                  }}
                >
                  <Eye className="h-4 w-4 mr-1" />
                  View
                </Button>
                <Button
                  variant="outline"
                  size="sm"
                  onClick={(e) => {
                    e.stopPropagation();
                    onEditPortfolio(portfolio.id);
                  }}
                >
                  <Edit className="h-4 w-4 mr-1" />
                  Edit
                </Button>
                <Button
                  variant="outline"
                  size="sm"
                  onClick={(e) => {
                    e.stopPropagation();
                    onDeletePortfolio(portfolio.id);
                  }}
                >
                  <Trash2 className="h-4 w-4 mr-1" />
                </Button>
              </div>
            </CardContent>
          </Card>
        ))}
      </div>
    </div>
  );
}
