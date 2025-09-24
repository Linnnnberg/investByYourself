'use client';

import React, { useState, useEffect } from 'react';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { Label } from '@/components/ui/label';
import { Textarea } from '@/components/ui/textarea';
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from '@/components/ui/select';
import { Progress } from '@/components/ui/progress';
import { WorkflowStep, WorkflowContext } from '@/types/workflow';

interface DataCollectionStepComponentProps {
  stepId: string;
  title: string;
  description: string;
  fields: Array<{
    id: string;
    label: string;
    type: 'text' | 'email' | 'number' | 'select' | 'textarea' | 'date';
    required?: boolean;
    options?: Array<{ value: string; label: string }>;
    placeholder?: string;
    validation?: {
      min?: number;
      max?: number;
      pattern?: string;
      message?: string;
    };
  }>;
  progress?: number;
  helpText?: string;
  onDataChange: (data: Record<string, any>) => void;
  onContinue: () => void;
  onBack: () => void;
  isLoading: boolean;
  initialData?: Record<string, any>;
}

const DataCollectionStepComponent: React.FC<DataCollectionStepComponentProps> = ({
  stepId,
  title,
  description,
  fields,
  progress = 0,
  helpText,
  onDataChange,
  onContinue,
  onBack,
  isLoading,
  initialData = {}
}) => {
  const [formData, setFormData] = useState<Record<string, any>>(initialData);
  const [errors, setErrors] = useState<Record<string, string>>({});
  const [isValid, setIsValid] = useState(false);

  useEffect(() => {
    // Validate form whenever formData changes
    const validationErrors: Record<string, string> = {};
    let valid = true;

    fields.forEach(field => {
      const value = formData[field.id];

      if (field.required && (!value || value.toString().trim() === '')) {
        validationErrors[field.id] = `${field.label} is required`;
        valid = false;
      } else if (value && field.validation) {
        if (field.type === 'number' && field.validation.min !== undefined && value < field.validation.min) {
          validationErrors[field.id] = `${field.label} must be at least ${field.validation.min}`;
          valid = false;
        } else if (field.type === 'number' && field.validation.max !== undefined && value > field.validation.max) {
          validationErrors[field.id] = `${field.label} must be at most ${field.validation.max}`;
          valid = false;
        } else if (field.validation.pattern && !new RegExp(field.validation.pattern).test(value)) {
          validationErrors[field.id] = field.validation.message || `${field.label} format is invalid`;
          valid = false;
        }
      }
    });

    setErrors(validationErrors);
    setIsValid(valid);
  }, [formData, fields]);

  const handleFieldChange = (fieldId: string, value: any) => {
    const newFormData = { ...formData, [fieldId]: value };
    setFormData(newFormData);
    onDataChange(newFormData);
  };

  const handleContinue = () => {
    if (isValid) {
      onContinue();
    }
  };

  const renderField = (field: any) => {
    const value = formData[field.id] || '';
    const error = errors[field.id];

    switch (field.type) {
      case 'select':
        return (
          <div key={field.id} className="space-y-2">
            <Label htmlFor={field.id}>{field.label} {field.required && '*'}</Label>
            <Select value={value} onValueChange={(val) => handleFieldChange(field.id, val)}>
              <SelectTrigger className={error ? 'border-red-500' : ''}>
                <SelectValue placeholder={field.placeholder || `Select ${field.label}`} />
              </SelectTrigger>
              <SelectContent>
                {field.options?.map((option: { value: string; label: string }) => (
                  <SelectItem key={option.value} value={option.value}>
                    {option.label}
                  </SelectItem>
                ))}
              </SelectContent>
            </Select>
            {error && <p className="text-sm text-red-500">{error}</p>}
          </div>
        );

      case 'textarea':
        return (
          <div key={field.id} className="space-y-2">
            <Label htmlFor={field.id}>{field.label} {field.required && '*'}</Label>
            <Textarea
              id={field.id}
              value={value}
              onChange={(e) => handleFieldChange(field.id, e.target.value)}
              placeholder={field.placeholder}
              className={error ? 'border-red-500' : ''}
              rows={4}
            />
            {error && <p className="text-sm text-red-500">{error}</p>}
          </div>
        );

      case 'date':
        return (
          <div key={field.id} className="space-y-2">
            <Label htmlFor={field.id}>{field.label} {field.required && '*'}</Label>
            <Input
              id={field.id}
              type="date"
              value={value}
              onChange={(e) => handleFieldChange(field.id, e.target.value)}
              className={error ? 'border-red-500' : ''}
            />
            {error && <p className="text-sm text-red-500">{error}</p>}
          </div>
        );

      default:
        return (
          <div key={field.id} className="space-y-2">
            <Label htmlFor={field.id}>{field.label} {field.required && '*'}</Label>
            <Input
              id={field.id}
              type={field.type}
              value={value}
              onChange={(e) => handleFieldChange(field.id, e.target.value)}
              placeholder={field.placeholder}
              className={error ? 'border-red-500' : ''}
            />
            {error && <p className="text-sm text-red-500">{error}</p>}
          </div>
        );
    }
  };

  return (
    <Card className="w-full">
      <CardHeader>
        <CardTitle>{title}</CardTitle>
        <CardDescription>{description}</CardDescription>
        {progress > 0 && (
          <div className="space-y-2">
            <div className="flex justify-between text-sm">
              <span>Progress</span>
              <span>{Math.round(progress)}%</span>
            </div>
            <Progress value={progress} className="w-full" />
          </div>
        )}
      </CardHeader>
      <CardContent className="space-y-6">
        {helpText && (
          <div className="p-4 bg-blue-50 border border-blue-200 rounded-md">
            <p className="text-sm text-blue-800">{helpText}</p>
          </div>
        )}

        <div className="space-y-4">
          {fields.map((field) => renderField(field))}
        </div>

        <div className="flex justify-between pt-4">
          <Button onClick={onBack} variant="outline" disabled={isLoading}>
            Back
          </Button>
          <Button
            onClick={handleContinue}
            disabled={!isValid || isLoading}
            className="min-w-[100px]"
          >
            {isLoading ? 'Processing...' : 'Continue'}
          </Button>
        </div>
      </CardContent>
    </Card>
  );
};

export default DataCollectionStepComponent;
