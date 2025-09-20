'use client';

import { useState } from 'react';
import { X, Check, AlertCircle, DollarSign, PieChart, TrendingUp } from 'lucide-react';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { Label } from '@/components/ui/label';
import { Textarea } from '@/components/ui/textarea';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Badge } from '@/components/ui/badge';

interface PortfolioTemplate {
  id: string;
  name: string;
  description: string;
  allocation: Record<string, number>;
  riskLevel: string;
  expectedReturn: string;
  volatility: string;
}

interface PortfolioTemplateConfirmationProps {
  template: PortfolioTemplate;
  onSave: (portfolioData: {
    name: string;
    description: string;
    allocation: Record<string, number>;
    riskLevel: string;
  }) => void;
  onDrop: () => void;
  onClose: () => void;
}

export default function PortfolioTemplateConfirmation({
  template,
  onSave,
  onDrop,
  onClose
}: PortfolioTemplateConfirmationProps) {
  const [portfolioName, setPortfolioName] = useState('');
  const [portfolioDescription, setPortfolioDescription] = useState(template.description);
  const [showDropConfirm, setShowDropConfirm] = useState(false);
  const [isSaving, setIsSaving] = useState(false);

  const handleSave = async () => {
    if (!portfolioName.trim()) {
      alert('Portfolio name is required');
      return;
    }

    setIsSaving(true);
    try {
      await onSave({
        name: portfolioName.trim(),
        description: portfolioDescription.trim(),
        allocation: template.allocation,
        riskLevel: template.riskLevel
      });
    } catch (error) {
      console.error('Error saving portfolio:', error);
      alert('Failed to save portfolio. Please try again.');
    } finally {
      setIsSaving(false);
    }
  };

  const handleDrop = () => {
    setShowDropConfirm(true);
  };

  const confirmDrop = () => {
    onDrop();
    setShowDropConfirm(false);
  };

  const formatAllocation = (allocation: Record<string, number>) => {
    return Object.entries(allocation)
      .sort(([,a], [,b]) => b - a)
      .map(([asset, weight]) => (
        <div key={asset} className="flex justify-between items-center py-1">
          <span className="text-sm font-medium">{asset}</span>
          <Badge variant="secondary" className="text-xs">
            {weight}%
          </Badge>
        </div>
      ));
  };

  const getRiskColor = (riskLevel: string) => {
    switch (riskLevel.toLowerCase()) {
      case 'low': return 'text-green-600 bg-green-50';
      case 'medium': return 'text-yellow-600 bg-yellow-50';
      case 'high': return 'text-red-600 bg-red-50';
      default: return 'text-gray-600 bg-gray-50';
    }
  };

  if (showDropConfirm) {
    return (
      <div className="fixed inset-0 bg-black/50 flex items-center justify-center p-4 z-50">
        <Card className="w-full max-w-md">
          <CardHeader className="text-center">
            <AlertCircle className="h-12 w-12 text-red-500 mx-auto mb-4" />
            <CardTitle className="text-xl">Drop Portfolio Draft?</CardTitle>
            <p className="text-gray-600">
              Are you sure you want to drop this portfolio draft? This action cannot be undone.
            </p>
          </CardHeader>
          <CardContent className="space-y-4">
            <div className="flex gap-3">
              <Button
                variant="outline"
                onClick={() => setShowDropConfirm(false)}
                className="flex-1"
              >
                Cancel
              </Button>
              <Button
                variant="outline"
                onClick={confirmDrop}
                className="flex-1 bg-red-600 text-white hover:bg-red-700"
              >
                Yes, Drop Draft
              </Button>
            </div>
          </CardContent>
        </Card>
      </div>
    );
  }

  return (
    <div className="fixed inset-0 bg-black/50 flex items-center justify-center p-4 z-50">
      <Card className="w-full max-w-2xl max-h-[90vh] overflow-y-auto">
        <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-4">
          <div>
            <CardTitle className="text-2xl">Portfolio Template Summary</CardTitle>
            <p className="text-gray-600">Review and customize your portfolio before saving</p>
          </div>
          <Button variant="ghost" onClick={onClose}>
            <X className="h-4 w-4" />
          </Button>
        </CardHeader>

        <CardContent className="space-y-6">
          {/* Template Overview */}
          <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
            <div className="space-y-4">
              <div>
                <h3 className="text-lg font-semibold mb-2">Template Details</h3>
                <div className="space-y-2">
                  <div className="flex items-center gap-2">
                    <DollarSign className="h-4 w-4 text-gray-500" />
                    <span className="font-medium">{template.name}</span>
                  </div>
                  <p className="text-sm text-gray-600">{template.description}</p>
                  <div className="flex items-center gap-2">
                    <span className="text-sm text-gray-500">Risk Level:</span>
                    <Badge className={getRiskColor(template.riskLevel)}>
                      {template.riskLevel}
                    </Badge>
                  </div>
                </div>
              </div>

              <div>
                <h4 className="text-sm font-semibold mb-2">Expected Performance</h4>
                <div className="grid grid-cols-2 gap-4 text-sm">
                  <div>
                    <span className="text-gray-500">Expected Return:</span>
                    <div className="font-medium text-green-600">{template.expectedReturn}</div>
                  </div>
                  <div>
                    <span className="text-gray-500">Volatility:</span>
                    <div className="font-medium">{template.volatility}</div>
                  </div>
                </div>
              </div>
            </div>

            <div>
              <h3 className="text-lg font-semibold mb-2">Allocation Breakdown</h3>
              <div className="space-y-1">
                {formatAllocation(template.allocation)}
              </div>
              <div className="mt-4 p-3 bg-blue-50 rounded-lg">
                <div className="flex items-center gap-2 text-sm text-blue-700">
                  <PieChart className="h-4 w-4" />
                  <span>Total Allocation: {Object.values(template.allocation).reduce((sum, weight) => sum + weight, 0)}%</span>
                </div>
              </div>
            </div>
          </div>

          {/* Portfolio Customization */}
          <div className="border-t pt-6">
            <h3 className="text-lg font-semibold mb-4">Customize Your Portfolio</h3>
            <div className="space-y-4">
              <div>
                <Label htmlFor="portfolio-name" className="text-sm font-medium">
                  Portfolio Name <span className="text-red-500">*</span>
                </Label>
                <Input
                  id="portfolio-name"
                  value={portfolioName}
                  onChange={(e) => setPortfolioName(e.target.value)}
                  placeholder="Enter a unique name for your portfolio"
                  className="mt-1"
                />
              </div>
              <div>
                <Label htmlFor="portfolio-description" className="text-sm font-medium">
                  Description
                </Label>
                <Textarea
                  id="portfolio-description"
                  value={portfolioDescription}
                  onChange={(e) => setPortfolioDescription(e.target.value)}
                  placeholder="Describe your investment strategy or goals"
                  className="mt-1"
                  rows={3}
                />
              </div>
            </div>
          </div>

          {/* Action Buttons */}
          <div className="flex gap-3 pt-4 border-t">
            <Button
              variant="outline"
              onClick={handleDrop}
              className="flex-1"
            >
              Drop Draft
            </Button>
            <Button
              onClick={handleSave}
              disabled={!portfolioName.trim() || isSaving}
              className="flex-1"
            >
              {isSaving ? (
                <>
                  <div className="animate-spin rounded-full h-4 w-4 border-b-2 border-white mr-2" />
                  Saving...
                </>
              ) : (
                <>
                  <Check className="h-4 w-4 mr-2" />
                  Save Portfolio
                </>
              )}
            </Button>
          </div>
        </CardContent>
      </Card>
    </div>
  );
}
