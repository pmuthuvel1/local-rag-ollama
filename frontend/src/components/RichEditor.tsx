import React, { useRef, useEffect } from 'react'

interface RichEditorProps {
  content: string
  onChange: (content: string) => void
  isLoading?: boolean
  onSelectionChange?: (text: string) => void
}

export const RichEditor: React.FC<RichEditorProps> = ({
  content,
  onChange,
  isLoading = false,
  onSelectionChange,
}) => {
  const editorRef = useRef<HTMLDivElement>(null)

  useEffect(() => {
    if (editorRef.current && editorRef.current.innerText !== content) {
      editorRef.current.innerText = content
    }
  }, [content])

  const handleInput = () => {
    if (editorRef.current) {
      onChange(editorRef.current.innerText)
    }
  }

  const handleMouseUp = () => {
    const selection = window.getSelection()
    if (selection && selection.toString().length > 0) {
      onSelectionChange?.(selection.toString())
    }
  }

  return (
    <div className="flex-1 flex flex-col bg-white">
      <div className="flex items-center gap-2 px-4 py-2 border-b border-gray-200 bg-gray-50">
        <button className="p-1.5 hover:bg-gray-200 rounded text-sm font-semibold text-gray-600">
          B
        </button>
        <button className="p-1.5 hover:bg-gray-200 rounded text-sm italic text-gray-600">
          I
        </button>
        <button className="p-1.5 hover:bg-gray-200 rounded text-sm underline text-gray-600">
          U
        </button>
        <div className="h-6 w-px bg-gray-300 mx-1"></div>
        <button className="p-1.5 hover:bg-gray-200 rounded text-sm text-gray-600">
          🎨
        </button>
      </div>

      <div
        ref={editorRef}
        onInput={handleInput}
        onMouseUp={handleMouseUp}
        contentEditable={!isLoading}
        suppressContentEditableWarning
        className="flex-1 p-6 overflow-auto focus:outline-none text-gray-800 leading-relaxed whitespace-pre-wrap break-words"
        style={{ minHeight: '400px' }}
      >
        {content}
      </div>
    </div>
  )
}
