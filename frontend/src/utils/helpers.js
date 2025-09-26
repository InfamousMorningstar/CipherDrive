// Format file size in human readable format
export const formatFileSize = (bytes) => {
  if (bytes === 0) return '0 B'
  
  const sizes = ['B', 'KB', 'MB', 'GB', 'TB']
  const i = Math.floor(Math.log(bytes) / Math.log(1024))
  const size = (bytes / Math.pow(1024, i)).toFixed(1)
  
  return `${size} ${sizes[i]}`
}

// Format date to human readable format
export const formatDate = (dateString) => {
  const date = new Date(dateString)
  const now = new Date()
  const diffTime = Math.abs(now - date)
  const diffDays = Math.ceil(diffTime / (1000 * 60 * 60 * 24))
  
  if (diffDays === 1) {
    return 'Yesterday'
  } else if (diffDays < 7) {
    return `${diffDays} days ago`
  } else if (diffDays < 30) {
    const weeks = Math.floor(diffDays / 7)
    return `${weeks} week${weeks > 1 ? 's' : ''} ago`
  } else {
    return date.toLocaleDateString()
  }
}

// Get file icon based on mime type
export const getFileIcon = (mimeType, isFolder = false) => {
  if (isFolder) return '📁'
  
  if (!mimeType) return '📄'
  
  if (mimeType.startsWith('image/')) return '🖼️'
  if (mimeType.startsWith('video/')) return '🎬'
  if (mimeType.startsWith('audio/')) return '🎵'
  if (mimeType.includes('pdf')) return '📕'
  if (mimeType.includes('word') || mimeType.includes('document')) return '📄'
  if (mimeType.includes('excel') || mimeType.includes('spreadsheet')) return '📊'
  if (mimeType.includes('powerpoint') || mimeType.includes('presentation')) return '📊'
  if (mimeType.includes('zip') || mimeType.includes('rar') || mimeType.includes('tar')) return '🗜️'
  if (mimeType.includes('text/') || mimeType.includes('json') || mimeType.includes('xml')) return '📝'
  
  return '📄'
}

// Check if file is previewable
export const isPreviewable = (mimeType) => {
  if (!mimeType) return false
  
  const previewableTypes = [
    'image/',
    'text/',
    'application/json',
    'application/pdf'
  ]
  
  return previewableTypes.some(type => mimeType.startsWith(type))
}

// Validate password strength
export const validatePassword = (password) => {
  const minLength = 8
  const hasUppercase = /[A-Z]/.test(password)
  const hasLowercase = /[a-z]/.test(password)
  const hasNumbers = /\d/.test(password)
  const hasSpecialChar = /[!@#$%^&*()_+\-=\[\]{};':"\\|,.<>\/?]/.test(password)
  
  const errors = []
  
  if (password.length < minLength) {
    errors.push(`Password must be at least ${minLength} characters long`)
  }
  
  if (!hasUppercase) {
    errors.push('Password must contain at least one uppercase letter')
  }
  
  if (!hasLowercase) {
    errors.push('Password must contain at least one lowercase letter')
  }
  
  if (!hasNumbers) {
    errors.push('Password must contain at least one number')
  }
  
  if (!hasSpecialChar) {
    errors.push('Password must contain at least one special character')
  }
  
  return {
    isValid: errors.length === 0,
    errors
  }
}

// Validate email format
export const validateEmail = (email) => {
  const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/
  return emailRegex.test(email)
}

// Generate random string for share links
export const generateShareId = (length = 8) => {
  const chars = 'ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789'
  let result = ''
  for (let i = 0; i < length; i++) {
    result += chars.charAt(Math.floor(Math.random() * chars.length))
  }
  return result
}

// Copy text to clipboard
export const copyToClipboard = async (text) => {
  try {
    await navigator.clipboard.writeText(text)
    return true
  } catch (err) {
    // Fallback for older browsers
    const textArea = document.createElement('textarea')
    textArea.value = text
    textArea.style.position = 'fixed'
    textArea.style.left = '-999999px'
    textArea.style.top = '-999999px'
    document.body.appendChild(textArea)
    textArea.focus()
    textArea.select()
    
    try {
      document.execCommand('copy')
      textArea.remove()
      return true
    } catch (err) {
      textArea.remove()
      return false
    }
  }
}

// Calculate storage usage percentage
export const calculateUsagePercentage = (used, total) => {
  if (total === 0) return 0
  return Math.min((used / total) * 100, 100)
}

// Get storage color based on usage percentage
export const getStorageColor = (percentage) => {
  if (percentage < 50) return 'text-green-600 dark:text-green-400'
  if (percentage < 80) return 'text-yellow-600 dark:text-yellow-400'
  return 'text-red-600 dark:text-red-400'
}

// Debounce function
export const debounce = (func, wait) => {
  let timeout
  return function executedFunction(...args) {
    const later = () => {
      clearTimeout(timeout)
      func(...args)
    }
    clearTimeout(timeout)
    timeout = setTimeout(later, wait)
  }
}

// Throttle function
export const throttle = (func, limit) => {
  let inThrottle
  return function(...args) {
    if (!inThrottle) {
      func.apply(this, args)
      inThrottle = true
      setTimeout(() => inThrottle = false, limit)
    }
  }
}