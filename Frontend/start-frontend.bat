@echo off
cd /d "%~dp0"
"C:\Program Files\nodejs\npm.cmd" run dev > dev-server.bat.log 2>&1
