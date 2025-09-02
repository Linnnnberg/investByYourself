/**
 * Typography Design Tokens for investByYourself Platform
 * Professional financial platform typography system
 */

export const typography = {
  // Font Families
  fontFamily: {
    sans: [
      'Inter',
      '-apple-system',
      'BlinkMacSystemFont',
      'Segoe UI',
      'Roboto',
      'Helvetica Neue',
      'Arial',
      'sans-serif',
    ],
    mono: [
      'JetBrains Mono',
      'Fira Code',
      'Monaco',
      'Consolas',
      'Liberation Mono',
      'Courier New',
      'monospace',
    ],
    display: [
      'Inter',
      'system-ui',
      'sans-serif',
    ],
  },

  // Font Sizes
  fontSize: {
    xs: '0.75rem',    // 12px
    sm: '0.875rem',   // 14px
    base: '1rem',     // 16px
    lg: '1.125rem',   // 18px
    xl: '1.25rem',    // 20px
    '2xl': '1.5rem',  // 24px
    '3xl': '1.875rem', // 30px
    '4xl': '2.25rem',  // 36px
    '5xl': '3rem',     // 48px
    '6xl': '3.75rem',  // 60px
    '7xl': '4.5rem',   // 72px
    '8xl': '6rem',     // 96px
    '9xl': '8rem',     // 128px
  },

  // Font Weights
  fontWeight: {
    thin: '100',
    extralight: '200',
    light: '300',
    normal: '400',
    medium: '500',
    semibold: '600',
    bold: '700',
    extrabold: '800',
    black: '900',
  },

  // Line Heights
  lineHeight: {
    none: '1',
    tight: '1.25',
    snug: '1.375',
    normal: '1.5',
    relaxed: '1.625',
    loose: '2',
  },

  // Letter Spacing
  letterSpacing: {
    tighter: '-0.05em',
    tight: '-0.025em',
    normal: '0em',
    wide: '0.025em',
    wider: '0.05em',
    widest: '0.1em',
  },

  // Text Styles (Predefined combinations)
  textStyles: {
    // Display styles for large headings
    display: {
      large: {
        fontSize: '3rem',
        fontWeight: '700',
        lineHeight: '1.2',
        letterSpacing: '-0.02em',
      },
      medium: {
        fontSize: '2.25rem',
        fontWeight: '700',
        lineHeight: '1.3',
        letterSpacing: '-0.01em',
      },
      small: {
        fontSize: '1.875rem',
        fontWeight: '600',
        lineHeight: '1.4',
        letterSpacing: '0em',
      },
    },

    // Heading styles
    heading: {
      h1: {
        fontSize: '2.25rem',
        fontWeight: '700',
        lineHeight: '1.3',
        letterSpacing: '-0.01em',
      },
      h2: {
        fontSize: '1.875rem',
        fontWeight: '600',
        lineHeight: '1.4',
        letterSpacing: '0em',
      },
      h3: {
        fontSize: '1.5rem',
        fontWeight: '600',
        lineHeight: '1.4',
        letterSpacing: '0em',
      },
      h4: {
        fontSize: '1.25rem',
        fontWeight: '600',
        lineHeight: '1.5',
        letterSpacing: '0em',
      },
      h5: {
        fontSize: '1.125rem',
        fontWeight: '600',
        lineHeight: '1.5',
        letterSpacing: '0em',
      },
      h6: {
        fontSize: '1rem',
        fontWeight: '600',
        lineHeight: '1.5',
        letterSpacing: '0em',
      },
    },

    // Body text styles
    body: {
      large: {
        fontSize: '1.125rem',
        fontWeight: '400',
        lineHeight: '1.6',
        letterSpacing: '0em',
      },
      medium: {
        fontSize: '1rem',
        fontWeight: '400',
        lineHeight: '1.6',
        letterSpacing: '0em',
      },
      small: {
        fontSize: '0.875rem',
        fontWeight: '400',
        lineHeight: '1.5',
        letterSpacing: '0em',
      },
    },

    // Caption and label styles
    caption: {
      large: {
        fontSize: '0.875rem',
        fontWeight: '500',
        lineHeight: '1.4',
        letterSpacing: '0.01em',
      },
      medium: {
        fontSize: '0.75rem',
        fontWeight: '500',
        lineHeight: '1.4',
        letterSpacing: '0.01em',
      },
      small: {
        fontSize: '0.75rem',
        fontWeight: '400',
        lineHeight: '1.3',
        letterSpacing: '0.01em',
      },
    },

    // Button text styles
    button: {
      large: {
        fontSize: '1rem',
        fontWeight: '600',
        lineHeight: '1.5',
        letterSpacing: '0.01em',
      },
      medium: {
        fontSize: '0.875rem',
        fontWeight: '600',
        lineHeight: '1.5',
        letterSpacing: '0.01em',
      },
      small: {
        fontSize: '0.75rem',
        fontWeight: '600',
        lineHeight: '1.5',
        letterSpacing: '0.01em',
      },
    },

    // Financial data styles
    financial: {
      price: {
        fontSize: '1.5rem',
        fontWeight: '700',
        lineHeight: '1.2',
        letterSpacing: '-0.01em',
      },
      change: {
        fontSize: '1rem',
        fontWeight: '600',
        lineHeight: '1.4',
        letterSpacing: '0em',
      },
      metric: {
        fontSize: '0.875rem',
        fontWeight: '500',
        lineHeight: '1.4',
        letterSpacing: '0.01em',
      },
    },
  },
} as const;

// Type definitions
export type TypographyToken = typeof typography;
export type FontSize = keyof typeof typography.fontSize;
export type FontWeight = keyof typeof typography.fontWeight;
export type LineHeight = keyof typeof typography.lineHeight;
export type LetterSpacing = keyof typeof typography.letterSpacing;
export type TextStyle = keyof typeof typography.textStyles;

// Utility function to get text style
export const getTextStyle = (style: TextStyle, variant?: string) => {
  const textStyle = typography.textStyles[style];
  if (variant && textStyle[variant as keyof typeof textStyle]) {
    return textStyle[variant as keyof typeof textStyle];
  }
  return textStyle;
};

// Export default typography
export default typography;
