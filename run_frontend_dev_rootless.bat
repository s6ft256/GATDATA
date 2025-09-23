@echo off
echo Starting frontend development server (rootless deployment)...

REM Check if we're in the right directory
if not exist "package.json" (
    echo Error: package.json not found
    echo Please run this script from the project root directory
    pause
    exit /b 1
)

REM Check if node_modules exists
if not exist "node_modules" (
    echo Warning: node_modules directory not found
    echo You may need to run setup_frontend_rootless.bat first
)

REM Start the frontend development server
echo Starting Vite development server...
npm run dev

if %errorlevel% neq 0 (
    echo Error: Failed to start frontend development server
    pause
    exit /b 1
)

echo Frontend development server started successfully!
pause