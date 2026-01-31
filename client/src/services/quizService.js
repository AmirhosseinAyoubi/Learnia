/**
 * Quiz Service
 */
import apiClient from './api'

export const quizService = {
  generateQuiz: async (quizRequest) => {
    const response = await apiClient.post('/api/v1/quizzes', quizRequest)
    return response.data
  },

  getQuizById: async (quizId) => {
    const response = await apiClient.get(`/api/v1/quizzes/${quizId}`)
    return response.data
  },

  submitQuizAttempt: async (quizId, answers) => {
    const response = await apiClient.post(`/api/v1/quizzes/${quizId}/attempts`, {
      answers,
    })
    return response.data
  },

  getQuizAttempts: async (quizId) => {
    const response = await apiClient.get(`/api/v1/quizzes/${quizId}/attempts`)
    return response.data
  },
}
