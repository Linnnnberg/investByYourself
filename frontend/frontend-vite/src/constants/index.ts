/**
 * Application constants for investByYourself Platform
 */

// ===== APP CONFIGURATION =====
export const APP_CONFIG = {
  name: 'investByYourself',
  version: '1.0.0',
  description: 'Professional investment platform for individual investors',
  author: 'investByYourself Team',
} as const;

// ===== API CONFIGURATION =====
export const API_CONFIG = {
  baseURL: 'https://ztxlcatckspsdtkepmwy.supabase.co/functions/v1/make-server-9c463a03',
  timeout: 30000, // 30 seconds
  retryAttempts: 3,
} as const;

// ===== SUPABASE CONFIGURATION =====
export const SUPABASE_CONFIG = {
  projectId: import.meta.env.VITE_SUPABASE_PROJECT_ID || 'ztxlcatckspsdtkepmwy',
  url: import.meta.env.VITE_SUPABASE_URL || 'https://ztxlcatckspsdtkepmwy.supabase.co',
  anonKey: import.meta.env.VITE_SUPABASE_ANON_KEY || '',
} as const;

// ===== NAVIGATION =====
export const NAVIGATION_TABS = [
  { id: 'dashboard', label: 'Dashboard', icon: '📊' },
  { id: 'market-insights', label: 'Market Insights', icon: '📈' },
  { id: 'portfolio', label: 'Portfolio', icon: '💼' },
  { id: 'analysis', label: 'Analysis', icon: '🔍' },
  { id: 'reports', label: 'Reports', icon: '📋' },
] as const;

// ===== TIME FRAMES =====
export const TIME_FRAMES = [
  { value: '1d', label: '1 Day' },
  { value: '1w', label: '1 Week' },
  { value: '1m', label: '1 Month' },
  { value: '3m', label: '3 Months' },
  { value: '6m', label: '6 Months' },
  { value: '1y', label: '1 Year' },
  { value: '5y', label: '5 Years' },
  { value: 'all', label: 'All Time' },
] as const;

// ===== CURRENCIES =====
export const CURRENCIES = [
  { code: 'USD', symbol: '$', name: 'US Dollar' },
  { code: 'EUR', symbol: '€', name: 'Euro' },
  { code: 'GBP', symbol: '£', name: 'British Pound' },
  { code: 'JPY', symbol: '¥', name: 'Japanese Yen' },
  { code: 'CAD', symbol: 'C$', name: 'Canadian Dollar' },
  { code: 'AUD', symbol: 'A$', name: 'Australian Dollar' },
  { code: 'CHF', symbol: 'CHF', name: 'Swiss Franc' },
  { code: 'CNY', symbol: '¥', name: 'Chinese Yuan' },
] as const;

// ===== MARKET SECTORS =====
export const MARKET_SECTORS = [
  'Technology',
  'Healthcare',
  'Financial Services',
  'Consumer Discretionary',
  'Consumer Staples',
  'Energy',
  'Industrials',
  'Materials',
  'Real Estate',
  'Utilities',
  'Communication Services',
] as const;

// ===== QUICK ACTIONS =====
export const QUICK_ACTIONS = [
  {
    id: 'search',
    label: 'Search Stocks',
    description: 'Find stocks by symbol or company name',
    icon: '🔍',
  },
  {
    id: 'import',
    label: 'Import Portfolio',
    description: 'Import your existing portfolio',
    icon: '📥',
  },
  {
    id: 'screener',
    label: 'Stock Screener',
    description: 'Filter stocks by criteria',
    icon: '🔍',
  },
  {
    id: 'report',
    label: 'Generate Report',
    description: 'Create performance reports',
    icon: '📊',
  },
] as const;

// ===== ERROR MESSAGES =====
export const ERROR_MESSAGES = {
  NETWORK_ERROR: 'Network error. Please check your connection.',
  UNAUTHORIZED: 'You are not authorized to perform this action.',
  NOT_FOUND: 'The requested resource was not found.',
  SERVER_ERROR: 'Server error. Please try again later.',
  VALIDATION_ERROR: 'Please check your input and try again.',
  TIMEOUT_ERROR: 'Request timed out. Please try again.',
} as const;

// ===== SUCCESS MESSAGES =====
export const SUCCESS_MESSAGES = {
  PORTFOLIO_UPDATED: 'Portfolio updated successfully.',
  WATCHLIST_UPDATED: 'Watchlist updated successfully.',
  SETTINGS_SAVED: 'Settings saved successfully.',
  DATA_REFRESHED: 'Data refreshed successfully.',
} as const;

// ===== LOCAL STORAGE KEYS =====
export const STORAGE_KEYS = {
  USER_PREFERENCES: 'user_preferences',
  THEME: 'theme',
  CURRENCY: 'currency',
  TIMEZONE: 'timezone',
  RECENT_SEARCHES: 'recent_searches',
  WATCHLIST: 'watchlist',
  PORTFOLIO: 'portfolio',
} as const;

// ===== BREAKPOINTS =====
export const BREAKPOINTS = {
  mobile: 320,
  tablet: 768,
  desktop: 1024,
  wide: 1280,
  ultra: 1536,
} as const;

// ===== ANIMATION DURATIONS =====
export const ANIMATION_DURATIONS = {
  fast: 150,
  normal: 250,
  slow: 350,
  verySlow: 500,
} as const;

// ===== Z-INDEX SCALE =====
export const Z_INDEX = {
  base: 0,
  dropdown: 1000,
  sticky: 1020,
  fixed: 1030,
  modal: 1040,
  popover: 1050,
  tooltip: 1060,
  toast: 1070,
} as const;
