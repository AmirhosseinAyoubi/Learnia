/**
 * AuthService — all API calls related to authentication.
 *
 * The API gateway runs at VITE_API_BASE_URL (default: http://localhost:8080).
 * All auth endpoints live under /api/v1/auth on the auth-service.
 */
import apiClient from './api'

export const authService = {
  /** Login: returns { accessToken, refreshToken, user } */
  login: async (email, password) => {
    const response = await apiClient.post('/api/v1/auth/login', { email, password })
    return response.data
  },

  /** Register: returns { accessToken, refreshToken, user } */
  register: async (userData) => {
    const response = await apiClient.post('/api/v1/auth/register', userData)
    return response.data
  },

  /** Fetch the currently-authenticated user profile using the JWT in localStorage. */
  getCurrentUser: async () => {
    const response = await apiClient.get('/api/v1/auth/me')
    return response.data
  },

  /** Exchange a refreshToken for a new { accessToken }. */
  refreshAccessToken: async (refreshToken) => {
    const response = await apiClient.post('/api/v1/auth/refresh', { refreshToken })
    return response.data
  },

  /** Logout: revoke the refreshToken server-side. */
  logout: async (refreshToken) => {
    try {
      await apiClient.post('/api/v1/auth/logout', { refreshToken })
    } catch {
      // Ignore errors during logout — clear client state regardless
    }
  },
}
