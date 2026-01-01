Write-Host "Killing all Python processes running uvicorn..." -ForegroundColor Yellow

Get-Process python* -ErrorAction SilentlyContinue | Where-Object {
    $_.CommandLine -like "*uvicorn*"
} | ForEach-Object {
    Write-Host "Killing process $($_.Id): $($_.ProcessName)" -ForegroundColor Red
    Stop-Process -Id $_.Id -Force
}

Write-Host "Done. Waiting 2 seconds..." -ForegroundColor Green
Start-Sleep -Seconds 2

Write-Host "Checking port 8000..." -ForegroundColor Yellow
$port8000 = netstat -ano | findstr :8000 | findstr LISTENING
if ($port8000) {
    Write-Host "WARNING: Port 8000 still in use:" -ForegroundColor Red
    Write-Host $port8000
} else {
    Write-Host "Port 8000 is free!" -ForegroundColor Green
}

Write-Host "`nPress any key to continue..."
$null = $Host.UI.RawUI.ReadKey("NoEcho,IncludeKeyDown")
