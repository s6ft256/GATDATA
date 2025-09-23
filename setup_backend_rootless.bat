@echo off
echo Setting up backend environment (rootless deployment)...

REM Check if Python is installed
python --version >nul 2>&1
if %errorlevel% neq 0 (
    echo Error: Python is not installed or not in PATH
    echo Please install Python 3.9 or later and try again
    pause
    exit /b 1
)

REM Check if pip is installed
pip --version >nul 2>&1
if %errorlevel% neq 0 (
    echo Error: pip is not installed
    echo Please install pip and try again
    pause
    exit /b 1
)

REM Navigate to backend directory
cd backend

REM Install Python dependencies
echo Installing Python dependencies...
pip install -r requirements.txt

if %errorlevel% neq 0 (
    echo Error: Failed to install Python dependencies
    pause
    exit /b 1
)

echo Backend setup completed successfully!
echo To run the backend server, execute: python app.py
pause