/**
 * Workflow TypeScript Types
 * InvestByYourself Financial Platform
 *
 * Type definitions for workflow engine and API.
 */

export enum WorkflowStepType {
  DATA_COLLECTION = 'data_collection',
  DECISION = 'decision',
  VALIDATION = 'validation',
  USER_INTERACTION = 'user_interaction',
  AI_GENERATED = 'ai_generated'
}

export enum WorkflowStatus {
  PENDING = 'pending',
  RUNNING = 'running',
  PAUSED = 'paused',
  COMPLETED = 'completed',
  FAILED = 'failed',
  CANCELLED = 'cancelled'
}

export interface WorkflowContext {
  user_id: string;
  session_id: string;
  data: Record<string, any>;
}

export interface WorkflowStep {
  id: string;
  name: string;
  step_type: WorkflowStepType;
  description?: string;
  config: Record<string, any>;
  dependencies: string[];
  ai_generated?: boolean;
  ai_prompt?: string;
}

export interface WorkflowDefinition {
  id: string;
  name: string;
  description?: string;
  version: string;
  category?: string;
  steps: WorkflowStep[];
  entry_points: string[];
  exit_points: string[];
  ai_configurable?: boolean;
  created_at?: string;
}

export interface WorkflowExecutionRequest {
  workflow_id: string;
  context: WorkflowContext;
  start_step_id?: string;
}

export interface WorkflowExecutionResponse {
  execution_id: string;
  workflow_id: string;
  status: WorkflowStatus;
  current_step?: string;
  progress: number;
  results: Record<string, any>;
  error_message?: string;
  started_at: string;
  completed_at?: string;
}

export interface WorkflowStatusResponse {
  execution_id: string;
  workflow_id: string;
  status: WorkflowStatus;
  current_step?: string;
  progress: number;
  step_results: Record<string, any>;
  error_message?: string;
  started_at: string;
  completed_at?: string;
}

export interface WorkflowListResponse {
  workflows: WorkflowDefinition[];
  total: number;
}

export interface StepExecutionRequest {
  execution_id: string;
  workflow_id: string;
  step_id: string;
  context: WorkflowContext;
  step_input: Record<string, any>;
}

export interface StepExecutionResponse {
  execution_id: string;
  workflow_id: string;
  step_id: string;
  status: WorkflowStatus;
  result: any;
  executed_at: string;
}

// UI-specific types for enhanced components

export interface DecisionOption {
  id: string;
  label: string;
  description?: string;
  value: string;
  disabled?: boolean;
}

export interface FormField {
  id: string;
  label: string;
  type: 'text' | 'email' | 'number' | 'textarea' | 'currency' | 'percentage';
  placeholder?: string;
  required?: boolean;
  validation?: {
    min?: number;
    max?: number;
    pattern?: string;
    message?: string;
  };
  description?: string;
  icon?: string;
}

export interface ValidationResult {
  id: string;
  label: string;
  status: 'success' | 'warning' | 'error';
  message: string;
  details?: string;
}

export interface SelectableItem {
  id: string;
  name: string;
  description?: string;
  category?: string;
  tags?: string[];
  metadata?: Record<string, any>;
  disabled?: boolean;
}

export interface FilterOption {
  id: string;
  label: string;
  type: 'checkbox' | 'range' | 'select';
  options?: { value: string; label: string }[];
  min?: number;
  max?: number;
}

// Hook types for React components

export interface UseWorkflowExecutionOptions {
  onComplete?: (result: WorkflowExecutionResponse) => void;
  onError?: (error: Error) => void;
  onStepComplete?: (stepId: string, result: any) => void;
  onStatusUpdate?: (status: WorkflowStatusResponse) => void;
  pollInterval?: number;
  maxPollAttempts?: number;
}

export interface UseWorkflowExecutionReturn {
  execution: WorkflowExecutionResponse | null;
  status: WorkflowStatusResponse | null;
  isLoading: boolean;
  error: Error | null;
  executeWorkflow: (request: WorkflowExecutionRequest) => Promise<void>;
  executeStep: (request: StepExecutionRequest) => Promise<void>;
  pauseWorkflow: () => Promise<void>;
  resumeWorkflow: () => Promise<void>;
  cancelWorkflow: () => Promise<void>;
  refreshStatus: () => Promise<void>;
}

// Error types

export interface WorkflowError {
  code: string;
  message: string;
  details?: any;
  step_id?: string;
  execution_id?: string;
}

export interface ApiError {
  status: number;
  message: string;
  details?: any;
}
