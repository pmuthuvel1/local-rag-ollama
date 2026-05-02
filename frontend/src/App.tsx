import React, { useState, useEffect } from 'react'
import { Header } from '@/components/Header'
import { DocumentGrid } from '@/components/DocumentGrid'
import { RichEditor } from '@/components/RichEditor'
import { AISidebar } from '@/components/AISidebar'
import { useEditorStore, useChatStore, useUIStore } from '@/store'
import api from '@/services/api'
import type { Document } from '@/types'
import '@/index.css'

export const App: React.FC = () => {
  const [view, setView] = useState<'grid' | 'editor'>('grid')
  const [documents, setDocuments] = useState<Document[]>([])
  const [currentDocument, setCurrentDocument] = useState<Document | null>(null)
  const [selectedText, setSelectedText] = useState('')
  const [isLoading, setIsLoading] = useState(false)
  const [showAssetManager, setShowAssetManager] = useState(false)

  useEffect(() => {
    loadDocuments()
  }, [])

  const loadDocuments = async () => {
    try {
      setIsLoading(true)
      const response = await api.getDocuments()
      setDocuments(response.documents)
    } catch (error) {
      console.error('Failed to load documents:', error)
    } finally {
      setIsLoading(false)
    }
  }

  const handleSelectDocument = async (doc: Document) => {
    try {
      setIsLoading(true)
      const fullDoc = await api.getDocument(doc.id)
      setCurrentDocument(fullDoc)
      setView('editor')
    } catch (error) {
      console.error('Failed to load document:', error)
    } finally {
      setIsLoading(false)
    }
  }

  const handleCreateDocument = async () => {
    try {
      setIsLoading(true)
      const newDoc = await api.createDocument('Untitled Document', '')
      setCurrentDocument(newDoc as Document)
      setView('editor')
      setDocuments((prev) => [...prev, newDoc as Document])
    } catch (error) {
      console.error('Failed to create document:', error)
    } finally {
      setIsLoading(false)
    }
  }

  const handleSaveDocument = async (content: string) => {
    if (!currentDocument) return

    try {
      const updated = await api.updateDocument(currentDocument.id, currentDocument.title, content)
      setCurrentDocument(updated as Document)
      setDocuments((prev) =>
        prev.map((d) => (d.id === updated.id ? (updated as Document) : d))
      )
    } catch (error) {
      console.error('Failed to save document:', error)
    }
  }

  const handleBackToGrid = () => {
    setView('grid')
    setSelectedText('')
  }

  return (
    <div className="h-screen flex flex-col bg-white">
      <Header
        title="Loomin-Docs"
        documentTitle={view === 'editor' ? currentDocument?.title : undefined}
      />

      {view === 'grid' ? (
        <DocumentGrid
          documents={documents}
          onSelect={handleSelectDocument}
          onCreate={handleCreateDocument}
          isLoading={isLoading}
        />
      ) : (
        <div className="flex-1 flex overflow-hidden">
          {/* Back Button & Controls */}
          <div className="w-full flex flex-col">
            <div className="px-4 py-2 border-b border-gray-200 flex items-center gap-2">
              <button
                onClick={handleBackToGrid}
                className="px-3 py-1 text-sm font-medium text-gray-700 hover:bg-gray-100 rounded"
              >
                ← Back
              </button>
              <div className="flex-1" />
              <button
                onClick={() => setShowAssetManager(!showAssetManager)}
                className="px-3 py-1 text-sm font-medium text-gray-700 hover:bg-gray-100 rounded"
              >
                📁 Assets
              </button>
              <button
                onClick={() => handleSaveDocument(currentDocument?.content || '')}
                className="px-3 py-1 text-sm font-medium bg-google-blue text-white rounded hover:bg-blue-500"
              >
                Save
              </button>
            </div>

            {/* Main Editor Area */}
            <div className="flex-1 flex overflow-hidden">
              <RichEditor
                content={currentDocument?.content || ''}
                onChange={(content) => setCurrentDocument((doc) => 
                  doc ? { ...doc, content } : null
                )}
                isLoading={isLoading}
                onSelectionChange={setSelectedText}
              />

              {/* AI Sidebar */}
              <AISidebar
                selectedText={selectedText}
                documentId={currentDocument?.id}
                onTextInsert={(text) => {
                  if (currentDocument) {
                    handleSaveDocument(currentDocument.content + '\n' + text)
                  }
                }}
                isOpen={true}
              />
            </div>
          </div>
        </div>
      )}
    </div>
  )
}

export default App
