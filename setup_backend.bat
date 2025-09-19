@echo off
echo Installing backend dependencies...
pip install -r backend/requirements.txt
echo.
echo Backend dependencies installed successfully!
echo.
echo To start the backend server, run:
echo   cd backend && python app.py
pause