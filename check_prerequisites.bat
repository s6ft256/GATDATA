@echo off
echo Checking prerequisites for rootless deployment...

set ERROR_COUNT=0

echo.
echo === Checking Python ===
python --version >nul 2>&1
if %errorlevel% equ 0 (
    for /f "tokens=*" %%i in ('python --version') do set PYTHON_VERSION=%%i
    echo [OK] %PYTHON_VERSION%
) else (
    echo [ERROR] Python is not installed or not in PATH
    set /a ERROR_COUNT+=1
)

echo.
echo === Checking pip ===
pip --version >nul 2>&1
if %errorlevel% equ 0 (
    echo [OK] pip is installed
) else (
    echo [ERROR] pip is not installed
    set /a ERROR_COUNT+=1
)

echo.
echo === Checking Node.js ===
node --version >nul 2>&1
if %errorlevel% equ 0 (
    for /f "tokens=*" %%i in ('node --version') do set NODE_VERSION=%%i
    echo [OK] %NODE_VERSION%
) else (
    echo [ERROR] Node.js is not installed or not in PATH
    set /a ERROR_COUNT+=1
)

echo.
echo === Checking npm ===
npm --version >nul 2>&1
if %errorlevel% equ 0 (
    for /f "tokens=*" %%i in ('npm --version') do set NPM_VERSION=%%i
    echo [OK] %NPM_VERSION%
) else (
    echo [ERROR] npm is not installed
    set /a ERROR_COUNT+=1
)

echo.
echo === Checking Backend Directory ===
if exist "backend" (
    echo [OK] backend directory found
) else (
    echo [ERROR] backend directory not found
    set /a ERROR_COUNT+=1
)

echo.
echo === Checking Frontend Files ===
if exist "index.html" (
    echo [OK] index.html found
) else (
    echo [ERROR] index.html not found
    set /a ERROR_COUNT+=1
)

echo.
echo ========================================
if %ERROR_COUNT% equ 0 (
    echo All prerequisites are satisfied!
    echo You can proceed with rootless deployment.
) else (
    echo %ERROR_COUNT% prerequisite(s) missing.
    echo Please install the missing components before proceeding.
)
echo ========================================

pause