/**
 * Design System Index for investByYourself Platform
 * Central export point for all design tokens and utilities
 */

// Import token values for use in designSystem object
import colors from './tokens/colors';
import typography from './tokens/typography';
import spacing from './tokens/spacing';

// Design Tokens
export { default as colors, type ColorToken, type ColorKey, type ColorShade } from './tokens/colors';
export { default as typography, type TypographyToken, type TextStyle } from './tokens/typography';
export { default as spacing, type SpacingToken, type SpacingSize } from './tokens/spacing';

// Design System Configuration
export const designSystem = {
  name: 'investByYourself Design System',
  version: '1.0.0',
  description: 'Professional financial platform design system',

  // Core tokens
  tokens: {
    colors,
    typography,
    spacing,
  },

  // Design principles
  principles: {
    consistency: 'Maintain visual consistency across all components',
    accessibility: 'Ensure designs meet WCAG 2.1 AA standards',
    scalability: 'Design system should scale with platform growth',
    performance: 'Optimize for fast loading and smooth interactions',
    userExperience: 'Prioritize intuitive and efficient user workflows',
  },

  // Brand guidelines
  brand: {
    primaryColor: colors.primary[500],
    secondaryColor: colors.secondary[500],
    accentColor: colors.financial.info,
    successColor: colors.financial.profit,
    warningColor: colors.financial.alert,
    dangerColor: colors.financial.loss,
  },

  // Typography scale
  typographyScale: {
    display: typography.textStyles.display,
    heading: typography.textStyles.heading,
    body: typography.textStyles.body,
    caption: typography.textStyles.caption,
    button: typography.textStyles.button,
    financial: typography.textStyles.financial,
  },

  // Spacing scale
  spacingScale: {
    xs: spacing.xs,
    sm: spacing.sm,
    md: spacing.md,
    lg: spacing.lg,
    xl: spacing.xl,
    '2xl': spacing['2xl'],
    '3xl': spacing['3xl'],
    '4xl': spacing['4xl'],
    '5xl': spacing['5xl'],
    '6xl': spacing['6xl'],
  },

  // Breakpoints for responsive design
  breakpoints: {
    mobile: '320px',
    tablet: '768px',
    desktop: '1024px',
    wide: '1280px',
    ultra: '1536px',
  },

  // Z-index scale
  zIndex: {
    base: 0,
    dropdown: 1000,
    sticky: 1020,
    fixed: 1030,
    modal: 1040,
    popover: 1050,
    tooltip: 1060,
    toast: 1070,
  },

  // Shadows
  shadows: {
    sm: '0 1px 2px 0 rgba(0, 0, 0, 0.05)',
    md: '0 4px 6px -1px rgba(0, 0, 0, 0.1), 0 2px 4px -1px rgba(0, 0, 0, 0.06)',
    lg: '0 10px 15px -3px rgba(0, 0, 0, 0.1), 0 4px 6px -2px rgba(0, 0, 0, 0.05)',
    xl: '0 20px 25px -5px rgba(0, 0, 0, 0.1), 0 10px 10px -5px rgba(0, 0, 0, 0.04)',
    '2xl': '0 25px 50px -12px rgba(0, 0, 0, 0.25)',
    inner: 'inset 0 2px 4px 0 rgba(0, 0, 0, 0.06)',
    none: 'none',
  },

  // Border radius
  borderRadius: {
    none: '0',
    sm: '0.125rem',    // 2px
    md: '0.375rem',    // 6px
    lg: '0.5rem',      // 8px
    xl: '0.75rem',     // 12px
    '2xl': '1rem',     // 16px
    '3xl': '1.5rem',   // 24px
    full: '9999px',
  },

  // Transitions
  transitions: {
    fast: '150ms ease-in-out',
    normal: '250ms ease-in-out',
    slow: '350ms ease-in-out',
    bounce: 'cubic-bezier(0.68, -0.55, 0.265, 1.55)',
    ease: 'cubic-bezier(0.4, 0, 0.2, 1)',
    easeIn: 'cubic-bezier(0.4, 0, 1, 1)',
    easeOut: 'cubic-bezier(0, 0, 0.2, 1)',
  },
} as const;

// Utility functions
export const designSystemUtils = {
  // Get color with opacity
  getColorWithOpacity: (color: string, opacity: number): string => {
    return `${color}${Math.round(opacity * 255).toString(16).padStart(2, '0')}`;
  },

  // Get responsive value
  getResponsiveValue: <T>(values: Record<string, T>, breakpoint: string): T => {
    return values[breakpoint] || values.desktop || Object.values(values)[0];
  },

  // Generate CSS custom properties
  generateCSSVariables: (): Record<string, string> => {
    const variables: Record<string, string> = {};

    // Color variables
    Object.entries(colors).forEach(([category, categoryColors]) => {
      if (typeof categoryColors === 'object' && categoryColors !== null) {
        Object.entries(categoryColors).forEach(([shade, value]) => {
          variables[`--color-${category}-${shade}`] = value;
        });
      } else {
        variables[`--color-${category}`] = categoryColors as string;
      }
    });

    // Spacing variables
    Object.entries(spacing).forEach(([key, value]) => {
      if (typeof value === 'string') {
        variables[`--spacing-${key}`] = value;
      }
    });

    // Typography variables
    Object.entries(typography.fontSize).forEach(([size, value]) => {
      variables[`--font-size-${size}`] = value;
    });

    Object.entries(typography.fontWeight).forEach(([weight, value]) => {
      variables[`--font-weight-${weight}`] = value;
    });

    return variables;
  },

  // Validate design token
  validateToken: (token: any, schema: any): boolean => {
    // Basic validation - can be expanded
    return token && typeof token === 'object';
  },
};

// Export design system as default
export default designSystem;

// Type exports
export type DesignSystem = typeof designSystem;
export type DesignSystemTokens = typeof designSystem.tokens;
export type DesignSystemPrinciples = typeof designSystem.principles;
export type DesignSystemBrand = typeof designSystem.brand;
