import { create } from 'zustand'
import type { Document, ChatMessage } from '@/types'

interface EditorState {
  currentDocument: Document | null
  documents: Document[]
  isLoading: boolean
  selectedText: string
  showAISidebar: boolean
  
  // Actions
  setCurrentDocument: (doc: Document | null) => void
  setDocuments: (docs: Document[]) => void
  setIsLoading: (loading: boolean) => void
  setSelectedText: (text: string) => void
  toggleAISidebar: () => void
  updateDocumentContent: (content: string) => void
}

export const useEditorStore = create<EditorState>((set) => ({
  currentDocument: null,
  documents: [],
  isLoading: false,
  selectedText: '',
  showAISidebar: true,
  
  setCurrentDocument: (doc) => set({ currentDocument: doc }),
  setDocuments: (docs) => set({ documents: docs }),
  setIsLoading: (loading) => set({ isLoading: loading }),
  setSelectedText: (text) => set({ selectedText: text }),
  toggleAISidebar: () => set((state) => ({ showAISidebar: !state.showAISidebar })),
  updateDocumentContent: (content) =>
    set((state) => {
      if (state.currentDocument) {
        return {
          currentDocument: { ...state.currentDocument, content },
        }
      }
      return {}
    }),
}))

interface ChatState {
  messages: ChatMessage[]
  isLoading: boolean
  
  // Actions
  addMessage: (message: ChatMessage) => void
  clearMessages: () => void
  setIsLoading: (loading: boolean) => void
}

export const useChatStore = create<ChatState>((set) => ({
  messages: [],
  isLoading: false,
  
  addMessage: (message) =>
    set((state) => ({
      messages: [...state.messages, message],
    })),
  clearMessages: () => set({ messages: [] }),
  setIsLoading: (loading) => set({ isLoading: loading }),
}))

interface UIState {
  selectedModel: string
  tokenUsagePercent: number
  
  // Actions
  setSelectedModel: (model: string) => void
  setTokenUsagePercent: (percent: number) => void
}

export const useUIStore = create<UIState>((set) => ({
  selectedModel: 'llama2',
  tokenUsagePercent: 0,
  
  setSelectedModel: (model) => set({ selectedModel: model }),
  setTokenUsagePercent: (percent) => set({ tokenUsagePercent: percent }),
}))
