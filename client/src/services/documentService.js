/**
 * Document Service
 */
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

  uploadDocument: async (file, courseId) => {
    const formData = new FormData()
    formData.append('file', file)
    formData.append('courseId', courseId)
    
    const response = await apiClient.post('/api/v1/documents', formData, {
      headers: {
        'Content-Type': 'multipart/form-data',
      },
    })
    return response.data
  },
}
