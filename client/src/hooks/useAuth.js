/**
 * Custom Hook for Authentication
 */
import { useEffect } from 'react'
import { useAuthStore } from '../context/authStore'
import { authService } from '../services/authService'

export const useAuth = () => {
  const { user, setUser, isAuthenticated } = useAuthStore()

  useEffect(() => {
    // Fetch current user if authenticated but user data not loaded
    if (isAuthenticated && !user) {
      authService
        .getCurrentUser()
        .then((userData) => setUser(userData))
        .catch((error) => {
          console.error('Failed to fetch user:', error)
        })
    }
  }, [isAuthenticated, user, setUser])

  return {
    user,
    isAuthenticated,
  }
}
