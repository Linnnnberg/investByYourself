/**
 * API Client Hook
 * Tech-028.1: Frontend-Backend Integration
 *
 * Manages API client with Supabase authentication integration.
 */

import { useEffect, useState } from 'react';
import { supabase } from '@/lib/supabase';
import { apiClient, ApiClient } from '@/lib/api-client';

export function useApiClient() {
  const [client, setClient] = useState<ApiClient>(apiClient);
  const [isAuthenticated, setIsAuthenticated] = useState(false);
  const [isLoading, setIsLoading] = useState(true);

  useEffect(() => {
    // Check for existing session
    const checkSession = async () => {
      try {
        const { data: { session } } = await supabase.auth.getSession();

        if (session?.access_token) {
          apiClient.setAuthToken(session.access_token);
          setIsAuthenticated(true);
        } else {
          apiClient.clearAuthToken();
          setIsAuthenticated(false);
        }
      } catch (error) {
        console.error('Error checking session:', error);
        apiClient.clearAuthToken();
        setIsAuthenticated(false);
      } finally {
        setIsLoading(false);
      }
    };

    checkSession();

    // Listen for auth changes
    const { data: { subscription } } = supabase.auth.onAuthStateChange(
      async (event, session) => {
        if (session?.access_token) {
          apiClient.setAuthToken(session.access_token);
          setIsAuthenticated(true);
        } else {
          apiClient.clearAuthToken();
          setIsAuthenticated(false);
        }
        setIsLoading(false);
      }
    );

    return () => {
      subscription.unsubscribe();
    };
  }, []);

  return {
    client,
    isAuthenticated,
    isLoading,
  };
}

// Hook for API calls with error handling
export function useApiCall<T>(
  apiCall: () => Promise<T>,
  dependencies: any[] = []
) {
  const [data, setData] = useState<T | null>(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const execute = async () => {
    try {
      setLoading(true);
      setError(null);
      const result = await apiCall();
      setData(result);
    } catch (err) {
      const errorMessage = err instanceof Error ? err.message : 'Unknown error';
      setError(errorMessage);
      console.error('API call failed:', err);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    execute();
  }, dependencies);

  return {
    data,
    loading,
    error,
    refetch: execute,
  };
}
