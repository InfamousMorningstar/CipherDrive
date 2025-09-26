import React, { useState, useEffect } from 'react'
import { motion, AnimatePresence } from 'framer-motion'
import { 
  CloudIcon, 
  UserIcon, 
  MoonIcon,
  SunIcon,
  ArrowRightOnRectangleIcon,
  PlusIcon
} from '@heroicons/react/24/outline'

import { useAuthStore } from '../store/authStore'
import { useThemeStore } from '../store/themeStore'
import { useFileStore } from '../store/fileStore'
import FileBrowser from './FileBrowser'
import FileUploader from './FileUploader'
import UserProfile from './UserProfile'
import { formatFileSize, calculateUsagePercentage, getStorageColor } from '../utils/helpers'

const Dashboard = () => {
  const [activeTab, setActiveTab] = useState('files')
  const [showUploader, setShowUploader] = useState(false)
  const [showProfile, setShowProfile] = useState(false)

  const { user, logout } = useAuthStore()
  const { isDark, toggleTheme } = useThemeStore()
  const { fetchFiles, files, loading } = useFileStore()

  useEffect(() => {
    // Fetch files on component mount
    fetchFiles()
  }, [fetchFiles])

  const handleLogout = () => {
    logout()
  }

  const usagePercentage = calculateUsagePercentage(
    user?.used_storage_bytes || 0, 
    (user?.quota_gb || 5) * 1024 * 1024 * 1024
  )

  return (
    <div className="min-h-screen bg-gray-50 dark:bg-dark-900">
      {/* Header */}
      <motion.header
        initial={{ y: -50 }}
        animate={{ y: 0 }}
        className="bg-white dark:bg-dark-800 shadow-sm border-b border-gray-200 dark:border-gray-700"
      >
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="flex justify-between items-center h-16">
            {/* Logo */}
            <div className="flex items-center">
              <div className="h-8 w-8 bg-gradient-to-r from-blue-500 to-indigo-600 rounded-lg flex items-center justify-center mr-3">
                <CloudIcon className="h-5 w-5 text-white" />
              </div>
              <h1 className="text-xl font-bold text-gray-900 dark:text-white">
                Dropbox Lite
              </h1>
            </div>

            {/* Navigation */}
            <nav className="hidden md:flex space-x-8">
              <button
                onClick={() => setActiveTab('files')}
                className={`px-3 py-2 rounded-md text-sm font-medium transition-colors ${
                  activeTab === 'files'
                    ? 'text-primary-600 dark:text-primary-400 bg-primary-50 dark:bg-primary-900/20'
                    : 'text-gray-700 dark:text-gray-300 hover:text-primary-600 dark:hover:text-primary-400'
                }`}
              >
                Files
              </button>
              {user?.is_admin && (
                <button
                  onClick={() => setActiveTab('admin')}
                  className={`px-3 py-2 rounded-md text-sm font-medium transition-colors ${
                    activeTab === 'admin'
                      ? 'text-primary-600 dark:text-primary-400 bg-primary-50 dark:bg-primary-900/20'
                      : 'text-gray-700 dark:text-gray-300 hover:text-primary-600 dark:hover:text-primary-400'
                  }`}
                >
                  Admin
                </button>
              )}
            </nav>

            {/* User Actions */}
            <div className="flex items-center space-x-4">
              {/* Storage Info */}
              <div className="hidden sm:block text-right">
                <div className={`text-sm font-medium ${getStorageColor(usagePercentage)}`}>
                  {formatFileSize(user?.used_storage_bytes || 0)} / {user?.quota_gb || 5} GB
                </div>
                <div className="w-24 bg-gray-200 dark:bg-gray-700 rounded-full h-2 mt-1">
                  <div 
                    className={`h-2 rounded-full transition-all duration-300 ${
                      usagePercentage < 50 ? 'bg-green-500' :
                      usagePercentage < 80 ? 'bg-yellow-500' : 'bg-red-500'
                    }`}
                    style={{ width: `${Math.min(usagePercentage, 100)}%` }}
                  ></div>
                </div>
              </div>

              {/* Theme Toggle */}
              <button
                onClick={toggleTheme}
                className="p-2 rounded-lg text-gray-700 dark:text-gray-300 hover:bg-gray-100 dark:hover:bg-gray-700 transition-colors"
                title={isDark ? 'Switch to light mode' : 'Switch to dark mode'}
              >
                {isDark ? (
                  <SunIcon className="h-5 w-5" />
                ) : (
                  <MoonIcon className="h-5 w-5" />
                )}
              </button>

              {/* Profile */}
              <button
                onClick={() => setShowProfile(true)}
                className="p-2 rounded-lg text-gray-700 dark:text-gray-300 hover:bg-gray-100 dark:hover:bg-gray-700 transition-colors"
                title="Profile"
              >
                <UserIcon className="h-5 w-5" />
              </button>

              {/* Logout */}
              <button
                onClick={handleLogout}
                className="p-2 rounded-lg text-gray-700 dark:text-gray-300 hover:bg-gray-100 dark:hover:bg-gray-700 transition-colors"
                title="Logout"
              >
                <ArrowRightOnRectangleIcon className="h-5 w-5" />
              </button>
            </div>
          </div>
        </div>
      </motion.header>

      {/* Main Content */}
      <main className="max-w-7xl mx-auto py-6 px-4 sm:px-6 lg:px-8">
        <AnimatePresence mode="wait">
          {activeTab === 'files' && (
            <motion.div
              key="files"
              initial={{ opacity: 0, x: -20 }}
              animate={{ opacity: 1, x: 0 }}
              exit={{ opacity: 0, x: 20 }}
              transition={{ duration: 0.2 }}
            >
              {/* Files Header */}
              <div className="flex justify-between items-center mb-6">
                <h2 className="text-2xl font-bold text-gray-900 dark:text-white">
                  My Files
                </h2>
                <button
                  onClick={() => setShowUploader(true)}
                  className="btn-primary flex items-center"
                >
                  <PlusIcon className="h-5 w-5 mr-2" />
                  Upload Files
                </button>
              </div>

              {/* File Browser */}
              <FileBrowser />
            </motion.div>
          )}

          {activeTab === 'admin' && user?.is_admin && (
            <motion.div
              key="admin"
              initial={{ opacity: 0, x: -20 }}
              animate={{ opacity: 1, x: 0 }}
              exit={{ opacity: 0, x: 20 }}
              transition={{ duration: 0.2 }}
            >
              <h2 className="text-2xl font-bold text-gray-900 dark:text-white mb-6">
                Admin Panel
              </h2>
              <div className="bg-white dark:bg-dark-800 rounded-lg shadow p-6">
                <p className="text-gray-600 dark:text-gray-400">
                  Admin functionality coming soon...
                </p>
              </div>
            </motion.div>
          )}
        </AnimatePresence>
      </main>

      {/* Upload Modal */}
      <AnimatePresence>
        {showUploader && (
          <FileUploader onClose={() => setShowUploader(false)} />
        )}
      </AnimatePresence>

      {/* Profile Modal */}
      <AnimatePresence>
        {showProfile && (
          <UserProfile onClose={() => setShowProfile(false)} />
        )}
      </AnimatePresence>

      {/* Password Change Notification */}
      {user?.must_change_password && (
        <motion.div
          initial={{ opacity: 0, y: 50 }}
          animate={{ opacity: 1, y: 0 }}
          className="fixed bottom-4 right-4 bg-yellow-500 text-white p-4 rounded-lg shadow-lg max-w-sm"
        >
          <div className="flex items-center">
            <div className="flex-shrink-0">
              ⚠️
            </div>
            <div className="ml-3">
              <p className="text-sm font-medium">
                Please change your password to secure your account.
              </p>
              <button
                onClick={() => setShowProfile(true)}
                className="text-sm underline hover:no-underline mt-1"
              >
                Change Password
              </button>
            </div>
          </div>
        </motion.div>
      )}
    </div>
  )
}

export default Dashboard