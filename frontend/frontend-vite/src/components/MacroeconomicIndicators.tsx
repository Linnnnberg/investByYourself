import { Card } from "./ui/card";
import { TrendingUp, TrendingDown } from "lucide-react";

interface MacroIndicator {
  name: string;
  value: string;
  change: number;
  period: string;
  description: string;
}

interface MacroeconomicIndicatorsProps {
  indicators?: MacroIndicator[];
}

export function MacroeconomicIndicators({ indicators = [] }: MacroeconomicIndicatorsProps) {
  const formatChange = (change: number) => {
    const isPositive = change >= 0;
    const Icon = isPositive ? TrendingUp : TrendingDown;
    const colorClass = isPositive ? "text-green-600" : "text-red-600";
    const bgClass = isPositive ? "bg-green-50" : "bg-red-50";

    return (
      <div className={`flex items-center gap-1 px-2 py-1 rounded ${bgClass}`}>
        <Icon className={`w-3 h-3 ${colorClass}`} />
        <span className={`text-xs ${colorClass}`}>
          {isPositive ? '+' : ''}{change.toFixed(1)}%
        </span>
      </div>
    );
  };

  return (
    <Card className="p-6">
      <h3 className="text-lg font-semibold mb-4">Macroeconomic Indicators</h3>

      {!indicators || indicators.length === 0 ? (
        <div className="text-center py-8">
          <p className="text-muted-foreground">Macroeconomic data unavailable</p>
        </div>
      ) : (
        <div className="grid grid-cols-2 lg:grid-cols-4 gap-4">
          {indicators.map((indicator, index) => (
            <div key={index} className="space-y-2">
              <div className="flex items-center justify-between">
                <h4 className="text-sm font-medium text-muted-foreground">{indicator.name}</h4>
                {formatChange(indicator.change)}
              </div>
              <p className="text-xl font-semibold">{indicator.value}</p>
              <div className="space-y-1">
                <p className="text-xs text-muted-foreground">{indicator.period}</p>
                <p className="text-xs text-muted-foreground">{indicator.description}</p>
              </div>
            </div>
          ))}
        </div>
      )}
    </Card>
  );
}
