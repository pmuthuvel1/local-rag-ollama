import React, { useState, useRef, useEffect } from 'react'
import type { ChatMessage, AIResponse } from '@/types'
import api from '@/services/api'

interface AISidebarProps {
  selectedText: string
  documentId?: number
  onTextInsert?: (text: string) => void
  isOpen?: boolean
}

export const AISidebar: React.FC<AISidebarProps> = ({
  selectedText,
  documentId,
  onTextInsert,
  isOpen = true,
}) => {
  const [messages, setMessages] = useState<ChatMessage[]>([])
  const [input, setInput] = useState('')
  const [isLoading, setIsLoading] = useState(false)
  const [selectedModel, setSelectedModel] = useState('llama2')
  const [models, setModels] = useState<string[]>([])
  const [tokenUsage, setTokenUsage] = useState(0)
  const messagesEndRef = useRef<HTMLDivElement>(null)

  useEffect(() => {
    scrollToBottom()
  }, [messages])

  useEffect(() => {
    loadModels()
  }, [])

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' })
  }

  const loadModels = async () => {
    try {
      const modelList = await api.getModels()
      setModels(modelList.map((m) => m.name))
    } catch (error) {
      console.error('Failed to load models:', error)
    }
  }

  const handleSendMessage = async () => {
    if (!input.trim()) return

    const userMessage = input
    setInput('')
    setMessages((prev) => [...prev, { role: 'user', content: userMessage }])
    setIsLoading(true)

    try {
      const response: AIResponse = await api.chat(
        userMessage,
        documentId,
        messages,
        true,
      )

      setMessages((prev) => [
        ...prev,
        { role: 'assistant', content: response.response },
      ])
      setTokenUsage(response.tokens.usage_percent)

      if (response.citations && response.citations.length > 0) {
        const citationText = response.citations
          .map((c) => `📌 ${c.file_name}: ${c.text.substring(0, 50)}...`)
          .join('\n')
        console.log('Citations:', citationText)
      }
    } catch (error) {
      console.error('Chat error:', error)
      setMessages((prev) => [
        ...prev,
        {
          role: 'assistant',
          content: 'Sorry, I encountered an error processing your request.',
        },
      ])
    } finally {
      setIsLoading(false)
    }
  }

  const handleSummarize = async () => {
    if (!selectedText) return
    setIsLoading(true)

    try {
      const response: AIResponse = await api.summarize(selectedText, documentId)
      const summary = response.response

      setMessages((prev) => [
        ...prev,
        { role: 'user', content: `Summarize: ${selectedText.substring(0, 50)}...` },
        { role: 'assistant', content: summary },
      ])

      onTextInsert?.(summary)
      setTokenUsage(response.tokens.usage_percent)
    } catch (error) {
      console.error('Summarize error:', error)
    } finally {
      setIsLoading(false)
    }
  }

  const handleImprove = async () => {
    if (!selectedText) return
    setIsLoading(true)

    try {
      const response: AIResponse = await api.improve(selectedText, 'enhance', documentId)
      const improved = response.response

      setMessages((prev) => [
        ...prev,
        { role: 'user', content: `Improve: ${selectedText.substring(0, 50)}...` },
        { role: 'assistant', content: improved },
      ])

      onTextInsert?.(improved)
      setTokenUsage(response.tokens.usage_percent)
    } catch (error) {
      console.error('Improve error:', error)
    } finally {
      setIsLoading(false)
    }
  }

  if (!isOpen) return null

  return (
    <div className="w-80 bg-white border-l border-gray-200 flex flex-col">
      {/* Header */}
      <div className="p-4 border-b border-gray-200">
        <h3 className="font-semibold text-gray-900 mb-3">AI Assistant</h3>
        
        <div className="flex flex-col gap-2">
          <select
            value={selectedModel}
            onChange={(e) => setSelectedModel(e.target.value)}
            className="text-sm px-2 py-1.5 border border-gray-300 rounded bg-white"
          >
            {models.map((model) => (
              <option key={model} value={model}>
                {model}
              </option>
            ))}
          </select>

          {/* Token Visualization */}
          <div>
            <div className="text-xs text-gray-500 mb-1">Context Usage</div>
            <div className="w-full bg-gray-200 rounded-full h-2">
              <div
                className="bg-google-blue h-2 rounded-full transition-all"
                style={{ width: `${Math.min(tokenUsage, 100)}%` }}
              ></div>
            </div>
            <div className="text-xs text-gray-600 mt-0.5">{tokenUsage.toFixed(1)}%</div>
          </div>
        </div>

        {/* Action Buttons */}
        <div className="flex gap-2 mt-3">
          <button
            onClick={handleSummarize}
            disabled={!selectedText || isLoading}
            className="flex-1 px-2 py-1 text-xs bg-google-blue text-white rounded hover:bg-blue-500 disabled:opacity-50 font-medium"
          >
            📝 Summarize
          </button>
          <button
            onClick={handleImprove}
            disabled={!selectedText || isLoading}
            className="flex-1 px-2 py-1 text-xs bg-google-green text-white rounded hover:bg-green-500 disabled:opacity-50 font-medium"
          >
            ✨ Improve
          </button>
        </div>
      </div>

      {/* Chat Messages */}
      <div className="flex-1 overflow-y-auto p-4 space-y-3">
        {messages.length === 0 && (
          <div className="text-center text-gray-500 text-sm py-8">
            Start a conversation or select text to improve it
          </div>
        )}
        {messages.map((msg, idx) => (
          <div
            key={idx}
            className={`flex ${msg.role === 'user' ? 'justify-end' : 'justify-start'}`}
          >
            <div
              className={`max-w-xs px-3 py-2 rounded-lg text-sm ${
                msg.role === 'user'
                  ? 'bg-google-blue text-white'
                  : 'bg-gray-100 text-gray-900'
              }`}
            >
              {msg.content}
            </div>
          </div>
        ))}
        {isLoading && (
          <div className="flex justify-start">
            <div className="bg-gray-100 px-3 py-2 rounded-lg">
              <div className="flex gap-1">
                <div className="w-2 h-2 bg-gray-400 rounded-full animate-bounce"></div>
                <div className="w-2 h-2 bg-gray-400 rounded-full animate-bounce delay-100"></div>
                <div className="w-2 h-2 bg-gray-400 rounded-full animate-bounce delay-200"></div>
              </div>
            </div>
          </div>
        )}
        <div ref={messagesEndRef} />
      </div>

      {/* Input */}
      <div className="p-4 border-t border-gray-200">
        <div className="flex gap-2">
          <input
            type="text"
            value={input}
            onChange={(e) => setInput(e.target.value)}
            onKeyPress={(e) => e.key === 'Enter' && handleSendMessage()}
            placeholder="Ask me anything..."
            disabled={isLoading}
            className="flex-1 px-3 py-2 border border-gray-300 rounded text-sm focus:outline-none focus:border-google-blue disabled:bg-gray-50"
          />
          <button
            onClick={handleSendMessage}
            disabled={isLoading || !input.trim()}
            className="px-3 py-2 bg-google-blue text-white rounded hover:bg-blue-500 disabled:opacity-50 font-medium text-sm"
          >
            Send
          </button>
        </div>
      </div>
    </div>
  )
}
