/**
 * Authentication Service
 */
import apiClient from './api'

export const authService = {
  login: async (email, password) => {
    const response = await apiClient.post('/api/v1/auth/login', {
      email,
      password,
    })
    return response.data
  },

  register: async (userData) => {
    const response = await apiClient.post('/api/v1/auth/register', userData)
    return response.data
  },

  logout: () => {
    localStorage.removeItem('token')
  },

  getCurrentUser: async () => {
    const response = await apiClient.get('/api/v1/auth/me')
    return response.data
  },
}
