@echo off
cd /d "%~dp0"
"C:\Users\haris\anaconda3\python.exe" -m uvicorn app.main:app --host 0.0.0.0 --port 8001 > backend-server.bat.log 2>&1
