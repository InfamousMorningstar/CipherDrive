import React, { useState } from 'react'
import { Link } from 'react-router-dom'
import { motion } from 'framer-motion'
import { EyeIcon, EyeSlashIcon, ComputerDesktopIcon } from '@heroicons/react/24/outline'
import toast from 'react-hot-toast'

import { useAuthStore } from '../store/authStore'
import { useThemeStore } from '../store/themeStore'
import { validateEmail } from '../utils/helpers'
import MatrixBackground from './MatrixBackground'

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
    <div className="min-h-screen bg-dark-bg text-dark-text-primary relative overflow-hidden">
      {/* Matrix Background */}
      <MatrixBackground />
      
      {/* Navigation */}
      <motion.nav 
        className="absolute top-0 left-0 right-0 z-20 flex justify-between items-center p-6"
        initial={{ opacity: 0, y: -20 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ duration: 0.6 }}
      >
        <Link to="/" className="flex items-center space-x-2">
          <ComputerDesktopIcon className="h-8 w-8 text-cipher-teal-400" />
          <span className="font-mono text-xl font-bold">CipherDrive</span>
        </Link>
      </motion.nav>

      {/* Login Form */}
      <div className="relative z-10 flex items-center justify-center min-h-screen px-4 sm:px-6 lg:px-8">
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.8 }}
          className="max-w-md w-full"
        >
          {/* Login Card */}
          <div className="bg-dark-card border border-cipher-border rounded-2xl p-8 backdrop-blur-sm">
            {/* Header */}
            <div className="text-center mb-8">
              <motion.div
                initial={{ scale: 0 }}
                animate={{ scale: 1 }}
                transition={{ delay: 0.2, type: "spring", stiffness: 200 }}
                className="mx-auto h-16 w-16 bg-gradient-to-r from-cipher-teal-400 to-cipher-purple-400 rounded-xl flex items-center justify-center mb-4 relative"
              >
                <motion.div
                  className="absolute inset-0 rounded-xl bg-cipher-purple-glow blur-xl opacity-30"
                  animate={{ 
                    scale: [1, 1.1, 1],
                    opacity: [0.3, 0.6, 0.3]
                  }}
                  transition={{ 
                    duration: 2,
                    repeat: Infinity,
                    ease: "easeInOut"
                  }}
                />
                <ComputerDesktopIcon className="h-8 w-8 text-white relative z-10" />
              </motion.div>
              
              <motion.h1
                initial={{ opacity: 0 }}
                animate={{ opacity: 1 }}
                transition={{ delay: 0.3 }}
                className="text-3xl font-bold font-mono mb-2"
              >
                <span className="bg-gradient-to-r from-cipher-teal-400 to-cipher-purple-400 bg-clip-text text-transparent">
                  CIPHER
                </span>
                <span className="text-white">DRIVE</span>
              </motion.h1>
              
              <motion.p
                initial={{ opacity: 0 }}
                animate={{ opacity: 1 }}
                transition={{ delay: 0.4 }}
                className="text-gray-300 font-mono"
              >
                <span className="text-cipher-teal-400">&gt;</span> System Access Required
              </motion.p>
            </div>

            {!showForgotPassword ? (
              /* Login Form */
              <form onSubmit={handleSubmit} className="space-y-6">
                <div>
                  <label htmlFor="email" className="block text-sm font-mono text-gray-300 mb-2">
                    <span className="text-cipher-teal-400">&gt;</span> Email Address
                  </label>
                  <motion.input
                    whileFocus={{ scale: 1.02 }}
                    type="email"
                    id="email"
                    value={email}
                    onChange={(e) => setEmail(e.target.value)}
                    className="w-full px-4 py-3 bg-dark-bg border border-cipher-border rounded-lg font-mono text-white placeholder-gray-400 focus:outline-none focus:border-cipher-teal-400 focus:ring-2 focus:ring-cipher-teal-400/20 transition-all duration-300"
                    placeholder="user@cipherdrive.local"
                    required
                  />
                </div>

                <div>
                  <label htmlFor="password" className="block text-sm font-mono text-gray-300 mb-2">
                    <span className="text-cipher-teal-400">&gt;</span> Password
                  </label>
                  <div className="relative">
                    <motion.input
                      whileFocus={{ scale: 1.02 }}
                      type={showPassword ? "text" : "password"}
                      id="password"
                      value={password}
                      onChange={(e) => setPassword(e.target.value)}
                      className="w-full px-4 py-3 pr-12 bg-dark-bg border border-cipher-border rounded-lg font-mono text-white placeholder-gray-400 focus:outline-none focus:border-cipher-teal-400 focus:ring-2 focus:ring-cipher-teal-400/20 transition-all duration-300"
                      placeholder="Enter your access code"
                      required
                    />
                    <button
                      type="button"
                      onClick={() => setShowPassword(!showPassword)}
                      className="absolute inset-y-0 right-0 pr-3 flex items-center text-gray-400 hover:text-cipher-teal-400 transition-colors duration-200"
                    >
                      {showPassword ? (
                        <EyeSlashIcon className="h-5 w-5" />
                      ) : (
                        <EyeIcon className="h-5 w-5" />
                      )}
                    </button>
                  </div>
                </div>

                <div className="flex items-center justify-between text-sm">
                  <button
                    type="button"
                    onClick={() => setShowForgotPassword(true)}
                    className="text-cipher-teal-400 hover:text-cipher-teal-300 transition-colors duration-200 font-mono"
                  >
                    <span className="text-gray-400">&gt;</span> Forgot access code?
                  </button>
                </div>

                <motion.button
                  type="submit"
                  disabled={isLoading}
                  whileHover={{ scale: 1.02 }}
                  whileTap={{ scale: 0.98 }}
                  className="w-full py-3 px-4 bg-gradient-to-r from-cipher-teal-400 to-cipher-purple-400 text-white font-mono font-bold rounded-lg hover:shadow-lg hover:shadow-cipher-teal-400/25 focus:outline-none focus:ring-2 focus:ring-cipher-teal-400/50 disabled:opacity-50 disabled:cursor-not-allowed transition-all duration-300 relative overflow-hidden"
                >
                  <motion.div
                    className="absolute inset-0 bg-white opacity-0"
                    whileHover={{ opacity: 0.1 }}
                    transition={{ duration: 0.3 }}
                  />
                  <span className="relative z-10 flex items-center justify-center">
                    {isLoading ? (
                      <>
                        <motion.div
                          animate={{ rotate: 360 }}
                          transition={{ duration: 1, repeat: Infinity, ease: "linear" }}
                          className="w-5 h-5 border-2 border-white border-t-transparent rounded-full mr-2"
                        />
                        Authenticating...
                      </>
                    ) : (
                      <>
                        <span className="mr-2">&gt;</span>
                        Initialize Access
                      </>
                    )}
                  </span>
                </motion.button>
              </form>
            ) : (
              /* Forgot Password Form */
              <form onSubmit={handleForgotPassword} className="space-y-6">
                <div>
                  <h3 className="text-lg font-mono font-bold text-white mb-4">
                    <span className="text-cipher-teal-400">&gt;</span> Password Recovery
                  </h3>
                  <label htmlFor="resetEmail" className="block text-sm font-mono text-gray-300 mb-2">
                    Email Address
                  </label>
                  <motion.input
                    whileFocus={{ scale: 1.02 }}
                    type="email"
                    id="resetEmail"
                    value={resetEmail}
                    onChange={(e) => setResetEmail(e.target.value)}
                    className="w-full px-4 py-3 bg-dark-bg border border-cipher-border rounded-lg font-mono text-white placeholder-gray-400 focus:outline-none focus:border-cipher-teal-400 focus:ring-2 focus:ring-cipher-teal-400/20 transition-all duration-300"
                    placeholder="user@cipherdrive.local"
                    required
                  />
                </div>

                <div className="flex space-x-4">
                  <motion.button
                    type="button"
                    onClick={() => setShowForgotPassword(false)}
                    whileHover={{ scale: 1.02 }}
                    whileTap={{ scale: 0.98 }}
                    className="flex-1 py-3 px-4 border border-cipher-border text-gray-300 font-mono rounded-lg hover:bg-cipher-border/20 focus:outline-none focus:ring-2 focus:ring-cipher-border/50 transition-all duration-300"
                  >
                    <span className="mr-2">&lt;</span>
                    Back
                  </motion.button>
                  
                  <motion.button
                    type="submit"
                    whileHover={{ scale: 1.02 }}
                    whileTap={{ scale: 0.98 }}
                    className="flex-1 py-3 px-4 bg-gradient-to-r from-cipher-teal-400 to-cipher-purple-400 text-white font-mono font-bold rounded-lg hover:shadow-lg hover:shadow-cipher-teal-400/25 focus:outline-none focus:ring-2 focus:ring-cipher-teal-400/50 transition-all duration-300"
                  >
                    <span className="mr-2">&gt;</span>
                    Send Reset
                  </motion.button>
                </div>
              </form>
            )}

            {/* Footer */}
            <motion.div
              initial={{ opacity: 0 }}
              animate={{ opacity: 1 }}
              transition={{ delay: 0.6 }}
              className="mt-6 text-center"
            >
              <p className="text-gray-400 font-mono text-sm">
                CipherDrive v1.0.0-alpha | Secure • Private • Fast
              </p>
            </motion.div>
          </div>
        </motion.div>
      </div>
    </div>
  )
}

export default LoginForm