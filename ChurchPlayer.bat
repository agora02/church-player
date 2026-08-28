@echo off
title Church Media Master
if exist "%~dp0dist\ChurchPlayer\ChurchPlayer.exe" (
    start "" "%~dp0dist\ChurchPlayer\ChurchPlayer.exe"
) else (
    python "%~dp0ChurchPlayer.py"
)