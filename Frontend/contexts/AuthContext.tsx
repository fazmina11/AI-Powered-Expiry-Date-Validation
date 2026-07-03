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

  useEffect(() => {
    let isMounted = true

    const restoreUser = async () => {
      const savedToken = localStorage.getItem("auth_token")
      const savedUser = localStorage.getItem("user")

      if (!savedToken) {
        setIsLoading(false)
        return
      }

      if (savedUser) {
        try {
          const parsedUser = JSON.parse(savedUser) as User
          if (!isMounted) return
          setUser(parsedUser)
          localStorage.setItem("auth_user_name", parsedUser.name || parsedUser.email)
          setIsLoading(false)
          return
        } catch {
          localStorage.removeItem("user")
        }
      }

      try {
        const me = await authApi.me(savedToken)
        const authUser: User = { id: me.email, email: me.email, name: me.name }
        if (!isMounted) return
        setUser(authUser)
        localStorage.setItem("user", JSON.stringify(authUser))
        localStorage.setItem("auth_user_name", authUser.name || authUser.email)
      } catch {
        localStorage.removeItem("user")
        localStorage.removeItem("auth_token")
        localStorage.removeItem("auth_user_name")
      } finally {
        if (isMounted) setIsLoading(false)
      }
    }

    restoreUser()

    return () => {
      isMounted = false
    }
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
      localStorage.setItem("auth_user_name", authUser.name || authUser.email)
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
      localStorage.setItem("auth_user_name", authUser.name || authUser.email)
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
