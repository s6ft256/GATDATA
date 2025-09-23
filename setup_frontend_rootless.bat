@echo off
echo Setting up frontend environment (rootless deployment)...

REM Check if Node.js is installed
node --version >nul 2>&1
if %errorlevel% neq 0 (
    echo Error: Node.js is not installed or not in PATH
    echo Please install Node.js 16 or later and try again
    pause
    exit /b 1
)

REM Check if npm is installed
npm --version >nul 2>&1
if %errorlevel% neq 0 (
    echo Error: npm is not installed
    echo Please install npm and try again
    pause
    exit /b 1
)

REM Install frontend dependencies
echo Installing frontend dependencies...
npm install

if %errorlevel% neq 0 (
    echo Error: Failed to install frontend dependencies
    pause
    exit /b 1
)

echo Frontend setup completed successfully!
echo To run the frontend development server, execute: npm run dev
pause