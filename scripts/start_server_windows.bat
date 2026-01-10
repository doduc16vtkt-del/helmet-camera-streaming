@echo off
REM Simple launcher for Helmet Camera RF Receiver
REM Khởi động đơn giản cho máy thu Camera Mũ Bảo Hiểm RF

title Helmet Camera RF Receiver

echo.
echo ============================================
echo   Helmet Camera RF Receiver
echo   May Thu Camera Mu Bao Hiem RF
echo ============================================
echo.

REM Change to backend directory
cd /d "%~dp0..\receiver\backend"

REM Check if Python is available
python --version >nul 2>&1
if errorlevel 1 (
    echo ERROR: Python not found!
    echo Please install Python 3.8 or newer
    echo Download from: https://www.python.org/downloads/
    echo.
    pause
    exit /b 1
)

echo Starting server...
echo Khoi dong may chu...
echo.
echo Dashboard will be available at: http://localhost:8080
echo Ban co the truy cap tai: http://localhost:8080
echo.
echo Press Ctrl+C to stop the server
echo Nhan Ctrl+C de dung may chu
echo.

REM Start the server
python app.py

REM If server stops
echo.
echo Server stopped.
echo May chu da dung.
echo.
pause
