import React from 'react'

interface HeaderProps {
  title?: string
  documentTitle?: string
}

export const Header: React.FC<HeaderProps> = ({ title = 'Loomin-Docs', documentTitle }) => {
  return (
    <header className="bg-white border-b border-gray-200 px-6 py-4 shadow-sm">
      <div className="flex items-center justify-between">
        <div className="flex items-center gap-4">
          <div className="w-8 h-8 bg-gradient-to-br from-google-blue to-google-red rounded-lg flex items-center justify-center text-white font-bold">
            L
          </div>
          <div>
            <h1 className="text-xl font-semibold text-gray-900">{title}</h1>
            {documentTitle && (
              <p className="text-sm text-gray-500">{documentTitle}</p>
            )}
          </div>
        </div>
        <div className="flex items-center gap-4">
          <button className="px-3 py-1.5 text-sm font-medium text-gray-700 hover:bg-gray-100 rounded">
            Sign Out
          </button>
        </div>
      </div>
    </header>
  )
}
