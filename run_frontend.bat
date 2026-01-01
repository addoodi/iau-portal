@echo off
echo ========================================
echo   IAU Portal - Frontend Server (Vite)
echo ========================================
echo.

REM Check if Node.js/npm is installed
npm --version >nul 2>&1
if errorlevel 1 (
    echo ERROR: Node.js/npm is not installed or not in PATH
    echo Please install Node.js 18+ from https://nodejs.org/
    pause
    exit /b 1
)

echo Checking Node.js and npm versions...
node --version
npm --version

echo.
echo Starting Vite development server with hot reload...
echo Frontend will be available at: http://localhost:3000
echo.
echo Press Ctrl+C to stop the server
echo ========================================
echo.

REM IMPORTANT: Use 'npm run dev' for Vite (not 'npm start' which was for CRA)
npm run dev

if errorlevel 1 (
    echo.
    echo ERROR: Frontend server failed to start
    echo.
    echo Common issues:
    echo   - Run 'npm install' if you haven't installed dependencies
    echo   - Check that port 3000 is not already in use
    echo   - Check the error message above for details
    pause
)
