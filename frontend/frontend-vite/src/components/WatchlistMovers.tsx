import { Card } from "./ui/card";
import { TrendingUp, TrendingDown } from "lucide-react";

interface WatchlistMover {
  symbol: string;
  name: string;
  price: number;
  change: number;
  changePercentage: number;
  volume: string;
}

interface WatchlistMoversProps {
  gainers: WatchlistMover[];
  losers: WatchlistMover[];
}

export function WatchlistMovers({ gainers, losers }: WatchlistMoversProps) {
  const formatCurrency = (amount: number) => {
    return new Intl.NumberFormat('en-US', {
      style: 'currency',
      currency: 'USD',
    }).format(amount);
  };

  const renderMoversList = (movers: WatchlistMover[], isGainer: boolean) => {
    const Icon = isGainer ? TrendingUp : TrendingDown;
    const colorClass = isGainer ? 'text-green-600' : 'text-red-600';
    const bgClass = isGainer ? 'bg-green-50' : 'bg-red-50';

    return (
      <div className="space-y-3">
        {movers.map((mover, index) => (
          <div key={index} className="flex items-center justify-between p-3 bg-gray-50 rounded-lg">
            <div className="flex items-center gap-3">
              <div className={`p-2 rounded ${bgClass}`}>
                <Icon className={`w-4 h-4 ${colorClass}`} />
              </div>
              <div>
                <h4 className="font-medium text-sm">{mover.symbol}</h4>
                <p className="text-xs text-muted-foreground">{mover.name}</p>
              </div>
            </div>

            <div className="text-right">
              <p className="font-medium text-sm">{formatCurrency(mover.price)}</p>
              <div className="flex items-center gap-1">
                <span className={`text-xs ${colorClass}`}>
                  {isGainer ? '+' : ''}{mover.change.toFixed(2)} ({isGainer ? '+' : ''}{mover.changePercentage.toFixed(2)}%)
                </span>
              </div>
              <p className="text-xs text-muted-foreground">Vol: {mover.volume}</p>
            </div>
          </div>
        ))}
      </div>
    );
  };

  return (
    <Card className="p-6">
      <div className="flex items-center justify-between mb-4">
        <h3 className="text-lg font-semibold">Watchlist Movers</h3>
        <button className="text-sm text-blue-600 hover:text-blue-700">
          View Watchlist →
        </button>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        <div>
          <h4 className="font-medium text-sm mb-3 flex items-center gap-2">
            <TrendingUp className="w-4 h-4 text-green-600" />
            Top Gainers
          </h4>
          {renderMoversList(gainers, true)}
        </div>

        <div>
          <h4 className="font-medium text-sm mb-3 flex items-center gap-2">
            <TrendingDown className="w-4 h-4 text-red-600" />
            Top Losers
          </h4>
          {renderMoversList(losers, false)}
        </div>
      </div>
    </Card>
  );
}
