@echo off
setlocal
set PYTHON=D:\CM\python3.13.13\python.exe
set SCRIPT_DIR=%~dp0

echo ============================================
echo    屏幕翻译工具 - 启动脚本
echo ============================================
echo.
echo Python路径: %PYTHON%
echo.
echo 选择启动模式:
echo   1) 启动后端服务 (端口 8000)
echo   2) 启动客户端 GUI
echo   3) 安装服务端依赖 (第一次使用需执行)
echo   4) 安装客户端依赖 (第一次使用需执行)
echo   5) 退出
echo.
set /p choice="请输入选项 (1-5): "

if "%choice%"=="1" goto start_server
if "%choice%"=="2" goto start_client
if "%choice%"=="3" goto install_server
if "%choice%"=="4" goto install_client
if "%choice%"=="5" goto end
echo 无效选项
pause
goto end

:start_server
echo 启动后端服务... (按 Ctrl+C 停止)
cd /d "%SCRIPT_DIR%server"
%PYTHON% -m uvicorn server:app --host 0.0.0.0 --port 8000 --reload
goto end

:start_client
echo 启动客户端...
cd /d "%SCRIPT_DIR%client"
%PYTHON% client.py
goto end

:install_server
cd /d "%SCRIPT_DIR%server"
%PYTHON% -m pip install -r requirements.txt
echo.
echo 服务端依赖安装完成！
pause
goto end

:install_client
cd /d "%SCRIPT_DIR%client"
%PYTHON% -m pip install -r requirements.txt
echo.
echo 客户端依赖安装完成！
pause
goto end

:end
endlocal
