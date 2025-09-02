/**
 * Figma Design Tokens for investByYourself Platform
 * Extract values from your Figma design and update this file
 */

export const figmaTokens = {
  // Color Palette - Update with your Figma colors
  colors: {
    // Primary brand colors
    primary: {
      50: '#eff6ff',   // Replace with your Figma primary-50
      100: '#dbeafe',  // Replace with your Figma primary-100
      200: '#bfdbfe',  // Replace with your Figma primary-200
      300: '#93c5fd',  // Replace with your Figma primary-300
      400: '#60a5fa',  // Replace with your Figma primary-400
      500: '#3b82f6',  // Replace with your Figma primary-500
      600: '#2563eb',  // Replace with your Figma primary-600
      700: '#1d4ed8',  // Replace with your Figma primary-700
      800: '#1e40af',  // Replace with your Figma primary-800
      900: '#1e3a8a',  // Replace with your Figma primary-900
    },

    // Secondary colors
    secondary: {
      50: '#f8fafc',   // Replace with your Figma secondary-50
      100: '#f1f5f9',  // Replace with your Figma secondary-100
      200: '#e2e8f0',  // Replace with your Figma secondary-200
      300: '#cbd5e1',  // Replace with your Figma secondary-300
      400: '#94a3b8',  // Replace with your Figma secondary-400
      500: '#64748b',  // Replace with your Figma secondary-500
      600: '#475569',  // Replace with your Figma secondary-600
      700: '#334155',  // Replace with your Figma secondary-700
      800: '#1e293b',  // Replace with your Figma secondary-800
      900: '#0f172a',  // Replace with your Figma secondary-900
    },

    // Semantic colors
    success: {
      50: '#f0fdf4',   // Replace with your Figma success colors
      500: '#22c55e',
      600: '#16a34a',
      700: '#15803d',
    },

    warning: {
      50: '#fffbeb',   // Replace with your Figma warning colors
      500: '#f59e0b',
      600: '#d97706',
      700: '#b45309',
    },

    danger: {
      50: '#fef2f2',   // Replace with your Figma danger colors
      500: '#ef4444',
      600: '#dc2626',
      700: '#b91c1c',
    },

    // Financial colors
    financial: {
      profit: '#10b981',    // Green for gains
      loss: '#ef4444',      // Red for losses
      neutral: '#6b7280',   // Gray for neutral
      info: '#3b82f6',      // Blue for information
      alert: '#f59e0b',     // Yellow for alerts
    },

    // Surface colors
    surface: {
      default: '#ffffff',   // Replace with your Figma surface color
      elevated: '#f8fafc',  // Replace with your Figma elevated surface
      outlined: '#ffffff',  // Replace with your Figma outlined surface
      interactive: '#f1f5f9', // Replace with your Figma interactive surface
    },

    // Text colors
    text: {
      primary: '#111827',   // Replace with your Figma primary text
      secondary: '#6b7280', // Replace with your Figma secondary text
      tertiary: '#9ca3af',  // Replace with your Figma tertiary text
      inverse: '#ffffff',   // Replace with your Figma inverse text
    },

    // Border colors
    border: {
      default: '#e5e7eb',   // Replace with your Figma default border
      elevated: '#d1d5db',  // Replace with your Figma elevated border
      outlined: '#3b82f6',  // Replace with your Figma outlined border
      interactive: '#3b82f6', // Replace with your Figma interactive border
    },

    // Background colors
    background: {
      primary: '#ffffff',   // Replace with your Figma primary background
      secondary: '#f9fafb', // Replace with your Figma secondary background
      tertiary: '#f3f4f6', // Replace with your Figma tertiary background
    },
  },

  // Spacing Scale - Update with your Figma spacing
  spacing: {
    xs: '0.25rem',    // 4px - Replace with your Figma xs spacing
    sm: '0.5rem',     // 8px - Replace with your Figma sm spacing
    md: '1rem',       // 16px - Replace with your Figma md spacing
    lg: '1.5rem',     // 24px - Replace with your Figma lg spacing
    xl: '2rem',       // 32px - Replace with your Figma xl spacing
    '2xl': '3rem',    // 48px - Replace with your Figma 2xl spacing
    '3xl': '4rem',    // 64px - Replace with your Figma 3xl spacing
    '4xl': '6rem',    // 96px - Replace with your Figma 4xl spacing
    '5xl': '8rem',    // 128px - Replace with your Figma 5xl spacing
    '6xl': '12rem',   // 192px - Replace with your Figma 6xl spacing
  },

  // Typography - Update with your Figma typography
  typography: {
    fontFamily: {
      primary: 'Inter, system-ui, sans-serif',    // Replace with your Figma font
      secondary: 'JetBrains Mono, monospace',     // Replace with your Figma secondary font
    },

    fontSize: {
      xs: '0.75rem',      // 12px - Replace with your Figma xs size
      sm: '0.875rem',     // 14px - Replace with your Figma sm size
      base: '1rem',       // 16px - Replace with your Figma base size
      lg: '1.125rem',     // 18px - Replace with your Figma lg size
      xl: '1.25rem',      // 20px - Replace with your Figma xl size
      '2xl': '1.5rem',    // 24px - Replace with your Figma 2xl size
      '3xl': '1.875rem',  // 30px - Replace with your Figma 3xl size
      '4xl': '2.25rem',   // 36px - Replace with your Figma 4xl size
      '5xl': '3rem',      // 48px - Replace with your Figma 5xl size
      '6xl': '3.75rem',   // 60px - Replace with your Figma 6xl size
      '7xl': '4.5rem',    // 72px - Replace with your Figma 7xl size
      '8xl': '6rem',      // 96px - Replace with your Figma 8xl size
      '9xl': '8rem',      // 128px - Replace with your Figma 9xl size
    },

    fontWeight: {
      thin: '100',         // Replace with your Figma weights
      extralight: '200',
      light: '300',
      normal: '400',
      medium: '500',
      semibold: '600',
      bold: '700',
      extrabold: '800',
      black: '900',
    },

    lineHeight: {
      none: '1',           // Replace with your Figma line heights
      tight: '1.25',
      snug: '1.375',
      normal: '1.5',
      relaxed: '1.625',
      loose: '2',
    },

    letterSpacing: {
      tighter: '-0.05em',  // Replace with your Figma letter spacing
      tight: '-0.025em',
      normal: '0em',
      wide: '0.025em',
      wider: '0.05em',
      widest: '0.1em',
    },
  },

  // Border Radius - Update with your Figma border radius
  borderRadius: {
    none: '0',             // Replace with your Figma values
    sm: '0.125rem',        // 2px
    md: '0.375rem',        // 6px
    lg: '0.5rem',          // 8px
    xl: '0.75rem',         // 12px
    '2xl': '1rem',         // 16px
    '3xl': '1.5rem',       // 24px
    full: '9999px',
  },

  // Shadows - Update with your Figma shadows
  shadows: {
    none: 'none',          // Replace with your Figma shadow values
    sm: '0 1px 2px 0 rgba(0, 0, 0, 0.05)',
    md: '0 4px 6px -1px rgba(0, 0, 0, 0.1), 0 2px 4px -1px rgba(0, 0, 0, 0.06)',
    lg: '0 10px 15px -3px rgba(0, 0, 0, 0.1), 0 4px 6px -2px rgba(0, 0, 0, 0.05)',
    xl: '0 20px 25px -5px rgba(0, 0, 0, 0.1), 0 10px 10px -5px rgba(0, 0, 0, 0.04)',
    '2xl': '0 25px 50px -12px rgba(0, 0, 0, 0.25)',
    inner: 'inset 0 2px 4px 0 rgba(0, 0, 0, 0.06)',
  },

  // Transitions - Update with your Figma transitions
  transitions: {
    fast: '150ms ease-in-out',      // Replace with your Figma transition values
    normal: '250ms ease-in-out',
    slow: '350ms ease-in-out',
    bounce: 'cubic-bezier(0.68, -0.55, 0.265, 1.55)',
    ease: 'cubic-bezier(0.4, 0, 0.2, 1)',
    easeIn: 'cubic-bezier(0.4, 0, 1, 1)',
    easeOut: 'cubic-bezier(0, 0, 0.2, 1)',
  },

  // Breakpoints - Update with your Figma breakpoints
  breakpoints: {
    mobile: '320px',       // Replace with your Figma mobile breakpoint
    tablet: '768px',       // Replace with your Figma tablet breakpoint
    desktop: '1024px',     // Replace with your Figma desktop breakpoint
    wide: '1280px',        // Replace with your Figma wide breakpoint
    ultra: '1536px',       // Replace with your Figma ultra breakpoint
  },

  // Z-Index Scale - Update with your Figma z-index values
  zIndex: {
    base: 0,               // Replace with your Figma z-index values
    dropdown: 1000,
    sticky: 1020,
    fixed: 1030,
    modal: 1040,
    popover: 1050,
    tooltip: 1060,
    toast: 1070,
  },
};

// Helper function to get responsive values
export function getResponsiveValue<T>(
  values: Record<string, T>,
  breakpoint: string
): T {
  return values[breakpoint] || values.desktop || Object.values(values)[0];
}

// Helper function to get color with opacity
export function getColorWithOpacity(color: string, opacity: number): string {
  return `${color}${Math.round(opacity * 255).toString(16).padStart(2, '0')}`;
}

// Export default
export default figmaTokens;
