import { ApiResponse, PaginatedResponse } from '../types';

/**
 * Centralized API service for investByYourself Platform
 */
class ApiService {
  private baseURL: string;
  private projectId: string;
  private anonKey: string;

  constructor() {
    this.projectId = import.meta.env.VITE_SUPABASE_PROJECT_ID || "ztxlcatckspsdtkepmwy";
    this.anonKey = import.meta.env.VITE_SUPABASE_ANON_KEY || "";
    this.baseURL = `https://${this.projectId}.supabase.co/functions/v1/make-server-9c463a03`;
  }

  private async request<T>(
    endpoint: string,
    options: RequestInit = {}
  ): Promise<ApiResponse<T>> {
    const url = `${this.baseURL}${endpoint}`;

    const defaultOptions: RequestInit = {
      headers: {
        'Authorization': `Bearer ${this.anonKey}`,
        'Content-Type': 'application/json',
        ...options.headers,
      },
      ...options,
    };

    try {
      const response = await fetch(url, defaultOptions);

      if (!response.ok) {
        throw new Error(`HTTP error! status: ${response.status}`);
      }

      const data = await response.json();
      return {
        data,
        success: true,
        message: 'Request successful',
      };
    } catch (error) {
      console.error(`API request failed for ${endpoint}:`, error);
      return {
        data: null as T,
        success: false,
        error: error instanceof Error ? error.message : 'Unknown error',
      };
    }
  }

  // Portfolio endpoints
  async getPortfolio(): Promise<ApiResponse<any>> {
    return this.request('/portfolio');
  }

  async addToPortfolio(symbol: string): Promise<ApiResponse<any>> {
    return this.request('/portfolio/add', {
      method: 'POST',
      body: JSON.stringify({ symbol }),
    });
  }

  async removeFromPortfolio(symbol: string): Promise<ApiResponse<any>> {
    return this.request('/portfolio/remove', {
      method: 'DELETE',
      body: JSON.stringify({ symbol }),
    });
  }

  // Watchlist endpoints
  async getWatchlist(): Promise<ApiResponse<any>> {
    return this.request('/watchlist');
  }

  async addToWatchlist(symbol: string): Promise<ApiResponse<any>> {
    return this.request('/watchlist/add', {
      method: 'POST',
      body: JSON.stringify({ symbol }),
    });
  }

  async removeFromWatchlist(symbol: string): Promise<ApiResponse<any>> {
    return this.request('/watchlist/remove', {
      method: 'DELETE',
      body: JSON.stringify({ symbol }),
    });
  }

  // Market data endpoints
  async getMarketData(): Promise<ApiResponse<any>> {
    return this.request('/market-data');
  }

  async getStockQuote(symbol: string): Promise<ApiResponse<any>> {
    return this.request(`/stock-quote/${symbol}`);
  }

  // News endpoints
  async getMarketNews(): Promise<ApiResponse<any>> {
    return this.request('/news');
  }

  // Analysis endpoints
  async getTechnicalAnalysis(symbol: string, timeframe: string): Promise<ApiResponse<any>> {
    return this.request(`/technical-analysis/${symbol}?timeframe=${timeframe}`);
  }

  async getFundamentalAnalysis(symbol: string): Promise<ApiResponse<any>> {
    return this.request(`/fundamental-analysis/${symbol}`);
  }
}

// Export singleton instance
export const apiService = new ApiService();
export default apiService;
