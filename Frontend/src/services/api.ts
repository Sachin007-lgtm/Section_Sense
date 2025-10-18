// API service for communicating with the backend
import { API_CONFIG } from '@/config/api';

const API_BASE_URL = API_CONFIG.BASE_URL;

export interface SearchRequest {
  query: string;
  search_type: 'section_search' | 'case_search' | 'qa_search' | 'similarity_search';
  user_type?: 'judge' | 'lawyer' | 'police' | 'student' | 'researcher' | 'general';
  filters?: Record<string, any>;
  max_results?: number;
}

export interface LawSectionResponse {
  section_code: string;
  section_number: string;
  title: string;
  description: string;
  category: string;
  punishment?: string;
  fine_range?: string;
  imprisonment_range?: string;
  bailable?: string;
  cognizable?: string;
  compoundable?: string;
  source?: string;
  last_updated?: string;
}

export interface SearchResult {
  query: string;
  search_type: string;
  total_results: number;
  execution_time: number;
  results: LawSectionResponse[];
  suggestions?: string[];
  filters_applied?: Record<string, any>;
}

export interface QARequest {
  question: string;
  context?: string;
  user_type?: 'judge' | 'lawyer' | 'police' | 'student' | 'researcher' | 'general';
}

export interface QAResponse {
  question: string;
  answer: string;
  confidence_score: number;
  relevant_sections: LawSectionResponse[];
  relevant_cases: any[];
  sources: string[];
  timestamp: string;
}

export interface SystemHealth {
  status: string;
  database_connected: boolean;
  search_index_healthy: boolean;
  total_sections: number;
  total_cases: number;
  last_data_update?: string;
  system_uptime?: string;
}

class ApiError extends Error {
  constructor(
    message: string,
    public status: number,
    public response?: any
  ) {
    super(message);
    this.name = 'ApiError';
  }
}

async function handleResponse<T>(response: Response): Promise<T> {
  if (!response.ok) {
    let errorMessage = `HTTP ${response.status}: ${response.statusText}`;
    let errorData;
    
    try {
      errorData = await response.json();
      errorMessage = errorData.message || errorData.detail || errorMessage;
    } catch {
      // If response is not JSON, use the status text
    }
    
    throw new ApiError(errorMessage, response.status, errorData);
  }
  
  return response.json();
}

export const api = {
  // Health check
  async getHealth(): Promise<SystemHealth> {
    const response = await fetch(`${API_BASE_URL}/api/v1/health`);
    return handleResponse<SystemHealth>(response);
  },

  // Search endpoints
  async search(request: SearchRequest): Promise<SearchResult> {
    const response = await fetch(`${API_BASE_URL}/api/v1/search`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify(request),
    });
    return handleResponse<SearchResult>(response);
  },

  async searchSections(
    query: string,
    category?: string,
    bailable?: string,
    cognizable?: string,
    maxResults: number = 10,
    userType?: string
  ): Promise<SearchResult> {
    const params = new URLSearchParams({
      query,
      max_results: maxResults.toString(),
    });
    
    if (category) params.append('category', category);
    if (bailable) params.append('bailable', bailable);
    if (cognizable) params.append('cognizable', cognizable);
    if (userType) params.append('user_type', userType);

    const response = await fetch(`${API_BASE_URL}/api/v1/search/sections?${params}`);
    return handleResponse<SearchResult>(response);
  },

  async searchCases(
    query: string,
    court?: string,
    caseType?: string,
    verdict?: string,
    maxResults: number = 10,
    userType?: string
  ): Promise<SearchResult> {
    const params = new URLSearchParams({
      query,
      max_results: maxResults.toString(),
    });
    
    if (court) params.append('court', court);
    if (caseType) params.append('case_type', caseType);
    if (verdict) params.append('verdict', verdict);
    if (userType) params.append('user_type', userType);

    const response = await fetch(`${API_BASE_URL}/api/v1/search/cases?${params}`);
    return handleResponse<SearchResult>(response);
  },

  // Q&A endpoint
  async askQuestion(request: QARequest): Promise<QAResponse> {
    const response = await fetch(`${API_BASE_URL}/api/v1/qa`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify(request),
    });
    return handleResponse<QAResponse>(response);
  },

  // Get section details
  async getSection(sectionCode: string): Promise<LawSectionResponse> {
    const response = await fetch(`${API_BASE_URL}/api/v1/sections/${sectionCode}`);
    return handleResponse<LawSectionResponse>(response);
  },

  // Get search suggestions
  async getSuggestions(query: string, maxSuggestions: number = 5): Promise<{ query: string; suggestions: string[] }> {
    const params = new URLSearchParams({
      query,
      max_suggestions: maxSuggestions.toString(),
    });

    const response = await fetch(`${API_BASE_URL}/api/v1/suggestions?${params}`);
    return handleResponse<{ query: string; suggestions: string[] }>(response);
  },
};

export { ApiError };
