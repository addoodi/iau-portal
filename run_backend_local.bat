@echo off
REM Run backend locally (outside Docker) with localhost database connection

echo Starting IAU Portal Backend (Local Mode)...
echo.

REM Set DATABASE_URL to use localhost instead of postgres container name
set DATABASE_URL=postgresql://iau_admin:iau_secure_password_2024@localhost:5432/iau_portal

REM Start backend with auto-reload
python -m uvicorn backend.main:app --reload --host 127.0.0.1 --port 8000

pause
