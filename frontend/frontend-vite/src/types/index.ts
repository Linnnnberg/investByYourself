/**
 * Central TypeScript types for investByYourself Platform
 */

// ===== CORE ENTITIES =====

export interface Stock {
  symbol: string;
  name: string;
  price: number;
  change: number;
  changePercentage: number;
  marketCap: string;
  peRatio: number;
}

export interface PortfolioData {
  totalValue: number;
  totalReturn: number;
  returnPercentage: number;
  holdings: number;
}

export interface PortfolioHolding {
  symbol: string;
  shares: number;
  avgPrice: number;
  currentPrice: number;
  totalValue: number;
  totalReturn: number;
  returnPercentage: number;
}

export interface WatchlistItem {
  symbol: string;
  name: string;
  price: number;
  change: number;
  changePercentage: number;
  addedAt: Date;
}

// ===== MARKET DATA =====

export interface MarketIndex {
  name: string;
  symbol: string;
  value: number;
  change: number;
  changePercentage: number;
}

export interface SectorPerformance {
  sector: string;
  performance: number;
  change: number;
  topStocks: string[];
}

export interface MacroeconomicIndicator {
  name: string;
  value: number;
  unit: string;
  change: number;
  trend: 'up' | 'down' | 'stable';
}

export interface MarketNews {
  id: string;
  title: string;
  summary: string;
  source: string;
  publishedAt: Date;
  impact: 'high' | 'medium' | 'low';
}

// ===== UI COMPONENTS =====

export interface TabItem {
  id: string;
  label: string;
  icon?: string;
  disabled?: boolean;
}

export interface QuickAction {
  id: string;
  label: string;
  description: string;
  icon: string;
  action: () => void;
}

// ===== API RESPONSES =====

export interface ApiResponse<T> {
  data: T;
  success: boolean;
  message?: string;
  error?: string;
}

export interface PaginatedResponse<T> {
  data: T[];
  total: number;
  page: number;
  limit: number;
  hasMore: boolean;
}

// ===== FORM TYPES =====

export interface PortfolioFormData {
  name: string;
  description?: string;
  isPublic: boolean;
}

export interface TradeFormData {
  symbol: string;
  action: 'buy' | 'sell';
  shares: number;
  price: number;
  portfolioId: string;
}

// ===== CHART DATA =====

export interface ChartDataPoint {
  date: string;
  value: number;
  volume?: number;
}

export interface ChartSeries {
  name: string;
  data: ChartDataPoint[];
  color?: string;
}

// ===== USER & AUTH =====

export interface User {
  id: string;
  email: string;
  name: string;
  avatar?: string;
  preferences: UserPreferences;
}

export interface UserPreferences {
  theme: 'light' | 'dark' | 'system';
  currency: string;
  timezone: string;
  notifications: NotificationSettings;
}

export interface NotificationSettings {
  email: boolean;
  push: boolean;
  sms: boolean;
  frequency: 'immediate' | 'daily' | 'weekly';
}

// ===== UTILITY TYPES =====

export type LoadingState = 'idle' | 'loading' | 'success' | 'error';

export type SortDirection = 'asc' | 'desc';

export type FilterOperator = 'eq' | 'gt' | 'lt' | 'gte' | 'lte' | 'contains' | 'in';

export interface FilterCondition {
  field: string;
  operator: FilterOperator;
  value: any;
}

export interface SortCondition {
  field: string;
  direction: SortDirection;
}

// ===== ENUMS =====

export enum OrderType {
  MARKET = 'market',
  LIMIT = 'limit',
  STOP = 'stop',
  STOP_LIMIT = 'stop_limit'
}

export enum OrderStatus {
  PENDING = 'pending',
  FILLED = 'filled',
  CANCELLED = 'cancelled',
  REJECTED = 'rejected'
}

export enum TimeFrame {
  '1D' = '1d',
  '1W' = '1w',
  '1M' = '1m',
  '3M' = '3m',
  '6M' = '6m',
  '1Y' = '1y',
  '5Y' = '5y',
  'ALL' = 'all'
}
