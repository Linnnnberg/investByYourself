'use client';

import { useState } from 'react';
import { Button } from '@/components/ui/button';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card';
import { Tabs, TabsContent, TabsList, TabsTrigger } from '@/components/ui/tabs';
import { Badge } from '@/components/ui/badge';
import {
  Plus,
  Settings,
  Upload,
  Zap,
  Target,
  PieChart,
  TrendingUp,
  Shield
} from 'lucide-react';

interface PortfolioCreationWizardProps {
  onWorkflowStart: (workflowId: string, context: any) => void;
  onClose: () => void;
}

export default function PortfolioCreationWizard({
  onWorkflowStart,
  onClose
}: PortfolioCreationWizardProps) {
  const [selectedMethod, setSelectedMethod] = useState<string>('');

  const creationMethods = [
    {
      id: 'quick_start',
      title: 'Quick Start',
      description: 'Create a portfolio using proven templates',
      icon: <Zap className="h-6 w-6" />,
      features: ['Pre-built allocation templates', 'Risk-based recommendations', '5-minute setup'],
      workflowId: 'comprehensive_portfolio_creation',
      badge: 'Recommended'
    },
    {
      id: 'custom_builder',
      title: 'Custom Builder',
      description: 'Build your own allocation framework',
      icon: <Settings className="h-6 w-6" />,
      features: ['Drag-and-drop interface', 'Custom asset classes', 'Advanced constraints'],
      workflowId: 'advanced_allocation_framework',
      badge: 'Advanced'
    },
    {
      id: 'import_portfolio',
      title: 'Import Portfolio',
      description: 'Upload existing portfolio or CSV file',
      icon: <Upload className="h-6 w-6" />,
      features: ['CSV/JSON import', 'Broker integration', 'Manual entry'],
      workflowId: 'portfolio_import_workflow',
      badge: 'Coming Soon'
    }
  ];

  const templatePortfolios = [
    {
      id: 'conservative',
      name: 'Conservative Growth',
      description: 'Low risk, steady growth portfolio',
      allocation: { 'Bonds': 60, 'Stocks': 30, 'Cash': 10 },
      riskLevel: 'Low',
      expectedReturn: '4-6%',
      volatility: '5-8%'
    },
    {
      id: 'balanced',
      name: 'Balanced Growth',
      description: 'Moderate risk, balanced approach',
      allocation: { 'Stocks': 60, 'Bonds': 30, 'Alternatives': 10 },
      riskLevel: 'Medium',
      expectedReturn: '6-8%',
      volatility: '8-12%'
    },
    {
      id: 'aggressive',
      name: 'Aggressive Growth',
      description: 'High growth potential portfolio',
      allocation: { 'Stocks': 80, 'Bonds': 15, 'Alternatives': 5 },
      riskLevel: 'High',
      expectedReturn: '8-12%',
      volatility: '12-18%'
    }
  ];

  const handleMethodSelect = (methodId: string) => {
    setSelectedMethod(methodId);
  };

  const handleStartWorkflow = (workflowId: string, context: any = {}) => {
    onWorkflowStart(workflowId, {
      ...context,
      creationMethod: selectedMethod,
      timestamp: new Date().toISOString()
    });
  };

  const handleTemplateSelect = (templateId: string) => {
    const template = templatePortfolios.find(t => t.id === templateId);
    if (template) {
      handleStartWorkflow('comprehensive_portfolio_creation', {
        template: template,
        quickStart: true
      });
    }
  };

  return (
    <div className="fixed inset-0 bg-black/50 flex items-center justify-center p-4 z-50">
      <Card className="w-full max-w-4xl max-h-[90vh] overflow-y-auto">
        <CardHeader>
          <div className="flex items-center justify-between">
            <div>
              <CardTitle className="text-2xl">Create New Portfolio</CardTitle>
              <CardDescription>
                Choose how you'd like to create your investment portfolio
              </CardDescription>
            </div>
            <Button variant="ghost" size="sm" onClick={onClose}>
              ✕
            </Button>
          </div>
        </CardHeader>
        <CardContent>
          <Tabs defaultValue="quick_start" className="w-full">
            <TabsList className="grid w-full grid-cols-3">
              <TabsTrigger value="quick_start">Quick Start</TabsTrigger>
              <TabsTrigger value="custom_builder">Custom Builder</TabsTrigger>
              <TabsTrigger value="import_portfolio">Import</TabsTrigger>
            </TabsList>

            <TabsContent value="quick_start" className="space-y-6">
              <div className="text-center py-4">
                <h3 className="text-lg font-semibold mb-2">Choose a Template</h3>
                <p className="text-muted-foreground">
                  Start with a proven allocation strategy
                </p>
              </div>

              <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
                {templatePortfolios.map((template) => (
                  <Card
                    key={template.id}
                    className="cursor-pointer hover:shadow-md transition-shadow"
                    onClick={() => handleTemplateSelect(template.id)}
                  >
                    <CardHeader className="pb-3">
                      <div className="flex items-center justify-between">
                        <CardTitle className="text-lg">{template.name}</CardTitle>
                        <Badge variant={
                          template.riskLevel === 'Low' ? 'default' :
                          template.riskLevel === 'Medium' ? 'secondary' : 'destructive'
                        }>
                          {template.riskLevel} Risk
                        </Badge>
                      </div>
                      <CardDescription>{template.description}</CardDescription>
                    </CardHeader>
                    <CardContent className="space-y-3">
                      <div className="space-y-2">
                        <h4 className="text-sm font-medium">Allocation</h4>
                        <div className="space-y-1">
                          {Object.entries(template.allocation).map(([asset, weight]) => (
                            <div key={asset} className="flex justify-between text-sm">
                              <span>{asset}</span>
                              <span className="font-medium">{weight}%</span>
                            </div>
                          ))}
                        </div>
                      </div>
                      <div className="grid grid-cols-2 gap-2 text-sm">
                        <div>
                          <span className="text-muted-foreground">Expected Return:</span>
                          <div className="font-medium">{template.expectedReturn}</div>
                        </div>
                        <div>
                          <span className="text-muted-foreground">Volatility:</span>
                          <div className="font-medium">{template.volatility}</div>
                        </div>
                      </div>
                    </CardContent>
                  </Card>
                ))}
              </div>
            </TabsContent>

            <TabsContent value="custom_builder" className="space-y-6">
              <div className="text-center py-4">
                <Settings className="h-12 w-12 mx-auto mb-4 text-blue-600" />
                <h3 className="text-lg font-semibold mb-2">Custom Portfolio Builder</h3>
                <p className="text-muted-foreground">
                  Build your own allocation framework with advanced controls
                </p>
              </div>

              <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
                <Card>
                  <CardHeader>
                    <CardTitle className="flex items-center gap-2">
                      <Target className="h-5 w-5" />
                      Framework Builder
                    </CardTitle>
                    <CardDescription>
                      Create custom asset allocation frameworks
                    </CardDescription>
                  </CardHeader>
                  <CardContent className="space-y-3">
                    <ul className="space-y-2 text-sm">
                      <li className="flex items-center gap-2">
                        <div className="w-2 h-2 bg-blue-600 rounded-full" />
                        Drag-and-drop asset classes
                      </li>
                      <li className="flex items-center gap-2">
                        <div className="w-2 h-2 bg-blue-600 rounded-full" />
                        Set custom weight constraints
                      </li>
                      <li className="flex items-center gap-2">
                        <div className="w-2 h-2 bg-blue-600 rounded-full" />
                        Define rebalancing rules
                      </li>
                    </ul>
                    <Button
                      className="w-full"
                      onClick={() => handleStartWorkflow('advanced_allocation_framework')}
                    >
                      Start Custom Builder
                    </Button>
                  </CardContent>
                </Card>

                <Card>
                  <CardHeader>
                    <CardTitle className="flex items-center gap-2">
                      <PieChart className="h-5 w-5" />
                      Factor-Based Investing
                    </CardTitle>
                    <CardDescription>
                      Advanced allocation using risk factors
                    </CardDescription>
                  </CardHeader>
                  <CardContent className="space-y-3">
                    <ul className="space-y-2 text-sm">
                      <li className="flex items-center gap-2">
                        <div className="w-2 h-2 bg-green-600 rounded-full" />
                        Risk parity allocation
                      </li>
                      <li className="flex items-center gap-2">
                        <div className="w-2 h-2 bg-green-600 rounded-full" />
                        Factor exposure analysis
                      </li>
                      <li className="flex items-center gap-2">
                        <div className="w-2 h-2 bg-green-600 rounded-full" />
                        Dynamic rebalancing
                      </li>
                    </ul>
                    <Button
                      variant="outline"
                      className="w-full"
                      onClick={() => handleStartWorkflow('advanced_allocation_framework', {
                        mode: 'factor_based'
                      })}
                    >
                      Start Factor Analysis
                    </Button>
                  </CardContent>
                </Card>
              </div>
            </TabsContent>

            <TabsContent value="import_portfolio" className="space-y-6">
              <div className="text-center py-4">
                <Upload className="h-12 w-12 mx-auto mb-4 text-orange-600" />
                <h3 className="text-lg font-semibold mb-2">Import Portfolio</h3>
                <p className="text-muted-foreground">
                  Upload your existing portfolio or connect to your broker
                </p>
              </div>

              <Card>
                <CardContent className="pt-6">
                  <div className="text-center">
                    <div className="border-2 border-dashed border-gray-300 rounded-lg p-8">
                      <Upload className="h-12 w-12 mx-auto mb-4 text-gray-400" />
                      <h4 className="text-lg font-medium mb-2">Coming Soon</h4>
                      <p className="text-muted-foreground mb-4">
                        Portfolio import functionality is under development
                      </p>
                      <Button variant="outline" disabled>
                        Upload Portfolio
                      </Button>
                    </div>
                  </div>
                </CardContent>
              </Card>
            </TabsContent>
          </Tabs>
        </CardContent>
      </Card>
    </div>
  );
}
