import { useState, useCallback } from 'react';
import { api, SearchRequest, SearchResult, ApiError } from '@/services/api';

export interface UseSearchOptions {
  searchType?: 'section_search' | 'case_search' | 'qa_search' | 'similarity_search';
  userType?: 'judge' | 'lawyer' | 'police' | 'student' | 'researcher' | 'general';
  maxResults?: number;
  filters?: Record<string, any>;
}

export interface UseSearchReturn {
  // State
  results: SearchResult | null;
  isLoading: boolean;
  error: string | null;
  
  // Actions
  search: (query: string) => Promise<void>;
  clearResults: () => void;
  clearError: () => void;
}

export function useSearch(options: UseSearchOptions = {}): UseSearchReturn {
  const [results, setResults] = useState<SearchResult | null>(null);
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const search = useCallback(async (query: string) => {
    if (!query.trim()) {
      setError('Please enter a search query');
      return;
    }

    setIsLoading(true);
    setError(null);

    try {
      const searchRequest: SearchRequest = {
        query: query.trim(),
        search_type: options.searchType || 'section_search',
        user_type: options.userType,
        filters: options.filters,
        max_results: options.maxResults || 10,
      };

      const searchResults = await api.search(searchRequest);
      setResults(searchResults);
    } catch (err) {
      if (err instanceof ApiError) {
        setError(err.message);
      } else {
        setError('An unexpected error occurred. Please try again.');
      }
      console.error('Search error:', err);
    } finally {
      setIsLoading(false);
    }
  }, [options.searchType, options.userType, options.filters, options.maxResults]);

  const clearResults = useCallback(() => {
    setResults(null);
    setError(null);
  }, []);

  const clearError = useCallback(() => {
    setError(null);
  }, []);

  return {
    results,
    isLoading,
    error,
    search,
    clearResults,
    clearError,
  };
}
