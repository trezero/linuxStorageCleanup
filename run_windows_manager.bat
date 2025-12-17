@echo off
REM Windows WSL Storage Manager Launcher
REM Run this file as Administrator to launch the Windows storage manager

echo ================================================================================
echo                    Windows WSL Storage Manager
echo ================================================================================
echo.
echo Checking for Administrator privileges...

net session >nul 2>&1
if %errorLevel% == 0 (
    echo [OK] Running as Administrator
    echo.
) else (
    echo [ERROR] This script must be run as Administrator!
    echo.
    echo Please right-click this file and select "Run as administrator"
    echo.
    pause
    exit /b 1
)

echo Checking for Python...
python --version >nul 2>&1
if %errorLevel% == 0 (
    echo [OK] Python is installed
    echo.
) else (
    echo [ERROR] Python is not installed or not in PATH!
    echo.
    echo Please install Python from: https://www.python.org/downloads/
    echo Make sure to check "Add Python to PATH" during installation
    echo.
    pause
    exit /b 1
)

echo Launching Windows Storage Manager...
echo.
python "%~dp0windows_storage_manager.py"

if %errorLevel% neq 0 (
    echo.
    echo [ERROR] The program exited with an error.
    pause
)
