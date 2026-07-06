"""
routes/auth.py — DISABLED (auth-free development mode)

This file is a stub. The original auth routes have been preserved in:
  app/legacy/auth/auth_routes.py

Auth endpoints (POST /login, POST /register, GET /me) are not registered
in main.py during auth-free development.

They will be restored when Firebase Admin SDK is integrated.
"""
from fastapi import APIRouter

router = APIRouter()

# ── All original auth endpoints moved to app/legacy/auth/auth_routes.py ──────
# ── This router is NOT mounted in main.py ────────────────────────────────────
