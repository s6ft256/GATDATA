@echo off
echo Starting backend server (rootless deployment)...

REM Check if we're in the right directory
if not exist "backend\app.py" (
    echo Error: backend\app.py not found
    echo Please run this script from the project root directory
    pause
    exit /b 1
)

REM Navigate to backend directory
cd backend

REM Check if required files exist
if not exist "requirements.txt" (
    echo Warning: requirements.txt not found
)

if not exist "serviceAccountKey.json" (
    echo Warning: serviceAccountKey.json not found
    echo You need to set up Firebase credentials for full functionality
)

REM Start the backend server
echo Starting Flask server...
python app.py

if %errorlevel% neq 0 (
    echo Error: Failed to start backend server
    pause
    exit /b 1
)

echo Backend server started successfully!
pause