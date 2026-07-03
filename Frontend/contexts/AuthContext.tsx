"use client"

import { createContext, useContext, useState, useEffect, ReactNode } from "react"
import { authApi } from "@/services/apiService"

interface User {
  id: string
  email: string
  name?: string
}

interface AuthContextType {
  user: User | null
  isLoading: boolean
  login: (email: string, password: string) => Promise<void>
  signup: (name: string, email: string, password: string) => Promise<void>
  logout: () => void
}

const AuthContext = createContext<AuthContextType | undefined>(undefined)

export function AuthProvider({ children }: { children: ReactNode }) {
  const [user, setUser] = useState<User | null>(null)
  const [isLoading, setIsLoading] = useState(true)

  // Restore user from localStorage on mount
  useEffect(() => {
    const savedUser = localStorage.getItem("user")
    const savedToken = localStorage.getItem("auth_token")
    if (savedUser && savedToken) {
      try {
        setUser(JSON.parse(savedUser))
      } catch {
        localStorage.removeItem("user")
      }
    }
    setIsLoading(false)
  }, [])

  const login = async (email: string, password: string) => {
    setIsLoading(true)
    try {
      const data = await authApi.login(email, password)
      localStorage.setItem("auth_token", data.access_token)

      const me = await authApi.me(data.access_token)
      const authUser: User = { id: me.email, email: me.email, name: me.name }
      setUser(authUser)
      localStorage.setItem("user", JSON.stringify(authUser))
    } finally {
      setIsLoading(false)
    }
  }

  const signup = async (name: string, email: string, password: string) => {
    setIsLoading(true)
    try {
      const data = await authApi.signup(name, email, password)
      localStorage.setItem("auth_token", data.access_token)

      const me = await authApi.me(data.access_token)
      const authUser: User = { id: me.email, email: me.email, name: me.name }
      setUser(authUser)
      localStorage.setItem("user", JSON.stringify(authUser))
    } finally {
      setIsLoading(false)
    }
  }

  const logout = () => {
    setUser(null)
    localStorage.removeItem("user")
    localStorage.removeItem("auth_token")
  }

  return (
    <AuthContext.Provider value={{ user, isLoading, login, signup, logout }}>
      {children}
    </AuthContext.Provider>
  )
}

export function useAuth() {
  const context = useContext(AuthContext)
  if (context === undefined) {
    throw new Error("useAuth must be used within an AuthProvider")
  }
  return context
}
