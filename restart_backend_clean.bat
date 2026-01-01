@echo off
echo ========================================
echo   CLEAN BACKEND RESTART
echo ========================================
echo.

echo Step 1: Killing any existing backend processes...
for /f "tokens=5" %%a in ('netstat -ano ^| findstr :8000 ^| findstr LISTENING') do (
    echo Killing process %%a
    taskkill /F /PID %%a >nul 2>&1
)
echo Done.
echo.

echo Step 2: Waiting for port to be released...
timeout /t 2 /nobreak >nul
echo.

echo Step 3: Clearing Python cache...
cd /d "%~dp0"
del /s /q backend\__pycache__\*.* >nul 2>&1
for /d /r backend %%d in (__pycache__) do @if exist "%%d" rd /s /q "%%d" >nul 2>&1
del /s /q backend\*.pyc >nul 2>&1
echo Done.
echo.

echo Step 4: Starting backend with fresh code...
echo Backend will be at: http://localhost:8000
echo API docs at: http://localhost:8000/docs
echo.
python -m uvicorn backend.main:app --reload --host 0.0.0.0 --port 8000

pause
