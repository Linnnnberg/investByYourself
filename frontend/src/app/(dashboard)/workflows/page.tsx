"use client";

import React, { useState } from 'react';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Tabs, TabsContent, TabsList, TabsTrigger } from '@/components/ui/tabs';
import MinimalWorkflowEngine from '@/components/workflows/MinimalWorkflowEngine';
import { WorkflowList } from '@/components/workflows/WorkflowList';
import { useWorkflows } from '@/hooks/useWorkflows';
import { WorkflowDefinition, WorkflowContext } from '@/types/workflow';

export default function WorkflowsPage() {
  const [selectedWorkflow, setSelectedWorkflow] = useState<WorkflowDefinition | null>(null);
  const [activeTab, setActiveTab] = useState('list');

  const { workflows, isLoading, error } = useWorkflows({ autoFetch: true });

  const handleSelectWorkflow = (workflow: WorkflowDefinition) => {
    setSelectedWorkflow(workflow);
    setActiveTab('execute');
  };

  const handleComplete = (result: any) => {
    console.log('Workflow completed:', result);
    // Show success message or redirect
    setActiveTab('list');
    setSelectedWorkflow(null);
  };

  const handleError = (error: any) => {
    console.error('Workflow error:', error);
    // Show error message
  };

  const handleStepComplete = (stepId: string, result: any) => {
    console.log('Step completed:', stepId, result);
  };

  const handleBackToList = () => {
    setActiveTab('list');
    setSelectedWorkflow(null);
  };

  // Mock context - in real app, this would come from user session
  const mockContext: WorkflowContext = {
    user_id: 'demo_user',
    session_id: 'demo_session',
    data: {}
  };

  return (
    <div className="container mx-auto py-8">
      <div className="mb-8">
        <h1 className="text-3xl font-bold">Workflow Engine</h1>
        <p className="text-muted-foreground mt-2">
          Interactive workflow engine for portfolio creation and management
        </p>
      </div>

      <Tabs value={activeTab} onValueChange={setActiveTab} className="w-full">
        <TabsList className="grid w-full grid-cols-3">
          <TabsTrigger value="list">Available Workflows</TabsTrigger>
          <TabsTrigger value="execute" disabled={!selectedWorkflow}>
            Execute Workflow
          </TabsTrigger>
          <TabsTrigger value="demo">Component Demo</TabsTrigger>
        </TabsList>

        <TabsContent value="list" className="mt-6">
          <WorkflowList
            onSelectWorkflow={handleSelectWorkflow}
            onViewExecutions={() => console.log('View executions')}
          />
        </TabsContent>

        <TabsContent value="execute" className="mt-6">
          {selectedWorkflow ? (
            <div className="space-y-4">
              <div className="flex items-center justify-between">
                <div>
                  <h2 className="text-xl font-semibold">{selectedWorkflow.name}</h2>
                  <p className="text-muted-foreground">{selectedWorkflow.description}</p>
                </div>
                <Button variant="outline" onClick={handleBackToList}>
                  Back to List
                </Button>
              </div>

              <MinimalWorkflowEngine
                workflow={selectedWorkflow}
                context={mockContext}
                onComplete={handleComplete}
                onError={handleError}
                onStepComplete={handleStepComplete}
              />
            </div>
          ) : (
            <Card>
              <CardContent className="p-8 text-center">
                <p className="text-muted-foreground">No workflow selected</p>
                <Button
                  variant="outline"
                  onClick={() => setActiveTab('list')}
                  className="mt-2"
                >
                  Select a Workflow
                </Button>
              </CardContent>
            </Card>
          )}
        </TabsContent>

        <TabsContent value="demo" className="mt-6">
          <Card>
            <CardHeader>
              <CardTitle>Component Demo</CardTitle>
              <CardDescription>
                Interactive demonstration of enhanced workflow step components
              </CardDescription>
            </CardHeader>
            <CardContent>
              <div className="text-center">
                <p className="text-muted-foreground mb-4">
                  Visit the component demo page to see all enhanced step components in action.
                </p>
                <a href="/workflows/demo">
                  <Button>View Component Demo</Button>
                </a>
              </div>
            </CardContent>
          </Card>
        </TabsContent>
      </Tabs>
    </div>
  );
}
