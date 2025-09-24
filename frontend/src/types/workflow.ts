export interface WorkflowStep {
  id: string;
  name: string;
  step_type: WorkflowStepType;
  description?: string;
  config: Record<string, any>;
  dependencies: string[];
}

export type WorkflowStepType =
  | 'data_collection'
  | 'decision'
  | 'validation'
  | 'user_interaction'
  | 'analysis'
  | 'transformation'
  | 'integration'
  | 'ai_generated';

export interface WorkflowDefinition {
  id: string;
  name: string;
  description: string;
  steps: WorkflowStep[];
  entry_points: string[];
  exit_points: string[];
  version?: string;
  category?: string;
  created_at?: string;
}

export interface WorkflowContext {
  user_id?: string;
  session_id?: string;
  workflow_id?: string;
  execution_id?: string;
  data: Record<string, any>;
  status?: string;
  current_step?: string;
  created_at?: Date | string;
  updated_at?: Date | string;
}

export interface WorkflowError extends Error {
  code?: string;
  details?: any;
}
