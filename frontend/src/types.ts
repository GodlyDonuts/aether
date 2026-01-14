export interface Message {
  id: string;
  role: 'user' | 'assistant';
  content: string;
  timestamp: string;
}

export interface IntentAnalysis {
  bucket: string;
  struggle: string;
  propensity: number;
  entities: string[];
}

export interface NudgeDetails {
  product: string;
  vendor: string;
  relevance: string;
}

export interface ChatResponse {
  response: string;
  session_id: string;
  intent_analysis?: IntentAnalysis;
  nudge_injected: boolean;
  nudge_details?: NudgeDetails;
}
