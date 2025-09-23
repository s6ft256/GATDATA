@echo off
echo Setting up both frontend and backend for rootless deployment...

REM Check if we're in the right directory
if not exist "package.json" (
    echo Error: package.json not found
    echo Please run this script from the project root directory
    pause
    exit /b 1
)

if not exist "backend\requirements.txt" (
    echo Error: backend\requirements.txt not found
    echo Please run this script from the project root directory
    pause
    exit /b 1
)

echo.
echo === Setting up Backend ===
call setup_backend_rootless.bat

if %errorlevel% neq 0 (
    echo Error: Backend setup failed
    pause
    exit /b 1
)

echo.
echo === Setting up Frontend ===
call setup_frontend_rootless.bat

if %errorlevel% neq 0 (
    echo Error: Frontend setup failed
    pause
    exit /b 1
)

echo.
echo ========================================
echo Rootless deployment setup completed!
echo ========================================
echo To run the application:
echo 1. Start the backend: run_backend_rootless.bat
echo 2. Start the frontend: run_frontend_dev_rootless.bat
echo.
pause