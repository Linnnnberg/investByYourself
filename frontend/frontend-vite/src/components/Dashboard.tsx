import { useState, useEffect } from "react";
import { PortfolioOverview } from "./PortfolioOverview";
import { WatchlistTable } from "./WatchlistTable";
import { QuickActions } from "./QuickActions";
import { figmaTokens } from "../styles/figma-tokens";
import { apiService } from "../services/api";
import { PortfolioData, Stock } from "../types";
import { NAVIGATION_TABS, QUICK_ACTIONS } from "../constants";

export function Dashboard() {
  const [portfolioData, setPortfolioData] = useState<PortfolioData>({
    totalValue: 41902.5,
    totalReturn: 7382.9,
    returnPercentage: 21.4,
    holdings: 3
  });

  const [watchlistStocks, setWatchlistStocks] = useState<Stock[]>([
    {
      symbol: "AAPL",
      name: "Apple Inc.",
      price: 150.25,
      change: 2.15,
      changePercentage: 1.45,
      marketCap: "$2500.0B",
      peRatio: 25.5
    },
    {
      symbol: "MSFT",
      name: "Microsoft Corporation",
      price: 320.80,
      change: -4.20,
      changePercentage: -1.29,
      marketCap: "$2400.0B",
      peRatio: 30.2
    },
    {
      symbol: "GOOGL",
      name: "Alphabet Inc.",
      price: 140.50,
      change: 1.50,
      changePercentage: 1.08,
      marketCap: "$1800.0B",
      peRatio: 22.8
    }
  ]);

  const [loading, setLoading] = useState(true);

  useEffect(() => {
    loadData();
  }, []);

  const loadData = async () => {
    try {
      // Load portfolio data from backend
      const portfolioResponse = await apiService.getPortfolio();
      if (portfolioResponse.success && portfolioResponse.data) {
        setPortfolioData(portfolioResponse.data);
      }

      // Load watchlist data from backend
      const watchlistResponse = await apiService.getWatchlist();
      if (watchlistResponse.success && watchlistResponse.data) {
        setWatchlistStocks(watchlistResponse.data);
      }
    } catch (error) {
      console.error("Error loading data:", error);
    } finally {
      setLoading(false);
    }
  };

  const handleBuy = async (symbol: string) => {
    try {
      const response = await apiService.addToPortfolio(symbol);
      if (response.success) {
        console.log(`Added ${symbol} to portfolio`);
        loadData(); // Refresh data
      }
    } catch (error) {
      console.error("Error adding to portfolio:", error);
    }
  };

  const handleRemoveFromWatchlist = async (symbol: string) => {
    try {
      const response = await apiService.removeFromWatchlist(symbol);
      if (response.success) {
        setWatchlistStocks(prev => prev.filter(stock => stock.symbol !== symbol));
      }
    } catch (error) {
      console.error("Error removing from watchlist:", error);
    }
  };

  const handleQuickAction = (action: string) => {
    console.log(`Quick action: ${action}`);
    // Handle different quick actions
    switch (action) {
      case 'search':
        // Implement search functionality
        break;
      case 'import':
        // Implement import functionality
        break;
      case 'screener':
        // Implement screener functionality
        break;
      case 'report':
        // Implement report functionality
        break;
    }
  };

  if (loading) {
    return (
      <div
        className="flex items-center justify-center h-64"
        style={{
          backgroundColor: figmaTokens.colors.background.secondary,
          fontFamily: figmaTokens.typography.fontFamily.primary
        }}
      >
        <div
          className="animate-pulse"
          style={{ color: figmaTokens.colors.text.secondary }}
        >
          Loading...
        </div>
      </div>
    );
  }

  return (
    <div
      className="p-6 space-y-8"
      style={{
        backgroundColor: figmaTokens.colors.background.primary,
        fontFamily: figmaTokens.typography.fontFamily.primary,
        minHeight: '100vh'
      }}
    >
      {/* Header Section with Figma Styling */}
      <div
        className="mb-8"
        style={{
          padding: figmaTokens.spacing.lg,
          backgroundColor: figmaTokens.colors.surface.elevated,
          borderRadius: figmaTokens.borderRadius.lg,
          border: `1px solid ${figmaTokens.colors.border.default}`,
          boxShadow: figmaTokens.shadows.sm
        }}
      >
        <h1
          className="text-2xl font-semibold mb-2"
          style={{
            color: figmaTokens.colors.text.primary,
            fontSize: figmaTokens.typography.fontSize['2xl'],
            fontWeight: figmaTokens.typography.fontWeight.semibold,
            lineHeight: figmaTokens.typography.lineHeight.tight
          }}
        >
          Investment Dashboard
        </h1>
        <p
          className="text-muted-foreground"
          style={{
            color: figmaTokens.colors.text.secondary,
            fontSize: figmaTokens.typography.fontSize.lg,
            lineHeight: figmaTokens.typography.lineHeight.normal
          }}
        >
          Welcome back! Here's your personalized investment overview.
        </p>
      </div>

      {/* Portfolio Overview with Figma Styling */}
      <div
        style={{
          backgroundColor: figmaTokens.colors.surface.default,
          borderRadius: figmaTokens.borderRadius.xl,
          border: `1px solid ${figmaTokens.colors.border.elevated}`,
          boxShadow: figmaTokens.shadows.md,
          padding: figmaTokens.spacing.xl
        }}
      >
        <PortfolioOverview data={portfolioData} />
      </div>

      {/* Watchlist Table with Figma Styling */}
      <div
        style={{
          backgroundColor: figmaTokens.colors.surface.default,
          borderRadius: figmaTokens.borderRadius.xl,
          border: `1px solid ${figmaTokens.colors.border.elevated}`,
          boxShadow: figmaTokens.shadows.md,
          padding: figmaTokens.spacing.xl
        }}
      >
        <WatchlistTable
          stocks={watchlistStocks}
          onBuy={handleBuy}
          onRemove={handleRemoveFromWatchlist}
        />
      </div>

      {/* Quick Actions with Figma Styling */}
      <div
        style={{
          backgroundColor: figmaTokens.colors.surface.default,
          borderRadius: figmaTokens.borderRadius.xl,
          border: `1px solid ${figmaTokens.colors.border.elevated}`,
          boxShadow: figmaTokens.shadows.md,
          padding: figmaTokens.spacing.xl
        }}
      >
        <QuickActions onAction={handleQuickAction} />
      </div>
    </div>
  );
}
