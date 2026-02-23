@echo off
setlocal enabledelayedexpansion
cd /d %~dp0

set NAME=LifeOS
set ICON=assets\life_os.ico

if not exist %ICON% (
    echo Generating icon...
    py build_icon.py
)

py -m pip install --upgrade pip >nul
py -m pip install pyinstaller pillow >nul

py -m PyInstaller ^
  --name "%NAME%" ^
  --onedir ^
  --windowed ^
  --icon "%ICON%" ^
  --clean ^
  --noconfirm ^
  --add-data "main.py;." ^
  --add-data "views;views" ^
  --add-data "modules;modules" ^
  --add-data "assets;assets" ^
  app_launcher.py

echo Build complete. Run dist\%NAME%\%NAME%.exe
endlocal
