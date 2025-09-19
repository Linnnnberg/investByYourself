/**
 * Workflow List Component
 * InvestByYourself Financial Platform
 *
 * Component for displaying and managing workflow definitions.
 */

import React from 'react';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Badge } from '@/components/ui/badge';
import { Alert, AlertDescription } from '@/components/ui/alert';
import { Play, Clock, CheckCircle, XCircle, Loader2 } from 'lucide-react';
import { WorkflowDefinition, WorkflowExecutionResponse, WorkflowStatus } from '@/types/workflow';
import { useWorkflows } from '@/hooks/useWorkflows';

interface WorkflowListProps {
  onSelectWorkflow?: (workflow: WorkflowDefinition) => void;
  onViewExecutions?: () => void;
  category?: string;
  showExecutions?: boolean;
}

export function WorkflowList({
  onSelectWorkflow,
  onViewExecutions,
  category,
  showExecutions = true
}: WorkflowListProps) {
  const {
    workflows,
    executions,
    isLoading,
    error,
    fetchWorkflows,
    fetchExecutions,
    refresh
  } = useWorkflows({
    autoFetch: true,
    category
  });

  const getStatusIcon = (status: WorkflowStatus) => {
    switch (status) {
      case 'completed':
        return <CheckCircle className="h-4 w-4 text-green-500" />;
      case 'failed':
        return <XCircle className="h-4 w-4 text-red-500" />;
      case 'running':
        return <Loader2 className="h-4 w-4 text-blue-500 animate-spin" />;
      default:
        return <Clock className="h-4 w-4 text-gray-500" />;
    }
  };

  const getStatusColor = (status: WorkflowStatus) => {
    switch (status) {
      case 'completed':
        return 'bg-green-100 text-green-800';
      case 'failed':
        return 'bg-red-100 text-red-800';
      case 'running':
        return 'bg-blue-100 text-blue-800';
      case 'paused':
        return 'bg-yellow-100 text-yellow-800';
      default:
        return 'bg-gray-100 text-gray-800';
    }
  };

  if (isLoading && workflows.length === 0) {
    return (
      <div className="flex items-center justify-center p-8">
        <Loader2 className="h-8 w-8 animate-spin" />
        <span className="ml-2">Loading workflows...</span>
      </div>
    );
  }

  if (error) {
    return (
      <Alert variant="destructive">
        <AlertDescription>
          Failed to load workflows: {error.message}
          <Button
            variant="outline"
            size="sm"
            onClick={refresh}
            className="ml-2"
          >
            Retry
          </Button>
        </AlertDescription>
      </Alert>
    );
  }

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex items-center justify-between">
        <div>
          <h2 className="text-2xl font-bold">Available Workflows</h2>
          <p className="text-muted-foreground">
            Choose a workflow to start your investment journey
          </p>
        </div>
        <div className="flex gap-2">
          <Button variant="outline" onClick={refresh} disabled={isLoading}>
            {isLoading ? <Loader2 className="h-4 w-4 animate-spin" /> : 'Refresh'}
          </Button>
          {showExecutions && onViewExecutions && (
            <Button variant="outline" onClick={onViewExecutions}>
              View Executions
            </Button>
          )}
        </div>
      </div>

      {/* Workflows Grid */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
        {workflows.map((workflow) => (
          <Card key={workflow.id} className="hover:shadow-lg transition-shadow">
            <CardHeader>
              <div className="flex items-start justify-between">
                <div>
                  <CardTitle className="text-lg">{workflow.name}</CardTitle>
                  <CardDescription className="mt-1">
                    {workflow.description}
                  </CardDescription>
                </div>
                {workflow.category && (
                  <Badge variant="secondary">{workflow.category}</Badge>
                )}
              </div>
            </CardHeader>
            <CardContent className="space-y-4">
              <div className="space-y-2">
                <div className="flex items-center justify-between text-sm">
                  <span className="text-muted-foreground">Steps:</span>
                  <span className="font-medium">{workflow.steps.length}</span>
                </div>
                <div className="flex items-center justify-between text-sm">
                  <span className="text-muted-foreground">Version:</span>
                  <span className="font-medium">{workflow.version}</span>
                </div>
                {workflow.ai_configurable && (
                  <div className="flex items-center gap-1 text-sm text-blue-600">
                    <span>🤖</span>
                    <span>AI Configurable</span>
                  </div>
                )}
              </div>

              <div className="flex gap-2">
                <Button
                  onClick={() => onSelectWorkflow?.(workflow)}
                  className="flex-1"
                >
                  <Play className="h-4 w-4 mr-2" />
                  Start Workflow
                </Button>
              </div>
            </CardContent>
          </Card>
        ))}
      </div>

      {/* Recent Executions */}
      {showExecutions && executions.length > 0 && (
        <div className="space-y-4">
          <h3 className="text-lg font-semibold">Recent Executions</h3>
          <div className="space-y-2">
            {executions.slice(0, 5).map((execution) => (
              <Card key={execution.execution_id} className="p-4">
                <div className="flex items-center justify-between">
                  <div className="flex items-center gap-3">
                    {getStatusIcon(execution.status as WorkflowStatus)}
                    <div>
                      <p className="font-medium">{execution.workflow_id}</p>
                      <p className="text-sm text-muted-foreground">
                        Started: {new Date(execution.started_at).toLocaleString()}
                      </p>
                    </div>
                  </div>
                  <div className="flex items-center gap-2">
                    <Badge className={getStatusColor(execution.status as WorkflowStatus)}>
                      {execution.status}
                    </Badge>
                    <span className="text-sm text-muted-foreground">
                      {Math.round(execution.progress)}%
                    </span>
                  </div>
                </div>
              </Card>
            ))}
          </div>
        </div>
      )}

      {workflows.length === 0 && (
        <div className="text-center py-8">
          <p className="text-muted-foreground">No workflows available</p>
          <Button variant="outline" onClick={refresh} className="mt-2">
            Refresh
          </Button>
        </div>
      )}
    </div>
  );
}
