@echo off
title Share Expiry Validation App
color 0A

cd /d "%~dp0"

echo ==============================================
echo   STARTING EXPIRY VALIDATION SHARING STACK
echo ==============================================
echo.
echo This starts:
echo   1. Docker Postgres + pgAdmin
echo   2. FastAPI backend on http://localhost:8001
echo   3. Next.js frontend on http://localhost:8000
echo.
echo Keep ngrok forwarding to http://localhost:8000
echo Friend URL: your current ngrok https URL
echo.

echo [1/3] Starting Docker database stack...
cd /d "%~dp0backend_v2"
docker compose up -d
if errorlevel 1 (
  echo.
  echo Docker failed to start. Open Docker Desktop and run this file again.
  pause
  exit /b 1
)

echo [2/3] Starting FastAPI backend on port 8001...
start "Expiry API Backend 8001" cmd /k cd /d "%~dp0backend_v2" ^&^& python -m uvicorn app.main:app --host 0.0.0.0 --port 8001
timeout /t 4 /nobreak > NUL

echo [3/3] Starting frontend on port 8000...
start "Expiry Frontend 8000" cmd /k cd /d "%~dp0Frontend" ^&^& npm.cmd run dev -- -p 8000

echo.
echo ==============================================
echo Sharing stack started.
echo Open locally: http://localhost:8000
echo Share ngrok:  https://charred-issuing-slit.ngrok-free.dev
echo ==============================================
echo.
pause
