@echo off
echo ===================================================
echo     Support Analysis System - Startup Script
echo ===================================================
echo.

echo [1/3] Installing Required Dependencies...
pip install -r requirements.txt
echo.

echo [2/3] Setting up the Database...
echo Ensuring backend and database are connected...
cd Backend
python -c "from app import app, db; app.app_context().push(); db.create_all()"
echo Database setup complete!
echo.

echo [3/3] Starting the Flask Backend Server...
echo The application will be available at http://127.0.0.1:5000
echo Press CTRL+C to stop the server.
echo.
python app.py
