import React, { useState, useEffect } from 'react'
import { motion, AnimatePresence } from 'framer-motion'
import { 
  FolderIcon,
  DocumentIcon,
  PhotoIcon,
  FilmIcon,
  MusicIcon,
  DownloadIcon,
  TrashIcon,
  ShareIcon,
  EyeIcon
} from '@heroicons/react/24/outline'

import { useFileStore } from '../store/fileStore'
import { formatFileSize, formatDate, getFileIcon, isPreviewable } from '../utils/helpers'
import FilePreview from './FilePreview'
import toast from 'react-hot-toast'

const FileBrowser = () => {
  const [selectedFiles, setSelectedFiles] = useState([])
  const [viewMode, setViewMode] = useState('grid') // grid or list
  const [sortBy, setSortBy] = useState('name') // name, date, size
  const [sortOrder, setSortOrder] = useState('asc') // asc or desc
  const [previewFile, setPreviewFile] = useState(null)

  const { 
    files, 
    loading, 
    currentFolder,
    fetchFiles,
    deleteFile,
    downloadFile,
    navigateToFolder,
    navigateUp
  } = useFileStore()

  useEffect(() => {
    if (!files.length && !loading) {
      fetchFiles()
    }
  }, [])

  const handleFileClick = async (file) => {
    if (file.is_folder) {
      await navigateToFolder(file.id)
    } else if (isPreviewable(file.mime_type)) {
      // Show preview for previewable files
      setPreviewFile(file)
    } else {
      // Download non-previewable files
      await handleDownload(file)
    }
  }

  const handlePreviewNavigation = (direction) => {
    if (!previewFile) return
    
    const previewableFiles = files.filter(file => 
      !file.is_folder && isPreviewable(file.mime_type)
    )
    
    const currentIndex = previewableFiles.findIndex(f => f.id === previewFile.id)
    
    if (direction === 'prev' && currentIndex > 0) {
      setPreviewFile(previewableFiles[currentIndex - 1])
    } else if (direction === 'next' && currentIndex < previewableFiles.length - 1) {
      setPreviewFile(previewableFiles[currentIndex + 1])
    }
  }

  const handleDownload = async (file) => {
    try {
      await downloadFile(file.id, file.filename)
    } catch (error) {
      console.error('Download failed:', error)
    }
  }

  const handleDelete = async (file) => {
    if (window.confirm(`Are you sure you want to delete "${file.filename}"?`)) {
      try {
        await deleteFile(file.id, file.filename)
        setSelectedFiles(prev => prev.filter(id => id !== file.id))
      } catch (error) {
        console.error('Delete failed:', error)
      }
    }
  }

  const handleSelectFile = (fileId) => {
    setSelectedFiles(prev => {
      if (prev.includes(fileId)) {
        return prev.filter(id => id !== fileId)
      } else {
        return [...prev, fileId]
      }
    })
  }

  const getFileIconComponent = (file) => {
    if (file.is_folder) {
      return <FolderIcon className="h-8 w-8 text-blue-500" />
    }

    const mimeType = file.mime_type || ''
    
    if (mimeType.startsWith('image/')) {
      return <PhotoIcon className="h-8 w-8 text-green-500" />
    }
    if (mimeType.startsWith('video/')) {
      return <FilmIcon className="h-8 w-8 text-purple-500" />
    }
    if (mimeType.startsWith('audio/')) {
      return <MusicIcon className="h-8 w-8 text-pink-500" />
    }
    
    return <DocumentIcon className="h-8 w-8 text-gray-500" />
  }

  const sortedFiles = [...files].sort((a, b) => {
    let aValue, bValue

    switch (sortBy) {
      case 'name':
        aValue = a.filename.toLowerCase()
        bValue = b.filename.toLowerCase()
        break
      case 'date':
        aValue = new Date(a.created_at)
        bValue = new Date(b.created_at)
        break
      case 'size':
        aValue = a.file_size
        bValue = b.file_size
        break
      default:
        aValue = a.filename.toLowerCase()
        bValue = b.filename.toLowerCase()
    }

    if (sortOrder === 'desc') {
      return bValue > aValue ? 1 : -1
    } else {
      return aValue > bValue ? 1 : -1
    }
  })

  if (loading) {
    return (
      <div className="flex items-center justify-center h-64">
        <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-primary-500"></div>
      </div>
    )
  }

  return (
    <div className="bg-white dark:bg-dark-800 rounded-lg shadow-sm border border-gray-200 dark:border-gray-700">
      {/* Toolbar */}
      <div className="p-4 border-b border-gray-200 dark:border-gray-700">
        <div className="flex items-center justify-between">
          {/* Breadcrumb */}
          <div className="flex items-center space-x-2">
            <button
              onClick={() => fetchFiles(null)}
              className="text-primary-600 hover:text-primary-500 text-sm font-medium"
            >
              Home
            </button>
            {currentFolder && (
              <>
                <span className="text-gray-400">/</span>
                <span className="text-gray-600 dark:text-gray-400 text-sm">
                  Current Folder
                </span>
              </>
            )}
          </div>

          {/* View Controls */}
          <div className="flex items-center space-x-2">
            <select
              value={sortBy}
              onChange={(e) => setSortBy(e.target.value)}
              className="text-sm border border-gray-300 dark:border-gray-600 rounded-md px-2 py-1 bg-white dark:bg-gray-800 text-gray-700 dark:text-gray-300"
            >
              <option value="name">Sort by Name</option>
              <option value="date">Sort by Date</option>
              <option value="size">Sort by Size</option>
            </select>
            
            <button
              onClick={() => setSortOrder(sortOrder === 'asc' ? 'desc' : 'asc')}
              className="p-1 text-gray-500 hover:text-gray-700 dark:text-gray-400 dark:hover:text-gray-200"
              title={`Sort ${sortOrder === 'asc' ? 'Descending' : 'Ascending'}`}
            >
              {sortOrder === 'asc' ? '↑' : '↓'}
            </button>
          </div>
        </div>
      </div>

      {/* File List */}
      <div className="p-4">
        {sortedFiles.length === 0 ? (
          <div className="text-center py-12">
            <FolderIcon className="mx-auto h-12 w-12 text-gray-400" />
            <h3 className="mt-4 text-sm font-medium text-gray-900 dark:text-white">No files</h3>
            <p className="mt-1 text-sm text-gray-500 dark:text-gray-400">
              Upload some files to get started
            </p>
          </div>
        ) : (
          <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 xl:grid-cols-4 gap-4">
            <AnimatePresence>
              {sortedFiles.map((file) => (
                <motion.div
                  key={file.id}
                  initial={{ opacity: 0, scale: 0.9 }}
                  animate={{ opacity: 1, scale: 1 }}
                  exit={{ opacity: 0, scale: 0.9 }}
                  transition={{ duration: 0.2 }}
                  className={`relative p-4 border-2 rounded-lg transition-all duration-200 cursor-pointer hover:shadow-md ${
                    selectedFiles.includes(file.id)
                      ? 'border-primary-500 bg-primary-50 dark:bg-primary-900/20'
                      : 'border-gray-200 dark:border-gray-700 hover:border-gray-300 dark:hover:border-gray-600'
                  }`}
                  onClick={() => handleFileClick(file)}
                >
                  {/* Selection Checkbox */}
                  <div className="absolute top-2 right-2">
                    <input
                      type="checkbox"
                      checked={selectedFiles.includes(file.id)}
                      onChange={(e) => {
                        e.stopPropagation()
                        handleSelectFile(file.id)
                      }}
                      className="rounded border-gray-300 text-primary-600 focus:ring-primary-500"
                    />
                  </div>

                  {/* File Icon */}
                  <div className="flex flex-col items-center">
                    <div className="mb-3">
                      {getFileIconComponent(file)}
                    </div>
                    
                    {/* File Info */}
                    <div className="text-center w-full">
                      <h4 className="text-sm font-medium text-gray-900 dark:text-white mb-1 truncate">
                        {file.filename}
                      </h4>
                      <p className="text-xs text-gray-500 dark:text-gray-400 mb-2">
                        {file.is_folder ? 'Folder' : formatFileSize(file.file_size)}
                      </p>
                      <p className="text-xs text-gray-400">
                        {formatDate(file.created_at)}
                      </p>
                    </div>

                    {/* File Actions */}
                    <div className="flex items-center space-x-1 mt-3 opacity-0 group-hover:opacity-100 transition-opacity">
                      {!file.is_folder && (
                        <button
                          onClick={(e) => {
                            e.stopPropagation()
                            handleDownload(file)
                          }}
                          className="p-1 text-gray-500 hover:text-primary-600 transition-colors"
                          title="Download"
                        >
                          <DownloadIcon className="h-4 w-4" />
                        </button>
                      )}
                      
                      <button
                        onClick={(e) => {
                          e.stopPropagation()
                          // TODO: Implement share functionality
                          toast.info('Share functionality coming soon!')
                        }}
                        className="p-1 text-gray-500 hover:text-primary-600 transition-colors"
                        title="Share"
                      >
                        <ShareIcon className="h-4 w-4" />
                      </button>
                      
                      <button
                        onClick={(e) => {
                          e.stopPropagation()
                          handleDelete(file)
                        }}
                        className="p-1 text-gray-500 hover:text-red-600 transition-colors"
                        title="Delete"
                      >
                        <TrashIcon className="h-4 w-4" />
                      </button>
                    </div>
                  </div>
                </motion.div>
              ))}
            </AnimatePresence>
          </div>
        )}
      </div>

      {/* File Preview Modal */}
      <AnimatePresence>
        {previewFile && (
          <FilePreview
            file={previewFile}
            onClose={() => setPreviewFile(null)}
            onNavigate={handlePreviewNavigation}
          />
        )}
      </AnimatePresence>
    </div>
  )
}

export default FileBrowser