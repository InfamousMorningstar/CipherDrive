import { create } from 'zustand'
import { persist } from 'zustand/middleware'
import api from '../utils/api'
import toast from 'react-hot-toast'

const useAuthStore = create(
  persist(
    (set, get) => ({
      user: null,
      token: null,
      refreshToken: null,
      isAuthenticated: false,
      loading: false,

      // Login action
      login: async (email, password) => {
        set({ loading: true })
        try {
          const formData = new FormData()
          formData.append('username', email)
          formData.append('password', password)
          
          const response = await api.post('/auth/login', formData, {
            headers: {
              'Content-Type': 'multipart/form-data',
            },
          })

          const { access_token, refresh_token, user } = response.data
          
          // Update API defaults
          api.defaults.headers.common['Authorization'] = `Bearer ${access_token}`

          set({
            user,
            token: access_token,
            refreshToken: refresh_token,
            isAuthenticated: true,
            loading: false,
          })

          toast.success(`Welcome back, ${user.username}!`)
          return { success: true, user }
        } catch (error) {
          set({ loading: false })
          const errorMessage = error.response?.data?.detail || 'Login failed'
          toast.error(errorMessage)
          return { success: false, error: errorMessage }
        }
      },

      // Logout action
      logout: () => {
        // Clear API authorization header
        delete api.defaults.headers.common['Authorization']
        
        set({
          user: null,
          token: null,
          refreshToken: null,
          isAuthenticated: false,
        })
        
        toast.success('Logged out successfully')
      },

      // Check authentication status
      checkAuth: async () => {
        const { token, refreshToken } = get()
        
        if (!token) {
          return false
        }

        try {
          // Set authorization header
          api.defaults.headers.common['Authorization'] = `Bearer ${token}`
          
          // Verify token by fetching user info
          const response = await api.get('/users/me')
          
          set({
            user: response.data,
            isAuthenticated: true,
          })
          
          return true
        } catch (error) {
          // Try to refresh token
          if (refreshToken) {
            try {
              const refreshResponse = await api.post('/auth/refresh', {
                refresh_token: refreshToken
              })
              
              const newToken = refreshResponse.data.access_token
              api.defaults.headers.common['Authorization'] = `Bearer ${newToken}`
              
              set({ token: newToken })
              
              // Try to get user info again
              const userResponse = await api.get('/users/me')
              set({
                user: userResponse.data,
                isAuthenticated: true,
              })
              
              return true
            } catch (refreshError) {
              // Refresh failed, logout user
              get().logout()
              return false
            }
          } else {
            // No refresh token, logout user
            get().logout()
            return false
          }
        }
      },

      // Change password
      changePassword: async (currentPassword, newPassword) => {
        try {
          await api.post('/users/change-password', {
            current_password: currentPassword,
            new_password: newPassword
          })
          
          toast.success('Password changed successfully')
          
          // Update user to mark password as changed
          set(state => ({
            user: { ...state.user, must_change_password: false }
          }))
          
          return { success: true }
        } catch (error) {
          const errorMessage = error.response?.data?.detail || 'Password change failed'
          toast.error(errorMessage)
          return { success: false, error: errorMessage }
        }
      },

      // Request password reset
      requestPasswordReset: async (email) => {
        try {
          await api.post('/auth/forgot-password', { email })
          toast.success('Password reset email sent')
          return { success: true }
        } catch (error) {
          const errorMessage = error.response?.data?.detail || 'Failed to send reset email'
          toast.error(errorMessage)
          return { success: false, error: errorMessage }
        }
      },

      // Reset password with token
      resetPassword: async (token, newPassword) => {
        try {
          await api.post('/auth/reset-password', {
            token,
            new_password: newPassword
          })
          
          toast.success('Password reset successfully')
          return { success: true }
        } catch (error) {
          const errorMessage = error.response?.data?.detail || 'Password reset failed'
          toast.error(errorMessage)
          return { success: false, error: errorMessage }
        }
      },
    }),
    {
      name: 'auth-storage',
      partialize: (state) => ({
        user: state.user,
        token: state.token,
        refreshToken: state.refreshToken,
        isAuthenticated: state.isAuthenticated,
      }),
    }
  )
)

export { useAuthStore }