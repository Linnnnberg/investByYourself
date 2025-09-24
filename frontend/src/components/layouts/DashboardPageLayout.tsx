/**
 * Dashboard Page Layout Component
 * Reusable layout for all dashboard pages to avoid duplication
 */

import React from 'react';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Badge } from '@/components/ui/badge';

export interface PageHeaderAction {
  label: string;
  onClick: () => void;
  variant?: 'primary' | 'secondary' | 'outline' | 'ghost' | 'danger' | 'success';
  icon?: React.ReactNode;
  disabled?: boolean;
}

export interface DashboardPageLayoutProps {
  // Page header
  title: string;
  description?: string;
  actions?: PageHeaderAction[];

  // Status indicators
  status?: {
    label: string;
    value: string;
    color: 'green' | 'yellow' | 'red' | 'blue' | 'gray';
  }[];

  // Loading state
  loading?: boolean;
  loadingText?: string;

  // Error state
  error?: string | null;
  onRetry?: () => void;

  // Content
  children: React.ReactNode;

  // Layout options
  maxWidth?: 'sm' | 'md' | 'lg' | 'xl' | '2xl' | 'full';
  className?: string;
}

const maxWidthClasses = {
  sm: 'max-w-2xl',
  md: 'max-w-4xl',
  lg: 'max-w-6xl',
  xl: 'max-w-7xl',
  '2xl': 'max-w-8xl',
  full: 'max-w-none',
};

const statusColors = {
  green: 'bg-green-500',
  yellow: 'bg-yellow-500',
  red: 'bg-red-500',
  blue: 'bg-blue-500',
  gray: 'bg-gray-500',
};

export const DashboardPageLayout: React.FC<DashboardPageLayoutProps> = ({
  title,
  description,
  actions = [],
  status = [],
  loading = false,
  loadingText = 'Loading...',
  error = null,
  onRetry,
  children,
  maxWidth = 'full',
  className = '',
}) => {
  // Loading state
  if (loading) {
    return (
      <div className={`container mx-auto px-4 py-8 ${className}`}>
        <div className="flex items-center justify-center h-64">
          <div className="text-center">
            <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-600 mx-auto mb-4"></div>
            <p className="text-gray-600">{loadingText}</p>
          </div>
        </div>
      </div>
    );
  }

  // Error state
  if (error) {
    return (
      <div className={`container mx-auto px-4 py-8 ${className}`}>
        <div className="flex items-center justify-center h-64">
          <Card className="max-w-md">
            <CardHeader className="text-center">
              <div className="text-6xl mb-4">⚠️</div>
              <CardTitle className="text-red-600">Error</CardTitle>
              <CardDescription>{error}</CardDescription>
            </CardHeader>
            <CardContent className="text-center">
              {onRetry && (
                <Button onClick={onRetry} variant="outline">
                  Try Again
                </Button>
              )}
            </CardContent>
          </Card>
        </div>
      </div>
    );
  }

  return (
    <div className={`container mx-auto px-4 py-8 ${maxWidthClasses[maxWidth]} ${className}`}>
      {/* Page Header */}
      <div className="mb-8">
        <div className="flex items-center justify-between">
          <div>
            <h1 className="text-3xl font-bold text-gray-900 mb-2">{title}</h1>
            {description && (
              <p className="text-gray-600">{description}</p>
            )}
          </div>

          {/* Status Indicators */}
          {status.length > 0 && (
            <div className="flex items-center space-x-4">
              {status.map((statusItem, index) => (
                <div key={index} className="text-sm text-gray-500">
                  <span className={`inline-block w-2 h-2 rounded-full mr-2 ${statusColors[statusItem.color]}`}></span>
                  {statusItem.label}: {statusItem.value}
                </div>
              ))}
            </div>
          )}
        </div>

        {/* Action Buttons */}
        {actions.length > 0 && (
          <div className="flex items-center space-x-4 mt-4">
            {actions.map((action, index) => (
              <Button
                key={index}
                variant={action.variant || 'primary'}
                onClick={action.onClick}
                disabled={action.disabled}
              >
                {action.icon && <span className="mr-2">{action.icon}</span>}
                {action.label}
              </Button>
            ))}
          </div>
        )}
      </div>

      {/* Page Content */}
      {children}
    </div>
  );
};

export default DashboardPageLayout;
