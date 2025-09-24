'use client';

import React, { useState, useEffect, useMemo } from 'react';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { Label } from '@/components/ui/label';
import { Checkbox } from '@/components/ui/checkbox';
import { Badge } from '@/components/ui/badge';
import { Search, Filter, X } from 'lucide-react';
import { WorkflowStep, WorkflowContext } from '@/types/workflow';

interface Item {
  id: string;
  name: string;
  description?: string;
  category?: string;
  tags?: string[];
  metadata?: Record<string, any>;
}

interface FilterOption {
  id: string;
  label: string;
  type: 'select' | 'multiselect' | 'range';
  options?: Array<{ value: string; label: string }>;
  min?: number;
  max?: number;
}

interface UserInteractionStepComponentProps {
  stepId: string;
  title: string;
  description: string;
  items: Item[];
  selectionType: 'single' | 'multiple';
  searchEnabled?: boolean;
  filters?: FilterOption[];
  maxSelections?: number;
  minSelections?: number;
  helpText?: string;
  onSelectionChange: (selection: Item[]) => void;
  onContinue: () => void;
  onBack: () => void;
  isLoading: boolean;
  initialSelection?: Item[];
}

const UserInteractionStepComponent: React.FC<UserInteractionStepComponentProps> = ({
  stepId,
  title,
  description,
  items,
  selectionType = 'single',
  searchEnabled = true,
  filters = [],
  maxSelections,
  minSelections = 1,
  helpText,
  onSelectionChange,
  onContinue,
  onBack,
  isLoading,
  initialSelection = []
}) => {
  const [searchQuery, setSearchQuery] = useState('');
  const [selectedItems, setSelectedItems] = useState<Item[]>(initialSelection);
  const [activeFilters, setActiveFilters] = useState<Record<string, any>>({});
  const [showFilters, setShowFilters] = useState(false);

  const filteredItems = useMemo(() => {
    let filtered = items;

    // Apply search filter
    if (searchQuery) {
      filtered = filtered.filter(item =>
        item.name.toLowerCase().includes(searchQuery.toLowerCase()) ||
        item.description?.toLowerCase().includes(searchQuery.toLowerCase()) ||
        item.tags?.some(tag => tag.toLowerCase().includes(searchQuery.toLowerCase()))
      );
    }

    // Apply custom filters
    Object.entries(activeFilters).forEach(([filterId, filterValue]) => {
      if (filterValue) {
        const filter = filters.find(f => f.id === filterId);
        if (filter) {
          filtered = filtered.filter(item => {
            const itemValue = item.metadata?.[filterId];
            if (filter.type === 'select' || filter.type === 'multiselect') {
              return Array.isArray(filterValue)
                ? filterValue.includes(itemValue)
                : itemValue === filterValue;
            } else if (filter.type === 'range') {
              return itemValue >= filterValue.min && itemValue <= filterValue.max;
            }
            return true;
          });
        }
      }
    });

    return filtered;
  }, [items, searchQuery, activeFilters, filters]);

  const handleItemToggle = (item: Item) => {
    if (selectionType === 'single') {
      const newSelection = selectedItems.includes(item) ? [] : [item];
      setSelectedItems(newSelection);
      onSelectionChange(newSelection);
    } else {
      const isSelected = selectedItems.some(selected => selected.id === item.id);
      let newSelection;

      if (isSelected) {
        newSelection = selectedItems.filter(selected => selected.id !== item.id);
      } else {
        if (maxSelections && selectedItems.length >= maxSelections) {
          return; // Don't add if max selections reached
        }
        newSelection = [...selectedItems, item];
      }

      setSelectedItems(newSelection);
      onSelectionChange(newSelection);
    }
  };

  const handleFilterChange = (filterId: string, value: any) => {
    setActiveFilters(prev => ({
      ...prev,
      [filterId]: value
    }));
  };

  const clearFilters = () => {
    setActiveFilters({});
    setSearchQuery('');
  };

  const isSelectionValid = () => {
    if (selectionType === 'single') {
      return selectedItems.length >= minSelections;
    } else {
      return selectedItems.length >= minSelections &&
             (!maxSelections || selectedItems.length <= maxSelections);
    }
  };

  const canContinue = isSelectionValid();

  const handleContinue = () => {
    if (canContinue) {
      onContinue();
    }
  };

  const renderFilter = (filter: FilterOption) => {
    switch (filter.type) {
      case 'select':
        return (
          <div key={filter.id} className="space-y-2">
            <Label className="text-sm font-medium">{filter.label}</Label>
            <select
              value={activeFilters[filter.id] || ''}
              onChange={(e) => handleFilterChange(filter.id, e.target.value || null)}
              className="w-full p-2 border border-gray-300 rounded-md text-sm"
            >
              <option value="">All</option>
              {filter.options?.map(option => (
                <option key={option.value} value={option.value}>
                  {option.label}
                </option>
              ))}
            </select>
          </div>
        );

      case 'multiselect':
        return (
          <div key={filter.id} className="space-y-2">
            <Label className="text-sm font-medium">{filter.label}</Label>
            <div className="space-y-1">
              {filter.options?.map(option => (
                <label key={option.value} className="flex items-center space-x-2">
                  <Checkbox
                    checked={(activeFilters[filter.id] || []).includes(option.value)}
                    onCheckedChange={(checked) => {
                      const current = activeFilters[filter.id] || [];
                      const newValue = checked
                        ? [...current, option.value]
                        : current.filter((v: string) => v !== option.value);
                      handleFilterChange(filter.id, newValue.length > 0 ? newValue : null);
                    }}
                  />
                  <span className="text-sm">{option.label}</span>
                </label>
              ))}
            </div>
          </div>
        );

      default:
        return null;
    }
  };

  return (
    <Card className="w-full">
      <CardHeader>
        <CardTitle>{title}</CardTitle>
        <CardDescription>{description}</CardDescription>
        {helpText && (
          <p className="text-sm text-gray-600 mt-2">{helpText}</p>
        )}
      </CardHeader>
      <CardContent className="space-y-6">
        {/* Search and Filters */}
        <div className="space-y-4">
          {searchEnabled && (
            <div className="relative">
              <Search className="absolute left-3 top-1/2 transform -translate-y-1/2 h-4 w-4 text-gray-400" />
              <Input
                placeholder="Search items..."
                value={searchQuery}
                onChange={(e) => setSearchQuery(e.target.value)}
                className="pl-10"
              />
            </div>
          )}

          {filters.length > 0 && (
            <div className="space-y-3">
              <div className="flex items-center justify-between">
                <Button
                  variant="outline"
                  size="sm"
                  onClick={() => setShowFilters(!showFilters)}
                >
                  <Filter className="h-4 w-4 mr-2" />
                  Filters
                </Button>
                {Object.keys(activeFilters).length > 0 && (
                  <Button
                    variant="ghost"
                    size="sm"
                    onClick={clearFilters}
                  >
                    <X className="h-4 w-4 mr-2" />
                    Clear
                  </Button>
                )}
              </div>

              {showFilters && (
                <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4 p-4 bg-gray-50 rounded-md">
                  {filters.map(renderFilter)}
                </div>
              )}
            </div>
          )}
        </div>

        {/* Selection Summary */}
        {selectedItems.length > 0 && (
          <div className="p-3 bg-blue-50 border border-blue-200 rounded-md">
            <div className="flex items-center justify-between">
              <span className="text-sm font-medium text-blue-800">
                {selectedItems.length} item{selectedItems.length !== 1 ? 's' : ''} selected
                {maxSelections && ` (max ${maxSelections})`}
              </span>
              <div className="flex flex-wrap gap-1">
                {selectedItems.map(item => (
                  <Badge key={item.id} variant="secondary" className="text-xs">
                    {item.name}
                    <button
                      onClick={() => handleItemToggle(item)}
                      className="ml-1 hover:bg-gray-300 rounded-full"
                    >
                      <X className="h-3 w-3" />
                    </button>
                  </Badge>
                ))}
              </div>
            </div>
          </div>
        )}

        {/* Items List */}
        <div className="space-y-2 max-h-96 overflow-y-auto">
          {filteredItems.length === 0 ? (
            <div className="text-center py-8 text-gray-500">
              No items found matching your criteria.
            </div>
          ) : (
            filteredItems.map(item => {
              const isSelected = selectedItems.some(selected => selected.id === item.id);
              const isDisabled = selectionType === 'multiple' &&
                               maxSelections &&
                               !isSelected &&
                               selectedItems.length >= maxSelections;

              return (
                <div
                  key={item.id}
                  className={`p-4 border rounded-md cursor-pointer transition-colors ${
                    isSelected
                      ? 'border-blue-500 bg-blue-50'
                      : isDisabled
                      ? 'border-gray-200 bg-gray-50 cursor-not-allowed opacity-50'
                      : 'border-gray-200 hover:border-gray-300 hover:bg-gray-50'
                  }`}
                  onClick={() => !isDisabled && handleItemToggle(item)}
                >
                  <div className="flex items-start space-x-3">
                    {selectionType === 'multiple' ? (
                      <Checkbox
                        checked={isSelected}
                        disabled={isDisabled}
                        className="mt-1"
                      />
                    ) : (
                      <input
                        type="radio"
                        checked={isSelected}
                        disabled={isDisabled}
                        className="mt-1"
                        readOnly
                      />
                    )}
                    <div className="flex-1 min-w-0">
                      <div className="flex items-center justify-between">
                        <h4 className="font-medium text-sm text-gray-900">{item.name}</h4>
                        {item.category && (
                          <Badge variant="outline" className="text-xs">
                            {item.category}
                          </Badge>
                        )}
                      </div>
                      {item.description && (
                        <p className="text-sm text-gray-600 mt-1">{item.description}</p>
                      )}
                      {item.tags && item.tags.length > 0 && (
                        <div className="flex flex-wrap gap-1 mt-2">
                          {item.tags.map(tag => (
                            <Badge key={tag} variant="secondary" className="text-xs">
                              {tag}
                            </Badge>
                          ))}
                        </div>
                      )}
                    </div>
                  </div>
                </div>
              );
            })
          )}
        </div>

        {/* Validation Messages */}
        {!canContinue && selectedItems.length > 0 && (
          <div className="p-3 bg-yellow-50 border border-yellow-200 rounded-md">
            <p className="text-sm text-yellow-800">
              {selectedItems.length < minSelections
                ? `Please select at least ${minSelections} item${minSelections !== 1 ? 's' : ''}.`
                : `Please select at most ${maxSelections} item${maxSelections !== 1 ? 's' : ''}.`
              }
            </p>
          </div>
        )}

        <div className="flex justify-between pt-4">
          <Button onClick={onBack} variant="outline" disabled={isLoading}>
            Back
          </Button>
          <Button
            onClick={handleContinue}
            disabled={!canContinue || isLoading}
            className="min-w-[100px]"
          >
            {isLoading ? 'Processing...' : 'Continue'}
          </Button>
        </div>
      </CardContent>
    </Card>
  );
};

export default UserInteractionStepComponent;
