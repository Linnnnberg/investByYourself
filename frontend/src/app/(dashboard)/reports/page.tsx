"use client";

import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { Badge } from "@/components/ui/badge";
import { Download, FileText, Calendar, TrendingUp } from "lucide-react";

export default function ReportsPage() {
  // Mock reports data
  const reports = [
    {
      id: 1,
      title: "Monthly Portfolio Performance",
      type: "Performance Report",
      date: "2025-09-01",
      status: "Generated",
      size: "2.3 MB"
    },
    {
      id: 2,
      title: "Q3 2025 Investment Analysis",
      type: "Analysis Report",
      date: "2025-08-15",
      status: "Generated",
      size: "1.8 MB"
    },
    {
      id: 3,
      title: "Risk Assessment Summary",
      type: "Risk Report",
      date: "2025-08-01",
      status: "Generated",
      size: "1.2 MB"
    },
    {
      id: 4,
      title: "Tax Loss Harvesting Report",
      type: "Tax Report",
      date: "2025-07-20",
      status: "Generated",
      size: "0.9 MB"
    }
  ];

  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-3xl font-bold tracking-tight">Reports</h1>
          <p className="text-muted-foreground">
            Generate and download investment reports and analysis
          </p>
        </div>
        <Button>
          <FileText className="mr-2 h-4 w-4" />
          Generate Report
        </Button>
      </div>

      <div className="grid gap-4">
        {reports.map((report) => (
          <Card key={report.id} className="hover:shadow-md transition-shadow">
            <CardHeader className="pb-3">
              <div className="flex items-center justify-between">
                <div>
                  <CardTitle className="text-lg">{report.title}</CardTitle>
                  <CardDescription className="text-sm">{report.type}</CardDescription>
                </div>
                <div className="flex items-center gap-2">
                  <Badge variant="secondary">{report.status}</Badge>
                  <Button variant="outline" size="sm">
                    <Download className="mr-2 h-4 w-4" />
                    Download
                  </Button>
                </div>
              </div>
            </CardHeader>
            <CardContent className="pt-0">
              <div className="grid grid-cols-2 gap-4 text-sm">
                <div className="flex items-center">
                  <Calendar className="mr-2 h-4 w-4 text-muted-foreground" />
                  <span className="text-muted-foreground">Generated:</span>
                  <span className="ml-2 font-medium">{report.date}</span>
                </div>
                <div>
                  <span className="text-muted-foreground">Size:</span>
                  <span className="ml-2 font-medium">{report.size}</span>
                </div>
              </div>
            </CardContent>
          </Card>
        ))}
      </div>

      <Card>
        <CardHeader>
          <CardTitle className="flex items-center">
            <TrendingUp className="mr-2 h-5 w-5" />
            Quick Stats
          </CardTitle>
        </CardHeader>
        <CardContent>
          <div className="grid grid-cols-3 gap-4 text-center">
            <div>
              <div className="text-2xl font-bold">4</div>
              <div className="text-sm text-muted-foreground">Total Reports</div>
            </div>
            <div>
              <div className="text-2xl font-bold">6.2 MB</div>
              <div className="text-sm text-muted-foreground">Total Size</div>
            </div>
            <div>
              <div className="text-2xl font-bold">30</div>
              <div className="text-sm text-muted-foreground">Days Retention</div>
            </div>
          </div>
        </CardContent>
      </Card>
    </div>
  );
}
