@echo off
echo Starting InvestByYourself API Server...
echo ========================================

cd /d "%~dp0"
python start-api.py

pause
