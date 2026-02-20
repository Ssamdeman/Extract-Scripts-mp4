@echo off
title Speech ^& Articulation Suite Launcher
cls

echo ===================================================
echo     Speech ^& Articulation Analysis Suite
echo ===================================================
echo.

:: Get the directory where the batch file is located and CD into it
cd /d "%~dp0"

:: Activate the virtual environment
if exist "mp4-script\Scripts\activate.bat" (
    call "mp4-script\Scripts\activate.bat"
    echo [OK] Virtual Environment Activated.
) else (
    echo [WARNING] Virtual environment 'mp4-script' not found!
    echo Please ensure you have run: python -m venv mp4-script
)

echo.
echo ---------------------------------------------------
echo Available Commands:
echo ---------------------------------------------------
echo 1. Speech Analysis (Filler words, Transcript, Readability)
echo    Run: python speech_analysis.py
echo.
echo 2. Articulation Tracker (Jaw/Tongue mobility, Clarity)
echo    Run: python articulation.py
echo.
echo Note: Simply type the command and press Enter. Both tools 
echo will auto-scan their respective 'resources' folders if no 
echo specific file is provided.
echo ---------------------------------------------------
echo.

:: Keep the command prompt open so the user can type commands
cmd /k
