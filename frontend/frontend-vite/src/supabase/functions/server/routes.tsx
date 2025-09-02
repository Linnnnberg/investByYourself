import { Hono } from "npm:hono";
import * as kv from "./kv_store.tsx";

export const portfolioRoutes = new Hono();
export const watchlistRoutes = new Hono();
export const marketInsightsRoutes = new Hono();
export const positionRoutes = new Hono();

// Portfolio routes
portfolioRoutes.get("/", async (c) => {
  try {
    const portfolio = await kv.get("portfolio");
    if (!portfolio) {
      // Return default portfolio data
      const defaultPortfolio = {
        totalValue: 41902.5,
        totalReturn: 7382.9,
        returnPercentage: 21.4,
        holdings: 3
      };
      await kv.set("portfolio", defaultPortfolio);
      return c.json(defaultPortfolio);
    }
    return c.json(portfolio);
  } catch (error) {
    console.error("Error getting portfolio:", error);
    return c.json({ error: "Failed to get portfolio" }, 500);
  }
});

portfolioRoutes.post("/add", async (c) => {
  try {
    const { symbol } = await c.req.json();
    console.log(`Adding ${symbol} to portfolio`);

    // Update portfolio holdings
    const portfolio = await kv.get("portfolio") || {
      totalValue: 41902.5,
      totalReturn: 7382.9,
      returnPercentage: 21.4,
      holdings: 3
    };

    portfolio.holdings += 1;
    await kv.set("portfolio", portfolio);

    return c.json({ success: true });
  } catch (error) {
    console.error("Error adding to portfolio:", error);
    return c.json({ error: "Failed to add to portfolio" }, 500);
  }
});

// Watchlist routes
watchlistRoutes.get("/", async (c) => {
  try {
    const watchlist = await kv.get("watchlist");
    if (!watchlist) {
      // Return default watchlist data
      const defaultWatchlist = [
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
      ];
      await kv.set("watchlist", defaultWatchlist);
      return c.json(defaultWatchlist);
    }
    return c.json(watchlist);
  } catch (error) {
    console.error("Error getting watchlist:", error);
    return c.json({ error: "Failed to get watchlist" }, 500);
  }
});

watchlistRoutes.delete("/remove", async (c) => {
  try {
    const { symbol } = await c.req.json();
    console.log(`Removing ${symbol} from watchlist`);

    const watchlist = await kv.get("watchlist") || [];
    const updatedWatchlist = watchlist.filter((stock: any) => stock.symbol !== symbol);

    await kv.set("watchlist", updatedWatchlist);

    return c.json({ success: true });
  } catch (error) {
    console.error("Error removing from watchlist:", error);
    return c.json({ error: "Failed to remove from watchlist" }, 500);
  }
});

// Market Insights routes
marketInsightsRoutes.get("/", async (c) => {
  try {
    let marketData = await kv.get("market_insights");

    // If marketData exists but doesn't have marketIndices, update it
    if (marketData && !marketData.marketIndices) {
      marketData = null; // Force regeneration with new structure
    }

    if (!marketData) {
      // Return default market insights data
      const defaultMarketInsights = {
        marketIndices: [
          {
            name: "S&P 500",
            symbol: "SPX",
            value: 4783.35,
            change: 12.45,
            changePercentage: 0.26,
            region: "US"
          },
          {
            name: "NASDAQ Composite",
            symbol: "IXIC",
            value: 15234.78,
            change: -23.12,
            changePercentage: -0.15,
            region: "US"
          },
          {
            name: "DAX",
            symbol: "DAX",
            value: 16890.45,
            change: 89.23,
            changePercentage: 0.53,
            region: "Germany"
          },
          {
            name: "Nikkei 225",
            symbol: "N225",
            value: 33486.89,
            change: -125.67,
            changePercentage: -0.37,
            region: "Japan"
          },
          {
            name: "Hang Seng",
            symbol: "HSI",
            value: 16234.52,
            change: 78.45,
            changePercentage: 0.49,
            region: "Hong Kong"
          },
          {
            name: "CSI 300",
            symbol: "000300",
            value: 3456.78,
            change: -12.34,
            changePercentage: -0.36,
            region: "China"
          }
        ],
        macroIndicators: [
          {
            name: "NFP",
            value: "199K",
            change: -0.3,
            period: "Nov 2024",
            description: "Non-Farm Payrolls"
          },
          {
            name: "CPI",
            value: "2.6%",
            change: 0.2,
            period: "Oct 2024",
            description: "Consumer Price Index"
          },
          {
            name: "PPI",
            value: "2.4%",
            change: 0.1,
            period: "Oct 2024",
            description: "Producer Price Index"
          },
          {
            name: "GDP",
            value: "2.8%",
            change: 0.3,
            period: "Q3 2024",
            description: "Gross Domestic Product"
          }
        ],
        sectors: [
          {
            name: "Technology",
            symbol: "XLK",
            price: 231.45,
            change: 3.21,
            changePercentage: 1.41
          },
          {
            name: "Financials",
            symbol: "XLF",
            price: 43.89,
            change: -0.67,
            changePercentage: -1.50
          },
          {
            name: "Healthcare",
            symbol: "XLV",
            price: 157.23,
            change: 1.85,
            changePercentage: 1.19
          },
          {
            name: "Energy",
            symbol: "XLE",
            price: 95.67,
            change: -2.14,
            changePercentage: -2.19
          },
          {
            name: "Consumer Discretionary",
            symbol: "XLY",
            price: 178.91,
            change: 2.45,
            changePercentage: 1.39
          }
        ],
        news: [
          {
            title: "Federal Reserve Holds Rates Steady Amid Economic Uncertainty",
            summary: "The Fed maintained the federal funds rate at 5.25%-5.50% as policymakers assess inflation trends and labor market conditions.",
            source: "Reuters",
            publishedAt: "2024-11-07T14:30:00Z",
            category: "Economic",
            url: "https://example.com/news1"
          },
          {
            title: "Tech Earnings Beat Expectations as AI Spending Continues",
            summary: "Major technology companies reported strong quarterly results driven by artificial intelligence investments and cloud computing growth.",
            source: "CNBC",
            publishedAt: "2024-11-07T12:15:00Z",
            category: "Earnings",
            url: "https://example.com/news2"
          },
          {
            title: "Oil Prices Decline on Demand Concerns",
            summary: "Crude oil futures fell 2% amid concerns about global economic growth and weakening demand from major economies.",
            source: "Bloomberg",
            publishedAt: "2024-11-07T10:45:00Z",
            category: "Market",
            url: "https://example.com/news3"
          },
          {
            title: "Apple Announces New Product Line Expected to Drive Q1 Sales",
            summary: "The tech giant unveiled its latest product innovations, with analysts expecting significant revenue impact in the upcoming quarter.",
            source: "MarketWatch",
            publishedAt: "2024-11-07T09:20:00Z",
            category: "Company",
            url: "https://example.com/news4"
          }
        ],
        watchlistGainers: [
          {
            symbol: "AAPL",
            name: "Apple Inc.",
            price: 152.40,
            change: 2.15,
            changePercentage: 1.43,
            volume: "2.1M"
          },
          {
            symbol: "GOOGL",
            name: "Alphabet Inc.",
            price: 142.00,
            change: 1.50,
            changePercentage: 1.07,
            volume: "1.8M"
          }
        ],
        watchlistLosers: [
          {
            symbol: "MSFT",
            name: "Microsoft Corporation",
            price: 316.60,
            change: -4.20,
            changePercentage: -1.31,
            volume: "1.9M"
          }
        ]
      };
      await kv.set("market_insights", defaultMarketInsights);
      return c.json(defaultMarketInsights);
    }
    return c.json(marketData);
  } catch (error) {
    console.error("Error getting market insights:", error);
    return c.json({ error: "Failed to get market insights" }, 500);
  }
});

// Development route to clear market insights cache
marketInsightsRoutes.delete("/clear-cache", async (c) => {
  try {
    await kv.del("market_insights");
    return c.json({ success: true, message: "Market insights cache cleared" });
  } catch (error) {
    console.error("Error clearing market insights cache:", error);
    return c.json({ error: "Failed to clear cache" }, 500);
  }
});

// Position routes
positionRoutes.get("/", async (c) => {
  try {
    const positions = await kv.get("positions");
    if (!positions) {
      return c.json([]);
    }
    return c.json(positions);
  } catch (error) {
    console.error("Error getting positions:", error);
    return c.json({ error: "Failed to get positions" }, 500);
  }
});

positionRoutes.post("/", async (c) => {
  try {
    const { symbol, name, averageCost, units } = await c.req.json();

    if (!symbol || !averageCost || !units) {
      return c.json({ error: "Symbol, average cost, and units are required" }, 400);
    }

    const positions = (await kv.get("positions")) || [];

    // Simulate getting current price (in a real app, this would fetch from a stock API)
    const currentPrice = await getCurrentPrice(symbol);

    const totalCost = averageCost * units;
    const totalValue = currentPrice * units;
    const gainLoss = totalValue - totalCost;
    const gainLossPercentage = totalCost > 0 ? (gainLoss / totalCost) * 100 : 0;

    const newPosition = {
      id: crypto.randomUUID(),
      symbol,
      name: name || symbol,
      currentPrice,
      averageCost,
      units,
      totalValue,
      totalCost,
      gainLoss,
      gainLossPercentage,
      createdAt: new Date().toISOString()
    };

    positions.push(newPosition);
    await kv.set("positions", positions);

    return c.json(newPosition);
  } catch (error) {
    console.error("Error adding position:", error);
    return c.json({ error: "Failed to add position" }, 500);
  }
});

positionRoutes.delete("/:id", async (c) => {
  try {
    const id = c.req.param("id");
    const positions = (await kv.get("positions")) || [];

    const filteredPositions = positions.filter((pos: any) => pos.id !== id);
    await kv.set("positions", filteredPositions);

    return c.json({ success: true });
  } catch (error) {
    console.error("Error removing position:", error);
    return c.json({ error: "Failed to remove position" }, 500);
  }
});

// Helper function to get current stock price (simulated)
async function getCurrentPrice(symbol: string): Promise<number> {
  // In a real app, you would fetch from a stock API like Alpha Vantage or Yahoo Finance
  // For now, we'll return simulated prices
  const mockPrices: Record<string, number> = {
    AAPL: 152.40,
    MSFT: 316.60,
    GOOGL: 142.00,
    TSLA: 248.50,
    AMZN: 145.75,
    NVDA: 478.30,
    META: 338.20,
    NFLX: 445.80,
    DIS: 91.25,
    PYPL: 58.90
  };

  // Return mock price or generate a random price between $50-$500
  return mockPrices[symbol] || Math.random() * 450 + 50;
}
