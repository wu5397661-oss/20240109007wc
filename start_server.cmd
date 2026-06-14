@echo off
setlocal
set "SCRIPT_DIR=%~dp0"
set "PYTHON=D:\CM\python3.13.13\python.exe"

cd /d "%SCRIPT_DIR%server"
echo 启动后端服务...
echo 监听端口: 8000
echo 按 Ctrl+C 停止
"%PYTHON%" -m uvicorn server:app --host 0.0.0.0 --port 8000
