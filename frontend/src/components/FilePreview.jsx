import React, { useState, useEffect } from 'react'
import { motion, AnimatePresence } from 'framer-motion'
import { 
  XMarkIcon, 
  ChevronLeftIcon, 
  ChevronRightIcon,
  MagnifyingGlassMinusIcon,
  MagnifyingGlassPlusIcon,
  ArrowsPointingOutIcon
} from '@heroicons/react/24/outline'

import api from '../utils/api'
import { isPreviewable } from '../utils/helpers'

const FilePreview = ({ file, onClose, onNavigate }) => {
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState(null)
  const [previewUrl, setPreviewUrl] = useState(null)
  const [zoom, setZoom] = useState(1)
  const [fullscreen, setFullscreen] = useState(false)

  useEffect(() => {
    if (file && isPreviewable(file.mime_type)) {
      loadPreview()
    } else {
      setError('File type not supported for preview')
      setLoading(false)
    }
  }, [file])

  const loadPreview = async () => {
    setLoading(true)
    setError(null)
    
    try {
      if (file.mime_type?.startsWith('image/')) {
        // For images, we can use the download endpoint
        const response = await api.get(`/files/${file.id}/download`, {
          responseType: 'blob'
        })
        
        const url = URL.createObjectURL(response.data)
        setPreviewUrl(url)
      } else if (file.mime_type === 'application/pdf') {
        // For PDFs, we'd need a PDF viewer
        // For now, we'll show a message
        setError('PDF preview requires additional setup')
      } else if (file.mime_type?.startsWith('text/')) {
        // For text files, we can fetch and display content
        const response = await api.get(`/files/${file.id}/download`, {
          responseType: 'text'
        })
        
        setPreviewUrl(response.data)
      } else {
        setError('Preview not available for this file type')
      }
    } catch (err) {
      setError('Failed to load preview')
    } finally {
      setLoading(false)
    }
  }

  const handleZoomIn = () => {
    setZoom(prev => Math.min(prev * 1.2, 5))
  }

  const handleZoomOut = () => {
    setZoom(prev => Math.max(prev / 1.2, 0.2))
  }

  const handleFullscreen = () => {
    if (!fullscreen && document.documentElement.requestFullscreen) {
      document.documentElement.requestFullscreen()
      setFullscreen(true)
    } else if (fullscreen && document.exitFullscreen) {
      document.exitFullscreen()
      setFullscreen(false)
    }
  }

  useEffect(() => {
    const handleFullscreenChange = () => {
      setFullscreen(!!document.fullscreenElement)
    }

    document.addEventListener('fullscreenchange', handleFullscreenChange)
    return () => {
      document.removeEventListener('fullscreenchange', handleFullscreenChange)
    }
  }, [])

  // Cleanup URL when component unmounts
  useEffect(() => {
    return () => {
      if (previewUrl && typeof previewUrl === 'string' && previewUrl.startsWith('blob:')) {
        URL.revokeObjectURL(previewUrl)
      }
    }
  }, [previewUrl])

  const renderPreview = () => {
    if (loading) {
      return (
        <div className="flex items-center justify-center h-full">
          <div className="text-center">
            <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-primary-500 mx-auto mb-4"></div>
            <p className="text-gray-600 dark:text-gray-400">Loading preview...</p>
          </div>
        </div>
      )
    }

    if (error) {
      return (
        <div className="flex items-center justify-center h-full">
          <div className="text-center">
            <div className="text-6xl mb-4">📄</div>
            <h3 className="text-lg font-medium text-gray-900 dark:text-white mb-2">
              Preview Not Available
            </h3>
            <p className="text-gray-600 dark:text-gray-400 mb-4">
              {error}
            </p>
            <button
              onClick={() => window.open(`/api/files/${file.id}/download`)}
              className="btn-primary"
            >
              Download File
            </button>
          </div>
        </div>
      )
    }

    if (file.mime_type?.startsWith('image/')) {
      return (
        <div className="flex items-center justify-center h-full overflow-auto">
          <img
            src={previewUrl}
            alt={file.filename}
            style={{ transform: `scale(${zoom})` }}
            className="max-w-none transition-transform duration-200 cursor-move"
            draggable={false}
          />
        </div>
      )
    }

    if (file.mime_type?.startsWith('text/')) {
      return (
        <div className="h-full overflow-auto p-6 bg-white dark:bg-gray-800">
          <pre 
            className="whitespace-pre-wrap text-sm text-gray-900 dark:text-gray-100 font-mono"
            style={{ fontSize: `${zoom}rem` }}
          >
            {previewUrl}
          </pre>
        </div>
      )
    }

    return (
      <div className="flex items-center justify-center h-full">
        <p className="text-gray-600 dark:text-gray-400">
          Preview not available for this file type
        </p>
      </div>
    )
  }

  return (
    <motion.div
      initial={{ opacity: 0 }}
      animate={{ opacity: 1 }}
      exit={{ opacity: 0 }}
      className={`fixed inset-0 bg-black bg-opacity-90 z-50 ${fullscreen ? 'z-[9999]' : ''}`}
    >
      {/* Header */}
      <div className="absolute top-0 left-0 right-0 z-10 bg-black bg-opacity-50 text-white">
        <div className="flex items-center justify-between p-4">
          <div className="flex items-center space-x-4">
            <h2 className="text-lg font-medium truncate max-w-md">
              {file?.filename}
            </h2>
            <div className="text-sm text-gray-300">
              {file?.mime_type}
            </div>
          </div>

          <div className="flex items-center space-x-2">
            {/* Navigation */}
            {onNavigate && (
              <>
                <button
                  onClick={() => onNavigate('prev')}
                  className="p-2 text-white hover:bg-white hover:bg-opacity-20 rounded-lg transition-colors"
                  title="Previous file"
                >
                  <ChevronLeftIcon className="h-6 w-6" />
                </button>
                <button
                  onClick={() => onNavigate('next')}
                  className="p-2 text-white hover:bg-white hover:bg-opacity-20 rounded-lg transition-colors"
                  title="Next file"
                >
                  <ChevronRightIcon className="h-6 w-6" />
                </button>
                <div className="w-px h-6 bg-gray-600 mx-2"></div>
              </>
            )}

            {/* Zoom Controls */}
            {file?.mime_type?.startsWith('image/') && (
              <>
                <button
                  onClick={handleZoomOut}
                  className="p-2 text-white hover:bg-white hover:bg-opacity-20 rounded-lg transition-colors"
                  title="Zoom out"
                >
                  <MagnifyingGlassMinusIcon className="h-5 w-5" />
                </button>
                <span className="text-sm text-gray-300 min-w-[3rem] text-center">
                  {Math.round(zoom * 100)}%
                </span>
                <button
                  onClick={handleZoomIn}
                  className="p-2 text-white hover:bg-white hover:bg-opacity-20 rounded-lg transition-colors"
                  title="Zoom in"
                >
                  <MagnifyingGlassPlusIcon className="h-5 w-5" />
                </button>
                <button
                  onClick={handleFullscreen}
                  className="p-2 text-white hover:bg-white hover:bg-opacity-20 rounded-lg transition-colors"
                  title="Toggle fullscreen"
                >
                  <ArrowsPointingOutIcon className="h-5 w-5" />
                </button>
                <div className="w-px h-6 bg-gray-600 mx-2"></div>
              </>
            )}

            {/* Close Button */}
            <button
              onClick={onClose}
              className="p-2 text-white hover:bg-white hover:bg-opacity-20 rounded-lg transition-colors"
              title="Close preview"
            >
              <XMarkIcon className="h-6 w-6" />
            </button>
          </div>
        </div>
      </div>

      {/* Preview Content */}
      <div className="pt-16 h-full">
        {renderPreview()}
      </div>

      {/* Keyboard Shortcuts Info */}
      <div className="absolute bottom-4 left-4 text-white text-xs bg-black bg-opacity-50 rounded-lg px-3 py-2">
        <div className="space-y-1">
          <div>ESC: Close</div>
          {file?.mime_type?.startsWith('image/') && (
            <>
              <div>+/-: Zoom</div>
              <div>F: Fullscreen</div>
            </>
          )}
          {onNavigate && (
            <div>←/→: Navigate</div>
          )}
        </div>
      </div>
    </motion.div>
  )
}

export default FilePreview