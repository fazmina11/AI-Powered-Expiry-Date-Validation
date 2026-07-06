"use client"

import { createContext, useContext, useState, useEffect, ReactNode } from "react"

// Development flag
const DEVELOPMENT_MODE = true

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

// Mock user for bypass mode
const MOCK_USER: User = {
  id: "dev-user",
  name: "Development User",
  email: "developer@local",
}

export function AuthProvider({ children }: { children: ReactNode }) {
  const [user, setUser] = useState<User | null>(null)
  const [isLoading, setIsLoading] = useState(true)

  useEffect(() => {
    if (DEVELOPMENT_MODE) {
      // Bypasses network completely, logs in immediately using mock user
      setUser(MOCK_USER)
      localStorage.setItem("user", JSON.stringify(MOCK_USER))
      localStorage.setItem("auth_token", "dev-mode-bypass-token")
      localStorage.setItem("auth_user_name", MOCK_USER.name || MOCK_USER.email)
      setIsLoading(false)
    } else {
      // Future Firebase configuration integration branch
      setIsLoading(false)
    }
  }, [])

  const login = async (email: string, password: string) => {
    setIsLoading(true)
    try {
      if (DEVELOPMENT_MODE) {
        setUser(MOCK_USER)
        localStorage.setItem("user", JSON.stringify(MOCK_USER))
        localStorage.setItem("auth_token", "dev-mode-bypass-token")
        localStorage.setItem("auth_user_name", MOCK_USER.name || MOCK_USER.email)
      }
    } finally {
      setIsLoading(false)
    }
  }

  const signup = async (name: string, email: string, password: string) => {
    setIsLoading(true)
    try {
      if (DEVELOPMENT_MODE) {
        const customUser = { ...MOCK_USER, name: name || MOCK_USER.name, email: email || MOCK_USER.email }
        setUser(customUser)
        localStorage.setItem("user", JSON.stringify(customUser))
        localStorage.setItem("auth_token", "dev-mode-bypass-token")
        localStorage.setItem("auth_user_name", customUser.name || customUser.email)
      }
    } finally {
      setIsLoading(false)
    }
  }

  const logout = () => {
    setUser(null)
    localStorage.removeItem("user")
    localStorage.removeItem("auth_token")
    localStorage.removeItem("auth_user_name")
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
