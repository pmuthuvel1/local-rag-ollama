import axios, { AxiosInstance } from 'axios'
import type { Document, AIResponse, UploadedFile, ModelInfo, HealthStatus } from '@/types'

class APIService {
  private api: AxiosInstance
  private userId: number = 1 // Default user for MVP

  constructor(baseURL = '/api') {
    this.api = axios.create({
      baseURL,
      headers: {
        'Content-Type': 'application/json',
      },
    })
  }

  setUserId(userId: number) {
    this.userId = userId
  }

  // Health & Status
  async getHealth(): Promise<HealthStatus> {
    const response = await this.api.get('/health')
    return response.data
  }

  // Documents
  async getDocuments(skip = 0, limit = 100) {
    const response = await this.api.get('/documents', {
      params: { user_id: this.userId, skip, limit },
    })
    return response.data
  }

  async createDocument(title: string, content: string): Promise<Document> {
    const response = await this.api.post('/documents', null, {
      params: { user_id: this.userId },
      data: { title, content, markdown_source: content },
    })
    return response.data
  }

  async getDocument(docId: number): Promise<Document> {
    const response = await this.api.get(`/documents/${docId}`, {
      params: { user_id: this.userId },
    })
    return response.data
  }

  async updateDocument(docId: number, title?: string, content?: string): Promise<Document> {
    const response = await this.api.put(`/documents/${docId}`, null, {
      params: { user_id: this.userId },
      data: { title, content, markdown_source: content },
    })
    return response.data
  }

  async deleteDocument(docId: number) {
    const response = await this.api.delete(`/documents/${docId}`, {
      params: { user_id: this.userId },
    })
    return response.data
  }

  // AI Endpoints
  async getModels(): Promise<ModelInfo[]> {
    const response = await this.api.get('/ai/models')
    return response.data.models
  }

  async summarize(text: string, docId?: number, maxLength = 150): Promise<AIResponse> {
    const response = await this.api.post('/ai/summarize', null, {
      params: { user_id: this.userId },
      data: { text, document_id: docId, max_length: maxLength },
    })
    return response.data
  }

  async improve(text: string, type = 'enhance', docId?: number): Promise<AIResponse> {
    const response = await this.api.post('/ai/improve', null, {
      params: { user_id: this.userId },
      data: { text, improvement_type: type, document_id: docId },
    })
    return response.data
  }

  async chat(message: string, docId?: number, history = [], useRAG = true): Promise<AIResponse> {
    const response = await this.api.post('/ai/chat', null, {
      params: { user_id: this.userId },
      data: { message, document_id: docId, conversation_history: history, use_rag: useRAG },
    })
    return response.data
  }

  // RAG Endpoints
  async retrieve(query: string, topK = 5) {
    const response = await this.api.post('/rag/retrieve', {
      query,
      top_k: topK,
      max_context_tokens: 2000,
    })
    return response.data
  }

  async getRAGStats() {
    const response = await this.api.get('/rag/index-stats')
    return response.data
  }

  // File Management
  async uploadFile(file: File): Promise<UploadedFile> {
    const formData = new FormData()
    formData.append('file', file)
    const response = await this.api.post('/files/upload', formData, {
      params: { user_id: this.userId },
      headers: { 'Content-Type': 'multipart/form-data' },
    })
    return response.data
  }

  async getFiles(): Promise<UploadedFile[]> {
    const response = await this.api.get('/files', {
      params: { user_id: this.userId },
    })
    return response.data.files
  }

  async deleteFile(fileId: number) {
    const response = await this.api.delete(`/files/${fileId}`, {
      params: { user_id: this.userId },
    })
    return response.data
  }
}

export default new APIService()
