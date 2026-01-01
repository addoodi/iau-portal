@echo off
cd /d "%~dp0"
echo Starting backend...
python -m uvicorn backend.main:app --reload --host 0.0.0.0 --port 8000
pause
