@echo off
cd /d "%~dp0"
echo Starting Morning 5 Backend Server...
echo Access the digest at: http://localhost:8080/schedule_daily_digest
python main_scheduler.py
pause
