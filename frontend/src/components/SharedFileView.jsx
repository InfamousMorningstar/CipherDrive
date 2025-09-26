import React, { useState, useEffect } from 'react'
import { useParams, useNavigate } from 'react-router-dom'
import { motion } from 'framer-motion'
import { 
  CloudIcon,
  ArrowDownTrayIcon,
  EyeIcon,
  LockClosedIcon,
  ExclamationTriangleIcon
} from '@heroicons/react/24/outline'

import { formatFileSize, formatDate } from '../utils/helpers'
import api from '../utils/api'
import toast from 'react-hot-toast'

const SharedFileView = () => {
  const { shareToken } = useParams()
  const navigate = useNavigate()
  
  const [fileInfo, setFileInfo] = useState(null)
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState(null)
  const [password, setPassword] = useState('')
  const [showPasswordInput, setShowPasswordInput] = useState(false)
  const [downloading, setDownloading] = useState(false)

  useEffect(() => {
    if (shareToken) {
      fetchFileInfo()
    }
  }, [shareToken])

  const fetchFileInfo = async (passwordAttempt = '') => {
    setLoading(true)
    setError(null)
    
    try {
      const response = await api.get(`/shared/${shareToken}`, {
        params: passwordAttempt ? { password: passwordAttempt } : {}
      })
      
      setFileInfo(response.data)
      setShowPasswordInput(false)
    } catch (err) {
      if (err.response?.status === 401 && err.response?.data?.detail === 'Password required') {
        setShowPasswordInput(true)
        setError('This shared file is password protected')
      } else if (err.response?.status === 401 && err.response?.data?.detail === 'Invalid password') {
        setShowPasswordInput(true)
        setError('Invalid password. Please try again.')
      } else if (err.response?.status === 404) {
        setError('Shared file not found or has been removed')
      } else if (err.response?.status === 410) {
        setError('This shared link has expired or reached its download limit')
      } else {
        setError('Failed to load shared file information')
      }
    } finally {
      setLoading(false)
    }
  }

  const handlePasswordSubmit = (e) => {
    e.preventDefault()
    if (password.trim()) {
      fetchFileInfo(password.trim())
    }
  }

  const handleDownload = async () => {
    if (!fileInfo) return

    setDownloading(true)
    try {
      const response = await api.get(`/shared/${shareToken}/download`, {
        params: showPasswordInput && password ? { password: password } : {},
        responseType: 'blob'
      })

      // Create download link
      const url = window.URL.createObjectURL(new Blob([response.data]))
      const link = document.createElement('a')
      link.href = url
      link.setAttribute('download', fileInfo.filename)
      document.body.appendChild(link)
      link.click()
      link.remove()
      window.URL.revokeObjectURL(url)
      
      toast.success('File downloaded successfully')
    } catch (err) {
      const errorMessage = err.response?.data?.detail || 'Download failed'
      toast.error(errorMessage)
    } finally {
      setDownloading(false)
    }
  }

  if (loading) {
    return (
      <div className="min-h-screen bg-gray-50 dark:bg-dark-900 flex items-center justify-center">
        <div className="text-center">
          <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-primary-500 mx-auto mb-4"></div>
          <p className="text-gray-600 dark:text-gray-400">Loading shared file...</p>
        </div>
      </div>
    )
  }

  if (error && !showPasswordInput) {
    return (
      <div className="min-h-screen bg-gray-50 dark:bg-dark-900 flex items-center justify-center">
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          className="max-w-md w-full mx-4"
        >
          <div className="bg-white dark:bg-gray-800 rounded-lg shadow-lg p-6 text-center">
            <ExclamationTriangleIcon className="mx-auto h-12 w-12 text-red-500 mb-4" />
            <h2 className="text-xl font-semibold text-gray-900 dark:text-white mb-2">
              File Not Available
            </h2>
            <p className="text-gray-600 dark:text-gray-400 mb-6">
              {error}
            </p>
            <button
              onClick={() => navigate('/')}
              className="btn-primary"
            >
              Go Home
            </button>
          </div>
        </motion.div>
      </div>
    )
  }

  return (
    <div className="min-h-screen bg-gradient-to-br from-blue-50 to-indigo-100 dark:from-gray-900 dark:to-gray-800 flex items-center justify-center py-12 px-4">
      <motion.div
        initial={{ opacity: 0, y: 20 }}
        animate={{ opacity: 1, y: 0 }}
        className="max-w-md w-full"
      >
        <div className="bg-white dark:bg-gray-800 rounded-2xl shadow-2xl overflow-hidden">
          {/* Header */}
          <div className="bg-gradient-to-r from-blue-500 to-indigo-600 px-6 py-8">
            <div className="text-center">
              <div className="mx-auto h-16 w-16 bg-white/20 rounded-xl flex items-center justify-center mb-4">
                <CloudIcon className="h-8 w-8 text-white" />
              </div>
              <h1 className="text-xl font-bold text-white">
                Shared File
              </h1>
              <p className="text-blue-100 text-sm mt-1">
                Dropbox Lite
              </p>
            </div>
          </div>

          <div className="p-6">
            {showPasswordInput ? (
              /* Password Input */
              <motion.div
                initial={{ opacity: 0 }}
                animate={{ opacity: 1 }}
                className="space-y-4"
              >
                <div className="text-center mb-6">
                  <LockClosedIcon className="mx-auto h-12 w-12 text-gray-400 mb-2" />
                  <h3 className="text-lg font-medium text-gray-900 dark:text-white">
                    Password Required
                  </h3>
                  <p className="text-sm text-gray-600 dark:text-gray-400 mt-1">
                    This shared file is protected with a password
                  </p>
                  {error && (
                    <p className="text-sm text-red-600 dark:text-red-400 mt-2">
                      {error}
                    </p>
                  )}
                </div>

                <form onSubmit={handlePasswordSubmit} className="space-y-4">
                  <div>
                    <input
                      type="password"
                      value={password}
                      onChange={(e) => setPassword(e.target.value)}
                      placeholder="Enter password"
                      className="input-primary"
                      required
                    />
                  </div>

                  <button
                    type="submit"
                    className="w-full btn-primary"
                    disabled={!password.trim()}
                  >
                    Access File
                  </button>
                </form>
              </motion.div>
            ) : fileInfo ? (
              /* File Info */
              <motion.div
                initial={{ opacity: 0 }}
                animate={{ opacity: 1 }}
                className="space-y-6"
              >
                {/* File Details */}
                <div className="text-center">
                  <div className="mx-auto h-16 w-16 bg-gray-100 dark:bg-gray-700 rounded-xl flex items-center justify-center mb-4">
                    <span className="text-2xl">📄</span>
                  </div>
                  <h2 className="text-xl font-semibold text-gray-900 dark:text-white mb-2">
                    {fileInfo.filename}
                  </h2>
                  <div className="flex items-center justify-center space-x-4 text-sm text-gray-500 dark:text-gray-400">
                    <span>{formatFileSize(fileInfo.file_size)}</span>
                    <span>•</span>
                    <span>{formatDate(fileInfo.created_at)}</span>
                  </div>
                </div>

                {/* Actions */}
                <div className="space-y-3">
                  <button
                    onClick={handleDownload}
                    disabled={downloading}
                    className={`w-full btn-primary ${downloading ? 'opacity-75 cursor-not-allowed' : ''}`}
                  >
                    <ArrowDownTrayIcon className="h-5 w-5 mr-2" />
                    {downloading ? 'Downloading...' : 'Download File'}
                  </button>

                  <button
                    onClick={() => window.history.back()}
                    className="w-full btn-secondary"
                  >
                    Go Back
                  </button>
                </div>

                {/* Security Notice */}
                <div className="text-center text-xs text-gray-500 dark:text-gray-400 pt-4 border-t border-gray-200 dark:border-gray-700">
                  <p>
                    This file was shared securely via Dropbox Lite.
                    <br />
                    Only download files from trusted sources.
                  </p>
                </div>
              </motion.div>
            ) : null}
          </div>
        </div>
      </motion.div>
    </div>
  )
}

export default SharedFileView