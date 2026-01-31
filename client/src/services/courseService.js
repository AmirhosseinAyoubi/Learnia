/**
 * Course Service
 */
import apiClient from './api'

export const courseService = {
  getAllCourses: async (userId) => {
    const response = await apiClient.get('/api/v1/courses', {
      params: { userId },
    })
    return response.data
  },

  getCourseById: async (courseId) => {
    const response = await apiClient.get(`/api/v1/courses/${courseId}`)
    return response.data
  },

  enrollInCourse: async (courseId) => {
    const response = await apiClient.post(`/api/v1/courses/${courseId}/enroll`)
    return response.data
  },
}
