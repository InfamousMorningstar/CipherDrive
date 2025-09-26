import React from 'react'
import { motion } from 'framer-motion'

const AdminPanel = () => {
  return (
    <motion.div
      initial={{ opacity: 0, y: 20 }}
      animate={{ opacity: 1, y: 0 }}
      className="max-w-7xl mx-auto py-6 px-4 sm:px-6 lg:px-8"
    >
      <div className="mb-8">
        <h1 className="text-3xl font-bold text-gray-900 dark:text-white">
          Admin Panel
        </h1>
        <p className="mt-2 text-gray-600 dark:text-gray-400">
          Manage users, monitor system usage, and configure settings
        </p>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
        {/* User Management */}
        <motion.div
          initial={{ opacity: 0, scale: 0.9 }}
          animate={{ opacity: 1, scale: 1 }}
          transition={{ delay: 0.1 }}
          className="card"
        >
          <h3 className="text-lg font-semibold text-gray-900 dark:text-white mb-4">
            User Management
          </h3>
          <p className="text-gray-600 dark:text-gray-400 mb-4">
            Create, edit, and manage user accounts
          </p>
          <button className="btn-primary w-full">
            Manage Users
          </button>
        </motion.div>

        {/* System Stats */}
        <motion.div
          initial={{ opacity: 0, scale: 0.9 }}
          animate={{ opacity: 1, scale: 1 }}
          transition={{ delay: 0.2 }}
          className="card"
        >
          <h3 className="text-lg font-semibold text-gray-900 dark:text-white mb-4">
            System Statistics
          </h3>
          <p className="text-gray-600 dark:text-gray-400 mb-4">
            View system usage and performance metrics
          </p>
          <button className="btn-secondary w-full">
            View Stats
          </button>
        </motion.div>

        {/* Audit Logs */}
        <motion.div
          initial={{ opacity: 0, scale: 0.9 }}
          animate={{ opacity: 1, scale: 1 }}
          transition={{ delay: 0.3 }}
          className="card"
        >
          <h3 className="text-lg font-semibold text-gray-900 dark:text-white mb-4">
            Audit Logs
          </h3>
          <p className="text-gray-600 dark:text-gray-400 mb-4">
            Review system access and activity logs
          </p>
          <button className="btn-secondary w-full">
            View Logs
          </button>
        </motion.div>

        {/* Settings */}
        <motion.div
          initial={{ opacity: 0, scale: 0.9 }}
          animate={{ opacity: 1, scale: 1 }}
          transition={{ delay: 0.4 }}
          className="card"
        >
          <h3 className="text-lg font-semibold text-gray-900 dark:text-white mb-4">
            System Settings
          </h3>
          <p className="text-gray-600 dark:text-gray-400 mb-4">
            Configure system-wide settings and preferences
          </p>
          <button className="btn-secondary w-full">
            Settings
          </button>
        </motion.div>

        {/* Backup & Restore */}
        <motion.div
          initial={{ opacity: 0, scale: 0.9 }}
          animate={{ opacity: 1, scale: 1 }}
          transition={{ delay: 0.5 }}
          className="card"
        >
          <h3 className="text-lg font-semibold text-gray-900 dark:text-white mb-4">
            Backup & Restore
          </h3>
          <p className="text-gray-600 dark:text-gray-400 mb-4">
            Manage system backups and data restoration
          </p>
          <button className="btn-secondary w-full">
            Manage Backups
          </button>
        </motion.div>

        {/* Monitoring */}
        <motion.div
          initial={{ opacity: 0, scale: 0.9 }}
          animate={{ opacity: 1, scale: 1 }}
          transition={{ delay: 0.6 }}
          className="card"
        >
          <h3 className="text-lg font-semibold text-gray-900 dark:text-white mb-4">
            System Monitoring
          </h3>
          <p className="text-gray-600 dark:text-gray-400 mb-4">
            Monitor server health and performance
          </p>
          <button className="btn-secondary w-full">
            View Monitor
          </button>
        </motion.div>
      </div>

      {/* Coming Soon Notice */}
      <motion.div
        initial={{ opacity: 0 }}
        animate={{ opacity: 1 }}
        transition={{ delay: 0.8 }}
        className="mt-8 p-4 bg-blue-50 dark:bg-blue-900/20 border border-blue-200 dark:border-blue-700 rounded-lg"
      >
        <div className="flex">
          <div className="flex-shrink-0">
            <span className="text-2xl">🚧</span>
          </div>
          <div className="ml-3">
            <h3 className="text-sm font-medium text-blue-800 dark:text-blue-200">
              Admin Panel Coming Soon
            </h3>
            <div className="mt-2 text-sm text-blue-700 dark:text-blue-300">
              <p>
                Full admin functionality including user management, system monitoring, 
                and advanced configuration options will be available in the next release.
              </p>
            </div>
          </div>
        </div>
      </motion.div>
    </motion.div>
  )
}

export default AdminPanel