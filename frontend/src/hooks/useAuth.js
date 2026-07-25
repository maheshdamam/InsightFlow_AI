import { useState, useEffect, useCallback } from 'react'
import { getCurrentUser, isAuthenticated, logout as doLogout } from '../services/authService.js'

export function useAuth() {
  const [user, setUser] = useState(getCurrentUser())
  const [authenticated, setAuthenticated] = useState(isAuthenticated())

  useEffect(() => {
    setUser(getCurrentUser())
    setAuthenticated(isAuthenticated())
  }, [])

  const refresh = useCallback(() => {
    setUser(getCurrentUser())
    setAuthenticated(isAuthenticated())
  }, [])

  const logout = useCallback(() => {
    doLogout()
    refresh()
  }, [refresh])

  return { user, authenticated, refresh, logout }
}
