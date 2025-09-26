import { create } from 'zustand'
import api from '../utils/api'
import toast from 'react-hot-toast'

const useFileStore = create((set, get) => ({
  files: [],
  currentFolder: null,
  loading: false,
  uploading: false,
  uploadProgress: 0,
  
  // Fetch files in current folder
  fetchFiles: async (folderId = null) => {
    set({ loading: true })
    try {
      const response = await api.get('/files', {
        params: { parent_folder_id: folderId }
      })
      
      set({ files: response.data.files, currentFolder: folderId, loading: false })
      return response.data.files
    } catch (error) {
      set({ loading: false })
      const errorMessage = error.response?.data?.detail || 'Failed to fetch files'
      toast.error(errorMessage)
      throw error
    }
  },

  // Upload file
  uploadFile: async (file, folderId = null, onProgress = null) => {
    set({ uploading: true, uploadProgress: 0 })
    
    try {
      const formData = new FormData()
      formData.append('file', file)
      if (folderId) {
        formData.append('parent_folder_id', folderId)
      }

      const response = await api.post('/files/upload', formData, {
        headers: {
          'Content-Type': 'multipart/form-data',
        },
        onUploadProgress: (progressEvent) => {
          const progress = Math.round((progressEvent.loaded * 100) / progressEvent.total)
          set({ uploadProgress: progress })
          if (onProgress) onProgress(progress)
        }
      })

      set({ uploading: false, uploadProgress: 0 })
      toast.success(`File "${file.name}" uploaded successfully`)
      
      // Refresh current folder
      await get().fetchFiles(get().currentFolder)
      
      return response.data
    } catch (error) {
      set({ uploading: false, uploadProgress: 0 })
      const errorMessage = error.response?.data?.detail || 'Upload failed'
      toast.error(errorMessage)
      throw error
    }
  },

  // Create folder
  createFolder: async (name, parentFolderId = null) => {
    try {
      const formData = new FormData()
      formData.append('name', name)
      if (parentFolderId) {
        formData.append('parent_folder_id', parentFolderId)
      }

      const response = await api.post('/files/folder', formData)
      
      toast.success(`Folder "${name}" created successfully`)
      
      // Refresh current folder
      await get().fetchFiles(get().currentFolder)
      
      return response.data
    } catch (error) {
      const errorMessage = error.response?.data?.detail || 'Failed to create folder'
      toast.error(errorMessage)
      throw error
    }
  },

  // Delete file or folder
  deleteFile: async (fileId, filename) => {
    try {
      await api.delete(`/files/${fileId}`)
      
      toast.success(`"${filename}" deleted successfully`)
      
      // Refresh current folder
      await get().fetchFiles(get().currentFolder)
      
    } catch (error) {
      const errorMessage = error.response?.data?.detail || 'Failed to delete file'
      toast.error(errorMessage)
      throw error
    }
  },

  // Download file
  downloadFile: async (fileId, filename) => {
    try {
      const response = await api.get(`/files/${fileId}/download`, {
        responseType: 'blob',
      })

      // Create download link
      const url = window.URL.createObjectURL(new Blob([response.data]))
      const link = document.createElement('a')
      link.href = url
      link.setAttribute('download', filename)
      document.body.appendChild(link)
      link.click()
      link.remove()
      window.URL.revokeObjectURL(url)
      
      toast.success(`"${filename}" downloaded successfully`)
    } catch (error) {
      const errorMessage = error.response?.data?.detail || 'Download failed'
      toast.error(errorMessage)
      throw error
    }
  },

  // Navigate to folder
  navigateToFolder: async (folderId) => {
    await get().fetchFiles(folderId)
  },

  // Go back to parent folder
  navigateUp: async () => {
    // This would require tracking folder hierarchy
    // For now, go to root
    await get().fetchFiles(null)
  },
}))

export { useFileStore }