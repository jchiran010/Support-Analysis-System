@echo off
echo ===================================================
echo     Support Analysis System - Installation Script
echo ===================================================
echo.

echo [1/3] Checking Python Installation...
python --version >nul 2>&1
if %errorlevel% neq 0 (
    echo Error: Python is not installed or not in PATH. Please install Python and try again.
    pause
    exit /b
)
echo Python found.

echo.
echo [2/3] Installing Dependencies...
pip install -r requirements.txt
if %errorlevel% neq 0 (
    echo Error: Failed to install dependencies.
    pause
    exit /b
)

echo.
echo [3/3] Installation Complete!
echo You can now run the application using start.bat
echo.
pause
