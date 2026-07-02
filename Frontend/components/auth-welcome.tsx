"use client"

import { useEffect, useState } from "react"

export default function AuthWelcome() {
  const [name, setName] = useState<string | null>(null)

  useEffect(() => {
    if (typeof window !== "undefined") {
      const storedName = localStorage.getItem("auth_user_name")
      if (storedName) {
        setName(storedName)
      }
    }
  }, [])

  if (!name) return null

  return (
    <div className="mb-8 rounded-3xl border border-white/20 bg-white/10 p-5 text-center text-white shadow-xl shadow-black/20 backdrop-blur-lg">
      <p className="text-sm uppercase tracking-[0.35em] text-white/70">Logged in</p>
      <h2 className="mt-2 text-3xl font-semibold">Welcome back, {name}!</h2>
      <p className="mt-2 text-sm text-white/70">You’re signed in and ready to manage expiry validation.</p>
    </div>
  )
}
