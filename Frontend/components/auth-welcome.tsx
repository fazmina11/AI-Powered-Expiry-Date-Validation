"use client"

import { useAuth } from "@/contexts/AuthContext"

export default function AuthWelcome() {
  const { user } = useAuth()
  const name = user?.name?.trim() || user?.email

  if (!name) return null

  return (
    <div className="mb-8 rounded-3xl border border-white/20 bg-white/10 p-5 text-center text-white shadow-xl shadow-black/20 backdrop-blur-lg">
      <p className="text-sm uppercase tracking-[0.35em] text-white/70">Logged in</p>
      <h2 className="mt-2 text-3xl font-semibold">Welcome back, {name}!</h2>
      <p className="mt-2 text-sm text-white/70">You’re signed in and ready to manage expiry validation.</p>
    </div>
  )
}
