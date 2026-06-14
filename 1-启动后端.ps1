$pythonPath = "D:\CM\python3.13.13\python.exe"
$serverDir = "d:\CM\翻译\server"

Write-Host "============================================" -ForegroundColor Cyan
Write-Host "   屏幕翻译 - 后端服务" -ForegroundColor Cyan
Write-Host "============================================" -ForegroundColor Cyan
Write-Host "Python: $pythonPath" -ForegroundColor Green
Write-Host "目录: $serverDir" -ForegroundColor Green
Write-Host "端口: 8000" -ForegroundColor Green
Write-Host "按 Ctrl+C 停止服务" -ForegroundColor Yellow
Write-Host "============================================" -ForegroundColor Cyan

Set-Location $serverDir
& $pythonPath -m uvicorn server:app --host 0.0.0.0 --port 8000

Write-Host ""
Write-Host "服务已停止，按任意键退出..." -ForegroundColor Gray
$null = $Host.UI.RawUI.ReadKey("NoEcho,IncludeKeyDown")
