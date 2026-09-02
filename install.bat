@echo off
title Manjeet TTS - Install
echo ==========================================
echo       MANJEET TTS - INSTALLER
echo ==========================================
echo.
python --version
if errorlevel 1 (
  echo.
  echo Python nahi mila.
  echo Pehle Python 3.8.10 install karein.
  pause
  exit /b 1
)
echo.
echo Installing required packages...
python -m pip install --upgrade "pip<24.1"
python -m pip install -r requirements.txt
echo.
echo Installation complete.
pause
