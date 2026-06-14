@echo off
chcp 65001 >nul
title 屏幕翻译 - 客户端 GUI
cd /d "%~dp0client"
echo ============================================
echo   正在启动客户端...
echo   请确保已先启动后端服务 (1-启动后端.bat)
echo ============================================
echo.
D:\CM\python3.13.13\python.exe client.py
echo.
echo 客户端已关闭，按任意键退出...
pause >nul
