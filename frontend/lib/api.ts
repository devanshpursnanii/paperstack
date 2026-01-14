// API Client for FastAPI backend

import type {
  CreateSessionResponse,
  BrainSearchResponse,
  BrainLoadResponse,
  ChatMessageResponse,
  SessionInfoResponse,
} from '@/types';

const API_BASE_URL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000';

export class APIError extends Error {
  constructor(public status: number, message: string) {
    super(message);
    this.name = 'APIError';
  }
}

async function fetchAPI<T>(endpoint: string, options?: RequestInit): Promise<T> {
  try {
    const response = await fetch(`${API_BASE_URL}${endpoint}`, {
      ...options,
      mode: 'cors',
      credentials: 'include',
      headers: {
        'Content-Type': 'application/json',
        'Accept': 'application/json',
        ...options?.headers,
      },
    });

    if (!response.ok) {
      const errorText = await response.text();
      // Only log non-404 errors (404s are expected during session recovery)
      if (response.status !== 404) {
        console.error(`API Error ${response.status}:`, errorText);
      }
      throw new APIError(response.status, `HTTP ${response.status}: ${response.statusText}`);
    }

    return await response.json();
  } catch (error) {
    // Only log non-404 errors
    if (error instanceof APIError && error.status !== 404) {
      console.error('API request failed:', error.message);
    } else if (!(error instanceof APIError)) {
      console.error('Network error:', error);
    }
    if (error instanceof APIError) throw error;
    throw new Error(`Network error: ${error instanceof Error ? error.message : 'Unknown error'}`);
  }
}

export const api = {
  // Create new session
  createSession: async (initialQuery: string): Promise<CreateSessionResponse> => {
    return fetchAPI<CreateSessionResponse>('/session/create', {
      method: 'POST',
      body: JSON.stringify({ initial_query: initialQuery }),
    });
  },

  // Search papers with Paper Brain
  searchPapers: async (sessionId: string, query: string, searchMode: 'title' | 'topic' = 'topic'): Promise<BrainSearchResponse> => {
    return fetchAPI<BrainSearchResponse>('/brain/search', {
      method: 'POST',
      body: JSON.stringify({ session_id: sessionId, query, search_mode: searchMode }),
    });
  },

  // Load selected papers
  loadPapers: async (sessionId: string, paperIds: string[]): Promise<BrainLoadResponse> => {
    return fetchAPI<BrainLoadResponse>('/brain/load', {
      method: 'POST',
      body: JSON.stringify({ session_id: sessionId, paper_ids: paperIds }),
    });
  },

  // Send message to Paper Chat
  sendMessage: async (sessionId: string, message: string): Promise<ChatMessageResponse> => {
    return fetchAPI<ChatMessageResponse>('/chat/message', {
      method: 'POST',
      body: JSON.stringify({ session_id: sessionId, message }),
    });
  },

  // Get session info and quota status
  getSessionInfo: async (sessionId: string): Promise<SessionInfoResponse> => {
    return fetchAPI<SessionInfoResponse>(`/session/${sessionId}/info`);
  },

  // Health check
  healthCheck: async (): Promise<{ status: string }> => {
    return fetchAPI<{ status: string }>('/health');
  },
};
