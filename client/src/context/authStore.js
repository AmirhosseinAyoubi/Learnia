/**
 * Authentication Store (Zustand)
 */
import { create } from 'zustand'
import { authService } from '../services/authService'

export const useAuthStore = create((set) => ({
  user: null,
  token: localStorage.getItem('token') || null,
  isAuthenticated: !!localStorage.getItem('token'),

  login: async (email, password) => {
    try {
      const response = await authService.login(email, password)
      const { token, user } = response
      
      localStorage.setItem('token', token)
      set({ token, user, isAuthenticated: true })
      return { success: true }
    } catch (error) {
      return { success: false, error: error.response?.data?.message || 'Login failed' }
    }
  },

  register: async (userData) => {
    try {
      const response = await authService.register(userData)
      const { token, user } = response
      
      localStorage.setItem('token', token)
      set({ token, user, isAuthenticated: true })
      return { success: true }
    } catch (error) {
      return { success: false, error: error.response?.data?.message || 'Registration failed' }
    }
  },

  logout: () => {
    authService.logout()
    set({ user: null, token: null, isAuthenticated: false })
  },

  setUser: (user) => set({ user }),
}))
