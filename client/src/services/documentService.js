/**
 * Document Service
 */
import axios from 'axios'
import apiClient from './api'

export const documentService = {
  getDocumentsByCourse: async (courseId) => {
    const response = await apiClient.get('/api/v1/documents', {
      params: { courseId },
    })
    return response.data
  },

  getDocumentById: async (documentId) => {
    const response = await apiClient.get(`/api/v1/documents/${documentId}`)
    return response.data
  },

  uploadDocument: async (file, title, courseId) => {
    const formData = new FormData()
    formData.append('file', file)
    formData.append('title', title)

    const response = await axios.post('http://localhost:8084/documents/upload', formData, {
      headers: {
        'Content-Type': 'multipart/form-data',
      },
    })

    return response.data
  },
}