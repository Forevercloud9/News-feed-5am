@echo off
cd /d "%~dp0"
echo ==========================================
echo   Morning 5 - Dashboard and Checker
echo ==========================================
echo.
echo 1. Stopping any previous instances...
taskkill /F /IM python.exe >nul 2>&1

echo 2. Starting Backend Server...
start "Morning 5 Server" cmd /k "python main_scheduler.py"

echo 3. Waiting for server to initialize (5 seconds)...
timeout /t 5 /nobreak >nul

echo 3. Opening Settings Dashboard...
start http://localhost:8080/settings

echo.
echo ==========================================
echo   Settings Page Opened!
echo   You can configure genres and emails there.
echo   To Run Digest: Click the link at the bottom of the settings page.
echo ==========================================
pause
