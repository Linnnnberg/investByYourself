import { useState, useEffect } from "react";
import { Card } from "./ui/card";
import { Input } from "./ui/input";
import { Label } from "./ui/label";
import { Trash2, Plus, TrendingUp, TrendingDown, X } from "lucide-react";
import { projectId, publicAnonKey } from "../utils/supabase/info";

interface Position {
  id: string;
  symbol: string;
  name: string;
  currentPrice: number;
  averageCost: number;
  units: number;
  totalValue: number;
  totalCost: number;
  gainLoss: number;
  gainLossPercentage: number;
}

export function PositionList() {
  const [positions, setPositions] = useState<Position[]>([]);
  const [loading, setLoading] = useState(true);
  const [isAddDialogOpen, setIsAddDialogOpen] = useState(false);
  const [newPosition, setNewPosition] = useState({
    symbol: "",
    name: "",
    averageCost: "",
    units: "",
  });

  useEffect(() => {
    loadPositions();
  }, []);

  useEffect(() => {
    const handleEscape = (e: KeyboardEvent) => {
      if (e.key === 'Escape' && isAddDialogOpen) {
        setIsAddDialogOpen(false);
      }
    };

    if (isAddDialogOpen) {
      document.addEventListener('keydown', handleEscape);
      document.body.style.overflow = 'hidden';
    } else {
      document.body.style.overflow = 'unset';
    }

    return () => {
      document.removeEventListener('keydown', handleEscape);
      document.body.style.overflow = 'unset';
    };
  }, [isAddDialogOpen]);

  const loadPositions = async () => {
    try {
      const response = await fetch(
        `https://${projectId}.supabase.co/functions/v1/make-server-9c463a03/positions`,
        {
          headers: {
            'Authorization': `Bearer ${publicAnonKey}`,
            'Content-Type': 'application/json',
          },
        }
      );

      if (response.ok) {
        const data = await response.json();
        setPositions(data);
      } else {
        console.error("Failed to load positions:", await response.text());
      }
    } catch (error) {
      console.error("Error loading positions:", error);
    } finally {
      setLoading(false);
    }
  };

  const addPosition = async () => {
    if (!newPosition.symbol || !newPosition.averageCost || !newPosition.units) {
      return;
    }

    try {
      const response = await fetch(
        `https://${projectId}.supabase.co/functions/v1/make-server-9c463a03/positions`,
        {
          method: 'POST',
          headers: {
            'Authorization': `Bearer ${publicAnonKey}`,
            'Content-Type': 'application/json',
          },
          body: JSON.stringify({
            symbol: newPosition.symbol.toUpperCase(),
            name: newPosition.name || newPosition.symbol.toUpperCase(),
            averageCost: parseFloat(newPosition.averageCost),
            units: parseFloat(newPosition.units),
          }),
        }
      );

      if (response.ok) {
        await loadPositions();
        setNewPosition({ symbol: "", name: "", averageCost: "", units: "" });
        setIsAddDialogOpen(false);
      } else {
        console.error("Failed to add position:", await response.text());
      }
    } catch (error) {
      console.error("Error adding position:", error);
    }
  };

  const removePosition = async (id: string) => {
    try {
      const response = await fetch(
        `https://${projectId}.supabase.co/functions/v1/make-server-9c463a03/positions/${id}`,
        {
          method: 'DELETE',
          headers: {
            'Authorization': `Bearer ${publicAnonKey}`,
          },
        }
      );

      if (response.ok) {
        await loadPositions();
      } else {
        console.error("Failed to remove position:", await response.text());
      }
    } catch (error) {
      console.error("Error removing position:", error);
    }
  };

  const formatCurrency = (amount: number) => {
    return new Intl.NumberFormat('en-US', {
      style: 'currency',
      currency: 'USD',
    }).format(amount);
  };

  const formatPercentage = (percentage: number) => {
    const isPositive = percentage >= 0;
    const sign = isPositive ? '+' : '';
    return `${sign}${percentage.toFixed(2)}%`;
  };

  const getTotalPortfolioValue = () => {
    return positions.reduce((sum, pos) => sum + pos.totalValue, 0);
  };

  const getTotalGainLoss = () => {
    return positions.reduce((sum, pos) => sum + pos.gainLoss, 0);
  };

  const getTotalGainLossPercentage = () => {
    const totalCost = positions.reduce((sum, pos) => sum + pos.totalCost, 0);
    const totalValue = positions.reduce((sum, pos) => sum + pos.totalValue, 0);
    if (totalCost === 0) return 0;
    return ((totalValue - totalCost) / totalCost) * 100;
  };

  if (loading) {
    return (
      <div className="p-6">
        <div className="flex items-center justify-center h-64">
          <div className="animate-pulse">Loading positions...</div>
        </div>
      </div>
    );
  }

  return (
    <div className="p-6 space-y-6">
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-2xl font-semibold mb-2">Portfolio</h1>
          <p className="text-muted-foreground">Manage your investment portfolio and track performance with real-time P&L calculations.</p>
        </div>

        <button
          onClick={() => setIsAddDialogOpen(true)}
          className="inline-flex items-center justify-center rounded-md bg-primary px-4 py-2 text-sm font-medium text-primary-foreground ring-offset-background transition-colors hover:bg-primary/90 focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-ring focus-visible:ring-offset-2 disabled:pointer-events-none disabled:opacity-50"
        >
          <Plus className="w-4 h-4 mr-2" />
          Add Position
        </button>

        {/* Custom Modal */}
        {isAddDialogOpen && (
          <div className="fixed inset-0 z-50 flex items-center justify-center">
            {/* Backdrop */}
            <div
              className="fixed inset-0 bg-black/50"
              onClick={() => setIsAddDialogOpen(false)}
            ></div>

            {/* Modal Content */}
            <div className="relative bg-card border border-border rounded-lg shadow-lg p-6 w-full max-w-md mx-4 z-10">
              <div className="flex items-center justify-between mb-4">
                <h2 className="text-lg font-semibold">Add New Position</h2>
                <button
                  onClick={() => setIsAddDialogOpen(false)}
                  className="inline-flex items-center justify-center rounded-md p-2 text-sm font-medium ring-offset-background transition-colors hover:bg-accent hover:text-accent-foreground focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-ring focus-visible:ring-offset-2"
                >
                  <X className="w-4 h-4" />
                </button>
              </div>

              <div className="space-y-4">
                <div>
                  <Label htmlFor="symbol">Symbol *</Label>
                  <Input
                    id="symbol"
                    placeholder="e.g., AAPL"
                    value={newPosition.symbol}
                    onChange={(e) => setNewPosition({...newPosition, symbol: e.target.value})}
                  />
                </div>
                <div>
                  <Label htmlFor="name">Company Name</Label>
                  <Input
                    id="name"
                    placeholder="e.g., Apple Inc."
                    value={newPosition.name}
                    onChange={(e) => setNewPosition({...newPosition, name: e.target.value})}
                  />
                </div>
                <div>
                  <Label htmlFor="averageCost">Average Cost *</Label>
                  <Input
                    id="averageCost"
                    type="number"
                    step="0.01"
                    placeholder="0.00"
                    value={newPosition.averageCost}
                    onChange={(e) => setNewPosition({...newPosition, averageCost: e.target.value})}
                  />
                </div>
                <div>
                  <Label htmlFor="units">Units *</Label>
                  <Input
                    id="units"
                    type="number"
                    step="0.001"
                    placeholder="0"
                    value={newPosition.units}
                    onChange={(e) => setNewPosition({...newPosition, units: e.target.value})}
                  />
                </div>
                <div className="flex gap-2 pt-4">
                  <button
                    onClick={addPosition}
                    className="flex-1 inline-flex items-center justify-center rounded-md bg-primary px-4 py-2 text-sm font-medium text-primary-foreground ring-offset-background transition-colors hover:bg-primary/90 focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-ring focus-visible:ring-offset-2 disabled:pointer-events-none disabled:opacity-50"
                  >
                    Add Position
                  </button>
                  <button
                    onClick={() => setIsAddDialogOpen(false)}
                    className="flex-1 inline-flex items-center justify-center rounded-md border border-input bg-background px-4 py-2 text-sm font-medium ring-offset-background transition-colors hover:bg-accent hover:text-accent-foreground focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-ring focus-visible:ring-offset-2 disabled:pointer-events-none disabled:opacity-50"
                  >
                    Cancel
                  </button>
                </div>
              </div>
            </div>
          </div>
        )}
      </div>

      {/* Portfolio Summary */}
      <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
        <Card className="p-4">
          <h3 className="text-sm font-medium text-muted-foreground mb-2">Total Value</h3>
          <p className="text-xl font-semibold">{formatCurrency(getTotalPortfolioValue())}</p>
        </Card>
        <Card className="p-4">
          <h3 className="text-sm font-medium text-muted-foreground mb-2">Total P&L</h3>
          <div className="flex items-center gap-2">
            <p className={`text-xl font-semibold ${getTotalGainLoss() >= 0 ? 'text-green-600' : 'text-red-600'}`}>
              {formatCurrency(getTotalGainLoss())}
            </p>
            {getTotalGainLoss() >= 0 ?
              <TrendingUp className="w-4 h-4 text-green-600" /> :
              <TrendingDown className="w-4 h-4 text-red-600" />
            }
          </div>
        </Card>
        <Card className="p-4">
          <h3 className="text-sm font-medium text-muted-foreground mb-2">Total P&L %</h3>
          <p className={`text-xl font-semibold ${getTotalGainLossPercentage() >= 0 ? 'text-green-600' : 'text-red-600'}`}>
            {formatPercentage(getTotalGainLossPercentage())}
          </p>
        </Card>
      </div>

      {/* Positions Table */}
      <Card>
        <div className="p-6">
          <h3 className="text-lg font-semibold mb-4">Portfolio Holdings</h3>

          {positions.length === 0 ? (
            <div className="text-center py-8">
              <p className="text-muted-foreground mb-4">No holdings in your portfolio yet</p>
              <button
                onClick={() => setIsAddDialogOpen(true)}
                className="inline-flex items-center justify-center rounded-md border border-input bg-background px-4 py-2 text-sm font-medium ring-offset-background transition-colors hover:bg-accent hover:text-accent-foreground focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-ring focus-visible:ring-offset-2 disabled:pointer-events-none disabled:opacity-50"
              >
                <Plus className="w-4 h-4 mr-2" />
                Add Your First Holding
              </button>
            </div>
          ) : (
            <div className="overflow-x-auto">
              <table className="w-full">
                <thead>
                  <tr className="border-b">
                    <th className="text-left py-3 px-2 font-medium">Symbol</th>
                    <th className="text-right py-3 px-2 font-medium">Price</th>
                    <th className="text-right py-3 px-2 font-medium">Avg. Cost</th>
                    <th className="text-right py-3 px-2 font-medium">Units</th>
                    <th className="text-right py-3 px-2 font-medium">W/L %</th>
                    <th className="text-right py-3 px-2 font-medium">W/L Amount</th>
                    <th className="text-right py-3 px-2 font-medium">Total Value</th>
                    <th className="w-10 py-3 px-2"></th>
                  </tr>
                </thead>
                <tbody>
                  {positions.map((position) => (
                    <tr key={position.id} className="border-b hover:bg-gray-50">
                      <td className="py-3 px-2">
                        <div>
                          <p className="font-medium">{position.symbol}</p>
                          <p className="text-sm text-muted-foreground">{position.name}</p>
                        </div>
                      </td>
                      <td className="text-right py-3 px-2 font-medium">
                        {formatCurrency(position.currentPrice)}
                      </td>
                      <td className="text-right py-3 px-2">
                        {formatCurrency(position.averageCost)}
                      </td>
                      <td className="text-right py-3 px-2">
                        {position.units.toLocaleString()}
                      </td>
                      <td className={`text-right py-3 px-2 font-medium ${position.gainLossPercentage >= 0 ? 'text-green-600' : 'text-red-600'}`}>
                        {formatPercentage(position.gainLossPercentage)}
                      </td>
                      <td className={`text-right py-3 px-2 font-medium ${position.gainLoss >= 0 ? 'text-green-600' : 'text-red-600'}`}>
                        {formatCurrency(position.gainLoss)}
                      </td>
                      <td className="text-right py-3 px-2 font-medium">
                        {formatCurrency(position.totalValue)}
                      </td>
                      <td className="py-3 px-2">
                        <button
                          onClick={() => removePosition(position.id)}
                          className="inline-flex items-center justify-center rounded-md p-2 text-sm font-medium text-red-600 ring-offset-background transition-colors hover:bg-red-50 hover:text-red-700 focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-ring focus-visible:ring-offset-2 disabled:pointer-events-none disabled:opacity-50"
                        >
                          <Trash2 className="w-4 h-4" />
                        </button>
                      </td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          )}
        </div>
      </Card>
    </div>
  );
}
