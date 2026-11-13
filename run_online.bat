@echo off
setlocal EnableExtensions

cd /d "%~dp0"

echo ============================================================
echo                 J-BOT - RUN ONLINE
echo ============================================================

if exist "venv\Scripts\activate.bat" (
    call venv\Scripts\activate.bat
) else (
    echo [WARN] venv not found. Trying system python...
)

echo.
echo [INFO] Working directory: %cd%

python ongent.py

if errorlevel 1 (
    echo.
    echo [ERROR] J-Bot online run failed with exit code %errorlevel%.
) else (
    echo.
    echo [OK] J-Bot online run finished.
)

pause
