import React, { useState } from 'react'
import { motion } from 'framer-motion'
import { XMarkIcon, UserIcon, KeyIcon } from '@heroicons/react/24/outline'

import { useAuthStore } from '../store/authStore'
import { validatePassword } from '../utils/helpers'
import toast from 'react-hot-toast'

const UserProfile = ({ onClose }) => {
  const [activeTab, setActiveTab] = useState('profile')
  const [currentPassword, setCurrentPassword] = useState('')
  const [newPassword, setNewPassword] = useState('')
  const [confirmPassword, setConfirmPassword] = useState('')
  const [isChangingPassword, setIsChangingPassword] = useState(false)

  const { user, changePassword } = useAuthStore()

  const handlePasswordChange = async (e) => {
    e.preventDefault()
    
    if (!currentPassword || !newPassword || !confirmPassword) {
      toast.error('Please fill in all fields')
      return
    }

    if (newPassword !== confirmPassword) {
      toast.error('New passwords do not match')
      return
    }

    const validation = validatePassword(newPassword)
    if (!validation.isValid) {
      toast.error(validation.errors[0])
      return
    }

    setIsChangingPassword(true)
    const result = await changePassword(currentPassword, newPassword)
    setIsChangingPassword(false)

    if (result.success) {
      setCurrentPassword('')
      setNewPassword('')
      setConfirmPassword('')
      setActiveTab('profile')
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
        className="bg-white dark:bg-dark-800 rounded-xl shadow-2xl w-full max-w-md"
      >
        {/* Header */}
        <div className="flex items-center justify-between p-6 border-b border-gray-200 dark:border-gray-700">
          <h2 className="text-xl font-semibold text-gray-900 dark:text-white">
            User Profile
          </h2>
          <button
            onClick={onClose}
            className="p-2 text-gray-400 hover:text-gray-600 dark:hover:text-gray-300 transition-colors"
          >
            <XMarkIcon className="h-6 w-6" />
          </button>
        </div>

        {/* Tabs */}
        <div className="border-b border-gray-200 dark:border-gray-700">
          <div className="flex">
            <button
              onClick={() => setActiveTab('profile')}
              className={`flex-1 py-3 px-4 text-sm font-medium text-center border-b-2 transition-colors ${
                activeTab === 'profile'
                  ? 'border-primary-500 text-primary-600 dark:text-primary-400'
                  : 'border-transparent text-gray-500 hover:text-gray-700 dark:text-gray-400 dark:hover:text-gray-300'
              }`}
            >
              <UserIcon className="h-4 w-4 inline mr-2" />
              Profile
            </button>
            <button
              onClick={() => setActiveTab('password')}
              className={`flex-1 py-3 px-4 text-sm font-medium text-center border-b-2 transition-colors ${
                activeTab === 'password'
                  ? 'border-primary-500 text-primary-600 dark:text-primary-400'
                  : 'border-transparent text-gray-500 hover:text-gray-700 dark:text-gray-400 dark:hover:text-gray-300'
              }`}
            >
              <KeyIcon className="h-4 w-4 inline mr-2" />
              Password
            </button>
          </div>
        </div>

        {/* Content */}
        <div className="p-6">
          {activeTab === 'profile' && (
            <motion.div
              initial={{ opacity: 0, x: -20 }}
              animate={{ opacity: 1, x: 0 }}
              className="space-y-4"
            >
              <div>
                <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-1">
                  Email
                </label>
                <input
                  type="email"
                  value={user?.email || ''}
                  disabled
                  className="input-primary bg-gray-100 dark:bg-gray-700 cursor-not-allowed"
                />
              </div>

              <div>
                <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-1">
                  Username
                </label>
                <input
                  type="text"
                  value={user?.username || ''}
                  disabled
                  className="input-primary bg-gray-100 dark:bg-gray-700 cursor-not-allowed"
                />
              </div>

              <div>
                <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-1">
                  Role
                </label>
                <input
                  type="text"
                  value={user?.is_admin ? 'Administrator' : 'User'}
                  disabled
                  className="input-primary bg-gray-100 dark:bg-gray-700 cursor-not-allowed"
                />
              </div>

              <div>
                <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-1">
                  Storage Quota
                </label>
                <input
                  type="text"
                  value={`${user?.quota_gb || 5} GB`}
                  disabled
                  className="input-primary bg-gray-100 dark:bg-gray-700 cursor-not-allowed"
                />
              </div>

              {user?.must_change_password && (
                <div className="mt-4 p-3 bg-yellow-50 dark:bg-yellow-900/20 border border-yellow-200 dark:border-yellow-700 rounded-lg">
                  <p className="text-sm text-yellow-800 dark:text-yellow-200">
                    ⚠️ You must change your password to secure your account.
                  </p>
                  <button
                    onClick={() => setActiveTab('password')}
                    className="text-sm text-yellow-600 dark:text-yellow-400 underline hover:no-underline mt-1"
                  >
                    Change Password Now
                  </button>
                </div>
              )}
            </motion.div>
          )}

          {activeTab === 'password' && (
            <motion.div
              initial={{ opacity: 0, x: 20 }}
              animate={{ opacity: 1, x: 0 }}
            >
              <form onSubmit={handlePasswordChange} className="space-y-4">
                <div>
                  <label htmlFor="currentPassword" className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-1">
                    Current Password
                  </label>
                  <input
                    id="currentPassword"
                    type="password"
                    value={currentPassword}
                    onChange={(e) => setCurrentPassword(e.target.value)}
                    className="input-primary"
                    placeholder="Enter current password"
                    required
                  />
                </div>

                <div>
                  <label htmlFor="newPassword" className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-1">
                    New Password
                  </label>
                  <input
                    id="newPassword"
                    type="password"
                    value={newPassword}
                    onChange={(e) => setNewPassword(e.target.value)}
                    className="input-primary"
                    placeholder="Enter new password"
                    required
                  />
                </div>

                <div>
                  <label htmlFor="confirmPassword" className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-1">
                    Confirm New Password
                  </label>
                  <input
                    id="confirmPassword"
                    type="password"
                    value={confirmPassword}
                    onChange={(e) => setConfirmPassword(e.target.value)}
                    className="input-primary"
                    placeholder="Confirm new password"
                    required
                  />
                </div>

                <div className="text-xs text-gray-500 dark:text-gray-400 space-y-1">
                  <p>Password requirements:</p>
                  <ul className="list-disc list-inside space-y-1">
                    <li>At least 8 characters long</li>
                    <li>Contains uppercase and lowercase letters</li>
                    <li>Contains at least one number</li>
                    <li>Contains at least one special character</li>
                  </ul>
                </div>

                <button
                  type="submit"
                  disabled={isChangingPassword}
                  className={`w-full btn-primary ${isChangingPassword ? 'opacity-75 cursor-not-allowed' : ''}`}
                >
                  {isChangingPassword ? 'Changing Password...' : 'Change Password'}
                </button>
              </form>
            </motion.div>
          )}
        </div>
      </motion.div>
    </motion.div>
  )
}

export default UserProfile