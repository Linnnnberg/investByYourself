import { useState, useEffect } from "react";
import { MarketIndices } from "./MarketIndices";
import { MacroeconomicIndicators } from "./MacroeconomicIndicators";
import { SectorPerformance } from "./SectorPerformance";
import { MarketNews } from "./MarketNews";
import { WatchlistMovers } from "./WatchlistMovers";
import { projectId, publicAnonKey } from "../utils/supabase/info";

interface MarketIndex {
  name: string;
  symbol: string;
  value: number;
  change: number;
  changePercentage: number;
  region: string;
}

interface MacroIndicator {
  name: string;
  value: string;
  change: number;
  period: string;
  description: string;
}

interface Sector {
  name: string;
  symbol: string;
  price: number;
  change: number;
  changePercentage: number;
}

interface NewsItem {
  title: string;
  summary: string;
  source: string;
  publishedAt: string;
  category: string;
  url?: string;
}

interface WatchlistMover {
  symbol: string;
  name: string;
  price: number;
  change: number;
  changePercentage: number;
  volume: string;
}

interface MarketInsightsData {
  marketIndices: MarketIndex[];
  macroIndicators: MacroIndicator[];
  sectors: Sector[];
  news: NewsItem[];
  watchlistGainers: WatchlistMover[];
  watchlistLosers: WatchlistMover[];
}

export function MarketInsights() {
  const [data, setData] = useState<MarketInsightsData>({
    marketIndices: [],
    macroIndicators: [],
    sectors: [],
    news: [],
    watchlistGainers: [],
    watchlistLosers: []
  });
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    loadMarketInsights();
  }, []);

  const loadMarketInsights = async () => {
    try {
      const response = await fetch(
        `https://${projectId}.supabase.co/functions/v1/make-server-9c463a03/market-insights`,
        {
          headers: {
            'Authorization': `Bearer ${publicAnonKey}`,
            'Content-Type': 'application/json',
          },
        }
      );

      if (response.ok) {
        const insights = await response.json();
        setData(insights);
      } else {
        console.error("Failed to load market insights:", await response.text());
      }
    } catch (error) {
      console.error("Error loading market insights:", error);
    } finally {
      setLoading(false);
    }
  };

  if (loading) {
    return (
      <div className="p-6">
        <div className="flex items-center justify-center h-64">
          <div className="animate-pulse">Loading market insights...</div>
        </div>
      </div>
    );
  }

  return (
    <div className="p-6 space-y-6">
      <div>
        <h1 className="text-2xl font-semibold mb-2">Market Insights</h1>
        <p className="text-muted-foreground">Stay informed with the latest market data, trends, and news.</p>
      </div>

      <MarketIndices indices={data.marketIndices} />

      <MacroeconomicIndicators indicators={data.macroIndicators} />

      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        <SectorPerformance sectors={data.sectors} />
        <MarketNews news={data.news} />
      </div>

      <WatchlistMovers
        gainers={data.watchlistGainers}
        losers={data.watchlistLosers}
      />
    </div>
  );
}
