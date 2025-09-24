/**
 * Badge UI Component
 * Simple badge component for displaying status, tags, etc.
 */

import React from 'react';

export type BadgeVariant = 'default' | 'secondary' | 'destructive' | 'outline' | 'success' | 'warning';
export type BadgeSize = 'sm' | 'md' | 'lg';

export interface BadgeProps {
  children: React.ReactNode;
  variant?: BadgeVariant;
  size?: BadgeSize;
  className?: string;
  style?: React.CSSProperties;
}

const badgeStyles = {
  base: {
    display: 'inline-flex',
    alignItems: 'center',
    justifyContent: 'center',
    borderRadius: '6px',
    fontWeight: '500',
    whiteSpace: 'nowrap' as const,
    transition: 'all 0.2s ease-in-out',
  },
  variant: {
    default: {
      backgroundColor: '#3b82f6',
      color: 'white',
      border: '1px solid transparent',
    },
    secondary: {
      backgroundColor: '#f1f5f9',
      color: '#475569',
      border: '1px solid #e2e8f0',
    },
    destructive: {
      backgroundColor: '#ef4444',
      color: 'white',
      border: '1px solid transparent',
    },
    outline: {
      backgroundColor: 'transparent',
      color: '#374151',
      border: '1px solid #d1d5db',
    },
    success: {
      backgroundColor: '#10b981',
      color: 'white',
      border: '1px solid transparent',
    },
    warning: {
      backgroundColor: '#f59e0b',
      color: 'white',
      border: '1px solid transparent',
    },
  },
  size: {
    sm: {
      padding: '2px 6px',
      fontSize: '11px',
      lineHeight: '16px',
    },
    md: {
      padding: '4px 8px',
      fontSize: '12px',
      lineHeight: '18px',
    },
    lg: {
      padding: '6px 12px',
      fontSize: '14px',
      lineHeight: '20px',
    },
  },
};

export const Badge: React.FC<BadgeProps> = ({
  children,
  variant = 'default',
  size = 'md',
  className = '',
  style,
}) => {
  const badgeStyle: React.CSSProperties = {
    ...badgeStyles.base,
    ...badgeStyles.variant[variant],
    ...badgeStyles.size[size],
    ...style,
  };

  return (
    <span
      className={`badge badge-${variant} badge-${size} ${className}`}
      style={badgeStyle}
    >
      {children}
    </span>
  );
};

export default Badge;
