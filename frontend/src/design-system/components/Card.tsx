/**
 * Card Component for investByYourself Platform
 * Built with design system tokens for consistency
 */

import React from 'react';
import { colors, spacing, designSystem } from '../index';

// Card variants
export type CardVariant = 'default' | 'elevated' | 'outlined' | 'interactive' | 'financial';
export type CardSize = 'small' | 'medium' | 'large';

// Card props interface
export interface CardProps {
  variant?: CardVariant;
  size?: CardSize;
  children: React.ReactNode;
  className?: string;
  onClick?: () => void;
  hoverable?: boolean;
  selected?: boolean;
  disabled?: boolean;
  header?: React.ReactNode;
  footer?: React.ReactNode;
  padding?: 'none' | 'small' | 'medium' | 'large' | 'custom';
  customPadding?: string;
  maxWidth?: string;
  minHeight?: string;
  style?: React.CSSProperties;
}

// Card styles based on design system
const cardStyles = {
  // Base card styles
  base: {
    backgroundColor: colors.background.card,
    borderRadius: designSystem.borderRadius.lg,
    fontFamily: 'inherit',
    position: 'relative' as const,
    overflow: 'hidden',
    transition: designSystem.transitions.normal,
  },

  // Size variants
  size: {
    small: {
      padding: spacing.component.card.padding,
    },
    medium: {
      padding: spacing.component.card.padding,
    },
    large: {
      padding: spacing.component.card.padding,
    },
  },

  // Variant styles
  variant: {
    default: {
      border: `1px solid ${colors.border.light}`,
      boxShadow: designSystem.shadows.sm,
    },
    elevated: {
      border: 'none',
      boxShadow: designSystem.shadows.lg,
    },
    outlined: {
      border: `2px solid ${colors.border.medium}`,
      boxShadow: 'none',
    },
    interactive: {
      border: `1px solid ${colors.border.light}`,
      boxShadow: designSystem.shadows.sm,
      cursor: 'pointer',
      '&:hover': {
        boxShadow: designSystem.shadows.md,
        transform: 'translateY(-2px)',
      },
      '&:active': {
        transform: 'translateY(0)',
      },
    },
    financial: {
      border: `1px solid ${colors.border.light}`,
      boxShadow: designSystem.shadows.sm,
      background: `linear-gradient(135deg, ${colors.background.primary} 0%, ${colors.background.secondary} 100%)`,
    },
  },

  // Padding variants
  padding: {
    none: {
      padding: '0',
    },
    small: {
      padding: spacing.sm,
    },
    medium: {
      padding: spacing.component.card.padding,
    },
    large: {
      padding: spacing.lg,
    },
    custom: {
      padding: 'var(--card-custom-padding)',
    },
  },

  // Interactive states
  interactive: {
    hoverable: {
      '&:hover': {
        boxShadow: designSystem.shadows.md,
        transform: 'translateY(-2px)',
      },
    },
    selected: {
      borderColor: colors.primary[500],
      boxShadow: `0 0 0 3px ${colors.primary[100]}`,
    },
    disabled: {
      opacity: 0.6,
      cursor: 'not-allowed',
      pointerEvents: 'none' as const,
    },
  },

  // Header and footer styles
  header: {
    borderBottom: `1px solid ${colors.border.light}`,
    padding: `${spacing.md} ${spacing.component.card.padding}`,
    margin: `-${spacing.component.card.padding} -${spacing.component.card.padding} ${spacing.component.card.padding} -${spacing.component.card.padding}`,
    backgroundColor: colors.background.secondary,
  },
  footer: {
    borderTop: `1px solid ${colors.border.light}`,
    padding: `${spacing.md} ${spacing.component.card.padding}`,
    margin: `${spacing.component.card.padding} -${spacing.component.card.padding} -${spacing.component.card.padding} -${spacing.component.card.padding}`,
    backgroundColor: colors.background.secondary,
  },
};

// Card component
export const Card: React.FC<CardProps> = ({
  variant = 'default',
  size = 'medium',
  children,
  className = '',
  onClick,
  hoverable = false,
  selected = false,
  disabled = false,
  header,
  footer,
  padding = 'medium',
  customPadding,
  maxWidth,
  minHeight,
  style,
}) => {
  // Determine if card is interactive
  const isInteractive = onClick || hoverable || variant === 'interactive';

  // Combine styles
  const cardStyle: React.CSSProperties = {
    ...cardStyles.base,
    ...cardStyles.size[size],
    ...cardStyles.variant[variant],
    ...cardStyles.padding[padding],
    ...(isInteractive && cardStyles.interactive.hoverable),
    ...(selected && cardStyles.interactive.selected),
    ...(disabled && cardStyles.interactive.disabled),
    ...(maxWidth && { maxWidth }),
    ...(minHeight && { minHeight }),
    ...(customPadding && padding === 'custom' && { '--card-custom-padding': customPadding } as any),
    ...style,
  };

  // Handle click events
  const handleClick = () => {
    if (onClick && !disabled) {
      onClick();
    }
  };

  // Render header
  const renderHeader = () => {
    if (!header) return null;

    return (
      <div className="card-header" style={cardStyles.header}>
        {header}
      </div>
    );
  };

  // Render footer
  const renderFooter = () => {
    if (!footer) return null;

    return (
      <div className="card-footer" style={cardStyles.footer}>
        {footer}
      </div>
    );
  };

  // Render card content
  const renderContent = () => {
    if (header || footer) {
      return (
        <>
          {renderHeader()}
          <div className="card-content">
            {children}
          </div>
          {renderFooter()}
        </>
      );
    }

    return children;
  };

  // Determine card element type
  const CardElement = isInteractive ? 'div' : 'div';
  const cardProps = isInteractive ? { onClick: handleClick, role: 'button', tabIndex: 0 } : {};

  // Build class names array and filter out empty strings
  const classNames = [
    'design-system-card',
    className
  ].filter(Boolean).join(' ');

  return (
    <CardElement
      className={classNames}
      style={cardStyle}
      {...cardProps}
    >
      {renderContent()}

      {/* Add CSS for hover effects */}
      <style jsx>{`
        .design-system-card {
          ${Object.entries(cardStyle)
            .map(([key, value]) => `${key}: ${value};`)
            .join(' ')}
        }

        .design-system-card[role="button"]:focus-visible {
          outline: 2px solid ${colors.primary[500]};
          outline-offset: 2px;
        }

        .card-content {
          padding: inherit;
        }
      `}</style>
    </CardElement>
  );
};

// Card sub-components for better composition
export const CardHeader: React.FC<{ children: React.ReactNode; className?: string }> = ({
  children,
  className = '',
}) => {
  const classNames = ['card-header', className].filter(Boolean).join(' ');
  return (
    <div className={classNames} style={cardStyles.header}>
      {children}
    </div>
  );
};

export const CardContent: React.FC<{ children: React.ReactNode; className?: string }> = ({
  children,
  className = '',
}) => {
  const classNames = ['card-content', className].filter(Boolean).join(' ');
  return (
    <div className={classNames}>
      {children}
    </div>
  );
};

export const CardFooter: React.FC<{ children: React.ReactNode; className?: string }> = ({
  children,
  className = '',
}) => {
  const classNames = ['card-footer', className].filter(Boolean).join(' ');
  return (
    <div className={classNames} style={cardStyles.footer}>
      {children}
    </div>
  );
};

// Export default
export default Card;
