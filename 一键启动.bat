@echo off
setlocal

set ROOT=%~dp0

echo Starting Screen Translator...

echo 1/2: Starting Backend...
start "Backend" cmd /c "cd /d %ROOT%server && start.bat"

echo Waiting...
ping -n 5 127.0.0.1 >nul

echo 2/2: Starting Client...
start "Client" cmd /c "cd /d %ROOT%client && start.bat"

echo Done!
pause