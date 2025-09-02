import { Card } from "./ui/card";
import { TrendingUp, TrendingDown } from "lucide-react";

interface MarketIndex {
  name: string;
  symbol: string;
  value: number;
  change: number;
  changePercentage: number;
  region: string;
}

interface MarketIndicesProps {
  indices?: MarketIndex[];
}

export function MarketIndices({ indices = [] }: MarketIndicesProps) {
  const formatValue = (value: number) => {
    return new Intl.NumberFormat('en-US', {
      minimumFractionDigits: 2,
      maximumFractionDigits: 2,
    }).format(value);
  };

  const formatChange = (change: number) => {
    const sign = change >= 0 ? '+' : '';
    return `${sign}${formatValue(change)}`;
  };

  const formatPercentage = (percentage: number) => {
    const sign = percentage >= 0 ? '+' : '';
    return `${sign}${percentage.toFixed(2)}%`;
  };

  return (
    <Card className="p-6">
      <h2 className="text-xl font-semibold mb-4">Global Market Indices</h2>

      {!indices || indices.length === 0 ? (
        <div className="text-center py-8">
          <p className="text-muted-foreground">Market indices data unavailable</p>
        </div>
      ) : (
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
          {indices.map((index) => (
            <div
              key={index.symbol}
              className="p-4 border rounded-lg bg-card hover:bg-accent/50 transition-colors"
            >
              <div className="flex items-start justify-between mb-2">
                <div>
                  <h3 className="font-medium text-sm">{index.name}</h3>
                  <p className="text-xs text-muted-foreground">{index.symbol} • {index.region}</p>
                </div>
                <div className={`flex items-center gap-1 ${
                  index.change >= 0 ? 'text-green-600' : 'text-red-600'
                }`}>
                  {index.change >= 0 ? (
                    <TrendingUp className="w-3 h-3" />
                  ) : (
                    <TrendingDown className="w-3 h-3" />
                  )}
                </div>
              </div>

              <div className="space-y-1">
                <p className="text-lg font-semibold">{formatValue(index.value)}</p>
                <div className={`text-sm ${
                  index.change >= 0 ? 'text-green-600' : 'text-red-600'
                }`}>
                  <span>{formatChange(index.change)}</span>
                  <span className="ml-2">({formatPercentage(index.changePercentage)})</span>
                </div>
              </div>
            </div>
          ))}
        </div>
      )}
    </Card>
  );
}
