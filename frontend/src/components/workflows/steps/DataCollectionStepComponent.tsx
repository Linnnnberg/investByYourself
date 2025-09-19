"use client";

import React, { useState, useEffect } from "react";
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import { Textarea } from "@/components/ui/textarea";
import { Alert, AlertDescription } from "@/components/ui/alert";
import { Progress } from "@/components/ui/progress";
import { CheckCircle, AlertCircle, HelpCircle, User, DollarSign, Calendar } from "lucide-react";

interface FormField {
  id: string;
  label: string;
  type: "text" | "email" | "number" | "textarea" | "currency" | "percentage";
  placeholder?: string;
  required?: boolean;
  validation?: {
    min?: number;
    max?: number;
    pattern?: string;
    message?: string;
  };
  description?: string;
  icon?: React.ReactNode;
}

interface DataCollectionStepComponentProps {
  stepId: string;
  title: string;
  description: string;
  fields: FormField[];
  progress?: number;
  helpText?: string;
  onDataChange: (data: Record<string, any>) => void;
  onContinue: () => void;
  onBack?: () => void;
  isLoading?: boolean;
  initialData?: Record<string, any>;
}

export function DataCollectionStepComponent({
  stepId,
  title,
  description,
  fields,
  progress = 0,
  helpText,
  onDataChange,
  onContinue,
  onBack,
  isLoading = false,
  initialData = {},
}: DataCollectionStepComponentProps) {
  const [formData, setFormData] = useState<Record<string, any>>(initialData);
  const [errors, setErrors] = useState<Record<string, string>>({});
  const [touched, setTouched] = useState<Record<string, boolean>>({});

  useEffect(() => {
    onDataChange(formData);
  }, [formData, onDataChange]);

  const validateField = (field: FormField, value: any): string | null => {
    if (field.required && (!value || value.toString().trim() === "")) {
      return `${field.label} is required`;
    }

    if (!value || value.toString().trim() === "") {
      return null; // Optional field, no validation needed
    }

    if (field.validation) {
      const { min, max, pattern, message } = field.validation;

      if (field.type === "number" || field.type === "currency" || field.type === "percentage") {
        const numValue = parseFloat(value);
        if (isNaN(numValue)) {
          return message || `${field.label} must be a valid number`;
        }
        if (min !== undefined && numValue < min) {
          return message || `${field.label} must be at least ${min}`;
        }
        if (max !== undefined && numValue > max) {
          return message || `${field.label} must be at most ${max}`;
        }
      }

      if (pattern && !new RegExp(pattern).test(value)) {
        return message || `${field.label} format is invalid`;
      }
    }

    return null;
  };

  const handleFieldChange = (fieldId: string, value: any) => {
    setFormData((prev) => ({ ...prev, [fieldId]: value }));
    setTouched((prev) => ({ ...prev, [fieldId]: true }));

    const field = fields.find((f) => f.id === fieldId);
    if (field) {
      const error = validateField(field, value);
      setErrors((prev) => ({ ...prev, [fieldId]: error || "" }));
    }
  };

  const validateForm = (): boolean => {
    const newErrors: Record<string, string> = {};
    let isValid = true;

    fields.forEach((field) => {
      const error = validateField(field, formData[field.id]);
      if (error) {
        newErrors[field.id] = error;
        isValid = false;
      }
    });

    setErrors(newErrors);
    return isValid;
  };

  const handleContinue = () => {
    if (validateForm()) {
      onContinue();
    }
  };

  const getFieldIcon = (field: FormField) => {
    if (field.icon) return field.icon;

    switch (field.type) {
      case "email":
        return <User className="h-4 w-4" />;
      case "currency":
      case "percentage":
        return <DollarSign className="h-4 w-4" />;
      case "number":
        return <Calendar className="h-4 w-4" />;
      default:
        return null;
    }
  };

  const formatValue = (field: FormField, value: any) => {
    if (!value) return "";

    switch (field.type) {
      case "currency":
        return typeof value === "number" ? value.toFixed(2) : value;
      case "percentage":
        return typeof value === "number" ? value.toFixed(1) : value;
      default:
        return value;
    }
  };

  const getInputType = (field: FormField) => {
    switch (field.type) {
      case "email":
        return "email";
      case "number":
      case "currency":
      case "percentage":
        return "number";
      default:
        return "text";
    }
  };

  const getInputProps = (field: FormField) => {
    const props: any = {
      type: getInputType(field),
      placeholder: field.placeholder,
      value: formatValue(field, formData[field.id] || ""),
      onChange: (e: React.ChangeEvent<HTMLInputElement>) => {
        let value = e.target.value;
        if (field.type === "number" || field.type === "currency" || field.type === "percentage") {
          value = value === "" ? "" : parseFloat(value).toString();
        }
        handleFieldChange(field.id, value);
      },
      disabled: isLoading,
    };

    if (field.validation) {
      if (field.validation.min !== undefined) {
        props.min = field.validation.min;
      }
      if (field.validation.max !== undefined) {
        props.max = field.validation.max;
      }
    }

    return props;
  };

  const renderField = (field: FormField) => {
    const hasError = touched[field.id] && errors[field.id];
    const fieldIcon = getFieldIcon(field);

    return (
      <div key={field.id} className="space-y-2">
        <Label htmlFor={field.id} className="flex items-center gap-2">
          {fieldIcon}
          {field.label}
          {field.required && <span className="text-red-500">*</span>}
        </Label>

        {field.description && (
          <p className="text-xs text-muted-foreground">{field.description}</p>
        )}

        {field.type === "textarea" ? (
          <Textarea
            id={field.id}
            placeholder={field.placeholder}
            value={formData[field.id] || ""}
            onChange={(e) => handleFieldChange(field.id, e.target.value)}
            disabled={isLoading}
            className={hasError ? "border-red-500" : ""}
            rows={4}
          />
        ) : (
          <Input
            id={field.id}
            {...getInputProps(field)}
            className={hasError ? "border-red-500" : ""}
          />
        )}

        {hasError && (
          <p className="text-xs text-red-500 flex items-center gap-1">
            <AlertCircle className="h-3 w-3" />
            {errors[field.id]}
          </p>
        )}
      </div>
    );
  };

  const canContinue = () => {
    return fields.every((field) => {
      if (!field.required) return true;
      const value = formData[field.id];
      return value !== undefined && value !== "" && value.toString().trim() !== "";
    });
  };

  return (
    <Card className="w-full max-w-2xl mx-auto">
      <CardHeader>
        <CardTitle className="flex items-center gap-2">
          {title}
        </CardTitle>
        <CardDescription>{description}</CardDescription>

        {progress > 0 && (
          <div className="space-y-2">
            <div className="flex justify-between text-sm">
              <span>Progress</span>
              <span>{Math.round(progress)}%</span>
            </div>
            <Progress value={progress} className="h-2" />
          </div>
        )}

        {helpText && (
          <Alert className="mt-4">
            <HelpCircle className="h-4 w-4" />
            <AlertDescription>{helpText}</AlertDescription>
          </Alert>
        )}
      </CardHeader>
      <CardContent className="space-y-6">
        <div className="grid gap-4">
          {fields.map(renderField)}
        </div>

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
              onClick={handleContinue}
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
