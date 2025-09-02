import { Card } from "./ui/card";

interface Sector {
  name: string;
  symbol: string;
  price: number;
  change: number;
  changePercentage: number;
}

interface SectorPerformanceProps {
  sectors: Sector[];
}

export function SectorPerformance({ sectors }: SectorPerformanceProps) {
  const formatCurrency = (amount: number) => {
    return new Intl.NumberFormat('en-US', {
      style: 'currency',
      currency: 'USD',
    }).format(amount);
  };

  const formatChange = (change: number, percentage: number) => {
    const isPositive = change >= 0;
    const sign = isPositive ? '+' : '';
    const colorClass = isPositive ? 'text-green-600' : 'text-red-600';
    const bgClass = isPositive ? 'bg-green-50' : 'bg-red-50';

    return (
      <div className={`px-2 py-1 rounded ${bgClass}`}>
        <span className={colorClass}>
          {sign}{change.toFixed(2)} ({sign}{percentage.toFixed(2)}%)
        </span>
      </div>
    );
  };

  return (
    <Card className="p-6">
      <div className="flex items-center justify-between mb-4">
        <h3 className="text-lg font-semibold">Sector Performance</h3>
        <button className="text-sm text-blue-600 hover:text-blue-700">
          View All Sectors →
        </button>
      </div>

      <div className="space-y-3">
        {sectors.map((sector, index) => (
          <div key={index} className="flex items-center justify-between p-3 bg-gray-50 rounded-lg">
            <div className="flex-1">
              <div className="flex items-center gap-3">
                <div>
                  <h4 className="font-medium">{sector.name}</h4>
                  <p className="text-sm text-muted-foreground">{sector.symbol}</p>
                </div>
              </div>
            </div>

            <div className="flex items-center gap-4">
              <div className="text-right">
                <p className="font-medium">{formatCurrency(sector.price)}</p>
              </div>
              {formatChange(sector.change, sector.changePercentage)}
            </div>
          </div>
        ))}
      </div>
    </Card>
  );
}
