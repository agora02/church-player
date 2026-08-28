@echo off
chcp 65001 > nul
title 교회 스마트 방송 미디어 플레이어

echo ========================================================
echo   교회 스마트 비디오 & 음악 방송 플레이어
echo   Church Smart Media Player Launcher
echo ========================================================
echo.
echo [1] 로컬 웹 서버를 시작합니다 (Port 8080)...
echo [2] 브라우저에서 컨트롤러 창을 엽니다...
echo.

start "" "http://localhost:8080"
python -m http.server 8080

pause
