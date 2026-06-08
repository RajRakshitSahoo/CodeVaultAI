@echo off
title CodeVault AI Launcher
color 0A

echo.
echo  ╔══════════════════════════════════════╗
echo  ║         CodeVault AI Launcher        ║
echo  ╚══════════════════════════════════════╝
echo.

:: Check Python
python --version >nul 2>&1
if errorlevel 1 (
    echo  [ERROR] Python not found. Please install Python 3.10+ from python.org
    pause
    exit /b 1
)

echo  [OK] Python found
echo.

:: Install / upgrade dependencies
echo  Installing dependencies...
python -m pip install -q pygments matplotlib 2>nul
echo  [OK] Dependencies ready
echo.

:: Launch app
echo  Starting CodeVault AI...
echo.
cd /d "%~dp0"
python main.py

if errorlevel 1 (
    echo.
    echo  [ERROR] Application crashed. Check the output above.
    pause
)
