'use client';

import { useState, useEffect } from 'react';
import Link from 'next/link';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Badge } from '@/components/ui/badge';
import { useWorkflowExecution } from '@/hooks/useWorkflowExecution';
import { WorkflowDefinition, WorkflowContext } from '@/types/workflow';
import RealWorkflowEngine from '@/components/workflows/RealWorkflowEngine';
import AppLayout from '@/components/layouts/AppLayout';

// Mock workflow data for demo
const mockWorkflow: WorkflowDefinition = {
  id: 'portfolio-creation-workflow',
  name: 'Portfolio Creation Workflow',
  description: 'AI-powered workflow to guide you through creating an optimal investment portfolio',
  version: '1.0.0',
  steps: [
    {
      id: 'risk-assessment',
      name: 'Risk Assessment',
      description: 'Evaluate your risk tolerance and investment goals',
      step_type: 'data_collection',
      dependencies: [],
      config: {
        fields: [
          { id: 'age', label: 'Age', type: 'number', required: true },
          { id: 'income', label: 'Annual Income', type: 'number', required: true },
          { id: 'risk_tolerance', label: 'Risk Tolerance', type: 'select', required: true, options: ['Conservative', 'Moderate', 'Aggressive'] }
        ]
      }
    },
    {
      id: 'investment-goals',
      name: 'Investment Goals',
      description: 'Define your investment objectives and timeline',
      step_type: 'decision',
      dependencies: ['risk-assessment'],
      config: {
        options: [
          { id: 'retirement', label: 'Retirement Planning', value: 'retirement' },
          { id: 'wealth-building', label: 'Wealth Building', value: 'wealth-building' },
          { id: 'income-generation', label: 'Income Generation', value: 'income-generation' }
        ],
        inputType: 'radio',
        required: true
      }
    },
    {
      id: 'asset-allocation',
      name: 'Asset Allocation',
      description: 'Determine optimal asset allocation based on your profile',
      step_type: 'validation',
      dependencies: ['risk-assessment', 'investment-goals'],
      config: {
        overallStatus: 'pending',
        results: [],
        summary: 'Calculating optimal asset allocation...'
      }
    }
  ],
  entry_points: ['risk-assessment'],
  exit_points: ['asset-allocation'],
  created_at: new Date().toISOString()
};

const mockContext: WorkflowContext = {
  workflow_id: 'portfolio-creation-workflow',
  execution_id: 'exec-123',
  data: {},
  status: 'pending',
  current_step: 'risk-assessment',
  created_at: new Date().toISOString(),
  updated_at: new Date().toISOString()
};

export default function WorkflowsPage() {
  const [selectedWorkflow, setSelectedWorkflow] = useState<WorkflowDefinition | null>(null);
  const [workflowContext, setWorkflowContext] = useState<WorkflowContext>(mockContext);

  const handleWorkflowComplete = (result: any) => {
    console.log('Workflow completed:', result);
    setSelectedWorkflow(null);
  };

  const handleWorkflowError = (error: any) => {
    console.error('Workflow error:', error);
    setSelectedWorkflow(null);
  };

  const handleStepComplete = (stepId: string, result: any) => {
    console.log('Step completed:', stepId, result);
    setWorkflowContext(prev => ({
      ...prev,
      data: { ...prev.data, [stepId]: result }
    }));
  };

  if (selectedWorkflow) {
    return (
      <AppLayout>
        <div className="max-w-6xl mx-auto">
          <div className="mb-6">
            <Button
              variant="outline"
              onClick={() => setSelectedWorkflow(null)}
              className="mb-4"
            >
              ← Back to Workflows
            </Button>
            <h1 className="text-3xl font-bold text-gray-900">{selectedWorkflow.name}</h1>
            <p className="text-gray-600 mt-2">{selectedWorkflow.description}</p>
          </div>

          <RealWorkflowEngine
            workflow={selectedWorkflow}
            context={workflowContext}
            onComplete={handleWorkflowComplete}
            onError={handleWorkflowError}
            onStepComplete={handleStepComplete}
          />
        </div>
      </AppLayout>
    );
  }

  return (
    <AppLayout>
      <div className="mb-6">
        <div className="mb-8">
          <h1 className="text-3xl font-bold text-gray-900">AI-Powered Workflows</h1>
          <p className="text-gray-600 mt-2">
            Intelligent workflows that guide you through complex investment decisions
          </p>
        </div>

        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
          {/* Portfolio Creation Workflow */}
          <Card className="hover:shadow-lg transition-shadow cursor-pointer" onClick={() => setSelectedWorkflow(mockWorkflow)}>
            <CardHeader>
              <div className="flex items-center justify-between">
                <CardTitle className="text-lg">Portfolio Creation</CardTitle>
                <Badge variant="default">Active</Badge>
              </div>
            </CardHeader>
            <CardContent>
              <p className="text-gray-600 mb-4">
                AI-powered workflow to guide you through creating an optimal investment portfolio based on your risk profile and goals.
              </p>
              <div className="space-y-2">
                <div className="flex items-center text-sm text-gray-500">
                  <span className="w-2 h-2 bg-blue-500 rounded-full mr-2"></span>
                  3 Steps
                </div>
                <div className="flex items-center text-sm text-gray-500">
                  <span className="w-2 h-2 bg-green-500 rounded-full mr-2"></span>
                  Risk Assessment
                </div>
                <div className="flex items-center text-sm text-gray-500">
                  <span className="w-2 h-2 bg-yellow-500 rounded-full mr-2"></span>
                  Goal Setting
                </div>
              </div>
            </CardContent>
          </Card>

          {/* Risk Assessment Workflow */}
          <Card className="hover:shadow-lg transition-shadow cursor-pointer">
            <CardHeader>
              <div className="flex items-center justify-between">
                <CardTitle className="text-lg">Risk Assessment</CardTitle>
                <Badge variant="secondary">Coming Soon</Badge>
              </div>
            </CardHeader>
            <CardContent>
              <p className="text-gray-600 mb-4">
                Comprehensive risk evaluation to determine your optimal investment strategy and asset allocation.
              </p>
              <div className="space-y-2">
                <div className="flex items-center text-sm text-gray-500">
                  <span className="w-2 h-2 bg-gray-400 rounded-full mr-2"></span>
                  5 Steps
                </div>
                <div className="flex items-center text-sm text-gray-500">
                  <span className="w-2 h-2 bg-gray-400 rounded-full mr-2"></span>
                  Questionnaire
                </div>
                <div className="flex items-center text-sm text-gray-500">
                  <span className="w-2 h-2 bg-gray-400 rounded-full mr-2"></span>
                  Analysis
                </div>
              </div>
            </CardContent>
          </Card>

          {/* Rebalancing Workflow */}
          <Card className="hover:shadow-lg transition-shadow cursor-pointer">
            <CardHeader>
              <div className="flex items-center justify-between">
                <CardTitle className="text-lg">Portfolio Rebalancing</CardTitle>
                <Badge variant="secondary">Coming Soon</Badge>
              </div>
            </CardHeader>
            <CardContent>
              <p className="text-gray-600 mb-4">
                Automated workflow to help you rebalance your portfolio based on market conditions and your investment goals.
              </p>
              <div className="space-y-2">
                <div className="flex items-center text-sm text-gray-500">
                  <span className="w-2 h-2 bg-gray-400 rounded-full mr-2"></span>
                  4 Steps
                </div>
                <div className="flex items-center text-sm text-gray-500">
                  <span className="w-2 h-2 bg-gray-400 rounded-full mr-2"></span>
                  Analysis
                </div>
                <div className="flex items-center text-sm text-gray-500">
                  <span className="w-2 h-2 bg-gray-400 rounded-full mr-2"></span>
                  Recommendations
                </div>
              </div>
            </CardContent>
          </Card>
        </div>

        {/* Workflow Features */}
        <div className="mt-12">
          <h2 className="text-2xl font-bold text-gray-900 mb-6">Why Use AI Workflows?</h2>
          <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
            <div className="text-center">
              <div className="text-4xl mb-4">🤖</div>
              <h3 className="text-lg font-semibold mb-2">Intelligent Guidance</h3>
              <p className="text-gray-600">
                AI-powered recommendations based on your unique financial situation and market conditions.
              </p>
            </div>
            <div className="text-center">
              <div className="text-4xl mb-4">📊</div>
              <h3 className="text-lg font-semibold mb-2">Data-Driven Decisions</h3>
              <p className="text-gray-600">
                Make informed investment decisions using comprehensive market data and analysis.
              </p>
            </div>
            <div className="text-center">
              <div className="text-4xl mb-4">⚡</div>
              <h3 className="text-lg font-semibold mb-2">Streamlined Process</h3>
              <p className="text-gray-600">
                Complex investment processes simplified into easy-to-follow, step-by-step workflows.
              </p>
            </div>
          </div>
        </div>
      </div>
    </AppLayout>
  );
}
