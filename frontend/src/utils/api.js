import axios from 'axios'

// Create axios instance with base configuration
const api = axios.create({
  baseURL: process.env.REACT_APP_API_URL || 'http://localhost:8000',
  timeout: 30000, // 30 seconds timeout
  headers: {
    'Content-Type': 'application/json',
  },
})

// Request interceptor to add auth token
api.interceptors.request.use(
  (config) => {
    // Don't add auth header for public endpoints
    const publicEndpoints = ['/auth/login', '/auth/refresh', '/auth/forgot-password', '/auth/reset-password']
    const isPublicEndpoint = publicEndpoints.some(endpoint => 
      config.url?.includes(endpoint)
    )
    
    if (!isPublicEndpoint) {
      const token = localStorage.getItem('auth-storage')
      if (token) {
        try {
          const authData = JSON.parse(token)
          if (authData.state?.token) {
            config.headers.Authorization = `Bearer ${authData.state.token}`
          }
        } catch (error) {
          console.error('Error parsing auth token:', error)
        }
      }
    }
    
    return config
  },
  (error) => {
    return Promise.reject(error)
  }
)

// Response interceptor to handle token refresh
api.interceptors.response.use(
  (response) => {
    return response
  },
  async (error) => {
    const originalRequest = error.config
    
    // If the error status is 401 and we haven't already tried to refresh
    if (error.response?.status === 401 && !originalRequest._retry) {
      originalRequest._retry = true
      
      try {
        const authStorage = localStorage.getItem('auth-storage')
        if (authStorage) {
          const authData = JSON.parse(authStorage)
          const refreshToken = authData.state?.refreshToken
          
          if (refreshToken) {
            const refreshResponse = await axios.post(
              `${api.defaults.baseURL}/auth/refresh`,
              { refresh_token: refreshToken }
            )
            
            const newToken = refreshResponse.data.access_token
            
            // Update stored token
            authData.state.token = newToken
            localStorage.setItem('auth-storage', JSON.stringify(authData))
            
            // Retry original request with new token
            originalRequest.headers.Authorization = `Bearer ${newToken}`
            return api(originalRequest)
          }
        }
      } catch (refreshError) {
        // Refresh failed, redirect to login
        localStorage.removeItem('auth-storage')
        window.location.href = '/login'
        return Promise.reject(refreshError)
      }
    }
    
    return Promise.reject(error)
  }
)

export default api