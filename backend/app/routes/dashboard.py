"""
routes/dashboard.py — Compatibility shim.
Canonical router is dashboard_routes.py (registered in main.py).
This file is kept so any stale imports don't break at startup.
"""
# No routes registered here — all endpoints live in dashboard_routes.py
from fastapi import APIRouter
router = APIRouter()
