@echo off
echo ========================================
echo   IAU Portal - Backend Server (FastAPI)
echo ========================================
echo.

REM Change to the directory where the batch file is located
cd /d "%~dp0"

REM Check if Python is installed
python --version >nul 2>&1
if errorlevel 1 (
    echo ERROR: Python is not installed or not in PATH
    echo Please install Python 3.9+ from https://www.python.org/
    pause
    exit /b 1
)

echo Checking Python version...
python --version

REM Check if backend directory exists
if not exist "backend" (
    echo ERROR: backend directory not found
    echo Current directory: %CD%
    echo.
    echo Please run this batch file from the project root directory
    pause
    exit /b 1
)

echo.
echo Starting Uvicorn server with hot reload...
echo Backend will be available at: http://localhost:8000
echo API docs available at: http://localhost:8000/docs
echo.
echo Press Ctrl+C to stop the server
echo ========================================
echo.

python -m uvicorn backend.main:app --reload --host 0.0.0.0 --port 8000

if errorlevel 1 (
    echo.
    echo ERROR: Backend server failed to start
    echo Check the error message above for details
    pause
    exit /b 1
)

pause
