@echo off
chcp 65001 >nul
title 屏幕翻译 - 后端服务
cd /d "%~dp0server"
echo ============================================
echo   正在启动后端服务...
echo   Python: D:\CM\python3.13.13\python.exe
echo   监听端口: 8000
echo   健康检查: http://127.0.0.1:8000/health
echo   按 Ctrl+C 停止服务
echo ============================================
echo.
D:\CM\python3.13.13\python.exe -m uvicorn server:app --host 0.0.0.0 --port 8000
echo.
echo 服务已停止，按任意键关闭窗口...
pause >nul
