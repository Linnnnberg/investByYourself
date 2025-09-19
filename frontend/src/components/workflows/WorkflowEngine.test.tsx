import React from 'react';
import { render, screen, fireEvent, waitFor } from '@testing-library/react';
import '@testing-library/jest-dom';
import MinimalWorkflowEngine from './MinimalWorkflowEngine';

// Mock workflow definition
const mockWorkflow = {
  id: 'test_workflow',
  name: 'Test Workflow',
  description: 'A test workflow for unit testing',
  steps: [
    {
      id: 'step1',
      name: 'Test Step 1',
      step_type: 'data_collection' as const,
      description: 'First test step',
      config: { required_fields: ['test_field'] },
      dependencies: []
    },
    {
      id: 'step2',
      name: 'Test Step 2',
      step_type: 'decision' as const,
      description: 'Second test step',
      config: { options: ['option1', 'option2'] },
      dependencies: ['step1']
    }
  ],
  entry_points: ['step1'],
  exit_points: ['step2']
};

const mockContext = {
  user_id: 'test_user',
  session_id: 'test_session',
  data: {},
  created_at: new Date().toISOString()
};

describe('MinimalWorkflowEngine', () => {
  it('renders workflow start screen', () => {
    render(
      <MinimalWorkflowEngine
        workflow={mockWorkflow}
        context={mockContext}
        onComplete={jest.fn()}
        onError={jest.fn()}
      />
    );

    expect(screen.getByText('Test Workflow')).toBeInTheDocument();
    expect(screen.getByText('A test workflow for unit testing')).toBeInTheDocument();
    expect(screen.getByText('Start Workflow')).toBeInTheDocument();
  });

  it('starts workflow when start button is clicked', async () => {
    const onComplete = jest.fn();
    const onError = jest.fn();

    render(
      <MinimalWorkflowEngine
        workflow={mockWorkflow}
        context={mockContext}
        onComplete={onComplete}
        onError={onError}
      />
    );

    const startButton = screen.getByText('Start Workflow');
    fireEvent.click(startButton);

    // Wait for the workflow to start and complete
    await waitFor(() => {
      expect(screen.getByText('Workflow Completed!')).toBeInTheDocument();
    });

    expect(onComplete).toHaveBeenCalled();
  });

  it('shows progress during workflow execution', async () => {
    render(
      <MinimalWorkflowEngine
        workflow={mockWorkflow}
        context={mockContext}
        onComplete={jest.fn()}
        onError={jest.fn()}
      />
    );

    const startButton = screen.getByText('Start Workflow');
    fireEvent.click(startButton);

    // Check that progress is shown
    await waitFor(() => {
      expect(screen.getByText(/Progress:/)).toBeInTheDocument();
    });
  });

  it('handles workflow errors', async () => {
    const onError = jest.fn();

    // Create a workflow that will cause an error
    const errorWorkflow = {
      ...mockWorkflow,
      steps: [
        {
          id: 'error_step',
          name: 'Error Step',
          step_type: 'unknown_type' as any,
          description: 'This step will cause an error',
          config: {},
          dependencies: []
        }
      ],
      entry_points: ['error_step'],
      exit_points: ['error_step']
    };

    render(
      <MinimalWorkflowEngine
        workflow={errorWorkflow}
        context={mockContext}
        onComplete={jest.fn()}
        onError={onError}
      />
    );

    const startButton = screen.getByText('Start Workflow');
    fireEvent.click(startButton);

    await waitFor(() => {
      expect(screen.getByText('Workflow Failed')).toBeInTheDocument();
    });

    expect(onError).toHaveBeenCalled();
  });
});
