"use client";

import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { Badge } from "@/components/ui/badge";
import { BarChart3, TrendingUp, TrendingDown, Calculator, PieChart } from "lucide-react";

export default function AnalysisPage() {
  // Mock analysis data
  const analysisMetrics = [
    {
      title: "Portfolio Performance",
      value: "+12.5%",
      change: "+2.3%",
      trend: "up",
      description: "Year-to-date return"
    },
    {
      title: "Risk Score",
      value: "7.2/10",
      change: "-0.5",
      trend: "down",
      description: "Moderate risk level"
    },
    {
      title: "Diversification",
      value: "85%",
      change: "+5%",
      trend: "up",
      description: "Well diversified"
    },
    {
      title: "Sharpe Ratio",
      value: "1.42",
      change: "+0.15",
      trend: "up",
      description: "Risk-adjusted return"
    }
  ];

  const sectorAllocation = [
    { sector: "Technology", percentage: 35, color: "bg-blue-500" },
    { sector: "Healthcare", percentage: 20, color: "bg-green-500" },
    { sector: "Financials", percentage: 15, color: "bg-yellow-500" },
    { sector: "Consumer", percentage: 12, color: "bg-purple-500" },
    { sector: "Industrial", percentage: 10, color: "bg-red-500" },
    { sector: "Other", percentage: 8, color: "bg-gray-500" }
  ];

  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-3xl font-bold tracking-tight">Analysis</h1>
          <p className="text-muted-foreground">
            Comprehensive portfolio analysis and insights
          </p>
        </div>
        <Button>
          <BarChart3 className="mr-2 h-4 w-4" />
          Run Analysis
        </Button>
      </div>

      {/* Key Metrics */}
      <div className="grid gap-4 md:grid-cols-2 lg:grid-cols-4">
        {analysisMetrics.map((metric, index) => (
          <Card key={index}>
            <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
              <CardTitle className="text-sm font-medium">{metric.title}</CardTitle>
              {metric.trend === "up" ? (
                <TrendingUp className="h-4 w-4 text-green-600" />
              ) : (
                <TrendingDown className="h-4 w-4 text-red-600" />
              )}
            </CardHeader>
            <CardContent>
              <div className="text-2xl font-bold">{metric.value}</div>
              <p className={`text-xs ${
                metric.trend === "up" ? "text-green-600" : "text-red-600"
              }`}>
                {metric.change} from last month
              </p>
              <p className="text-xs text-muted-foreground mt-1">{metric.description}</p>
            </CardContent>
          </Card>
        ))}
      </div>

      <div className="grid gap-6 md:grid-cols-2">
        {/* Sector Allocation */}
        <Card>
          <CardHeader>
            <CardTitle className="flex items-center">
              <PieChart className="mr-2 h-5 w-5" />
              Sector Allocation
            </CardTitle>
            <CardDescription>
              Portfolio distribution across sectors
            </CardDescription>
          </CardHeader>
          <CardContent>
            <div className="space-y-3">
              {sectorAllocation.map((item, index) => (
                <div key={index} className="flex items-center justify-between">
                  <div className="flex items-center space-x-2">
                    <div className={`w-3 h-3 rounded-full ${item.color}`}></div>
                    <span className="text-sm font-medium">{item.sector}</span>
                  </div>
                  <span className="text-sm text-muted-foreground">{item.percentage}%</span>
                </div>
              ))}
            </div>
          </CardContent>
        </Card>

        {/* Performance Comparison */}
        <Card>
          <CardHeader>
            <CardTitle className="flex items-center">
              <Calculator className="mr-2 h-5 w-5" />
              Performance vs Benchmarks
            </CardTitle>
            <CardDescription>
              How your portfolio compares to market indices
            </CardDescription>
          </CardHeader>
          <CardContent>
            <div className="space-y-4">
              <div className="flex items-center justify-between">
                <span className="text-sm font-medium">Your Portfolio</span>
                <Badge variant="default">+12.5%</Badge>
              </div>
              <div className="flex items-center justify-between">
                <span className="text-sm font-medium">S&P 500</span>
                <Badge variant="secondary">+8.2%</Badge>
              </div>
              <div className="flex items-center justify-between">
                <span className="text-sm font-medium">NASDAQ</span>
                <Badge variant="secondary">+10.1%</Badge>
              </div>
              <div className="flex items-center justify-between">
                <span className="text-sm font-medium">Russell 2000</span>
                <Badge variant="secondary">+5.8%</Badge>
              </div>
            </div>
          </CardContent>
        </Card>
      </div>

      {/* Analysis Actions */}
      <Card>
        <CardHeader>
          <CardTitle>Analysis Tools</CardTitle>
          <CardDescription>
            Run detailed analysis on your portfolio
          </CardDescription>
        </CardHeader>
        <CardContent>
          <div className="grid gap-4 md:grid-cols-3">
            <Button variant="outline" className="h-20 flex-col">
              <BarChart3 className="mb-2 h-6 w-6" />
              Performance Analysis
            </Button>
            <Button variant="outline" className="h-20 flex-col">
              <Calculator className="mb-2 h-6 w-6" />
              Risk Assessment
            </Button>
            <Button variant="outline" className="h-20 flex-col">
              <PieChart className="mb-2 h-6 w-6" />
              Diversification Check
            </Button>
          </div>
        </CardContent>
      </Card>
    </div>
  );
}
