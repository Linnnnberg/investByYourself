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
    '&:focus-visible': {
      boxShadow: `0 0 0 3px ${colors.primary[200]}`,
    },
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
      '&:hover': {
        backgroundColor: colors.primary[600],
      },
      '&:active': {
        backgroundColor: colors.primary[700],
      },
      '&:disabled': {
        backgroundColor: colors.neutral[300],
        color: colors.text.disabled,
        cursor: 'not-allowed',
      },
    },
    secondary: {
      backgroundColor: colors.secondary[100],
      color: colors.text.primary,
      border: `1px solid ${colors.secondary[300]}`,
      '&:hover': {
        backgroundColor: colors.secondary[200],
        borderColor: colors.secondary[400],
      },
      '&:active': {
        backgroundColor: colors.secondary[300],
        borderColor: colors.secondary[500],
      },
      '&:disabled': {
        backgroundColor: colors.neutral[100],
        borderColor: colors.neutral[300],
        color: colors.text.disabled,
        cursor: 'not-allowed',
      },
    },
    outline: {
      backgroundColor: 'transparent',
      color: colors.primary[600],
      border: `2px solid ${colors.primary[500]}`,
      '&:hover': {
        backgroundColor: colors.primary[50],
        borderColor: colors.primary[600],
      },
      '&:active': {
        backgroundColor: colors.primary[100],
        borderColor: colors.primary[700],
      },
      '&:disabled': {
        borderColor: colors.neutral[300],
        color: colors.text.disabled,
        cursor: 'not-allowed',
      },
    },
    ghost: {
      backgroundColor: 'transparent',
      color: colors.text.secondary,
      '&:hover': {
        backgroundColor: colors.neutral[100],
        color: colors.text.primary,
      },
      '&:active': {
        backgroundColor: colors.neutral[200],
        color: colors.text.primary,
      },
      '&:disabled': {
        color: colors.text.disabled,
        cursor: 'not-allowed',
      },
    },
    danger: {
      backgroundColor: colors.danger[500],
      color: colors.text.inverse,
      '&:hover': {
        backgroundColor: colors.danger[600],
      },
      '&:active': {
        backgroundColor: colors.danger[700],
      },
      '&:disabled': {
        backgroundColor: colors.neutral[300],
        color: colors.text.disabled,
        cursor: 'not-allowed',
      },
    },
    success: {
      backgroundColor: colors.success[500],
      color: colors.text.inverse,
      '&:hover': {
        backgroundColor: colors.success[600],
      },
      '&:active': {
        backgroundColor: colors.success[700],
      },
      '&:disabled': {
        backgroundColor: colors.neutral[300],
        color: colors.text.disabled,
        cursor: 'not-allowed',
      },
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

  return (
    <button
      className={`design-system-button ${className}`}
      style={buttonStyle as React.CSSProperties}
      disabled={isDisabled}
      {...props}
    >
      {loading && renderLoadingSpinner()}
      {icon && iconPosition === 'left' && renderIcon()}
      <span className="button-content">{children}</span>
      {icon && iconPosition === 'right' && renderIcon()}

      {/* Add CSS for animations */}
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
      `}</style>
    </button>
  );
};

// Export default
export default Button;
