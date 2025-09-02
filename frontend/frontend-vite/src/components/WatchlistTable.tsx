import { Button } from "./ui/button";
import { Card } from "./ui/card";

interface Stock {
  symbol: string;
  name: string;
  price: number;
  change: number;
  changePercentage: number;
  marketCap: string;
  peRatio: number;
}

interface WatchlistTableProps {
  stocks: Stock[];
  onBuy: (symbol: string) => void;
  onRemove: (symbol: string) => void;
}

export function WatchlistTable({ stocks, onBuy, onRemove }: WatchlistTableProps) {
  const formatCurrency = (amount: number) => {
    return new Intl.NumberFormat('en-US', {
      style: 'currency',
      currency: 'USD',
    }).format(amount);
  };

  const formatChange = (change: number, percentage: number) => {
    const sign = change >= 0 ? '+' : '';
    const color = change >= 0 ? 'text-green-600' : 'text-red-600';
    return (
      <span className={color}>
        {sign}{change.toFixed(2)} ({sign}{percentage.toFixed(2)}%)
      </span>
    );
  };

  return (
    <Card className="mb-8">
      <div className="p-6">
        <div className="flex items-center justify-between mb-6">
          <h2 className="text-xl font-semibold">Watchlist</h2>
          <button className="text-sm text-blue-600 hover:text-blue-700">
            View All →
          </button>
        </div>

        <div className="overflow-x-auto">
          <table className="w-full">
            <thead>
              <tr className="border-b border-border">
                <th className="text-left text-sm text-muted-foreground py-3 font-medium">SYMBOL</th>
                <th className="text-left text-sm text-muted-foreground py-3 font-medium">NAME</th>
                <th className="text-left text-sm text-muted-foreground py-3 font-medium">PRICE</th>
                <th className="text-left text-sm text-muted-foreground py-3 font-medium">CHANGE</th>
                <th className="text-left text-sm text-muted-foreground py-3 font-medium">MARKET CAP</th>
                <th className="text-left text-sm text-muted-foreground py-3 font-medium">P/E RATIO</th>
                <th className="text-left text-sm text-muted-foreground py-3 font-medium">ACTIONS</th>
              </tr>
            </thead>
            <tbody>
              {stocks.map((stock) => (
                <tr key={stock.symbol} className="border-b border-border/50">
                  <td className="py-4">
                    <span className="text-blue-600 font-medium">{stock.symbol}</span>
                  </td>
                  <td className="py-4">
                    <div>
                      <div className="font-medium">{stock.name}</div>
                      <div className="text-sm text-muted-foreground">Technology</div>
                    </div>
                  </td>
                  <td className="py-4 font-medium">{formatCurrency(stock.price)}</td>
                  <td className="py-4">{formatChange(stock.change, stock.changePercentage)}</td>
                  <td className="py-4">{stock.marketCap}</td>
                  <td className="py-4">{stock.peRatio}</td>
                  <td className="py-4">
                    <div className="flex gap-2">
                      <Button
                        size="sm"
                        onClick={() => onBuy(stock.symbol)}
                        className="bg-blue-600 hover:bg-blue-700 text-white"
                      >
                        Buy
                      </Button>
                      <Button
                        size="sm"
                        variant="outline"
                        onClick={() => onRemove(stock.symbol)}
                      >
                        Remove
                      </Button>
                    </div>
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </div>
    </Card>
  );
}
