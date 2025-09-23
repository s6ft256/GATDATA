@echo off
echo Starting both frontend and backend services (rootless deployment)...

REM Check if we're in the right directory
if not exist "package.json" (
    echo Error: package.json not found
    echo Please run this script from the project root directory
    pause
    exit /b 1
)

if not exist "backend\app.py" (
    echo Error: backend\app.py not found
    echo Please run this script from the project root directory
    pause
    exit /b 1
)

echo This script will start both services. You'll need to open two separate terminals
echo or use a process manager to run them simultaneously.
echo.
echo Option 1: Manual approach (recommended)
echo 1. Open a new terminal and run: run_backend_rootless.bat
echo 2. In this terminal, run: run_frontend_dev_rootless.bat
echo.
echo Option 2: Using a process manager (if installed)
echo npm install -g concurrently
echo concurrently "cd backend && python app.py" "npm run dev"
echo.
echo Press any key to continue...
pause >nul

echo Starting backend server in a new window...
start "Backend Server" /D "backend" cmd /k "python app.py"

echo Starting frontend development server...
npm run dev

if %errorlevel% neq 0 (
    echo Error: Failed to start services
    pause
    exit /b 1
)

echo Services started successfully!
pause