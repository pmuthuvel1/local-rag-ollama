import React, { useState } from 'react'
import type { Document } from '@/types'

interface DocumentGridProps {
  documents: Document[]
  onSelect: (doc: Document) => void
  onCreate: () => void
  isLoading: boolean
}

export const DocumentGrid: React.FC<DocumentGridProps> = ({ 
  documents, 
  onSelect, 
  onCreate, 
  isLoading 
}) => {
  const [hoveredId, setHoveredId] = useState<number | null>(null)

  return (
    <div className="p-8">
      <div className="mb-8 flex items-center justify-between">
        <h2 className="text-3xl font-bold text-gray-900">My Documents</h2>
        <button
          onClick={onCreate}
          disabled={isLoading}
          className="px-4 py-2 bg-google-blue text-white rounded-lg hover:bg-blue-500 disabled:opacity-50 font-medium"
        >
          + New Document
        </button>
      </div>

      {documents.length === 0 ? (
        <div className="text-center py-16">
          <div className="text-gray-400 text-6xl mb-4">📄</div>
          <p className="text-gray-500 text-lg">No documents yet. Create one to get started!</p>
        </div>
      ) : (
        <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 xl:grid-cols-4 gap-6">
          {documents.map((doc) => (
            <div
              key={doc.id}
              onMouseEnter={() => setHoveredId(doc.id)}
              onMouseLeave={() => setHoveredId(null)}
              onClick={() => onSelect(doc)}
              className={`
                p-4 rounded-lg border-2 border-gray-200 cursor-pointer transition-all
                hover:border-google-blue hover:shadow-lg
                ${hoveredId === doc.id ? 'bg-blue-50' : 'bg-white'}
              `}
            >
              <h3 className="font-semibold text-gray-900 truncate mb-2">{doc.title}</h3>
              <p className="text-sm text-gray-500 line-clamp-2 mb-3">
                {doc.content.substring(0, 100)}...
              </p>
              <div className="flex items-center justify-between text-xs text-gray-400">
                <span>v{doc.version}</span>
                <span>{new Date(doc.updated_at).toLocaleDateString()}</span>
              </div>
            </div>
          ))}
        </div>
      )}
    </div>
  )
}
