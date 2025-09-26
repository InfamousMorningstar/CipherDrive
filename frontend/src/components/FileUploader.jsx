import React, { useState, useCallback } from 'react'
import { motion } from 'framer-motion'
import { useDropzone } from 'react-dropzone'
import { 
  XMarkIcon,
  CloudArrowUpIcon,
  DocumentIcon,
  CheckCircleIcon,
  XCircleIcon
} from '@heroicons/react/24/outline'

import { useFileStore } from '../store/fileStore'
import { formatFileSize } from '../utils/helpers'
import toast from 'react-hot-toast'

const FileUploader = ({ onClose }) => {
  const [uploadQueue, setUploadQueue] = useState([])
  const [isUploading, setIsUploading] = useState(false)
  
  const { uploadFile, currentFolder } = useFileStore()

  const onDrop = useCallback((acceptedFiles) => {
    const newFiles = acceptedFiles.map(file => ({
      id: Math.random().toString(36).substr(2, 9),
      file,
      status: 'pending', // pending, uploading, success, error
      progress: 0,
      error: null
    }))
    
    setUploadQueue(prev => [...prev, ...newFiles])
  }, [])

  const { getRootProps, getInputProps, isDragActive } = useDropzone({
    onDrop,
    multiple: true,
    maxSize: 100 * 1024 * 1024, // 100MB limit
  })

  const removeFile = (fileId) => {
    setUploadQueue(prev => prev.filter(item => item.id !== fileId))
  }

  const uploadAll = async () => {
    const pendingFiles = uploadQueue.filter(item => item.status === 'pending')
    
    if (pendingFiles.length === 0) {
      toast.error('No files to upload')
      return
    }

    setIsUploading(true)

    for (const fileItem of pendingFiles) {
      try {
        // Update status to uploading
        setUploadQueue(prev => 
          prev.map(item => 
            item.id === fileItem.id 
              ? { ...item, status: 'uploading', progress: 0 }
              : item
          )
        )

        // Upload file with progress tracking
        await uploadFile(
          fileItem.file,
          currentFolder,
          (progress) => {
            setUploadQueue(prev => 
              prev.map(item => 
                item.id === fileItem.id 
                  ? { ...item, progress }
                  : item
              )
            )
          }
        )

        // Mark as success
        setUploadQueue(prev => 
          prev.map(item => 
            item.id === fileItem.id 
              ? { ...item, status: 'success', progress: 100 }
              : item
          )
        )

      } catch (error) {
        // Mark as error
        setUploadQueue(prev => 
          prev.map(item => 
            item.id === fileItem.id 
              ? { ...item, status: 'error', error: error.message }
              : item
          )
        )
      }
    }

    setIsUploading(false)
    
    // Show completion message
    const successCount = uploadQueue.filter(item => item.status === 'success').length
    if (successCount > 0) {
      setTimeout(() => {
        onClose()
      }, 2000)
    }
  }

  const getStatusIcon = (status) => {
    switch (status) {
      case 'success':
        return <CheckCircleIcon className="h-5 w-5 text-green-500" />
      case 'error':
        return <XCircleIcon className="h-5 w-5 text-red-500" />
      case 'uploading':
        return (
          <div className="animate-spin rounded-full h-5 w-5 border-b-2 border-primary-500"></div>
        )
      default:
        return <DocumentIcon className="h-5 w-5 text-gray-400" />
    }
  }

  return (
    <motion.div
      initial={{ opacity: 0 }}
      animate={{ opacity: 1 }}
      exit={{ opacity: 0 }}
      className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center p-4 z-50"
      onClick={onClose}
    >
      <motion.div
        initial={{ scale: 0.9, opacity: 0 }}
        animate={{ scale: 1, opacity: 1 }}
        exit={{ scale: 0.9, opacity: 0 }}
        onClick={(e) => e.stopPropagation()}
        className="bg-white dark:bg-dark-800 rounded-xl shadow-2xl w-full max-w-2xl max-h-[80vh] flex flex-col"
      >
        {/* Header */}
        <div className="flex items-center justify-between p-6 border-b border-gray-200 dark:border-gray-700">
          <h2 className="text-xl font-semibold text-gray-900 dark:text-white">
            Upload Files
          </h2>
          <button
            onClick={onClose}
            className="p-2 text-gray-400 hover:text-gray-600 dark:hover:text-gray-300 transition-colors"
          >
            <XMarkIcon className="h-6 w-6" />
          </button>
        </div>

        {/* Upload Area */}
        <div className="p-6">
          <div
            {...getRootProps()}
            className={`border-2 border-dashed rounded-lg p-8 text-center transition-colors cursor-pointer ${
              isDragActive
                ? 'border-primary-500 bg-primary-50 dark:bg-primary-900/20'
                : 'border-gray-300 dark:border-gray-600 hover:border-primary-400 dark:hover:border-primary-500'
            }`}
          >
            <input {...getInputProps()} />
            
            <CloudArrowUpIcon className="mx-auto h-12 w-12 text-gray-400 mb-4" />
            
            {isDragActive ? (
              <p className="text-primary-600 dark:text-primary-400 font-medium">
                Drop files here...
              </p>
            ) : (
              <>
                <p className="text-gray-600 dark:text-gray-300 font-medium mb-2">
                  Drag & drop files here, or click to select
                </p>
                <p className="text-sm text-gray-500 dark:text-gray-400">
                  Maximum file size: 100MB
                </p>
              </>
            )}
          </div>
        </div>

        {/* Upload Queue */}
        {uploadQueue.length > 0 && (
          <div className="flex-1 min-h-0 border-t border-gray-200 dark:border-gray-700">
            <div className="p-4">
              <h3 className="text-sm font-medium text-gray-900 dark:text-white mb-3">
                Upload Queue ({uploadQueue.length})
              </h3>
              
              <div className="space-y-3 max-h-64 overflow-y-auto">
                {uploadQueue.map((fileItem) => (
                  <div
                    key={fileItem.id}
                    className="flex items-center space-x-3 p-3 bg-gray-50 dark:bg-gray-700 rounded-lg"
                  >
                    {getStatusIcon(fileItem.status)}
                    
                    <div className="flex-1 min-w-0">
                      <p className="text-sm font-medium text-gray-900 dark:text-white truncate">
                        {fileItem.file.name}
                      </p>
                      <p className="text-xs text-gray-500 dark:text-gray-400">
                        {formatFileSize(fileItem.file.size)}
                      </p>
                      
                      {fileItem.status === 'uploading' && (
                        <div className="mt-2">
                          <div className="bg-gray-200 dark:bg-gray-600 rounded-full h-2">
                            <div
                              className="bg-primary-500 h-2 rounded-full transition-all duration-300"
                              style={{ width: `${fileItem.progress}%` }}
                            />
                          </div>
                          <p className="text-xs text-gray-500 dark:text-gray-400 mt-1">
                            {fileItem.progress}%
                          </p>
                        </div>
                      )}
                      
                      {fileItem.status === 'error' && fileItem.error && (
                        <p className="text-xs text-red-500 mt-1">
                          {fileItem.error}
                        </p>
                      )}
                    </div>

                    {fileItem.status === 'pending' && (
                      <button
                        onClick={() => removeFile(fileItem.id)}
                        className="p-1 text-gray-400 hover:text-red-500 transition-colors"
                      >
                        <XMarkIcon className="h-4 w-4" />
                      </button>
                    )}
                  </div>
                ))}
              </div>
            </div>
          </div>
        )}

        {/* Footer */}
        <div className="flex items-center justify-between p-6 border-t border-gray-200 dark:border-gray-700">
          <div className="text-sm text-gray-500 dark:text-gray-400">
            {uploadQueue.length > 0 && (
              <>
                {uploadQueue.filter(f => f.status === 'success').length} of {uploadQueue.length} uploaded
              </>
            )}
          </div>
          
          <div className="flex space-x-3">
            <button
              onClick={onClose}
              disabled={isUploading}
              className="btn-secondary"
            >
              {uploadQueue.some(f => f.status === 'success') ? 'Done' : 'Cancel'}
            </button>
            
            {uploadQueue.length > 0 && (
              <button
                onClick={uploadAll}
                disabled={isUploading || uploadQueue.filter(f => f.status === 'pending').length === 0}
                className="btn-primary"
              >
                {isUploading ? 'Uploading...' : 'Upload All'}
              </button>
            )}
          </div>
        </div>
      </motion.div>
    </motion.div>
  )
}

export default FileUploader