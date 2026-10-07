
@echo off
setlocal EnableExtensions EnableDelayedExpansion

:: ============================================================
:: J-BOT SETUP
:: ============================================================

:: Enable ANSI colors in modern Windows
for /F "delims=" %%E in ('echo prompt $E^| cmd') do set "ESC=%%E"

set "GREEN=!ESC![92m"
set "CYAN=!ESC![96m"
set "YELLOW=!ESC![93m"
set "RED=!ESC![91m"
set "WHITE=!ESC![97m"
set "GRAY=!ESC![90m"
set "RESET=!ESC![0m"

cls

echo.
echo !CYAN!============================================================!RESET!
echo !CYAN!                         J-BOT SETUP!RESET!
echo !CYAN!============================================================!RESET!
echo.
echo !WHITE!Welcome to the J-BOT setup wizard.!RESET!
echo.

:: ============================================================
:: INSTALL UV
:: ============================================================

echo !YELLOW![1/3] Checking UV...!RESET!
echo.

where uv >nul 2>&1

if !errorlevel! EQU 0 (
    echo !GREEN![OK] UV is already installed.!RESET!
) else (
    echo !YELLOW![INFO] UV was not found. Installing UV...!RESET!
    echo.

    powershell -ExecutionPolicy Bypass -Command "irm https://astral.sh/uv/install.ps1 | iex"

    if !errorlevel! NEQ 0 (
        echo.
        echo !RED![ERROR] Failed to install UV.!RESET!
        pause
        exit /b 1
    )

    echo.
    echo !GREEN![OK] UV installation completed.!RESET!
)

echo.

:: ============================================================
:: ENVIRONMENT SETUP
:: ============================================================

echo !YELLOW![2/3] Python environment setup!RESET!
echo.
echo !WHITE!Choose where J-BOT dependencies should be installed:!RESET!
echo.
echo !CYAN![1]!RESET! Virtual environment
echo !CYAN![2]!RESET! System Python
echo.

set "env_option="
set /p "env_option=Enter your choice (1/2): "

if "!env_option!"=="1" goto VENV
if "!env_option!"=="2" goto SYSTEM

echo.
echo !RED![ERROR] Invalid choice.!RESET!
pause
exit /b 1


:VENV

echo.
echo !CYAN![VENV] Creating virtual environment...!RESET!

if exist "venv\Scripts\python.exe" (
    echo !GREEN![OK] Virtual environment already exists.!RESET!
) else (
    uv venv

    if !errorlevel! NEQ 0 (
        echo !RED![ERROR] Failed to create virtual environment.!RESET!
        pause
        exit /b 1
    )

    echo !GREEN![OK] Virtual environment created.!RESET!
)

echo.
echo !CYAN![VENV] Installing dependencies...!RESET!

uv pip install -r requirements.txt

if !errorlevel! NEQ 0 (
    echo.
    echo !RED![ERROR] Dependency installation failed.!RESET!
    pause
    exit /b 1
)

echo.
echo !GREEN![OK] Dependencies installed.!RESET!
goto MODE


:SYSTEM

echo.
echo !CYAN![SYSTEM] Installing dependencies into system Python...!RESET!

uv pip install --system -r requirements.txt

if !errorlevel! NEQ 0 (
    echo.
    echo !RED![ERROR] Dependency installation failed.!RESET!
    pause
    exit /b 1
)

echo.
echo !GREEN![OK] Dependencies installed.!RESET!
goto MODE


:: ============================================================
:: ONLINE / OFFLINE MODE
:: ============================================================

:MODE

echo.
echo !YELLOW![3/3] J-BOT mode selection!RESET!
echo.
echo !WHITE!J-BOT supports two modes:!RESET!
echo.
echo !GREEN![1] Offline!RESET!  - Runs locally
echo !CYAN![2] Online!RESET!   - Requires an API key
echo.

set "option="
set /p "option=Enter your choice (1/2): "

if "!option!"=="1" goto OFFLINE
if "!option!"=="2" goto ONLINE

echo.
echo !RED![ERROR] Invalid option. Please choose 1 or 2.!RESET!
pause
goto MODE


:OFFLINE

echo.
echo !GREEN!============================================================!RESET!
echo !GREEN!                       OFFLINE MODE!RESET!
echo !GREEN!============================================================!RESET!
echo.
echo !WHITE!Starting J-BOT offline...!RESET!
echo.

if "!env_option!"=="1" (
    call venv\Scripts\activate.bat
)

python agent.py

if !errorlevel! NEQ 0 (
    echo.
    echo !RED![ERROR] J-BOT exited with an error.!RESET!
)

goto END


:ONLINE

echo.
echo !CYAN!============================================================!RESET!
echo !CYAN!                        ONLINE MODE!RESET!
echo !CYAN!============================================================!RESET!
echo.
echo !WHITE!Starting J-BOT online...!RESET!
echo.

if "!env_option!"=="1" (
    call venv\Scripts\activate.bat
)

python ongent.py

if !errorlevel! NEQ 0 (
    echo.
    echo !RED![ERROR] J-BOT exited with an error.!RESET!
)

goto END


:END

echo.
echo !GRAY!============================================================!RESET!
echo !GREEN!                         DONE!RESET!
echo !GRAY!============================================================!RESET!
echo.

pause
