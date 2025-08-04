#!/usr/bin/env powershell

Write-Host "Starting MarketSwimmer GUI..." -ForegroundColor Green
Write-Host ""

$pythonPath = "C:/Users/jerem/AppData/Local/Programs/Python/Python312/python.exe"
$scriptPath = "market_swimmer_gui.py"

if (Test-Path $pythonPath) {
    Write-Host "Using Python 3.12..." -ForegroundColor Yellow
    & $pythonPath $scriptPath
} else {
    Write-Host "Python 3.12 not found at expected location." -ForegroundColor Red
    Write-Host "Trying alternative Python commands..." -ForegroundColor Yellow
    
    try {
        python $scriptPath
    } catch {
        try {
            py $scriptPath
        } catch {
            Write-Host "ERROR: Could not find Python executable!" -ForegroundColor Red
            Write-Host "Please make sure Python is installed and accessible." -ForegroundColor Red
        }
    }
}

Write-Host ""
Write-Host "GUI has closed." -ForegroundColor Yellow
Read-Host "Press Enter to continue"
