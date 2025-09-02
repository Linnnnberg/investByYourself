/**
 * Spacing Design Tokens for investByYourself Platform
 * Consistent spacing scale for layout and components
 */

export const spacing = {
  // Base spacing scale (4px grid system)
  xs: '0.25rem',    // 4px
  sm: '0.5rem',     // 8px
  md: '1rem',       // 16px
  lg: '1.5rem',     // 24px
  xl: '2rem',       // 32px
  '2xl': '3rem',    // 48px
  '3xl': '4rem',    // 64px
  '4xl': '6rem',    // 96px
  '5xl': '8rem',    // 128px
  '6xl': '12rem',   // 192px

  // Component-specific spacing
  component: {
    // Button spacing
    button: {
      padding: {
        small: '0.5rem 1rem',    // 8px 16px
        medium: '0.75rem 1.5rem', // 12px 24px
        large: '1rem 2rem',      // 16px 32px
      },
      gap: '0.5rem',             // 8px between button elements
    },

    // Card spacing
    card: {
      padding: '1.5rem',         // 24px
      gap: '1rem',               // 16px between card elements
      margin: '1rem',            // 16px margin
    },

    // Form spacing
    form: {
      gap: '1.5rem',             // 24px between form sections
      fieldGap: '1rem',          // 16px between form fields
      labelGap: '0.5rem',        // 8px between label and input
    },

    // Navigation spacing
    nav: {
      itemGap: '1rem',           // 16px between nav items
      sectionGap: '2rem',        // 32px between nav sections
      padding: '1rem',           // 16px nav padding
    },

    // Layout spacing
    layout: {
      sectionGap: '3rem',        // 48px between major sections
      contentGap: '2rem',        // 32px between content blocks
      sidebarGap: '1.5rem',      // 24px sidebar spacing
    },

    // Table spacing
    table: {
      cellPadding: '0.75rem',    // 12px cell padding
      rowGap: '0.25rem',         // 4px between rows
      headerGap: '1rem',         // 16px header spacing
    },

    // Modal spacing
    modal: {
      padding: '2rem',           // 32px modal padding
      gap: '1.5rem',             // 24px between modal elements
      margin: '2rem',            // 32px modal margin
    },
  },

  // Layout spacing
  layout: {
    // Container spacing
    container: {
      padding: '1rem',           // 16px container padding
      maxWidth: '1200px',        // Max container width
      gutter: '2rem',            // 32px gutter between columns
    },

    // Grid spacing
    grid: {
      gap: '1.5rem',             // 24px grid gap
      columnGap: '1.5rem',       // 24px between columns
      rowGap: '1.5rem',          // 24px between rows
    },

    // Section spacing
    section: {
      padding: '3rem 0',         // 48px vertical, 0 horizontal
      margin: '2rem 0',          // 32px vertical, 0 horizontal
      gap: '2rem',               // 32px between sections
    },

    // Page spacing
    page: {
      padding: '2rem',           // 32px page padding
      margin: '0 auto',          // Center page content
      maxWidth: '1400px',        // Max page width
    },
  },

  // Responsive spacing
  responsive: {
    mobile: {
      container: '1rem',         // 16px mobile container padding
      section: '2rem 0',         // 32px mobile section padding
      gap: '1rem',               // 16px mobile gap
    },
    tablet: {
      container: '1.5rem',       // 24px tablet container padding
      section: '2.5rem 0',       // 40px tablet section padding
      gap: '1.5rem',             // 24px tablet gap
    },
    desktop: {
      container: '2rem',         // 32px desktop container padding
      section: '3rem 0',         // 48px desktop section padding
      gap: '2rem',               // 32px desktop gap
    },
  },

  // Utility spacing
  utility: {
    // Auto spacing
    auto: 'auto',

    // Zero spacing
    none: '0',

    // Full spacing
    full: '100%',

    // Viewport spacing
    screen: '100vw',
    screenHeight: '100vh',

    // Min/Max spacing
    min: 'min-content',
    max: 'max-content',
    fit: 'fit-content',
  },
} as const;

// Type definitions
export type SpacingToken = typeof spacing;
export type SpacingSize = keyof typeof spacing;
export type ComponentSpacing = keyof typeof spacing.component;
export type LayoutSpacing = keyof typeof spacing.layout;
export type ResponsiveSpacing = keyof typeof spacing.responsive;

// Utility functions
export const getSpacing = (size: SpacingSize): string => {
  return spacing[size];
};

export const getComponentSpacing = (component: ComponentSpacing, property: string): string => {
  const componentSpacing = spacing.component[component];
  return componentSpacing[property as keyof typeof componentSpacing] || spacing.md;
};

export const getResponsiveSpacing = (breakpoint: ResponsiveSpacing, property: string): string => {
  const responsiveSpacing = spacing.responsive[breakpoint];
  return responsiveSpacing[property as keyof typeof responsiveSpacing] || spacing.md;
};

// CSS custom properties for use in CSS
export const spacingCSS = {
  '--spacing-xs': spacing.xs,
  '--spacing-sm': spacing.sm,
  '--spacing-md': spacing.md,
  '--spacing-lg': spacing.lg,
  '--spacing-xl': spacing.xl,
  '--spacing-2xl': spacing['2xl'],
  '--spacing-3xl': spacing['3xl'],
  '--spacing-4xl': spacing['4xl'],
  '--spacing-5xl': spacing['5xl'],
  '--spacing-6xl': spacing['6xl'],
} as const;

// Export default spacing
export default spacing;
