@echo off
title Build ChurchPlayer EXE
echo ========================================================
echo   Building ChurchPlayer.exe...
echo ========================================================
echo.
python -m PyInstaller --noconfirm --onedir --windowed --name "ChurchPlayer" ChurchPlayer.py
echo.
echo Build complete. Check dist\ChurchPlayer\ChurchPlayer.exe
pause