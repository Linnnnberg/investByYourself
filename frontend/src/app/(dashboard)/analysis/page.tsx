"use client";

import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { Badge } from "@/components/ui/badge";
import { BarChart3, TrendingUp, TrendingDown, Calculator, PieChart } from "lucide-react";

export default function AnalysisPage() {
  const handleRunAnalysis = () => {
    console.log('Run analysis clicked');
  };

  return (
    <div className="container mx-auto px-4 py-8">
      <div className="mb-8">
        <h1 className="text-3xl font-bold text-gray-900 mb-2">Analysis</h1>
        <p className="text-gray-600">Comprehensive portfolio analysis and insights</p>
        <div className="mt-4">
          <Button onClick={handleRunAnalysis}>
            <BarChart3 className="h-4 w-4 mr-2" />
            Run Analysis
          </Button>
        </div>
      </div>

      <div className="grid gap-4 md:grid-cols-2 lg:grid-cols-4">
        <Card>
          <CardHeader className="pb-2">
            <CardTitle className="text-sm font-medium">Portfolio Performance</CardTitle>
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold">+12.5%</div>
            <p className="text-xs text-muted-foreground">+2.3% from last month</p>
          </CardContent>
        </Card>

        <Card>
          <CardHeader className="pb-2">
            <CardTitle className="text-sm font-medium">Risk Score</CardTitle>
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold">7.2/10</div>
            <p className="text-xs text-muted-foreground">-0.5 from last month</p>
          </CardContent>
        </Card>

        <Card>
          <CardHeader className="pb-2">
            <CardTitle className="text-sm font-medium">Diversification</CardTitle>
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold">85%</div>
            <p className="text-xs text-muted-foreground">+5% from last month</p>
          </CardContent>
        </Card>

        <Card>
          <CardHeader className="pb-2">
            <CardTitle className="text-sm font-medium">Sharpe Ratio</CardTitle>
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold">1.42</div>
            <p className="text-xs text-muted-foreground">+0.15 from last month</p>
          </CardContent>
        </Card>
      </div>

      <div className="grid gap-6 md:grid-cols-2 mt-8">
        <Card>
          <CardHeader>
            <CardTitle>Sector Allocation</CardTitle>
            <CardDescription>Current portfolio distribution by sector</CardDescription>
          </CardHeader>
          <CardContent>
            <div className="space-y-4">
              <div className="flex items-center justify-between">
                <span className="text-sm font-medium">Technology</span>
                <span className="text-sm text-muted-foreground">35%</span>
              </div>
              <div className="flex items-center justify-between">
                <span className="text-sm font-medium">Healthcare</span>
                <span className="text-sm text-muted-foreground">20%</span>
              </div>
              <div className="flex items-center justify-between">
                <span className="text-sm font-medium">Financials</span>
                <span className="text-sm text-muted-foreground">15%</span>
              </div>
            </div>
          </CardContent>
        </Card>

        <Card>
          <CardHeader>
            <CardTitle>Quick Actions</CardTitle>
            <CardDescription>Common analysis tasks</CardDescription>
          </CardHeader>
          <CardContent>
            <div className="grid grid-cols-2 gap-4">
              <Button variant="outline" className="h-12 flex items-center justify-center gap-2">
                <TrendingUp className="h-4 w-4" />
                Performance
              </Button>
              <Button variant="outline" className="h-12 flex items-center justify-center gap-2">
                <Calculator className="h-4 w-4" />
                Risk Analysis
              </Button>
              <Button variant="outline" className="h-12 flex items-center justify-center gap-2">
                <TrendingDown className="h-4 w-4" />
                Volatility
              </Button>
              <Button variant="outline" className="h-12 flex items-center justify-center gap-2">
                <PieChart className="h-4 w-4" />
                Diversification
              </Button>
            </div>
          </CardContent>
        </Card>
      </div>
    </div>
  );
}
