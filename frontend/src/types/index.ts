// TypeScript type definitions

export interface User {
  id: number
  username: string
  email?: string
  folder_path: string
}

export interface Document {
  id: number
  user_id: number
  title: string
  content: string
  markdown_source?: string
  version: number
  created_at: string
  updated_at: string
}

export interface ChatMessage {
  role: 'user' | 'assistant'
  content: string
}

export interface Citation {
  file_id: number
  file_name: string
  chunk_id: number
  text: string
  score: number
}

export interface TokenMetadata {
  input_tokens: number
  output_tokens: number
  total_tokens: number
  context_window_size: number
  usage_percent: number
}

export interface LatencyMetadata {
  retrieval_time_ms: number
  generation_time_ms: number
  total_time_ms: number
}

export interface AIResponse {
  response: string
  citations?: Citation[]
  request_id: string
  tokens: TokenMetadata
  latency: LatencyMetadata
  model_used: string
}

export interface UploadedFile {
  id: number
  filename: string
  file_type: string
  file_size: number
  upload_date: string
  indexed_at?: string
}

export interface ModelInfo {
  name: string
  size_gb: number
}

export interface HealthStatus {
  status: 'healthy' | 'degraded' | 'unhealthy'
  timestamp: string
  services: {
    ollama: {
      status: string
      models: number
      default_model: string
    }
    rag: {
      status: string
      total_vectors: number
      total_chunks: number
    }
  }
}
