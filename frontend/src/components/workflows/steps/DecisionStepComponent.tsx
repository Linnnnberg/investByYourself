'use client';

import React, { useState, useEffect } from 'react';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Label } from '@/components/ui/label';
import { RadioGroup, RadioGroupItem } from '@/components/ui/radio-group';
import { Checkbox } from '@/components/ui/checkbox';
import { WorkflowStep, WorkflowContext } from '@/types/workflow';

interface DecisionStepComponentProps {
  stepId: string;
  title: string;
  description: string;
  options: Array<{
    id: string;
    label: string;
    description?: string;
    value: string;
    disabled?: boolean;
  }>;
  inputType: 'radio' | 'checkbox';
  required?: boolean;
  helpText?: string;
  validation?: {
    minSelections?: number;
    maxSelections?: number;
  };
  onSelectionChange: (selection: string | string[]) => void;
  onContinue: () => void;
  onBack: () => void;
  isLoading: boolean;
  selectedValue?: string | string[];
}

const DecisionStepComponent: React.FC<DecisionStepComponentProps> = ({
  stepId,
  title,
  description,
  options,
  inputType = 'radio',
  required = true,
  helpText,
  validation,
  onSelectionChange,
  onContinue,
  onBack,
  isLoading,
  selectedValue
}) => {
  const [selection, setSelection] = useState<string | string[]>(
    inputType === 'radio' ? (selectedValue as string) || '' : (selectedValue as string[]) || []
  );
  const [errors, setErrors] = useState<string>('');

  useEffect(() => {
    // Validate selection
    let error = '';

    if (required) {
      if (inputType === 'radio' && !selection) {
        error = 'Please make a selection';
      } else if (inputType === 'checkbox') {
        const selectedArray = selection as string[];
        if (selectedArray.length === 0) {
          error = 'Please select at least one option';
        } else if (validation?.minSelections && selectedArray.length < validation.minSelections) {
          error = `Please select at least ${validation.minSelections} options`;
        } else if (validation?.maxSelections && selectedArray.length > validation.maxSelections) {
          error = `Please select at most ${validation.maxSelections} options`;
        }
      }
    }

    setErrors(error);
  }, [selection, required, inputType, validation]);

  const handleSelectionChange = (value: string) => {
    if (inputType === 'radio') {
      setSelection(value);
      onSelectionChange(value);
    } else {
      const currentSelection = selection as string[];
      const newSelection = currentSelection.includes(value)
        ? currentSelection.filter(item => item !== value)
        : [...currentSelection, value];

      setSelection(newSelection);
      onSelectionChange(newSelection);
    }
  };

  const handleContinue = () => {
    if (!errors) {
      onContinue();
    }
  };

  const renderRadioOptions = () => (
    <RadioGroup value={selection as string} onValueChange={handleSelectionChange}>
      <div className="space-y-3">
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
                className={`text-sm font-medium ${option.disabled ? 'text-gray-400' : 'text-gray-900'}`}
              >
                {option.label}
              </Label>
              {option.description && (
                <p className="text-xs text-gray-500 mt-1">{option.description}</p>
              )}
            </div>
          </div>
        ))}
      </div>
    </RadioGroup>
  );

  const renderCheckboxOptions = () => (
    <div className="space-y-3">
      {options.map((option) => {
        const isSelected = (selection as string[]).includes(option.value);
        return (
          <div key={option.id} className="flex items-start space-x-3">
            <Checkbox
              id={option.id}
              checked={isSelected}
              onCheckedChange={() => handleSelectionChange(option.value)}
              disabled={option.disabled || isLoading}
              className="mt-1"
            />
            <div className="flex-1">
              <Label
                htmlFor={option.id}
                className={`text-sm font-medium ${option.disabled ? 'text-gray-400' : 'text-gray-900'}`}
              >
                {option.label}
              </Label>
              {option.description && (
                <p className="text-xs text-gray-500 mt-1">{option.description}</p>
              )}
            </div>
          </div>
        );
      })}
    </div>
  );

  return (
    <Card className="w-full">
      <CardHeader>
        <CardTitle>{title}</CardTitle>
        <CardDescription>{description}</CardDescription>
      </CardHeader>
      <CardContent className="space-y-6">
        {helpText && (
          <div className="p-4 bg-blue-50 border border-blue-200 rounded-md">
            <p className="text-sm text-blue-800">{helpText}</p>
          </div>
        )}

        <div className="space-y-4">
          {inputType === 'radio' ? renderRadioOptions() : renderCheckboxOptions()}
        </div>

        {errors && (
          <div className="p-3 bg-red-50 border border-red-200 rounded-md">
            <p className="text-sm text-red-800">{errors}</p>
          </div>
        )}

        <div className="flex justify-between pt-4">
          <Button onClick={onBack} variant="outline" disabled={isLoading}>
            Back
          </Button>
          <Button
            onClick={handleContinue}
            disabled={!!errors || isLoading}
            className="min-w-[100px]"
          >
            {isLoading ? 'Processing...' : 'Continue'}
          </Button>
        </div>
      </CardContent>
    </Card>
  );
};

export default DecisionStepComponent;
