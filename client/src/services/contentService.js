/**
 * Content Service - Semantic search
 */
import apiClient from './api'

export const contentService = {
  searchContent: async (query, courseId) => {
    const response = await apiClient.get('/api/v1/content/chunks', {
      params: { search: query, courseId },
    })
    return response.data
  },
}
