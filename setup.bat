@echo off
echo ============================================
echo   YTLinkExporter - Setup
echo ============================================
echo.

echo [1/2] Creating virtual environment...
python -m venv .venv
if errorlevel 1 (
    echo ERROR: Failed to create virtual environment. Is Python installed?
    pause
    exit /b 1
)

echo [2/2] Installing dependencies...
.venv\Scripts\pip.exe install -r requirements.txt
if errorlevel 1 (
    echo ERROR: Failed to install dependencies.
    pause
    exit /b 1
)

echo.
echo ============================================
echo   Setup complete!
echo   You can now run "launch.bat" to start
echo   the application.
echo ============================================
pause
