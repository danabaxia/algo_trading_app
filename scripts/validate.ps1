
$backendPort = 8001
$frontendPort = 5173
$backendUrl = "http://localhost:$backendPort"
$frontendUrl = "http://localhost:$frontendPort"

function Test-Port {
    param($port)
    $tcp = New-Object Net.Sockets.TcpClient
    try {
        $tcp.Connect("localhost", $port)
        $tcp.Close()
        return $true
    } catch {
        return $false
    }
}

Write-Host "=== System Validation Started ===" -ForegroundColor Cyan

# 1. Check Backend
if (Test-Port $backendPort) {
    Write-Host "[OK] Backend Port $backendPort is open." -ForegroundColor Green
    try {
        $res = Invoke-WebRequest -Uri "$backendUrl/" -UseBasicParsing -TimeoutSec 2
        Write-Host "     Backend Health Check: OK ($($res.StatusCode))" -ForegroundColor Green
    } catch {
        Write-Host "     [ERROR] Backend Port open but not responding HTTP: $_" -ForegroundColor Red
    }
} else {
    Write-Host "[WARN] Backend not running on $backendPort. Attempting to start..." -ForegroundColor Yellow
    try {
        Start-Process "cmd.exe" -ArgumentList "/c run_backend.bat" -WorkingDirectory $PSScriptRoot -WindowStyle Minimized
        Write-Host "     Started run_backend.bat. Waiting 10s..."
        Start-Sleep -Seconds 10
        if (Test-Port $backendPort) {
             Write-Host "     [OK] Backend started successfully." -ForegroundColor Green
        } else {
             Write-Host "     [FAIL] Backend failed to start within timeout." -ForegroundColor Red
        }
    } catch {
        Write-Host "     [FAIL] Could not launch run_backend.bat" -ForegroundColor Red
    }
}

# 2. Check Frontend
if (Test-Port $frontendPort) {
    Write-Host "[OK] Frontend Port $frontendPort is open." -ForegroundColor Green
    try {
        $res = Invoke-WebRequest -Uri "$frontendUrl" -UseBasicParsing -TimeoutSec 2
        Write-Host "     Frontend Health Check: OK ($($res.StatusCode))" -ForegroundColor Green
    } catch {
        Write-Host "     [ERROR] Frontend Port open but not responding HTTP: $_" -ForegroundColor Red
    }
} else {
    Write-Host "[WARN] Frontend not running on $frontendPort. Attempting to start..." -ForegroundColor Yellow
    try {
        Start-Process "cmd.exe" -ArgumentList "/c run_dashboard.bat" -WorkingDirectory $PSScriptRoot -WindowStyle Minimized
        Write-Host "     Started run_dashboard.bat. Waiting 15s..."
        Start-Sleep -Seconds 15
        if (Test-Port $frontendPort) {
             Write-Host "     [OK] Frontend started successfully." -ForegroundColor Green
        } else {
             Write-Host "     [FAIL] Frontend failed to start within timeout." -ForegroundColor Red
        }
    } catch {
        Write-Host "     [FAIL] Could not launch run_dashboard.bat" -ForegroundColor Red
    }
}

Write-Host "=== Validation Complete ===" -ForegroundColor Cyan
