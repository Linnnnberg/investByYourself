'use client';

import React from 'react';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Badge } from '@/components/ui/badge';
import { CheckCircle, XCircle, AlertTriangle, RefreshCw } from 'lucide-react';
import { WorkflowStep, WorkflowContext } from '@/types/workflow';

interface ValidationResult {
  id: string;
  name: string;
  status: 'passed' | 'failed' | 'warning';
  message: string;
  details?: string;
}

interface ValidationStepComponentProps {
  stepId: string;
  title: string;
  description: string;
  results: ValidationResult[];
  overallStatus: 'passed' | 'failed' | 'warning' | 'pending';
  summary?: string;
  onRetry?: () => void;
  onContinue: () => void;
  onBack: () => void;
  isLoading: boolean;
  showDetails?: boolean;
}

const ValidationStepComponent: React.FC<ValidationStepComponentProps> = ({
  stepId,
  title,
  description,
  results,
  overallStatus,
  summary,
  onRetry,
  onContinue,
  onBack,
  isLoading,
  showDetails = true
}) => {
  const getStatusIcon = (status: string) => {
    switch (status) {
      case 'passed':
        return <CheckCircle className="h-5 w-5 text-green-500" />;
      case 'failed':
        return <XCircle className="h-5 w-5 text-red-500" />;
      case 'warning':
        return <AlertTriangle className="h-5 w-5 text-yellow-500" />;
      default:
        return <RefreshCw className="h-5 w-5 text-gray-400" />;
    }
  };

  const getStatusBadge = (status: string) => {
    switch (status) {
      case 'passed':
        return <Badge variant="default" className="bg-green-100 text-green-800">Passed</Badge>;
      case 'failed':
        return <Badge variant="destructive">Failed</Badge>;
      case 'warning':
        return <Badge variant="secondary" className="bg-yellow-100 text-yellow-800">Warning</Badge>;
      default:
        return <Badge variant="outline">Pending</Badge>;
    }
  };

  const getOverallStatusColor = (status: string) => {
    switch (status) {
      case 'passed':
        return 'text-green-600';
      case 'failed':
        return 'text-red-600';
      case 'warning':
        return 'text-yellow-600';
      default:
        return 'text-gray-600';
    }
  };

  const canContinue = overallStatus === 'passed' || overallStatus === 'warning';
  const hasErrors = overallStatus === 'failed';

  return (
    <Card className="w-full">
      <CardHeader>
        <CardTitle className={`flex items-center gap-2 ${getOverallStatusColor(overallStatus)}`}>
          {getStatusIcon(overallStatus)}
          {title}
        </CardTitle>
        <CardDescription>{description}</CardDescription>
        <div className="flex items-center gap-2">
          {getStatusBadge(overallStatus)}
          {summary && (
            <span className="text-sm text-gray-600">{summary}</span>
          )}
        </div>
      </CardHeader>
      <CardContent className="space-y-6">
        {showDetails && results.length > 0 && (
          <div className="space-y-3">
            <h4 className="font-medium text-sm text-gray-900">Validation Results</h4>
            <div className="space-y-2">
              {results.map((result) => (
                <div key={result.id} className="flex items-start gap-3 p-3 bg-gray-50 rounded-md">
                  {getStatusIcon(result.status)}
                  <div className="flex-1 min-w-0">
                    <div className="flex items-center gap-2">
                      <span className="font-medium text-sm text-gray-900">{result.name}</span>
                      {getStatusBadge(result.status)}
                    </div>
                    <p className="text-sm text-gray-600 mt-1">{result.message}</p>
                    {result.details && (
                      <p className="text-xs text-gray-500 mt-1">{result.details}</p>
                    )}
                  </div>
                </div>
              ))}
            </div>
          </div>
        )}

        {hasErrors && (
          <div className="p-4 bg-red-50 border border-red-200 rounded-md">
            <div className="flex items-start gap-2">
              <XCircle className="h-5 w-5 text-red-500 mt-0.5" />
              <div>
                <h4 className="font-medium text-red-800">Validation Failed</h4>
                <p className="text-sm text-red-700 mt-1">
                  Please review the errors above and try again.
                </p>
              </div>
            </div>
          </div>
        )}

        {overallStatus === 'warning' && (
          <div className="p-4 bg-yellow-50 border border-yellow-200 rounded-md">
            <div className="flex items-start gap-2">
              <AlertTriangle className="h-5 w-5 text-yellow-500 mt-0.5" />
              <div>
                <h4 className="font-medium text-yellow-800">Validation Warnings</h4>
                <p className="text-sm text-yellow-700 mt-1">
                  The validation completed with warnings. You can continue or review the issues.
                </p>
              </div>
            </div>
          </div>
        )}

        {overallStatus === 'passed' && (
          <div className="p-4 bg-green-50 border border-green-200 rounded-md">
            <div className="flex items-start gap-2">
              <CheckCircle className="h-5 w-5 text-green-500 mt-0.5" />
              <div>
                <h4 className="font-medium text-green-800">Validation Passed</h4>
                <p className="text-sm text-green-700 mt-1">
                  All validations completed successfully. You can proceed to the next step.
                </p>
              </div>
            </div>
          </div>
        )}

        <div className="flex justify-between pt-4">
          <div className="flex gap-2">
            <Button onClick={onBack} variant="outline" disabled={isLoading}>
              Back
            </Button>
            {onRetry && hasErrors && (
              <Button onClick={onRetry} variant="outline" disabled={isLoading}>
                <RefreshCw className="h-4 w-4 mr-2" />
                Retry
              </Button>
            )}
          </div>
          <Button
            onClick={onContinue}
            disabled={!canContinue || isLoading}
            className="min-w-[100px]"
          >
            {isLoading ? 'Processing...' : 'Continue'}
          </Button>
        </div>
      </CardContent>
    </Card>
  );
};

export default ValidationStepComponent;
