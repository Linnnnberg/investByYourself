"use client";

import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { Badge } from "@/components/ui/badge";
import { FileText, Download, Calendar, BarChart3 } from "lucide-react";

export default function ReportsPage() {
  const handleGenerateReport = () => {
    console.log('Generate report clicked');
  };

  const reports = [
    {
      id: 1,
      title: "Monthly Portfolio Report",
      description: "Comprehensive analysis of your portfolio performance",
      date: "2024-01-15",
      status: "completed",
      type: "monthly"
    },
    {
      id: 2,
      title: "Risk Assessment Report",
      description: "Detailed risk analysis and recommendations",
      date: "2024-01-10",
      status: "completed",
      type: "risk"
    },
    {
      id: 3,
      title: "Sector Analysis Report",
      description: "Industry and sector performance analysis",
      date: "2024-01-05",
      status: "completed",
      type: "sector"
    }
  ];

  return (
    <div className="container mx-auto px-4 py-8">
      <div className="mb-8">
        <h1 className="text-3xl font-bold text-gray-900 mb-2">Reports</h1>
        <p className="text-gray-600">Generate and download investment reports and analysis</p>
        <div className="mt-4">
          <Button onClick={handleGenerateReport}>
            <FileText className="h-4 w-4 mr-2" />
            Generate Report
          </Button>
        </div>
      </div>

      <div className="grid gap-4">
        {reports.map((report) => (
          <Card key={report.id} className="hover:shadow-md transition-shadow">
            <CardHeader className="pb-3">
              <div className="flex items-center justify-between">
                <div>
                  <CardTitle className="text-lg">{report.title}</CardTitle>
                  <CardDescription className="mt-1">{report.description}</CardDescription>
                </div>
                <Badge variant={report.status === 'completed' ? 'success' : 'secondary'}>
                  {report.status}
                </Badge>
              </div>
            </CardHeader>
            <CardContent>
              <div className="flex items-center justify-between">
                <div className="flex items-center space-x-4 text-sm text-muted-foreground">
                  <div className="flex items-center">
                    <Calendar className="h-4 w-4 mr-1" />
                    {report.date}
                  </div>
                  <div className="flex items-center">
                    <BarChart3 className="h-4 w-4 mr-1" />
                    {report.type}
                  </div>
                </div>
                <Button variant="outline" size="sm">
                  <Download className="h-4 w-4 mr-1" />
                  Download
                </Button>
              </div>
            </CardContent>
          </Card>
        ))}
      </div>

      <div className="mt-8">
        <Card>
          <CardHeader>
            <CardTitle>Report Statistics</CardTitle>
            <CardDescription>Overview of your report generation activity</CardDescription>
          </CardHeader>
          <CardContent>
            <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
              <div className="text-center">
                <div className="text-2xl font-bold">12</div>
                <div className="text-sm text-muted-foreground">Total Reports</div>
              </div>
              <div className="text-center">
                <div className="text-2xl font-bold">8</div>
                <div className="text-sm text-muted-foreground">This Month</div>
              </div>
              <div className="text-center">
                <div className="text-2xl font-bold">30</div>
                <div className="text-sm text-muted-foreground">Days Retention</div>
              </div>
            </div>
          </CardContent>
        </Card>
      </div>
    </div>
  );
}
