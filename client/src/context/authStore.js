/**
 * authStore — Zustand global store for authentication state.
 *
 * Stores both the JWT accessToken (used in every API header) and the
 * opaque refreshToken (used only on /refresh). Both are persisted to
 * localStorage so the user stays logged in across page reloads.
 */
import { create } from 'zustand'
import { authService } from '../services/authService'

export const useAuthStore = create((set, get) => ({
  user: null,
  accessToken: localStorage.getItem('accessToken') || null,
  refreshToken: localStorage.getItem('refreshToken') || null,
  isAuthenticated: !!localStorage.getItem('accessToken'),

  login: async (email, password) => {
    try {
      const { accessToken, refreshToken, user } = await authService.login(email, password)
      localStorage.setItem('accessToken', accessToken)
      localStorage.setItem('refreshToken', refreshToken)
      set({ accessToken, refreshToken, user, isAuthenticated: true })
      return { success: true }
    } catch (error) {
      return { success: false, error: error.response?.data?.message || 'Login failed' }
    }
  },

  register: async (userData) => {
    try {
      const { accessToken, refreshToken, user } = await authService.register(userData)
      localStorage.setItem('accessToken', accessToken)
      localStorage.setItem('refreshToken', refreshToken)
      set({ accessToken, refreshToken, user, isAuthenticated: true })
      return { success: true }
    } catch (error) {
      return { success: false, error: error.response?.data?.message || 'Registration failed' }
    }
  },

  fetchCurrentUser: async () => {
    try {
      const user = await authService.getCurrentUser()
      set({ user, isAuthenticated: true })
      return { success: true }
    } catch (error) {
      // If the server returns 401, the axios interceptor will auto-logout
      set({ user: null, isAuthenticated: false })
      return { success: false, error: error.response?.data?.message || 'Failed to load user' }
    }
  },

  logout: async () => {
    const { refreshToken } = get()
    await authService.logout(refreshToken)
    localStorage.removeItem('accessToken')
    localStorage.removeItem('refreshToken')
    set({ user: null, accessToken: null, refreshToken: null, isAuthenticated: false })
  },

  setUser: (user) => set({ user }),
}))
