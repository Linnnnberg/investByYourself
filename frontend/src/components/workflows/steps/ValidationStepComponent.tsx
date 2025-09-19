"use client";

import React from "react";
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { Alert, AlertDescription } from "@/components/ui/alert";
import { Badge } from "@/components/ui/badge";
import { CheckCircle, AlertCircle, XCircle, RefreshCw, ArrowRight, ArrowLeft } from "lucide-react";

interface ValidationResult {
  id: string;
  label: string;
  status: "success" | "warning" | "error";
  message: string;
  details?: string;
}

interface ValidationStepComponentProps {
  stepId: string;
  title: string;
  description: string;
  results: ValidationResult[];
  overallStatus: "success" | "warning" | "error" | "pending";
  summary?: string;
  onRetry?: () => void;
  onContinue: () => void;
  onBack?: () => void;
  isLoading?: boolean;
  showDetails?: boolean;
}

export function ValidationStepComponent({
  stepId,
  title,
  description,
  results,
  overallStatus,
  summary,
  onRetry,
  onContinue,
  onBack,
  isLoading = false,
  showDetails = true,
}: ValidationStepComponentProps) {
  const getStatusIcon = (status: string) => {
    switch (status) {
      case "success":
        return <CheckCircle className="h-5 w-5 text-green-500" />;
      case "warning":
        return <AlertCircle className="h-5 w-5 text-yellow-500" />;
      case "error":
        return <XCircle className="h-5 w-5 text-red-500" />;
      default:
        return <RefreshCw className="h-5 w-5 text-gray-500 animate-spin" />;
    }
  };

  const getStatusColor = (status: string) => {
    switch (status) {
      case "success":
        return "bg-green-100 text-green-800 border-green-200";
      case "warning":
        return "bg-yellow-100 text-yellow-800 border-yellow-200";
      case "error":
        return "bg-red-100 text-red-800 border-red-200";
      default:
        return "bg-gray-100 text-gray-800 border-gray-200";
    }
  };

  const getOverallStatusInfo = () => {
    switch (overallStatus) {
      case "success":
        return {
          icon: <CheckCircle className="h-6 w-6 text-green-500" />,
          title: "Validation Successful",
          description: "All checks passed successfully",
          color: "text-green-600",
        };
      case "warning":
        return {
          icon: <AlertCircle className="h-6 w-6 text-yellow-500" />,
          title: "Validation Warning",
          description: "Some issues were found but can be resolved",
          color: "text-yellow-600",
        };
      case "error":
        return {
          icon: <XCircle className="h-6 w-6 text-red-500" />,
          title: "Validation Failed",
          description: "Please fix the errors below",
          color: "text-red-600",
        };
      default:
        return {
          icon: <RefreshCw className="h-6 w-6 text-gray-500 animate-spin" />,
          title: "Validating...",
          description: "Please wait while we validate your input",
          color: "text-gray-600",
        };
    }
  };

  const canContinue = () => {
    return overallStatus === "success" || overallStatus === "warning";
  };

  const statusInfo = getOverallStatusInfo();

  return (
    <Card className="w-full max-w-2xl mx-auto">
      <CardHeader>
        <CardTitle className="flex items-center gap-2">
          {title}
        </CardTitle>
        <CardDescription>{description}</CardDescription>
      </CardHeader>
      <CardContent className="space-y-6">
        {/* Overall Status */}
        <div className={`p-4 rounded-lg border-2 ${getStatusColor(overallStatus)}`}>
          <div className="flex items-center gap-3">
            {statusInfo.icon}
            <div>
              <h3 className={`font-semibold ${statusInfo.color}`}>
                {statusInfo.title}
              </h3>
              <p className="text-sm opacity-90">
                {statusInfo.description}
              </p>
            </div>
          </div>
        </div>

        {/* Summary */}
        {summary && (
          <Alert>
            <AlertCircle className="h-4 w-4" />
            <AlertDescription>{summary}</AlertDescription>
          </Alert>
        )}

        {/* Results */}
        {showDetails && results.length > 0 && (
          <div className="space-y-3">
            <h4 className="font-medium text-sm text-muted-foreground">
              Validation Results
            </h4>
            <div className="space-y-2">
              {results.map((result) => (
                <div
                  key={result.id}
                  className="flex items-start gap-3 p-3 rounded-lg border"
                >
                  {getStatusIcon(result.status)}
                  <div className="flex-1 min-w-0">
                    <div className="flex items-center gap-2 mb-1">
                      <span className="font-medium text-sm">{result.label}</span>
                      <Badge
                        variant="outline"
                        className={`text-xs ${getStatusColor(result.status)}`}
                      >
                        {result.status}
                      </Badge>
                    </div>
                    <p className="text-sm text-muted-foreground">
                      {result.message}
                    </p>
                    {result.details && (
                      <p className="text-xs text-muted-foreground mt-1">
                        {result.details}
                      </p>
                    )}
                  </div>
                </div>
              ))}
            </div>
          </div>
        )}

        {/* Actions */}
        <div className="flex justify-between items-center pt-4">
          <div className="flex gap-2">
            {onBack && (
              <Button
                variant="outline"
                onClick={onBack}
                disabled={isLoading}
                className="flex items-center gap-2"
              >
                <ArrowLeft className="h-4 w-4" />
                Back
              </Button>
            )}
            {onRetry && overallStatus === "error" && (
              <Button
                variant="outline"
                onClick={onRetry}
                disabled={isLoading}
                className="flex items-center gap-2"
              >
                <RefreshCw className="h-4 w-4" />
                Retry
              </Button>
            )}
          </div>
          <div className="flex gap-2">
            <Button
              onClick={onContinue}
              disabled={!canContinue() || isLoading}
              className="min-w-[100px] flex items-center gap-2"
            >
              {isLoading ? (
                <>
                  <RefreshCw className="h-4 w-4 animate-spin" />
                  Processing...
                </>
              ) : (
                <>
                  {overallStatus === "success" ? (
                    <>
                      <CheckCircle className="h-4 w-4" />
                      Continue
                    </>
                  ) : overallStatus === "warning" ? (
                    <>
                      <AlertCircle className="h-4 w-4" />
                      Continue
                    </>
                  ) : (
                    <>
                      <ArrowRight className="h-4 w-4" />
                      Next
                    </>
                  )}
                </>
              )}
            </Button>
          </div>
        </div>
      </CardContent>
    </Card>
  );
}
