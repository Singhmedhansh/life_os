@echo off
echo Starting Life OS Dashboard...
echo.
cd /d "%~dp0"
python -m streamlit run main.py
pause
