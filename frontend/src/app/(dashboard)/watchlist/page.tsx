"use client";

import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { Badge } from "@/components/ui/badge";
import { DashboardPageLayout, StatsCard, EmptyState } from "@/components/layouts";
import { Plus, TrendingUp, TrendingDown, Minus } from "lucide-react";
import Link from "next/link";

export default function WatchlistPage() {
  // Mock watchlist data
  const watchlistItems = [
    {
      symbol: "AAPL",
      name: "Apple Inc.",
      price: 175.43,
      change: 2.15,
      changePercent: 1.24,
      volume: "45.2M",
      marketCap: "2.7T"
    },
    {
      symbol: "GOOGL",
      name: "Alphabet Inc.",
      price: 142.56,
      change: -1.23,
      changePercent: -0.86,
      volume: "28.7M",
      marketCap: "1.8T"
    },
    {
      symbol: "MSFT",
      name: "Microsoft Corporation",
      price: 378.85,
      change: 5.67,
      changePercent: 1.52,
      volume: "32.1M",
      marketCap: "2.8T"
    },
    {
      symbol: "TSLA",
      name: "Tesla, Inc.",
      price: 248.42,
      change: -3.21,
      changePercent: -1.27,
      volume: "89.3M",
      marketCap: "790B"
    }
  ];

  const handleAddStock = () => {
    console.log('Add stock clicked');
    // TODO: Implement add stock functionality
  };

  const handleRemoveStock = (symbol: string) => {
    console.log('Remove stock:', symbol);
    // TODO: Implement remove stock functionality
  };

  return (
    <DashboardPageLayout
      title="Watchlist"
      description="Track your favorite stocks and monitor market movements"
      actions={[
        {
          label: 'Add Stock',
          onClick: handleAddStock,
          icon: <Plus className="h-4 w-4" />
        }
      ]}
      status={[
        { label: 'API', value: 'Connected', color: 'green' },
        { label: 'Backend', value: 'FastAPI', color: 'blue' }
      ]}
    >

      <div className="grid gap-4">
        {watchlistItems.map((item) => (
          <Card key={item.symbol} className="hover:shadow-md transition-shadow">
            <CardHeader className="pb-3">
              <div className="flex items-center justify-between">
                <div className="flex-1">
                  <Link href={`/companies/${item.symbol}`} className="hover:underline">
                    <CardTitle className="text-lg text-blue-600 hover:text-blue-800">{item.symbol}</CardTitle>
                  </Link>
                  <CardDescription className="text-sm">{item.name}</CardDescription>
                </div>
                <div className="text-right">
                  <div className="text-lg font-semibold">${item.price}</div>
                  <div className={`flex items-center text-sm ${
                    item.change >= 0 ? 'text-green-600' : 'text-red-600'
                  }`}>
                    {item.change >= 0 ? (
                      <TrendingUp className="mr-1 h-3 w-3" />
                    ) : (
                      <TrendingDown className="mr-1 h-3 w-3" />
                    )}
                    {item.change >= 0 ? '+' : ''}{item.change} ({item.changePercent >= 0 ? '+' : ''}{item.changePercent}%)
                  </div>
                </div>
              </div>
            </CardHeader>
            <CardContent className="pt-0">
              <div className="grid grid-cols-2 gap-4 text-sm">
                <div>
                  <span className="text-muted-foreground">Volume:</span>
                  <span className="ml-2 font-medium">{item.volume}</span>
                </div>
                <div>
                  <span className="text-muted-foreground">Market Cap:</span>
                  <span className="ml-2 font-medium">{item.marketCap}</span>
                </div>
              </div>
            </CardContent>
          </Card>
        ))}
      </div>
    </DashboardPageLayout>
  );
}
