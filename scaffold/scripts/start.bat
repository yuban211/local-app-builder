@echo off
chcp 65001 >nul 2>&1
cd /d "%~dp0.."
echo.
echo   Local App Scaffold
echo   ------------------
echo.

where python >nul 2>nul
if errorlevel 1 (
    where python3 >nul 2>nul
    if errorlevel 1 (
        echo   [ERROR] Python not found.
        echo   Install from https://www.python.org/downloads/
        echo   Remember to check "Add Python to PATH" during install.
        echo.
        pause
        exit /b 1
    )
    set PY=python3
) else (
    set PY=python
)

echo   Python: %PY%
echo   Data:   %CD%\data\app.db
echo   Starting on http://127.0.0.1:8770/
echo   Press Ctrl+C in this window to stop.
echo.

%PY% src\app.py 8770

echo.
echo   Stopped.
pause
