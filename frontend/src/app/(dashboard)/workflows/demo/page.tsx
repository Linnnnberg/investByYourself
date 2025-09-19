"use client";

import React, { useState } from "react";
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { Badge } from "@/components/ui/badge";
import {
  DecisionStepComponent,
  DataCollectionStepComponent,
  ValidationStepComponent,
  UserInteractionStepComponent
} from "@/components/workflows/steps";

export default function WorkflowDemoPage() {
  const [currentDemo, setCurrentDemo] = useState<string | null>(null);

  const demos = [
    {
      id: "decision",
      name: "Decision Step",
      description: "Interactive decision making with radio buttons, checkboxes, and dropdowns",
      component: "DecisionStepComponent"
    },
    {
      id: "data-collection",
      name: "Data Collection Step",
      description: "Form-based data collection with validation and progress tracking",
      component: "DataCollectionStepComponent"
    },
    {
      id: "validation",
      name: "Validation Step",
      description: "Results display with success, warning, and error states",
      component: "ValidationStepComponent"
    },
    {
      id: "user-interaction",
      name: "User Interaction Step",
      description: "Product selection with search, filters, and multi-selection",
      component: "UserInteractionStepComponent"
    }
  ];

  const renderDemo = () => {
    switch (currentDemo) {
      case "decision":
        return (
          <DecisionStepComponent
            stepId="risk_tolerance"
            title="Select Your Risk Tolerance"
            description="Choose the risk level that best matches your investment preferences and financial goals."
            options={[
              {
                id: "conservative",
                label: "Conservative",
                description: "Low risk, stable returns, capital preservation focus",
                value: "conservative"
              },
              {
                id: "moderate",
                label: "Moderate",
                description: "Balanced risk and return, steady growth approach",
                value: "moderate"
              },
              {
                id: "aggressive",
                label: "Aggressive",
                description: "Higher risk for potentially higher returns, growth focus",
                value: "aggressive"
              }
            ]}
            inputType="radio"
            required={true}
            helpText="Your risk tolerance will determine the asset allocation in your portfolio."
            onSelectionChange={(value) => console.log("Risk tolerance selected:", value)}
            onContinue={() => setCurrentDemo(null)}
            isLoading={false}
          />
        );

      case "data-collection":
        return (
          <DataCollectionStepComponent
            stepId="investment_profile"
            title="Investment Profile"
            description="Tell us about your investment goals and preferences to create a personalized portfolio."
            fields={[
              {
                id: "age",
                label: "Age",
                type: "number",
                placeholder: "Enter your age",
                required: true,
                validation: { min: 18, max: 100, message: "Age must be between 18 and 100" },
                icon: "👤"
              },
              {
                id: "annual_income",
                label: "Annual Income",
                type: "currency",
                placeholder: "Enter your annual income",
                required: true,
                validation: { min: 0, message: "Income must be positive" },
                icon: "💰"
              },
              {
                id: "investment_goals",
                label: "Investment Goals",
                type: "textarea",
                placeholder: "Describe your investment goals (e.g., retirement, house purchase, education)",
                required: true,
                description: "Be specific about your financial objectives"
              },
              {
                id: "time_horizon",
                label: "Investment Time Horizon",
                type: "number",
                placeholder: "Years until you need the money",
                required: true,
                validation: { min: 1, max: 50, message: "Time horizon must be between 1 and 50 years" },
                icon: "📅"
              }
            ]}
            progress={75}
            helpText="This information helps us recommend the most suitable investment strategy for you."
            onDataChange={(data) => console.log("Profile data updated:", data)}
            onContinue={() => setCurrentDemo(null)}
            isLoading={false}
          />
        );

      case "validation":
        return (
          <ValidationStepComponent
            stepId="portfolio_validation"
            title="Portfolio Validation"
            description="We've analyzed your portfolio configuration and found the following results."
            results={[
              {
                id: "diversification",
                label: "Diversification Check",
                status: "success",
                message: "Portfolio is well diversified across asset classes",
                details: "60% stocks, 30% bonds, 10% alternatives"
              },
              {
                id: "risk_alignment",
                label: "Risk Alignment",
                status: "success",
                message: "Risk level matches your tolerance",
                details: "Moderate risk portfolio aligns with your moderate risk tolerance"
              },
              {
                id: "rebalancing",
                label: "Rebalancing Schedule",
                status: "warning",
                message: "Consider quarterly rebalancing",
                details: "Current allocation may drift over time without rebalancing"
              }
            ]}
            overallStatus="success"
            summary="Your portfolio configuration looks good! Minor adjustments recommended for optimal performance."
            onRetry={() => console.log("Retry validation")}
            onContinue={() => setCurrentDemo(null)}
            isLoading={false}
            showDetails={true}
          />
        );

      case "user-interaction":
        return (
          <UserInteractionStepComponent
            stepId="product_selection"
            title="Select Investment Products"
            description="Choose from our curated selection of investment products that match your profile."
            items={[
              {
                id: "spy",
                name: "SPDR S&P 500 ETF Trust (SPY)",
                description: "Low-cost ETF tracking the S&P 500 index",
                category: "US Large Cap",
                tags: ["ETF", "S&P 500", "Low Cost"],
                metadata: { expense_ratio: 0.09, risk_level: "moderate" }
              },
              {
                id: "vti",
                name: "Vanguard Total Stock Market ETF (VTI)",
                description: "Broad market exposure to US stocks",
                category: "US Total Market",
                tags: ["ETF", "Total Market", "Vanguard"],
                metadata: { expense_ratio: 0.03, risk_level: "moderate" }
              },
              {
                id: "bnd",
                name: "Vanguard Total Bond Market ETF (BND)",
                description: "Diversified exposure to US investment-grade bonds",
                category: "US Bonds",
                tags: ["ETF", "Bonds", "Vanguard"],
                metadata: { expense_ratio: 0.03, risk_level: "conservative" }
              },
              {
                id: "vxus",
                name: "Vanguard Total International Stock ETF (VXUS)",
                description: "International stock market exposure",
                category: "International",
                tags: ["ETF", "International", "Vanguard"],
                metadata: { expense_ratio: 0.08, risk_level: "moderate" }
              }
            ]}
            selectionType="multiple"
            searchEnabled={true}
            filters={[
              {
                id: "category",
                label: "Category",
                type: "checkbox",
                options: [
                  { value: "US Large Cap", label: "US Large Cap" },
                  { value: "US Total Market", label: "US Total Market" },
                  { value: "US Bonds", label: "US Bonds" },
                  { value: "International", label: "International" }
                ]
              },
              {
                id: "risk_level",
                label: "Risk Level",
                type: "select",
                options: [
                  { value: "conservative", label: "Conservative" },
                  { value: "moderate", label: "Moderate" },
                  { value: "aggressive", label: "Aggressive" }
                ]
              }
            ]}
            maxSelections={3}
            minSelections={1}
            helpText="Select 1-3 products that align with your investment goals and risk tolerance."
            onSelectionChange={(items) => console.log("Selected products:", items)}
            onContinue={() => setCurrentDemo(null)}
            isLoading={false}
          />
        );

      default:
        return null;
    }
  };

  return (
    <div className="container mx-auto py-8 space-y-8">
      <div className="text-center space-y-4">
        <h1 className="text-3xl font-bold">Enhanced Workflow Step Components</h1>
        <p className="text-muted-foreground max-w-2xl mx-auto">
          Interactive demonstration of the enhanced workflow step components built for the allocation framework.
          Each component provides rich user interactions and validation.
        </p>
      </div>

      {!currentDemo ? (
        <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
          {demos.map((demo) => (
            <Card key={demo.id} className="cursor-pointer hover:shadow-lg transition-shadow">
              <CardHeader>
                <CardTitle className="flex items-center justify-between">
                  {demo.name}
                  <Badge variant="outline">{demo.component}</Badge>
                </CardTitle>
                <CardDescription>{demo.description}</CardDescription>
              </CardHeader>
              <CardContent>
                <Button
                  onClick={() => setCurrentDemo(demo.id)}
                  className="w-full"
                >
                  Try Demo
                </Button>
              </CardContent>
            </Card>
          ))}
        </div>
      ) : (
        <div className="space-y-4">
          <div className="flex items-center justify-between">
            <Button
              variant="outline"
              onClick={() => setCurrentDemo(null)}
            >
              ← Back to Demos
            </Button>
            <Badge variant="secondary">
              {demos.find(d => d.id === currentDemo)?.component}
            </Badge>
          </div>
          {renderDemo()}
        </div>
      )}

      <Card className="mt-8">
        <CardHeader>
          <CardTitle>Component Features</CardTitle>
          <CardDescription>Key features of the enhanced workflow step components</CardDescription>
        </CardHeader>
        <CardContent>
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
            <div className="space-y-2">
              <h4 className="font-semibold">DecisionStepComponent</h4>
              <ul className="text-sm text-muted-foreground space-y-1">
                <li>• Radio buttons, checkboxes, dropdowns</li>
                <li>• Real-time validation</li>
                <li>• Help text and descriptions</li>
                <li>• Required field handling</li>
              </ul>
            </div>
            <div className="space-y-2">
              <h4 className="font-semibold">DataCollectionStepComponent</h4>
              <ul className="text-sm text-muted-foreground space-y-1">
                <li>• Multiple input types</li>
                <li>• Form validation</li>
                <li>• Progress tracking</li>
                <li>• Field descriptions</li>
              </ul>
            </div>
            <div className="space-y-2">
              <h4 className="font-semibold">ValidationStepComponent</h4>
              <ul className="text-sm text-muted-foreground space-y-1">
                <li>• Success/warning/error states</li>
                <li>• Detailed result display</li>
                <li>• Retry functionality</li>
                <li>• Summary information</li>
              </ul>
            </div>
            <div className="space-y-2">
              <h4 className="font-semibold">UserInteractionStepComponent</h4>
              <ul className="text-sm text-muted-foreground space-y-1">
                <li>• Search and filtering</li>
                <li>• Multi-selection support</li>
                <li>• Item metadata display</li>
                <li>• Selection validation</li>
              </ul>
            </div>
          </div>
        </CardContent>
      </Card>
    </div>
  );
}
