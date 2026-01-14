// Type definitions for PaperStack

export interface ThinkingStep {
  step: string;
  status: 'in_progress' | 'complete' | 'error' | 'pending';
  result: string | null;
}

export interface Paper {
  title: string;
  authors: string;
  abstract: string;
  arxiv_id: string;
  url: string;
  score: number;
}

export interface Citation {
  paper: string;
  page: number;
}

export interface Message {
  id: string;
  role: 'user' | 'assistant';
  content: string;
  citations?: Citation[];
  thinking_steps?: ThinkingStep[];
  timestamp: Date;
  isLoading?: boolean;
}

export interface QuotaStatus {
  brain: {
    allowed: boolean;
    searches_used: number;
    searches_remaining: number;
    cooldown_minutes: number;
  };
  chat: {
    allowed: boolean;
    messages_used: number;
    messages_remaining: number;
    cooldown_minutes: number;
  };
  api_exhausted: boolean;
}

export interface SessionInfo {
  session_id: string;
  created_at: string;
  last_activity: string;
  initial_query: string;
  loaded_papers: string[];
  quota_status: QuotaStatus;
  brain_searches_used: number;
  chat_messages_used: number;
}

// API Response types
export interface CreateSessionResponse {
  session_id: string;
  message: string;
  error?: string;
}

export interface BrainSearchResponse {
  thinking_steps: ThinkingStep[];
  papers: Paper[];
  searches_remaining: number;
  error?: string;
}

export interface BrainLoadResponse {
  thinking_steps: ThinkingStep[];
  loaded_papers: string[];
  status: string;
  error?: string;
}

export interface ChatMessageResponse {
  thinking_steps: ThinkingStep[];
  answer: string;
  citations: Citation[];
  messages_remaining: number;
  error?: string;
}

export interface SessionInfoResponse {
  session_info: SessionInfo;
  logs_summary: any;
  error?: string;
}
