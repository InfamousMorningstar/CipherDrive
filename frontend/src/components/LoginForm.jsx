import React, { useState } from 'react'
import { Link } from 'react-router-dom'
import { motion } from 'framer-motion'
import { EyeIcon, EyeSlashIcon, CloudIcon } from '@heroicons/react/24/outline'
import toast from 'react-hot-toast'

import { useAuthStore } from '../store/authStore'
import { useThemeStore } from '../store/themeStore'
import { validateEmail } from '../utils/helpers'

const LoginForm = () => {
  const [email, setEmail] = useState('')
  const [password, setPassword] = useState('')
  const [showPassword, setShowPassword] = useState(false)
  const [isLoading, setIsLoading] = useState(false)
  const [showForgotPassword, setShowForgotPassword] = useState(false)
  const [resetEmail, setResetEmail] = useState('')

  const { login, requestPasswordReset } = useAuthStore()
  const { isDark, toggleTheme } = useThemeStore()

  const handleSubmit = async (e) => {
    e.preventDefault()
    
    if (!email || !password) {
      toast.error('Please fill in all fields')
      return
    }

    if (!validateEmail(email)) {
      toast.error('Please enter a valid email address')
      return
    }

    setIsLoading(true)
    const result = await login(email, password)
    setIsLoading(false)

    if (result.success && result.user?.must_change_password) {
      toast.info('Please change your password to continue', { duration: 6000 })
    }
  }

  const handleForgotPassword = async (e) => {
    e.preventDefault()
    
    if (!resetEmail || !validateEmail(resetEmail)) {
      toast.error('Please enter a valid email address')
      return
    }

    const result = await requestPasswordReset(resetEmail)
    if (result.success) {
      setShowForgotPassword(false)
      setResetEmail('')
    }
  }

  return (
    <div className="min-h-screen flex items-center justify-center py-12 px-4 sm:px-6 lg:px-8 bg-gradient-to-br from-blue-50 to-indigo-100 dark:from-gray-900 dark:to-gray-800">
      <motion.div
        initial={{ opacity: 0, y: 20 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ duration: 0.5 }}
        className="max-w-md w-full"
      >
        {/* Theme Toggle */}
        <div className="flex justify-end mb-4">
          <button
            onClick={toggleTheme}
            className="p-2 rounded-lg bg-white dark:bg-gray-800 shadow-md hover:shadow-lg transition-all duration-200"
            title={isDark ? 'Switch to light mode' : 'Switch to dark mode'}
          >
            {isDark ? '☀️' : '🌙'}
          </button>
        </div>

        <div className="bg-white dark:bg-gray-800 rounded-2xl shadow-2xl p-8">
          {/* Header */}
          <div className="text-center mb-8">
            <motion.div
              initial={{ scale: 0 }}
              animate={{ scale: 1 }}
              transition={{ delay: 0.2, type: "spring", stiffness: 200 }}
              className="mx-auto h-16 w-16 bg-gradient-to-r from-blue-500 to-indigo-600 rounded-xl flex items-center justify-center mb-4"
            >
              <CloudIcon className="h-8 w-8 text-white" />
            </motion.div>
            
            <motion.h1
              initial={{ opacity: 0 }}
              animate={{ opacity: 1 }}
              transition={{ delay: 0.3 }}
              className="text-3xl font-bold text-gray-900 dark:text-white mb-2"
            >
              Dropbox Lite
            </motion.h1>
            
            <motion.p
              initial={{ opacity: 0 }}
              animate={{ opacity: 1 }}
              transition={{ delay: 0.4 }}
              className="text-gray-600 dark:text-gray-400"
            >
              Secure file sharing made simple
            </motion.p>
          </div>

          {!showForgotPassword ? (
            /* Login Form */
            <motion.form
              initial={{ opacity: 0, x: -20 }}
              animate={{ opacity: 1, x: 0 }}
              transition={{ delay: 0.5 }}
              onSubmit={handleSubmit}
              className="space-y-6"
            >
              <div>
                <label htmlFor="email" className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
                  Email Address
                </label>
                <input
                  id="email"
                  name="email"
                  type="email"
                  autoComplete="email"
                  required
                  value={email}
                  onChange={(e) => setEmail(e.target.value)}
                  className="input-primary"
                  placeholder="Enter your email"
                />
              </div>

              <div>
                <label htmlFor="password" className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
                  Password
                </label>
                <div className="relative">
                  <input
                    id="password"
                    name="password"
                    type={showPassword ? "text" : "password"}
                    autoComplete="current-password"
                    required
                    value={password}
                    onChange={(e) => setPassword(e.target.value)}
                    className="input-primary pr-12"
                    placeholder="Enter your password"
                  />
                  <button
                    type="button"
                    onClick={() => setShowPassword(!showPassword)}
                    className="absolute inset-y-0 right-0 pr-3 flex items-center"
                  >
                    {showPassword ? (
                      <EyeSlashIcon className="h-5 w-5 text-gray-400" />
                    ) : (
                      <EyeIcon className="h-5 w-5 text-gray-400" />
                    )}
                  </button>
                </div>
              </div>

              <div className="flex items-center justify-between">
                <div className="text-sm">
                  <button
                    type="button"
                    onClick={() => setShowForgotPassword(true)}
                    className="text-primary-600 hover:text-primary-500 font-medium"
                  >
                    Forgot your password?
                  </button>
                </div>
              </div>

              <motion.button
                type="submit"
                disabled={isLoading}
                whileHover={{ scale: 1.02 }}
                whileTap={{ scale: 0.98 }}
                className={`w-full btn-primary ${isLoading ? 'opacity-75 cursor-not-allowed' : ''}`}
              >
                {isLoading ? (
                  <div className="flex items-center justify-center">
                    <div className="animate-spin rounded-full h-5 w-5 border-b-2 border-white mr-2"></div>
                    Signing in...
                  </div>
                ) : (
                  'Sign In'
                )}
              </motion.button>
            </motion.form>
          ) : (
            /* Forgot Password Form */
            <motion.form
              initial={{ opacity: 0, x: 20 }}
              animate={{ opacity: 1, x: 0 }}
              transition={{ duration: 0.3 }}
              onSubmit={handleForgotPassword}
              className="space-y-6"
            >
              <div className="text-center mb-6">
                <h3 className="text-lg font-medium text-gray-900 dark:text-white mb-2">
                  Reset Your Password
                </h3>
                <p className="text-sm text-gray-600 dark:text-gray-400">
                  Enter your email address and we'll send you a link to reset your password.
                </p>
              </div>

              <div>
                <label htmlFor="resetEmail" className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
                  Email Address
                </label>
                <input
                  id="resetEmail"
                  name="resetEmail"
                  type="email"
                  autoComplete="email"
                  required
                  value={resetEmail}
                  onChange={(e) => setResetEmail(e.target.value)}
                  className="input-primary"
                  placeholder="Enter your email"
                />
              </div>

              <div className="flex space-x-3">
                <button
                  type="button"
                  onClick={() => {
                    setShowForgotPassword(false)
                    setResetEmail('')
                  }}
                  className="flex-1 btn-secondary"
                >
                  Cancel
                </button>
                <motion.button
                  type="submit"
                  whileHover={{ scale: 1.02 }}
                  whileTap={{ scale: 0.98 }}
                  className="flex-1 btn-primary"
                >
                  Send Reset Link
                </motion.button>
              </div>
            </motion.form>
          )}

          {/* Footer */}
          <motion.div
            initial={{ opacity: 0 }}
            animate={{ opacity: 1 }}
            transition={{ delay: 0.6 }}
            className="mt-8 pt-6 border-t border-gray-200 dark:border-gray-700"
          >
            <p className="text-center text-sm text-gray-500 dark:text-gray-400">
              © 2025 Dropbox Lite. Secure file sharing solution.
            </p>
          </motion.div>
        </div>
      </motion.div>
    </div>
  )
}

export default LoginForm