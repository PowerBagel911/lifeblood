export interface Citation {
  doc_id: string;
  title?: string;
  chunk_id?: string;
  snippet: string;
  score: number;
}

export interface Message {
  id: string;
  question: string;
  answer: string;
  citations: Citation[];
  mode: ResponseMode;
  timestamp: Date;
}

export type ResponseMode = 'general' | 'checklist' | 'plain_english';

export interface AskRequest {
  question: string;
  mode: ResponseMode;
  top_k: number;
}

export interface AskResponse {
  question: string;
  answer: string;
  citations: Citation[];
  mode: ResponseMode;
  trace_id: string;
}
