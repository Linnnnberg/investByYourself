/**
 * Button Component for investByYourself Platform
 * Built with design system tokens for consistency
 */

import React from 'react';
import { colors, typography, spacing, designSystem } from '../index';

// Button variants
export type ButtonVariant = 'primary' | 'secondary' | 'outline' | 'ghost' | 'danger' | 'success';
export type ButtonSize = 'small' | 'medium' | 'large';
export type ButtonState = 'default' | 'hover' | 'active' | 'disabled' | 'loading';

// Button props interface
export interface ButtonProps extends React.ButtonHTMLAttributes<HTMLButtonElement> {
  variant?: ButtonVariant;
  size?: ButtonSize;
  state?: ButtonState;
  loading?: boolean;
  icon?: React.ReactNode;
  iconPosition?: 'left' | 'right';
  fullWidth?: boolean;
  children: React.ReactNode;
}

// Button styles based on design system
const buttonStyles = {
  // Base button styles
  base: {
    display: 'inline-flex',
    alignItems: 'center',
    justifyContent: 'center',
    gap: spacing.component.button.gap,
    border: 'none',
    borderRadius: designSystem.borderRadius.md,
    fontFamily: typography.fontFamily.sans.join(', '),
    fontWeight: typography.fontWeight.semibold,
    textDecoration: 'none',
    cursor: 'pointer',
    transition: designSystem.transitions.fast,
    outline: 'none',
  },

  // Size variants
  size: {
    small: {
      padding: spacing.component.button.padding.small,
      fontSize: typography.textStyles.button.small.fontSize,
      lineHeight: typography.textStyles.button.small.lineHeight,
      letterSpacing: typography.textStyles.button.small.letterSpacing,
      minHeight: '2rem',
    },
    medium: {
      padding: spacing.component.button.padding.medium,
      fontSize: typography.textStyles.button.medium.fontSize,
      lineHeight: typography.textStyles.button.medium.lineHeight,
      letterSpacing: typography.textStyles.button.medium.letterSpacing,
      minHeight: '2.5rem',
    },
    large: {
      padding: spacing.component.button.padding.large,
      fontSize: typography.textStyles.button.large.fontSize,
      lineHeight: typography.textStyles.button.large.lineHeight,
      letterSpacing: typography.textStyles.button.large.letterSpacing,
      minHeight: '3rem',
    },
  },

  // Variant styles
  variant: {
    primary: {
      backgroundColor: colors.primary[500],
      color: colors.text.inverse,
    },
    secondary: {
      backgroundColor: colors.secondary[100],
      color: colors.text.primary,
      border: `1px solid ${colors.secondary[300]}`,
    },
    outline: {
      backgroundColor: 'transparent',
      color: colors.primary[600],
      border: `2px solid ${colors.primary[500]}`,
    },
    ghost: {
      backgroundColor: 'transparent',
      color: colors.text.secondary,
    },
    danger: {
      backgroundColor: colors.danger[500],
      color: colors.text.inverse,
    },
    success: {
      backgroundColor: colors.success[500],
      color: colors.text.inverse,
    },
  },

  // State styles
  state: {
    loading: {
      cursor: 'wait',
      opacity: 0.7,
    },
    disabled: {
      cursor: 'not-allowed',
      opacity: 0.5,
    },
  },

  // Full width style
  fullWidth: {
    width: '100%',
  },
};

// Button component
export const Button: React.FC<ButtonProps> = ({
  variant = 'primary',
  size = 'medium',
  state = 'default',
  loading = false,
  icon,
  iconPosition = 'left',
  fullWidth = false,
  children,
  disabled,
  className = '',
  ...props
}) => {
  // Determine if button should be disabled
  const isDisabled = disabled || loading || state === 'disabled';

  // Combine styles
  const buttonStyle = {
    ...buttonStyles.base,
    ...buttonStyles.size[size],
    ...buttonStyles.variant[variant],
    ...(isDisabled && buttonStyles.state.disabled),
    ...(loading && buttonStyles.state.loading),
    ...(fullWidth && buttonStyles.fullWidth),
  };

  // Convert styles to CSS string
  const styleString = Object.entries(buttonStyle)
    .map(([key, value]) => {
      if (typeof value === 'object') {
        return Object.entries(value)
          .map(([subKey, subValue]) => `${key}-${subKey}: ${subValue};`)
          .join(' ');
      }
      return `${key}: ${value};`;
    })
    .join(' ');

  // Render icon based on position
  const renderIcon = () => {
    if (!icon) return null;

    return (
      <span className="button-icon" style={{ display: 'flex', alignItems: 'center' }}>
        {icon}
      </span>
    );
  };

  // Render loading spinner
  const renderLoadingSpinner = () => {
    if (!loading) return null;

    return (
      <span className="button-loading" style={{ display: 'inline-block', width: '1em', height: '1em' }}>
        <svg
          style={{ animation: 'spin 1s linear infinite' }}
          viewBox="0 0 24 24"
          fill="none"
          xmlns="http://www.w3.org/2000/svg"
        >
          <circle
            cx="12"
            cy="12"
            r="10"
            stroke="currentColor"
            strokeWidth="4"
            strokeLinecap="round"
            strokeDasharray="31.416"
            strokeDashoffset="31.416"
            style={{
              animation: 'dash 1.5s ease-in-out infinite',
            }}
          />
        </svg>
      </span>
    );
  };

  // Build class names array and filter out empty strings
  const classNames = [
    'design-system-button',
    `design-system-button-${variant}`,
    `design-system-button-${size}`,
    isDisabled ? 'design-system-button-disabled' : '',
    loading ? 'design-system-button-loading' : '',
    className
  ].filter(Boolean).join(' ');

  return (
    <button
      className={classNames}
      style={buttonStyle as React.CSSProperties}
      disabled={isDisabled}
      {...props}
    >
      {loading && renderLoadingSpinner()}
      {icon && iconPosition === 'left' && renderIcon()}
      {children}
      {icon && iconPosition === 'right' && renderIcon()}

      {/* Add CSS for animations and hover states */}
      <style jsx>{`
        @keyframes spin {
          from { transform: rotate(0deg); }
          to { transform: rotate(360deg); }
        }

        @keyframes dash {
          0% { stroke-dashoffset: 31.416; }
          50% { stroke-dashoffset: 0; }
          100% { stroke-dashoffset: -31.416; }
        }

        .design-system-button {
          ${styleString}
        }

        .design-system-button:focus-visible {
          box-shadow: 0 0 0 3px ${colors.primary[200]};
        }

        .design-system-button-primary:hover:not(:disabled) {
          background-color: ${colors.primary[600]};
        }

        .design-system-button-primary:active:not(:disabled) {
          background-color: ${colors.primary[700]};
        }

        .design-system-button-secondary:hover:not(:disabled) {
          background-color: ${colors.secondary[200]};
          border-color: ${colors.secondary[400]};
        }

        .design-system-button-secondary:active:not(:disabled) {
          background-color: ${colors.secondary[300]};
          border-color: ${colors.secondary[500]};
        }

        .design-system-button-outline:hover:not(:disabled) {
          background-color: ${colors.primary[50]};
          border-color: ${colors.primary[600]};
        }

        .design-system-button-outline:active:not(:disabled) {
          background-color: ${colors.primary[100]};
          border-color: ${colors.primary[700]};
        }

        .design-system-button-ghost:hover:not(:disabled) {
          background-color: ${colors.neutral[100]};
          color: ${colors.text.primary};
        }

        .design-system-button-ghost:active:not(:disabled) {
          background-color: ${colors.neutral[200]};
          color: ${colors.text.primary};
        }

        .design-system-button-danger:hover:not(:disabled) {
          background-color: ${colors.danger[600]};
        }

        .design-system-button-danger:active:not(:disabled) {
          background-color: ${colors.danger[700]};
        }

        .design-system-button-success:hover:not(:disabled) {
          background-color: ${colors.success[600]};
        }

        .design-system-button-success:active:not(:disabled) {
          background-color: ${colors.success[700]};
        }

        .design-system-button-disabled {
          background-color: ${colors.neutral[300]} !important;
          color: ${colors.text.disabled} !important;
          cursor: not-allowed !important;
        }

        .design-system-button-outline.design-system-button-disabled {
          border-color: ${colors.neutral[300]} !important;
          background-color: transparent !important;
        }

        .design-system-button-loading {
          cursor: wait;
          opacity: 0.7;
        }
      `}</style>
    </button>
  );
};

// Export default
export default Button;
