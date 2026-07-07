@echo off
title Product Guardian Network (PGN) Launcher
color 05

echo ==============================================
echo      LAUNCHING PRODUCT GUARDIAN NETWORK (PGN)
echo ==============================================
cd /d "%~dp0"

echo [1/3] Starting PostgreSQL via Docker Compose...
cd backend_v2
docker-compose up -d postgres
cd ..
timeout /t 5 /nobreak > NUL

echo [2/3] Starting FastAPI Backend V2 on port 8001...
start "PGN API Backend" cmd /c "cd backend_v2 && python -m uvicorn app.main:app --host 0.0.0.0 --port 8001"
timeout /t 3 /nobreak > NUL

echo [3/3] Starting Next.js Frontend on port 3000...
start "PGN Frontend" cmd /c "cd Frontend && npm run dev"

echo.
echo =======================================================
echo PGN System successfully launched!
echo.
echo - Next.js Frontend: http://localhost:3000/community
echo - FastAPI V2 Backend Docs: http://localhost:8001/docs
echo.
echo To seed the database with community sample data, run:
echo   cd backend_v2
echo   python scripts/seed_community.py
echo.
echo Close the newly opened terminal windows to shut down the servers.
echo =======================================================
pause
