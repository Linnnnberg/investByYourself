'use client';

import { useState } from 'react';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Badge } from '@/components/ui/badge';
import { Tabs, TabsContent, TabsList, TabsTrigger } from '@/components/ui/tabs';

// Allocation Framework Templates
const ALLOCATION_TEMPLATES = [
  {
    id: 'conservative',
    name: 'Conservative',
    description: 'Low risk, income-focused allocation',
    riskLevel: 'Low',
    allocations: [
      { asset: 'Bonds', percentage: 60, color: 'bg-blue-500' },
      { asset: 'Stocks', percentage: 30, color: 'bg-green-500' },
      { asset: 'Cash', percentage: 10, color: 'bg-gray-500' }
    ]
  },
  {
    id: 'balanced',
    name: 'Balanced',
    description: 'Moderate risk, growth and income balance',
    riskLevel: 'Medium',
    allocations: [
      { asset: 'Stocks', percentage: 60, color: 'bg-green-500' },
      { asset: 'Bonds', percentage: 30, color: 'bg-blue-500' },
      { asset: 'Cash', percentage: 10, color: 'bg-gray-500' }
    ]
  },
  {
    id: 'growth',
    name: 'Growth',
    description: 'Higher risk, growth-focused allocation',
    riskLevel: 'High',
    allocations: [
      { asset: 'Stocks', percentage: 80, color: 'bg-green-500' },
      { asset: 'Bonds', percentage: 15, color: 'bg-blue-500' },
      { asset: 'Cash', percentage: 5, color: 'bg-gray-500' }
    ]
  },
  {
    id: 'aggressive',
    name: 'Aggressive Growth',
    description: 'Highest risk, maximum growth potential',
    riskLevel: 'Very High',
    allocations: [
      { asset: 'Stocks', percentage: 90, color: 'bg-green-500' },
      { asset: 'Bonds', percentage: 5, color: 'bg-blue-500' },
      { asset: 'Cash', percentage: 5, color: 'bg-gray-500' }
    ]
  }
];

interface AllocationTemplate {
  id: string;
  name: string;
  description: string;
  riskLevel: string;
  allocations: Array<{
    asset: string;
    percentage: number;
    color: string;
  }>;
}

interface PortfolioConstructionProps {
  onFrameworkSelect?: (framework: AllocationTemplate) => void;
  onCustomBuild?: () => void;
  onImport?: () => void;
}

export default function PortfolioConstruction({
  onFrameworkSelect,
  onCustomBuild,
  onImport
}: PortfolioConstructionProps) {
  const [selectedTemplate, setSelectedTemplate] = useState<string | null>(null);
  const [activeTab, setActiveTab] = useState('templates');

  const handleTemplateSelect = (template: AllocationTemplate) => {
    setSelectedTemplate(template.id);
    onFrameworkSelect?.(template);
  };

  return (
    <div className="space-y-6">
      <div className="text-center">
        <h2 className="text-2xl font-bold text-gray-900 mb-2">Portfolio Construction</h2>
        <p className="text-gray-600">
          Choose an allocation framework to guide your portfolio construction
        </p>
      </div>

      <Tabs value={activeTab} onValueChange={setActiveTab}>
        <TabsList className="grid w-full grid-cols-3">
          <TabsTrigger value="templates">Templates</TabsTrigger>
          <TabsTrigger value="custom">Custom</TabsTrigger>
          <TabsTrigger value="import">Import</TabsTrigger>
        </TabsList>

        {/* Templates Tab */}
        <TabsContent value="templates" className="space-y-6">
          <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
            {ALLOCATION_TEMPLATES.map((template) => (
              <Card
                key={template.id}
                className={`cursor-pointer transition-all hover:shadow-lg ${
                  selectedTemplate === template.id
                    ? 'ring-2 ring-blue-500 border-blue-500'
                    : 'hover:border-blue-300'
                }`}
                onClick={() => handleTemplateSelect(template)}
              >
                <CardHeader>
                  <div className="flex items-center justify-between">
                    <CardTitle className="text-lg">{template.name}</CardTitle>
                    <Badge
                      variant={
                        template.riskLevel === 'Low' ? 'secondary' :
                        template.riskLevel === 'Medium' ? 'default' :
                        template.riskLevel === 'High' ? 'destructive' : 'destructive'
                      }
                    >
                      {template.riskLevel}
                    </Badge>
                  </div>
                  <p className="text-sm text-gray-600">{template.description}</p>
                </CardHeader>
                <CardContent>
                  <div className="space-y-3">
                    <h4 className="font-semibold text-sm">Allocation Breakdown:</h4>
                    <div className="space-y-2">
                      {template.allocations.map((allocation, index) => (
                        <div key={index} className="flex items-center justify-between">
                          <div className="flex items-center space-x-2">
                            <div className={`w-3 h-3 rounded-full ${allocation.color}`}></div>
                            <span className="text-sm">{allocation.asset}</span>
                          </div>
                          <span className="text-sm font-semibold">{allocation.percentage}%</span>
                        </div>
                      ))}
                    </div>
                    <div className="pt-3 border-t">
                      <div className="flex space-x-2">
                        <div className="flex-1 h-2 bg-gray-200 rounded-full overflow-hidden">
                          {template.allocations.map((allocation, index) => (
                            <div
                              key={index}
                              className={`h-full ${allocation.color.replace('bg-', 'bg-')}`}
                              style={{ width: `${allocation.percentage}%` }}
                            ></div>
                          ))}
                        </div>
                      </div>
                    </div>
                  </div>
                </CardContent>
              </Card>
            ))}
          </div>

          {selectedTemplate && (
            <Card className="border-blue-200 bg-blue-50">
              <CardContent className="p-6">
                <div className="flex items-center justify-between">
                  <div>
                    <h3 className="text-lg font-semibold text-blue-900">
                      {ALLOCATION_TEMPLATES.find(t => t.id === selectedTemplate)?.name} Selected
                    </h3>
                    <p className="text-blue-700">
                      Ready to proceed with this allocation framework
                    </p>
                  </div>
                  <Button className="bg-blue-600 hover:bg-blue-700">
                    Continue with Template
                  </Button>
                </div>
              </CardContent>
            </Card>
          )}
        </TabsContent>

        {/* Custom Tab */}
        <TabsContent value="custom" className="space-y-6">
          <Card>
            <CardHeader>
              <CardTitle>Custom Allocation Framework</CardTitle>
              <p className="text-gray-600">
                Build your own allocation framework with custom asset classes and weights
              </p>
            </CardHeader>
            <CardContent>
              <div className="space-y-4">
                <div className="text-center py-8">
                  <div className="text-4xl mb-4">🛠️</div>
                  <h3 className="text-lg font-semibold mb-2">Custom Framework Builder</h3>
                  <p className="text-gray-600 mb-6">
                    Create a custom allocation framework tailored to your specific investment goals
                  </p>
                  <Button onClick={onCustomBuild} className="bg-green-600 hover:bg-green-700">
                    Start Building Custom Framework
                  </Button>
                </div>
              </div>
            </CardContent>
          </Card>
        </TabsContent>

        {/* Import Tab */}
        <TabsContent value="import" className="space-y-6">
          <Card>
            <CardHeader>
              <CardTitle>Import Allocation Framework</CardTitle>
              <p className="text-gray-600">
                Import allocation frameworks from JSON or CSV files
              </p>
            </CardHeader>
            <CardContent>
              <div className="space-y-4">
                <div className="text-center py-8">
                  <div className="text-4xl mb-4">📁</div>
                  <h3 className="text-lg font-semibold mb-2">Import Framework</h3>
                  <p className="text-gray-600 mb-6">
                    Upload your allocation framework from external sources
                  </p>
                  <div className="space-y-3">
                    <Button onClick={onImport} className="w-full">
                      Upload JSON/CSV File
                    </Button>
                    <Button variant="outline" className="w-full">
                      Download Template
                    </Button>
                  </div>
                </div>
              </div>
            </CardContent>
          </Card>
        </TabsContent>
      </Tabs>
    </div>
  );
}
