@echo off
echo Building frontend for production (rootless deployment)...

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

REM Build the frontend
echo Building frontend...
npm run build

if %errorlevel% neq 0 (
    echo Error: Failed to build frontend
    pause
    exit /b 1
)

echo Frontend built successfully!
echo To serve the production build, you can use:
echo npm install -g serve
echo serve -s dist -l 3000
pause