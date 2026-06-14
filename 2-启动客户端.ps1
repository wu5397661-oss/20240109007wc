$pythonPath = "D:\CM\python3.13.13\python.exe"
$clientDir = "d:\CM\翻译\client"

Write-Host "============================================" -ForegroundColor Cyan
Write-Host "   屏幕翻译 - 客户端 GUI" -ForegroundColor Cyan
Write-Host "============================================" -ForegroundColor Cyan
Write-Host "请确保已先启动后端服务 (1-启动后端.ps1)" -ForegroundColor Yellow
Write-Host "============================================" -ForegroundColor Cyan

Set-Location $clientDir
& $pythonPath client.py

Write-Host ""
Write-Host "客户端已关闭，按任意键退出..." -ForegroundColor Gray
$null = $Host.UI.RawUI.ReadKey("NoEcho,IncludeKeyDown")
