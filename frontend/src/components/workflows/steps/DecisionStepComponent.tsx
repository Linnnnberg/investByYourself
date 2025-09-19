"use client";

import React, { useState, useEffect } from "react";
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { RadioGroup, RadioGroupItem } from "@/components/ui/radio-group";
import { Checkbox } from "@/components/ui/checkbox";
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from "@/components/ui/select";
import { Label } from "@/components/ui/label";
import { Alert, AlertDescription } from "@/components/ui/alert";
import { CheckCircle, AlertCircle, HelpCircle } from "lucide-react";

interface DecisionOption {
  id: string;
  label: string;
  description?: string;
  value: string;
  disabled?: boolean;
}

interface DecisionStepComponentProps {
  stepId: string;
  title: string;
  description: string;
  options: DecisionOption[];
  inputType: "radio" | "checkbox" | "select";
  required?: boolean;
  helpText?: string;
  validation?: {
    isValid: boolean;
    message?: string;
  };
  onSelectionChange: (value: string | string[]) => void;
  onContinue: () => void;
  onBack?: () => void;
  isLoading?: boolean;
  selectedValue?: string | string[];
}

export function DecisionStepComponent({
  stepId,
  title,
  description,
  options,
  inputType,
  required = true,
  helpText,
  validation,
  onSelectionChange,
  onContinue,
  onBack,
  isLoading = false,
  selectedValue,
}: DecisionStepComponentProps) {
  const [localValue, setLocalValue] = useState<string | string[]>(
    selectedValue || (inputType === "checkbox" ? [] : "")
  );
  const [hasInteracted, setHasInteracted] = useState(false);

  useEffect(() => {
    if (selectedValue !== undefined) {
      setLocalValue(selectedValue);
    }
  }, [selectedValue]);

  const handleValueChange = (value: string | string[]) => {
    setLocalValue(value);
    setHasInteracted(true);
    onSelectionChange(value);
  };

  const handleRadioChange = (value: string) => {
    handleValueChange(value);
  };

  const handleCheckboxChange = (optionId: string, checked: boolean) => {
    const currentValues = Array.isArray(localValue) ? localValue : [];
    const newValues = checked
      ? [...currentValues, optionId]
      : currentValues.filter((id) => id !== optionId);
    handleValueChange(newValues);
  };

  const handleSelectChange = (value: string) => {
    handleValueChange(value);
  };

  const canContinue = () => {
    if (!required) return true;
    if (inputType === "checkbox") {
      return Array.isArray(localValue) && localValue.length > 0;
    }
    return localValue !== "" && localValue !== undefined;
  };

  const renderInput = () => {
    switch (inputType) {
      case "radio":
        return (
          <RadioGroup
            value={localValue as string}
            onValueChange={handleRadioChange}
            className="space-y-3"
          >
            {options.map((option) => (
              <div key={option.id} className="flex items-start space-x-3">
                <RadioGroupItem
                  value={option.value}
                  id={option.id}
                  disabled={option.disabled || isLoading}
                  className="mt-1"
                />
                <div className="flex-1">
                  <Label
                    htmlFor={option.id}
                    className={`text-sm font-medium cursor-pointer ${
                      option.disabled ? "text-muted-foreground" : ""
                    }`}
                  >
                    {option.label}
                  </Label>
                  {option.description && (
                    <p className="text-xs text-muted-foreground mt-1">
                      {option.description}
                    </p>
                  )}
                </div>
              </div>
            ))}
          </RadioGroup>
        );

      case "checkbox":
        return (
          <div className="space-y-3">
            {options.map((option) => (
              <div key={option.id} className="flex items-start space-x-3">
                <Checkbox
                  id={option.id}
                  checked={Array.isArray(localValue) && localValue.includes(option.id)}
                  onCheckedChange={(checked) =>
                    handleCheckboxChange(option.id, checked as boolean)
                  }
                  disabled={option.disabled || isLoading}
                  className="mt-1"
                />
                <div className="flex-1">
                  <Label
                    htmlFor={option.id}
                    className={`text-sm font-medium cursor-pointer ${
                      option.disabled ? "text-muted-foreground" : ""
                    }`}
                  >
                    {option.label}
                  </Label>
                  {option.description && (
                    <p className="text-xs text-muted-foreground mt-1">
                      {option.description}
                    </p>
                  )}
                </div>
              </div>
            ))}
          </div>
        );

      case "select":
        return (
          <Select
            value={localValue as string}
            onValueChange={handleSelectChange}
            disabled={isLoading}
          >
            <SelectTrigger className="w-full">
              <SelectValue placeholder="Select an option..." />
            </SelectTrigger>
            <SelectContent>
              {options.map((option) => (
                <SelectItem
                  key={option.id}
                  value={option.value}
                  disabled={option.disabled}
                >
                  <div>
                    <div className="font-medium">{option.label}</div>
                    {option.description && (
                      <div className="text-xs text-muted-foreground">
                        {option.description}
                      </div>
                    )}
                  </div>
                </SelectItem>
              ))}
            </SelectContent>
          </Select>
        );

      default:
        return null;
    }
  };

  const showValidationError = validation && !validation.isValid && hasInteracted;

  return (
    <Card className="w-full max-w-2xl mx-auto">
      <CardHeader>
        <CardTitle className="flex items-center gap-2">
          {title}
          {required && <span className="text-red-500">*</span>}
        </CardTitle>
        <CardDescription>{description}</CardDescription>
        {helpText && (
          <Alert className="mt-4">
            <HelpCircle className="h-4 w-4" />
            <AlertDescription>{helpText}</AlertDescription>
          </Alert>
        )}
      </CardHeader>
      <CardContent className="space-y-6">
        {renderInput()}

        {showValidationError && (
          <Alert variant="destructive">
            <AlertCircle className="h-4 w-4" />
            <AlertDescription>{validation.message}</AlertDescription>
          </Alert>
        )}

        <div className="flex justify-between items-center pt-4">
          <div className="flex gap-2">
            {onBack && (
              <Button
                variant="outline"
                onClick={onBack}
                disabled={isLoading}
              >
                Back
              </Button>
            )}
          </div>
          <div className="flex gap-2">
            <Button
              onClick={onContinue}
              disabled={!canContinue() || isLoading}
              className="min-w-[100px]"
            >
              {isLoading ? (
                <div className="flex items-center gap-2">
                  <div className="w-4 h-4 border-2 border-white border-t-transparent rounded-full animate-spin" />
                  Processing...
                </div>
              ) : (
                <>
                  <CheckCircle className="w-4 h-4 mr-2" />
                  Continue
                </>
              )}
            </Button>
          </div>
        </div>
      </CardContent>
    </Card>
  );
}
