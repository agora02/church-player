@echo off
chcp 65001 > nul
title GitHub Church Player 업로드 매니저
echo ========================================================
echo   ✝️ Church Media Master - GitHub 원격 업로드 시작
echo ========================================================
echo.
cd /d "%~dp0"

echo [1/3] Git 설정 및 파일 추가 중...
tools\git\cmd\git.exe init
tools\git\cmd\git.exe config user.name "agora02"
tools\git\cmd\git.exe config user.email "agora02@github.com"
tools\git\cmd\git.exe add -A
tools\git\cmd\git.exe commit -m "feat: Church Media Master Pro v2.0.0 release" > nul 2>&1
tools\git\cmd\git.exe branch -M main
tools\git\cmd\git.exe remote remove origin > nul 2>&1
tools\git\cmd\git.exe remote add origin https://github.com/agora02/church-player.git

echo.
echo [2/3] GitHub로 소스 코드 및 릴리즈 전송 중...
echo (브라우저 로그인 창이 뜨면 확인을 눌러주세요)
echo.
tools\git\cmd\git.exe push -u origin main

echo.
echo [3/3] v2.0.0 릴리즈 태그 전송 중...
tools\git\cmd\git.exe tag -a v2.0.0 -m "Release v2.0.0" > nul 2>&1
tools\git\cmd\git.exe push origin v2.0.0

echo.
echo ========================================================
echo   🎉 업로드가 성공적으로 완료되었습니다!
echo ========================================================
echo.
pause
