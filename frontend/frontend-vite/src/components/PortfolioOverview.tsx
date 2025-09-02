import { Card } from "./ui/card";

interface PortfolioData {
  totalValue: number;
  totalReturn: number;
  returnPercentage: number;
  holdings: number;
}

interface PortfolioOverviewProps {
  data: PortfolioData;
}

export function PortfolioOverview({ data }: PortfolioOverviewProps) {
  const formatCurrency = (amount: number) => {
    return new Intl.NumberFormat('en-US', {
      style: 'currency',
      currency: 'USD',
    }).format(amount);
  };

  const formatPercentage = (percentage: number) => {
    const sign = percentage >= 0 ? '+' : '';
    return `${sign}${percentage.toFixed(2)}%`;
  };

  return (
    <div className="mb-8">
      <div className="flex items-center justify-between mb-4">
        <h2 className="text-xl font-semibold">Growth Portfolio</h2>
        <button className="text-sm text-blue-600 hover:text-blue-700">
          View Details →
        </button>
      </div>

      <p className="text-sm text-muted-foreground mb-4">
        Technology and growth stocks
      </p>

      <div className="grid grid-cols-3 gap-6">
        <div>
          <label className="text-sm text-muted-foreground">Total Value</label>
          <p className="text-2xl font-semibold">{formatCurrency(data.totalValue)}</p>
        </div>

        <div>
          <label className="text-sm text-muted-foreground">Total Return</label>
          <div className="flex items-center gap-2">
            <p className={`text-2xl font-semibold ${data.totalReturn >= 0 ? 'text-green-600' : 'text-red-600'}`}>
              {data.totalReturn >= 0 ? '+' : ''}{formatCurrency(data.totalReturn)}
            </p>
            <span className={`text-sm ${data.totalReturn >= 0 ? 'text-green-600' : 'text-red-600'}`}>
              ({formatPercentage(data.returnPercentage)})
            </span>
          </div>
        </div>

        <div>
          <label className="text-sm text-muted-foreground">Holdings</label>
          <p className="text-2xl font-semibold">{data.holdings}</p>
        </div>
      </div>
    </div>
  );
}
