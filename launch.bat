@echo off
echo Starting YTLinkExporter...

:: Check if .venv exists; if not, run setup first
if not exist ".venv\Scripts\python.exe" (
    echo Virtual environment not found. Running setup first...
    echo.
    python -m venv .venv
    .venv\Scripts\pip.exe install -r requirements.txt
    echo.
)

start "" .venv\Scripts\pythonw.exe src/main.py
