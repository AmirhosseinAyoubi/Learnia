/**
 * Question Service
 */
import apiClient from './api'

export const questionService = {
  submitQuestion: async (questionData) => {
    const response = await apiClient.post('/api/v1/questions', questionData)
    return response.data
  },

  getQuestionsByCourse: async (courseId) => {
    const response = await apiClient.get('/api/v1/questions', {
      params: { courseId },
    })
    return response.data
  },

  getQuestionById: async (questionId) => {
    const response = await apiClient.get(`/api/v1/questions/${questionId}`)
    return response.data
  },

  upvoteQuestion: async (questionId) => {
    const response = await apiClient.put(`/api/v1/questions/${questionId}/upvote`)
    return response.data
  },
}
