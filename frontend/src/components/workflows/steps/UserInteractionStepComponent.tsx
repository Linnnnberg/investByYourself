"use client";

import React, { useState, useEffect, useMemo } from "react";
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import { Checkbox } from "@/components/ui/checkbox";
import { Badge } from "@/components/ui/badge";
import { Alert, AlertDescription } from "@/components/ui/alert";
import { Search, Filter, CheckCircle, AlertCircle, HelpCircle, X } from "lucide-react";

interface SelectableItem {
  id: string;
  name: string;
  description?: string;
  category?: string;
  tags?: string[];
  metadata?: Record<string, any>;
  disabled?: boolean;
}

interface FilterOption {
  id: string;
  label: string;
  type: "checkbox" | "range" | "select";
  options?: { value: string; label: string }[];
  min?: number;
  max?: number;
}

interface UserInteractionStepComponentProps {
  stepId: string;
  title: string;
  description: string;
  items: SelectableItem[];
  selectionType: "single" | "multiple";
  searchEnabled?: boolean;
  filters?: FilterOption[];
  maxSelections?: number;
  minSelections?: number;
  helpText?: string;
  onSelectionChange: (selectedItems: SelectableItem[]) => void;
  onContinue: () => void;
  onBack?: () => void;
  isLoading?: boolean;
  initialSelection?: SelectableItem[];
}

export function UserInteractionStepComponent({
  stepId,
  title,
  description,
  items,
  selectionType,
  searchEnabled = true,
  filters = [],
  maxSelections,
  minSelections = 1,
  helpText,
  onSelectionChange,
  onContinue,
  onBack,
  isLoading = false,
  initialSelection = [],
}: UserInteractionStepComponentProps) {
  const [selectedItems, setSelectedItems] = useState<SelectableItem[]>(initialSelection);
  const [searchQuery, setSearchQuery] = useState("");
  const [activeFilters, setActiveFilters] = useState<Record<string, any>>({});
  const [showFilters, setShowFilters] = useState(false);

  useEffect(() => {
    onSelectionChange(selectedItems);
  }, [selectedItems, onSelectionChange]);

  const filteredItems = useMemo(() => {
    let filtered = items;

    // Apply search filter
    if (searchQuery) {
      filtered = filtered.filter((item) =>
        item.name.toLowerCase().includes(searchQuery.toLowerCase()) ||
        item.description?.toLowerCase().includes(searchQuery.toLowerCase()) ||
        item.tags?.some(tag => tag.toLowerCase().includes(searchQuery.toLowerCase()))
      );
    }

    // Apply custom filters
    Object.entries(activeFilters).forEach(([filterId, filterValue]) => {
      if (filterValue !== undefined && filterValue !== "") {
        const filter = filters.find(f => f.id === filterId);
        if (filter) {
          filtered = filtered.filter((item) => {
            const itemValue = item.metadata?.[filterId];
            if (filter.type === "checkbox") {
              return Array.isArray(filterValue) ? filterValue.includes(itemValue) : itemValue === filterValue;
            } else if (filter.type === "range") {
              const numValue = parseFloat(itemValue);
              return numValue >= filter.min! && numValue <= filter.max!;
            } else if (filter.type === "select") {
              return itemValue === filterValue;
            }
            return true;
          });
        }
      }
    });

    return filtered;
  }, [items, searchQuery, activeFilters, filters]);

  const handleItemToggle = (item: SelectableItem) => {
    if (item.disabled) return;

    if (selectionType === "single") {
      setSelectedItems([item]);
    } else {
      const isSelected = selectedItems.some(selected => selected.id === item.id);
      if (isSelected) {
        setSelectedItems(selectedItems.filter(selected => selected.id !== item.id));
      } else {
        if (maxSelections && selectedItems.length >= maxSelections) {
          return; // Don't add if max selections reached
        }
        setSelectedItems([...selectedItems, item]);
      }
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
    setSearchQuery("");
  };

  const canContinue = () => {
    return selectedItems.length >= minSelections &&
           (!maxSelections || selectedItems.length <= maxSelections);
  };

  const getSelectionStatus = () => {
    if (selectedItems.length < minSelections) {
      return {
        status: "error",
        message: `Please select at least ${minSelections} item${minSelections > 1 ? 's' : ''}`,
      };
    }
    if (maxSelections && selectedItems.length > maxSelections) {
      return {
        status: "error",
        message: `Please select no more than ${maxSelections} items`,
      };
    }
    return {
      status: "success",
      message: `${selectedItems.length} item${selectedItems.length !== 1 ? 's' : ''} selected`,
    };
  };

  const selectionStatus = getSelectionStatus();

  return (
    <Card className="w-full max-w-4xl mx-auto">
      <CardHeader>
        <CardTitle className="flex items-center gap-2">
          {title}
        </CardTitle>
        <CardDescription>{description}</CardDescription>

        {helpText && (
          <Alert className="mt-4">
            <HelpCircle className="h-4 w-4" />
            <AlertDescription>{helpText}</AlertDescription>
          </Alert>
        )}

        {/* Search and Filters */}
        <div className="flex gap-2 mt-4">
          {searchEnabled && (
            <div className="flex-1 relative">
              <Search className="absolute left-3 top-1/2 transform -translate-y-1/2 h-4 w-4 text-muted-foreground" />
              <Input
                placeholder="Search items..."
                value={searchQuery}
                onChange={(e) => setSearchQuery(e.target.value)}
                className="pl-10"
                disabled={isLoading}
              />
            </div>
          )}
          {filters.length > 0 && (
            <Button
              variant="outline"
              onClick={() => setShowFilters(!showFilters)}
              className="flex items-center gap-2"
            >
              <Filter className="h-4 w-4" />
              Filters
            </Button>
          )}
        </div>

        {/* Filters Panel */}
        {showFilters && filters.length > 0 && (
          <div className="mt-4 p-4 border rounded-lg bg-muted/50">
            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
              {filters.map((filter) => (
                <div key={filter.id} className="space-y-2">
                  <Label className="text-sm font-medium">{filter.label}</Label>
                  {filter.type === "checkbox" && filter.options && (
                    <div className="space-y-1">
                      {filter.options.map((option) => (
                        <div key={option.value} className="flex items-center space-x-2">
                          <Checkbox
                            id={`${filter.id}-${option.value}`}
                            checked={Array.isArray(activeFilters[filter.id]) &&
                                    activeFilters[filter.id].includes(option.value)}
                            onCheckedChange={(checked) => {
                              const currentValues = activeFilters[filter.id] || [];
                              const newValues = checked
                                ? [...currentValues, option.value]
                                : currentValues.filter((v: string) => v !== option.value);
                              handleFilterChange(filter.id, newValues);
                            }}
                          />
                          <Label htmlFor={`${filter.id}-${option.value}`} className="text-xs">
                            {option.label}
                          </Label>
                        </div>
                      ))}
                    </div>
                  )}
                  {filter.type === "select" && filter.options && (
                    <select
                      value={activeFilters[filter.id] || ""}
                      onChange={(e) => handleFilterChange(filter.id, e.target.value)}
                      className="w-full p-2 border rounded text-sm"
                    >
                      <option value="">All</option>
                      {filter.options.map((option) => (
                        <option key={option.value} value={option.value}>
                          {option.label}
                        </option>
                      ))}
                    </select>
                  )}
                </div>
              ))}
            </div>
            <div className="flex justify-end mt-4">
              <Button variant="outline" size="sm" onClick={clearFilters}>
                Clear Filters
              </Button>
            </div>
          </div>
        )}
      </CardHeader>
      <CardContent className="space-y-6">
        {/* Selection Status */}
        <div className={`p-3 rounded-lg border ${
          selectionStatus.status === "error" ? "border-red-200 bg-red-50" : "border-green-200 bg-green-50"
        }`}>
          <div className="flex items-center gap-2">
            {selectionStatus.status === "error" ? (
              <AlertCircle className="h-4 w-4 text-red-500" />
            ) : (
              <CheckCircle className="h-4 w-4 text-green-500" />
            )}
            <span className={`text-sm font-medium ${
              selectionStatus.status === "error" ? "text-red-700" : "text-green-700"
            }`}>
              {selectionStatus.message}
            </span>
          </div>
        </div>

        {/* Items Grid */}
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4 max-h-96 overflow-y-auto">
          {filteredItems.map((item) => {
            const isSelected = selectedItems.some(selected => selected.id === item.id);
            return (
              <div
                key={item.id}
                className={`p-4 border rounded-lg cursor-pointer transition-all ${
                  isSelected
                    ? "border-blue-500 bg-blue-50"
                    : item.disabled
                    ? "border-gray-200 bg-gray-50 cursor-not-allowed opacity-50"
                    : "border-gray-200 hover:border-gray-300 hover:bg-gray-50"
                }`}
                onClick={() => handleItemToggle(item)}
              >
                <div className="flex items-start justify-between">
                  <div className="flex-1 min-w-0">
                    <div className="flex items-center gap-2 mb-2">
                      {selectionType === "multiple" && (
                        <Checkbox
                          checked={isSelected}
                          disabled={item.disabled}
                          className="pointer-events-none"
                        />
                      )}
                      <h4 className="font-medium text-sm truncate">{item.name}</h4>
                    </div>
                    {item.description && (
                      <p className="text-xs text-muted-foreground mb-2 line-clamp-2">
                        {item.description}
                      </p>
                    )}
                    {item.category && (
                      <Badge variant="secondary" className="text-xs">
                        {item.category}
                      </Badge>
                    )}
                    {item.tags && item.tags.length > 0 && (
                      <div className="flex flex-wrap gap-1 mt-2">
                        {item.tags.slice(0, 3).map((tag) => (
                          <Badge key={tag} variant="outline" className="text-xs">
                            {tag}
                          </Badge>
                        ))}
                        {item.tags.length > 3 && (
                          <Badge variant="outline" className="text-xs">
                            +{item.tags.length - 3}
                          </Badge>
                        )}
                      </div>
                    )}
                  </div>
                </div>
              </div>
            );
          })}
        </div>

        {filteredItems.length === 0 && (
          <div className="text-center py-8 text-muted-foreground">
            <Search className="h-8 w-8 mx-auto mb-2 opacity-50" />
            <p>No items found matching your criteria</p>
            <Button variant="outline" size="sm" onClick={clearFilters} className="mt-2">
              Clear Filters
            </Button>
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
